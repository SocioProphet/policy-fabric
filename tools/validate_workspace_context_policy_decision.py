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
SCHEMA = ROOT / "contracts" / "workspace-context-policy-decision.v0.schema.json"
EXAMPLES = ROOT / "examples" / "workspace-context-policy"
VALID = EXAMPLES / "valid.project-modify.json"


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} root must be an object")
    return data


def semantic_check(data: dict[str, Any]) -> None:
    request = data["request"]
    result = data["decision"]["result"]
    audit_result = data["audit_payload"]["result"]
    evidence_refs = data["evidence_refs"]
    constraints = data.get("runtime_constraints", [])

    if audit_result != result:
        raise ValueError("audit result mismatch")

    if result == "allow" and not evidence_refs:
        raise ValueError("allow requires evidence refs")

    if request["operation"] == "workspace.context.recall.promote" and result == "allow":
        raise ValueError("recall promotion requires modify or escalate in v0")

    if request["release_mode"] == "public" and result == "allow":
        raise ValueError("public release cannot be unrestricted allow in v0")

    if request["sensitivity"] in {"confidential", "restricted"} and request["release_mode"] == "public":
        if result not in {"deny", "escalate"}:
            raise ValueError("confidential or restricted public release must deny or escalate")

    if result == "modify" and not constraints:
        raise ValueError("modify requires runtime constraints")

    if result == "deny" and not data["decision"]["reason"]:
        raise ValueError("deny requires reason")


def validate_file(path: Path, schema: dict[str, Any]) -> None:
    data = load_json(path)
    jsonschema.validate(data, schema)
    semantic_check(data)


def main() -> int:
    schema = load_json(SCHEMA)
    validate_file(VALID, schema)

    invalid = sorted(EXAMPLES.glob("invalid.*.json"))
    if not invalid:
        raise SystemExit("missing invalid workspace-context-policy examples")

    unexpected_pass = []
    for path in invalid:
        try:
            validate_file(path, schema)
        except Exception:
            continue
        unexpected_pass.append(str(path.relative_to(ROOT)))

    if unexpected_pass:
        raise SystemExit("invalid examples unexpectedly passed: " + ", ".join(unexpected_pass))

    print("OK: workspace context policy decision examples validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
