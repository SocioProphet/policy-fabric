from __future__ import annotations

import fnmatch
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOW = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def git(*args: str) -> str:
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()


def git_lines(*args: str) -> list[str]:
    out = git(*args)
    return [line for line in out.splitlines() if line.strip()]


def ref_exists(ref: str) -> bool:
    try:
        subprocess.check_call(
            ['git', 'rev-parse', '-q', '--verify', ref],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def state_file(name: str) -> bool:
    return (ROOT / '.git' / name).exists()


def matches_any(path_str: str, patterns: list[str]) -> bool:
    for pattern in patterns:
        if fnmatch.fnmatch(path_str, pattern):
            return True
        if pattern.endswith('/**') and path_str.startswith(pattern[:-3]):
            return True
    return False


policy = json.loads((ROOT / '.policy-fabric' / 'branch_policy.json').read_text())
ownership = json.loads((ROOT / '.policy-fabric' / 'ownership.json').read_text())
noise_patterns = ownership.get('generatedPaths', []) + ownership.get('localOverridePaths', [])
current_branch = git('rev-parse', '--abbrev-ref', 'HEAD')
detached = current_branch == 'HEAD'
status_lines = git_lines('status', '--porcelain')
relevant_status_lines = []
for line in status_lines:
    path_part = line[3:].strip() if len(line) > 3 else ''
    if ' -> ' in path_part:
        path_part = path_part.split(' -> ', 1)[1]
    if matches_any(path_part, noise_patterns):
        continue
    relevant_status_lines.append(line)
clean = not bool(relevant_status_lines)

local_branches: list[str] = []
for line in git_lines('branch', '-vv'):
    if line.startswith('* '):
        local_branches.append(line.split()[1])
    else:
        local_branches.append(line.strip().split()[0])

remotes = git_lines('remote') if ref_exists('HEAD') else []
merge_states = {
    'MERGE_HEAD': state_file('MERGE_HEAD'),
    'REBASE_HEAD': state_file('REBASE_HEAD'),
    'CHERRY_PICK_HEAD': state_file('CHERRY_PICK_HEAD'),
    'REVERT_HEAD': state_file('REVERT_HEAD'),
}
merge_state_active = any(merge_states.values())

recent_commits = []
for line in git_lines(
    'log', '--decorate=short', '--pretty=format:%H%x09%h%x09%ad%x09%s', '--date=iso', '-n', '12'
):
    full, short, date_s, subj = line.split('\t', 3)
    recent_commits.append({'rev': short, 'fullRev': full, 'date': date_s, 'subject': subj})

merge_commit_count = int(git('rev-list', '--count', '--merges', 'HEAD'))
recent_graph = git_lines('log', '--graph', '--decorate', '--oneline', '-n', '20', '--all')
tags = git_lines('tag', '--list', 'baseline/*')

checks = []


def add(check_id: str, status: str, code: str, message: str) -> None:
    checks.append({'id': check_id, 'status': status, 'code': code, 'message': message})


if not detached:
    add('branch:head-attached', 'pass', 'PFB010_BRANCH_HEAD_OK', f'HEAD is attached to `{current_branch}`')
else:
    add('branch:head-attached', 'fail', 'PFB011_BRANCH_HEAD_DETACHED', 'HEAD is detached')

if not merge_state_active:
    add('branch:merge-state', 'pass', 'PFB012_BRANCH_STATE_OK', 'No in-progress merge/rebase/cherry-pick/revert state detected')
else:
    active = [k for k, v in merge_states.items() if v]
    add('branch:merge-state', 'fail', 'PFB013_BRANCH_STATE_DIRTY', f'In-progress git state detected: {active}')

if 'main' in local_branches:
    add('branch:main-present', 'pass', 'PFB014_BRANCH_MAIN_PRESENT', '`main` branch exists')
else:
    add('branch:main-present', 'fail', 'PFB015_BRANCH_MAIN_MISSING', '`main` branch missing')

if len(local_branches) == 1 and local_branches == ['main']:
    add(
        'branch:single-main-only',
        'warn',
        'PFB016_BRANCH_LINEAR_BOOTSTRAP',
        'Only `main` exists; safe from divergence, but risky for upcoming high-risk changes',
    )
else:
    add('branch:single-main-only', 'pass', 'PFB017_BRANCH_TOPOLOGY_OK', f'Local branches present: {local_branches}')

if remotes:
    add('branch:remotes', 'pass', 'PFB018_BRANCH_REMOTE_PRESENT', f'Remotes configured: {remotes}')
else:
    add('branch:remotes', 'warn', 'PFB019_BRANCH_NO_REMOTE', 'No remotes configured in snapshot; remote protection cannot be observed here')

if merge_commit_count == 0:
    add(
        'branch:merge-history',
        'warn',
        'PFB020_BRANCH_LINEAR_HISTORY',
        'History is fully linear so far; keep baseline tags and use work branches for risky changes',
    )
else:
    add('branch:merge-history', 'pass', 'PFB021_BRANCH_MERGE_HISTORY_PRESENT', f'History contains {merge_commit_count} merge commits')

if tags:
    add('branch:baseline-tags', 'pass', 'PFB022_BRANCH_BASELINE_TAGS_OK', f'Baseline tags present: {tags}')
else:
    add('branch:baseline-tags', 'warn', 'PFB023_BRANCH_BASELINE_TAGS_MISSING', 'No baseline tags present')

if policy.get('protectedBranches') == ['main']:
    add('branch:policy-protected-main', 'pass', 'PFB024_BRANCH_POLICY_OK', 'Branch policy protects `main` as the baseline branch')
else:
    add(
        'branch:policy-protected-main',
        'warn',
        'PFB025_BRANCH_POLICY_DRIFT',
        f"Protected branches differ from expected bootstrap baseline: {policy.get('protectedBranches')}",
    )

summary_status = 'pass'
if any(c['status'] == 'fail' for c in checks):
    summary_status = 'fail'
elif any(c['status'] == 'warn' for c in checks):
    summary_status = 'warn'

report = {
    'apiVersion': 'policy.fabric.branch-audit/v1',
    'kind': 'BranchAuditReport',
    'metadata': {'generatedAt': NOW, 'generator': 'policy-fabric-branch-audit/0.1.0'},
    'summary': {
        'status': summary_status,
        'currentBranch': current_branch,
        'cleanWorktree': clean,
        'ignoredDirtyPaths': [line[3:].strip() if len(line) > 3 else '' for line in status_lines if line not in relevant_status_lines],
        'localBranchCount': len(local_branches),
        'remoteCount': len(remotes),
        'mergeCommitCount': merge_commit_count,
    },
    'topology': {
        'localBranches': local_branches,
        'remotes': remotes,
        'mergeStates': merge_states,
        'baselineTags': tags,
        'recentGraph': recent_graph,
        'recentCommits': recent_commits,
    },
    'recommendations': policy.get('nextRecommendedBranches', []),
    'checks': checks,
}

out_json = ROOT / 'docs' / 'reports' / 'branch_audit_latest.json'
out_md = ROOT / 'docs' / 'reports' / 'branch_audit_latest.md'
out_json.write_text(json.dumps(report, indent=2) + '\n')

lines = [
    '# Branch Audit Report',
    '',
    f'Overall status: {summary_status.upper()}',
    '',
    f'Current branch: `{current_branch}`',
    f'Local branches: `{len(local_branches)}`',
    f'Remotes: `{len(remotes)}`',
    f'Merge commits in history: `{merge_commit_count}`',
    '',
]
for item in checks:
    marker = 'OK' if item['status'] == 'pass' else ('WARN' if item['status'] == 'warn' else 'FAIL')
    lines.append(f"- [{marker}] {item['id']} — {item['code']} — {item['message']}")
lines += ['', '## Recommended Next Work Branches', '']
for rec in policy.get('nextRecommendedBranches', []):
    lines.append(f"- `{rec['name']}` — {rec['purpose']}")
out_md.write_text('\n'.join(lines) + '\n')

print(json.dumps(report, indent=2))
raise SystemExit(0 if summary_status != 'fail' else 1)
