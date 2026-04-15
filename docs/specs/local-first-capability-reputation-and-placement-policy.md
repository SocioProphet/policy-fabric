# Local-First Capability, Reputation, and Placement Policy

Status: Draft  
Repository role: Policy binding for local-first execution, sync, and trust governance

## Purpose

This document binds the platform-wide local-first desktop and sync standard into Policy Fabric terms.

Policy Fabric owns the policy layer for:

- capability grants and denials
- package / remote / mirror trust posture
- session placement policy
- reputation and concentration controls
- operator override rules
- evidence expectations for governed decisions

## Policy subjects

The following policy subjects are in scope:

- desktop application package
- package remote / mirror
- sync peer
- local session
- fog / edge / cloud placement target
- agent skill or tool surface
- capability request
- operator override

## Mandatory policy decisions

A conforming deployment MUST be able to evaluate and emit evidence for:

1. whether a package may be installed
2. whether a remote or mirror may be trusted for a package or update path
3. whether a capability request should be allowed, denied, reduced, or time-bounded
4. whether a session should remain local, use fog placement, or use cloud fallback
5. whether a reputation score change is permitted to influence ranking, task routing, or visibility
6. whether a concentration threshold has been crossed and mitigation is required

## Capability policy model

Capability policy MUST support:

- default deny for high-risk host capabilities
- explicit allow rules by capability class
- time-bounded grants when a long-lived grant is not required
- actor, device, and session scoping
- policy reason text suitable for user-visible explanation
- evidence output showing which rule produced the outcome

Recommended capability classes:

- file.read
- file.write
- folder.scope
- uri.open
- notification.send
- camera.use
- microphone.use
- screen.capture
- clipboard.read
- clipboard.write
- secret.request
- network.broad
- network.scoped
- device.attach

## Placement policy model

Placement policy MUST evaluate at least:

- data sensitivity
- locality requirement
- trust tier of the target node or region
- latency budget
- capacity budget
- identity / group entitlement
- operator emergency override status

Placement outcomes SHOULD include:

- local-only
- preferred-local-then-fog
- fog-only
- fog-then-cloud-fallback
- cloud-allowed
- denied

Every placement outcome MUST emit a receipt that includes the evaluated constraints and the selected placement class.

## Reputation and concentration policy

Policy Fabric MUST NOT treat reputation as a simple linear amplifier.

Reputation policy SHOULD separately track:

- integrity / trustworthiness
- utility / service quality
- freshness of evidence
- abuse / scam exposure
- concentration contribution
- newcomer protection / diversity budget

A policy deployment MUST support concentration guards that can:

- reduce ranking amplification for already dominant subjects
- require more evidence before increasing privilege for highly visible subjects
- preserve visibility or routing budget for emerging subjects
- quarantine suspicious spikes in reputation

## Remote and package trust policy

Package and remote trust policy SHOULD support:

- trust roots and signer classes
- approved mirror sets
- degraded mode when the preferred remote is unavailable
- local cache preference
- rollback and quarantine behavior
- policy differentiation between stable, preview, and experimental channels

## Evidence requirements

Every material policy decision MUST be able to produce a policy evidence object containing:

- subject
- decision
- rule path
- evaluated attributes
- resulting constraints
- override state
- timestamp
- policy bundle version
- receipt correlation id

## Relationship to other repositories

- `SocioProphet/TriTRPC` carries the decision and receipt transport surface
- `SocioProphet/prophet-platform` executes the policy outcomes in running services
- `SocioProphet/synapseiq` enriches and reasons over policy evidence and trust telemetry
- `SocioProphet/socioprophet-standards-storage` defines the governing standard posture
- `SourceOS-Linux/sourceos-spec` must eventually carry typed schemas for these policy objects

## Initial policy backlog

1. Define capability request contract examples
2. Define placement decision contract examples
3. Define reputation input and concentration telemetry fields
4. Define mirror trust and remote trust policy bundles
5. Add validation rules that reject winner-take-all-only ranking policies for governed package and agent surfaces
