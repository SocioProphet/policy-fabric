# AGENTS.md

This is the root gateway for coding-agent work in the **Policy Fabric Control Repository**.

## Fast orientation

- **Product:** Policy Fabric.
- **Repository role:** Policy Fabric Control Repository.
- **Directory path today:** `policy-fabric-working-repo`.
- **Workflow status:** cumulative Git-backed working tree with repo-native governance already in place.
- **AgentPlane status:** AgentPlane-ready, not yet fully AgentPlane-initialized.

## Fast path for agents

1. Read `README.md` for repository identity and current focus.
2. Read `.policy-fabric/WORKFLOW.md` for the authoritative repo workflow.
3. Read `.policy-fabric/ownership.json` before changing files.
4. Make the change.
5. Run `python scripts/reconcile.py`.
6. Run `python scripts/doctor.py`.
7. Review `docs/reports/doctor_latest.md` and `docs/reports/validation_report_latest.json`.
8. Run `python scripts/build_dist_bundle.py` if the change affects release artifacts.

## High-value surfaces

- `contracts/` — source-of-truth machine-readable contracts.
- `examples/` — aligned examples that should validate against the contracts.
- `docs/specs/` — design rules and repo governance details.
- `docs/assessments/` — what is strong, what is weak, what to do next.
- `scripts/` — authoritative automation for reconcile, doctor, semantic checks, and bundle build.
- `archive/prior-reference/` — historical reference only; do not treat as active product identity.

## Guardrails

- Do not rename the product away from **Policy Fabric** without explicit intent.
- Do not revive historical project branding in active artifacts.
- Do not hand-edit generated report surfaces unless the workflow explicitly requires it.
- Do not treat `archive/prior-reference/` as current truth.
- Do not add secrets inline; use reference-style declarations only.

## AgentPlane bridge

This repo is prepared to work with AgentPlane, but we have intentionally not hand-authored a fake `.agentplane/` managed tree.
When we adopt the official AgentPlane CLI, initialize it on a dedicated branch and let the CLI generate its managed files.
Until then, `.policy-fabric/` remains the authoritative workflow surface.

The explicit adoption plan lives in `docs/specs/agentplane_integration_plan.md`.
