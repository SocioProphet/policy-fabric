# Semantic Tranche 1 — Selector Overlap and Negative Fixtures

## Goal
Deepen Policy Fabric semantic validation beyond exact selector identity and happy-path fixture readiness.

## Scope
1. Detect likely selector overlap for:
   - JSONPath prefix overlap
   - wildcard vs concrete index overlap
   - repeated normalized selector prefixes
   - obvious regex shadow/equivalence cases
2. Add negative fixture semantics:
   - expectedFailureCode
   - expectedFailingRule
   - expectedFailingSelector
   - expectedNoop
   - failureAttestation assertions
3. Emit new validation findings and stable reason codes.

## Non-goals
- full formal selector theorem proving
- full regex subsumption analysis
- runtime execution receipts

## Acceptance
- doctor remains green
- enhanced example policy includes at least one negative fixture
- validation report example shows at least one expected failure case
