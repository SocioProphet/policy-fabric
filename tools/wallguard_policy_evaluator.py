#!/usr/bin/env python3
"""Deterministic WallGuard runtime policy evaluator.

This module is intentionally local and side-effect free. It turns a
WallGuard decision-input-shaped record into a decision/receipt pair suitable
for downstream runtime gates. It does not call external services and it does
not store payload content.
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any

ALLOW_OUTCOMES = {"allow", "clean_room_release_allowed"}
BLOCKING_OUTCOMES = {"deny", "quarantine", "clean_room_release_denied"}
RESTRICTED_CLASSES = {"client_confidential", "matter_restricted", "wall_restricted"}
GLOBAL_CLASSES = {"public", "firm_approved"}

MISSING_CONTEXT = "missing_wall_context"
SUBJECT_OUTSIDE_WALL = "subject_outside_wall"
SUBJECT_RECUSED = "subject_recused"
CONTAMINATED_SESSION = "contaminated_session_state"
RESOURCE_OUTSIDE_WALL = "resource_outside_wall"
PROHIBITED_DESTINATION = "prohibited_destination"
RESTRICTED_GLOBAL_MEMORY = "restricted_global_memory_write"
CLEAN_ROOM_REQUIRED = "clean_room_release_required"
SAME_WALL_ALLOWED = "same_wall_allowed"


def labels_match(left: dict[str, Any], right: dict[str, Any]) -> bool:
    return all(left.get(key) == right.get(key) for key in ("client_id", "matter_id", "wall_id"))


def has_missing_context(record: dict[str, Any]) -> bool:
    context = record.get("wall_context", {})
    required = ("workroom_id", "client_id", "matter_id", "wall_id", "confidentiality_class")
    return any(context.get(key) in {None, "", "unknown"} for key in required)


def active_context_labels(record: dict[str, Any]) -> dict[str, Any]:
    context = record["wall_context"]
    return {
        "client_id": context["client_id"],
        "matter_id": context["matter_id"],
        "wall_id": context["wall_id"],
        "confidentiality_class": context["confidentiality_class"],
    }


def evaluate(record: dict[str, Any]) -> dict[str, Any]:
    decision = copy.deepcopy(record)
    policy_ref = decision["policy_ref"]
    subject = decision["subject"]
    action = decision["action"]
    resources = decision["resources"]
    destination = decision["destination"]

    outcome = "allow"
    reason_code = SAME_WALL_ALLOWED
    reason = "Subject, resource, and destination share the active WallGuard context."

    if has_missing_context(decision):
        outcome, reason_code, reason = "deny", MISSING_CONTEXT, "Missing or unknown wall context fails closed."
    else:
        context_labels = active_context_labels(decision)
        subject_wall = context_labels["wall_id"] in set(subject.get("wall_memberships", []))
        all_resources_same_wall = all(labels_match(context_labels, resource["labels"]) for resource in resources)
        destination_same_wall = labels_match(context_labels, destination["labels"])
        dest_class = destination["labels"].get("confidentiality_class")
        context_class = context_labels.get("confidentiality_class")

        if not subject_wall:
            outcome, reason_code, reason = "deny", SUBJECT_OUTSIDE_WALL, "Subject is not a member of the active wall."
        elif subject.get("recusal_state", "none") != "none":
            outcome, reason_code, reason = "deny", SUBJECT_RECUSED, "Subject is recused or otherwise unavailable for this wall."
        elif subject.get("session_state") in {"contaminated", "unknown"}:
            outcome, reason_code, reason = "quarantine", CONTAMINATED_SESSION, "Session state is contaminated or unknown."
        elif not all_resources_same_wall:
            outcome, reason_code, reason = "deny", RESOURCE_OUTSIDE_WALL, "One or more resources are outside the active wall."
        elif action["action_type"] == "write_memory" and destination.get("destination_type") == "memory_compartment" and dest_class in GLOBAL_CLASSES and context_class in RESTRICTED_CLASSES:
            outcome, reason_code, reason = "deny", RESTRICTED_GLOBAL_MEMORY, "Restricted wall context cannot write directly to global or firm-approved memory."
        elif not destination_same_wall and action["action_type"] != "clean_room_release":
            outcome, reason_code, reason = "deny", PROHIBITED_DESTINATION, "Destination is outside the active wall."
        elif action["action_type"] == "clean_room_release":
            if destination_same_wall:
                outcome, reason_code, reason = "allow", SAME_WALL_ALLOWED, "Same-wall clean-room preparation remains inside the wall."
            else:
                outcome, reason_code, reason = "clean_room_release_allowed", CLEAN_ROOM_REQUIRED, "Clean-room release is explicitly required and allowed for this destination."

    decision["decision"] = {"outcome": outcome, "reason_code": reason_code, "reason": reason}
    decision["receipt"] = {
        "receipt_id": f"wg-receipt-runtime-{decision['decision_id']}",
        "decision_id": decision["decision_id"],
        "policy_id": policy_ref["policy_id"],
        "policy_version": policy_ref["policy_version"],
        "outcome": outcome,
        "reason_code": reason_code,
        "receipt_visibility_class": "internal",
        "evidence_refs": decision.get("evidence_refs", ["SocioProphet/policy-fabric#93"]),
        "redaction_summary": "No restricted payload content included in receipt.",
        "residual_restrictions": [decision.get("wall_context", {}).get("confidentiality_class", "unknown")],
    }
    return decision


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: wallguard_policy_evaluator.py <input.json>", file=sys.stderr)
        return 2
    record = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    print(json.dumps(evaluate(record), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
