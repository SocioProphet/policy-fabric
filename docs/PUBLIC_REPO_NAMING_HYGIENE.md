# Public Repository Naming Hygiene

## Purpose

This repository is public-facing. Branch names, pull request titles, pull request bodies, issue threads, file names, and example artifact names should therefore be treated as public metadata.

## Rule

Do not use sensitive, misleading, unnecessarily loaded, or avoidably specific labels in public-facing GitHub metadata when a neutral term would do.

## Preferred posture

Prefer neutral external naming such as:
- companion
- placement
- verdict report
- policy binding
- tranche
- execution surface
- validation guide

Avoid introducing specialized or sensitive contextual labels into:
- branch names
- pull request titles
- pull request bodies
- issue titles
- long-lived public-facing file names

## If a public-facing name is already wrong

Use this remediation order:
1. stop opening new branches or PRs with the problematic label
2. create a neutralized replacement branch/PR if needed
3. mark the stale public artifact as superseded
4. close or replace the stale artifact when GitHub controls allow it
5. continue only on the neutralized merge path

## Merge guidance

A technically good PR may still be the wrong public merge path if its public-facing naming is not acceptable.

In that case:
- do not treat the stale artifact as the canonical merge candidate
- rebuild the narrow slice on a neutral branch
- use the neutral replacement as the merge path

## Maintainer note

This guidance exists because public GitHub metadata is part of the repository surface, not just incidental tooling state.
