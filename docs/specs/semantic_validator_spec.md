
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
- capability-catalog provider ids must be unique
- capability-catalog capability ids must be unique
- every capability provider reference must resolve
- every provider/capability reference in policy rules must resolve to an allowed capability catalog entry

### Phase 3: Safety and governance
- `reidentify` transforms require elevated approval state and dedicated trust boundary
- rollout tenants, environments, and regions must be non-empty where required
- approved policy rollout tenants and regions must stay within provider/capability allow-lists
- reversible transforms must not appear in irreversible-only deployment lanes
- provider classes must be authorized for the requested transform types

### Phase 4: Execution legality
- overlapping selectors with incompatible transforms are errors
- conflicting priorities with the same target require explicit precedence handling
- impossible transform chains are errors
- cardinality mismatches may be warnings or errors depending on policy mode

### Phase 5: Test and attestation readiness
- approved policies should carry at least one positive fixture
- risky transforms should also carry at least one attestation-aware fixture
- risky transforms should also carry at least one negative or failure-mode fixture (still pending implementation)
- compiled audit nodes must expose required identifiers for audit and explain mode

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

The current `scripts/doctor.py` plus `scripts/policy_semantic_validator.py` now implement Phase 0, structural checks, capability-catalog reference integrity, rollout/provider authorization checks, exact-target conflict detection, and attestation/test readiness checks. Deeper selector-overlap analysis, richer negative-fixture enforcement, and runtime semantics remain the next major layer to implement.

## Semantic Tranche 1

### Selector overlap heuristics
The validator SHOULD emit non-fatal overlap findings when selectors are not textually identical but likely overlap semantically:
- JSONPath/XPath/pointer prefix overlap
- wildcard-vs-concrete index overlap
- normalized path equivalence after array index normalization
- obvious regex equivalence or shadow heuristics

### Negative fixtures
Fixtures MAY declare:
- `expectFailure`
- `expectedFailureCode`
- `expectedFailingRule`
- `expectedFailingSelector`
- `expectedNoop`
- `failureAttestation`

Approved policies SHOULD include at least one negative fixture so failure semantics are reviewable alongside happy-path assertions.

## Semantic Tranche 2

### Classified selector overlap
Selector overlap findings SHOULD be emitted in distinct classes rather than one generic overlap bucket:
- normalized path equivalence
- path prefix overlap
- wildcard shadow
- regex normalized equivalence
- regex shadow heuristic

### No-op and failure fixture semantics
Negative fixtures SHOULD distinguish between expected failure and expected no-op behavior.

Fixtures may use:
- `expectFailure`
- `expectedFailureCode`
- `expectedFailingRule`
- `expectedFailingSelector`
- `expectedNoop`
- `failureAttestation`

Validator semantics should ensure these declarations remain internally coherent.
