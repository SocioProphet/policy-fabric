# Policy Fabric Release Pack v1 Draft

## Purpose

The release pack is the governed unit of promotion for Policy Fabric.

It is the smallest self-contained artifact that says:

- which authored policy is being promoted
- which compiled execution plan was derived from it
- which examples and fixtures were validated
- which evidence should be retained for replay and audit
- which rollout lane and human gate rules apply

This idea is influenced by the bundle/evidence/replay discipline in SocioProphet AgentPlane, but adapted to Policy Fabric's policy-and-plan model rather than VM execution.

## Why this matters

Today, Policy Fabric has strong core contracts but weak release packaging. A release pack fixes that by making promotion inspectable and replayable.

## Required contents

A v1 release pack must identify:

1. policy artifact reference and digest
2. compiled plan reference and digest
3. supporting fixtures/examples used for validation
4. evidence directory and replay corpus reference
5. rollout lane and gate requirements
6. provenance metadata for source revision and build inputs

## Lifecycle

1. assemble release pack
2. validate schema and semantic rules
3. run doctor and fixture validation
4. emit evidence manifest
5. approve for a target lane
6. promote and retain replayable artifacts

## Relationship to existing Policy Fabric surfaces

- Authored policy remains the source of intent.
- Compiled plan remains the source of execution.
- OpenAPI remains the service boundary.
- Release pack becomes the source of promotion and replay.

## Non-goals

- It does not embed raw secrets.
- It does not replace runtime attestation.
- It does not define the semantic validator itself.

## Expected next step

Add semantic validation rules for digest consistency, lane restrictions, evidence completeness, and replay-corpus availability.
