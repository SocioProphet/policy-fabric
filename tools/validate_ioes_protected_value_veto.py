#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

try:
    import jsonschema
except Exception as exc:  # pragma: no cover
    print(f"dependency error: {exc}", file=sys.stderr)
    raise

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "contracts" / "ioes-protected-value-veto-profile.schema.json"
VALID_FIXTURES = [
    ROOT / "examples" / "ioes" / "ioes-protected-value-veto.valid.json",
]
REJECTED_FIXTURES = [
    ROOT / "examples" / "ioes" / "ioes-protected-value-veto.rejected.consent-required.json",
]

REQUIRED_PROTECTED_VALUES = {
    "human_dignity",
    "consent",
    "stewardship_without_ownership",
    "developmental_integrity",
    "ecological_accountability",
    "provenance",
    "succession",
    "agent_boundedness",
}


def load(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"fixture must be an object: {path}")
    return data


def require_rule(doc: dict[str, Any], value_name: str, evidence_ref: str, path: Path) -> None:
    rule = doc.get("protected_values", {}).get(value_name, {})
    if rule.get("enabled") is not True:
        raise ValueError(f"{path}: protected value {value_name} must be enabled")
    if rule.get("veto_capable") is not True:
        raise ValueError(f"{path}: protected value {value_name} must be veto-capable")
    evidence = rule.get("required_evidence", [])
    if evidence_ref not in evidence:
        raise ValueError(f"{path}: protected value {value_name} requires {evidence_ref}")


def validate_semantics(doc: dict[str, Any], path: Path) -> None:
    scope = doc.get("scope", {})
    protected_values = doc.get("protected_values", {})
    decision = doc.get("decision_policy", {})
    fail_closed = doc.get("fail_closed_defaults", {})
    exception = doc.get("exception_policy", {})

    missing_values = sorted(REQUIRED_PROTECTED_VALUES - set(protected_values.keys()))
    if missing_values:
        raise ValueError(f"{path}: missing protected values: {missing_values}")

    for value_name in REQUIRED_PROTECTED_VALUES:
        rule = protected_values.get(value_name, {})
        if rule.get("enabled") is not True:
            raise ValueError(f"{path}: protected value {value_name} must be enabled")
        if rule.get("veto_capable") is not True:
            raise ValueError(f"{path}: protected value {value_name} must be veto-capable")

    if scope.get("human_impacting") is True:
        if fail_closed.get("deny_on_missing_consent") is not True:
            raise ValueError(f"{path}: human-impacting profiles must deny on missing consent")
        if fail_closed.get("deny_on_missing_authority") is not True:
            raise ValueError(f"{path}: human-impacting profiles must deny on missing authority")
        if fail_closed.get("deny_on_unreplayable_human_impact") is not True:
            raise ValueError(f"{path}: human-impacting profiles must deny unreplayable human-impacting actions")
        if fail_closed.get("candidate_only_for_model_only_canonical_claims") is not True:
            raise ValueError(f"{path}: model-only canonical claims must remain candidate-only")

    action_families = set(scope.get("action_families", []))
    if "identity.projection.emit" in action_families:
        require_rule(doc, "consent", "consent_receipt", path)
        if decision.get("missing_consent") != "deny":
            raise ValueError(f"{path}: identity projection must deny missing consent")
        if decision.get("outward_projection") not in {"allow_with_consent", "review"}:
            raise ValueError(f"{path}: outward projection requires consent or review posture")

    if "stewardship.edge.assign" in action_families or "stewardship.edge.transfer" in action_families:
        require_rule(doc, "stewardship_without_ownership", "keeper_log_ref", path)
        require_rule(doc, "stewardship_without_ownership", "authority_ref", path)
        require_rule(doc, "succession", "succession_rule_ref", path)
        if decision.get("stewardship_transfer") not in {"review", "allow_with_succession_rule"}:
            raise ValueError(f"{path}: stewardship transfer must require review or succession rule")

    if "ontogenesis.state.update" in action_families:
        require_rule(doc, "developmental_integrity", "review_record_ref", path)
        if decision.get("developmental_state_mutation") not in {"review", "allow_with_explicit_rule"}:
            raise ValueError(f"{path}: developmental mutation requires review or explicit rule")

    if "gaia.dependency.record" in action_families:
        require_rule(doc, "ecological_accountability", "gaia_dependency_ref", path)

    if "learning.artifact.promote" in action_families:
        require_rule(doc, "provenance", "evidence_ref", path)
        require_rule(doc, "succession", "succession_rule_ref", path)
        if decision.get("model_only_evidence") != "candidate_only":
            raise ValueError(f"{path}: model-only learning claims must remain candidate-only")

    if "agent.bundle.execute" in action_families:
        require_rule(doc, "agent_boundedness", "authority_ref", path)
        require_rule(doc, "agent_boundedness", "replay_evidence_ref", path)

    if exception.get("allowed") is True:
        if exception.get("requires_authority") is not True:
            raise ValueError(f"{path}: exceptions require authority")
        if exception.get("requires_expiration") is not True:
            raise ValueError(f"{path}: exceptions require expiration")
        if exception.get("requires_review_evidence") is not True:
            raise ValueError(f"{path}: exceptions require review evidence")


def validate_valid_fixture(schema: dict[str, Any], path: Path) -> list[dict[str, Any]]:
    try:
        doc = load(path)
        jsonschema.validate(doc, schema)
        validate_semantics(doc, path)
        return [{"check_id": f"valid:{path.name}", "passed": True, "diagnostics": []}]
    except Exception as exc:  # noqa: BLE001
        return [{"check_id": f"valid:{path.name}", "passed": False, "diagnostics": [str(exc)]}]


def validate_rejected_fixture(schema: dict[str, Any], path: Path) -> list[dict[str, Any]]:
    try:
        doc = load(path)
        jsonschema.validate(doc, schema)
        validate_semantics(doc, path)
    except Exception as exc:  # noqa: BLE001
        return [{"check_id": f"rejected:{path.name}", "passed": True, "diagnostics": [str(exc)]}]
    return [{"check_id": f"rejected:{path.name}", "passed": False, "diagnostics": ["rejected fixture unexpectedly passed"]}]


def main() -> int:
    schema = load(SCHEMA)
    results: list[dict[str, Any]] = []
    for path in VALID_FIXTURES:
        results.extend(validate_valid_fixture(schema, path))
    for path in REJECTED_FIXTURES:
        results.extend(validate_rejected_fixture(schema, path))
    passed = all(item["passed"] for item in results)
    print(json.dumps({"validator": "policy-fabric.ioes-protected-value-veto.v0.1", "passed": passed, "results": results}, indent=2, sort_keys=True))
    print(("PASS" if passed else "FAIL") + ": IOES protected-value veto profiles")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
