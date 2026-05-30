# Workspace Context Policy Decision v0

Status: v0.1 bounded contract surface.

## Purpose

This document defines the Policy Fabric decision primitive for Workspace Context Fabric.

Policy Fabric owns the decision boundary for whether a workspace-context request is allowed, denied, modified, or escalated.

## Supported request types

The v0 request family is:

```text
workspace.context.capture
workspace.context.project
workspace.context.share
workspace.context.recall.propose
workspace.context.recall.promote
workspace.context.continuation.record
```

## Boundary

Policy Fabric does not own Workroom, ContextGraph, platform record, AgentPlane evidence, Memory Mesh promotion, or Agent Registry authority binding contracts.

Policy Fabric evaluates requested handling against declared sensitivity, release mode, recall mode, policy refs, and evidence refs.

## v0 rule posture

The v0 rule is intentionally conservative:

- public release requires a policy result other than unrestricted allow unless the request is low risk and explicitly evidence-backed;
- recall promotion requires review or escalation;
- missing evidence cannot produce allow;
- denied requests must carry a reason;
- modified requests must carry runtime constraints.

## Added surfaces

```text
contracts/workspace-context-policy-decision.v0.schema.json
examples/workspace-context-policy/valid.project-modify.json
examples/workspace-context-policy/invalid.promote-allow.json
examples/workspace-context-policy/invalid.missing-evidence-allow.json
tools/validate_workspace_context_policy_decision.py
```

## Validation

```bash
make workspace-context-policy-decision-validate
```
