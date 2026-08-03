# Consent-plane decision engine

`policy_fabric/purpose_admissibility_gate.py` is the **runtime** consent-plane
gate. Until now the consent plane had a decision *contract*
(`contracts/purpose_admissibility_gate_decision_v1.schema.json`) and a document
*validator* (`tools/validate_purpose_admissibility_gate.py`) — but nothing that
read the catalogs and **decided**. This engine is that missing piece: it turns
E1 from "envelope declared in CI" into "a disallowed invocation is refused at
run".

## Use

```python
from policy_fabric.purpose_admissibility_gate import enforce, ConsentDenied

try:
    enforce({"role": "implementer", "surface": "browser", "space": "agent-space",
             "tool": "source-mutate", "declaredPurpose": "implement"})
except ConsentDenied as deny:
    ...  # invocation refused: deny.reasons, deny.decision (a v1 decision doc)
```

`enforce()` is the call a surface makes **before** dispatching a tool. It returns
the admit decision or raises `ConsentDenied` — the invocation cannot proceed on a
deny. `decide()` returns the decision document without raising (for audit/log).

CLI: `python -m policy_fabric.purpose_admissibility_gate --role .. --surface .. --space .. --tool .. --purpose ..`
(exit 0 admit, 3 deny).

## What it decides (fail-closed)

Reads the canonical catalogs from socioprophet-agent-standards consent-plane/001
(`agent-roles`, `surfaces`, `spaces`, `tool-purpose-bindings`). An invocation is
admitted only if **all** hold; deny reasons accumulate:

1. the tool serves the declared purpose;
2. the role admits the purpose;
3. the surface allows it and does not deny it (deny wins);
4. the surface does not deny the target space (containment — e.g. a browser agent
   is confined to agent-space);
5. the role tolerates every blocking taint on the space, and a data-namespace
   crossing carries a per-tenant consent toleration (GDPR Art 6/7);
6. per-purpose consent is present where the surface or tool requires it.

Anything unknown — role, surface, space, tool, purpose, or a missing catalog —
is a **deny**.

## Catalog discovery (zero-config)

`$PURPOSE_GATE_CATALOG_ROOT` → a sibling `socioprophet-agent-standards` checkout
→ vendored `tests/fixtures/consent-plane/`. An **explicit** root is honoured
alone (a miss there fails closed, not a silent fallback). A drift guard test
asserts the vendored fixtures byte-match the canonical catalogs when a sibling
checkout is present.

## Follow-on

The engine + `enforce()` are the teeth. The remaining step is each surface app
calling `enforce()` on its real tool-dispatch path (goose-notes / BearBrowser /
TurtleTerm / sourceos-shell) so the refusal happens inside the running app, not
only here. Tracked as the consent-plane runtime-dispatch work.
