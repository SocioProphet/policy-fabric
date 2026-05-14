# Constitutional Policy Engine API Surface

This file records the internal v0.1 review surface for the constitutional policy engine without selecting an HTTP framework.

This is an author-checkpoint / internal contract-freeze candidate. It is not an external API commitment and does not claim deployed service behavior.

## Axiom surface status

The constitutional axiom set is A1 through A7. Not all axioms have a landed per-axiom evaluation endpoint in v0.1. The table below records the current status of each axiom's surface; deferred axioms are tracked in the issues listed.

| Axiom | Name | v0.1 status | Endpoint | Delegated to / tracked in |
|---|---|---|---|---|
| A1 | Coherence | landed | `POST /axioms/{axiom_id}` with `axiom_id=A1` | — |
| A2 | Solver-backed admissibility | deferred | `/verdict` contract-only | LTL-to-SMT-LIB + Z3 backend; issue #82 |
| A3 | Identity continuity | landed | `POST /axioms/{axiom_id}` with `axiom_id=A3` | — |
| A4 | Spawn stability | landed | `POST /axioms/{axiom_id}` with `axiom_id=A4` | — |
| A5 | Rate-distortion budget | landed | `POST /axioms/{axiom_id}` with `axiom_id=A5` | — |
| A6 | Scope under review | deferred | none in v0.1 numeric checker | define A6 check surface; issue #83 |
| A7 | Lyapunov non-increase | landed | `POST /axioms/{axiom_id}` with `axiom_id=A7` | A7 p-value upgrade; issue #84 |

A2 is referenced in the v0.1 ledger schemas (`claims_ledger.v0_1.schema.yaml` permits `uaibb_axiom_ref: A2` for claim-tagging purposes) but has no direct numeric per-axiom evaluation endpoint in this tranche. A2 evaluation is expected to flow through `/verdict` once solver-backed semantics land.

A6 appears as an allowed enum value in the claims ledger schema but has no evaluation surface in v0.1 and no committed delegation target. A6's scope is under review; see issue #83.

Consumers of this contract should:

- Code against the five landed per-axiom checks (`A1`, `A3`, `A4`, `A5`, `A7`) through `POST /axioms/{axiom_id}`.
- Treat A2 and A6 claim-tag references as allowed-but-uncheckable in v0.1.
- Expect A2 evaluation to appear under `/verdict` rather than as a numeric `/axioms/A2` check.
- Not assume A6 will appear as `/axioms/A6`; the surface is undecided.

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
