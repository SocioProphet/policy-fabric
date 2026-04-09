# Contributing to Policy Fabric

## Repository model

This repository is both a product contract repo and a control repo.

That means changes are expected to touch not just source files, but also generated reports, manifests, and workflow metadata when appropriate.

## Branching

- `main` is the stable baseline.
- use `work/*` branches for tranche-scoped or risky changes.
- avoid piling unrelated concerns into one PR.

## Before pushing

Run the standard loop:

    python3 scripts/reconcile.py
    python3 scripts/doctor.py

If the change affects workflow, branch, AgentPlane, or GitHub surfaces, also run:

    python3 scripts/agentplane_probe.py
    python3 scripts/branch_audit.py
    python3 scripts/github_publish_prep.py

## Pull requests

A strong PR should include:

- a tight scope
- a clear problem statement
- the repo surfaces changed
- whether generated reports and manifests changed as a consequence
- any new reason codes, schemas, or example semantics introduced

## Generated artifacts

Generated artifacts are versioned here as part of the control surface.

Do not hand-edit generated reports unless the generating logic itself requires it; prefer regenerating them through the repo scripts.

## Semantic changes

If a change alters policy semantics, update the following together when relevant:

- schema
- example policy
- compiled plan example
- release pack example
- validation report example
- validator spec
- semantic validator implementation

## Security

Do not report vulnerabilities through public issues. Use the process in `SECURITY.md`.
