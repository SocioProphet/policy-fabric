# Consent-Bound Experienced Sensing v0.1

Status: schema and governance substrate. This tranche lands a minimal consent-bound session core, not the full experimental-session schema.

## Purpose

This tranche captures the consent-bound experienced-sensing data plane as Policy Fabric contracts. It binds session core data, evidence entries, claims, and agent identity records to explicit consent, chain-of-custody, public-law commitments, and policy-verifiable predicates.

## Contract layer

The schema layer contains four active records plus one deprecated alias:

1. `Evidence Ledger Entry` — content-addressable evidence with SHA-256 binding, signer DID, optional hash-chain predecessor, source metadata, UAIBB mapping, token extraction, chain-of-custody, and claim references.
2. `Claim Record` — theoretical or operational claim with LTL/FOL-compatible predicates, evidence support/refutation references, epistemic status, confidence, axiom binding, and falsification protocol.
3. `SAI Agent Identity Record` — agent identity, immutable traits, public-law commitments, self-model distribution, spawn lineage, coherence state, and communications budget.
4. `Consent-Bound Session Core Record` — minimal session core with participant/session IDs, consent binding, topic class, target/decoy fields, stage mix, raw artifact hash, and judgment references.
5. `Deprecated Experimental Session Alias` — `experimental_session.v0_1.schema.yaml` remains only as an alias to the core schema for PR continuity.

## Consent boundary

`experimental_session_core.v0_1.schema.yaml` makes consent explicit through `consent_ref`:

- `consent_version`
- `consent_hash`
- `scope`
- `withdrawn`
- `granted_at`

Policy consumers must treat `withdrawn: true` as a hard boundary. Any downstream replay, export, model training, or evidence promotion must pass a policy admission check before use.

## Explicit non-claims

The core schema does not yet include the full source-drop session fields, including AOL density, ESO profile, mood fields, or optional physiology. The full experimental-session schema remains follow-up work.

This tranche does not implement the SRC-025 session runner.

This tranche does not choose HTTP framework, schema registry hosting, sync versus async dispatch, or audit-log substrate.

## Cross-repo role split

Policy Fabric owns the contract and policy-validation surface.

AgentPlane should not integrate against this until PR #80 exits draft and endpoint naming is stable.

Superconscious should not integrate against this until PR #80 exits draft and `/verdict` status is explicit.

ProCybernetica should carry the public doctrine and cybernetic-control positioning.

SocioSphere should register canonical ownership and dependency direction.

Prophet Platform should deploy the service only after the LTL-to-SMT/Z3 tranche closes the executable `/verdict` path.
