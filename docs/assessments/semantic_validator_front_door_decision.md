# Semantic Validator Front-Door Decision

## Decision to be made

Policy Fabric now has multiple semantic-validation surfaces:
- `scripts/policy_semantic_validator.py`
- `scripts/policy_semantic_validator_tranche_03_runner.py`
- `scripts/policy_semantic_validate.py`

The repository now needs an explicit decision about which of these is the **front door** for semantic validation.

## Option A — Keep the wrapper as the front door

Use:

```bash
python3 scripts/policy_semantic_validate.py
```

### Advantages
- stable command surface
- additive and low-risk
- allows tranche-specific runners behind one predictable entrypoint
- minimizes brittle in-place rewrites of the legacy validator module

### Costs
- one extra abstraction layer
- the main validator remains only part of the effective execution path
- future maintainers must understand wrapper precedence rules

## Option B — Consolidate back into the main validator

Use:

```bash
python3 scripts/policy_semantic_validator.py
```

and inline runner/tranche logic into that module.

### Advantages
- one obvious implementation path
- less indirection
- easier to explain to maintainers who expect a single validator module

### Costs
- higher short-term rewrite risk
- more brittle during active tranche evolution
- requires more careful regression handling for merged semantic work

## Current recommendation

Short term, Policy Fabric should treat `scripts/policy_semantic_validate.py` as the **preferred front door**.

That keeps the repo operationally stable while semantic tranches continue to accumulate.

## Consolidation trigger

A later consolidation back into `scripts/policy_semantic_validator.py` becomes reasonable when all of the following are true:
- tranche behavior has stabilized
- maintainers no longer expect frequent runner layering
- the wrapper no longer adds meaningful safety or flexibility
- the semantic-validation execution order is unlikely to change again soon

## Merge guidance

This document is intended to record the architectural choice explicitly before another tranche changes the execution surface again.

If maintainers agree with the current recommendation, the next implementation slice should:
1. keep the wrapper as the preferred front door
2. update any remaining docs that still imply the legacy validator is the main command
3. defer consolidation until semantic behavior stabilizes further

If maintainers reject the recommendation, the next slice should be a narrow consolidation PR only.
