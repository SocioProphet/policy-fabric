# OrgGov Policy Decision v0.1

## Purpose

OrgGov Policy Decision v0.1 makes Policy Fabric the executable decision surface for Organization Governance Control Plane v0.

The decision answers:

```text
Can this actor, under this role binding, perform this action, against these assets, inside this workroom and work order?
```

## Decision states

The v0 decision vocabulary is:

- `allow`
- `deny`
- `escalate`
- `allow_with_constraints`
- `revoke`
- `blocked_expected`

`blocked_expected` is important: not every blocked action is a system error. Some blocks prove the policy layer is working.

## Contract files

- `contracts/schemas/orggov-policy-decision.schema.json`
- `examples/orggov-policy-decision.allow-with-constraints.example.json`
- `scripts/validate_orggov_policy_decision.py`

## Cross-repo bindings

- Parent: `SocioProphet/prophet-platform#406`
- Policy workstream: `SocioProphet/policy-fabric#57`
- Actor authority: `SocioProphet/agent-registry#18`
- Workspace control room: `SocioProphet/prophet-workspace#15`
- Execution evidence: `SocioProphet/agentplane#104`

## Invariants

- Every decision must reference a workroom and work order.
- Every decision must reference an actor, role binding, action, and at least one asset.
- Every decision must include evidence references.
- Decisions requiring review must declare approver references.
- Replay posture must be explicit.
- Raw private prompts, secrets, or credentials do not belong in decision fixtures.
