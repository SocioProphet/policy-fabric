from __future__ import annotations

import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / '.policy-fabric/github_publish.json'
JSON_OUT = ROOT / 'docs/reports/github_publish_prep_latest.json'
MD_OUT = ROOT / 'docs/reports/github_publish_prep_latest.md'
NOW = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def run(cmd: list[str]) -> dict[str, Any]:
    try:
        proc = subprocess.run(
            cmd,
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
            timeout=20,
        )
        return {
            'ok': proc.returncode == 0,
            'returncode': proc.returncode,
            'stdout': proc.stdout.strip(),
            'stderr': proc.stderr.strip(),
        }
    except Exception as exc:  # pragma: no cover
        return {
            'ok': False,
            'returncode': None,
            'stdout': '',
            'stderr': str(exc),
        }


contract = json.loads(CONTRACT_PATH.read_text())
checks: list[dict[str, Any]] = []


def add(check_id: str, status: str, severity: str, code: str, message: str, artifact_ref: str | None = None, details: dict[str, Any] | None = None) -> None:
    item = {
        'id': check_id,
        'status': status,
        'severity': severity,
        'code': code,
        'message': message,
    }
    if artifact_ref:
        item['artifactRef'] = artifact_ref
    if details:
        item['details'] = details
    checks.append(item)


def git_out(*args: str) -> dict[str, Any]:
    return run(['git', *args])


# Contract presence and basic shape
required_keys = {'owner', 'repoName', 'visibility', 'defaultBranch', 'remoteName', 'publishMode', 'requiredRepoSurfaces'}
missing_keys = sorted(required_keys - set(contract))
if not missing_keys:
    add('contract:shape', 'pass', 'info', 'PFG001_CONTRACT_OK', 'GitHub publish contract has required keys', '.policy-fabric/github_publish.json')
else:
    add('contract:shape', 'fail', 'error', 'PFG002_CONTRACT_INVALID', f'missing contract keys: {missing_keys}', '.policy-fabric/github_publish.json')

# Required files
missing_surfaces = [p for p in contract.get('requiredRepoSurfaces', []) if not (ROOT / p).exists()]
if not missing_surfaces:
    add('surface:required-files', 'pass', 'info', 'PFG010_REQUIRED_SURFACES_OK', 'required GitHub-facing surfaces are present', '.policy-fabric/github_publish.json')
else:
    add('surface:required-files', 'fail', 'error', 'PFG011_REQUIRED_SURFACES_MISSING', f'missing required surfaces: {missing_surfaces}', '.policy-fabric/github_publish.json')

# Git status / branch / tags / remotes
branch = git_out('branch', '--show-current')
status = git_out('status', '--porcelain')
remotes = git_out('remote', '-v')
tags = git_out('tag', '--list', 'baseline/*')

if branch['ok'] and branch['stdout']:
    add('git:branch', 'pass', 'info', 'PFG020_BRANCH_OK', f'current branch is `{branch["stdout"]}`', details={'branch': branch['stdout']})
else:
    add('git:branch', 'fail', 'error', 'PFG021_BRANCH_UNKNOWN', 'unable to resolve current git branch', details=branch)

if status['ok']:
    clean = not bool(status['stdout'])
    add('git:worktree-clean', 'pass' if clean else 'warn', 'info' if clean else 'warn', 'PFG022_WORKTREE_CLEAN' if clean else 'PFG023_WORKTREE_DIRTY', 'working tree is clean for publication prep' if clean else 'working tree is dirty; publish only after review or commit', details={'stdout': status['stdout'][:1000]})
else:
    add('git:worktree-clean', 'fail', 'error', 'PFG024_WORKTREE_CHECK_FAILED', 'unable to inspect git worktree status', details=status)

if remotes['ok'] and remotes['stdout']:
    add('git:remote', 'pass', 'info', 'PFG025_REMOTE_PRESENT', 'git remote already configured', details={'stdout': remotes['stdout']})
else:
    add('git:remote', 'warn', 'warn', 'PFG026_REMOTE_MISSING', 'no git remote configured yet; expected before first push', details={'stdout': remotes.get('stdout', ''), 'stderr': remotes.get('stderr', '')})

if tags['ok'] and tags['stdout']:
    add('git:baseline-tags', 'pass', 'info', 'PFG027_BASELINE_TAGS_PRESENT', 'baseline tags are present', details={'stdout': tags['stdout']})
