# Branch Safety

## Purpose

This repository started as a single-user bootstrap control repo with a clean linear history on `main`. That kept the build loop simple while the core contracts stabilized. The next phase carries more risk: official AgentPlane initialization, ownership-model changes, bundle-build changes, and deeper semantic-validator changes. Those changes should not land on `main` without a tagged recovery point and a work branch.

## Current Policy

- `main` is the protected baseline branch.
- Direct commits to `main` are tolerated only during bootstrap and only while no remote protection exists.
- High-risk changes must branch from a tagged good baseline.
- Use `baseline/` tags for recovery points and `work/` branches for risky development.

## Required Preflight For High-Risk Work

1. Ensure the worktree is clean enough to produce deterministic reports.
2. Run `python scripts/reconcile.py`.
3. Run `python scripts/branch_audit.py`.
4. Run `python scripts/doctor.py`.
5. Create a `baseline/` tag on the current good state.
6. Create a `work/` branch from that baseline.

## High-Risk Work Classes

- official AgentPlane init
- ownership-model changes
- bundle-build changes
- schema-breaking changes
- validator-breaking changes
- history rewrite

## Current Recommended Branches

- `work/official-agentplane-init-eval`
- `work/policy-semantics-overlap`
