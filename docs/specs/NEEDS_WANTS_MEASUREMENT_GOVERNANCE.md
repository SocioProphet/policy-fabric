# Needs/Wants Measurement Governance

Status: v1 implementation contract.
Source framework: `Needs vs Wants: An Instrumented Framework for Voice + Text Analytics`, v1.3, prepared 2026-02-07.

This specification converts the Needs/Wants framework into a Policy Fabric control surface. It is measurement-first rather than model-first: the repository stores the contract that decides when a conversational analytics output is valid, when it must be refused, and which downstream actions are forbidden.

## Core invariant

The system has two regimes.

Regime N is for deprivation-sensitive and rights-adjacent needs. Regime N claims may be emitted only from explicit indicator bundles, validated psychometrics, administrative records, or self-report forms. Transcript language alone is not Regime N evidence.

Regime W is for wants, satisfier preferences, and interaction-style hints. Regime W outputs require uncertainty, stability, and domain provenance. They are never diagnoses, vulnerability labels, eligibility signals, or deprivation claims.

This firewall prevents semantic laundering: a preference must not be relabeled as a need merely because it improves routing, personalization, conversion, or prediction.

## Contract surface

The implementation surface is:

- `schemas/measurement/needs-wants-measurement-decision.v1.json`
- `examples/measurement/needs-wants-measurement-governance.fixture-pack.json`
- `tools/validate_needs_wants_measurement_decision.py`

The fixture pack contains two positive cases and four negative cases. The positive cases cover the full all-text CASE-ACME-2026-001 emission path and the calls-only underpowered refusal path. The negative cases prove rejection of W-as-Need laundering, sensitive monetization, hiring-domain transfer, and transcript-derived N inference.

## Gates

`G1_W` controls W evidence sufficiency. W output emission requires the configured minimum word count and context count. The canonical v1.3 worked example uses 2,500 words and at least 2 contexts. Calls-only evidence with 2,200 words and 1 context must refuse W emission.

`G1_N` controls N evidence sufficiency. N output requires explicit instruments: indicator bundles, validated psychometrics, administrative records, or self-report forms. The validator rejects transcript-derived N inference.

`G2_HARM` is the sensitivity gate. It triggers when AF-style deprivation meets or exceeds the configured cutoff. In the canonical example, 4 of 12 indicators are active, giving a rounded score of 0.333 against the default cutoff 0.333.

`G3_LABEL` blocks semantic laundering. Motivational or preference-like constructs remain Regime W. They cannot be admitted as Regime N merely because a historical product taxonomy called them “needs.”

`G4_DOMAIN` blocks uncalibrated transfer. W outputs are domain scoped. A contact-center W tuple cannot transfer to hiring, credit, insurance, or other high-stakes selection contexts without a separate calibration and validity contract.

## Action policy

Allowed under the canonical sensitive case:

- support routing
- agent coaching for clarity and step-by-step process
- friction reduction
- timeline confirmation
- state-based escalation without stable W emission

Denied under the canonical sensitive case:

- persuasion targeting
- churn-risk monetization
- high-stakes eligibility
- treating W as deprivation evidence
- transferring W output to hiring/selection

## Integration points

Policy Fabric owns the gate and forbidden-use enforcement contract.

AgentPlane should consume the decision object before invoking agent actions.

SocioSphere should expose only allowed actions and preserve refusal state.

Regis Entity Graph may store W outputs only as domain-scoped interaction-style edges. N indicators require stronger provenance, access control, retention, and audit treatment.

ProCybernetica and Orion/OFIF should consume the audit and forbidden-use outcomes as safety intelligence for human-facing agentic systems.
