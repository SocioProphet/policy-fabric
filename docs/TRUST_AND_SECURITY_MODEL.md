# Trust and Security Model

Policy Fabric is a governed control repository, not just a schema bucket.

## Trust boundaries

### Authored policy
Authored policy is the intent layer. It must remain reviewable, versioned, and constrained.

### Compiled plan
Compiled plans must faithfully reflect authored policy and are checked against the source policy id/version.

### Release and validation artifacts
Release packs and validation reports bind authored policy to promotion and evidence semantics.

### Secrets
Secrets must never be committed inline. Use reference-style declarations only.

### Generated artifacts
Generated reports and manifests are versioned here as part of the control surface, but they should be regenerated through scripts rather than hand-edited.

## Security posture

Policy Fabric currently models or enforces:
- provider/capability authorization checks
- rollout scope checks
- re-identification governance checks
- release-pack digest integrity
- promotion-gate expectations
- repo ownership classification
- branch policy and CI health checks

## Vulnerability reporting

Do not use public issues for vulnerability disclosure.

Follow SECURITY.md.

## Operational rule

A branch should not be treated as merge-ready until:
- python3 scripts/reconcile.py has been run
- python3 scripts/doctor.py passes
- branch / AgentPlane / GitHub checks have been rerun where applicable

## Why this matters

Without explicit trust boundaries, policy repos become ambiguous and unsafe. Policy Fabric is intended to make policy, execution, release, and evidence reviewable as one governed system.
