# Policy Fabric Repository Workflow

This repository uses a repo-native workflow surface so the contract work stays inspectable.

## Ownership model

- `contracts/`, `examples/`, `docs/blueprints/`, `docs/assessments/`, `docs/research/`, `docs/rebrand/`, `docs/comparison/`, and `scripts/` are framework-managed working surfaces.
- `archive/prior-reference/` preserves earlier reference material but is not authoritative for the active product.
- `.policy-fabric/local-notes/` is reserved for local, non-authoritative overrides or operator notes.

## Pre-release loop

1. Change tracked files.
2. Run `python scripts/doctor.py`.
3. Review `docs/reports/doctor_latest.md` and any failures.
4. Run `python scripts/build_dist_bundle.py`.
5. Record the change in `CHANGELOG.md` and `docs/turns/`.
6. Commit the repository state.

## Why this exists

The goal is to avoid detached artifacts and silent drift. Every meaningful change should leave a file-level trail inside the repository.
