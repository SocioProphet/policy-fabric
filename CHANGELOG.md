# Changelog

## 2026-03-31T18:27:26Z

- created the first cumulative working repository for Policy Fabric
- copied active contracts, examples, blueprint, comparison, and rebrand notes into a repo layout
- archived prior-reference Magen artifacts under `archive/prior-reference/magen/`
- added repo-local workflow surfaces under `.policy-fabric/`
- added `scripts/doctor.py` for repo health checks and example/schema validation
- added `scripts/build_dist_bundle.py` for reproducible bundle generation
- added assessment and research notes, including AgentPlane alignment analysis
- exported a fresh distributable contract bundle and a Git-backed repository snapshot

## 2026-04-01T13:35:00Z

- corrected AgentPlane research source to the official public site/docs rather than a GitHub repo interpretation
- added an official-site lessons note under `docs/research/2026-04-01_agentplane_official_site_lessons.md`
- updated repository focus/backlog to reflect managed ownership, reconcile/upgrade, and profile-based workflow lessons
- extended `scripts/doctor.py` to validate release-pack, validation-report, and replay-report examples in addition to core contracts
- refreshed doctor reports, repository manifest, distributable bundle, and Git-backed snapshot

## 2026-04-01T16:10:00Z

- added a formal ownership contract under `.policy-fabric/ownership.json`
- added workflow profiles under `.policy-fabric/profiles.json` and selected the `normal` profile in repo config
- added reconcile guidance and a real `scripts/reconcile.py` repair step
- strengthened `scripts/doctor.py` with ownership/profile drift checks, release-pack digest checks, replay-evidence checks, and bundle-exclusion checks
- began emitting machine-readable validation evidence at `docs/reports/validation_report_latest.json`
- updated bundle generation to exclude sanctioned local-override notes from distributable bundles
- refreshed repository governance docs, backlog, assessments, and turn notes

## 2026-04-01T18:05:00Z

- added `contracts/policy_fabric_capability_catalog_v1.schema.json` and a governed catalog example for provider/capability authorization
- added `scripts/policy_semantic_validator.py` and wired it into `scripts/doctor.py`
- extended release packs to optionally pin a capability-catalog artifact and digest
- implemented authored-policy semantic checks for duplicate ids, selectorRef resolution, provider/capability authorization, rollout scope, re-identification governance, exact-target conflicts, attestation readiness, and fixture readiness
- updated semantic-validator, release-pack, and capability-catalog specs
- refreshed assessment, backlog, reports, bundle, and repo snapshot exports
