# Companion Policy Binding v0

## Status

Plan/spec document.

This note records how a companion tranche can be represented in Policy Fabric without promoting every upstream artifact into the core contract surface.

## Core idea

A companion tranche may contain richer upstream material than Policy Fabric should expose directly as first-class contracts.

Examples include:
- typed substrate work
- threshold sweep machinery
- boundary comparison notes
- evaluation packs
- placement and governance scaffolding

Policy Fabric should only absorb the narrow artifacts that are directly required for governed execution, audit, release, or promotion control.

## Binding rule

Promote the smallest downstream-consumable artifacts first.

Typical order:
1. verdict report
2. execution-lane binding
3. policy bundle or release-pack references only when needed

## Why this matters

This prevents Policy Fabric from becoming a dumping ground for upstream tranche material while still allowing governed downstream execution decisions.

## Acceptance gate

A companion artifact is a good Policy Fabric binding candidate when it is:
- downstream-consumable
- semantically central to execution or promotion
- stable enough to survive later tranche evolution
- narrow enough to avoid dragging in upstream implementation detail unnecessarily
