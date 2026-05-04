# Diff Hygiene Gate v0

Date: 2026-05-04  
Status: Proposed  
Owning repo: `SocioProphet/policy-fabric`  
Tracking issue: `SocioProphet/policy-fabric#44`  
Paired execution issue: `SocioProphet/agentplane#82`  
Paired execution PR: `SocioProphet/agentplane#84`

## Purpose

Diff Hygiene Gate v0 is the pre-review and pre-merge policy check for agent-produced pull requests. Its job is to reject obviously unsafe or overbroad diffs before semantic review time is spent.

Passing tests is not sufficient. A pull request can pass CI and still be unacceptable if it commits a virtual environment, generated dependency tree, local cache, binary blob, secret-bearing file, stale branch, or unrelated product-surface mutation.

Policy Fabric owns this rule surface because it is the governance layer for repo-local rules, ownership contracts, validation gates, release expectations, and reviewable policy evidence.

## Gate placement

The gate runs twice:

1. **Pre-review** — before reviewer-agent semantic review.
2. **Pre-merge** — immediately before merge, using the expected head SHA.

```text
Issue Work Order
  -> AgentPlane Draft PR
  -> Diff Hygiene Gate
  -> Reviewer Agent
  -> CI / Status Checks
  -> Diff Hygiene Gate at expected head SHA
  -> Merge Gate
  -> Ledger
```

## Required inputs

The gate consumes these inputs when available:

- issue-scoped work order, preferably `AgenticPRWorkOrder` from AgentPlane;
- repository full name;
- base branch and base SHA;
- PR head branch and head SHA;
- changed file list;
- additions, deletions, and changed-file count;
- PR body sections;
- validation commands and outcomes;
- allowed paths;
- denied paths;
- maximum changed-file count and allowance;
- issue-authorized exceptions;
- CI/status-check summary;
- review status.

The gate must fail closed when required policy inputs are missing at merge time. It may emit warnings for missing optional context at pre-review time.

## Verdict model

The gate emits one overall verdict and per-rule findings.

| Verdict | Meaning |
|---|---|
| `allow` | No hard blockers were found. The PR may proceed to semantic review or merge-gate evaluation. |
| `warn` | No hard blocker was found, but a reviewer should inspect a non-fatal risk or missing optional evidence. |
| `block` | A hard blocker was found. The PR must not proceed until remediated. |
| `needs_exception` | The PR violates a normal rule but may proceed only if the issue contract explicitly authorizes the exception. |

A reviewer approval cannot override a `block` verdict. A `needs_exception` verdict requires explicit issue-level or policy-level authorization before merge.

## Hard blockers

### 1. File-count overrun

Block when:

```text
changed_files > max_changed_files + changed_file_allowance
```

The allowed file count must come from the issue work order, policy default, or repo-specific override.

### 2. Denied generated paths

Block any changed file under known generated or local-environment paths unless explicitly authorized.

Default denied path prefixes include:

- `.venv/`
- `.venv-tools/`
- `venv/`
- `env/`
- `node_modules/`
- `.mypy_cache/`
- `.pytest_cache/`
- `__pycache__/`
- `.ruff_cache/`
- `.tox/`
- `.nox/`
- `.cache/`
- `dist/`
- `build/`
- `target/`
- package-manager cache directories

### 3. Binary and blob discipline

Block binary files, archive files, media blobs, database files, model weights, or opaque generated artifacts unless the work order explicitly allows them.

### 4. Secret-bearing files

Block likely secret-bearing files, including private keys, local environment files, credential files, token dumps, cloud config dumps, and unredacted authentication artifacts.

The gate is not a complete secret scanner. It is a first-line merge-policy blocker that must be paired with dedicated secret scanning where available.

### 5. Scope-path violation

Block changed files outside `allowedPaths` unless the work order or policy exception explicitly permits them.

### 6. Unrelated product-surface mutation

Block broad rewrites, formatting sweeps, unrelated product changes, dependency churn, or generated artifact refreshes when they are not part of the issue contract.

### 7. Missing review-readiness evidence

Block or warn, depending on lane strictness, when the PR body lacks required sections:

- summary;
- changed files;
- validation evidence;
- known gaps;
- self-critique;
- linked issue;
- policy evidence.

For merge, missing validation evidence is a blocker.

### 8. Stale branch or unknown head SHA

Block merge when:

- branch is behind required base policy;
- expected head SHA is absent;
- PR head moved after review or policy evaluation;
- merge gate cannot prove that the reviewed commit equals the merge candidate.

## Warnings

Warnings should not block pre-review by default, but they should appear in the report.

Examples:

- schema added without validator in a spec-only tranche;
- docs added without index wiring when explicitly deferred;
- validation command not runnable in the current connector environment;
- large additive documentation file that is still inside issue scope;
- policy input missing at pre-review but required before merge.

## Exceptions

An exception is valid only when all of these are true:

1. the work order or issue explicitly names the exception;
2. the PR body repeats the exception rationale;
3. the report records the exception under `exceptionsUsed`;
4. the merge gate evaluates the exact head SHA that used the exception.

Reviewer approval alone is not an exception.

## Output artifact

The gate emits a `DiffHygieneGateReport`.

The report should include:

- `apiVersion`;
- `kind`;
- metadata with repo, PR, base SHA, head SHA, issue ref, and generated timestamp;
- overall verdict;
- lane (`pre-review` or `pre-merge`);
- changed-file summary;
- rule findings;
- required PR-body sections and presence status;
- exceptions used;
- required follow-up actions.

## AgentPlane integration

AgentPlane owns the issue-to-draft-PR execution lifecycle. Policy Fabric owns the policy verdict. The AgentPlane `AgenticPRWorkOrder` gives this gate the expected file count, allowed paths, denied paths, required validation commands, output sections, and ledger fields.

The first integration path is:

```text
AgentPlane AgenticPRWorkOrder
  -> agent draft PR
  -> Policy Fabric DiffHygieneGateReport
  -> reviewer-agent decision
  -> merge-gate decision
  -> AgentPlane / SocioSphere ledger view
```

## Minimum v0 acceptance

A useful v0 gate must be able to distinguish these cases:

| Case | Expected verdict |
|---|---|
| Three-file docs/schema/example PR inside issue scope | `allow` or `warn` |
| PR containing `.venv-tools/` | `block` |
| PR containing `node_modules/` | `block` |
| PR changing 1,000 files for a 3-file issue | `block` |
| PR lacking expected head SHA at merge | `block` |
| PR with issue-authorized generated fixture refresh | `needs_exception` until exception is confirmed |

## Non-goals

- This v0 spec does not implement a complete secret scanner.
- This v0 spec does not replace semantic review.
- This v0 spec does not authorize implementation agents to merge their own work.
- This v0 spec does not define every repository-specific allowlist.
- This v0 spec does not claim production completeness.

## Backlog

- Add a validator for `DiffHygieneGateReport` examples.
- Wire the gate into GitHub Actions for agent-produced PRs.
- Add repo-specific policy overlays for generated artifacts.
- Add structured import of AgentPlane `AgenticPRWorkOrder`.
- Add Global DevSecOps anti-pattern classifiers as advisory findings.
- Emit merge-ledger records after the pre-merge gate passes.
