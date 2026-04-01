# What Policy Fabric Can Learn from SocioProphet AgentPlane

## Core lesson

The most valuable lesson is not the VM substrate. It is the operating discipline:
**bundle -> validate -> run -> evidence -> replay**.
For Policy Fabric, that becomes **release pack -> validate -> replay -> promote -> attest**.

## Strong lessons to copy

### 1. Promotion artifact first
AgentPlane treats bundles as the deployment unit with metadata, policy intent, smoke hooks, artifact output paths, and secret references.
Policy Fabric should likewise treat the release pack as the promotion unit instead of promoting loose policy JSON plus side-channel CI state.

### 2. Evidence is part of the system model
AgentPlane's system-space note says runs emit validation, placement, run, and replay artifacts.
That is the right posture for us too: evidence is not optional logging; it is part of the contract.

### 3. Repo-owned truth beats host-local truth
AgentPlane prefers bundle pinning and repo fleet inventory over host-local fallback files.
For us, the analog is repo-owned contracts, release packs, provider refs, and policy fixtures rather than environment-specific deploy glue.

### 4. Secrets stay as references
The bundle schema explicitly says secrets are refs/paths only, never inline values.
That matches our trust model and should remain non-negotiable.

### 5. One stable runner contract across backends
AgentPlane keeps run/stop/status/logs/smoke/promote/rollback stable even as backends change.
For Policy Fabric, the analogous lesson is keeping process/validate/compile/explain/evidence stable even as adapters, provider backends, and deployment modes evolve.

### 6. Backend intent should be declared, not inferred from ambient state
AgentPlane records backend intent and explicit executor precedence.
Our analog is declaring provider class, execution mode, release lane, and replay mode directly in the pack and plan.

### 7. System evolution should be explicit
AgentPlane documents a path from local-first to fleet to image-native delivery.
We should do the same for Policy Fabric: local validation -> service deployment -> sidecar/stream rollout -> signed release promotion.

### 8. Compliance gates belong in artifacts
The bundle schema includes a license policy gate.
For Policy Fabric, we should treat re-identification approval, region constraints, and human-gate requirements the same way: explicit in artifacts.

## Lessons to reject

- Do not turn Policy Fabric into a VM orchestration platform.
- Do not import Nix, Lima, QEMU, or fleet inventory concepts unless we truly need infrastructure orchestration.
- Do not let release packs absorb runtime secrets or environment-specific inline configuration.

## Translation into Policy Fabric

This turn adds:
- a `ReleasePack` schema
- a `ValidationReport` schema
- a `ReplayReport` schema
- aligned examples for each

These are not copies of AgentPlane artifacts.
They are the Policy Fabric translation of the strongest AgentPlane governance pattern.
