#!/usr/bin/env python3
"""Validate Professional Policy Decision examples against schema."""

from __future__ import annotations

from pathlib import Path
import json

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "contracts" / "schemas" / "professional-policy-decision.schema.json"
EXAMPLES = [
    ROOT / "examples" / "professional-policy-decision.allow.example.json",
    ROOT / "examples" / "professional-policy-decision.require-approval.example.json",
    ROOT / "examples" / "professional-policy-decision.deny.example.json",
]


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    schema = load_json(SCHEMA)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)

    failures = []
    for example_path in EXAMPLES:
        example = load_json(example_path)
        errors = sorted(validator.iter_errors(example), key=lambda error: list(error.path))
        if errors:
            for error in errors:
                location = ".".join(str(part) for part in error.path) or "<root>"
                failures.append(f"{example_path.relative_to(ROOT)} {location}: {error.message}")
        else:
            print(f"ok: {example_path.relative_to(ROOT)} validates against {SCHEMA.relative_to(ROOT)}")

    if failures:
        print("Professional PolicyDecision examples failed validation:")
        for failure in failures:
            print(f" - {failure}")
        return 1

    print("Professional PolicyDecision examples validate against schema.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
