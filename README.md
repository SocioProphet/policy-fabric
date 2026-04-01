
# Policy Fabric Working Repository

This repository is the cumulative working copy for the Policy Fabric platform design and contract work.
It keeps the active contracts, aligned examples, supporting design notes, and archived prior-reference artifacts in one place so the work can become a real Git repository without reconstructing history from detached files.

## Repository goals

- Keep one authoritative working tree for all current Policy Fabric artifacts.
- Preserve archived prior-reference materials without letting them pollute the active product identity.
- Rebuild the distributable contract bundle reproducibly from repository contents.
- Run reconcile and doctor before each release snapshot.
- Keep ownership, profile, and repair semantics explicit inside the repo.

## Active surfaces

- `contracts/` — active machine-readable service and schema contracts.
- `examples/` — aligned example payloads and responses.
- `docs/` — blueprint, assessments, research, comparison, rebrand notes, specs, reports, and turn logs.
- `.policy-fabric/` — repo-local workflow, ownership, profile, repair, and generated-report surfaces.
- `scripts/` — reconcile, doctor, and bundle-build utilities.

## Generated outputs

- `/mnt/data/policy_fabric_contracts_bundle_latest.zip` — latest distributable bundle without Git metadata.
- `/mnt/data/policy_fabric_repo_snapshot_latest.zip` — latest repository snapshot including `.git`.

## Workflow

1. Edit tracked files in the repository.
2. Run `python scripts/reconcile.py`.
3. Run `python scripts/doctor.py`.
4. Review `docs/reports/doctor_latest.md` and `docs/reports/validation_report_latest.json`.
5. Run `python scripts/build_dist_bundle.py`.
6. Commit the result and export the latest snapshot zip.

## Current focus

The current focus is pushing semantic enforcement into the authored-policy layer: managed ownership and release-pack governance are in place, and the next maturity step is provider/capability authorization, rollout-bound policy validation, attestation readiness, and stronger fixture enforcement.
