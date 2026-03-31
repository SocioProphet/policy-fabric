# Error Taxonomy (Draft)

## Purpose

Define stable machine-readable reason codes so validation, compile, explain, and runtime failures can be handled deterministically.

## Validation codes

- `PFV001` duplicate selector id
- `PFV002` duplicate rule id
- `PFV003` unresolved selectorRef
- `PFV004` unauthorized provider for transform type
- `PFV005` reidentify transform requires stronger approval state
- `PFV006` rollout scope invalid or empty
- `PFV007` conflicting transforms on same target
- `PFV008` illegal transform chain
- `PFV009` attestation template missing required fields
- `PFV010` required test fixtures missing for approved policy

## Compile codes

- `PFC001` policy cannot compile because semantic validation failed
- `PFC002` plan hash generation failed
- `PFC003` provider dependency resolution failed
- `PFC004` plan contains unreachable nodes

## Runtime codes

- `PFR001` no matching approved policy version
- `PFR002` content type unsupported by adapter
- `PFR003` provider denied requested capability
- `PFR004` selector cardinality violation
- `PFR005` transform execution failed
- `PFR006` attestation emission failed
- `PFR007` reidentify operation blocked by trust boundary

## Explain and doctor guidance

`doctor` should surface validation and repository-state findings using the same stable codes. This borrows the spirit of reason-code ergonomics seen in repo-governance tools while keeping the taxonomy product-specific.
