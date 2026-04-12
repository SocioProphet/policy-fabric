# Planning Governance Binding v0

## Status

Plan/spec document.

This document binds the abstract-reasoning and governed-planning slice into the Policy Fabric repository.

## Canonical upstreams

Policy Fabric does not own the normative cross-repository contract canon.

The canonical upstreams are:
- `SocioProphet/semantic-serdes` for planner-facing semantic artifacts
- `SocioProphet/TriTRPC` for typed planning and execution bridge contracts
- `SocioProphet/socioprophet-standards-storage` for benchmark and evaluation doctrine

Policy Fabric is the authored-policy and compiled-policy lane.

## Why this binding exists

Abstract reasoning is not reliably solved by language-model fluency alone.
A branch that produces a plausible answer, rationale, or compilable program may still fail to recover the governing rule.

Policy Fabric therefore defines the admissibility conditions for abstract and program-induction lanes.

## Policy Fabric responsibilities

Policy Fabric owns the following responsibilities for the planning slice:

1. define reasoning-class specific admissibility rules
2. define llm-only prohibition rules where required
3. define minimum verification mode per reasoning class
4. define when program-candidate evidence is mandatory
5. define when counterexample search is mandatory
6. define when declared backtracking capability is mandatory
7. compile authored branch-admissibility policy into execution-oriented gate inputs

## Core invariants

1. A branch in the `ABSTRACT` or `PROGRAM_INDUCTION` lane MUST NOT be admissible as llm-only when policy declares `llmOnlyForbidden=true`.
2. A branch requiring program induction MUST carry a program-candidate reference before execution eligibility.
3. A branch requiring counterexample search MUST carry a counterexample-search result before execution eligibility.
4. A branch requiring backtracking capability MUST declare a backtracking-capable execution path or be denied.
5. A branch accepted under this slice MUST remain traceable to its authored Policy Fabric policy id and version.

## Acceptance gate

The v0 slice is acceptable when we can show:
- one authored branch-admissibility policy
- one compiled gate-context representation
- one denied abstract branch for llm-only posture
- one admitted abstract branch with program candidate and counterexample evidence
- lineage from decision back to policy id and version
