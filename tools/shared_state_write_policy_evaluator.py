#!/usr/bin/env python3
"""Deterministic evaluator for the shared-state write / live-activation authorization policy.

Policy: shared_state.live_activation_authorization.v0

Shared-state / live-infrastructure WRITES require explicit authorized-principal
authorization. A relayed coordinator instruction or an agent-to-agent instruction
does NOT satisfy the authorization bar. Live activation (running production
workflows, mutating a cluster/namespace, writing to a shared graph store or shared
ledger) must be gated to the authorized principal. Automated/agent actors may only
READ-probe shared state and must ship changes as reviewable artifacts (PRs against
mock/test transports) whose live activation is a separate, explicitly-authorized
step.

The evaluator is pure and deterministic: evaluate(record) -> record augmented with a
`decision` and a `receipt`. It fails closed on missing/unknown context.
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any

# Mutating actions against shared state / live infrastructure.
WRITE_ACTIONS = {
    "write_shared_graph",
    "write_shared_ledger",
    "mutate_namespace",
    "run_production_workflow",
    "port_forward",
    "activate",
}
# Non-mutating probes are always permitted, including against live shared state.
READ_ACTIONS = {"read_probe", "list", "get"}
# Reviewable artifacts (the compliant path for automated actors).
ARTIFACT_ACTIONS = {"ship_reviewable_artifact", "open_pull_request"}

# Target kinds that constitute shared state / live infrastructure.
SHARED_LIVE_KINDS = {
    "shared_graph_store",
    "shared_ledger",
    "cluster_namespace",
    "production_workflow",
}
NON_LIVE_ENVIRONMENTS = {"mock", "test"}

# Outcomes
ALLOW = "allow"
DENY = "deny"

# Reason codes
READ_PROBE_ALLOWED = "read_probe_allowed"
GATED_ARTIFACT_ALLOWED = "gated_artifact_allowed"
MOCK_TRANSPORT_WRITE_ALLOWED = "mock_transport_write_allowed"
LIVE_ACTIVATION_AUTHORIZED = "live_activation_authorized"
SHARED_WRITE_REQUIRES_AUTHORIZED_PRINCIPAL = "shared_write_requires_authorized_principal"
RELAYED_AUTHORIZATION_INSUFFICIENT = "relayed_authorization_insufficient"
AGENT_TO_AGENT_AUTHORIZATION_INSUFFICIENT = "agent_to_agent_authorization_insufficient"
NON_EXPLICIT_ACTIVATION = "non_explicit_activation"
ARTIFACT_TARGETS_LIVE_ENDPOINT = "artifact_targets_live_endpoint"
MISSING_AUTHORIZATION_CONTEXT = "missing_authorization_context"

_UNKNOWN = {None, "", "unknown"}


def _has_missing_context(record: dict[str, Any]) -> bool:
    action = record.get("action", {})
    target = record.get("target", {})
    authz = record.get("authorization", {})
    if action.get("action_type") in _UNKNOWN:
        return True
    if target.get("target_kind") in _UNKNOWN or target.get("environment") in _UNKNOWN:
        return True
    if authz.get("source") in _UNKNOWN:
        return True
    return False


def _principal_authorized(subject: dict[str, Any], authz: dict[str, Any]) -> bool:
    """A live activation is authorized only when the acting subject IS an authorized
    principal AND the authorization is an explicit, principal-scoped activation grant."""
    return (
        subject.get("actor_class") == "authorized_principal"
        and authz.get("source") == "authorized_principal"
        and authz.get("explicit_activation") is True
        and bool(authz.get("principal_id"))
    )


def evaluate(record: dict[str, Any]) -> dict[str, Any]:
    decision = copy.deepcopy(record)
    policy_ref = decision["policy_ref"]
    subject = decision["subject"]
    action = decision["action"]
    target = decision["target"]
    authz = decision["authorization"]

    if _has_missing_context(decision):
        outcome, reason_code, reason = (
            DENY,
            MISSING_AUTHORIZATION_CONTEXT,
            "Missing or unknown action/target/authorization context fails closed.",
        )
    else:
        action_type = action["action_type"]
        target_kind = target["target_kind"]
        environment = target["environment"]
        auth_source = authz["source"]

        is_shared_live = environment == "live" and target_kind in SHARED_LIVE_KINDS

        if action_type in READ_ACTIONS:
            # Read-probing shared state is permitted for any actor.
            outcome, reason_code, reason = (
                ALLOW,
                READ_PROBE_ALLOWED,
                "Read-probe of shared state is permitted; no shared-state mutation performed.",
            )
        elif action_type in ARTIFACT_ACTIONS:
            if environment in NON_LIVE_ENVIRONMENTS:
                outcome, reason_code, reason = (
                    ALLOW,
                    GATED_ARTIFACT_ALLOWED,
                    "Change shipped as a reviewable artifact against a mock/test transport; live activation remains a separate step.",
                )
            else:
                outcome, reason_code, reason = (
                    DENY,
                    ARTIFACT_TARGETS_LIVE_ENDPOINT,
                    "Reviewable artifacts must target mock/test transports, not live endpoints.",
                )
        elif action_type in WRITE_ACTIONS:
            if not is_shared_live:
                outcome, reason_code, reason = (
                    ALLOW,
                    MOCK_TRANSPORT_WRITE_ALLOWED,
                    "Write targets a mock/test transport, not live shared state.",
                )
            elif _principal_authorized(subject, authz):
                outcome, reason_code, reason = (
                    ALLOW,
                    LIVE_ACTIVATION_AUTHORIZED,
                    "Live activation is gated to the authorized principal via an explicit activation grant.",
                )
            elif subject.get("actor_class") != "authorized_principal":
                # Automated/agent actor attempting a live shared-state write.
                if auth_source == "relayed_coordinator":
                    outcome, reason_code, reason = (
                        DENY,
                        RELAYED_AUTHORIZATION_INSUFFICIENT,
                        "A relayed coordinator instruction does not satisfy the authorized-principal bar for a live shared-state write.",
                    )
                elif auth_source == "agent_to_agent":
                    outcome, reason_code, reason = (
                        DENY,
                        AGENT_TO_AGENT_AUTHORIZATION_INSUFFICIENT,
                        "An agent-to-agent instruction does not satisfy the authorized-principal bar for a live shared-state write.",
                    )
                else:
                    outcome, reason_code, reason = (
                        DENY,
                        SHARED_WRITE_REQUIRES_AUTHORIZED_PRINCIPAL,
                        "Automated actors may only read-probe shared state; live writes require an authorized principal.",
                    )
            else:
                # Authorized-principal actor but the activation was not explicit.
                outcome, reason_code, reason = (
                    DENY,
                    NON_EXPLICIT_ACTIVATION,
                    "Live activation by the authorized principal must be an explicit, separately-authorized step.",
                )
        else:
            outcome, reason_code, reason = (
                DENY,
                SHARED_WRITE_REQUIRES_AUTHORIZED_PRINCIPAL,
                "Unrecognized action against shared state fails closed.",
            )

    decision["decision"] = {"outcome": outcome, "reason_code": reason_code, "reason": reason}
    decision["receipt"] = {
        "receipt_id": f"ssw-receipt-runtime-{decision['decision_id']}",
        "decision_id": decision["decision_id"],
        "policy_id": policy_ref["policy_id"],
        "policy_version": policy_ref["policy_version"],
        "outcome": outcome,
        "reason_code": reason_code,
        "receipt_visibility_class": "internal",
        "evidence_refs": decision.get("evidence_refs", ["SocioProphet/policy-fabric#102"]),
        "redaction_summary": "No shared-state payload content included in receipt.",
        "residual_restrictions": [target.get("environment", "unknown"), target.get("target_kind", "unknown")],
    }
    return decision


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: shared_state_write_policy_evaluator.py <input.json>", file=sys.stderr)
        return 2
    record = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    print(json.dumps(evaluate(record), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
