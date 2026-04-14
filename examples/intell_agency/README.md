# Intell-Agency Example Surface

This directory is the first Policy Fabric landing surface for the intell-agency companion tranche.

It is intentionally small in v0.

## What is here now

- `README.md` — review-oriented explanation of the example surface
- `intell_agency_companion_manifest_v0.json` — manifest describing the current slice families and their intended normalization path

## Why this starts in `examples/`

The current tranche is broader than a single stable contract.

It includes:
- typed policy and observation surfaces
- runtime policy guards
- verdict and release-gating logic
- positive / negative / edge fixtures
- threshold rationale and boundary comparison material

Before elevating more of that material into `contracts/`, we want a reviewable manifest that makes the slice legible inside Policy Fabric without pretending every piece is already a stable product contract.

## Planned normalization

After review, expected follow-on moves are:

1. elevate durable machine-readable contracts into `contracts/`
2. keep review and fixture-oriented material in `examples/`
3. keep tranche semantics in `docs/specs/`
4. add generated or refreshed state reports to `docs/reports/` only when the generating logic is also present and understood

## Downstream relationship

Agentplane is expected to consume verdict and promotion outputs from this slice downstream.

That integration is intentionally deferred to a separate tranche in `SocioProphet/agentplane`.
