
# Turn Note — Managed Ownership, Workflow Profiles, and Drift Checks

## Objective

Convert the repo from a documented working copy into a self-policing workspace with explicit ownership, profiles, repair, and semantic release-pack checks.

## What changed

- added `.policy-fabric/ownership.json` as the canonical ownership contract
- added `.policy-fabric/profiles.json` with `solo`, `normal`, and `release-gated`
- upgraded `.policy-fabric/config.json` to select a profile and reference the ownership/profile contracts
- added `.policy-fabric/RECONCILE.md` and `scripts/reconcile.py`
- strengthened `scripts/doctor.py` with ownership drift, profile drift, release-pack digest, replay-evidence, and bundle-exclusion checks
- started emitting `docs/reports/validation_report_latest.json`
- updated bundle building so local override notes do not leak into distributable bundles

## Why it matters

This is the first pass where repository governance is not just described. It is enforced. The repo now has an internal constitution and repair loop, which is the strongest transferable lesson from the official AgentPlane docs.
