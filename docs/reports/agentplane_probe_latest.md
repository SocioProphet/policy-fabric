# AgentPlane probe report

- Generated at: `2026-04-06T08:23:12.088487Z`
- Target: `official-agentplane`
- Trial mode: `no-touch-disposable-clone-probe`
- Status: `warn`
- Checks: `10` total / `0` fail / `4` warn

## Highlights

- ✅ `PFA001_BRIDGE_CONTRACT_PRESENT` — AgentPlane bridge contract present
  - Artifact: `.policy-fabric/agentplane_bridge.json`
- ✅ `PFA010_NODE_OK` — node available for official AgentPlane prerequisite check
  - stdout=v24.14.1
- ✅ `PFA012_NPM_OK` — npm available for official AgentPlane prerequisite check
  - stdout=11.12.1
- ⚠️ `PFA021_CLI_NOT_ON_PATH` — agentplane executable not on PATH in current container
- ✅ `PFA022_PACKAGE_VISIBLE` — npm package metadata for agentplane is visible in the current container
  - stdout=0.3.10
- ✅ `PFA024_NPX_HELP_OK` — npx agentplane --help executed successfully in the current container
  - stdout=Usage:
  agentplane help [<cmd...>] [--compact] [--json]

Commands:
  Backend:
    backend  Backend-related operations.
    backend inspect  Inspect visible backend readiness facts without mutating remote state.
    backend migrate-canonical-state  Backfill canonical_state for issues in the configured backend.
    backend sync  Sync the configured backend (push or pull).
    sync  Sync the configured backend (alias).
  Branch:
    branch base  Manage the pinned base branch used in branch_pr work
- ⚠️ `PFA030_ROOT_GATEWAY_COLLISION` — AGENTS.md already exists and is the main collision point with official AgentPlane init
  - Artifact: `AGENTS.md`
- ✅ `PFA032_POLICY_FABRIC_SURFACE_PRESENT` — .policy-fabric workflow surface present
  - Artifact: `.policy-fabric/`
- ⚠️ `PFA035_AGENTPLANE_SURFACE_PRESENT` — .agentplane tree already exists and should be reviewed for ownership and drift
  - Artifact: `.agentplane/`
- ⚠️ `PFA040_BRIDGE_COLLISIONS_IDENTIFIED` — bridge contract identifies collisions or execution blockers that must be resolved before official init
  - Artifact: `.policy-fabric/agentplane_bridge.json`
  - count=2

## Next action

Run official AgentPlane init in a disposable clone from a clean environment where npm package execution works, then merge the observed managed surfaces back into the ownership contract and doctor checks.
