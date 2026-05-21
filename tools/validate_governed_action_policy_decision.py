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
SCHEMA = ROOT / "contracts" / "governed-action-policy-decision.v0.schema.json"
EXAMPLES = ROOT / "examples" / "governed-action-policy"
VALID = EXAMPLES / "valid.low-risk-allow.json"
CONFIRMED = {
    "confirmed_official",
    "confirmed_bibliographic",
    "confirmed_pdf",
    "confirmed_artifact",
}
REVIEW_ONLY = {
    "plausible_needs_source",
    "speculative_do_not_use",
}


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} root must be an object")
    return data


def semantic_check(data: dict[str, Any]) -> None:
    policy_input = data["policy_input"]
    result = data["decision"]["result"]
    audit_result = data["audit_payload"]["result"]
    evidence_refs = data["evidence_refs"]

    if audit_result != result:
        raise ValueError("audit result mismatch")

    qualities = {item["source_quality"] for item in evidence_refs}
    all_safe = all(item["implementation_safe"] for item in evidence_refs)

    if policy_input["evidence_grade"] == "research_only" and result == "allow":
        raise ValueError("review-only evidence cannot produce allow")

    if qualities & REVIEW_ONLY and result == "allow":
        raise ValueError("review-only source quality cannot produce allow")

    if result == "allow":
        if policy_input["risk_class"] != "low":
            raise ValueError("allow requires low classification")
        if policy_input["evidence_grade"] != "implementation_safe":
            raise ValueError("allow requires implementation_safe evidence grade")
        if not all_safe:
            raise ValueError("allow requires all evidence refs marked implementation_safe")
        if not qualities <= CONFIRMED:
            raise ValueError("allow requires confirmed source qualities")

    if policy_input["risk_class"] in {"high", "critical"} and result == "allow":
        raise ValueError("upper classifications must not allow in v0")


def validate_file(path: Path, schema: dict[str, Any]) -> None:
    data = load_json(path)
    jsonschema.validate(data, schema)
    semantic_check(data)


def main() -> int:
    schema = load_json(SCHEMA)
    validate_file(VALID, schema)

    invalid = sorted(EXAMPLES.glob("invalid.*.json"))
    if not invalid:
        raise SystemExit("missing invalid governed-action-policy examples")

    unexpected_pass = []
    for path in invalid:
        try:
            validate_file(path, schema)
        except Exception:
            continue
        unexpected_pass.append(str(path.relative_to(ROOT)))

    if unexpected_pass:
        raise SystemExit("invalid examples unexpectedly passed: " + ", ".join(unexpected_pass))

    print("OK: governed action policy decision examples validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
