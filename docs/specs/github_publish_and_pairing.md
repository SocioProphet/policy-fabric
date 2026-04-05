# GitHub Publish and Pairing Plan

## Purpose

This document turns the local **Policy Fabric Control Repository** into a push-ready GitHub repository without losing the repo-native governance already built under `.policy-fabric/`.

## Recommended initial remote

- Owner: `SocioProphet`
- Repository: `policy-fabric-control-repository`
- Initial visibility: `private`
- Default branch: `main`

Keep the initial publication private until licensing, disclosure routing, and first official AgentPlane initialization are settled.

## Pre-publish checklist

1. Restore the latest repo snapshot or start from the current local working tree.
2. Run `python scripts/branch_audit.py`.
3. Tag a clean baseline if the next step is risky.
4. Run `python scripts/reconcile.py`.
5. Run `python scripts/agentplane_probe.py` if bridge/workflow surfaces changed.
6. Run `python scripts/github_publish_prep.py`.
7. Run `python scripts/doctor.py`.
8. Run `python scripts/build_dist_bundle.py`.
9. Review `docs/reports/github_publish_prep_latest.md`, `docs/reports/doctor_latest.md`, and `docs/reports/branch_audit_latest.md`.

## Publish path A: GitHub CLI

Use GitHub CLI to create the remote from the existing local repository, then push the current branch and tags.

Recommended command:

```bash
gh repo create SocioProphet/policy-fabric-control-repository --private --source . --remote origin --push --description "Control repository for Policy Fabric contracts, examples, workflow governance, and promotion artifacts."
```

## Publish path B: Web UI + git remote

1. Create an empty repository in the GitHub web UI.
2. Do not add a README, license, or gitignore during creation.
3. Add the remote locally.
4. Push `main` and tags.

```bash
git remote add origin git@github.com:SocioProphet/policy-fabric-control-repository.git
git push -u origin main --follow-tags
```

## Pair programming push model

### Roles

- **Driver**: edits files, runs commands, and writes commit messages.
- **Navigator**: watches contract drift, checks generated reports, and validates that the branch remains scoped.

### Rhythm

- Work on a feature branch.
- Push at the end of each coherent slice.
- Use pull requests even for solo work once the remote exists.
- Require repo-health checks before merge.

### First pairing push

The best first pairing push is a low-risk bootstrap PR that only verifies:

- remote creation
- CI workflow discovery
- issue and PR templates
- CODEOWNERS placeholder visibility
- doctor and bundle generation on GitHub Actions

Do **not** combine the first remote push with the first official AgentPlane initialization.

## Post-publish GitHub settings

After the first push:

1. Set `main` as the default branch.
2. Configure branch protection or a ruleset for `main`.
3. Require pull requests and at least one approval.
4. Require the repo-health status check.
5. Keep force-pushes and deletions disabled on `main`.
6. Enable issues and use the repository templates in `.github/ISSUE_TEMPLATE/`.

## Current non-blockers vs blockers

### Non-blockers

- no remote yet
- CODEOWNERS still placeholder-only
- official AgentPlane init not yet executed

### Blockers for public publication

- license decision is pending
- disclosure route is pending
- official AgentPlane init has not yet been trialed in a clean environment
