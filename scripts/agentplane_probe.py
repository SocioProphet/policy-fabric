from __future__ import annotations

import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
NOW = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
BRIDGE_PATH = ROOT / '.policy-fabric/agentplane_bridge.json'
JSON_OUT = ROOT / 'docs/reports/agentplane_probe_latest.json'
MD_OUT = ROOT / 'docs/reports/agentplane_probe_latest.md'


def run(cmd: list[str], timeout: int = 20) -> dict[str, Any]:
    try:
        proc = subprocess.run(
            cmd,
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
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


bridge = json.loads(BRIDGE_PATH.read_text())

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


add(
    'bridge-contract:present',
    'pass' if BRIDGE_PATH.exists() else 'fail',
    'info' if BRIDGE_PATH.exists() else 'error',
    'PFA001_BRIDGE_CONTRACT_PRESENT' if BRIDGE_PATH.exists() else 'PFA002_BRIDGE_CONTRACT_MISSING',
    'AgentPlane bridge contract present' if BRIDGE_PATH.exists() else 'AgentPlane bridge contract missing',
    '.policy-fabric/agentplane_bridge.json',
)

node = run(['node', '-v'])
npm = run(['npm', '-v'])
add('prereq:node', 'pass' if node['ok'] else 'fail', 'info' if node['ok'] else 'error', 'PFA010_NODE_OK' if node['ok'] else 'PFA011_NODE_MISSING', 'node available for official AgentPlane prerequisite check' if node['ok'] else 'node unavailable', details={'stdout': node['stdout'], 'stderr': node['stderr']})
add('prereq:npm', 'pass' if npm['ok'] else 'fail', 'info' if npm['ok'] else 'error', 'PFA012_NPM_OK' if npm['ok'] else 'PFA013_NPM_MISSING', 'npm available for official AgentPlane prerequisite check' if npm['ok'] else 'npm unavailable', details={'stdout': npm['stdout'], 'stderr': npm['stderr']})

agentplane_on_path = shutil.which('agentplane')
add('cli:on-path', 'pass' if agentplane_on_path else 'warn', 'info' if agentplane_on_path else 'warn', 'PFA020_CLI_ON_PATH' if agentplane_on_path else 'PFA021_CLI_NOT_ON_PATH', 'agentplane executable on PATH' if agentplane_on_path else 'agentplane executable not on PATH in current container', details={'path': agentplane_on_path or ''})

npm_view = run(['npm', 'view', 'agentplane', 'version'])
add(
    'cli:npm-view',
    'pass' if npm_view['ok'] and npm_view['stdout'] else 'warn',
    'info' if npm_view['ok'] and npm_view['stdout'] else 'warn',
    'PFA022_PACKAGE_VISIBLE' if npm_view['ok'] and npm_view['stdout'] else 'PFA023_PACKAGE_VIEW_BLOCKED',
    'npm package metadata for agentplane is visible in the current container' if npm_view['ok'] and npm_view['stdout'] else 'npm package metadata for agentplane could not be resolved in the current container',
    details={'stdout': npm_view['stdout'], 'stderr': npm_view['stderr']},
)

npx_help = run(['npx', '-y', 'agentplane', '--help'], timeout=30)
add(
    'cli:npx-help',
    'pass' if npx_help['ok'] else 'warn',
    'info' if npx_help['ok'] else 'warn',
    'PFA024_NPX_HELP_OK' if npx_help['ok'] else 'PFA025_NPX_HELP_BLOCKED',
    'npx agentplane --help executed successfully in the current container' if npx_help['ok'] else 'npx agentplane --help did not execute cleanly in the current container',
    details={'stdout': npx_help['stdout'][:500], 'stderr': npx_help['stderr'][:500]},
)

ag = ROOT / 'AGENTS.md'
agentplane_dir = ROOT / '.agentplane'
policyfabric_dir = ROOT / '.policy-fabric'

add('surface:agents-md', 'warn' if ag.exists() else 'fail', 'warn' if ag.exists() else 'error', 'PFA030_ROOT_GATEWAY_COLLISION' if ag.exists() else 'PFA031_ROOT_GATEWAY_MISSING', 'AGENTS.md already exists and is the main collision point with official AgentPlane init' if ag.exists() else 'AGENTS.md missing from Policy Fabric control repo', 'AGENTS.md')
add('surface:policy-fabric', 'pass' if policyfabric_dir.exists() else 'fail', 'info' if policyfabric_dir.exists() else 'error', 'PFA032_POLICY_FABRIC_SURFACE_PRESENT' if policyfabric_dir.exists() else 'PFA033_POLICY_FABRIC_SURFACE_MISSING', '.policy-fabric workflow surface present' if policyfabric_dir.exists() else '.policy-fabric workflow surface missing', '.policy-fabric/')
add('surface:agentplane-dir', 'info' if not agentplane_dir.exists() else 'warn', 'info' if not agentplane_dir.exists() else 'warn', 'PFA034_AGENTPLANE_SURFACE_ABSENT' if not agentplane_dir.exists() else 'PFA035_AGENTPLANE_SURFACE_PRESENT', 'no .agentplane tree exists yet; no mixed-state workspace is present' if not agentplane_dir.exists() else '.agentplane tree already exists and should be reviewed for ownership and drift', '.agentplane/')

# Simple collision summary from bridge contract
collisions = [finding for finding in bridge.get('currentProbeFindings', []) if finding.get('severity') in {'warn', 'error'}]
add('bridge:collision-summary', 'warn' if collisions else 'pass', 'warn' if collisions else 'info', 'PFA040_BRIDGE_COLLISIONS_IDENTIFIED' if collisions else 'PFA041_BRIDGE_COLLISION_FREE', 'bridge contract identifies collisions or execution blockers that must be resolved before official init' if collisions else 'bridge contract reports no current collisions', '.policy-fabric/agentplane_bridge.json', details={'count': len(collisions), 'findings': collisions})

fail_count = sum(1 for c in checks if c['status'] == 'fail')
warn_count = sum(1 for c in checks if c['status'] == 'warn')
status = 'fail' if fail_count else 'warn' if warn_count else 'pass'

report = {
    'apiVersion': 'policy.fabric.agentplane-probe/v1',
    'kind': 'AgentPlaneProbeReport',
    'metadata': {
        'generatedAt': NOW,
        'generator': 'policy-fabric-agentplane-probe/0.1.0',
    },
    'subject': {
        'type': 'repository',
        'ref': '.',
        'target': bridge.get('target', 'official-agentplane'),
        'trialMode': bridge.get('trialMode', 'unknown'),
    },
    'summary': {
        'status': status,
        'checkCount': len(checks),
        'failCount': fail_count,
        'warnCount': warn_count,
        'nextAction': bridge.get('nextAction', ''),
    },
    'checks': checks,
}

JSON_OUT.write_text(json.dumps(report, indent=2) + '\n')

lines = [
    '# AgentPlane probe report',
    '',
    f'- Generated at: `{NOW}`',
    f'- Target: `{report["subject"]["target"]}`',
    f'- Trial mode: `{report["subject"]["trialMode"]}`',
    f'- Status: `{status}`',
    f'- Checks: `{len(checks)}` total / `{fail_count}` fail / `{warn_count}` warn',
    '',
    '## Highlights',
    '',
]
for item in checks:
    prefix = {'pass': '- ✅', 'warn': '- ⚠️', 'fail': '- ❌', 'info': '- ℹ️'}.get(item['status'], '-')
    lines.append(f"{prefix} `{item['code']}` — {item['message']}")
    if item.get('artifactRef'):
        lines.append(f"  - Artifact: `{item['artifactRef']}`")
    details = item.get('details')
    if details:
        detail_parts = []
        if details.get('path'):
            detail_parts.append(f"path={details['path']}")
        if details.get('stdout'):
            detail_parts.append(f"stdout={details['stdout']}")
        if details.get('stderr'):
            detail_parts.append(f"stderr={details['stderr']}")
        if details.get('count') is not None:
            detail_parts.append(f"count={details['count']}")
        if detail_parts:
            lines.append('  - ' + '; '.join(detail_parts[:3]))
lines.extend(['', '## Next action', '', bridge.get('nextAction', '')])
MD_OUT.write_text('\n'.join(lines) + '\n')
print(json.dumps(report['summary'], indent=2))
