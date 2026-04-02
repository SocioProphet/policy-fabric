# Running Backlog

1. Deepen selector-overlap analysis beyond exact-path identity into true semantic overlap heuristics for JSONPath/XPath/regex selectors.
2. Add deterministic error taxonomy coverage across compile, explain, and runtime surfaces, not just doctor and semantic validation.
3. Add stronger policy test DSL assertions, including shape, regex, exact hit counts, expected failures, and negative fixture classification.
4. Add semantic diffing between policy versions, capability catalogs, and release packs.
5. Add signed release bundles with provenance metadata.
6. Add corpus replay packs and impact analysis for rollout review.
7. Add region-aware provider resolution and trust-boundary constraints at compile/runtime, not just repo validation.
8. Add execution-receipt and release-receipt schemas.
9. Decide whether release-pack lifecycle belongs only in repo-native tooling or also in OpenAPI.
10. Add stricter release-gated profile enforcement once the repo leaves active design mode.
11. Evaluate official AgentPlane initialization in a disposable clone and record the generated surface map.
12. Decide the long-term bridge model between `AGENTS.md`/`.agentplane/` and `.policy-fabric/`.
13. If AgentPlane is adopted, update ownership and doctor to make `.agentplane/` surfaces explicit and enforced.
