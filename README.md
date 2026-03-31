# Policy Fabric Working Repository

This repository is the cumulative working copy for the Policy Fabric platform design and contract work.
It keeps the active contracts, aligned examples, supporting design notes, and archived prior-reference artifacts in one place so the work can become a real Git repository without reconstructing history from detached files.

## Repository goals

- Keep one authoritative working tree for all current Policy Fabric artifacts.
- Preserve archived prior-reference materials without letting them pollute the active product identity.
- Rebuild the distributable contract bundle reproducibly from repository contents.
- Run a local health check (`doctor`) before each release snapshot.

## Active surfaces

- `contracts/` — active machine-readable service and schema contracts.
- `examples/` — aligned example payloads and responses.
- `docs/` — blueprint, assessments, research, comparison, rebrand notes, and turn logs.
- `.policy-fabric/` — repo-local workflow surface inspired by repo-native governance patterns.
- `scripts/` — bundle-build and doctor utilities.

## Generated outputs

- `/mnt/data/policy_fabric_contracts_bundle_latest.zip` — latest distributable bundle without Git metadata.
- `/mnt/data/policy_fabric_repo_snapshot_latest.zip` — latest repository snapshot including `.git`.

## Workflow

1. Edit tracked files in the repository.
2. Run `python scripts/doctor.py`.
3. Run `python scripts/build_dist_bundle.py`.
4. Commit the result and export the latest snapshot zip.

## Current focus

The current focus is turning the architecture into a fully buildable platform contract with stronger semantic validation, richer policy testing, and a repo-native operating model for contract evolution.
