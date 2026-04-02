# AgentPlane integration plan for Policy Fabric

## Purpose

This note reconnects the original goal of the project to the current repository state.
We started by modernizing a technical prior-reference design for platform incorporation.
We then built out the control repository, promotion artifacts, and semantic validation surfaces needed to make that modernization executable.
Now the question is how to place this work into AgentPlane without losing the original point.

## The three identities we must not confuse

### 1. Product identity

**Policy Fabric** is the product.
It is the data-protection policy platform we are designing: authored policy, compiled execution plan, service contracts, promotion artifacts, evidence, and validation.

### 2. Repository identity

**Policy Fabric Control Repository** is the rolling source-of-truth repo.
Its current filesystem path is `policy-fabric-working-repo`, but its role is to be the authoritative cumulative working tree for the product artifacts.

### 3. Workflow/control identity

**AgentPlane** is the candidate repo-native workflow layer.
It should govern how agents operate in this repository.
It should not replace Policy Fabric as the product or collapse the Policy Fabric runtime model into AgentPlane concepts.

## What we originally set out to do

The original task was not “invent repo governance for its own sake.”
The original task was:

1. preserve the strong technical kernel from the prior reference design;
2. modernize it into a platform-grade system;
3. make it incorporable into a larger platform;
4. keep the result buildable and governable.

The repo work was a consequence of that, not a distraction.
It solved the problem of detached artifacts, lost state, and non-reproducible outputs.

## What we have accomplished so far

### A. Preserved and modernized the technical kernel

We preserved the durable concepts from the starting design:

- processor
- selector
- predicate
- graph/DAG execution
- policy-driven behavior
- service wrapper / API surface

We modernized them into:

- Policy v2 schema
- compiled execution-plan IR
- OpenAPI contract
- release pack and evidence artifacts
- capability catalog and semantic validation

### B. Built the repository as a control plane for the design work

We created a cumulative Git-backed repository with:

- active contracts and examples
- blueprints and comparison notes
- repo-native ownership and workflow policy
- reconcile and doctor automation
- reproducible dist bundle generation
- release-pack and evidence validation

### C. Hardened the repo into something AgentPlane can actually govern

We now have:

- an explicit ownership contract
- workflow profiles
- reconcile/repair automation
- machine-readable validation evidence
- a root `AGENTS.md` gateway

That means the repo is now **AgentPlane-ready** even though it is not yet fully AgentPlane-initialized.

## Why the repo work was necessary

Without the rolling repo, we would have had a growing pile of detached schemas, examples, and notes with no stable source of truth, no consistent validation, and no promotion story.
That would have made later AgentPlane adoption harder, not easier.

So the repo work was not a rabbit hole in the bad sense.
It was the step required to turn the original modernization effort into something that can be governed, promoted, and later wrapped with AgentPlane.

## Current architecture stack

### Product layer

Policy Fabric contracts and semantics:

- `contracts/policy_fabric_policy_v2.schema.json`
- `contracts/policy_fabric_execution_plan_ir_v1.schema.json`
- `contracts/policy_fabric_openapi_v2.yaml`
- `contracts/policy_fabric_release_pack_v1.schema.json`
- `contracts/policy_fabric_capability_catalog_v1.schema.json`
- validation and replay report schemas

### Repository workflow layer

Policy Fabric repo governance:

- `.policy-fabric/config.json`
- `.policy-fabric/WORKFLOW.md`
- `.policy-fabric/ownership.json`
- `.policy-fabric/profiles.json`
- `scripts/reconcile.py`
- `scripts/doctor.py`
- `scripts/policy_semantic_validator.py`
- `scripts/build_dist_bundle.py`

### Future AgentPlane layer

AgentPlane should sit around the repo workflow layer, not inside the product semantics.
Its job should be:

- agent startup and task workflow
- managed repair/recovery around repo surfaces
- workflow gating and promotion discipline
- visibility around agent actions in the repository

## Recommended adoption path

### Phase 0 — current state

Stay in the current cumulative repo model.
Use `AGENTS.md` plus `.policy-fabric/` as the authoritative workflow surface.
This is where we are now.

### Phase 1 — disposable AgentPlane evaluation

Clone the repo into a disposable working directory.
Initialize AgentPlane there using the official CLI.
Observe what managed files it generates and how they overlap with the existing repo-governance surfaces.
Do not do this first in the primary working tree.

### Phase 2 — bridge design

Decide whether to:

- keep `.policy-fabric/` authoritative and let AgentPlane reference it, or
- let AgentPlane own startup/workflow surfaces while Policy Fabric remains authoritative for contracts, examples, and release artifacts.

The most likely correct answer is hybrid:

- AgentPlane owns agent workflow and managed startup surfaces.
- `.policy-fabric/` remains authoritative for repository governance and product-specific validation.

### Phase 3 — branch-based initialization

Initialize AgentPlane on a dedicated feature branch.
Review every generated file.
Update the ownership contract and doctor checks so the new `.agentplane/` surfaces become explicit rather than ambient.
Only then merge.

## Immediate practical next steps

1. Keep using this repository as the source of truth.
2. Do not rename or discard `.policy-fabric/` yet.
3. Use `AGENTS.md` as the root gateway for agent workflows right now.
4. When ready, test official AgentPlane initialization in a disposable clone first.
5. After that, encode the chosen bridge model back into the ownership contract and doctor checks.

## Naming answers

- **Product:** Policy Fabric.
- **Rolling repo / source-of-truth repo:** Policy Fabric Control Repository.
- **Current filesystem path:** `policy-fabric-working-repo`.
- **Future workflow wrapper candidate:** AgentPlane.
