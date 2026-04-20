# Agent / Eval Fabric Gate Alignment (Draft)

## Purpose

This note records how Policy Fabric should align with the downstream agent and eval-fabric stacks.

## Why this repo matters

`policy-fabric` is the canonical policy/control repository. It should define and validate the governed decision shapes that downstream runtime lanes consume.

For the agent and eval-fabric stack, the most important policy-facing surfaces are:
- policy decisions referenced by gate activation records
- approval and rollback expectations for side-effecting actions
- validation evidence for promotion decisions

## Alignment targets

The downstream stacks already use and test these concepts:
- authorization gates
- scope gates
- policy gates
- risk gates
- evidence gates
- approval gates
- rollback gates

This repository should remain the canonical place for the policy contract and validation semantics behind those gates.

## Scope rule

- `socioprophet-agent-standards` owns the normative profile language for control/gating/graduation.
- `prophet-platform` owns executable eval-fabric runtime behavior and downstream suite consumption.
- `policy-fabric` owns policy contracts, validation, and governed-decision semantics.

## Expected artifacts

The policy layer should remain compatible with downstream references such as:
- `policy_decision_ref`
- `approval_ref`
- `rollback_requirement`
- release or validation evidence for promotion decisions

## Status

Captured as a narrow alignment note. Not yet linked from a broader policy-fabric integration index.
