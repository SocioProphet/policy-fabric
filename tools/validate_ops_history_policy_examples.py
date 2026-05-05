#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_DIR = ROOT / "examples" / "ops-history"
REQUIRED_FAMILIES = {
    "replicate_event",
    "hydrate_context",
    "write_memory",
    "redact_event",
    "bridge_event",
    "export_artifact",
    "browser_event_export",
    "receipt_event_export",
}
ALLOWED_OUTCOMES = {
    "allow",
    "deny",
    "metadata-only",
    "summary-only",
    "ref-only",
    "require-human-approval",
    "deny-writeback",
    "redaction-required",
}


def validate_example(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    family = data.get("decisionFamily")
    if family not in REQUIRED_FAMILIES:
        raise ValueError(f"{path}: unexpected decisionFamily {family!r}")
    if not str(data.get("decisionId", "")).startswith("urn:srcos:policy-decision:"):
        raise ValueError(f"{path}: decisionId must use urn:srcos:policy-decision:")
    if data.get("outcome") not in ALLOWED_OUTCOMES:
        raise ValueError(f"{path}: unexpected outcome {data.get('outcome')!r}")
    if not isinstance(data.get("input"), dict):
        raise ValueError(f"{path}: input must be an object")
    if not isinstance(data.get("obligations"), list) or not data["obligations"]:
        raise ValueError(f"{path}: obligations must be a non-empty list")
    if not isinstance(data.get("evidenceRefs"), list):
        raise ValueError(f"{path}: evidenceRefs must be a list")
    return family


def main() -> int:
    seen: set[str] = set()
    for path in sorted(EXAMPLE_DIR.glob("*.json")):
        seen.add(validate_example(path))
    missing = sorted(REQUIRED_FAMILIES - seen)
    if missing:
        raise SystemExit(f"Missing OpsHistory policy examples: {missing}")
    print(json.dumps({"ok": True, "families": sorted(seen)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
