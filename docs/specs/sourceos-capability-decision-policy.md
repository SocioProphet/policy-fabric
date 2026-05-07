# SourceOS Capability Decision Policy

Status: v0.1 baseline

Policy Fabric owns the governance-facing policy contract for SourceOS capability decisions. `sourceos-syncd` owns the local event, service, launch, process provenance, and incident schemas. This policy lane connects those contracts to explicit allow, deny, audit, and defer decisions.

## Purpose

The SourceOS control plane requires policy decisions that are inspectable, local-first, and suitable for agents. Static service manifests are not enough. Every sensitive capability needs a policy result, explanation code, actor, subject, retention posture, and canonical event path.

This lane establishes the baseline policy for:

- app/browser service capabilities
- developer terminal capabilities
- product identity boundaries
- launch hygiene
- local and remote telemetry
- local-first trust posture
- canonical event requirements
- audit requirements for policy decisions

## Artifacts

- `contracts/sourceos-capability-decision-policy.schema.json`
- `examples/sourceos/sourceos-capability-decision-baseline.policy.json`
- `tools/validate_sourceos_capability_decision_policy.py`

Validate locally:

```bash
python3 -m pip install --user jsonschema
python3 tools/validate_sourceos_capability_decision_policy.py
make sourceos-capability-decision-policy-validate
```

The policy is also included in the repository-level validation loop:

```bash
make validate
```

## Baseline doctrine

The default decision is `deny`.

Remote telemetry is denied by default. Local telemetry is audit-only and must be emitted as local canonical evidence, not silent product analytics.

Upstream engine provenance is allowed as provenance, source, license, and mirror metadata. Upstream product identity leakage is denied on user-facing product surfaces.

Packaged apps must not inherit user shell environments. Duplicate launch PATH entries are denied. Developer/toolchain PATH entries are warning-level by default until platform packaging hardens further.

Trust evaluation is local-first by default. Silent remote trust lookup is denied. Any network trust lookup requires explicit policy.

Expected denials must not render above `notice` severity by default. They must carry a decision ID, explanation code, actor, subject, retention class, and operator narrative.

## Required service classes

### `sourceos.app.browser`

The browser service class covers BearBrowser and future SourceOS-governed browser products.

Required capabilities include browser profile access, renderer spawn, GPU helper spawn, web network client, local incident diagnostics, and canonical event emission.

Denied capabilities include default remote telemetry, ambient cloud sync lookup, upstream product identity leakage, and inherited user shell launch.

### `sourceos.developer.terminal`

The developer terminal service class covers TurtleTerm and future SourceOS developer shells.

Required capabilities include developer session provenance, canonical event emission, and local incident diagnostics.

Denied capabilities include default remote telemetry, untraced privilege escalation, and unbounded user-shell inheritance.

## Required explanation codes

The baseline validator requires these explanation codes:

- `CAPABILITY_ALLOWED_CANONICAL_EVENT_EMIT`
- `CAPABILITY_AUDIT_LOCAL_TELEMETRY`
- `CAPABILITY_ALLOWED_DEVELOPER_SESSION_PROVENANCE`
- `CAPABILITY_DENIED_REMOTE_TELEMETRY_DEFAULT`
- `CAPABILITY_DENIED_PRODUCT_IDENTITY_LEAK`
- `CAPABILITY_DENIED_INHERIT_USER_SHELL`
- `CAPABILITY_DENIED_UNTRACED_PRIVILEGE_ESCALATION`

These codes become the stable bridge between Policy Fabric decisions, SourceOS canonical events, operator narratives, and DeliveryExcellence metrics.

## Integration targets

- `SourceOS-Linux/sourceos-syncd`: consumes policy decisions as canonical event fields and service graph release gates.
- `SourceOS-Linux/BearBrowser`: consumes browser service-class decisions for product identity, telemetry, launch hygiene, and local evidence.
- `SourceOS-Linux/TurtleTerm`: should consume developer terminal service-class decisions for command provenance, project-scoped developer mode, and privileged-action receipts.
- `SocioProphet/agentplane`: should attach these policy decisions to agent actions and process lineage.
- `SocioProphet/sociosphere`: should surface capability decisions as operator cards.
- `SocioProphet/delivery-excellence`: should track policy-decision quality, denial noise, and release readiness.

## Non-goals

- This lane does not replace SourceOS runtime enforcement.
- This lane does not grant remote telemetry.
- This lane does not hide upstream provenance.
- This lane does not allow unbounded developer shell inheritance.

## Completion criteria

This lane is minimally complete when:

1. The schema validates.
2. The baseline example validates.
3. Semantic invariants pass.
4. `make validate` includes the validator.
5. Browser and developer terminal service classes are present.
6. Required denial and explanation-code semantics are stable.
