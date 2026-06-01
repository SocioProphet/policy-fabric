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
SCHEMA = ROOT / "contracts" / "trust_chain_admission_policy_profile.v0.schema.json"
VALID_FIXTURES = [
    ROOT / "examples" / "trust-chain" / "trust-chain-admission-policy.preview.example.json",
    ROOT / "examples" / "trust-chain" / "trust-chain-admission-policy.production.example.json",
]
INVALID_FIXTURES = [
    ROOT / "examples" / "trust-chain" / "trust-chain-admission-policy.production.invalid.json",
]

PRODUCTION_REQUIRED_EVIDENCE = {
    "sbom_ref",
    "vex_ref",
    "lockfile_ref",
    "signature_ref",
    "scan_record_ref",
    "policy_profile_ref",
    "agentplane_validation_ref",
    "runtime_receipt_ref",
    "promotion_evidence_ref",
    "rollback_evidence_ref",
}


def load(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"fixture must be an object: {path}")
    return data


def validate_semantics(doc: dict[str, Any], path: Path) -> None:
    scope = doc.get("scope", {})
    required_evidence = doc.get("required_evidence", {})
    posture = doc.get("posture_requirements", {})
    exception = doc.get("exception_policy", {})
    decision = doc.get("decision_policy", {})

    if scope.get("environment") == "production" and scope.get("risk_tier") == "regulated_enterprise":
        missing = sorted(key for key in PRODUCTION_REQUIRED_EVIDENCE if required_evidence.get(key) is not True)
        if missing:
            raise ValueError(f"{path}: production regulated profile requires evidence flags: {missing}")
        if posture.get("vulnerability_posture") != "no_known_blocking_findings":
            raise ValueError(f"{path}: production regulated profile requires no_known_blocking_findings")
        if posture.get("patch_posture") != "current_for_scope":
            raise ValueError(f"{path}: production regulated profile requires current_for_scope")
        if posture.get("source_channel_trust") != "trusted":
            raise ValueError(f"{path}: production regulated profile requires trusted source_channel_trust")
        if posture.get("promotion_posture") != "production_allowed":
            raise ValueError(f"{path}: production regulated profile requires production_allowed")
        if exception.get("requires_authority") is not True:
            raise ValueError(f"{path}: production regulated exceptions require authority")
        if exception.get("requires_expiration") is not True:
            raise ValueError(f"{path}: production regulated exceptions require expiration")
        if exception.get("requires_compensating_control") is not True:
            raise ValueError(f"{path}: production regulated exceptions require compensating control")
        if exception.get("requires_review_evidence") is not True:
            raise ValueError(f"{path}: production regulated exceptions require review evidence")
        if decision.get("missing_required_evidence") != "deny":
            raise ValueError(f"{path}: production regulated missing evidence must deny")
        if decision.get("restricted_posture") != "deny":
            raise ValueError(f"{path}: production regulated restricted posture must deny")
        if decision.get("satisfied") != "allow":
            raise ValueError(f"{path}: production regulated satisfied posture must allow")


def validate_valid_fixture(schema: dict[str, Any], path: Path) -> list[dict[str, Any]]:
    try:
        doc = load(path)
        jsonschema.validate(doc, schema)
        validate_semantics(doc, path)
        return [{"check_id": f"valid:{path.name}", "passed": True, "diagnostics": []}]
    except Exception as exc:  # noqa: BLE001
        return [{"check_id": f"valid:{path.name}", "passed": False, "diagnostics": [str(exc)]}]


def validate_invalid_fixture(schema: dict[str, Any], path: Path) -> list[dict[str, Any]]:
    try:
        doc = load(path)
        jsonschema.validate(doc, schema)
        validate_semantics(doc, path)
    except Exception as exc:  # noqa: BLE001
        return [{"check_id": f"invalid:{path.name}", "passed": True, "diagnostics": [str(exc)]}]
    return [{"check_id": f"invalid:{path.name}", "passed": False, "diagnostics": ["invalid fixture unexpectedly passed"]}]


def main() -> int:
    schema = load(SCHEMA)
    results: list[dict[str, Any]] = []
    for path in VALID_FIXTURES:
        results.extend(validate_valid_fixture(schema, path))
    for path in INVALID_FIXTURES:
        results.extend(validate_invalid_fixture(schema, path))
    passed = all(item["passed"] for item in results)
    print(json.dumps({"validator": "policy-fabric.trust-chain-admission-policy.v0.1", "passed": passed, "results": results}, indent=2, sort_keys=True))
    print(("PASS" if passed else "FAIL") + ": trust-chain admission policy profiles")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
