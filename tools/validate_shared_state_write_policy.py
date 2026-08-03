#!/usr/bin/env python3
"""Validate the deterministic shared-state write / live-activation authorization evaluator.

This is the enforcement gate with teeth. Each case pins the expected (outcome,
reason_code); the run fails if the evaluator drifts. The table deliberately contains
NEGATIVE cases (a live shared-state write must be denied) and POSITIVE cases (a
read-probe and a gated activation must pass) so the control provably fires in both
directions -- a control that never fires is suspect.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

try:
    import jsonschema
except ImportError as exc:  # pragma: no cover
    raise SystemExit("jsonschema is required: python3 -m pip install jsonschema") from exc

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "contracts" / "shared-state-write-policy-decision.v0.schema.json"
sys.path.insert(0, str(ROOT / "tools"))
from shared_state_write_policy_evaluator import evaluate  # noqa: E402


def base_record(case_id: str) -> dict[str, Any]:
    return {
        "schema_version": "0.1",
        "kind": "shared_state_write_policy_decision",
        "decision_id": case_id,
        "policy_ref": {
            "policy_id": "shared_state.live_activation_authorization.v0",
            "policy_version": "0.1.0",
            "policy_authority": "SocioProphet/policy-fabric#102",
        },
        "subject": {"subject_id": "subagent-alpha", "subject_type": "subagent", "actor_class": "automated_actor"},
        "action": {"action_type": "read_probe", "enforcement_point": "hellgraph_store"},
        "target": {
            "target_id": "hellgraph-socioprophet",
            "target_kind": "shared_graph_store",
            "environment": "live",
            "endpoint_class": "live_endpoint",
        },
        "authorization": {"source": "none", "explicit_activation": False},
        "decision": {"outcome": "deny", "reason_code": "read_probe_allowed", "reason": "placeholder"},
        "receipt": {
            "receipt_id": "placeholder",
            "decision_id": case_id,
            "policy_id": "shared_state.live_activation_authorization.v0",
            "policy_version": "0.1.0",
            "outcome": "deny",
            "reason_code": "read_probe_allowed",
            "receipt_visibility_class": "internal",
            "evidence_refs": ["SocioProphet/policy-fabric#102"],
            "redaction_summary": "No shared-state payload content included in receipt.",
            "residual_restrictions": ["live", "shared_graph_store"],
        },
    }


def cases() -> dict[str, tuple[dict[str, Any], tuple[str, str]]]:
    # --- NEGATIVE: the 2026-08-03 incident. A subagent acting on a relayed
    # coordinator message port-forwarded into the live socioprophet namespace and
    # attempted a probe-node WRITE to the shared HellGraph store. Must be DENIED. ---
    incident = base_record("incident-relayed-hellgraph-write-2026-08-03")
    incident["action"] = {"action_type": "write_shared_graph", "enforcement_point": "hellgraph_store"}
    incident["authorization"] = {"source": "relayed_coordinator", "explicit_activation": False}

    # NEGATIVE: agent-to-agent instruction mutating a live cluster namespace.
    a2a_namespace = base_record("agent-to-agent-namespace-mutate")
    a2a_namespace["subject"] = {"subject_id": "agent-beta", "subject_type": "agent", "actor_class": "automated_actor"}
    a2a_namespace["action"] = {"action_type": "mutate_namespace", "enforcement_point": "gke_admission"}
    a2a_namespace["target"] = {
        "target_id": "socioprophet",
        "target_kind": "cluster_namespace",
        "environment": "live",
        "endpoint_class": "live_endpoint",
    }
    a2a_namespace["authorization"] = {"source": "agent_to_agent", "explicit_activation": False}

    # NEGATIVE: automated write to a live shared ledger with no authorization at all.
    no_auth_ledger = base_record("automated-ledger-write-no-auth")
    no_auth_ledger["action"] = {"action_type": "write_shared_ledger", "enforcement_point": "prophet_core_ledger"}
    no_auth_ledger["target"] = {
        "target_id": "prophet-core-ledger",
        "target_kind": "shared_ledger",
        "environment": "live",
        "endpoint_class": "live_endpoint",
    }
    no_auth_ledger["authorization"] = {"source": "none", "explicit_activation": False}

    # NEGATIVE: authorized principal, but the activation was not explicit.
    non_explicit = base_record("principal-non-explicit-activation")
    non_explicit["subject"] = {"subject_id": "mdheller", "subject_type": "human", "actor_class": "authorized_principal"}
    non_explicit["action"] = {"action_type": "run_production_workflow", "enforcement_point": "gitops_promote"}
    non_explicit["target"] = {
        "target_id": "prod-workflow",
        "target_kind": "production_workflow",
        "environment": "live",
        "endpoint_class": "live_endpoint",
    }
    non_explicit["authorization"] = {"source": "authorized_principal", "principal_id": "mdheller", "explicit_activation": False}

    # NEGATIVE: reviewable artifact pointed at a live endpoint (the incident also
    # wrote manifests pointing at live endpoints).
    artifact_live = base_record("artifact-targets-live-endpoint")
    artifact_live["action"] = {"action_type": "open_pull_request", "enforcement_point": "gitops_promote"}
    artifact_live["target"] = {
        "target_id": "manifests-live",
        "target_kind": "production_workflow",
        "environment": "live",
        "endpoint_class": "live_endpoint",
    }
    artifact_live["authorization"] = {"source": "agent_to_agent", "explicit_activation": False}

    # NEGATIVE: unknown authorization provenance fails closed.
    missing = base_record("missing-context-fail-closed")
    missing["action"] = {"action_type": "write_shared_graph", "enforcement_point": "hellgraph_store"}
    missing["authorization"] = {"source": "unknown", "explicit_activation": False}

    # --- POSITIVE: automated actor read-probing live shared state is allowed. ---
    read_probe = base_record("read-probe-live-shared-graph")
    # base_record is already a read_probe against live shared_graph_store.

    # POSITIVE: automated actor ships change as a reviewable artifact (PR) against a
    # mock transport -- the compliant path.
    gated_artifact = base_record("gated-artifact-mock-transport")
    gated_artifact["action"] = {"action_type": "open_pull_request", "enforcement_point": "gitops_promote"}
    gated_artifact["target"] = {
        "target_id": "mock-hellgraph",
        "target_kind": "mock_transport",
        "environment": "mock",
        "endpoint_class": "mock_endpoint",
    }
    gated_artifact["authorization"] = {"source": "agent_to_agent", "explicit_activation": False}

    # POSITIVE: automated write against a mock transport is allowed.
    mock_write = base_record("mock-transport-write")
    mock_write["action"] = {"action_type": "write_shared_graph", "enforcement_point": "hellgraph_store"}
    mock_write["target"] = {
        "target_id": "mock-hellgraph",
        "target_kind": "mock_transport",
        "environment": "mock",
        "endpoint_class": "mock_endpoint",
    }

    # POSITIVE: gated live activation by the authorized principal via an explicit grant.
    live_ok = base_record("live-activation-authorized-principal")
    live_ok["subject"] = {"subject_id": "mdheller", "subject_type": "human", "actor_class": "authorized_principal"}
    live_ok["action"] = {"action_type": "activate", "enforcement_point": "gitops_promote"}
    live_ok["target"] = {
        "target_id": "prod-workflow",
        "target_kind": "production_workflow",
        "environment": "live",
        "endpoint_class": "live_endpoint",
    }
    live_ok["authorization"] = {
        "source": "authorized_principal",
        "principal_id": "mdheller",
        "explicit_activation": True,
        # Non-secret placeholder: a pointer to an activation grant record, not a
        # credential (the evaluator keys on source + explicit_activation, not this value).
        "grant_ref": "example-grant-ref-nonsecret",
    }

    return {
        # negatives
        "incident-relayed-hellgraph-write": (incident, ("deny", "relayed_authorization_insufficient")),
        "agent-to-agent-namespace-mutate": (a2a_namespace, ("deny", "agent_to_agent_authorization_insufficient")),
        "automated-ledger-write-no-auth": (no_auth_ledger, ("deny", "shared_write_requires_authorized_principal")),
        "principal-non-explicit-activation": (non_explicit, ("deny", "non_explicit_activation")),
        "artifact-targets-live-endpoint": (artifact_live, ("deny", "artifact_targets_live_endpoint")),
        "missing-context-fail-closed": (missing, ("deny", "missing_authorization_context")),
        # positives
        "read-probe-live-shared-graph": (read_probe, ("allow", "read_probe_allowed")),
        "gated-artifact-mock-transport": (gated_artifact, ("allow", "gated_artifact_allowed")),
        "mock-transport-write": (mock_write, ("allow", "mock_transport_write_allowed")),
        "live-activation-authorized-principal": (live_ok, ("allow", "live_activation_authorized")),
    }


def assert_receipt_consistency(record: dict[str, Any]) -> None:
    if record["receipt"]["decision_id"] != record["decision_id"]:
        raise ValueError("receipt decision_id mismatch")
    if record["receipt"]["outcome"] != record["decision"]["outcome"]:
        raise ValueError("receipt outcome mismatch")
    if record["receipt"]["reason_code"] != record["decision"]["reason_code"]:
        raise ValueError("receipt reason_code mismatch")
    if "payload" not in record["receipt"].get("redaction_summary", "").lower():
        raise ValueError("receipt must explicitly state that payload content is excluded")


def main() -> int:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    validator = jsonschema.Draft202012Validator(schema)
    checked = []
    for name, (record, expected) in sorted(cases().items()):
        evaluated = evaluate(record)
        errors = sorted(validator.iter_errors(evaluated), key=lambda error: list(error.path))
        if errors:
            rendered = [f"{'.'.join(str(part) for part in error.path) or '<root>'}: {error.message}" for error in errors]
            raise ValueError(f"{name} failed schema validation: " + "; ".join(rendered))
        assert_receipt_consistency(evaluated)
        actual = (evaluated["decision"]["outcome"], evaluated["decision"]["reason_code"])
        if actual != expected:
            raise ValueError(f"{name}: expected {expected}, got {actual}")
        checked.append({"case": name, "outcome": actual[0], "reason_code": actual[1]})
    print(json.dumps({"ok": True, "policy_id": "shared_state.live_activation_authorization.v0", "checked": checked}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
