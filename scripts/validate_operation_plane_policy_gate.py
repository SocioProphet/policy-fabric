from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]

PAIRS = [
    (
        "contracts/operation_plane_policy_gate_v1.schema.json",
        "examples/operation_plane_policy_gate_record_example.json",
    ),
    (
        "contracts/operation_plane_policy_gate_v1.schema.json",
        "examples/operation_plane_policy_eval_request_example.json",
    ),
    (
        "contracts/operation_plane_policy_gate_v1.schema.json",
        "examples/operation_plane_policy_eval_response_example.json",
    ),
]


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def main() -> int:
    for schema_rel, example_rel in PAIRS:
        jsonschema.validate(load_json(example_rel), load_json(schema_rel))
        print(f"[OK] {example_rel} validates against {schema_rel}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
