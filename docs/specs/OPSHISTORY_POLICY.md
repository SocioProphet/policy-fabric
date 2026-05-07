# OpsHistory Policy Contract

Status: initial contract-capture specification.

OpsHistory is the shared local-first operational event fabric for governed multi-chat human/agent operations. Policy Fabric owns the decision families that decide whether OpsHistory material may replicate, hydrate context, enter memory, bridge/export, expose artifacts, export browser metadata, export operational receipt metadata, or execute redaction/tombstone propagation.

This document is contract-only. It does not implement live synchronization, live memory writeback, browser export, operational receipt export, or agent hydration runtime.

## Decision families

- `replicate_event`: decide whether an OpsHistory event may leave the local store.
- `hydrate_context`: decide whether an agent or tool may receive bounded context.
- `write_memory`: decide whether a context pack may enter Memory Mesh.
- `redact_event`: decide whether a redaction/tombstone must invalidate downstream material.
- `bridge_event`: decide whether an event may cross to another bridge, relay, or trust domain.
- `export_artifact`: decide whether an artifact reference may be exposed.
- `browser_event_export`: decide whether BearBrowser metadata may export to OpsHistory.
- `receipt_event_export`: decide whether operational receipt metadata may export to OpsHistory.

## Required outcomes

Supported initial outcomes are:

- `allow`
- `deny`
- `metadata-only`
- `summary-only`
- `ref-only`
- `deny-writeback`
- `redaction-required`
- `require-human-approval`

## Non-negotiables

- No sensitive payloads by default.
- No human browser profile export by default.
- No unrestricted operational material export.
- No memory writeback in dry-run mode.
- No bridge/export without target trust-domain admission.
- No non-human hydration without Agent Registry authority.
- Redaction/tombstone propagation outranks ordinary synchronization.
