
# Semantic Validator Spec (Draft)

## Goal

Define the non-JSON-Schema validation rules required before a Policy Fabric policy may be approved, compiled, or released.

## Validation phases

### Phase 0: Repository governance and release-pack integrity
- ownership contract must classify every tracked file
- ownership classes must not overlap on actual tracked files
- selected workflow profile must exist and permit the current workflow mode
- release-pack referenced artifact digests must match the bytes on disk
- replay retention must imply replay corpus reference and replay-report expectation
- local override surfaces must stay out of the distributable bundle

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

- `python scripts/reconcile.py`
- `python scripts/doctor.py`
- future: `policy-fabric validate policy.json`
- future: `policy-fabric compile policy.json --strict`

## Relationship to current repo

The current `scripts/doctor.py` now implements Phase 0 plus structural checks. Policy/compiler/runtime semantics remain the next major layer to implement.
