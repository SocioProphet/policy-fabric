#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

VERSION = "prophet-understanding.v0"
HIGH_RISK_POLICY_PATHS = (".github/workflows/", "infra/", "policy", "secrets", "deploy", "runtime")


def fail(message: str) -> None:
    print(f"ERR: {message}", file=sys.stderr)
    raise SystemExit(2)


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        fail(f"missing artifact: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid artifact JSON: {exc}")
    if not isinstance(value, dict):
        fail("artifact root must be an object")
    return value


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def decision(check_id: str, state: str, message: str, evidence_receipt_ids: list[str] | None = None, affected_ids: list[str] | None = None) -> dict[str, Any]:
    return {
        "id": check_id,
        "state": state,
        "message": message,
        "evidence_receipt_ids": evidence_receipt_ids or [],
        "affected_ids": affected_ids or [],
    }


def evaluate(artifact: dict[str, Any]) -> dict[str, Any]:
    repo = artifact.get("repo", {}) if isinstance(artifact.get("repo"), dict) else {}
    receipts = [item for item in as_list(artifact.get("provenance_receipts")) if isinstance(item, dict)]
    receipt_ids = {item.get("id") for item in receipts}
    nodes = [item for item in as_list(artifact.get("nodes")) if isinstance(item, dict)]
    edges = [item for item in as_list(artifact.get("edges")) if isinstance(item, dict)]
    node_ids = {node.get("id") for node in nodes}
    checks: list[dict[str, Any]] = []

    if artifact.get("schema_version") == VERSION:
        checks.append(decision("graph.schema.version", "allow", "Artifact declares prophet-understanding.v0."))
    else:
        checks.append(decision("graph.schema.version", "deny", "Artifact schema_version is missing or unsupported."))

    commit = repo.get("commit")
    if isinstance(commit, str) and re.match(r"^[0-9a-fA-F]{7,40}$|^unknown$", commit):
        checks.append(decision("graph.commit.shape", "allow", "Artifact carries a SHA-like commit or explicit unknown marker."))
    else:
        checks.append(decision("graph.commit.shape", "require_review", "Artifact commit is missing or malformed."))

    endpoint_errors = []
    for edge in edges:
        if edge.get("source") not in node_ids or edge.get("target") not in node_ids:
            endpoint_errors.append(edge.get("id", "edge:unknown"))
    if endpoint_errors:
        checks.append(decision("graph.edge.valid_endpoints", "deny", "One or more edges reference missing nodes.", affected_ids=endpoint_errors))
    else:
        checks.append(decision("graph.edge.valid_endpoints", "allow", "All edges reference existing nodes."))

    factual_nodes = [node for node in nodes if node.get("kind") not in {"repo", "directory"}]
    anchored = [node for node in factual_nodes if isinstance(node.get("source_anchor"), dict)]
    missing_anchor = [str(node.get("id")) for node in factual_nodes if not isinstance(node.get("source_anchor"), dict)]
    anchor_ratio = len(anchored) / len(factual_nodes) if factual_nodes else 1.0
    if missing_anchor:
        checks.append(decision("graph.source_anchor.coverage", "require_review", f"Source-anchor coverage is {anchor_ratio:.2f}; missing anchors require review.", affected_ids=missing_anchor))
    else:
        checks.append(decision("graph.source_anchor.coverage", "allow", "All factual nodes carry source anchors."))

    missing_provenance: list[str] = []
    for family in ("nodes", "edges", "summaries", "tours", "diff_impact_sets"):
        for item in as_list(artifact.get(family)):
            if isinstance(item, dict):
                refs = set(as_list(item.get("provenance_receipt_ids")))
                if not refs or not refs <= receipt_ids:
                    missing_provenance.append(str(item.get("id", f"{family}:unknown")))
    if missing_provenance:
        checks.append(decision("graph.provenance.coverage", "require_review", "Some graph facts lack valid provenance receipts.", affected_ids=missing_provenance[:50]))
    else:
        checks.append(decision("graph.provenance.coverage", "allow", "Graph facts carry valid provenance receipt references."))

    risk_paths = []
    for node in nodes:
        path = str(node.get("path", ""))
        lower = path.lower()
        if any(marker in lower for marker in HIGH_RISK_POLICY_PATHS):
            risk_paths.append(str(node.get("id")))
    if risk_paths:
        checks.append(decision("graph.high_risk.paths", "require_review", "High-risk paths are present in the graph and require review for impact claims.", affected_ids=risk_paths[:50]))
    else:
        checks.append(decision("graph.high_risk.paths", "allow", "No high-risk path markers were detected in graph nodes."))

    hook_like = [str(node.get("id")) for node in nodes if "hook" in str(node.get("path", "")).lower()]
    if hook_like:
        checks.append(decision("graph.hook.reviewed", "require_review", "Hook-like paths require explicit review before automation use.", affected_ids=hook_like[:50]))
    else:
        checks.append(decision("graph.hook.reviewed", "allow", "No hook-like paths were detected."))

    state_order = {"allow": 0, "warn": 1, "unknown": 1, "require_review": 2, "deny": 3}
    overall = max((check["state"] for check in checks), key=lambda state: state_order.get(state, 1))
    return {
        "schema_version": VERSION,
        "repo_full_name": repo.get("full_name", "unknown"),
        "repo_commit": repo.get("commit", "unknown"),
        "policy_state": overall,
        "checks": checks,
        "metrics": {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "source_anchor_coverage_ratio": round(anchor_ratio, 4),
            "provenance_receipt_count": len(receipts),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate Prophet Understand graph artifact policy status.")
    parser.add_argument("--artifact", required=True, help="Path to prophet-understanding.json")
    parser.add_argument("--out", default=None, help="Optional output policy decision JSON")
    args = parser.parse_args()

    result = evaluate(load(Path(args.artifact)))
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        print(f"wrote {out}")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
