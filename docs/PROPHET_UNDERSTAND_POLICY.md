# Prophet Understand Policy Gates

## Purpose

Policy Fabric evaluates Prophet Understand / Repo Intelligence v0 artifacts for schema validity, provenance completeness, source-anchor coverage, freshness, and PR impact risk.

The policy lane must make graph trust explicit. Missing, stale, invalid, or inferred graph facts are not silently ignored.

## Canonical artifact

```text
.prophet/prophet-understanding.json
```

Normative platform contract:

```text
SocioProphet/prophet-platform/schemas/repo-intelligence/prophet-understanding.schema.json
```

## Policy states

- `allow`: artifact is valid enough for the requested use.
- `warn`: artifact can be used for advisory context, but gaps exist.
- `require_review`: human review is required before relying on the graph for scope or impact.
- `deny`: artifact or behavior is unsafe for the requested use.
- `unknown`: policy could not determine trust state.

## Required checks

- `graph.artifact.present`: artifact exists at the expected path.
- `graph.schema.valid`: artifact validates against the v0 schema.
- `graph.commit.fresh`: artifact commit matches or is explicitly tied to the target ref.
- `graph.node.stable_ids`: node IDs are stable and do not include host paths or timestamps.
- `graph.edge.valid_endpoints`: every edge references existing source and target nodes.
- `graph.source_anchor.coverage`: factual non-directory nodes carry source anchors unless marked inferred.
- `graph.provenance.coverage`: nodes, edges, summaries, tours, and diff impacts carry provenance receipt references.
- `graph.policy.receipts`: policy checks cite evidence receipt IDs.
- `graph.diff.impact_radius`: high impact radius requires human review.
- `graph.hook.reviewed`: post-commit hooks or local file-serving surfaces require explicit review.
- `graph.secret_paths.skipped`: secret-like paths are skipped and reported, not indexed as content.

## v0 default posture

In v0, missing graph artifacts should usually produce `warn` or `require_review`, not universal hard failure. High-risk paths and unsafe behaviors may still produce `deny`.

## Policy receipt shape

A policy receipt should include:

- policy check ID
- artifact hash
- repo and commit
- decision state
- severity
- evidence receipt IDs
- affected node IDs where applicable
- remediation text

## Non-goals

- Graph artifacts do not override branch protection.
- Graph artifacts do not grant mutation authority.
- Policy Fabric does not generate the graph.
- Policy Fabric does not treat inferred facts as authoritative evidence.
