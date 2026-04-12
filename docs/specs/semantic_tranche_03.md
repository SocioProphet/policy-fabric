# Semantic Tranche 3 — Precedence, Cardinality, and Rollout Subsumption

## Goal
Deepen Policy Fabric semantic validation from overlap classification into deterministic decision semantics.

## Scope
1. Precedence semantics
   - define when overlapping rules may legally coexist
   - distinguish hard conflicts from ordered override chains
   - require explicit precedence explanation for same-target multi-rule evaluation
2. Cardinality semantics
   - strengthen selector cardinality handling beyond `zeroOrOne` and `exactlyOne`
   - model fail-closed vs warn-only behavior for overmatch conditions
   - require fixture coverage for cardinality edge cases
3. Rollout subsumption
   - detect when one rule’s rollout scope strictly contains or shadows another
   - distinguish legal specialization from accidental shadowing
   - emit stable reason-code families for rollout overlap and subsumption
4. Explainability
   - require validator/explain outputs to describe why a winner rule prevailed when multiple candidates overlap

## Non-goals
- full symbolic theorem proving over selector languages
- runtime receipt generation for every shadow/precedence event
- multi-policy federation or cross-pack composition

## Candidate reason-code families
- `PFV020_RULE_PRECEDENCE_REQUIRED`
- `PFV021_RULE_PRECEDENCE_CONFLICT`
- `PFV022_SELECTOR_CARDINALITY_OVERMATCH`
- `PFV023_SELECTOR_CARDINALITY_UNDERSPECIFIED`
- `PFV024_ROLLOUT_SUBSUMPTION_WARNING`
- `PFV025_ROLLOUT_SHADOW_CONFLICT`
- `PFV026_EXPLAIN_DECISION_INCOMPLETE`

## Acceptance
- a tranche-3 spec exists on branch
- the next validator tranche can implement precedence/cardinality/rollout checks without reopening tranche-2 decisions
- reason-code families are stable enough to use in fixtures and validation reports
