#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EVALUATOR = ROOT / "tools/evaluate_prophet_understand_policy.py"


def fail(message: str) -> None:
    print(f"ERR: {message}", file=sys.stderr)
    raise SystemExit(2)


def artifact() -> dict[str, Any]:
    return {
        "schema_version": "prophet-understanding.v0",
        "repo": {"full_name": "SocioProphet/policy-fixture", "default_branch": "main", "commit": "abcdef1", "generated_at": "2026-05-05T00:00:00Z", "artifact_hash": "sha256:fixture"},
        "generator": {"name": "smart-tree", "version": "fixture", "parser_versions": {"fixture": "v0"}},
        "agent_identity": {"kind": "fixture", "id": "agent://fixture", "did": None},
        "nodes": [
            {"id": "repo:SocioProphet/policy-fixture", "kind": "repo", "label": "repo", "path": ".", "confidence": 1.0, "provenance_receipt_ids": ["receipt:run"], "metadata": {}},
            {"id": "workflow:.github/workflows/ci.yml", "kind": "workflow", "label": "ci", "path": ".github/workflows/ci.yml", "source_anchor": {"path": ".github/workflows/ci.yml", "start_line": 1, "end_line": 1, "content_hash": "sha256:workflow"}, "confidence": 1.0, "provenance_receipt_ids": ["receipt:workflow"], "metadata": {}},
        ],
        "edges": [{"id": "edge:repo-contains-workflow", "kind": "contains", "source": "repo:SocioProphet/policy-fixture", "target": "workflow:.github/workflows/ci.yml", "confidence": 1.0, "provenance_receipt_ids": ["receipt:run"], "metadata": {}}],
        "summaries": [],
        "tours": [],
        "diff_impact_sets": [],
        "provenance_receipts": [
            {"id": "receipt:run", "claim_type": "repo-scan", "generator": "smart-tree", "parser_version": "fixture", "input_source_hash": "sha256:run", "generated_at": "2026-05-05T00:00:00Z", "confidence": 1.0, "validation_state": "valid", "warnings": []},
            {"id": "receipt:workflow", "claim_type": "workflow-node", "generator": "smart-tree", "parser_version": "fixture", "input_source_hash": "sha256:workflow", "generated_at": "2026-05-05T00:00:00Z", "confidence": 1.0, "validation_state": "valid", "warnings": []},
        ],
        "validation_results": [],
        "policy_status": {"state": "allow", "checks": [{"id": "policy:fixture", "state": "allow", "message": "fixture", "evidence_receipt_ids": ["receipt:run"]}]},
    }


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="policy-prophet-understand-") as raw_tmp:
        tmp = Path(raw_tmp)
        artifact_path = tmp / "prophet-understanding.json"
        out = tmp / "policy.json"
        artifact_path.write_text(json.dumps(artifact(), indent=2, sort_keys=True), encoding="utf-8")
        result = subprocess.run([sys.executable, str(EVALUATOR), "--artifact", str(artifact_path), "--out", str(out)], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
        if result.returncode != 0:
            print(result.stdout, file=sys.stderr)
            fail("policy evaluator exited nonzero")
        payload = json.loads(out.read_text(encoding="utf-8"))
        if payload.get("policy_state") != "require_review":
            fail(f"expected require_review for workflow path, got {payload.get('policy_state')}")
        check_ids = {check.get("id") for check in payload.get("checks", []) if isinstance(check, dict)}
        for check_id in {"graph.schema.version", "graph.edge.valid_endpoints", "graph.high_risk.paths"}:
            if check_id not in check_ids:
                fail(f"missing policy check: {check_id}")
        print("OK: Policy Fabric Prophet Understand policy smoke passed")


if __name__ == "__main__":
    main()
