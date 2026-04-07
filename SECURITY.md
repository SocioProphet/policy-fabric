# Security Policy

## Scope

This repository holds design contracts, validation tooling, release-pack examples, and workflow governance for **Policy Fabric**. It must not become a place where secrets, production credentials, or raw sensitive payloads are stored inline.

## What must never be committed

- access tokens
- API keys
- passwords
- private keys
- raw KMS material
- raw vault credentials
- sensitive production payloads
- customer data used without explicit sanitization

Use reference-style declarations only, such as provider refs, capability refs, and secret refs.

## Reporting security concerns

Until the repository is published and a final disclosure channel is configured, do **not** open a public issue for a suspected vulnerability involving secrets, re-identification paths, or sensitive data handling.

Route the finding through a private maintainer channel in the owning GitHub organization first, then record the sanitized outcome back in the repo once handling guidance is ready.

## Publication posture

This repository is currently prepared for a **private** initial GitHub publication. Keep it private until:

- a license decision is finalized
- disclosure routing is finalized
- remote branch protection is enabled
- the first official AgentPlane initialization trial is understood

## Operational hygiene

Before pushing:

1. run `python scripts/branch_audit.py`
2. run `python scripts/github_publish_prep.py`
3. run `python scripts/doctor.py`
4. inspect `docs/reports/*.md` and `docs/reports/*.json`
