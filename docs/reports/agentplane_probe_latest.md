# AgentPlane probe report

- Generated at: `2026-04-02T14:27:51.107921Z`
- Target: `official-agentplane`
- Trial mode: `no-touch-disposable-clone-probe`
- Status: `warn`
- Checks: `10` total / `0` fail / `4` warn

## Highlights

- ✅ `PFA001_BRIDGE_CONTRACT_PRESENT` — AgentPlane bridge contract present
  - Artifact: `.policy-fabric/agentplane_bridge.json`
- ✅ `PFA010_NODE_OK` — node available for official AgentPlane prerequisite check
  - stdout=v22.16.0
- ✅ `PFA012_NPM_OK` — npm available for official AgentPlane prerequisite check
  - stdout=10.9.2
- ⚠️ `PFA021_CLI_NOT_ON_PATH` — agentplane executable not on PATH in current container
- ✅ `PFA022_PACKAGE_VISIBLE` — npm package metadata for agentplane is visible in the current container
  - stdout=0.3.7
- ⚠️ `PFA025_NPX_HELP_BLOCKED` — npx agentplane --help did not execute cleanly in the current container
  - stderr=npm error code E401
npm error Incorrect or missing password.
npm error If you were trying to login, change your password, create an
npm error authentication token or enable two-factor authentication then
npm error that means you likely typed your password in incorrectly.
npm error Please try again, or recover your password at:
npm error   https://www.npmjs.com/forgot
npm error
npm error If you were doing some other operation then your saved credentials are
npm error probably out of date. To corr
- ⚠️ `PFA030_ROOT_GATEWAY_COLLISION` — AGENTS.md already exists and is the main collision point with official AgentPlane init
  - Artifact: `AGENTS.md`
- ✅ `PFA032_POLICY_FABRIC_SURFACE_PRESENT` — .policy-fabric workflow surface present
  - Artifact: `.policy-fabric/`
- ℹ️ `PFA034_AGENTPLANE_SURFACE_ABSENT` — no .agentplane tree exists yet; no mixed-state workspace is present
  - Artifact: `.agentplane/`
- ⚠️ `PFA040_BRIDGE_COLLISIONS_IDENTIFIED` — bridge contract identifies collisions or execution blockers that must be resolved before official init
  - Artifact: `.policy-fabric/agentplane_bridge.json`
  - count=2

## Next action

Run official AgentPlane init in a disposable clone from a clean environment where npm package execution works, then merge the observed managed surfaces back into the ownership contract and doctor checks.
