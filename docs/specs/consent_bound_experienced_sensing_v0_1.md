# Consent-Bound Experienced Sensing v0.1

Status: schema and governance substrate.

## Purpose

This tranche captures the consent-bound experienced-sensing data plane as Policy Fabric contracts. It binds session data, evidence entries, claims, and agent identity records to explicit consent, chain-of-custody, public-law commitments, and policy-verifiable predicates.

## Contract layer

The schema layer contains four records:

1. `Evidence Ledger Entry` — content-addressable evidence with SHA-256 binding, signer DID, optional hash-chain predecessor, source metadata, UAIBB mapping, token extraction, chain-of-custody, and claim references.
2. `Claim Record` — theoretical or operational claim with LTL/FOL-compatible predicates, evidence support/refutation references, epistemic status, confidence, axiom binding, and falsification protocol.
3. `SAI Agent Identity Record` — agent identity, immutable traits, public-law commitments, self-model distribution, spawn lineage, coherence state, and communications budget.
4. `Experienced Sensing Session` — one consent-bound session record with participant/session IDs, consent binding, topic class, target/decoy fields, stage mix, AOL density, ESO profile, raw artifact hash, optional physiology, and judgment references.

## Consent boundary

`experimental_session.v0_1.schema.json` makes consent explicit through `consent_ref`:

- `consent_version`
- `consent_hash`
- `scope`
- `withdrawn`
- `granted_at`

Policy consumers must treat `withdrawn: true` as a hard boundary. Any downstream replay, export, model training, or evidence promotion must pass a policy admission check before use.

## Cross-repo role split

Policy Fabric owns the contract and policy-validation surface.

AgentPlane should consume policy verdicts and emit verdict artifacts inside run/replay evidence.

Superconscious should request policy admission before cognition-loop actions that change tools, memory, external systems, or execution handoff.

ProCybernetica should carry the public doctrine and cybernetic-control positioning.

SocioSphere should register canonical ownership and dependency direction.

Prophet Platform should deploy the service after the LTL-to-SMT/Z3 tranche closes the executable `/verdict` path.

## Open decisions retained as blockers

- HTTP framework selection.
- Schema registry hosting.
- Sync versus async axiom dispatch.
- Audit-log substrate.

These are not decided in this tranche.
