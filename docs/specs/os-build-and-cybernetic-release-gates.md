# OS Build and Cybernetic Release Gates

## Status

Draft.

## Purpose

This document defines the first Policy Fabric release-gate posture for the SourceOS OS-build / cybernetic boundary.

It is intended to consume the upstream contract seam introduced in `SourceOS-Linux/sourceos-spec`:

- `OSImage`
- `NodeBinding`
- `CyberneticAssignment`

Policy Fabric does not redefine those schemas. It defines the **review and validation gates** that determine whether a release pack, runtime bundle, or evidence set preserves the boundary correctly.

## Non-negotiable gate rules

### Gate 1 — Immutable image identity must remain substrate-only

An `OSImage` object MUST fail validation if it contains any of the following categories of data:

- deployment environment values such as `dev`, `stage`, `prod`, `production`
- topology values such as region, site, cell, or customer identifiers inside immutable IDs
- runtime service identity (`service.name`, `service.namespace`, instance identity)
- cybernetic role or control words such as `sensor`, `planner`, `governor`, `auditor`
- runtime policy refs or graph relations
- control objectives

### Gate 2 — Node binding must remain mutable assignment

A `NodeBinding` object MUST fail validation if it attempts to redefine immutable image identity or substrate provenance.

A `NodeBinding` object SHOULD contain:

- topology
- fleet
- update ring
- installer profile
- mirror / registry selection
- bootstrap trust-root refs

### Gate 3 — Cybernetic assignment must remain runtime meaning

A `CyberneticAssignment` object MUST fail validation if it attempts to redefine immutable OS image identity.

A `CyberneticAssignment` object SHOULD contain:

- service identity
- deployment environment projection
- policy refs
- graph relations
- control profile refs
- objective set

## Expected enforcement surfaces

This tranche is expected to support:

1. pre-merge release-pack validation
2. policy review on generated artifacts
3. replay bundle conformance review
4. runtime evidence audits after deployment

## Evidence expectations

A passing gate report SHOULD record:

- subject path
- detected object kind
- pass/fail status
- any forbidden fields encountered
- any suspicious identity strings encountered

## First implementation

The initial runnable implementation is `scripts/check_os_cybernetic_boundary.py`.

That script is deliberately narrow. It is not a full semantic validator. It provides a deterministic first-pass gate that can be called by repo workflows, doctor surfaces, or release-pack assembly logic.
