# GitHub publish prep report

- Generated at: `2026-04-05T01:11:09.276766Z`
- Target owner/repo: `SocioProphet/policy-fabric-control-repository`
- Visibility: `private`
- Status: `warn`

## Highlights

- ✅ `PFG001_CONTRACT_OK` — GitHub publish contract has required keys
  - Artifact: `.policy-fabric/github_publish.json`
- ✅ `PFG010_REQUIRED_SURFACES_OK` — required GitHub-facing surfaces are present
  - Artifact: `.policy-fabric/github_publish.json`
- ✅ `PFG020_BRANCH_OK` — current branch is `main`
  - branch=main
- ⚠️ `PFG023_WORKTREE_DIRTY` — working tree has non-generated changes; publish only after review or commit
  - stdout=M .policy-fabric/reports/doctor_latest.json
 M scripts/branch_audit.py
 M scripts/github_publish_prep.py
- ⚠️ `PFG026_REMOTE_MISSING` — no git remote configured yet; expected before first push
- ✅ `PFG027_BASELINE_TAGS_PRESENT` — baseline tags are present
  - stdout=baseline/2026-04-02_pre-branch-audit
baseline/2026-04-04_branch-audited
baseline/2026-04-05_docs-github-prep-validated
baseline/2026-04-05_post-github-publish-prep
baseline/2026-04-05_pre-github-publish-prep
- ⚠️ `PFG031_GH_MISSING` — GitHub CLI not available in current environment; use web UI + git remote path or install gh
- ✅ `PFG040_LICENSE_PRIVATE_OK` — license is pending but private publication is allowed by contract
  - Artifact: `.policy-fabric/github_publish.json`
- ✅ `PFG050_COMMANDS_READY` — publish command previews are available
  - Artifact: `.policy-fabric/github_publish.json`

## Command preview

### GitHub CLI

```bash
gh repo create SocioProphet/policy-fabric-control-repository --private --source . --remote origin --push --description "Control repository for Policy Fabric contracts, examples, workflow governance, and promotion artifacts."
```

### Manual remote path

```bash
git remote add origin git@github.com:SocioProphet/policy-fabric-control-repository.git && git push -u origin main --follow-tags
```

## Next action

Create or configure the remote, then push the current baseline using the command preview in the report.
