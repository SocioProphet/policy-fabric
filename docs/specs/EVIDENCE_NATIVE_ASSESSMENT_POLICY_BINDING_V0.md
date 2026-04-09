# Evidence-Native Assessment Policy Binding v0

## Status

Plan/spec document.

This document binds the canonical evidence-native assessment contract pack into the Policy Fabric repository.

## Canonical upstreams

Policy Fabric does not own the normative cross-repository contract canon.

The canonical upstreams are:
- `SocioProphet/socioprophet-standards-storage` for contract and conformance definitions
- `SocioProphet/socioprophet-standards-knowledge` for semantic / JSON-LD context

Policy Fabric is the authored-policy and compiled-policy lane.

## Why this binding exists

Policy Fabric already treats authored policy, compiled execution structure, validation artifacts, replay artifacts, promotion semantics, and governance as one governed system.

The evidence-native assessment slice extends that model so that control evaluation is not just a narrative report activity. It becomes a policy-driven, replayable, evidence-bearing execution path.

## Policy Fabric responsibilities

Policy Fabric owns the following responsibilities for the assessment slice:

1. author and version `ControlRequirement` rows
2. define required proof classes per row
3. define blocker / decision policy per row
4. define exception semantics and approval requirements
5. compile authored policy into execution-oriented control bundles
6. validate that generated structures preserve policy identity and version

## Contract mapping

### Authored policy layer

The authored policy layer is the source of:
- framework identifiers
- control identifiers
- row identifiers
- titles and descriptions
- required proof classes
- decision policy
- exception and approval rules

This layer should map directly to `ControlRequirement`.

### Compiled execution layer

The compiled layer translates authored policy into evaluator-ready structure.

The compiled layer should produce, directly or indirectly:
- row selection sets
- proof-class requirements
- decision thresholds or approval rules
- exception linkage expectations
- evaluator input envelopes

### Promotion and evidence layer

The promotion / evidence layer should bind:
- policy bundle id and version
- validation artifacts
- replay reports
- release packs
- assessment receipt references

A policy release that cannot be traced into an `AssessmentReceipt` should be treated as incomplete for this slice.

## Required invariants

1. Every `ControlCellEvaluation` must reference a row derived from Policy Fabric authored policy.
2. Every `AssessmentReceipt` must carry the policy bundle id and version that governed the run.
3. Every finding emitted downstream must be structurally recoverable to one or more Policy Fabric rows.
4. Exception handling must be explicit and linkable; it must not exist only as prose.
5. Release packs and replay reports must preserve enough material to explain which policy bundle governed the observed decision.

## First compilation targets

The first compiled assessment slice should generate the following artifacts or equivalent envelopes:

- control requirement bundle
- evaluator input manifest
- proof-class expectations per row
- exception / approval policy envelope
- release-pack linkage to assessment receipt ids

## Non-goals for v0

This binding does not require Policy Fabric to:
- render stakeholder dashboards
- own runtime executor placement
- own evidence extraction pipelines
- own full narrative report rendering

Those belong downstream.

## Acceptance gate

The v0 slice is acceptable when we can show:
- one authored control row
- one compiled evaluator-ready representation
- one downstream control evaluation
- one downstream finding
- one downstream assessment receipt
- full lineage from receipt back to policy bundle and row id
