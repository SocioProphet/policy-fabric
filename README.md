# Policy Fabric Control Repository

This repository is the cumulative working copy and control repository for the **Policy Fabric** platform.
The filesystem directory is still `policy-fabric-working-repo`, but the repository role is now named **Policy Fabric Control Repository** so we have a stable identity for the rolling repo itself.

## What this repo is

- **Product name:** Policy Fabric.
- **Repository role:** Policy Fabric Control Repository.
- **Current state:** cumulative Git-backed source-of-truth working tree.
- **AgentPlane state:** AgentPlane-ready, but not yet fully AgentPlane-initialized.

The repo keeps the active contracts, aligned examples, supporting design notes, and archived prior-reference artifacts in one place so the work can become a real product repository without reconstructing history from detached files.

## Repository goals

- Keep one authoritative working tree for all current Policy Fabric artifacts.
- Preserve archived prior-reference materials without letting them pollute the active product identity.
- Rebuild the distributable contract bundle reproducibly from repository contents.
- Run reconcile and doctor before each release snapshot.
- Keep ownership, profile, repair, and promotion semantics explicit inside the repo.
- Provide a clean bridge into AgentPlane without losing the Policy Fabric workflow that already exists.

## Active surfaces

- `contracts/` — active machine-readable service and schema contracts.
- `examples/` — aligned example payloads and responses.
- `docs/` — blueprint, assessments, research, comparison, rebrand notes, specs, reports, and turn logs.
- `.policy-fabric/` — repo-local workflow, ownership, profile, repair, generated-report, and AgentPlane-bridge surfaces.
- `scripts/` — reconcile, AgentPlane bridge probing, doctor, semantic validation, and bundle-build utilities.
- `AGENTS.md` — root gateway for coding-agent workflows, including AgentPlane-oriented startup guidance.

## Generated outputs

- `/mnt/data/policy_fabric_contracts_bundle_latest.zip` — latest distributable bundle without Git metadata.
- `/mnt/data/policy_fabric_repo_snapshot_latest.zip` — latest repository snapshot including `.git`.

## Standard loop

1. Edit tracked files in the repository.
2. Run `python scripts/reconcile.py`.
3. Run `python scripts/agentplane_probe.py` when the change affects the AgentPlane bridge or repo workflow surfaces.
4. Run `python scripts/doctor.py`.
5. Review `docs/reports/doctor_latest.md`, `docs/reports/validation_report_latest.json`, and `docs/reports/agentplane_probe_latest.md` as applicable.
6. Run `python scripts/build_dist_bundle.py`.
7. Commit the result and export the latest snapshot zip.

## How this relates to AgentPlane

Policy Fabric is the product and runtime/control-plane design.
This repository is the source-of-truth control repo for that work.
AgentPlane is the candidate repo-native workflow layer we can place around this repository.

The intended relationship is:

- Policy Fabric stays the product identity and the data-protection platform.
- Policy Fabric Control Repository stays the authoritative design/contracts repo.
- AgentPlane, if adopted, should govern repository workflow, repair, recovery, and promotion discipline around this repo rather than replace the Policy Fabric runtime model.

See `AGENTS.md`, `.policy-fabric/agentplane_bridge.json`, and `docs/specs/agentplane_integration_plan.md` for the explicit bridge.

## Current focus

The current focus is reconnecting the original modernization goal to the repo we built: preserve the strong technical kernel, make the contracts and promotion artifacts executable, and now prepare a clean AgentPlane adoption path without throwing away the Policy Fabric governance layer we already created.
