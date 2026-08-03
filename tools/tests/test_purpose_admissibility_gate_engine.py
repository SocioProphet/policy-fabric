"""The consent-plane decision ENGINE, proven both ways at call time.

A conformant invocation is admitted; the containment cases (a prompt-injected
browser agent, a notes agent trying to egress, an implementer reaching kernel
space, an unknown tool) are REFUSED — and enforce() raises so the invocation
cannot proceed. Every emitted decision also satisfies the v1 contract's schema
and the fail-closed semantics the document validator already checks. Hermetic:
runs against the vendored catalog fixtures, offline.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
import sys

sys.path.insert(0, str(ROOT))
from policy_fabric import purpose_admissibility_gate as gate  # noqa: E402

FIXTURES = ROOT / "tests" / "fixtures" / "consent-plane"
CATALOGS = gate.load_catalogs(FIXTURES)


def req(**kw):
    base = {"role": "implementer", "surface": "terminal", "space": "user-space",
            "tool": "source-mutate", "declaredPurpose": "implement"}
    base.update(kw)
    return base


# ------------------------------------------------------------------ admits
def test_admit_implementer_edits_source_in_terminal():
    doc = gate.decide(req(), CATALOGS)
    assert doc["spec"]["decision"] == "admit"
    assert "denyReasons" not in doc["spec"]  # contract: absent on admit


def test_enforce_returns_on_admit():
    doc = gate.enforce(req(), CATALOGS)
    assert doc["spec"]["decision"] == "admit"


# ------------------------------------------------------------------ denies (containment)
def test_deny_browser_agent_cannot_implement():
    # prompt-injection containment: the browser surface denies implement outright
    reasons = gate.decide(req(surface="browser", space="agent-space",
                               tool="source-mutate", declaredPurpose="implement"),
                          CATALOGS)["spec"]["denyReasons"]
    assert any("browser" in r and "implement" in r for r in reasons)


def test_deny_notes_agent_cannot_egress():
    reasons = gate.decide(req(surface="notes", space="agent-space", role="explorer",
                               tool="external-send", declaredPurpose="egress"),
                          CATALOGS)["spec"]["denyReasons"]
    assert any("denies purpose 'egress'" in r for r in reasons)


def test_deny_browser_cannot_reach_user_space():
    reasons = gate.decide(req(surface="browser", space="user-space", role="explorer",
                               tool="web", declaredPurpose="discover"),
                          CATALOGS)["spec"]["denyReasons"]
    assert any("denies space 'user-space'" in r for r in reasons)


def test_deny_non_operator_cannot_enter_kernel_space():
    reasons = gate.decide(req(role="implementer", surface="terminal", space="kernel-space",
                               tool="exec-read", declaredPurpose="discover"),
                          CATALOGS)["spec"]["denyReasons"]
    # both the surface (terminal space_deny) and the role taint fire — fail-closed
    assert any("kernel" in r for r in reasons)


def test_operator_is_the_only_role_that_tolerates_system_space():
    # operator DOES tolerate ring=system; ci-runner surface allows operate there
    op = gate.decide(req(role="operator", surface="ci-runner", space="system-space",
                         tool="exec-mutate", declaredPurpose="operate",
                         consent={"purposes": ["operate"]}), CATALOGS)
    assert op["spec"]["decision"] == "admit", op["spec"].get("denyReasons")
    # implementer does NOT
    reasons = gate.decide(req(role="implementer", surface="ci-runner", space="system-space",
                               tool="exec-mutate", declaredPurpose="operate"),
                          CATALOGS)["spec"]["denyReasons"]
    assert any("system" in r or "operate" in r for r in reasons)


def test_deny_data_namespace_without_tenant_consent():
    reasons = gate.decide(req(role="operator", surface="cluster-operator", space="data-namespace",
                               tool="cluster", declaredPurpose="operate", tenant="acme",
                               consent={"purposes": ["operate"]}),  # tenant NOT granted
                          CATALOGS)["spec"]["denyReasons"]
    assert any("per-tenant consent" in r for r in reasons)


def test_deny_data_namespace_without_region_toleration():
    # tenant granted but NO region -> refused on the geographic-residency taint
    reasons = gate.decide(req(role="operator", surface="cluster-operator", space="data-namespace",
                               tool="cluster", declaredPurpose="operate", tenant="acme", region="EU",
                               consent={"purposes": ["operate"], "tenants": ["acme"]}),
                          CATALOGS)["spec"]["denyReasons"]
    assert any("geographic-residency" in r and "EU" in r for r in reasons)


def test_admit_data_namespace_with_tenant_and_region_consent():
    doc = gate.decide(req(role="operator", surface="cluster-operator", space="data-namespace",
                          tool="cluster", declaredPurpose="operate", tenant="acme", region="EU",
                          consent={"purposes": ["operate"], "tenants": ["acme"], "regions": ["EU"]}),
                      CATALOGS)
    assert doc["spec"]["decision"] == "admit", doc["spec"].get("denyReasons")
    assert doc["spec"]["request"]["region"] == "EU"


def test_deny_unknown_tool_fail_closed():
    reasons = gate.decide(req(tool="totally-unknown-tool"), CATALOGS)["spec"]["denyReasons"]
    assert any("not in the tool-purpose catalog" in r for r in reasons)


def test_enforce_raises_on_deny():
    with pytest.raises(gate.ConsentDenied) as ei:
        gate.enforce(req(surface="notes", role="explorer", space="agent-space",
                         tool="external-send", declaredPurpose="egress"), CATALOGS)
    assert ei.value.reasons  # non-empty
    assert ei.value.decision["spec"]["decision"] == "deny"


def test_missing_catalogs_fail_closed():
    with pytest.raises(gate.ConsentDenied):
        gate.load_catalogs(ROOT / "does" / "not" / "exist")


# ------------------------------------------------------------------ contract conformance
def test_emitted_decision_matches_v1_schema_and_semantics():
    schema = json.loads((ROOT / "contracts" / "purpose_admissibility_gate_decision_v1.schema.json").read_text())
    admit = gate.decide(req(), CATALOGS)
    deny = gate.decide(req(surface="notes", role="explorer", space="agent-space",
                           tool="external-send", declaredPurpose="egress"), CATALOGS)
    try:
        import jsonschema
        jsonschema.validate(admit, schema)
        jsonschema.validate(deny, schema)
    except ImportError:
        pytest.skip("jsonschema not installed")
    # reuse the existing validator's fail-closed semantic checks
    sys.path.insert(0, str(ROOT / "tools"))
    from validate_purpose_admissibility_gate import semantic_checks  # noqa: E402
    assert semantic_checks(admit) == []
    assert semantic_checks(deny) == []


def test_vendored_catalogs_do_not_drift_from_canonical():
    """If a sibling socioprophet-agent-standards checkout is present, the vendored
    fixtures MUST byte-match the canonical catalogs — vendoring can't silently rot."""
    canonical = None
    for parent in ROOT.parents:
        c = parent / "socioprophet-agent-standards" / "standards" / "consent-plane"
        if c.is_dir():
            canonical = c
            break
    if canonical is None:
        pytest.skip("no sibling agent-standards checkout to compare against")
    for fname in gate.CATALOG_FILES.values():
        want = (canonical / fname).read_bytes()
        got = (FIXTURES / fname).read_bytes()
        assert got == want, f"vendored {fname} drifted from canonical; re-vendor it"
