#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    import jsonschema
except ImportError as exc:
    raise SystemExit("jsonschema is required: python3 -m pip install jsonschema") from exc

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "contracts" / "wallguard-policy-decision.v0.schema.json"
EXAMPLES = ROOT / "examples" / "wallguard-policy"
VALID = EXAMPLES / "valid.same-wall-allow.json"

ALLOW_OUTCOMES = {"allow", "clean_room_release_allowed"}


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} root must be an object")
    return data


def labels_match(left: dict[str, Any], right: dict[str, Any]) -> bool:
    keys = {"client_id", "matter_id", "wall_id"}
    return all(left.get(key) == right.get(key) for key in keys)


def semantic_check(data: dict[str, Any]) -> None:
    context = data["wall_context"]
    subject = data["subject"]
    action = data["action"]
    resources = data["resources"]
    destination = data["destination"]
    decision = data["decision"]
    receipt = data["receipt"]
    policy_ref = data["policy_ref"]

    outcome = decision["outcome"]
    reason_code = decision["reason_code"]

    if receipt["decision_id"] != data["decision_id"]:
        raise ValueError("receipt decision_id must match decision_id")
    if receipt["policy_id"] != policy_ref["policy_id"]:
        raise ValueError("receipt policy_id must match policy_ref policy_id")
    if receipt["policy_version"] != policy_ref["policy_version"]:
        raise ValueError("receipt policy_version must match policy_ref policy_version")
    if receipt["outcome"] != outcome:
        raise ValueError("receipt outcome must match decision outcome")
    if receipt["reason_code"] != reason_code:
        raise ValueError("receipt reason_code must match decision reason_code")

    context_labels = {
        "client_id": context["client_id"],
        "matter_id": context["matter_id"],
        "wall_id": context["wall_id"],
        "confidentiality_class": context["confidentiality_class"],
    }

    subject_wall = context["wall_id"] in set(subject.get("wall_memberships", []))
    all_resources_same_wall = all(labels_match(context_labels, resource["labels"]) for resource in resources)
    destination_same_wall = labels_match(context_labels, destination["labels"])

    if outcome in ALLOW_OUTCOMES:
        if not subject_wall:
            raise ValueError("allow requires subject membership in active wall")
        if subject.get("recusal_state", "none") != "none":
            raise ValueError("allow requires non-recused subject")
        if subject["session_state"] in {"contaminated", "unknown"}:
            raise ValueError("allow requires clean or wall_scoped session state")
        if not all_resources_same_wall:
            raise ValueError("allow requires all resources to match active wall context")
        if not destination_same_wall and action["action_type"] != "clean_room_release":
            raise ValueError("allow requires destination to match active wall unless clean_room_release")
        if reason_code != "same_wall_allowed" and outcome == "allow":
            raise ValueError("plain allow requires same_wall_allowed reason_code")

    if action["action_type"] == "write_memory" and destination["destination_type"] == "memory_compartment":
        dest_class = destination["labels"]["confidentiality_class"]
        if dest_class in {"public", "firm_approved"} and context["confidentiality_class"] in {"client_confidential", "matter_restricted", "wall_restricted"}:
            if outcome in ALLOW_OUTCOMES:
                raise ValueError("restricted context cannot be allowed to write directly to public/firm global memory")

    if outcome in {"deny", "redact", "quarantine", "escalate", "clean_room_release_denied"}:
        if reason_code == "same_wall_allowed":
            raise ValueError("negative decisions must not use same_wall_allowed")


def validate_file(path: Path, schema: dict[str, Any]) -> None:
    data = load_json(path)
    jsonschema.validate(data, schema)
    semantic_check(data)


def main() -> int:
    schema = load_json(SCHEMA)
    jsonschema.Draft202012Validator.check_schema(schema)
    validate_file(VALID, schema)

    invalid = sorted(EXAMPLES.glob("invalid.*.json"))
    if not invalid:
        raise SystemExit("missing invalid WallGuard policy examples")

    unexpected_pass = []
    for path in invalid:
        try:
            validate_file(path, schema)
        except Exception:
            continue
        unexpected_pass.append(str(path.relative_to(ROOT)))

    if unexpected_pass:
        raise SystemExit("invalid WallGuard examples unexpectedly passed: " + ", ".join(unexpected_pass))

    print("OK: WallGuard policy decision examples validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
