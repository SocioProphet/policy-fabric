# Intell-Agency Companion Placement Assessment v0

## Question

Where should the current intell-agency companion tranche live upstream?

## Candidates considered

### 1. `SocioProphet/policy-fabric`

**Fit:** strong

Reasons:
- the tranche is principally policy-governed and evidence-bearing
- the tranche centers typed policy, validation, release gates, fixture expectations, and audit semantics
- Policy Fabric already presents itself as the authored-policy, compiled-policy, validation, and release-pack control repository

### 2. `SocioProphet/agentplane`

**Fit:** partial / downstream

Reasons:
- Agentplane is the execution control plane and downstream consumer of governed release semantics
- it is the right place for integration documents and runtime consumption of verdict artifacts
- it is not the clean canonical owner of the policy/audit tranche itself

### 3. `SocioProphet/sociosphere`

**Fit:** weak

Reasons:
- the tranche is not primarily a local supervisor or local-runtime concern
- placing the canonical policy/audit slice there would blur repo ownership boundaries

## Decision

The canonical upstream home is:

`SocioProphet/policy-fabric`

## Why this decision is correct

The tranche is best understood as a governed representational-audit and release-control slice.

Its center of gravity is:
- policy meaning
- fit classification
- rights-critical release behavior
- fixture-controlled validation
- evidence-bearing review surfaces

That aligns directly with Policy Fabric.

## Exact initial landing paths

### Primary spec and assessment

- `docs/specs/INTELL_AGENCY_POLICY_BINDING_V0.md`
- `docs/assessments/INTELL_AGENCY_COMPANION_PLACEMENT_V0.md`

### Example/manifest surface

- `examples/intell_agency/README.md`
- `examples/intell_agency/intell_agency_companion_manifest_v0.json`

## Deferred follow-on in Agentplane

A follow-on tranche should land in `SocioProphet/agentplane` documenting:
- how Agentplane consumes verdict artifacts
- how rights-critical promotion blocking affects execution eligibility
- how Policy Fabric release artifacts map into execution control and evidence flow

That is a second PR, not part of this first placement tranche.

## Review guidance

Review this tranche for:
- correctness of canonical-home decision
- correctness of repo-boundary reasoning
- clarity of normalization path for later work
- whether any machine-readable contracts should be elevated next into Policy Fabric `contracts/`
