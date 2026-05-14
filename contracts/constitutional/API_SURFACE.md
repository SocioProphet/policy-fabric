# Constitutional Policy Engine API Surface

This file records the internal v0.1 review surface for the constitutional policy engine without selecting an HTTP framework.

This is an author-checkpoint / internal contract-freeze candidate. It is not an external API commitment and does not claim deployed service behavior.

## Axiom status

| Axiom | Status | Surface | Delegated to / follow-up |
|---|---|---|---|
| A1 | landed | `POST /axioms/{axiom_id}` with `axiom_id=A1` | — |
| A2 | deferred | `/verdict` contract-only | solver-backed admissibility path, issue #82 |
| A3 | landed | `POST /axioms/{axiom_id}` with `axiom_id=A3` | — |
| A4 | landed | `POST /axioms/{axiom_id}` with `axiom_id=A4` | — |
| A5 | landed | `POST /axioms/{axiom_id}` with `axiom_id=A5` | — |
| A6 | deferred | none in v0.1 numeric checker | define A6 check surface, issue #83 |
| A7 | landed | `POST /axioms/{axiom_id}` with `axiom_id=A7` | — |

## Required endpoints for this tranche

- `POST /axioms/{axiom_id}` where `axiom_id` is one of `A1`, `A3`, `A4`, `A5`, or `A7`.
- `POST /verdict` remains contract-only until the LTL-to-SMT-LIB translator and solver backend land.
- `POST /merge/barycenter` remains part of the uploaded source-drop surface but is not materialized in the review stub.

## Non-claims

- This tranche does not claim a deployed HTTP service.
- This tranche does not implement A2 admissibility.
- This tranche does not define A6 semantics.
- This tranche does not select HTTP framework, registry host, dispatch mode, or audit-log substrate.
- This tranche does not replace the full OpenAPI 3.1 source artifact tracked by issue #81.

The uploaded source drop contains the complete OpenAPI 3.1 contract. This repository tranche preserves the reviewable internal surface and keeps executable service binding out of scope.
