# Agent Reliability Policy Inheritance and Break-Glass Overrides

This document defines the first Policy Fabric contract surface for the SourceOS Agent Reliability Control Plane.

## Purpose

AgentPlane and guardrail-fabric need a governed override object. A loose string reference is not enough for high-risk agent operations. Policy Fabric owns the contract for:

- policy inheritance across enterprise, organization, repository, local, user, and runtime scopes;
- strict conflict resolution;
- fail-closed and audit-required behavior;
- scoped break-glass overrides;
- human approval and expiry semantics.

## Contracts

### `AgentPolicyInheritanceProfile`

Schema: `contracts/policy_fabric_agent_inheritance_profile_v1.schema.json`

Example: `examples/policy_fabric_agent_inheritance_profile_example.json`

The profile defines:

- scope precedence;
- conflict resolution;
- per-scope policy refs;
- forced policies;
- denied action classes;
- audit requirements;
- fail-closed posture;
- provider/tool allowlists;
- break-glass limits.

The default SourceOS Agent Reliability profile uses `stricter-wins` conflict resolution. Lower scopes may tighten controls but may not weaken higher scopes.

### `BreakGlassOverride`

Schema: `contracts/policy_fabric_break_glass_override_v1.schema.json`

Example: `examples/policy_fabric_break_glass_override_example.json`

A break-glass override is a scoped, expiring, human-approved authorization to bypass one bounded policy or stop-gate result.

Required properties:

- human approver;
- scope;
- action class;
- resource;
- reason;
- audit reference;
- expiry;
- usage constraints;
- signature object.

The initial schema permits a placeholder signature for development fixtures, but consumers should treat production overrides as requiring a verifiable signature.

## Validation

Run:

```bash
make agent-reliability-overrides-validate
```

or as part of the normal repo validation:

```bash
make validate
```

The validator checks more than JSON shape. It enforces:

- expected scope precedence;
- `stricter-wins` conflict resolution;
- no lower-scope weakening;
- audit-required layers;
- fail-closed layers;
- required enterprise, repository, and runtime layers;
- break-glass human approver;
- break-glass expiry;
- duration not exceeding profile max;
- allowed action class;
- single-use/max-use consistency;
- non-empty reason and audit ref;
- signature object presence.

## Consumer mapping

- guardrail-fabric should use the inheritance profile to resolve policy pack scope and reject weakening overrides.
- AgentPlane should reference `BreakGlassOverride` artifacts from stop-gate and invocation artifacts instead of plain override strings.
- SocioSphere should render these overrides in the human approval queue.
- MemoryMesh should ingest accepted overrides as governed audit memory, not general-purpose memory.

## Non-goals

This contract does not implement signature verification yet. It defines the artifact shape and validation boundary required before signature verification is wired into runtime consumers.
