# Maintainer Runbook

## Purpose

This runbook is the shortest path for a maintainer to understand how to operate the Policy Fabric repository without reconstructing context from chat history.

## Repository posture

Policy Fabric is both:
- a product-contract repository
- a control repository

That means generated manifests and validation outputs may be intentionally versioned when they are part of the governed control surface.

## Recommended command surfaces

### Core repo health

```bash
python3 scripts/reconcile.py
python3 scripts/doctor.py
```

### Semantic validation

Preferred command surface:

```bash
python3 scripts/policy_semantic_validate.py
```

This wrapper is currently the recommended front door for semantic validation.

### Additional governance checks

Use these when the change affects workflow, branch, AgentPlane, or GitHub-facing repo surfaces:

```bash
python3 scripts/agentplane_probe.py
python3 scripts/branch_audit.py
python3 scripts/github_publish_prep.py
```

## Branching posture

- `main` is the stable baseline.
- use `work/*` branches for tranche-scoped or risky changes.
- keep PRs narrow and coherent.
- prefer additive slices when connector or tooling behavior makes in-place rewrites brittle.

## Semantic-validation posture

The current semantic-validation stack includes:
- `scripts/policy_semantic_validator.py`
- `scripts/policy_semantic_tranche_03.py`
- `scripts/policy_semantic_validator_tranche_03_runner.py`
- `scripts/policy_semantic_validate.py`

Current recommendation:
- treat `scripts/policy_semantic_validate.py` as the preferred front door
- defer full consolidation back into the legacy validator until tranche behavior stabilizes further

## What to read first

If resuming work after a pause, start with:
- `README.md`
- `docs/SEMANTIC_VALIDATION.md`
- `docs/specs/semantic_validator_execution_surface.md`
- `docs/assessments/semantic_validator_front_door_decision.md`
- latest open PR descriptions and changed files

## Good next-step discipline

Before opening the next tranche:
1. confirm `main` is the actual baseline
2. decide whether the tranche is prep, execution, consolidation, or docs
3. keep the PR description explicit about what is intentionally not included
4. only regenerate repo-managed reports/manifests when the branch actually changes the governed execution or documentation surface that owns them

## Stop / handoff condition

The repo is in a good handoff state when:
- the preferred command surface is obvious
- the next architectural decision is written down in-repo
- the next patch target is narrow
- maintainers do not need chat history to understand current posture
