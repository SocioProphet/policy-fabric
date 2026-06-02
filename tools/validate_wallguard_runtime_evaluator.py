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
FIXTURES = ROOT / "examples" / "wallguard-runtime"

sys.path.insert(0, str(ROOT / "tools"))
from wallguard_policy_evaluator import evaluate  # noqa: E402

EXPECTED = {
    "same-wall-retrieval.input.json": ("allow", "same_wall_allowed"),
    "cross-wall-collaboration.input.json": ("deny", "resource_outside_wall"),
    "missing-wall-context.input.json": ("deny", "missing_wall_context"),
    "contaminated-session.input.json": ("quarantine", "contaminated_session_state"),
    "restricted-global-memory-write.input.json": ("deny", "prohibited_memory_compartment"),
    "clean-room-release.input.json": ("clean_room_release_allowed", "clean_room_release_required"),
}


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path.relative_to(ROOT)} root must be an object")
    return data


def assert_receipt_consistency(record: dict[str, Any]) -> None:
    decision = record["decision"]
    receipt = record["receipt"]
    policy = record["policy_ref"]
    if receipt["decision_id"] != record["decision_id"]:
        raise ValueError("receipt decision_id must match record decision_id")
    if receipt["policy_id"] != policy["policy_id"]:
        raise ValueError("receipt policy_id must match policy_ref policy_id")
    if receipt["policy_version"] != policy["policy_version"]:
        raise ValueError("receipt policy_version must match policy_ref policy_version")
    if receipt["outcome"] != decision["outcome"]:
        raise ValueError("receipt outcome must match decision outcome")
    if receipt["reason_code"] != decision["reason_code"]:
        raise ValueError("receipt reason_code must match decision reason_code")
    redaction_summary = receipt.get("redaction_summary", "")
    if not redaction_summary or "payload" not in redaction_summary.lower():
        raise ValueError("receipt must include an explicit no-payload redaction summary")


def main() -> int:
    schema = load_json(SCHEMA)
    jsonschema.Draft202012Validator.check_schema(schema)
    validator = jsonschema.Draft202012Validator(schema)

    missing = [name for name in sorted(EXPECTED) if not (FIXTURES / name).exists()]
    if missing:
        raise SystemExit("missing WallGuard runtime fixtures: " + ", ".join(missing))

    results: list[dict[str, str]] = []
    for fixture_name, (expected_outcome, expected_reason) in sorted(EXPECTED.items()):
        fixture = load_json(FIXTURES / fixture_name)
        evaluated = evaluate(fixture)
        errors = sorted(validator.iter_errors(evaluated), key=lambda error: list(error.path))
        if errors:
            rendered = []
            for error in errors:
                location = ".".join(str(part) for part in error.path) or "<root>"
                rendered.append(f"{location}: {error.message}")
            raise ValueError(f"{fixture_name} evaluated output failed schema validation: " + "; ".join(rendered))
        assert_receipt_consistency(evaluated)
        actual_outcome = evaluated["decision"]["outcome"]
        actual_reason = evaluated["decision"]["reason_code"]
        if (actual_outcome, actual_reason) != (expected_outcome, expected_reason):
            raise ValueError(
                f"{fixture_name}: expected {(expected_outcome, expected_reason)} "
                f"got {(actual_outcome, actual_reason)}"
            )
        if actual_outcome in {"deny", "quarantine", "clean_room_release_denied"} and actual_reason == "same_wall_allowed":
            raise ValueError(f"{fixture_name}: blocking outcome cannot use same_wall_allowed")
        results.append({"fixture": fixture_name, "outcome": actual_outcome, "reason_code": actual_reason})

    print(json.dumps({"ok": True, "checked": results}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
