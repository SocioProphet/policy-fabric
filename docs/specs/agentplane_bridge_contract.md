# AgentPlane bridge contract for Policy Fabric

## Purpose

This document defines the bridge between the **Policy Fabric Control Repository** and the **official AgentPlane** workflow model.
It exists because the repo already has a Policy Fabric governance surface under `.policy-fabric/`, while official AgentPlane expects to generate and manage a separate `.agentplane/` workflow surface and a root gateway file such as `AGENTS.md`.

## Design goal

Adopt official AgentPlane as a workflow wrapper **without** collapsing Policy Fabric product semantics into AgentPlane.
The bridge is therefore hybrid:

- official AgentPlane owns its own managed runtime/workflow surface after initialization;
- `.policy-fabric/` remains authoritative for Policy Fabric-specific governance, validation, promotion artifacts, and bundle generation.

## Expected official AgentPlane surfaces

The public AgentPlane docs and repository describe these repo-visible workflow artifacts:

- `AGENTS.md` or `CLAUDE.md`
- `.agentplane/config.json`
- `.agentplane/WORKFLOW.md`
- `.agentplane/tasks/`
- `.agentplane/tasks.json` (optional export)
- `.agentplane/policy/**`
- `.agentplane/policy/incidents.md` as the sanctioned local override area
- `.agentplane/workflows/last-known-good.md` as a recovery/runtime artifact

## Policy Fabric surfaces that must remain authoritative

Even after AgentPlane adoption, these remain authoritative for the product design itself:

- `contracts/**`
- `examples/**`
- `docs/specs/**`
- `docs/assessments/**`
- `.policy-fabric/config.json`
- `.policy-fabric/ownership.json`
- `.policy-fabric/profiles.json`
- `scripts/doctor.py`
- `scripts/policy_semantic_validator.py`
- `scripts/build_dist_bundle.py`

## Collision handling

### Root gateway

`AGENTS.md` is the main collision point because both Policy Fabric and official AgentPlane use it.
Current rule:

- do not hand-author a fake official AgentPlane managed gateway;
- when official AgentPlane init is run, do it on a dedicated branch;
- let the CLI generate or upgrade its own gateway material;
- then reconcile the gateway so Policy Fabric instructions and AgentPlane-managed sections coexist intentionally.

### Workflow directories

`.policy-fabric/` is not replaced by `.agentplane/`.
Instead:

- `.agentplane/` becomes the official AgentPlane workflow surface;
- `.policy-fabric/` remains the product-specific governance surface.

### Managed ownership

After official init, ownership should be updated as follows:

- `.agentplane/policy/**` → AgentPlane-managed
- `.agentplane/policy/incidents.md` → sanctioned local override
- `.agentplane/WORKFLOW.md`, `.agentplane/config.json`, `.agentplane/workflows/**` → generated or AgentPlane-managed

## Trial status

We completed a no-touch compatibility probe in a disposable clone.
We did **not** complete an actual `agentplane init` in this container because the npm execution path for the public CLI was blocked by an authentication failure in the container environment.
That is an environment limitation, not a repository-design limitation.

## Next action

Run the official CLI init in a disposable clone from a clean environment where `npm install -g agentplane` or equivalent package execution works, then merge the observed surfaces back into the bridge contract and ownership/doctor checks.
