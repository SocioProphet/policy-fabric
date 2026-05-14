"""Smoke validator for constitutional_policy_engine.py.

Run from the repository root:

    python3 tools/validate_constitutional_policy_engine.py

This is a tranche-level smoke check, not a full scientific test suite.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.constitutional_policy_engine import _self_test  # noqa: E402


EXPECTED_PASS = {
    "A1": True,
    "A3": True,
    "A4": False,  # fails by design on the synthetic unstable Jacobian
    "A5": True,
    "A7": True,
}


def main() -> int:
    results = _self_test()
    failures: list[str] = []

    for axiom, expected in EXPECTED_PASS.items():
        actual = results.get(axiom, {}).get("passed")
        if actual is not expected:
            failures.append(f"{axiom}: expected passed={expected!r}, got {actual!r}")

    a7 = results.get("A7", {})
    if "p_value" in a7:
        failures.append("A7 still emits p_value; expected nonincrease_indicator")
    if "nonincrease_indicator" not in a7:
        failures.append("A7 missing nonincrease_indicator")

    print(json.dumps(results, indent=2, sort_keys=True))
    if failures:
        print("constitutional policy engine smoke validation failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
