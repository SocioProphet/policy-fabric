# Semantic Tranche 3 — Merge Criteria Checklist

## Branch purpose

PR #9 is currently a **semantic-prep / handoff tranche**.

It is intended to make the next validator-integration slice deterministic, reviewable, and low-ambiguity.

## Already present on the branch

- tranche spec
- helper implementation module
- tranche-specific policy example
- tranche-specific validation-report example
- tranche-specific explain/decision example
- handoff / implementation-plan doc

## Minimum criteria to merge as a prep tranche

This branch is acceptable to merge as a prep tranche if maintainers agree that:
- additive spec/example/helper surfaces are valuable on their own
- main-validator integration will be delivered in the next PR
- no shared control-surface artifacts need regeneration yet because the main validator entrypoint was not changed

## Minimum criteria to merge as a full tranche

This branch should **not** be treated as a full Tranche 3 semantic implementation until all of the following are true:

1. `scripts/policy_semantic_validator.py` imports or inlines Tranche 3 logic
2. Tranche 3 reason-code families are emitted by the default validator path
3. any shared example/report surfaces affected by validator behavior are updated
4. generated repo control-surface artifacts are refreshed if required by repo policy
5. PR discussion explicitly states whether PR #9 is prep-only or full semantic integration

## Recommended next patch sequence

1. integrate `scripts/policy_semantic_tranche_03.py` into the main validator
2. widen shared validation examples only if the repo wants Tranche 3 semantics reflected in default examples
3. regenerate repo-managed reports/manifests if validator behavior changes
4. re-check PR scope and merge intent

## Stop / handoff condition

The branch is in a good stop-and-handoff state when:
- a maintainer can see what Tranche 3 is
- a maintainer can run the helper/example artifacts independently
- the next patch target is obvious
- there is no ambiguity about whether the PR is prep-only or fully integrated
