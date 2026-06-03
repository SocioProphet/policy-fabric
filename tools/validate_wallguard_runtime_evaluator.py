#!/usr/bin/env python3
"""Validate the deterministic WallGuard runtime evaluator."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

try:
    import jsonschema
except ImportError as exc:
    raise SystemExit("jsonschema is required: python3 -m pip install jsonschema") from exc

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "contracts" / "wallguard-policy-decision.v0.schema.json"
sys.path.insert(0, str(ROOT / "tools"))
from wallguard_policy_evaluator import evaluate  # noqa: E402


def base_record(case_id: str) -> dict[str, Any]:
    return {
        "schema_version": "0.1",
        "kind": "wallguard_policy_decision",
        "decision_id": case_id,
        "policy_ref": {"policy_id": "wallguard.professional_workroom.v0", "policy_version": "0.1.0", "policy_authority": "SocioProphet/policy-fabric#93"},
        "wall_context": {"workroom_id": "workroom-client-a-matter-x", "client_id": "client-a", "matter_id": "matter-x", "wall_id": "wall-client-a-matter-x", "confidentiality_class": "matter_restricted"},
        "subject": {"subject_id": "agent-alpha", "subject_type": "agent", "wall_memberships": ["wall-client-a-matter-x"], "acknowledgments": ["ack-wall-client-a-matter-x-v0"], "recusal_state": "none", "session_state": "wall_scoped"},
        "action": {"action_type": "retrieve", "enforcement_point": "sherlock_search"},
        "resources": [{"resource_id": "doc-client-a-matter-x-001", "resource_type": "document", "labels": {"client_id": "client-a", "matter_id": "matter-x", "wall_id": "wall-client-a-matter-x", "confidentiality_class": "matter_restricted"}}],
        "destination": {"destination_id": "workroom-client-a-matter-x", "destination_type": "workroom", "labels": {"client_id": "client-a", "matter_id": "matter-x", "wall_id": "wall-client-a-matter-x", "confidentiality_class": "matter_restricted"}},
        "decision": {"outcome": "deny", "reason_code": "same_wall_allowed", "reason": "placeholder"},
        "receipt": {"receipt_id": "placeholder", "decision_id": case_id, "policy_id": "wallguard.professional_workroom.v0", "policy_version": "0.1.0", "outcome": "deny", "reason_code": "same_wall_allowed", "receipt_visibility_class": "internal", "evidence_refs": ["SocioProphet/policy-fabric#93"], "redaction_summary": "placeholder", "residual_restrictions": ["matter_restricted"]},
    }


def cases() -> dict[str, tuple[dict[str, Any], tuple[str, str]]]:
    same = base_record("same-wall-retrieval-001")

    cross = base_record("cross-wall-collaboration-001")
    cross["action"] = {"action_type": "collaborate", "enforcement_point": "agentplane"}
    cross["resources"][0]["resource_type"] = "message"
    cross["resources"][0]["labels"] = {"client_id": "client-b", "matter_id": "matter-y", "wall_id": "wall-client-b-matter-y", "confidentiality_class": "matter_restricted"}
    cross["destination"] = {"destination_id": "agent-beta", "destination_type": "agent", "labels": {"client_id": "client-b", "matter_id": "matter-y", "wall_id": "wall-client-b-matter-y", "confidentiality_class": "matter_restricted"}}

    missing = base_record("missing-wall-context-001")
    missing["wall_context"].update({"workroom_id": "unknown", "matter_id": "unknown", "wall_id": "unknown"})

    contaminated = base_record("contaminated-session-001")
    contaminated["subject"]["session_state"] = "contaminated"
    contaminated["action"] = {"action_type": "read_memory", "enforcement_point": "memory_mesh"}
    contaminated["resources"][0]["resource_type"] = "memory"

    global_write = base_record("restricted-global-memory-write-001")
    global_write["action"] = {"action_type": "write_memory", "enforcement_point": "memory_mesh"}
    global_write["resources"][0]["resource_type"] = "memory"
    global_write["destination"] = {"destination_id": "memory-global-firm-approved", "destination_type": "memory_compartment", "labels": {"client_id": "firm", "matter_id": "global", "wall_id": "none", "confidentiality_class": "firm_approved"}}

    release = base_record("clean-room-release-001")
    release["action"] = {"action_type": "clean_room_release", "enforcement_point": "holmes"}
    release["resources"][0]["resource_type"] = "generated_artifact"
    release["destination"] = {"destination_id": "public-sanitized-artifact-001", "destination_type": "public_artifact", "labels": {"client_id": "firm", "matter_id": "public", "wall_id": "none", "confidentiality_class": "firm_approved"}}

    return {
        "same-wall-retrieval": (same, ("allow", "same_wall_allowed")),
        "cross-wall-collaboration": (cross, ("deny", "resource_outside_wall")),
        "missing-wall-context": (missing, ("deny", "missing_wall_context")),
        "contaminated-session": (contaminated, ("quarantine", "contaminated_session_state")),
        "restricted-global-memory-write": (global_write, ("deny", "prohibited_memory_compartment")),
        "clean-room-release": (release, ("clean_room_release_allowed", "clean_room_release_required")),
    }


def assert_receipt_consistency(record: dict[str, Any]) -> None:
    if record["receipt"]["decision_id"] != record["decision_id"]:
        raise ValueError("receipt decision_id mismatch")
    if record["receipt"]["outcome"] != record["decision"]["outcome"]:
        raise ValueError("receipt outcome mismatch")
    if record["receipt"]["reason_code"] != record["decision"]["reason_code"]:
        raise ValueError("receipt reason_code mismatch")
    if "payload" not in record["receipt"].get("redaction_summary", "").lower():
        raise ValueError("receipt must explicitly state that payload content is excluded")


def main() -> int:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    validator = jsonschema.Draft202012Validator(schema)
    checked = []
    for name, (record, expected) in sorted(cases().items()):
        evaluated = evaluate(record)
        errors = sorted(validator.iter_errors(evaluated), key=lambda error: list(error.path))
        if errors:
            rendered = [f"{'.'.join(str(part) for part in error.path) or '<root>'}: {error.message}" for error in errors]
            raise ValueError(f"{name} failed schema validation: " + "; ".join(rendered))
        assert_receipt_consistency(evaluated)
        actual = (evaluated["decision"]["outcome"], evaluated["decision"]["reason_code"])
        if actual != expected:
            raise ValueError(f"{name}: expected {expected}, got {actual}")
        checked.append({"case": name, "outcome": actual[0], "reason_code": actual[1]})
    print(json.dumps({"ok": True, "checked": checked}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
