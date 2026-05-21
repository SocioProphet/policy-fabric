# Governed Action Policy Decision v0

Status: v0.1 bounded contract surface.

This document defines the first Policy Fabric decision primitive for the Watson/Cyc/Semantic-Web/CHRONOS deployable loop.

## Purpose

Policy Fabric owns the decision boundary for whether a bounded downstream proposal may proceed, must be denied, must be modified, or must escalate.

The intended integration path is:

```text
Sherlock source-quality answer trace
  -> Ontogenesis corpus event semantics
  -> Policy Fabric decision
  -> Agentplane bounded proposal and trace
  -> Model Governance Ledger audit event
```

## Added surfaces

```text
contracts/governed-action-policy-decision.v0.schema.json
examples/governed-action-policy/valid.low-risk-allow.json
examples/governed-action-policy/invalid.research-only-allow.json
examples/governed-action-policy/invalid.high-risk-allow.json
tools/validate_governed_action_policy_decision.py
```

## v0 decision rule

`allow` is only valid when:

- `risk_class == low`
- `evidence_grade == implementation_safe`
- all evidence refs are marked `implementation_safe: true`
- all evidence source qualities are confirmed classes

Research-only evidence must not produce `allow`.

High or critical risk classifications must not produce `allow` in this v0 contract.

## Validation

Run:

```bash
make governed-action-policy-decision-validate
```

The target is also included in:

```bash
make validate
```

## Boundary

This contract does not implement a full policy language, external compliance integration, downstream execution, or persistence. It provides the machine-readable decision payload, examples, and validation rules for the first bounded cross-repo loop.
