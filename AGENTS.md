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
6. Run `python scripts/agentplane_probe.py` when the change affects the AgentPlane bridge or repo workflow surfaces.
7. Run `python scripts/doctor.py`.
8. Run `python scripts/github_publish_prep.py` when the change affects `.github/`, publication readiness, or pair-programming push flow.
9. Review `docs/reports/doctor_latest.md`, `docs/reports/validation_report_latest.json`, `docs/reports/agentplane_probe_latest.md`, and `docs/reports/github_publish_prep_latest.md` as needed.
10. Run `python scripts/build_dist_bundle.py` if the change affects release artifacts.

## High-value surfaces

- `contracts/` — source-of-truth machine-readable contracts.
- `examples/` — aligned examples that should validate against the contracts.
- `docs/specs/` — design rules and repo governance details.
- `.github/` — GitHub collaboration and automation surfaces for the first publish and ongoing pair-programming flow.
- `docs/assessments/` — what is strong, what is weak, what to do next.
- `scripts/` — authoritative automation for reconcile, AgentPlane bridge probing, doctor, semantic checks, and bundle build.
- `.policy-fabric/agentplane_bridge.json` — machine-readable contract for the official AgentPlane bridge.
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

## GitHub-first collaboration

Use `CONTRIBUTING.md`, `SECURITY.md`, `.policy-fabric/github_publish.json`, and `docs/specs/github_publish_and_pairing.md` as the authoritative surfaces for the first GitHub publish and pair-programming push.


## Branch Discipline

Before risky work, run `python scripts/branch_audit.py`, `.policy-fabric/branch_policy.json`, create a `baseline/` tag, and branch off `main` using a `work/` prefix. Do not run the first real official AgentPlane init directly on `main`.
