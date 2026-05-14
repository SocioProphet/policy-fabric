# Constitutional contract history

This file records pre-merge contract-shape corrections for the constitutional policy engine v0.1 tranche. These entries are not external breaking changes because no deployed external API contract exists yet.

## v0.1 draft cleanup

### Endpoint naming

Initial review stub used five hardcoded endpoint paths:

```text
/a1/evaluate
/a3/evaluate
/a4/evaluate
/a5/evaluate
/a7/evaluate
```

The review surface now uses one durable path shape:

```text
POST /axioms/{axiom_id}
```

Allowed v0.1 `axiom_id` values are `A1`, `A3`, `A4`, `A5`, and `A7`. A2 is deferred to `/verdict` and issue #82. A6 is deferred to issue #83.

### Session schema naming

The reduced connector-safe session schema is now named:

```text
experimental_session_core.v0_1.schema.yaml
```

The previous path, `experimental_session.v0_1.schema.yaml`, is retained only as a deprecated alias. It must not be treated as the complete experimental-session contract.

### A7 result field

The A7 result field formerly named `p_value` is now:

```text
nonincrease_indicator
```

Reason: the current implementation returns a provisional threshold indicator, not a statistical p-value. A future tranche should replace this with an OLS t-statistic or bootstrap significance calculation before A7 is treated as a statistical inference surface.