else:
    add('git:baseline-tags', 'warn', 'warn', 'PFG028_BASELINE_TAGS_MISSING', 'no baseline tags found for publish prep', details={'stdout': tags.get('stdout', ''), 'stderr': tags.get('stderr', '')})

# GitHub CLI availability
which_gh = shutil.which('gh')
if which_gh:
    gh_version = run(['gh', '--version'])
    add('tool:gh', 'pass', 'info', 'PFG030_GH_OK', 'GitHub CLI available for repo bootstrap', details={'path': which_gh, 'stdout': gh_version.get('stdout', '')})
else:
    add('tool:gh', 'warn', 'warn', 'PFG031_GH_MISSING', 'GitHub CLI not available in current environment; use web UI + git remote path or install gh', details={'path': ''})

# License readiness
license_decision = contract.get('licenseDecision', {})
license_status = license_decision.get('status')
visibility = contract.get('visibility')
if license_status == 'pending' and visibility == 'private':
    add('policy:license-private-safe', 'pass', 'info', 'PFG040_LICENSE_PRIVATE_OK', 'license is pending but private publication is allowed by contract', '.policy-fabric/github_publish.json')
elif license_status == 'pending' and visibility != 'private':
    add('policy:license-private-safe', 'fail', 'error', 'PFG041_LICENSE_PUBLIC_BLOCK', 'public publication is blocked while license is pending', '.policy-fabric/github_publish.json')
else:
    add('policy:license-private-safe', 'pass', 'info', 'PFG042_LICENSE_READY', 'license policy allows the configured visibility', '.policy-fabric/github_publish.json')

# Publishing command previews
commands = contract.get('recommendedCommands', {})
command_preview = {k: v for k, v in commands.items() if v}
add('commands:preview', 'pass', 'info', 'PFG050_COMMANDS_READY', 'publish command previews are available', '.policy-fabric/github_publish.json', details=command_preview)

fail_count = sum(1 for c in checks if c['status'] == 'fail')
warn_count = sum(1 for c in checks if c['status'] == 'warn')
overall = 'fail' if fail_count else 'warn' if warn_count else 'pass'

report = {
    'apiVersion': 'policy.fabric.github-publish-report/v1',
    'kind': 'GitHubPublishPrepReport',
    'metadata': {
        'generatedAt': NOW,
        'generator': 'policy-fabric-github-publish-prep/0.1.0',
    },
    'subject': {
        'type': 'repository',
        'ref': '.',
        'owner': contract.get('owner'),
        'repoName': contract.get('repoName'),
    },
    'summary': {
        'status': overall,
        'checkCount': len(checks),
        'failCount': fail_count,
        'warnCount': warn_count,
        'recommendedVisibility': visibility,
        'nextAction': 'Create or configure the remote, then push the current baseline using the command preview in the report.' if not remotes.get('stdout') else 'Verify remote settings, then open the first low-risk bootstrap PR.',
    },
    'checks': checks,
    'commandPreview': command_preview,
}

JSON_OUT.write_text(json.dumps(report, indent=2) + '\n')

lines = [
    '# GitHub publish prep report',
    '',
    f'- Generated at: `{NOW}`',
    f'- Target owner/repo: `{contract.get("owner")}/{contract.get("repoName")}`',
    f'- Visibility: `{visibility}`',
    f'- Status: `{overall}`',
    '',
    '## Highlights',
    '',
]
for item in checks:
    marker = {'pass': '✅', 'warn': '⚠️', 'fail': '❌'}.get(item['status'], '•')
    lines.append(f'- {marker} `{item["code"]}` — {item["message"]}')
    if item.get('artifactRef'):
        lines.append(f'  - Artifact: `{item["artifactRef"]}`')
    details = item.get('details') or {}
    if details:
        preview = []
        for key in ('branch', 'path', 'stdout', 'stderr'):
            value = details.get(key)
            if value:
                preview.append(f'{key}={value}')
        if preview:
            lines.append('  - ' + '; '.join(preview[:3]))

lines.extend([
    '',
    '## Command preview',
    '',
    '### GitHub CLI',
    '',
    '```bash',
    command_preview.get('ghCli', ''),
    '```',
    '',
    '### Manual remote path',
    '',
    '```bash',
    command_preview.get('manualRemote', ''),
    '```',
    '',
    '## Next action',
    '',
    report['summary']['nextAction'],
])
MD_OUT.write_text('\n'.join(lines) + '\n')
print(json.dumps(report['summary'], indent=2))
