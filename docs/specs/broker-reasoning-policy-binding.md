# Broker Reasoning Policy Binding

## Purpose

Policy Fabric is the PolicyPlane implementation surface for the cross-cloud services broker model.

It does not own broker runtime or execution placement. It authors, validates, packages, and reviews policy decisions and policy evidence used by the broker.

## PolicyPlane responsibilities

PolicyPlane should decide:

- whether a service request is allowed
- whether a provider is eligible
- whether a provider binding meets required controls
- which policy pack applies
- whether human review is required
- whether an exception is allowed
- what compensating controls are required
- what evidence must be emitted
- what policy snapshot applies to the decision

## Inputs

PolicyPlane broker inputs include:

- service request
- service class
- provider class
- provider binding
- policy pack references
- data classification
- jurisdiction and residency context
- cost and continuity requirements

## Outputs

PolicyPlane should emit:

- `PolicyDecision`
- `PolicyPack`
- compiled execution plan
- validation report
- release pack
- replay report
- exception decision, if applicable

## Broker rule

BrokerPlane must not fulfill a production service without a PolicyPlane decision or explicit exception record.

## Design invariant

PolicyPlane decides. AgentPlane executes. BrokerPlane coordinates lifecycle and evidence.
