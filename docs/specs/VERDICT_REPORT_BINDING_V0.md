# Verdict Report Binding v0

## Status

Plan/spec document.

This note defines the first narrow machine-readable verdict artifact promoted into Policy Fabric public product surfaces.

## Why this artifact is first

The verdict report is the smallest artifact that still carries the essential governed release semantics:
- domain-level promote or block decision
- rights-critical classification
- fit classification
- failed predicates and reason strings
- threshold context
- artifact and explanation references

This is sufficient for downstream consumers to make governed execution decisions without importing the full authored-policy and fixture machinery.

## Intended bound artifacts

- `contracts/policy_fabric_verdict_report_v1.schema.json`
- `examples/policy_fabric_verdict_report_example.json`

## Downstream consumer posture

A downstream execution plane should consume the verdict report or an equivalent governed envelope rather than recomputing upstream fit and threshold logic locally.

## Acceptance gate

This binding is acceptable when:
- the schema is reviewable as a Policy Fabric contract surface
- the example shows both blocked and promotable domains
- the artifact is sufficient for downstream execution eligibility decisions
- later tranches can extend, but not invalidate, this narrow contract
