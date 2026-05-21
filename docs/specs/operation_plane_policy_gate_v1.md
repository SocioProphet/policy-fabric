# Operation Plane Policy Gate v1

## Purpose

This specification defines the Policy Fabric boundary for Workspace Operation Plane commands, artifact admission, trust boundaries, and human/agent remediation.

Policy logic must **not** be embedded inside `prophet-platform`, UI repos, TurtleTerm, BearBrowser, or agents. The Operation Plane runtime must call Policy Fabric and persist gate records. UI components may render Policy Fabric response fields but must not act as policy authority.

## References

- `SocioProphet/workspace-inventory#3`
- `SocioProphet/prophet-core-contracts#1`
- `SocioProphet/prophet-platform#376`
- Contract: `contracts/operation_plane_policy_gate_v1.schema.json`

---

## Document kinds

All shapes in this specification are serialized as JSON documents with `kind` and `schema_version: "v1"` fields. The unified JSON Schema at `contracts/operation_plane_policy_gate_v1.schema.json` validates all kinds.

| Kind | Purpose |
|---|---|
| `PolicyGateRecord` | Machine-checkable gate event record persisted by the Operation Plane runtime |
| `PolicyEvaluationRequest` | Request sent by the runtime to Policy Fabric before executing a command |
| `PolicyEvaluationResponse` | Actor-relative authorization response from Policy Fabric |
| `TrustBoundaryRecord` | Description of an external trust boundary that affects evaluation |
| `OverridePolicyRecord` | Scoped, time-bounded, audited override of a gate block |

---

## Authorized commands

The following Operation Plane commands are authorized to call Policy Fabric gate evaluation. Any command not in this list must not bypass gate evaluation.

| Command | Description |
|---|---|
| `CreateOperation` | Initialize a new Workspace operation |
| `StartOperation` | Begin execution of a created operation |
| `RetryTask` | Retry a failed task within an operation |
| `CancelOperation` | Cancel an operation in flight |
| `ResolveDecision` | Resolve a human-in-the-loop decision point |
| `AdmitArtifact` | Submit an artifact for policy-gated admission |
| `ActivateArtifact` | Promote an admitted artifact to active status |
| `ExportDiagnostics` | Export operation diagnostics, subject to export policy |
| `RequestOverride` | Request a scoped policy override for a blocked gate |

---

## Artifact admission gates

Each gate maps to a distinct block reason and a `responsible_actor` who can fix the block.

| Gate type | Description | Default responsible actor |
|---|---|---|
| `metadata.required` | Artifact is missing required metadata fields | `user` |
| `security.secret_detected` | A secret or credential was detected in the artifact | `user` |
| `security.malware_blocked` | Malware signature was detected in the artifact | `workspace_owner` |
| `security.pii_phi_review_required` | PII or PHI found; human review required before admission | `workspace_owner` |
| `encryption.key_unavailable` | Encryption key required for admission is unavailable | `local_device_owner` |
| `quota.workspace_limit` | Workspace artifact quota would be exceeded | `workspace_owner` |
| `conversion.failed` | Artifact format conversion required for admission failed | `user` |
| `indexing.unsupported` | Artifact type is not supported for workspace indexing | `tenant_admin` |
| `policy.external_sharing_blocked` | Admission would trigger external sharing blocked by policy | `tenant_admin` |
| `agent.review_required` | An agent must review the artifact before admission proceeds | `agent_operator` |
| `license.unverified` | Artifact license could not be verified against workspace policy | `external_owner` |
| `provenance.unknown` | Artifact origin or chain of custody cannot be verified | `connector_owner` |

---

## Trust boundaries

The following trust boundary types are modeled as `TrustBoundaryRecord` documents:

| Boundary type | Description |
|---|---|
| `external_connector` | A connector to an external data source or service |
| `third_party_model_endpoint` | A third-party model inference endpoint |
| `remote_agent` | A remote agent operating outside the local trust domain |
| `customer_key_service` | A customer-managed key service (BYOK/HYOK) |
| `imported_repo` | A repository imported into the workspace from an external source |
| `enterprise_firewall` | An enterprise network boundary controlling data egress |

---

## Authorization response shape

A `PolicyEvaluationResponse` carries:

- `outcome`: `allow` or `deny` — only binary outcomes; deferral is modeled as a pending `PolicyGateRecord`.
- `reason`: Machine-readable reason string. UI may render this; UI must not generate it.
- `responsible_actor`: Which actor class can fix the block (`RemediationActor` enum).
- `audit_required`: Boolean; when `true` the runtime must emit an audit record.
- `remediation_options`: Actor-relative list of `RemediationOption` objects, each naming an `actor`, `action`, and `description`. Empty when `outcome` is `allow`.
- `gate_record_ids`: IDs of `PolicyGateRecord` documents generated for this evaluation.
- `expires_at`: When `allow` with time-bounded scope, the expiry of the authorization.

---

## Remediation actors

Policy Fabric responses are actor-relative. The `responsible_actor` field and each `RemediationOption` actor field identify who can resolve a block:

| Actor | Can fix |
|---|---|
| `user` | Actions the end user can take directly (e.g., remove secrets, add metadata) |
| `workspace_owner` | Actions requiring workspace-level authority |
| `tenant_admin` | Actions requiring tenant-level authority or override power |
| `external_owner` | Actions requiring the external data or artifact provider |
| `connector_owner` | Actions requiring the connector configuration owner |
| `model_provider` | Actions requiring the model or inference provider |
| `local_device_owner` | Actions requiring the local device key or credential owner |
| `agent_operator` | Actions requiring the agent operator or orchestrator owner |

---

## Override policy shape

An `OverridePolicyRecord` enables responsible actors to waive a gate within a defined scope. Requirements:

- **Scope** must be one of: `workspace`, `tenant`, `artifact`, `operation`, `connector`.
- **Actor** must be identified and typed.
- **Expiry** is mandatory; no perpetual overrides.
- **Affected gate types** must be explicitly enumerated.
- **Audit record reference** is required; no override may be issued without an audit trail.
- **Status** lifecycle: `active` → `expired` (automatic) or `revoked` (early termination with `revocation_reason`).

---

## Scope rule

- `policy-fabric` (this repository) owns policy contracts, gate validation semantics, and governed-decision shapes.
- `prophet-platform` owns the Operation Plane runtime behavior and consumes Policy Fabric gate decisions.
- UI repositories may render `PolicyEvaluationResponse` fields but must not generate, cache, or interpret policy outcomes independently.
- Agents must call Policy Fabric for gate evaluation and must not embed policy logic inline.

---

## Machine-checkability

All gate records must be serializable and machine-checkable:

- `PolicyGateRecord` documents are the unit of persistence. The runtime persists one per gate event.
- Gate records are correlated to operations via `operation_id` and to responses via `gate_record_ids`.
- Override records are correlated to gate records via `override_ref` on `PolicyGateRecord`.
- Trust boundary records are correlated via `trust_boundary_ref` on `PolicyGateRecord`.

---

## Examples

| File | Kind | Scenario |
|---|---|---|
| `examples/operation_plane_policy_gate_record_example.json` | `PolicyGateRecord` | Blocked on `security.secret_detected` during `AdmitArtifact` |
| `examples/operation_plane_policy_eval_request_example.json` | `PolicyEvaluationRequest` | `AdmitArtifact` request for a notebook |
| `examples/operation_plane_policy_eval_response_example.json` | `PolicyEvaluationResponse` | Deny response with actor-relative remediation options |

---

## Status

Active. This specification is machine-enforced by `scripts/validate_operation_plane_policy_gate.py` and `scripts/doctor.py`.
