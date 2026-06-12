#!/usr/bin/env python3
"""Validate the enrichment placement locus-eligibility policy.

Checks:
  - Policy validates against enrichment-placement-locus-policy.v0.1.schema.json
  - All three sensitivity classes are declared (public, internal, sensitive)
  - Locus eligibility is monotonically decreasing (more sensitive = fewer loci)
  - sensitive class never includes attested_fog or burst_cloud
  - internal class never includes burst_cloud
  - local_first_ordering is enforced and locus order starts with 'local'
  - Both required approval gates are present and marked required=true
  - non_claims is non-empty
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_FILE = ROOT / "contracts" / "enrichment-placement-locus-policy.v0.1.schema.json"
DEFAULT_POLICY = (
    ROOT / "examples" / "enrichment" / "enrichment-placement-locus-baseline.policy.json"
)

REQUIRED_SENSITIVITY_CLASSES = {"public", "internal", "sensitive"}
REQUIRED_APPROVAL_GATES = {"burst_cloud_placement", "host_index_writeback"}

# Loci that are forbidden per class regardless of approval
FORBIDDEN_LOCI: dict[str, set[str]] = {
    "sensitive": {"attested_fog", "burst_cloud"},
    "internal": {"burst_cloud"},
    "public": set(),
}

LOCUS_ORDER = ["local", "trusted_private", "attested_fog", "burst_cloud"]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def schema_errors(schema: dict[str, Any], instance: dict[str, Any]) -> list[str]:
    validator = Draft202012Validator(schema)
    return [e.message for e in sorted(validator.iter_errors(instance), key=str)]


def validate_placement_invariants(policy: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    # All three sensitivity classes must be declared
    declared_classes = {
        entry["sensitivityClass"]
        for entry in policy.get("sensitivityClasses", [])
    }
    missing = REQUIRED_SENSITIVITY_CLASSES - declared_classes
    if missing:
        errors.append(f"missing sensitivity classes: {sorted(missing)}")

    # Per-class locus eligibility constraints
    for entry in policy.get("sensitivityClasses", []):
        sc = entry.get("sensitivityClass", "")
        eligible = set(entry.get("eligibleLoci", []))
        forbidden = FORBIDDEN_LOCI.get(sc, set())
        violations = eligible & forbidden
        if violations:
            errors.append(
                f"sensitivity class '{sc}' illegally includes loci: {sorted(violations)}"
            )

        # Every sensitive class must require burst_cloud approval
        if not entry.get("burstCloudRequiresApproval", False):
            errors.append(
                f"sensitivity class '{sc}' must set burstCloudRequiresApproval=true"
            )

    # Monotonic locus set (more sensitive = subset of less sensitive)
    by_class: dict[str, set[str]] = {}
    for entry in policy.get("sensitivityClasses", []):
        by_class[entry.get("sensitivityClass", "")] = set(
            entry.get("eligibleLoci", [])
        )
    if {"public", "internal", "sensitive"} <= set(by_class):
        if not by_class["sensitive"] <= by_class["internal"]:
            errors.append(
                "sensitive eligible loci must be a subset of internal eligible loci"
            )
        if not by_class["internal"] <= by_class["public"]:
            errors.append(
                "internal eligible loci must be a subset of public eligible loci"
            )

    # local_first_ordering must be enforced and start with 'local'
    ordering = policy.get("localFirstOrdering", {})
    if not ordering.get("enforced", False):
        errors.append("localFirstOrdering.enforced must be true")
    locus_order = ordering.get("locusOrder", [])
    if locus_order and locus_order[0] != "local":
        errors.append(
            f"localFirstOrdering.locusOrder must start with 'local' (got '{locus_order[0]}')"
        )

    # Both approval gates must be present and required=true
    gates = policy.get("approvalGates", {})
    for gate in REQUIRED_APPROVAL_GATES:
        if gate not in gates:
            errors.append(f"approvalGates missing required gate: {gate}")
        elif not gates[gate].get("required", False):
            errors.append(
                f"approvalGates.{gate}.required must be true"
            )

    # non_claims must be non-empty
    if not policy.get("nonClaims"):
        errors.append("nonClaims must be non-empty")

    return errors


def main() -> int:
    schema = load_json(SCHEMA_FILE)
    Draft202012Validator.check_schema(schema)

    policy_path = DEFAULT_POLICY
    policy = load_json(policy_path)

    errs = schema_errors(schema, policy)
    if errs:
        print(f"FAIL: schema validation errors in {policy_path.name}:")
        for e in errs:
            print(f"  {e}")
        return 1

    inv_errs = validate_placement_invariants(policy)
    if inv_errs:
        print(f"FAIL: invariant violations in {policy_path.name}:")
        for e in inv_errs:
            print(f"  {e}")
        return 1

    print(f"enrichment placement locus policy validated: {policy_path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
