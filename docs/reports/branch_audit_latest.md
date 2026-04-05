# Branch Audit Report

Overall status: WARN

Current branch: `docs/github-publish-pairing-prep`
Local branches: `4`
Remotes: `0`
Merge commits in history: `0`

- [OK] branch:head-attached — PFB010_BRANCH_HEAD_OK — HEAD is attached to `docs/github-publish-pairing-prep`
- [OK] branch:merge-state — PFB012_BRANCH_STATE_OK — No in-progress merge/rebase/cherry-pick/revert state detected
- [OK] branch:main-present — PFB014_BRANCH_MAIN_PRESENT — `main` branch exists
- [OK] branch:single-main-only — PFB017_BRANCH_TOPOLOGY_OK — Local branches present: ['docs/github-publish-pairing-prep', 'main', 'work/official-agentplane-init-eval', 'work/policy-semantics-overlap']
- [WARN] branch:remotes — PFB019_BRANCH_NO_REMOTE — No remotes configured in snapshot; remote protection cannot be observed here
- [WARN] branch:merge-history — PFB020_BRANCH_LINEAR_HISTORY — History is fully linear so far; keep baseline tags and use work branches for risky changes
- [OK] branch:baseline-tags — PFB022_BRANCH_BASELINE_TAGS_OK — Baseline tags present: ['baseline/2026-04-02_pre-branch-audit', 'baseline/2026-04-04_branch-audited', 'baseline/2026-04-05_pre-github-publish-prep']
- [OK] branch:policy-protected-main — PFB024_BRANCH_POLICY_OK — Branch policy protects `main` as the baseline branch

## Recommended Next Work Branches

- `work/official-agentplane-init-eval` — Run the first real official AgentPlane initialization in a disposable clone or feature branch.
- `work/policy-semantics-overlap` — Deepen selector-overlap analysis and richer failure-fixture semantics without risking the main workflow surfaces.
