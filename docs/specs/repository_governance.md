
# Repository Governance Contract

## Objective

Define the repo-native operating model for Policy Fabric so ownership, repair, validation, and bundling are explicit.

## Managed ownership

The canonical ownership contract is `.policy-fabric/ownership.json`.

Surface classes:
- framework-managed — authored contracts, examples, design notes, workflow policy, and scripts
- generated — reports, manifests, and distributable bundles
- local override — sanctioned non-authoritative notes under `.policy-fabric/local-notes/`
- archive protected — preserved prior-reference material

## Workflow profiles

The canonical profile contract is `.policy-fabric/profiles.json`.

Profiles:
- `solo`
- `normal`
- `release-gated`

Profiles let us adjust strictness without changing the underlying contract system.

## Core commands

- `python scripts/reconcile.py`
- `python scripts/doctor.py`
- `python scripts/build_dist_bundle.py`

## Drift model

The repository treats the following as actionable drift:
- ownership overlaps across surface classes
- unclassified tracked files
- release-pack digest mismatch versus referenced artifacts
- replay retention without replay corpus reference or replay evidence expectation
- invalid profile selection or workflow-mode mismatch
- local override files leaking into the distributable bundle

## Non-goal

This governance layer does not replace runtime semantics for policy execution. It governs how repository artifacts are authored, repaired, validated, and promoted.
