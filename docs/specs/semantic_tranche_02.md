# Semantic Tranche 2 — Classified Overlap and No-op Fixture Semantics

## Goal
Deepen Policy Fabric semantic validation beyond a single generic selector-overlap finding and beyond failure-only negative fixtures.

## Scope
1. Split selector-overlap findings into explicit classes:
   - normalized path equivalence
   - path prefix overlap
   - wildcard shadow
   - regex normalized equivalence
   - regex shadow heuristic
2. Strengthen negative-fixture semantics:
   - explicit no-op fixture support using `expectedNoop`
   - stronger coherence checks across `expectFailure`, `expectedNoop`, and failure-specific expectations
3. Keep the release-pack and compiled-plan examples aligned to the authored policy version.

## Non-goals
- formal selector theorem proving
- deep regex subsumption analysis
- runtime execution receipts

## Acceptance
- doctor remains green
- enhanced example policy includes both failure and no-op semantic fixtures
- validation report example documents both overlap classification and richer negative-fixture semantics
