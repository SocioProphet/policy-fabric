# Banking Policy Boundary Note

## Current fit

The existing `policy_fabric_policy_v2` contract is a strong fit for:
- masking or tokenizing filing fields before publication
- controlling export transformations on sensitive counterparty data
- redacting operator notes or review annotations that should not leave a bounded lane

## Current non-fit

The existing contract is **not yet** a natural fit for:
- general model promotion state machines
- non-transform approval orchestration
- capital override lifecycle semantics as pure allow/deny workflows

Those concerns may eventually need either:
- a new Policy Fabric contract family, or
- a separate governance contract surface that composes with Policy Fabric artifacts.

## Rule of thumb

If the policy is fundamentally about:
- selecting sensitive data,
- applying transformation or controlled exposure,
- testing that transformation deterministically,
then it belongs cleanly in the current Policy Fabric contract.

If the policy is fundamentally about:
- approval workflow progression,
- release gates without a transform surface,
- stateful promotion ladders,
then it likely needs a different primary contract surface.
