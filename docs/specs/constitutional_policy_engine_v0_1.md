# Constitutional Policy Engine v0.1

Status: internal contract and reference-library checkpoint. This is not a deployed `/verdict` service and not an external API commitment.

This tranche introduces the Policy Fabric review surface for the SocioProphet constitutional operator `C`: YAML-form JSON Schema contracts, a numeric axiom reference library, an OpenAPI review stub, and smoke-validation wiring.

Canonical implementation home: `SocioProphet/policy-fabric`.

Downstream consumers are expected to wait until this PR exits draft before integrating against the endpoint shape.

## Landed artifacts

```text
contracts/constitutional/
  API_SURFACE.md
  CONTRACT_HISTORY.md
  evidence_ledger.v0_1.schema.yaml
  claims_ledger.v0_1.schema.yaml
  agent_identity.v0_1.schema.yaml
  experimental_session_core.v0_1.schema.yaml
  experimental_session.v0_1.schema.yaml        # deprecated alias only

docs/openapi/
  constitutional-policy-engine-v0_1.stub.yaml
  README.md

tools/
  constitutional_policy_engine.py
  validate_constitutional_policy_engine.py
```

## Axiom surface

The v0.1 review stub exposes `POST /axioms/{axiom_id}` for the landed numeric checks, with `axiom_id` restricted to `A1`, `A3`, `A4`, `A5`, or `A7`.

A2 is deferred to the solver-backed `/verdict` path and tracked by issue #82. A6 is deferred pending scope definition and tracked by issue #83. See `contracts/constitutional/API_SURFACE.md` for the authoritative v0.1 status table.

The Python reference engine implements the landed numeric checks only:

- `check_A1_coherence`
- `check_A3_identity`
- `check_A4_spawn`
- `check_A5_rate_distortion`
- `check_A7_lyapunov`

It is intentionally library-only. It does not choose an HTTP framework, queue model, registry host, audit-log substrate, or solver backend.

## A7 provisionality

A7 currently returns `nonincrease_indicator`, not a statistical p-value. The indicator is a provisional threshold signal for non-increase. A later tranche should replace or supplement it with a real OLS t-statistic or bootstrap significance calculation before A7 is treated as a statistical inference surface.

## Explicit non-claims

This tranche does not implement LTL-to-SMT translation. `/verdict` remains contract-only until a solver-backed implementation lands.

This tranche does not define A6 semantics or expose an A6 evaluation surface.

This tranche does not materialize the exact full OpenAPI 3.1 source artifact; issue #81 tracks that work.

This tranche does not implement Hopf-shell observables, ESO ontology export, mixed-effects power-table recomputation, or the SRC-025 session runner.

## Validation

```bash
python -m pip install numpy
python tools/validate_constitutional_policy_engine.py
```

Expected reference behavior: A1 pass, A3 pass, A4 fail by design on the synthetic unstable Jacobian, A5 pass, A7 pass, and A7 emits `nonincrease_indicator` rather than `p_value`.

## Next tranche

The next blocking tranche is the LTL-to-SMT-LIB translator with a solver backend for `/verdict`.
