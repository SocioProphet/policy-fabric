# Governed Action Policy Decision v0

Status: v0.1 bounded contract surface.

This document defines the first Policy Fabric decision primitive for the Watson/Cyc/Semantic-Web/CHRONOS deployable loop.

## Purpose

Policy Fabric owns the decision boundary for whether a bounded downstream proposal may proceed, must be denied, must be modified, or must escalate.

The intended integration path is:

```text
Sherlock source-quality answer trace
  -> Ontogenesis corpus event semantics
  -> Policy Fabric decision
  -> Agentplane bounded proposal and trace
  -> Model Governance Ledger audit event
```

## Added surfaces

```text
contracts/governed-action-policy-decision.v0.schema.json
examples/governed-action-policy/valid.low-risk-allow.json
examples/governed-action-policy/valid.method-family-benign.json
examples/governed-action-policy/invalid.research-only-allow.json
examples/governed-action-policy/invalid.high-risk-allow.json
examples/governed-action-policy/invalid.dsr-dsp-live-controller-pre-admission.json
examples/governed-action-policy/invalid.neurasp-stable-model-bypass.json
tools/validate_governed_action_policy_decision.py
```

## v0 decision rule

`allow` is only valid when:

- `risk_class == low`
- `evidence_grade == implementation_safe`
- all evidence refs are marked `implementation_safe: true`
- all evidence source qualities are confirmed classes

Research-only evidence must not produce `allow`.

High or critical risk classifications must not produce `allow` in this v0 contract.

## CHRONOS method-family gate (additive, policy-fabric#97)

`sociosphere/docs/integration/neurosymbolic-chronos-alignment.md` (tracked at
`SocioProphet/socioprophet#498`) assigns Policy Fabric the "policy admission
and cancellation" authority role and defines per-method-family admissible /
forbidden-use rules for the neuro-symbolic method taxonomy (Kautz, LTN, LNN,
NeurASP, SATNet, dILP, DON-RRN, DSR/DSP). Policy Fabric does not own that
taxonomy or its doctrine, but as the admission authority it is the layer that
must be able to check those rules mechanically at decision time.

Each `evidence_refs[]` entry gained two **optional** fields, additive to the
existing `risk_class` / `evidence_grade` fields (nothing was removed or
renamed; `schema_version` stays `"0.1"`):

- `method_family` — which neuro-symbolic method family (if any) produced this
  evidence: `kautz`, `ltn`, `lnn`, `neurasp`, `satnet`, `dilp`, `don_rrn`, or
  `dsr_dsp`.
- `method_family_claim` — the specific claimed use being made of that
  evidence: `none` (no forbidden-use claim), or one of
  `live_controller_pre_admission`, `stable_model_bypasses_admission`,
  `soft_constraint_promoted_as_truth`, `symbolic_derivation_as_admission`.

`tools/validate_governed_action_policy_decision.py` enforces, for every
evidence ref that sets both fields: if `method_family_claim` is one of that
family's doctrine-forbidden claims, the decision must not resolve to `allow`
(it must `deny`/`modify`/`escalate` instead). Two mappings come directly from
the negative rules quoted in policy-fabric#97 (DSR/DSP forbids running as a
live controller before governance admission; NeurASP forbids bypassing
admission because ASP returned a stable model). The remaining two claims
implement the alignment doc's general negative rules (a fuzzy/soft
satisfaction score promoted as truth; a symbolic derivation treated as policy
admission itself), applied per the reasoning documented alongside
`FORBIDDEN_BY_METHOD_FAMILY` in the validator. This is Policy Fabric applying
CHRONOS's doctrine at its own admission boundary, not a redefinition of that
doctrine.

## Validation

Run:

```bash
make governed-action-policy-decision-validate
```

The target is also included in:

```bash
make validate
```

## Boundary

This contract does not implement a full policy language, external compliance integration, downstream execution, or persistence. It provides the machine-readable decision payload, examples, and validation rules for the first bounded cross-repo loop.
