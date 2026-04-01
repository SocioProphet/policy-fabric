
# Policy Fabric Repository Workflow

This repository uses a repo-native workflow surface so the contract work stays inspectable, recoverable, and promotable.

## Ownership model

- `contracts/`, `examples/`, `docs/blueprints/`, `docs/assessments/`, `docs/research/`, `docs/rebrand/`, `docs/comparison/`, `docs/specs/`, `docs/turns/`, and `scripts/` are framework-managed working surfaces.
- `docs/reports/`, `.policy-fabric/reports/`, `REPO_MANIFEST.json`, and `dist/` are generated surfaces and may be rewritten by repo tooling.
- `.policy-fabric/local-notes/` is the sanctioned local override surface. It is non-authoritative and excluded from release bundles.
- `archive/prior-reference/` preserves historical reference material but is not an active product surface.

The authoritative path definitions live in `.policy-fabric/ownership.json`. The active workflow profile lives in `.policy-fabric/profiles.json` and is selected through `.policy-fabric/config.json`.

## Workflow profiles

- `solo` — direct local authoring with soft warnings.
- `normal` — cumulative team mode for active design and contract work.
- `release-gated` — stricter promotion mode intended for branch/PR release preparation.

Current profile: `normal`.

## Standard loop

1. Edit tracked files.
2. Run `python scripts/reconcile.py`.
3. Run `python scripts/doctor.py`.
4. Review `docs/reports/doctor_latest.md` and `docs/reports/validation_report_latest.json`.
5. Run `python scripts/build_dist_bundle.py`.
6. Record the change in `CHANGELOG.md` and `docs/turns/`.
7. Commit the repository state.

## Why this exists

The goal is to avoid detached artifacts, silent drift, and undocumented repair work. Every meaningful change should leave a file-level trail inside the repository.
