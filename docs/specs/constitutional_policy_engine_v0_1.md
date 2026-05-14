# Constitutional Policy Engine v0.1

Status: contract and reference-library drop. This is not yet the deployed `/verdict` service.

This tranche introduces the Policy Fabric surface for the SocioProphet constitutional operator `C`: machine-readable contracts, a numeric axiom reference library, examples, and validation tooling.

Canonical implementation home: `SocioProphet/policy-fabric`.

Downstream consumers are expected to integrate after this contract is reviewed:

- `SocioProphet/agentplane` consumes verdicts before governed execution actions.
- `SocioProphet/superconscious` requests policy admission before governed cognition-loop actions.
- `SocioProphet/prophet-platform` may later wrap the library as a deployable service.
- `SocioProphet/sociosphere` registers topology and canonical-source ownership.
- `SocioProphet/ProCybernetica` carries doctrine and public cybernetic-control framing.

## Landed artifacts

```text
contracts/constitutional/
  evidence_ledger.v0_1.schema.json
  claims_ledger.v0_1.schema.json
  agent_identity.v0_1.schema.json
  experimental_session.v0_1.schema.json
  policy_engine.openapi.v0_1.yaml

tools/
  constitutional_policy_engine.py
  validate_constitutional_policy_engine.py

examples/constitutional/
  evidence_ledger.example.json
  claims_ledger.example.json
  agent_identity.example.json
  experimental_session.example.json
```

## Axiom surface

The v0.1 review stub exposes `POST /axioms/{axiom_id}` for the landed numeric checks, with `axiom_id` restricted to `A1`, `A3`, `A4`, `A5`, or `A7`. It also records `/verdict` as contract-only until the LTL-to-SMT-LIB translator and solver backend land, and preserves `/merge/barycenter` as part of the uploaded source-drop surface but not as a materialized review-stub endpoint.

A2 is deferred to the solver-backed `/verdict` path. A6 is deferred pending scope definition. See `contracts/constitutional/API_SURFACE.md` for the authoritative v0.1 status table.

The Python reference engine implements A1, A3, A4, A5, A7, and a lightweight barycenter helper. It is intentionally library-only. It does not choose an HTTP framework, queue model, registry host, or audit-log substrate.

## Explicit non-claims

This tranche does not implement LTL-to-SMT translation. `/verdict` is a contract shape until a Z3-backed translator lands.

This tranche does not define A6 semantics or expose an A6 evaluation surface.

This tranche does not implement Hopf-shell observables, ESO ontology export, mixed-effects power-table recomputation, or the SRC-025 session runner.

## Validation

```bash
python -m pip install jsonschema pyyaml numpy
python tools/validate_constitutional_policy_engine.py
```

Expected reference behavior: A1 pass, A3 pass, A4 fail by design on the synthetic unstable Jacobian, A5 pass, A7 pass.

## Next tranche

The next blocking tranche is the LTL-to-SMT-LIB translator with a Z3 backend.
