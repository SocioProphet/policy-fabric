# Semantic Tranche 3 — Handoff and Implementation Plan

## Current branch state

Branch: `work/semantic-tranche-03`

This tranche now contains:
- a normative tranche spec (`docs/specs/semantic_tranche_03.md`)
- a helper implementation module for precedence, cardinality, and rollout-subsumption analysis (`scripts/policy_semantic_tranche_03.py`)
- a tranche-specific policy example (`examples/policy_fabric_policy_v2_semantic_tranche_03_example.json`)
- a tranche-specific validation report example (`examples/policy_fabric_validation_report_tranche_03_example.json`)

## What is done

### 1. Precedence semantics are framed
The tranche spec now names explicit reason-code families for:
- precedence required
- precedence conflict
- rollout subsumption warning
- rollout shadow conflict
- explain decision incomplete

### 2. Cardinality semantics are framed
The helper module now flags selectors that may overmatch relative to a declared `expectedCardinality`, especially wildcard JSONPath and non-anchored regex cases.

### 3. Rollout subsumption semantics are framed
The helper module now models scope overlap and scope subsumption across:
- mode
- environment
- route
- purpose

### 4. Example artifacts exist
The example policy intentionally creates:
- one same-priority precedence conflict
- one wider-scope shadowing case
- one cardinality-overmatch case

The example validation report documents the expected findings for those semantics.

## What is not done yet

### 1. Main validator integration is not complete
The main `scripts/policy_semantic_validator.py` entrypoint still needs to import or inline the tranche-3 helper logic so these findings become part of the default semantic-validation pipeline.

### 2. Generated control-surface artifacts are not refreshed for this tranche yet
If tranche-3 is elevated from branch-local semantic prep to merge-ready control-surface work, the repo should regenerate and version any relevant report/manifest fallout.

### 3. Explain-surface wiring is still illustrative
We have defined reason-code families and example semantics, but we have not yet wired compiled explain outputs or runtime decision traces to emit winner-rule justification.

## Recommended next implementation slice

Patch `scripts/policy_semantic_validator.py` to:
1. import tranche-3 helper routines
2. run tranche-3 checks after tranche-2 overlap classification
3. emit findings using these reason codes:
   - `PFV020_RULE_PRECEDENCE_REQUIRED`
   - `PFV021_RULE_PRECEDENCE_CONFLICT`
   - `PFV022_SELECTOR_CARDINALITY_OVERMATCH`
   - `PFV023_SELECTOR_CARDINALITY_UNDERSPECIFIED`
   - `PFV024_ROLLOUT_SUBSUMPTION_WARNING`
   - `PFV025_ROLLOUT_SHADOW_CONFLICT`
   - `PFV026_EXPLAIN_DECISION_INCOMPLETE`

## Merge recommendation

This branch is now in a good **semantic-prep / handoff** state.

It is strong enough to pause and hand off because:
- the tranche intent is explicit
- the example policy is concrete
- the expected findings are documented
- the next implementation slice is narrowly defined

It is **not** yet in a good final-merge state if the requirement is full mainline validator integration in the same PR.

## Clean handoff summary

If another maintainer or agent picks this up, the next safest move is:
1. patch `scripts/policy_semantic_validator.py`
2. refresh generated reports/manifests if required by repo policy
3. verify PR scope stayed coherent
4. then merge PR #9
