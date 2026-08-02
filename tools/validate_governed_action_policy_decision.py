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

# Per-method-family forbidden-use claims, sourced from the negative rules in
# sociosphere/docs/integration/neurosymbolic-chronos-alignment.md as evidenced
# in policy-fabric#97. Policy Fabric does not own this taxonomy or its
# doctrine -- CHRONOS/sociosphere does -- but it is the admission authority,
# so a decision whose evidence carries one of these claims must not resolve
# to "allow"; it must deny/modify/escalate instead.
#
# Two claims are named explicitly against a specific method family in #97:
#   - dsr_dsp / live_controller_pre_admission: "run a symbolic policy as a
#     live controller before governance admission" is forbidden for DSR/DSP.
#   - neurasp / stable_model_bypasses_admission: "bypass policy admission...
#     because ASP returned a stable model" is forbidden for NeurASP.
# The remaining two claims are the alignment doc's general negative rules
# ("a fuzzy satisfaction score is promoted as truth", "a symbolic derivation
# is treated as policy admission"); they are applied here to every method
# family in the taxonomy since nothing in #97 scopes them more narrowly, and
# to LTN/LNN specifically for soft-constraint claims since both families are
# defined by producing fuzzy/soft satisfaction scores rather than admitted
# truth values.
FORBIDDEN_BY_METHOD_FAMILY = {
    "kautz": {"symbolic_derivation_as_admission"},
    "ltn": {"symbolic_derivation_as_admission", "soft_constraint_promoted_as_truth"},
    "lnn": {"symbolic_derivation_as_admission", "soft_constraint_promoted_as_truth"},
    "neurasp": {"symbolic_derivation_as_admission", "stable_model_bypasses_admission"},
    "satnet": {"symbolic_derivation_as_admission"},
    "dilp": {"symbolic_derivation_as_admission"},
    "don_rrn": {"symbolic_derivation_as_admission"},
    "dsr_dsp": {"symbolic_derivation_as_admission", "live_controller_pre_admission"},
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

    for item in evidence_refs:
        method_family = item.get("method_family")
        claim = item.get("method_family_claim", "none")
        if claim == "none":
            continue
        # A non-"none" claim without a method_family used to `continue` here,
        # silently bypassing the gate entirely (Copilot review, policy-fabric#98).
        # The schema now rejects this combination too, but fail fast here as
        # well rather than depend solely on schema validation running first.
        if method_family is None:
            raise ValueError(
                f"method_family_claim '{claim}' is set without a method_family; "
                "the method-family gate cannot be evaluated for this evidence ref"
            )
        if method_family not in FORBIDDEN_BY_METHOD_FAMILY:
            # Fail closed: an unrecognized method_family must not be treated as
            # having an empty forbidden-claims set (Copilot review, policy-fabric#98).
            raise ValueError(
                f"unrecognized method_family '{method_family}'; refusing to assume "
                "it has no forbidden-use claims"
            )
        forbidden_claims = FORBIDDEN_BY_METHOD_FAMILY[method_family]
        if claim in forbidden_claims and result == "allow":
            raise ValueError(
                f"method_family '{method_family}' forbids '{claim}' per "
                "neurosymbolic-chronos-alignment.md; decision must not allow"
            )


def validate_file(path: Path, schema: dict[str, Any]) -> None:
    data = load_json(path)
    jsonschema.validate(data, schema)
    semantic_check(data)


def main() -> int:
    schema = load_json(SCHEMA)

    valid = sorted(EXAMPLES.glob("valid.*.json"))
    if VALID not in valid:
        raise SystemExit(f"missing canonical valid fixture: {VALID}")
    for path in valid:
        validate_file(path, schema)

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
