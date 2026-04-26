#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from policy_fabric.operations_decision_api import app  # noqa: E402

SCHEMA = ROOT / "contracts" / "prophet_operations_action_decision_v1.schema.json"


def main() -> int:
    client = TestClient(app)
    health = client.get("/healthz")
    recommendation = {
        "recommendation_id": "oprec-worker-2-restart",
        "risk_level": "low",
        "requested_outcome": "allow",
        "subject": {"id": "worker-2", "type": "service", "name": "worker-2"},
        "action": {"type": "restart", "intent": "restore health", "description": "restart unhealthy worker"},
        "policy_refs": ["policy://operations/default-action-gates/v1"],
    }
    response = client.post("/v1/operations/action-decision", json={"recommendation": recommendation, "mode": "report_only"})
    decision = response.json()
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.validate(decision, schema)

    checks = {
        "health_ok": health.status_code == 200 and health.json().get("status") == "ok",
        "decision_status_ok": response.status_code == 200,
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
