"""The telemetry.emit purpose binding, proven at call time.

Telemetry about a person's own usage leaving their device is bound to lawful_basis
`consent` and `consent_required: per-purpose`. This proves the binding actually decides
something rather than merely being present in a YAML file:

  * it is in the catalog with the intended basis (a weaker basis would be a silent
    downgrade — legitimate-interest telemetry is the thing this plane exists to refuse)
  * an emission with NO consent is denied, and the consent constraint is what denies it
  * granting consent for the purpose REMOVES the consent denial

It also records a live governance fact, discovered while writing this: no role in the
catalog currently admits `egress` at all, so consented telemetry still cannot flow. That
is fail-closed and arguably correct as a default, but it means the WO-4 emission path is
blocked on a POLICY decision (which role, if any, may egress) and not on code. The test
asserts the shape of that blockage rather than asserting it forever holds, so granting a
role egress admissibility does not break this file.
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from policy_fabric import purpose_admissibility_gate as gate  # noqa: E402

FIXTURES = ROOT / "tests" / "fixtures" / "consent-plane"
CATALOGS = gate.load_catalogs(FIXTURES)

TOOL = "telemetry.emit"


def _binding():
    raw = yaml.safe_load((FIXTURES / "tool-purpose-bindings_v1.yaml").read_text())
    for b in raw["spec"]["bindings"]:
        if b["tool"] == TOOL:
            return b
    return None


def req(**kw):
    base = {
        "role": "emitter",
        "surface": "agent-runtime",
        "space": "agent-space",
        "tool": TOOL,
        "declaredPurpose": "egress",
    }
    base.update(kw)
    return base


# ------------------------------------------------------------------ the binding itself
def test_telemetry_emit_is_in_the_catalog():
    assert _binding() is not None, "telemetry.emit missing from tool-purpose-bindings"


def test_lawful_basis_is_consent_and_nothing_weaker():
    """There is no legitimate-interest reading under which a product observes its user by
    default. A downgrade here would silently make telemetry lawful without a grant."""
    b = _binding()
    assert b["lawful_basis"] == "consent"
    assert b["consent_required"] == "per-purpose"


def test_bound_to_egress_not_operate():
    """The defining act is that the data LEAVES the device. Calling it operate would
    understate what the person is agreeing to."""
    assert _binding()["purposes"] == ["egress"]


def test_data_class_names_the_subject_matter():
    assert _binding()["data_class"] == "personal-usage"


# ------------------------------------------------------------------ teeth at call time
def test_emission_without_consent_is_denied_for_consent_reasons():
    doc = gate.decide(req(), CATALOGS)
    assert doc["spec"]["decision"] == "deny"
    reasons = doc["spec"]["denyReasons"]
    assert any("consent" in r for r in reasons), reasons


def test_granting_consent_removes_the_consent_denial():
    """Consent is load-bearing: the consent-specific reason disappears once granted. Any
    remaining denial is a different constraint, which the next test pins down."""
    without = gate.decide(req(), CATALOGS)["spec"]["denyReasons"]
    with_ = gate.decide(req(consent={"purposes": ["egress"]}), CATALOGS)["spec"].get("denyReasons", [])
    consent_reasons = [r for r in without if "requires per-purpose consent" in r]
    assert consent_reasons, without
    assert not [r for r in with_ if "requires per-purpose consent" in r], with_


def test_enforce_raises_so_an_unconsented_emission_cannot_proceed():
    try:
        gate.enforce(req(), CATALOGS)
    except gate.ConsentDenied as e:
        assert e.reasons
        return
    raise AssertionError("an unconsented telemetry emission was allowed to proceed")


# ------------------------------------------------------------------ the emitter path admits
def test_consented_emission_from_the_emitter_role_is_admitted():
    """The path WO-4 actually needs. Without this the whole consent plane would be
    show-and-toggle: a person could grant consent and still have nothing be emitable."""
    doc = gate.decide(req(consent={"purposes": ["egress"]}), CATALOGS)
    assert doc["spec"]["decision"] == "admit", doc["spec"].get("denyReasons")
    assert "denyReasons" not in doc["spec"]


def test_enforce_returns_on_a_consented_emission():
    doc = gate.enforce(req(consent={"purposes": ["egress"]}), CATALOGS)
    assert doc["spec"]["decision"] == "admit"


# --------------------------------------------------- and the permission stays narrow
def test_emitter_cannot_do_anything_but_egress():
    """The point of a dedicated role. If emitter could also discover, it would have a read
    path whose output it could then send — which is the capability we refused to create."""
    roles = yaml.safe_load((FIXTURES / "agent-roles_v1.yaml").read_text())["spec"]["roles"]
    emitter = next(r for r in roles if r["id"] == "emitter")
    assert emitter["admissible"] == ["egress"]
    assert emitter["tolerations"] == []
    for purpose in ["discover", "implement", "verify", "ship", "operate", "administer"]:
        doc = gate.decide(req(declaredPurpose=purpose, consent={"purposes": [purpose]}), CATALOGS)
        assert doc["spec"]["decision"] == "deny", purpose


def test_agent_runtime_surface_cannot_do_anything_but_egress():
    doc = gate.decide(
        req(role="explorer", declaredPurpose="discover", consent={"purposes": ["discover"]}),
        CATALOGS,
    )
    assert doc["spec"]["decision"] == "deny"
    assert any("agent-runtime" in r for r in doc["spec"]["denyReasons"])


def test_emitter_cannot_reach_system_or_kernel_space():
    for space in ["kernel-space", "system-space"]:
        doc = gate.decide(req(space=space, consent={"purposes": ["egress"]}), CATALOGS)
        assert doc["spec"]["decision"] == "deny", space


def test_emitter_still_cannot_egress_from_another_surface():
    """The role does not carry the permission around with it — the surface envelope is
    checked independently, so an emitter on the terminal is still refused."""
    doc = gate.decide(req(surface="terminal", consent={"purposes": ["egress"]}), CATALOGS)
    assert doc["spec"]["decision"] == "deny"


def test_another_role_cannot_egress_from_the_agent_runtime_surface():
    """Symmetric to the above: the surface does not grant the purpose to whoever stands on
    it. Both halves must independently permit egress."""
    doc = gate.decide(req(role="operator", consent={"purposes": ["egress"]}), CATALOGS)
    assert doc["spec"]["decision"] == "deny"
    assert any("role 'operator'" in r for r in doc["spec"]["denyReasons"])


def test_emitter_is_the_only_role_admitting_egress():
    roles = yaml.safe_load((FIXTURES / "agent-roles_v1.yaml").read_text())["spec"]["roles"]
    assert [r["id"] for r in roles if "egress" in r["admissible"]] == ["emitter"]
