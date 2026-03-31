# AgentPlane Alignment Notes

This note captures how current AgentPlane ideas inform the Policy Fabric working repository and future control-plane design.

## What AgentPlane contributes

The GitHub repository and public docs describe AgentPlane as a git-native control plane for auditable agent work, with a policy gateway file at the repo root, repo-local workflow state under `.agentplane/`, explicit task state, verification, and closure recorded in the repository.

Useful patterns for Policy Fabric:

1. **Repo-native visible workflow surface**
   A governed system should leave state in the repository, not just in chat or ephemeral memory.

2. **Managed ownership boundaries**
   AgentPlane distinguishes framework-managed files from sanctioned local override areas. Policy Fabric should do the same for generated contracts, local notes, and archived references.

3. **Doctor and upgrade ergonomics**
   AgentPlane emphasizes `doctor` and `upgrade` flows to detect drift and recover partially updated repositories. Policy Fabric should adopt the same discipline for contract bundles and generated outputs.

4. **Workflow modes**
   AgentPlane supports both `direct` and `branch_pr` integration styles. Policy Fabric can eventually mirror this with a lighter solo-edit mode and a stricter release-gated mode.

5. **Explicit closure and verification**
   Changes should not count as done until validation, examples, and release artifacts have been rebuilt and recorded.

## How the two systems come together

Policy Fabric and AgentPlane solve different layers.

- Policy Fabric defines the governed runtime for data-protection policy execution.
- AgentPlane demonstrates a governed repository workflow for how humans and agents evolve a technical system.

The immediate synthesis is operational rather than semantic: use a repo-native workflow surface to evolve Policy Fabric safely.

## Recommended adaptation for Policy Fabric

- keep `.policy-fabric/` as the repo-local workflow namespace rather than adopting `.agentplane/`
- add a `doctor` command and report
- add a reproducible `build bundle` script
- record change notes per turn under `docs/turns/`
- later, consider a stricter gated workflow mode for release preparation

## References

- GitHub: basilisk-labs/agentplane
- Docs: agentplane.org
