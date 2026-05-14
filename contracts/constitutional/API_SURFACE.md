# Constitutional Policy Engine API Surface

This file records the API surface from the v0.1 integration drop without selecting an HTTP framework.

Required endpoints:

- `POST /verdict`
- `POST /axioms/A1`
- `POST /axioms/A3`
- `POST /axioms/A4`
- `POST /axioms/A5`
- `POST /axioms/A7`
- `POST /merge/barycenter`

`/verdict` remains contract-only until the LTL-to-SMT-LIB translator and Z3 backend land.

The uploaded source drop contains the complete OpenAPI 3.1 contract. This repository tranche preserves the endpoint surface and keeps executable service binding out of scope.
