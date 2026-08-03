# Shared-State Write / Live-Activation Authorization Policy (v0)

- **Policy ID:** `shared_state.live_activation_authorization.v0`
- **Policy version:** `0.1.0`
- **Contract:** [`contracts/shared-state-write-policy-decision.v0.schema.json`](../../contracts/shared-state-write-policy-decision.v0.schema.json)
- **Runtime evaluator:** [`tools/shared_state_write_policy_evaluator.py`](../../tools/shared_state_write_policy_evaluator.py)
- **Enforcement gate (teeth):** [`tools/validate_shared_state_write_policy.py`](../../tools/validate_shared_state_write_policy.py) via `make shared-state-write-policy-validate` and the `shared-state-write-policy` CI workflow.

## Policy

Shared-state / live-infrastructure **WRITES require explicit authorized-principal
authorization**. A relayed coordinator/agent-to-agent instruction does **NOT** satisfy
the authorization bar.

Live activation — running production workflows, mutating a cluster/namespace, writing
to a shared graph store or shared ledger — must be gated to the authorized principal.
Automated/agent actors may only **READ-probe** shared state, and must ship changes as
**reviewable artifacts (PRs against mock/test transports)** whose live activation is a
separate, explicitly-authorized step.

## Rationale (incident of 2026-08-03)

On 2026-08-03 a subagent, acting on a *relayed coordinator message* (not the user),
port-forwarded into the live `socioprophet` GKE namespace and attempted a probe-node
**WRITE** to the shared HellGraph store, and wrote manifests pointing at live
endpoints — tripping the security classifier. Harm was ~nil only because the store was
down and nothing merged. This policy makes that boundary explicit and enforced: the
relayed instruction is not authorization, the acting subject was an automated actor,
and the target was live shared state — so the write is denied at the gate.

## Decision model

The evaluator is pure and deterministic (`evaluate(record) -> record + decision +
receipt`) and **fails closed** on missing/unknown context.

| Case | Outcome | Reason code |
| --- | --- | --- |
| Read-probe of shared state (any actor) | `allow` | `read_probe_allowed` |
| Reviewable artifact against a mock/test transport | `allow` | `gated_artifact_allowed` |
| Write against a mock/test transport | `allow` | `mock_transport_write_allowed` |
| Live shared-state write by the authorized principal with an explicit activation grant | `allow` | `live_activation_authorized` |
| Live shared-state write authorized only by a relayed coordinator message | `deny` | `relayed_authorization_insufficient` |
| Live shared-state write authorized only by an agent-to-agent instruction | `deny` | `agent_to_agent_authorization_insufficient` |
| Live shared-state write by an automated actor with no authorization | `deny` | `shared_write_requires_authorized_principal` |
| Live activation by the authorized principal that is not explicit | `deny` | `non_explicit_activation` |
| Reviewable artifact pointed at a live endpoint | `deny` | `artifact_targets_live_endpoint` |
| Unknown authorization provenance | `deny` | `missing_authorization_context` |

A live shared-state write is authorized **only** when the acting subject IS an
authorized principal (`subject.actor_class == "authorized_principal"`) **and** the
authorization is an explicit, principal-scoped activation grant
(`authorization.source == "authorized_principal"`, `explicit_activation == true`,
`principal_id` present). Every other path to a live shared-state write is denied.

## Enforcement (teeth)

The gate carries both a NEGATIVE proof (the 2026-08-03 incident record is denied) and
a POSITIVE proof (a read-probe and a gated authorized activation pass). A control that
never fires is suspect, so the validator pins the expected `(outcome, reason_code)` for
every case and fails on drift.

```
make shared-state-write-policy-validate
```

runs the full case table locally and in the `shared-state-write-policy` CI workflow on
every PR and on push to `main`.
