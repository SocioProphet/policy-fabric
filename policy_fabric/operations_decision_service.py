from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

DEFAULT_POLICY_REF = "policy://operations/default-action-gates/v1"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _decision_id(recommendation: dict[str, Any]) -> str:
    basis = json.dumps(recommendation, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(basis.encode("utf-8")).hexdigest()[:16]
    rec_id = recommendation.get("recommendation_id") or recommendation.get("id") or "unknown"
    return f"opdec-{rec_id}-{digest}"


def _recommendation_ref(recommendation: dict[str, Any]) -> str:
    return str(recommendation.get("recommendation_id") or recommendation.get("id") or "unknown")


def _risk_level(recommendation: dict[str, Any]) -> str:
    risk = str(recommendation.get("risk_level") or recommendation.get("risk") or "unknown").lower()
    if risk in {"low", "medium", "high", "critical", "unknown"}:
        return risk
    return "unknown"


def evaluate_operations_action(recommendation: dict[str, Any], *, mode: str = "report_only") -> dict[str, Any]:
    """Evaluate an operations recommendation into a Policy Fabric decision artifact.

    This intentionally defaults to report-only/manual-review. It does not execute remediation.
    """
    rec_ref = _recommendation_ref(recommendation)
    risk = _risk_level(recommendation)
    requested_outcome = str(recommendation.get("requested_outcome") or "manual_review")
    policy_refs = recommendation.get("policy_refs") or [DEFAULT_POLICY_REF]

    if mode != "enforcing":
        outcome = "manual_review"
        reason = "report_only_mode_requires_human_review"
    elif requested_outcome == "allow" and risk in {"low", "medium"}:
        outcome = "allow"
        reason = "enforcing_mode_allows_low_or_medium_risk_request"
    elif requested_outcome == "deny":
        outcome = "deny"
        reason = "requested_outcome_denied"
    else:
        outcome = "manual_review"
        reason = "policy_requires_manual_review"

    return {
        "kind": "ProphetOperationsActionDecision",
        "schema_version": "v1",
        "decision_id": _decision_id(recommendation),
        "decided_at": _utc_now(),
        "recommendation_ref": rec_ref,
        "subject": recommendation.get("subject", {}),
        "proposed_action": recommendation.get("action") or recommendation.get("proposed_action", {}),
        "decision": {
            "outcome": outcome,
            "reason": reason,
            "risk_level": risk,
            "expires_at": None,
        },
        "basis": {
            "policy_refs": policy_refs,
            "health_assessment_ref": recommendation.get("health_assessment_ref"),
            "topology_ref": recommendation.get("topology_ref"),
            "signal_refs": recommendation.get("signal_refs", []),
            "evidence_refs": recommendation.get("evidence_refs", []),
        },
        "controls": {
            "requires_human_approval": outcome != "allow",
            "requires_change_window": bool(recommendation.get("requires_change_window", False)),
            "max_execution_scope": recommendation.get("max_execution_scope"),
            "rollback_required": bool(recommendation.get("rollback_required", False)),
        },
        "audit": {
            "actor": "policy-fabric.operations_decision_service",
            "mode": "automated",
            "notes": "local deterministic evaluator; no remediation execution",
        },
    }
