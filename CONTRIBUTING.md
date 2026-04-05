# Contributing to Policy Fabric Control Repository

This repository is the source-of-truth control repository for **Policy Fabric**. Treat it like a governed product repository, not a throwaway working directory.

## Working model

Use the repo in three layers:

1. **Product layer** — contracts, examples, semantics, evidence, release packs.
2. **Control-repo layer** — reconcile, doctor, branch audit, publish prep, bundle build.
3. **Workflow layer** — current `.policy-fabric/` governance and future official AgentPlane initialization.

## Standard local loop

1. Start from `AGENTS.md` and `README.md`.
2. Read `.policy-fabric/WORKFLOW.md` and `.policy-fabric/ownership.json`.
3. For risky changes, run `python scripts/branch_audit.py`, tag a baseline, and branch off `main`.
4. Make the change.
5. Run `python scripts/reconcile.py`.
6. Run `python scripts/agentplane_probe.py` if workflow or AgentPlane bridge surfaces changed.
7. Run `python scripts/github_publish_prep.py` if GitHub-facing surfaces changed.
8. Run `python scripts/doctor.py`.
9. Run `python scripts/build_dist_bundle.py`.
10. Review the generated reports before committing.

## Pair programming push model

Use short, explicit driver/navigator loops.

- **Driver** edits files, runs commands, and records decisions.
- **Navigator** checks contract alignment, branch safety, and report outputs.
- Keep work on a feature branch unless the repo is in a narrow bootstrap exception.
- Push early when the branch contains a coherent slice, not a half-edited worktree.
- Open a pull request even for solo work once the repository has a real remote and branch protection.

## Branch and PR expectations

- `main` is the protected baseline.
- Prefer `work/`, `docs/`, `fix/`, or `spike/` branches.
- Use baseline tags before high-risk changes.
- Keep PRs scoped to one concern: contracts, docs, validator semantics, workflow bridge, or release automation.
- Include report outputs or summaries when a change affects generated evidence.

## GitHub publish expectations

The recommended first remote is `SocioProphet/policy-fabric-control-repository` and the recommended initial visibility is **private** until licensing and disclosure posture are frozen.

Before the first push:

- run `python scripts/github_publish_prep.py`
- verify `docs/reports/github_publish_prep_latest.md`
- verify `docs/reports/doctor_latest.md`
- verify `docs/reports/branch_audit_latest.md`
- build `dist/policy_fabric_contracts_bundle_latest.zip`

See `docs/specs/github_publish_and_pairing.md` for the detailed bootstrap path.
