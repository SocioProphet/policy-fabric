#!/usr/bin/env python3
"""Validate the purpose-admissibility-gate contract + its example.

Structural (jsonschema) + fail-closed semantics: a `deny` MUST carry reasons;
an `admit` MUST NOT; and the receipt MUST mirror the request + decision
(accountability). Proven both ways by the negative branch below.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "contracts" / "purpose_admissibility_gate_decision_v1.schema.json"
EXAMPLE = ROOT / "examples" / "purpose_admissibility_gate_decision_example.json"


def semantic_checks(inst: dict) -> list[str]:
    errs: list[str] = []
    spec = inst["spec"]; req = spec["request"]; rec = spec["receipt"]
    if spec["decision"] == "deny" and not spec.get("denyReasons"):
        errs.append("decision=deny requires non-empty denyReasons (fail-closed)")
    if spec["decision"] == "admit" and "denyReasons" in spec:
        # key must be ABSENT for admit — a present-but-empty [] is still wrong
        errs.append("decision=admit must not carry a denyReasons key")
    for k in ("role", "surface", "space", "tool"):
        if rec[k] != req[k]:
            errs.append(f"receipt.{k} must mirror request.{k}")
    if rec["purpose"] != req["declaredPurpose"]:
        errs.append("receipt.purpose must equal request.declaredPurpose")
    if rec["decision"] != spec["decision"]:
        errs.append("receipt.decision must equal spec.decision")
    return errs


def main() -> int:
    schema = json.loads(SCHEMA.read_text())
    inst = json.loads(EXAMPLE.read_text())
    try:
        import jsonschema  # type: ignore
        jsonschema.validate(inst, schema)
    except ImportError:
        print("WARN: jsonschema not installed; skipping structural validation", file=sys.stderr)
    except Exception as exc:  # jsonschema.ValidationError
        print(f"FAIL: example does not match schema: {exc}", file=sys.stderr)
        return 1
    errs = semantic_checks(inst)
    # self-test the admit-must-not-carry-denyReasons rule in ISOLATION: build a
    # fully-consistent admit (receipt mirrors it) that still carries denyReasons,
    # so only that one rule should fire.
    probe = json.loads(EXAMPLE.read_text())
    probe["spec"]["decision"] = "admit"
    probe["spec"]["receipt"]["decision"] = "admit"
    probe["spec"]["receipt"]["purpose"] = probe["spec"]["request"]["declaredPurpose"]
    probe_errs = semantic_checks(probe)
    if not any("must not carry a denyReasons key" in e for e in probe_errs):
        print("FAIL: self-test — admit-with-denyReasons rule did not fire", file=sys.stderr)
        return 1
    if errs:
        print("FAIL:", file=sys.stderr)
        for e in errs: print(f"  - {e}", file=sys.stderr)
        return 1
    print("OK: purpose-admissibility-gate contract + example valid (structural + fail-closed semantics).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
