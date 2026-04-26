#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from policy_fabric.operations_decision_service import evaluate_operations_action  # noqa: E402

SCHEMA = ROOT / "contracts" / "prophet_operations_action_decision_v1.schema.json"


def main() -> int:
    recommendation = {
        "recommendation_id": "oprec-worker-1-isolate",
        "risk_level": "high",
        "requested_outcome": "allow",
        "subject": {"id": "worker-1", "type": "service", "name": "worker-1"},
        "action": {"type": "isolate", "intent": "reduce blast radius", "description": "isolate unhealthy worker"},
        "policy_refs": ["policy://operations/default-action-gates/v1"],
        "signal_refs": ["signal://worker-1/error-rate"],
        "evidence_refs": ["evidence://worker-1/health"],
    }
    decision = evaluate_operations_action(recommendation, mode="report_only")
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.validate(decision, schema)

    checks = {
        "kind": decision.get("kind") == "ProphetOperationsActionDecision",
        "schema_version": decision.get("schema_version") == "v1",
        "recommendation_ref": decision.get("recommendation_ref") == recommendation["recommendation_id"],
        "report_only_manual_review": decision.get("decision", {}).get("outcome") == "manual_review",
        "requires_human_approval": decision.get("controls", {}).get("requires_human_approval") is True,
        "policy_ref_preserved": decision.get("basis", {}).get("policy_refs") == recommendation["policy_refs"],
    }
    ok = all(checks.values())
    print(json.dumps({"ok": ok, "checks": checks, "decision": decision}, indent=2, sort_keys=True))
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
