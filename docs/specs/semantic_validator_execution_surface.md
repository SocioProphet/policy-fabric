# Semantic Validator Execution Surface

## Goal

Provide one stable command surface for semantic validation while the repository transitions from tranche-specific helper modules toward a unified main validator entrypoint.

## Current execution order

The recommended execution wrapper is:

```bash
python3 scripts/policy_semantic_validate.py
```

The wrapper resolves validator sources in this order:
1. `scripts/policy_semantic_validator_tranche_03_runner.py`
2. `scripts/policy_semantic_validator.py`

This means the repository can expose newer tranche behavior without requiring an immediate in-place rewrite of the main validator module.

## Why this wrapper exists

The repository has evolved through semantic tranches:
- Tranche 1: selector-overlap heuristics and negative fixtures
- Tranche 2: classified overlap and explicit no-op semantics
- Tranche 3 prep: precedence, cardinality, rollout-subsumption, and explainability scaffolding
- Tranche 3 integration: additive runner surface

A stable wrapper avoids forcing all tranche work to land through a single brittle entrypoint edit.

## Short-term posture

Short term, this wrapper should be treated as the preferred semantic-validation command surface.

## Long-term posture

Long term, maintainers may choose one of two paths:
1. inline the runner logic back into `scripts/policy_semantic_validator.py`
2. keep the wrapper as the stable public command surface and allow tranche-specific runners behind it

## Merge guidance

A branch that adds semantic-validator behavior without modifying the main entrypoint directly is still acceptable if:
- it improves the effective execution surface
- it remains additive and reviewable
- the wrapper clearly defines precedence among validator sources

## Handoff note

If another maintainer picks this up, the next clean consolidation step is:
- move tranche-3 runner logic into the main validator or
- explicitly bless the wrapper as the permanent front door
