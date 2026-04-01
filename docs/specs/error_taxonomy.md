
# Error Taxonomy (Draft)

## Purpose

Define stable machine-readable reason codes so repository validation, compile, explain, and runtime failures can be handled deterministically.

## Repository / doctor codes

- `PFD001_REQUIRED_FILE_PRESENT` required file exists
- `PFD002_REQUIRED_FILE_MISSING` required file missing
- `PFD010_SCHEMA_OK` example validates against schema
- `PFD011_SCHEMA_INVALID` example does not validate against schema
- `PFD020_OPENAPI_OK` openapi parsed and exposes required core surface
- `PFD021_OPENAPI_INVALID` openapi parse or required-surface check failed
- `PFD030_OWNERSHIP_SYNC_OK` config and ownership contract agree
- `PFD031_OWNERSHIP_DRIFT` config and ownership contract diverged
- `PFD032_OWNERSHIP_OVERLAP_FREE` no actual file matched multiple ownership categories
- `PFD033_OWNERSHIP_OVERLAP` actual file matched multiple ownership categories
- `PFD034_OWNERSHIP_CLASSIFICATION_OK` every tracked file is classified
- `PFD035_OWNERSHIP_UNCLASSIFIED` one or more tracked files are unclassified
- `PFD036_OWNERSHIP_PARSE_ERROR` repo governance contract could not be parsed
- `PFD040_PROFILE_OK` selected profile exists and permits the current mode
- `PFD041_PROFILE_MODE_MISMATCH` selected profile does not permit current workflow mode
- `PFD042_PROFILE_UNKNOWN` selected workflow profile missing from contract
- `PFD050_DOC_SYNC_OK` workflow/reconcile docs mention the governed command and contract surfaces
- `PFD051_DOC_SYNC_DRIFT` workflow/reconcile docs drift from governed command and contract surfaces
- `PFD060_RELEASE_PACK_DIGEST_OK` referenced artifact digests match the release pack
- `PFD061_RELEASE_PACK_DIGEST_MISMATCH` referenced artifact digest mismatch
- `PFD062_PROMOTION_GATE_OK` lane and human-gate semantics are acceptable
- `PFD063_PROMOTION_GATE_REQUIRED` prod promotion missing required human gate
- `PFD064_REPLAY_EVIDENCE_OK` replay evidence requirements satisfied
- `PFD065_REPLAY_EVIDENCE_INCOMPLETE` replay evidence requirements not satisfied
- `PFD066_SECRET_REF_OK` release pack uses reference-style secret declarations
- `PFD067_SECRET_REF_INVALID` release pack embeds or misstates secret reference semantics
- `PFD068_RELEASE_PACK_GIT_DRIFT` release pack git metadata drifts from current repo state
- `PFD069_RELEASE_PACK_GIT_OK` release pack git metadata is working-style or aligned
- `PFD070_RELEASE_PACK_PARSE_ERROR` release pack could not be parsed for semantic checks
- `PFD080_BUNDLE_EXCLUSION_OK` local override files excluded from distributable bundle
- `PFD081_BUNDLE_EXCLUSION_FAILED` local override files leaked into distributable bundle
- `PFD082_BUNDLE_MANIFEST_PARSE_ERROR` bundle manifest could not be parsed
- `PFD083_BUNDLE_MANIFEST_MISSING` bundle manifest missing so exclusion check deferred

## Capability catalog validation codes

- `PFCAT000_CATALOG_SEMANTICS_OK` capability catalog semantic cluster passed
- `PFCAT001` duplicate provider id
- `PFCAT002` duplicate capability id
- `PFCAT003` capability references unknown provider
- `PFCAT004` capability transform type not allowed by provider

## Policy validation codes

- `PFV000_POLICY_SEMANTICS_OK` policy semantic cluster passed

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
- `PFV099` policy semantic validator crashed

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
