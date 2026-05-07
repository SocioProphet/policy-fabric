#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "contracts" / "agent_harness_policy_gate_decision_v0.schema.json"
EXAMPLE = ROOT / "examples" / "agent_harness_policy_gate_decision_example.json"

VALID_DECISIONS = {"allow", "warn", "block", "needs-human-review"}
VALID_RISK_TIERS = {"low", "medium", "high", "critical"}
VALID_GATE_TYPES = {
    "outcome-admission",
    "plan-graph-review",
    "graph-admission",
    "run-admission",
    "tool-grant",
    "skill-grant",
    "mcp-grant",
    "browser-action",
    "terminal-action",
    "memory",
    "judge",
    "human-control",
    "promotion",
}
REQUIRED_TOP_LEVEL = {"apiVersion", "kind", "metadata", "spec"}
REQUIRED_METADATA = {"name", "repository", "generatedAt", "subjectRef"}
REQUIRED_SPEC = {"gateType", "decision", "riskTier", "checks", "evidenceRefs", "requiredActions"}


def fail(message: str) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return 1


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate_example(data: dict[str, Any]) -> None:
    missing_top = REQUIRED_TOP_LEVEL - set(data)
    require(not missing_top, f"missing top-level fields: {sorted(missing_top)}")
    require(data.get("apiVersion") == "policy.fabric.agent-harness/v0", "invalid apiVersion")
    require(data.get("kind") == "AgentHarnessPolicyGateDecision", "invalid kind")

    metadata = data.get("metadata")
    require(isinstance(metadata, dict), "metadata must be an object")
    missing_metadata = REQUIRED_METADATA - set(metadata)
    require(not missing_metadata, f"missing metadata fields: {sorted(missing_metadata)}")
    require(str(metadata.get("repository")), "metadata.repository must not be empty")
    require(str(metadata.get("subjectRef")), "metadata.subjectRef must not be empty")

    spec = data.get("spec")
    require(isinstance(spec, dict), "spec must be an object")
    missing_spec = REQUIRED_SPEC - set(spec)
    require(not missing_spec, f"missing spec fields: {sorted(missing_spec)}")
    require(spec.get("gateType") in VALID_GATE_TYPES, "invalid gateType")
    require(spec.get("decision") in VALID_DECISIONS, "invalid decision")
    require(spec.get("riskTier") in VALID_RISK_TIERS, "invalid riskTier")

    checks = spec.get("checks")
    require(isinstance(checks, list) and checks, "checks must be a non-empty list")
    for index, check in enumerate(checks):
        require(isinstance(check, dict), f"check {index} must be an object")
        require(check.get("name"), f"check {index} missing name")
        require(check.get("status") in {"pass", "warn", "fail", "not-applicable"}, f"check {index} invalid status")
        require(check.get("message"), f"check {index} missing message")

    evidence_refs = spec.get("evidenceRefs")
    require(isinstance(evidence_refs, list) and evidence_refs, "evidenceRefs must be a non-empty list")
    required_actions = spec.get("requiredActions")
    require(isinstance(required_actions, list), "requiredActions must be a list")

    if spec.get("decision") == "needs-human-review":
        require(spec.get("humanControlRequired") is True, "needs-human-review requires humanControlRequired=true")
        require(required_actions, "needs-human-review requires at least one required action")


def main() -> int:
    try:
        for path in [SCHEMA, EXAMPLE]:
            if not path.exists():
                return fail(f"missing {path}")
        schema = load_json(SCHEMA)
        require(schema.get("title") == "Agent Harness Policy Gate Decision v0", "schema title mismatch")
        require(schema.get("properties", {}).get("apiVersion", {}).get("const") == "policy.fabric.agent-harness/v0", "schema apiVersion const mismatch")
        require(schema.get("properties", {}).get("kind", {}).get("const") == "AgentHarnessPolicyGateDecision", "schema kind const mismatch")
        validate_example(load_json(EXAMPLE))
    except json.JSONDecodeError as exc:
        return fail(f"invalid JSON: {exc}")
    except ValueError as exc:
        return fail(str(exc))

    print("OK: validated agent harness policy gate schema and fixture")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
