# Semantic Validation Guide

## Purpose

Policy Fabric now exposes a stable semantic-validation execution surface.

The recommended command is:

```bash
python3 scripts/policy_semantic_validate.py
```

This wrapper gives the repository one predictable front door while semantic-validator behavior continues to evolve through tranches.

## Execution order

The wrapper currently resolves validator sources in this order:
1. `scripts/policy_semantic_validator_tranche_03_runner.py`
2. `scripts/policy_semantic_validator.py`

This means newer tranche logic can be exercised without requiring every tranche to rewrite the legacy validator entrypoint immediately.

## What semantic validation covers today

The semantic-validation stack now spans:
- selector-overlap heuristics
- classified overlap reason codes
- negative fixture semantics
- no-op fixture semantics
- tranche-3 helper logic for precedence, cardinality, rollout subsumption, and explainability scaffolding

## What it does not fully cover yet

The main `scripts/policy_semantic_validator.py` entrypoint is not yet fully rewritten to inline all tranche-3 logic. Instead, the stable wrapper routes to the most capable available validator surface.

## Recommended maintainer posture

Treat `python3 scripts/policy_semantic_validate.py` as the preferred semantic-validation command until maintainers explicitly consolidate the wrapper and runner behavior back into a single validator entrypoint.

## Related artifacts

- `docs/specs/semantic_validator_execution_surface.md`
- `docs/specs/semantic_tranche_01.md`
- `docs/specs/semantic_tranche_02.md`
- `docs/specs/semantic_tranche_03.md`
- `scripts/policy_semantic_validator_tranche_03_runner.py`
- `scripts/policy_semantic_tranche_03.py`
