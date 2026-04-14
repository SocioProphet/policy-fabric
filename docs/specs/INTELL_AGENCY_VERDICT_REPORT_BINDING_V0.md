# Intell-Agency Verdict Report Binding v0

## Status

Plan/spec document.

This document binds the first durable machine-readable verdict artifact from the intell-agency companion tranche into Policy Fabric product surfaces.

## Why this artifact is first

The first durable contract promoted out of the tranche should be the verdict report because it is the narrowest artifact that still carries the essential governed release semantics:

- domain-level promote / block decision
- rights-critical classification
- fit classification
- failed predicates and reason strings
- threshold context
- explanation and artifact references

This is enough for downstream consumers to make governed execution decisions without importing the entire authored-policy and fixture machinery.

## Bound artifact

- `contracts/policy_fabric_verdict_report_v1.schema.json`
- `examples/policy_fabric_verdict_report_example.json`

## Relationship to the companion tranche

The companion tranche currently carries richer surfaces including:
- typed substrate
- policy guards
- fixture packs
- threshold sweep tooling
- boundary comparison material

Not all of those belong in Policy Fabric `contracts/` immediately.

The verdict report is the correct first promotion because it is both:
1. downstream-consumable
2. semantically central to release behavior

## Intended downstream consumer

The first downstream consumer is `SocioProphet/agentplane`.

Agentplane should consume the verdict report or an equivalent envelope rather than recomputing the upstream fit and threshold logic locally.

## Acceptance gate

This binding is acceptable when:
- the schema is reviewable as a Policy Fabric contract surface
- the example shows both blocked and promotable domains
- the artifact is sufficient for downstream execution eligibility decisions
- later tranches can extend, but not invalidate, this narrow contract
