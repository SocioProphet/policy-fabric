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
11. Re-run official AgentPlane initialization in a disposable clone from an environment where npm package execution works, then record the generated surface map.
12. Keep the new hybrid bridge model explicit between `AGENTS.md`/`.agentplane/` and `.policy-fabric/`.
13. If AgentPlane is adopted, update ownership and doctor to make `.agentplane/` surfaces explicit and enforced.
14. Add bridge-aware reconcile behavior once a real `.agentplane/` tree exists.

- Implement branch safety and evaluate recent branch topology.

- Add real GitHub remote, branch protection/rulesets, and CODEOWNERS ownership after the first private publish.
- Run the first low-risk GitHub bootstrap PR before the first official AgentPlane init.
