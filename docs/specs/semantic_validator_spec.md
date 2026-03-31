# Semantic Validator Spec (Draft)

## Goal

Define the non-JSON-Schema validation rules required before a Policy Fabric policy may be approved, compiled, or released.

## Validation phases

### Phase 1: Structural parse
- JSON Schema validation for authored policy
- OpenAPI parse validation
- compiled plan IR schema validation

### Phase 2: Reference integrity
- selector ids must be unique
- rule ids must be unique
- every `selectorRef` must resolve
- every provider/capability reference must resolve to an allowed capability catalog entry

### Phase 3: Safety and governance
- `reidentify` transforms require elevated approval state and dedicated trust boundary
- rollout tenants, environments, and regions must be non-empty where required
- reversible transforms must not appear in irreversible-only deployment lanes
- provider classes must be authorized for the requested transform types

### Phase 4: Execution legality
- overlapping selectors with incompatible transforms are errors
- conflicting priorities with the same target require explicit precedence handling
- impossible transform chains are errors
- cardinality mismatches may be warnings or errors depending on policy mode

### Phase 5: Test and attestation readiness
- approved policies should carry at least one positive fixture
- risky transforms should also carry at least one negative or failure-mode fixture
- attestation templates must expose required identifiers for audit and explain mode

## Output envelope

Each validation finding should include:
- `code`
- `severity` (`error`, `warning`, `info`)
- `path`
- `message`
- `remediation`
- optional `relatedPaths`

## Recommended command surface

- `policy-fabric validate policy.json`
- `policy-fabric doctor`
- `policy-fabric compile policy.json --strict`

## Relationship to current repo

The current `scripts/doctor.py` only performs structural checks. This spec defines the next layer that should be implemented.
