#!/usr/bin/env python3
"""Validate broker PolicyDecision example against schema."""

from __future__ import annotations

from pathlib import Path
import json

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "contracts" / "schemas" / "broker-policy-decision.schema.json"
EXAMPLE = ROOT / "examples" / "broker-policy-decision.example.json"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    schema = load_json(SCHEMA)
    example = load_json(EXAMPLE)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(example), key=lambda error: list(error.path))
    if errors:
        print("Broker PolicyDecision example failed validation:")
        for error in errors:
            location = ".".join(str(part) for part in error.path) or "<root>"
            print(f" - {location}: {error.message}")
        return 1
    print("Broker PolicyDecision example validates against schema.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
