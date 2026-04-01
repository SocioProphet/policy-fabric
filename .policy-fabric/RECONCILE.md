
# Policy Fabric Reconcile and Upgrade Notes

## Purpose

`python scripts/reconcile.py` is the repo repair step. It normalizes generated directories, refreshes `REPO_MANIFEST.json`, and emits reconcile evidence before `doctor` and bundle generation.

## When to run it

- before `python scripts/doctor.py`
- after adding or removing tracked files
- after changing ownership, workflow, or profile contracts
- after recovering from partial edits or generated-file drift

## What it repairs

- ensures generated report directories exist
- ensures the sanctioned local override directory exists
- rebuilds `REPO_MANIFEST.json` from the working tree
- writes reconcile evidence under `.policy-fabric/reports/` and `docs/reports/`

## Recovery stance

This repository intentionally treats repair as normal workflow rather than emergency cleanup. Managed surfaces may drift; reconcile is the shortest recovery path.
