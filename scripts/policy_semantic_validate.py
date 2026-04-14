from __future__ import annotations

import json
from pathlib import Path


def _load_runner():
    try:
        from scripts import policy_semantic_validator_tranche_03_runner as runner
        return runner.collect_policy_semantic_findings, "policy_semantic_validator_tranche_03_runner"
    except ImportError:
        try:
            from scripts import policy_semantic_validator as runner
            return runner.collect_policy_semantic_findings, "policy_semantic_validator"
        except ImportError:
            import policy_semantic_validator as runner
            return runner.collect_policy_semantic_findings, "policy_semantic_validator"


def main() -> int:
    import sys

    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
    collect, source = _load_runner()
    findings = collect(root)
    out = {
        "source": source,
        "findingCount": len(findings),
        "failCount": sum(1 for item in findings if item.get("status") == "fail"),
        "warnCount": sum(1 for item in findings if item.get("status") == "warn"),
        "findings": findings,
    }
    print(json.dumps(out, indent=2))
    return 0 if out["failCount"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
