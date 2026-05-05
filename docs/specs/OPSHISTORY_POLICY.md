# OpsHistory Policy Contract

Status: initial contract-capture specification.

## Purpose

OpsHistory is the shared local-first operational event fabric for governed multi-chat human/agent operations. Policy Fabric owns the decision families that decide whether OpsHistory material may replicate, hydrate context, enter memory, bridge/export, expose artifacts, export browser metadata, export operational receipt metadata, or execute redaction/tombstone propagation.

This document is contract-only. It does not implement live sync, live memory writeback, browser export, terminal capture, or agent context hydration.

## Decision families

### replicate_event

Question: may an OpsHistory event leave the local store?

Inputs should include:

- event class;
- source plane;
- room/thread/workroom/topic scope;
- actor ref;
- Agent Registry grant ref for non-human actors;
- payload mode;
- payload size;
- artifact refs;
- redaction refs;
- target relay, bridge, or workroom.

Allowed outcomes:

- allow;
- deny;
- metadata-only;
- summary-only;
- ref-only;
- require-human-approval.

### hydrate_context

Question: may an agent or tool receive context from an OpsHistory scope?

Hydration must be denied by default for raw sensitive material. Summary-only and ref-only outcomes should be preferred unless a stronger policy decision exists.

### write_memory

Question: may an event or context pack enter Memory Mesh?

Dry-run mode must always produce no-writeback behavior. Durable writeback requires policy admission and retention posture.

### redact_event

Question: is a redaction/tombstone accepted, and what downstream material must be invalidated?

Redaction propagation must take priority over ordinary sync and ordinary memory writeback.

### bridge_event

Question: may an event cross from the canonical Matrix/local-first substrate to Slack, Discord, GitHub, CI, enterprise relay, or another bridge?

Bridge decisions must preserve metadata and strip or summarize material that is not admitted for the target trust domain.

### export_artifact

Question: may an artifact referenced by OpsHistory be exposed?

Hash/ref-only export is the default. Human approval may be required for any payload-bearing export.

### browser_event_export

Question: may a BearBrowser event export to OpsHistory?

Human-secure profile export is denied by default. Agent-runtime browser events may be admitted as metadata-only, summary, or ref-only.

### receipt_event_export

Question: may an operational receipt export to OpsHistory?

Content capture is disabled by default. Receipt metadata may be exported when policy and authority allow.

## Required evidence

Every allow, summary-only, ref-only, redaction-required, or deny decision must produce a stable PolicyDecision reference suitable for OpsHistoryEvent.policyDecisionRefs.

## Non-negotiables

- No raw sensitive payloads by default.
- No human browser profile export by default.
- No unrestricted operational recording.
- No memory writeback in dry-run mode.
- No bridge/export without explicit target trust-domain admission.
- No non-human hydration without Agent Registry authority.
- Redaction/tombstone propagation outranks ordinary synchronization.

## Consumers

- SourceOS-Linux/agent-term
- SourceOS-Linux/BearBrowser
- SourceOS-Linux/sourceos-shell
- SocioProphet/memory-mesh
- SocioProphet/agent-registry
- SocioProphet/agentplane
- SourceOS-Linux/sourceos-spec
