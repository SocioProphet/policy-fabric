from __future__ import annotations

import json
from pathlib import Path

try:
    import policy_semantic_validator as base_validator
    from policy_semantic_tranche_03 import collect_tranche3_findings
except ImportError:
    from scripts import policy_semantic_validator as base_validator
    from scripts.policy_semantic_tranche_03 import collect_tranche3_findings


def _finding(check_id: str, status: str, severity: str, code: str, message: str, artifact_ref: str | None = None) -> dict:
    item = {
        "id": check_id,
        "status": status,
        "severity": severity,
        "code": code,
        "message": message,
    }
    if artifact_ref:
        item["artifactRef"] = artifact_ref
    return item


def _ok(check_id: str, message: str, artifact_ref: str | None = None, code: str = "PFV000_POLICY_SEMANTICS_OK") -> dict:
    return _finding(check_id, "pass", "info", code, message, artifact_ref)


def _fail(check_id: str, code: str, message: str, artifact_ref: str | None = None) -> dict:
    return _finding(check_id, "fail", "error", code, message, artifact_ref)


def _warn(check_id: str, code: str, message: str, artifact_ref: str | None = None) -> dict:
    return _finding(check_id, "warn", "warn", code, message, artifact_ref)


def _translate_tranche3_findings(raw_findings: list[dict], artifact_ref: str) -> list[dict]:
    translated: list[dict] = []
    if not raw_findings:
        return [_ok("policy:tranche3", "no tranche-3 precedence/cardinality/rollout issues detected", artifact_ref, "PFV019_TRANCHE3_OK")]

    for index, raw in enumerate(raw_findings, start=1):
        code = raw.get("code", "PFV020_RULE_PRECEDENCE_REQUIRED")
        message = raw.get("message", "")
        check_id = f"policy:tranche3:{index}"
        if code == "PFV021_RULE_PRECEDENCE_CONFLICT":
            translated.append(_fail(check_id, code, message, artifact_ref))
        elif code in {
            "PFV020_RULE_PRECEDENCE_REQUIRED",
            "PFV022_SELECTOR_CARDINALITY_OVERMATCH",
            "PFV023_SELECTOR_CARDINALITY_UNDERSPECIFIED",
            "PFV024_ROLLOUT_SUBSUMPTION_WARNING",
            "PFV025_ROLLOUT_SHADOW_CONFLICT",
            "PFV026_EXPLAIN_DECISION_INCOMPLETE",
        }:
            translated.append(_warn(check_id, code, message, artifact_ref))
        else:
            translated.append(_warn(check_id, code, message, artifact_ref))
    return translated


def collect_policy_semantic_findings(root: Path) -> list[dict]:
    findings = list(base_validator.collect_policy_semantic_findings(root))
    policy_ref = "examples/policy_fabric_policy_v2_enhanced_example.json"
    policy = json.loads((root / policy_ref).read_text())
    findings.extend(_translate_tranche3_findings(collect_tranche3_findings(policy), policy_ref))
    return findings


if __name__ == "__main__":
    import sys

    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
    findings = collect_policy_semantic_findings(root)
    print(json.dumps({"findings": findings}, indent=2))
    raise SystemExit(0 if not any(item["status"] == "fail" for item in findings) else 1)
