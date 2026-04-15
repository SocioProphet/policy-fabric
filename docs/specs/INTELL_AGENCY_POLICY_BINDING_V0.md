# Intell-Agency Policy Binding v0

## Status

Plan/spec document.

This document binds the current intell-agency companion tranche into the Policy Fabric repository as the canonical authored-policy and governed-release home for this slice.

## Canonical home decision

The canonical upstream home for this slice is `SocioProphet/policy-fabric`.

`policy-fabric` is the right primary home because the tranche is centered on:
- typed policy contracts
- rights-critical overlays
- governed validation and release gating
- audit artifacts and verdict semantics
- threshold rationale and fixture-controlled promotion behavior

This slice is not primarily an execution plane feature.

## Relationship to adjacent repositories

### Policy Fabric

Policy Fabric owns the authored-policy, compiled-policy, validation, release-pack, replay, and governance semantics for this slice.

### Agentplane

Agentplane is the downstream execution-plane consumer.

Agentplane should consume verdict artifacts and release eligibility outputs produced by this slice, but it should not be the canonical owner of the policy and audit contract pack.

### Sociosphere

Sociosphere is not the primary home for this slice. The tranche is not principally a local supervisor/runtime feature.

## What this slice contains

The current companion tranche includes the following families:

1. typed substrate for agents, observations, policy references, world-model references, and gossip payloads
2. policy guards and rights-critical overlays
3. release-gating semantics driven by verdict artifacts
4. audit harness logic for fit classification, thresholds, and fixture validation
5. positive, negative, and edge boundary fixtures
6. threshold rationale and boundary comparison artifacts

## Policy Fabric responsibilities for this slice

Policy Fabric owns the following responsibilities:

1. define the normative policy and validation semantics for the slice
2. define release and promotion meaning for rights-critical domains
3. define threshold rationale and fixture expectations
4. version the machine-readable artifact surfaces that downstream systems consume
5. preserve evidence-bearing review material in-repo

## Initial landing shape

The first tranche in Policy Fabric should be repository-native and reviewable before any large normalization pass.

### Docs/spec surface

- `docs/specs/INTELL_AGENCY_POLICY_BINDING_V0.md`
- `docs/assessments/INTELL_AGENCY_COMPANION_PLACEMENT_V0.md`

### Example surface

- `examples/intell_agency/README.md`
- `examples/intell_agency/intell_agency_companion_manifest_v0.json`

## Normalization path after v0

After the first tranche is merged, the slice can be decomposed more formally into:
- `contracts/` for stable machine-readable contracts worth elevating into Policy Fabric product surfaces
- `examples/` for aligned fixture packs and example verdict/report artifacts
- `docs/specs/` for normative tranche semantics and governance notes
- `docs/reports/` for generated comparison or boundary-state reports when appropriate

## Non-goals for v0

This binding does not require Policy Fabric to:
- absorb the entire companion repository as a top-level mirrored subtree
- own executor placement or runtime scheduling
- own local supervisor behavior
- settle the final standards-repo boundary for every contract in one tranche

## Acceptance gate

The v0 binding is acceptable when we can show:
- a clear canonical-home decision recorded in Policy Fabric
- a clear downstream integration boundary to Agentplane
- a reviewable example manifest for the slice
- a clean path for later normalization into contracts/examples/docs surfaces
