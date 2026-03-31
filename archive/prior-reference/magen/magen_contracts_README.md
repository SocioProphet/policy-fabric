# Magen contracts bundle

This bundle turns the architecture blueprint into buildable contracts.

## Files

- `magen_policy_v2.schema.json`  
  Governs authored policy documents. Includes structural constraints plus semantic-validation notes.

- `magen_execution_plan_ir_v1.schema.json`  
  Governs the compiled execution-plan intermediate representation that the runtime should execute.

- `magen_openapi_v2.yaml`  
  Canonical service contract for process, jobs, validate, compile, and explain.

- `magen_policy_v2_enhanced_example.json`  
  Enhanced example policy aligned to the schema and enriched with rollout and test fixtures.

- `magen_process_request_v2_enhanced_example.json`  
  Example synchronous process request aligned to the service contract.

- `magen_compiled_plan_example.json`  
  Example compiled plan showing how the policy becomes a deterministic DAG-style IR.

- `magen_process_response_example.json`  
  Example synchronous response with attestation.

- `magen_validate_response_example.json`  
  Example validation response.

- `magen_explain_response_example.json`  
  Example explain response.

- `magen_comparison_matrix.md`  
  One-for-one comparison between the preserved baseline, our enhancement, and additional improvements.

## Recommended implementation order

1. Validate authored policies against `magen_policy_v2.schema.json`.
2. Add semantic validation on top of the schema constraints.
3. Compile valid policies into `magen_execution_plan_ir_v1.schema.json`.
4. Execute only compiled plans, not raw policy documents.
5. Expose `/v2/process`, `/v2/policies:validate`, `/v2/policies:compile`, and `/v2/explain` first.
6. Add `/v2/jobs` after idempotency, chunking, and attestation are stable.

## Important design choices

- The authored policy is not the runtime artifact; the compiled plan is.
- Policies reference capabilities and providers; they do not embed secrets.
- Re-identification is not operationally symmetric with masking.
- Selectors are reusable objects with cardinality expectations.
- Every execution should return an attestation summary without leaking raw sensitive values.

## Known limitations in this bundle

- JSON Schema cannot enforce all cross-reference and uniqueness rules by itself; semantic validation is still required.
- The OpenAPI spec is self-contained for the service surface, but deployment/authn/authz policy is intentionally left to platform integration.
- The original 2018 source document is not currently live in the file tool, so the comparison matrix is concept-preserving rather than a literal paragraph-by-paragraph redline.
