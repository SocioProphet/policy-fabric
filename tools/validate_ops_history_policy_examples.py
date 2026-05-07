#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "ops-history" / "policy-decisions.example.json"
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
    "deny-writeback",
    "redaction-required",
    "require-human-approval",
}


def main() -> int:
    data = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    decisions = data.get("decisions", [])
    if not decisions:
        raise SystemExit("No OpsHistory policy decisions found")
    seen: set[str] = set()
    for decision in decisions:
        family = decision.get("decisionFamily")
        if family not in REQUIRED_FAMILIES:
            raise SystemExit(f"Unexpected decisionFamily: {family}")
        if decision.get("outcome") not in ALLOWED_OUTCOMES:
            raise SystemExit(f"Unexpected outcome for {family}: {decision.get('outcome')}")
        if not str(decision.get("decisionId", "")).startswith("urn:srcos:policy-decision:"):
            raise SystemExit(f"Invalid decisionId for {family}")
        if not decision.get("inputRefs"):
            raise SystemExit(f"Missing inputRefs for {family}")
        if not decision.get("obligations"):
            raise SystemExit(f"Missing obligations for {family}")
        seen.add(family)
    missing = sorted(REQUIRED_FAMILIES - seen)
    if missing:
        raise SystemExit(f"Missing OpsHistory policy families: {missing}")
    print(json.dumps({"ok": True, "families": sorted(seen)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
