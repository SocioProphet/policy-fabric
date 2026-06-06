# IOES Protected-Value Veto Profile

## Purpose

This profile defines the first Policy Fabric doctrine for IOES human-protection gates.

IOES means Identity, Ontogenesis, Ecology, and Stewardship.

The profile is intentionally policy-facing rather than philosophical. It defines the values that must survive optimization, automation, projection, delivery, and agent execution.

Policy Fabric should treat these values as veto-capable constraints, not advisory preferences.

## Protected values

### Human dignity

A human subject must not be reduced to an account, score, digital twin, projection, role, productivity metric, credential, or agent summary.

Any policy that permits human-impacting action from such a reduction must fail closed.

### Consent

Consent must be scoped, legible, revocable, time-bounded where appropriate, and tied to purpose.

A consent receipt must not silently authorize unrelated projection, export, inference, or delivery actions.

### Stewardship without ownership

A stewardship relationship grants responsibility, not possession.

A policy must reject any action that treats a steward, mentor, guardian, maintainer, teacher, or successor as the owner of the subject or artifact unless a separate ownership authority is explicitly present.

### Developmental integrity

Ontogenetic or developmental state must not be mutated without authority, evidence, review posture, and appeal or repair path where meaningful.

A learner, project, theory, community, or human developmental state must not be changed merely because a model inferred it.

### Ecological accountability

Gaia dependency and impact records must not be stripped from a decision merely because they complicate execution.

A policy must preserve material dependency, impact, and reciprocal-obligation context for actions that affect ecosystems, communities, knowledge commons, or shared infrastructure.

### Provenance

Every identity-affecting, stewardship-affecting, learning-affecting, or delivery-affecting claim must carry evidence or be marked unsupported.

Unsupported claims may be stored as candidates but must not be promoted into canonical state or outward projection.

### Succession

A stewardship object should have a succession posture.

Where no successor exists, policy should require review, risk flagging, or repair rather than silently accepting abandonment risk.

### Agent boundedness

Agents may propose, summarize, classify, and execute only within explicit grants.

An agent must not alter identity, consent, stewardship, developmental state, canon status, or delivery authority without scoped permission and evidence.

## Required decision outcomes

Policy decisions should distinguish at least these outcomes.

Allow: action is permitted under current evidence, authority, and protected-value posture.

Deny: action violates a protected value, authority boundary, or required evidence condition.

Repair: action may become admissible after missing evidence, consent, succession, provenance, or review is supplied.

Review: action requires human or governance review before execution or promotion.

Exception: action is temporarily allowed under documented exception authority and expiry.

## Minimum evaluation questions

Before allowing a human-impacting action, a policy must be able to answer:

Who or what is affected?

Which IOES dimension is affected?

What authority permits the action?

What consent applies?

What evidence supports the action?

What protected values are at risk?

What can be repaired or reversed?

What cannot be reversed?

Which agent, human, or institution is accountable?

Which graph, twin, projection, execution, learning, or delivery record will receive the decision?

## Initial policy surfaces

The first machine-readable implementation should cover these action families.

identity.projection.emit

identity.prime_topic.merge

stewardship.edge.assign

stewardship.edge.transfer

stewardship.edge.revoke

ontogenesis.state.update

gaia.dependency.record

learning.artifact.promote

learning.nba.emit

agent.bundle.execute

delivery.outcome.score

## Fail-closed defaults

If consent is missing, deny.

If authority is missing, deny.

If evidence is missing, repair or deny.

If the action changes developmental state, review unless a specific policy allows automated promotion.

If the action assigns or transfers stewardship, review unless a specific succession rule permits automated transfer.

If the action emits an outward projection, require consent and projection-loss disclosure.

If the action affects a protected class, minor, patient context, civic context, family context, or employment context, require heightened review.

If a model output is the only evidence, do not promote to canonical truth.

## Non-goals

This document does not implement Rego, JSON Schema, or runtime enforcement.

It defines the semantic veto profile to be converted into machine-readable contracts and fixtures.

## Next implementation targets

Create `contracts/ioes-protected-value-veto-profile.schema.json`.

Create valid and invalid examples for identity projection, stewardship transfer, and ontogenesis mutation.

Add validator coverage proving fail-closed behavior.

Bind the profile to AgentPlane execution evidence and ProCybernetica IOES conformance.
