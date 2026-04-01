# What Policy Fabric Can Learn from Official AgentPlane Site/Docs

This note supersedes earlier AgentPlane research that focused on repository layouts rather than the official public product/docs surfaces.

## Source used

- https://agentplane.org/
- https://agentplane.org/docs/user/overview/
- https://agentplane.org/docs/user/prerequisites/
- https://agentplane.org/docs/user/setup/
- https://agentplane.org/docs/user/agent-bootstrap.generated/
- https://agentplane.org/docs/help/legacy-upgrade-recovery/
- https://agentplane.org/docs/releases/v0.3.2/

## Strong lessons

### 1. Local-first, repo-native execution
AgentPlane presents itself as a local CLI workflow for agent-driven development in a git repository, not a hosted service. The durable lesson is that workflow state, approvals, artifacts, and recovery surfaces should live with the repo rather than in a hidden control plane.

### 2. Make workflow policy explicit and versioned
The official docs center `AGENTS.md`, `.agentplane/config.json`, and `.agentplane/WORKFLOW.md` as explicit local governance surfaces. The lesson for Policy Fabric is to keep authored policy, release-pack policy, and repo workflow policy as first-class versioned artifacts.

### 3. Profiles are a better onboarding mechanism than a single rigid mode
AgentPlane setup uses `light`, `normal`, and `full-harness` profiles with different default approvals and hooks. The lesson is that one product can support multiple guardrail postures without forking the whole tool.

### 4. Recovery is a primary UX, not an afterthought
The public docs emphasize `doctor`, `upgrade`, and the shortest recovery path for partially updated repos. The lesson is that governed systems must model mixed state and provide a deterministic repair path.

### 5. Managed ownership boundaries should be explicit
AgentPlane documents a sharp line between framework-managed files and a sanctioned local override area. The lesson is that Policy Fabric should distinguish generated/managed contract surfaces from local override and incident surfaces.

### 6. Happy-path compression matters
The generated bootstrap page compresses the startup path into a small command block and keeps non-default paths out of the normal route. The lesson is to optimize for a very short default path while isolating exceptional flows.

### 7. Evidence should be emitted automatically by core workflow commands
AgentPlane setup says core workflow operations write evidence to `.agentplane/workflows/evidence/`. The lesson is that evidence belongs in the normal workflow, not only in exceptional debugging.

### 8. Drift checks should cover docs and operator guidance too
The release notes show startup-surface drift checks that keep bootstrap docs, quickstart output, and role guidance aligned. The lesson is that documentation drift is a real correctness bug and should be checked like code.

## Translation into Policy Fabric

These lessons reinforce the following Policy Fabric directions:

- keep Policy Fabric repo-native and local-first for authoring/governance work
- formalize managed ownership of contracts and generated workflow surfaces
- add profile-based repo guardrails rather than one global strictness level
- elevate doctor/upgrade/reconcile into first-class workflow features
- store promotion evidence and replay evidence as expected normal artifacts
- treat docs and workflow guidance as testable outputs, not static prose

## Immediate implications

1. Add a repo ownership contract under `.policy-fabric/`.
2. Add a `reconcile`/`upgrade` discipline for managed artifacts.
3. Add profile-aware workflow modes for solo vs gated release work.
4. Extend `doctor` beyond structure into semantic and drift checks.
5. Keep release packs and evidence files as ordinary tracked artifacts.
