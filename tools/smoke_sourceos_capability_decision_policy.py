#!/usr/bin/env python3
from __future__ import annotations

import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "tools" / "validate_sourceos_capability_decision_policy.py"
VALID_POLICY = ROOT / "examples" / "sourceos" / "sourceos-capability-decision-baseline.policy.json"
INVALID_POLICY = ROOT / "examples" / "sourceos" / "invalid" / "sourceos-capability-decision-missing-remote-telemetry-deny.policy.json"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def main() -> int:
    valid = run("--policy", str(VALID_POLICY))
    if valid.returncode != 0:
        print(valid.stdout)
        print(valid.stderr, file=sys.stderr)
        raise SystemExit("valid SourceOS capability decision baseline failed validation")

    invalid = run("--policy", str(INVALID_POLICY))
    if invalid.returncode == 0:
        print(invalid.stdout)
        raise SystemExit("invalid SourceOS capability decision policy unexpectedly passed validation")

    combined = f"{invalid.stdout}\n{invalid.stderr}"
    expected_markers = [
        "telemetry.emit.remote.default",
        "CAPABILITY_DENIED_REMOTE_TELEMETRY_DEFAULT",
    ]
    if not any(marker in combined for marker in expected_markers):
        print(invalid.stdout)
        print(invalid.stderr, file=sys.stderr)
        raise SystemExit("invalid policy failed without the expected remote telemetry denial diagnostic")

    print("SourceOS capability decision policy smoke test passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
