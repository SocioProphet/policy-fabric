# Validation Report

Overall status: PASS

Check count: `54`; fails: `0`; warnings: `0`

- `PFD001_REQUIRED_FILE_PRESENT` — pass — required file present
- `PFD001_REQUIRED_FILE_PRESENT` — pass — required file present
- `PFD001_REQUIRED_FILE_PRESENT` — pass — required file present
- `PFD001_REQUIRED_FILE_PRESENT` — pass — required file present
- `PFD001_REQUIRED_FILE_PRESENT` — pass — required file present
- `PFD001_REQUIRED_FILE_PRESENT` — pass — required file present
- `PFD001_REQUIRED_FILE_PRESENT` — pass — required file present
- `PFD001_REQUIRED_FILE_PRESENT` — pass — required file present
- `PFD001_REQUIRED_FILE_PRESENT` — pass — required file present
- `PFD001_REQUIRED_FILE_PRESENT` — pass — required file present
- `PFD001_REQUIRED_FILE_PRESENT` — pass — required file present
- `PFD001_REQUIRED_FILE_PRESENT` — pass — required file present
- `PFD001_REQUIRED_FILE_PRESENT` — pass — required file present
- `PFD001_REQUIRED_FILE_PRESENT` — pass — required file present
- `PFD001_REQUIRED_FILE_PRESENT` — pass — required file present
- `PFD001_REQUIRED_FILE_PRESENT` — pass — required file present
- `PFD001_REQUIRED_FILE_PRESENT` — pass — required file present
- `PFD001_REQUIRED_FILE_PRESENT` — pass — required file present
- `PFD001_REQUIRED_FILE_PRESENT` — pass — required file present
- `PFD010_SCHEMA_OK` — pass — policy example validates against policy schema
- `PFD010_SCHEMA_OK` — pass — compiled plan validates against plan schema
- `PFD010_SCHEMA_OK` — pass — release pack example validates against release pack schema
- `PFD010_SCHEMA_OK` — pass — capability catalog example validates against capability catalog schema
- `PFD010_SCHEMA_OK` — pass — validation report example validates against validation report schema
- `PFD010_SCHEMA_OK` — pass — replay report example validates against replay report schema
- `PFD020_OPENAPI_OK` — pass — openapi parses and contains expected core surfaces
- `PFD030_OWNERSHIP_SYNC_OK` — pass — config managed paths match ownership contract
- `PFD030_OWNERSHIP_SYNC_OK` — pass — config generated paths match ownership contract
- `PFD030_OWNERSHIP_SYNC_OK` — pass — config local override paths match ownership contract
- `PFD040_PROFILE_OK` — pass — selected workflow profile `normal` exists
- `PFD040_PROFILE_OK` — pass — workflow mode allowed by selected profile
- `PFD050_DOC_SYNC_OK` — pass — workflow documentation references governed commands and contracts
- `PFD050_DOC_SYNC_OK` — pass — reconcile documentation references repair surfaces and commands
- `PFD032_OWNERSHIP_OVERLAP_FREE` — pass — ownership categories do not overlap on actual files
- `PFD034_OWNERSHIP_CLASSIFICATION_OK` — pass — all tracked files are classified by the ownership contract
- `PFD060_RELEASE_PACK_DIGEST_OK` — pass — release-pack artifact digests match referenced files
- `PFD062_PROMOTION_GATE_OK` — pass — promotion gate semantics satisfy current lane requirements
- `PFD064_REPLAY_EVIDENCE_OK` — pass — replay evidence requirements are satisfied
- `PFD066_SECRET_REF_OK` — pass — release pack uses reference-style secret declarations
- `PFD069_RELEASE_PACK_GIT_OK` — pass — release-pack git source is intentionally working or matches current rev semantics
- `PFCAT000_CATALOG_SEMANTICS_OK` — pass — capability catalog provider ids are unique
- `PFCAT000_CATALOG_SEMANTICS_OK` — pass — capability catalog capability ids are unique
- `PFCAT000_CATALOG_SEMANTICS_OK` — pass — capability catalog provider references and transform types are internally consistent
- `PFV000_POLICY_SEMANTICS_OK` — pass — policy selector ids are unique
- `PFV000_POLICY_SEMANTICS_OK` — pass — policy rule ids are unique
- `PFV000_POLICY_SEMANTICS_OK` — pass — all enabled rule selectorRef values resolve to declared selectors
- `PFV000_POLICY_SEMANTICS_OK` — pass — approved policy rollout scope is present and non-empty where required
- `PFV000_POLICY_SEMANTICS_OK` — pass — enabled rules use authorized provider and capability pairs within rollout scope
- `PFV000_POLICY_SEMANTICS_OK` — pass — re-identification boundary rules are satisfied or no re-identification transforms are present
- `PFV000_POLICY_SEMANTICS_OK` — pass — no enabled rules conflict on the same exact selector identity
- `PFV000_POLICY_SEMANTICS_OK` — pass — no illegal exact-target transform chains were detected
- `PFV000_POLICY_SEMANTICS_OK` — pass — compiled plan attestation fields are aligned to audit and explain requirements
- `PFV000_POLICY_SEMANTICS_OK` — pass — policy fixtures cover approved-state minimums and attestation-aware assertions
- `PFD080_BUNDLE_EXCLUSION_OK` — pass — local override files are excluded from the distributable bundle
