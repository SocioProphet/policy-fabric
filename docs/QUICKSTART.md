# Quickstart

## What this repo is

Policy Fabric is a governed control repository for authored policy, compiled plans, release packs, validation evidence, and repo-native workflow governance.

## First five minutes

1. Clone the repository.
2. Run the standard validation loop:
   python3 scripts/reconcile.py
   python3 scripts/doctor.py
3. Read:
   - README.md
   - docs/ARCHITECTURE_OVERVIEW.md
   - docs/TRUST_AND_SECURITY_MODEL.md
   - SECURITY.md
4. Create a work branch for any non-trivial change.

## Standard commands

Core loop:
- python3 scripts/reconcile.py
- python3 scripts/doctor.py

When workflow or governance surfaces changed, also run:
- python3 scripts/agentplane_probe.py
- python3 scripts/branch_audit.py
- python3 scripts/github_publish_prep.py

## Where to look first

- contracts/ — schemas and machine-readable contracts
- examples/ — example authored policy, plans, release packs, and reports
- scripts/ — validation and repo-control scripts
- .policy-fabric/ — control and governance surfaces
- .agentplane/ — official AgentPlane workflow surfaces

## Contribution rule

Do not treat a branch as merge-ready until doctor passes.
