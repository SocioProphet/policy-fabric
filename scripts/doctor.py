from __future__ import annotations

import fnmatch
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import jsonschema
    import yaml
    from policy_semantic_validator import collect_policy_semantic_findings
except Exception as exc:  # pragma: no cover
    print(f"dependency error: {exc}", file=sys.stderr)
    raise

ROOT = Path(__file__).resolve().parents[1]
NOW = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

try:
    CURRENT_REV = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'], cwd=ROOT, text=True).strip()
    CURRENT_DIRTY = bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip())
except Exception:
    CURRENT_REV = 'UNKNOWN'
    CURRENT_DIRTY = True

report = {
    'apiVersion': 'policy.fabric.validation/v1',
    'kind': 'ValidationReport',
    'metadata': {
        'generatedAt': NOW,
        'generator': 'policy-fabric-doctor/0.5.0',
        'runId': f'doctor-{NOW}',
    },
    'subject': {
        'type': 'releasePack',
        'ref': 'examples/policy_fabric_release_pack_example.json',
        'version': '1.0.0',
    },
    'summary': {
        'status': 'pass',
        'checkCount': 0,
        'failCount': 0,
        'warnCount': 0,
    },
    'checks': [],
}


def add(check_id: str, status: str, severity: str, code: str, message: str, artifact_ref: str | None = None) -> None:
    item = {
        'id': check_id,
        'status': status,
        'severity': severity,
        'code': code,
        'message': message,
    }
    if artifact_ref:
        item['artifactRef'] = artifact_ref
    report['checks'].append(item)


def ok(check_id: str, code: str, message: str, artifact_ref: str | None = None) -> None:
    add(check_id, 'pass', 'info', code, message, artifact_ref)


def warn(check_id: str, code: str, message: str, artifact_ref: str | None = None) -> None:
    add(check_id, 'warn', 'warn', code, message, artifact_ref)


def fail(check_id: str, code: str, message: str, artifact_ref: str | None = None) -> None:
    add(check_id, 'fail', 'error', code, message, artifact_ref)


def load_json(rel: str):
    return json.loads((ROOT / rel).read_text())


def sha256_file(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def run_validator(check_id: str, command: list[str], success_message: str, artifact_ref: str) -> None:
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
    except Exception as exc:
        fail(check_id, 'PFD201_VALIDATOR_CRASH', str(exc), artifact_ref)
        return
    if completed.returncode == 0:
        ok(check_id, 'PFD200_VALIDATOR_OK', success_message, artifact_ref)
    else:
        fail(check_id, 'PFD202_VALIDATOR_FAILED', completed.stdout.strip() or f'{command} failed', artifact_ref)


required = [
    'contracts/policy_fabric_policy_v2.schema.json',
    'contracts/policy_fabric_execution_plan_ir_v1.schema.json',
    'contracts/policy_fabric_openapi_v2.yaml',
    'contracts/policy_fabric_release_pack_v1.schema.json',
    'contracts/policy_fabric_capability_catalog_v1.schema.json',
    'contracts/policy_fabric_validation_report_v1.schema.json',
    'contracts/policy_fabric_replay_report_v1.schema.json',
    'examples/policy_fabric_policy_v2_enhanced_example.json',
    'examples/policy_fabric_compiled_plan_example.json',
    'examples/policy_fabric_release_pack_example.json',
    'examples/policy_fabric_capability_catalog_example.json',
    'examples/policy_fabric_validation_report_example.json',
    'examples/policy_fabric_replay_report_example.json',
    '.policy-fabric/config.json',
    '.policy-fabric/WORKFLOW.md',
    '.policy-fabric/ownership.json',
    '.policy-fabric/profiles.json',
    '.policy-fabric/RECONCILE.md',
    '.policy-fabric/agentplane_bridge.json',
    '.policy-fabric/branch_policy.json',
    '.policy-fabric/github_publish.json',
    'AGENTS.md',
    'CONTRIBUTING.md',
    'SECURITY.md',
    '.github/PULL_REQUEST_TEMPLATE.md',
    '.github/ISSUE_TEMPLATE/bug_report.yml',
    '.github/ISSUE_TEMPLATE/feature_request.yml',
    '.github/ISSUE_TEMPLATE/config.yml',
    '.github/CODEOWNERS',
    '.github/workflows/repo_health.yml',
    'scripts/reconcile.py',
    'scripts/agentplane_probe.py',
    'scripts/branch_audit.py',
    'scripts/github_publish_prep.py',
    'contracts/operation_plane_policy_gate_v1.schema.json',
    'examples/operation_plane_policy_gate_record_example.json',
    'examples/operation_plane_policy_eval_request_example.json',
    'examples/operation_plane_policy_eval_response_example.json',
    'docs/specs/operation_plane_policy_gate_v1.md',
    'scripts/validate_operation_plane_policy_gate.py',
    'contracts/wallguard-policy-decision.v0.schema.json',
    'examples/wallguard-policy/valid.same-wall-allow.json',
    'examples/wallguard-policy/invalid.cross-wall-allow.json',
    'examples/wallguard-policy/invalid.contaminated-session-allow.json',
    'tools/validate_wallguard_policy_decision.py',
]
for rel in required:
    p = ROOT / rel
    if p.exists():
        ok(f'exists:{rel}', 'PFD001_REQUIRED_FILE_PRESENT', 'required file present', rel)
    else:
        fail(f'exists:{rel}', 'PFD002_REQUIRED_FILE_MISSING', 'required file missing', rel)

pairs = [
    ('validate:policy-example', 'contracts/policy_fabric_policy_v2.schema.json', 'examples/policy_fabric_policy_v2_enhanced_example.json', 'policy example validates against policy schema'),
    ('validate:plan-example', 'contracts/policy_fabric_execution_plan_ir_v1.schema.json', 'examples/policy_fabric_compiled_plan_example.json', 'compiled plan validates against plan schema'),
    ('validate:release-pack-example', 'contracts/policy_fabric_release_pack_v1.schema.json', 'examples/policy_fabric_release_pack_example.json', 'release pack example validates against release pack schema'),
    ('validate:capability-catalog-example', 'contracts/policy_fabric_capability_catalog_v1.schema.json', 'examples/policy_fabric_capability_catalog_example.json', 'capability catalog example validates against capability catalog schema'),
    ('validate:validation-report-example', 'contracts/policy_fabric_validation_report_v1.schema.json', 'examples/policy_fabric_validation_report_example.json', 'validation report example validates against validation report schema'),
    ('validate:replay-report-example', 'contracts/policy_fabric_replay_report_v1.schema.json', 'examples/policy_fabric_replay_report_example.json', 'replay report example validates against replay report schema'),
    ('validate:operation-plane-gate-record-example', 'contracts/operation_plane_policy_gate_v1.schema.json', 'examples/operation_plane_policy_gate_record_example.json', 'operation plane gate record example validates against gate schema'),
    ('validate:operation-plane-eval-request-example', 'contracts/operation_plane_policy_gate_v1.schema.json', 'examples/operation_plane_policy_eval_request_example.json', 'operation plane eval request example validates against gate schema'),
    ('validate:operation-plane-eval-response-example', 'contracts/operation_plane_policy_gate_v1.schema.json', 'examples/operation_plane_policy_eval_response_example.json', 'operation plane eval response example validates against gate schema'),
    ('validate:wallguard-same-wall-allow', 'contracts/wallguard-policy-decision.v0.schema.json', 'examples/wallguard-policy/valid.same-wall-allow.json', 'WallGuard same-wall allow example validates against schema'),
]
for check_id, schema_rel, example_rel, message in pairs:
    try:
        jsonschema.validate(load_json(example_rel), load_json(schema_rel))
        ok(check_id, 'PFD010_SCHEMA_OK', message, example_rel)
    except Exception as exc:
        fail(check_id, 'PFD011_SCHEMA_INVALID', str(exc), example_rel)

run_validator(
    'validate:wallguard-policy-decision-semantic',
    [sys.executable, 'tools/validate_wallguard_policy_decision.py'],
    'WallGuard policy validator accepts valid fixture and rejects invalid fixtures',
    'tools/validate_wallguard_policy_decision.py',
)

try:
    spec = yaml.safe_load((ROOT / 'contracts/policy_fabric_openapi_v2.yaml').read_text())
    paths = spec.get('paths', {})
    if spec.get('openapi') == '3.1.0' and '/v2/process' in paths and '/v2/explain' in paths:
        ok('parse:openapi', 'PFD020_OPENAPI_OK', 'openapi parses and contains expected core surfaces', 'contracts/policy_fabric_openapi_v2.yaml')
    else:
        fail('parse:openapi', 'PFD021_OPENAPI_INVALID', 'openapi missing expected core surfaces', 'contracts/policy_fabric_openapi_v2.yaml')
except Exception as exc:
    fail('parse:openapi', 'PFD021_OPENAPI_INVALID', str(exc), 'contracts/policy_fabric_openapi_v2.yaml')

try:
    config = load_json('.policy-fabric/config.json')
    ownership = load_json('.policy-fabric/ownership.json')
    profiles = load_json('.policy-fabric/profiles.json')

    if set(config.get('managedPaths', [])) == set(ownership.get('managedPaths', ownership.get('frameworkManagedPaths', []))):
        ok('ownership:managed-sync', 'PFD030_OWNERSHIP_SYNC_OK', 'config managed paths match ownership contract', '.policy-fabric/config.json')
    else:
        fail('ownership:managed-sync', 'PFD031_OWNERSHIP_DRIFT', 'config managed paths drift from ownership contract', '.policy-fabric/config.json')

    if set(config.get('generatedPaths', [])) == set(ownership.get('generatedPaths', [])):
        ok('ownership:generated-sync', 'PFD030_OWNERSHIP_SYNC_OK', 'config generated paths match ownership contract', '.policy-fabric/config.json')
    else:
        fail('ownership:generated-sync', 'PFD031_OWNERSHIP_DRIFT', 'config generated paths drift from ownership contract', '.policy-fabric/config.json')

    if set(config.get('localOverridePaths', [])) == set(ownership.get('localOverridePaths', [])):
        ok('ownership:local-sync', 'PFD030_OWNERSHIP_SYNC_OK', 'config local override paths match ownership contract', '.policy-fabric/config.json')
    else:
        fail('ownership:local-sync', 'PFD031_OWNERSHIP_DRIFT', 'config local override paths drift from ownership contract', '.policy-fabric/config.json')

    profile_name = config.get('workflowProfile')
    profile_map = profiles.get('profiles', {})
    if profile_name in profile_map:
        ok('profiles:selected-profile', 'PFD040_PROFILE_OK', f'selected workflow profile `{profile_name}` exists', '.policy-fabric/profiles.json')
        if config.get('workflowMode') in profile_map[profile_name].get('allowedWorkflowModes', []):
            ok('profiles:mode-allowed', 'PFD040_PROFILE_OK', 'workflow mode allowed by selected profile', '.policy-fabric/config.json')
        else:
            fail('profiles:mode-allowed', 'PFD041_PROFILE_MODE_MISMATCH', 'workflow mode is not allowed by selected profile', '.policy-fabric/config.json')
    else:
        fail('profiles:selected-profile', 'PFD042_PROFILE_UNKNOWN', 'selected workflow profile does not exist', '.policy-fabric/profiles.json')

    workflow_text = (ROOT / '.policy-fabric/WORKFLOW.md').read_text()
    reconcile_text = (ROOT / '.policy-fabric/RECONCILE.md').read_text()
    workflow_tokens = ['ownership.json', 'profiles.json', 'scripts/reconcile.py', 'scripts/agentplane_probe.py', 'scripts/github_publish_prep.py', 'scripts/doctor.py', 'scripts/build_dist_bundle.py']
    missing_workflow_tokens = [token for token in workflow_tokens if token not in workflow_text]
    if not missing_workflow_tokens:
        ok('docs:workflow-sync', 'PFD050_DOC_SYNC_OK', 'workflow documentation references governed commands and contracts', '.policy-fabric/WORKFLOW.md')
    else:
        fail('docs:workflow-sync', 'PFD051_DOC_SYNC_DRIFT', f'workflow documentation missing tokens: {missing_workflow_tokens}', '.policy-fabric/WORKFLOW.md')

    reconcile_tokens = ['scripts/reconcile.py', 'REPO_MANIFEST.json', 'doctor', 'generated']
    missing_reconcile_tokens = [token for token in reconcile_tokens if token not in reconcile_text]
    if not missing_reconcile_tokens:
        ok('docs:reconcile-sync', 'PFD050_DOC_SYNC_OK', 'reconcile documentation references repair surfaces and commands', '.policy-fabric/RECONCILE.md')
    else:
        fail('docs:reconcile-sync', 'PFD051_DOC_SYNC_DRIFT', f'reconcile documentation missing tokens: {missing_reconcile_tokens}', '.policy-fabric/RECONCILE.md')

    agents_text = (ROOT / 'AGENTS.md').read_text()
    if config.get('branchPolicyContract') == '.policy-fabric/branch_policy.json' and config.get('branchAuditCommand') == 'python scripts/branch_audit.py':
        ok('branch-policy:config-sync', 'PFD043_BRANCH_POLICY_SYNC_OK', 'config references the branch policy contract and branch audit command', '.policy-fabric/config.json')
    else:
        fail('branch-policy:config-sync', 'PFD044_BRANCH_POLICY_SYNC_DRIFT', 'config missing branch policy contract or branch audit command', '.policy-fabric/config.json')

    if config.get('githubPublishContract') == '.policy-fabric/github_publish.json' and config.get('githubPublishPrepCommand') == 'python scripts/github_publish_prep.py':
        ok('github-publish:config-sync', 'PFD045_GITHUB_PUBLISH_SYNC_OK', 'config references the GitHub publish contract and prep command', '.policy-fabric/config.json')
    else:
        fail('github-publish:config-sync', 'PFD046_GITHUB_PUBLISH_SYNC_DRIFT', 'config missing GitHub publish contract or prep command', '.policy-fabric/config.json')

    agents_tokens = ['Policy Fabric', 'scripts/reconcile.py', 'scripts/agentplane_probe.py', 'scripts/branch_audit.py', 'scripts/github_publish_prep.py', 'scripts/doctor.py', 'scripts/build_dist_bundle.py', '.policy-fabric/WORKFLOW.md', '.policy-fabric/agentplane_bridge.json', '.policy-fabric/branch_policy.json', '.policy-fabric/github_publish.json']
    missing_agents_tokens = [token for token in agents_tokens if token not in agents_text]
    if not missing_agents_tokens:
        ok('docs:agents-gateway-sync', 'PFD050_DOC_SYNC_OK', 'AGENTS.md references the active repository workflow surfaces', 'AGENTS.md')
    else:
        fail('docs:agents-gateway-sync', 'PFD051_DOC_SYNC_DRIFT', f'AGENTS.md missing tokens: {missing_agents_tokens}', 'AGENTS.md')

    category_map = {
        'frameworkManaged': ownership.get('managedPaths', ownership.get('frameworkManagedPaths', [])),
        'generated': ownership.get('generatedPaths', []),
        'localOverride': ownership.get('localOverridePaths', []),
        'archiveProtected': ownership.get('archiveProtectedPaths', []),
    }
    overlapping = []
    unclassified = []
    for path in sorted(p for p in ROOT.rglob('*') if p.is_file()):
        rel = path.relative_to(ROOT).as_posix()
        if rel.startswith('.git/'):
            continue
        matches = [
            category
            for category, patterns in category_map.items()
            if any(fnmatch.fnmatch(rel, pattern) for pattern in patterns)
        ]
        if len(matches) > 1:
            overlapping.append({'path': rel, 'categories': matches})
        elif len(matches) == 0:
            unclassified.append(rel)
    if not overlapping:
        ok('ownership:no-overlap', 'PFD032_OWNERSHIP_OVERLAP_FREE', 'ownership categories do not overlap on actual files', '.policy-fabric/ownership.json')
    else:
        fail('ownership:no-overlap', 'PFD033_OWNERSHIP_OVERLAP', f'overlapping ownership categories found: {overlapping[:5]}', '.policy-fabric/ownership.json')
    if not unclassified:
        ok('ownership:no-unclassified', 'PFD034_OWNERSHIP_CLASSIFICATION_OK', 'all tracked files are classified by the ownership contract', '.policy-fabric/ownership.json')
    else:
        fail('ownership:no-unclassified', 'PFD035_OWNERSHIP_UNCLASSIFIED', f'unclassified files found: {unclassified[:10]}', '.policy-fabric/ownership.json')
except Exception as exc:
    fail('ownership:parse', 'PFD036_OWNERSHIP_PARSE_ERROR', str(exc), '.policy-fabric/ownership.json')

try:
    release_pack = load_json('examples/policy_fabric_release_pack_example.json')

    artifacts = [
        ('spec.policy', release_pack['spec']['policy']['artifactRef'], release_pack['spec']['policy']['sha256']),
        ('spec.plan', release_pack['spec']['plan']['artifactRef'], release_pack['spec']['plan']['sha256']),
    ]
    if 'openapi' in release_pack['spec']:
        artifacts.append(('spec.openapi', release_pack['spec']['openapi']['artifactRef'], release_pack['spec']['openapi']['sha256']))
    if 'capabilityCatalog' in release_pack['spec']:
        artifacts.append(('spec.capabilityCatalog', release_pack['spec']['capabilityCatalog']['artifactRef'], release_pack['spec']['capabilityCatalog']['sha256']))
    for fixture in release_pack['spec'].get('fixtures', []):
        artifacts.append((f"fixture:{fixture['name']}", fixture['artifactRef'], fixture['sha256']))

    digest_failures = []
    for label, ref, expected in artifacts:
        path = ROOT / ref
        if not path.exists():
            digest_failures.append(f'{label} missing {ref}')
            continue
        actual = sha256_file(ref)
        if actual != expected:
            digest_failures.append(f'{label} digest mismatch for {ref}: expected {expected}, actual {actual}')
    if not digest_failures:
        ok('release-pack:digest-integrity', 'PFD060_RELEASE_PACK_DIGEST_OK', 'release-pack artifact digests match referenced files', 'examples/policy_fabric_release_pack_example.json')
    else:
        fail('release-pack:digest-integrity', 'PFD061_RELEASE_PACK_DIGEST_MISMATCH', '; '.join(digest_failures), 'examples/policy_fabric_release_pack_example.json')

    promotion = release_pack['spec']['promotion']
    lane = promotion['lane']
    if lane != 'prod' or promotion.get('humanGateRequired') is True:
        ok('release-pack:promotion-gate', 'PFD062_PROMOTION_GATE_OK', 'promotion gate semantics satisfy current lane requirements', 'examples/policy_fabric_release_pack_example.json')
    else:
        fail('release-pack:promotion-gate', 'PFD063_PROMOTION_GATE_REQUIRED', 'prod release pack requires humanGateRequired=true', 'examples/policy_fabric_release_pack_example.json')

    evidence = release_pack['spec']['evidence']
    expected_artifacts = set(evidence.get('expectedArtifacts', []))
    replay_ok = True
    replay_msgs = []
    if evidence.get('retainReplayArtifacts'):
        if not evidence.get('replayCorpusRef'):
            replay_ok = False
            replay_msgs.append('retainReplayArtifacts=true requires replayCorpusRef')
        if 'replay-report' not in expected_artifacts:
            replay_ok = False
            replay_msgs.append('retainReplayArtifacts=true requires replay-report in expectedArtifacts')
    if replay_ok:
        ok('release-pack:replay-evidence', 'PFD064_REPLAY_EVIDENCE_OK', 'replay evidence requirements are satisfied', 'examples/policy_fabric_release_pack_example.json')
    else:
        fail('release-pack:replay-evidence', 'PFD065_REPLAY_EVIDENCE_INCOMPLETE', '; '.join(replay_msgs), 'examples/policy_fabric_release_pack_example.json')

    secret_ref_root = release_pack['spec'].get('secrets', {}).get('secretRefRoot', '')
    secret_names = release_pack['spec'].get('secrets', {}).get('required', [])
    bad_secret_names = [name for name in secret_names if not re.fullmatch(r'[A-Z0-9_]+', name)]
    if secret_ref_root.startswith('secrets://') and not bad_secret_names:
        ok('release-pack:secret-refs', 'PFD066_SECRET_REF_OK', 'release pack uses reference-style secret declarations', 'examples/policy_fabric_release_pack_example.json')
    else:
        fail('release-pack:secret-refs', 'PFD067_SECRET_REF_INVALID', f'invalid secret root or secret names: root={secret_ref_root}, bad={bad_secret_names}', 'examples/policy_fabric_release_pack_example.json')

    git_source = release_pack.get('metadata', {}).get('source', {}).get('git', {})
    if git_source.get('dirty') is False and git_source.get('rev') not in {'WORKING', CURRENT_REV}:
        warn('release-pack:git-source-drift', 'PFD068_RELEASE_PACK_GIT_DRIFT', 'release-pack git source is clean but does not match current repository rev', 'examples/policy_fabric_release_pack_example.json')
    else:
        ok('release-pack:git-source-drift', 'PFD069_RELEASE_PACK_GIT_OK', 'release-pack git source is intentionally working or matches current rev semantics', 'examples/policy_fabric_release_pack_example.json')
except Exception as exc:
    fail('release-pack:semantic-parse', 'PFD070_RELEASE_PACK_PARSE_ERROR', str(exc), 'examples/policy_fabric_release_pack_example.json')

try:
    for item in collect_policy_semantic_findings(ROOT):
        report['checks'].append(item)
except Exception as exc:
    fail('policy:semantic-validator-crash', 'PFV099', str(exc), 'scripts/policy_semantic_validator.py')


try:
    bridge = load_json('.policy-fabric/agentplane_bridge.json')
    if bridge.get('target') == 'official-agentplane' and bridge.get('bridgeModel', {}).get('type') == 'hybrid':
        ok('agentplane-bridge:contract-shape', 'PFD090_AGENTPLANE_BRIDGE_OK', 'AgentPlane bridge contract targets official AgentPlane with a hybrid bridge model', '.policy-fabric/agentplane_bridge.json')
    else:
        fail('agentplane-bridge:contract-shape', 'PFD091_AGENTPLANE_BRIDGE_INVALID', 'AgentPlane bridge contract target/model drift detected', '.policy-fabric/agentplane_bridge.json')

    current_findings = bridge.get('currentProbeFindings', [])
    ids = {item.get('id') for item in current_findings}
    required_ids = {
        'bridge-root-gateway-collision',
        'bridge-workflow-parallel-surface',
        'bridge-official-workspace-absent',
    }
    if required_ids.issubset(ids):
        ok('agentplane-bridge:expected-findings', 'PFD092_AGENTPLANE_BRIDGE_FINDINGS_OK', 'AgentPlane bridge contract records expected current-state findings', '.policy-fabric/agentplane_bridge.json')
    else:
        fail('agentplane-bridge:expected-findings', 'PFD093_AGENTPLANE_BRIDGE_FINDINGS_MISSING', f'missing bridge findings: {sorted(required_ids - ids)}', '.policy-fabric/agentplane_bridge.json')
except Exception as exc:
    fail('agentplane-bridge:parse', 'PFD094_AGENTPLANE_BRIDGE_PARSE_ERROR', str(exc), '.policy-fabric/agentplane_bridge.json')

probe_path = ROOT / 'docs/reports/agentplane_probe_latest.json'
if probe_path.exists():
    try:
        probe = load_json('docs/reports/agentplane_probe_latest.json')
        if probe.get('apiVersion') == 'policy.fabric.agentplane-probe/v1':
            ok('agentplane-probe:report-shape', 'PFD095_AGENTPLANE_PROBE_OK', 'AgentPlane probe report present with expected API version', 'docs/reports/agentplane_probe_latest.json')
        else:
            fail('agentplane-probe:report-shape', 'PFD096_AGENTPLANE_PROBE_INVALID', 'AgentPlane probe report API version mismatch', 'docs/reports/agentplane_probe_latest.json')

        summary = probe.get('summary', {})
        if summary.get('status') in {'pass', 'warn'}:
            ok('agentplane-probe:report-status', 'PFD097_AGENTPLANE_PROBE_STATUS_OK', 'AgentPlane probe report is non-failing', 'docs/reports/agentplane_probe_latest.json')
        else:
            fail('agentplane-probe:report-status', 'PFD098_AGENTPLANE_PROBE_STATUS_FAIL', 'AgentPlane probe report is failing', 'docs/reports/agentplane_probe_latest.json')
    except Exception as exc:
        fail('agentplane-probe:parse', 'PFD099_AGENTPLANE_PROBE_PARSE_ERROR', str(exc), 'docs/reports/agentplane_probe_latest.json')
else:
    warn('agentplane-probe:missing', 'PFD100_AGENTPLANE_PROBE_MISSING', 'AgentPlane probe report missing; run python scripts/agentplane_probe.py', 'docs/reports/agentplane_probe_latest.json')

try:
    publish_contract = load_json('.policy-fabric/github_publish.json')
    if publish_contract.get('owner') and publish_contract.get('repoName') and publish_contract.get('visibility') in {'private', 'public', 'internal'}:
        ok('github-publish:contract-shape', 'PFD110_GITHUB_PUBLISH_OK', 'GitHub publish contract has expected core fields', '.policy-fabric/github_publish.json')
    else:
        fail('github-publish:contract-shape', 'PFD111_GITHUB_PUBLISH_INVALID', 'GitHub publish contract missing owner, repoName, or valid visibility', '.policy-fabric/github_publish.json')

    gh_workflow = yaml.safe_load((ROOT / '.github/workflows/repo_health.yml').read_text())
    triggers = gh_workflow.get(True) if True in gh_workflow else gh_workflow.get('on', {})
    if 'push' in triggers and 'pull_request' in triggers:
        ok('github-publish:workflow-triggers', 'PFD112_GITHUB_WORKFLOW_OK', 'repo health workflow is configured for push and pull_request', '.github/workflows/repo_health.yml')
    else:
        fail('github-publish:workflow-triggers', 'PFD113_GITHUB_WORKFLOW_INVALID', 'repo health workflow missing push or pull_request trigger', '.github/workflows/repo_health.yml')
except Exception as exc:
    fail('github-publish:parse', 'PFD114_GITHUB_PUBLISH_PARSE_ERROR', str(exc), '.policy-fabric/github_publish.json')

github_prep_path = ROOT / 'docs/reports/github_publish_prep_latest.json'
if github_prep_path.exists():
    try:
        github_prep = load_json('docs/reports/github_publish_prep_latest.json')
        if github_prep.get('apiVersion') == 'policy.fabric.github-publish-report/v1':
            ok('github-publish:report-shape', 'PFD115_GITHUB_PUBLISH_REPORT_OK', 'GitHub publish prep report present with expected API version', 'docs/reports/github_publish_prep_latest.json')
        else:
            fail('github-publish:report-shape', 'PFD116_GITHUB_PUBLISH_REPORT_INVALID', 'GitHub publish prep report API version mismatch', 'docs/reports/github_publish_prep_latest.json')

        if github_prep.get('summary', {}).get('status') in {'pass', 'warn'}:
            ok('github-publish:report-status', 'PFD117_GITHUB_PUBLISH_STATUS_OK', 'GitHub publish prep report is non-failing', 'docs/reports/github_publish_prep_latest.json')
        else:
            fail('github-publish:report-status', 'PFD118_GITHUB_PUBLISH_STATUS_FAIL', 'GitHub publish prep report is failing', 'docs/reports/github_publish_prep_latest.json')
    except Exception as exc:
        fail('github-publish:report-parse', 'PFD119_GITHUB_PUBLISH_REPORT_PARSE_ERROR', str(exc), 'docs/reports/github_publish_prep_latest.json')
else:
    warn('github-publish:report-missing', 'PFD120_GITHUB_PUBLISH_REPORT_MISSING', 'GitHub publish prep report missing; run python scripts/github_publish_prep.py', 'docs/reports/github_publish_prep_latest.json')

try:
    branch_policy = load_json('.policy-fabric/branch_policy.json')
    if branch_policy.get('protectedBranches') == ['main'] and branch_policy.get('baselineTagPrefix') == 'baseline/':
        ok('branch-policy:contract-shape', 'PFD101_BRANCH_POLICY_OK', 'branch policy protects main and defines baseline tag prefix', '.policy-fabric/branch_policy.json')
    else:
        fail('branch-policy:contract-shape', 'PFD102_BRANCH_POLICY_INVALID', 'branch policy missing expected bootstrap protections', '.policy-fabric/branch_policy.json')
except Exception as exc:
    fail('branch-policy:parse', 'PFD103_BRANCH_POLICY_PARSE_ERROR', str(exc), '.policy-fabric/branch_policy.json')

branch_audit_path = ROOT / 'docs/reports/branch_audit_latest.json'
if branch_audit_path.exists():
    try:
        branch_audit = load_json('docs/reports/branch_audit_latest.json')
        if branch_audit.get('apiVersion') == 'policy.fabric.branch-audit/v1':
            ok('branch-audit:report-shape', 'PFD104_BRANCH_AUDIT_OK', 'branch audit report present with expected API version', 'docs/reports/branch_audit_latest.json')
        else:
            fail('branch-audit:report-shape', 'PFD105_BRANCH_AUDIT_INVALID', 'branch audit report API version mismatch', 'docs/reports/branch_audit_latest.json')

        if branch_audit.get('summary', {}).get('status') in {'pass', 'warn'}:
            ok('branch-audit:report-status', 'PFD106_BRANCH_AUDIT_STATUS_OK', 'branch audit report is non-failing', 'docs/reports/branch_audit_latest.json')
        else:
            fail('branch-audit:report-status', 'PFD107_BRANCH_AUDIT_STATUS_FAIL', 'branch audit report is failing', 'docs/reports/branch_audit_latest.json')
    except Exception as exc:
        fail('branch-audit:parse', 'PFD108_BRANCH_AUDIT_PARSE_ERROR', str(exc), 'docs/reports/branch_audit_latest.json')
else:
    warn('branch-audit:missing', 'PFD109_BRANCH_AUDIT_MISSING', 'branch audit report missing; run python scripts/branch_audit.py', 'docs/reports/branch_audit_latest.json')

bundle_manifest_path = ROOT / 'dist/policy_fabric_contracts_bundle_manifest.json'
if bundle_manifest_path.exists():
    try:
        ownership = load_json('.policy-fabric/ownership.json')
        manifest = load_json('dist/policy_fabric_contracts_bundle_manifest.json')
        exclusions = ownership.get('localOverridePaths', [])
        leaking = []
        for item in manifest.get('files', []):
            rel = item.get('path', '')
            if any(fnmatch.fnmatch(rel, pattern) for pattern in exclusions):
                leaking.append(rel)
        if not leaking:
            ok('bundle:local-overrides-excluded', 'PFD080_BUNDLE_EXCLUSION_OK', 'local override files are excluded from the distributable bundle', 'dist/policy_fabric_contracts_bundle_manifest.json')
        else:
            fail('bundle:local-overrides-excluded', 'PFD081_BUNDLE_EXCLUSION_FAILED', f'local override files leaked into bundle: {leaking}', 'dist/policy_fabric_contracts_bundle_manifest.json')
    except Exception as exc:
        fail('bundle:local-overrides-excluded', 'PFD082_BUNDLE_MANIFEST_PARSE_ERROR', str(exc), 'dist/policy_fabric_contracts_bundle_manifest.json')
else:
    warn('bundle:local-overrides-excluded', 'PFD083_BUNDLE_MANIFEST_MISSING', 'bundle manifest missing; exclusion check deferred until build step', 'dist/policy_fabric_contracts_bundle_manifest.json')

report['summary']['checkCount'] = len(report['checks'])
report['summary']['failCount'] = sum(1 for c in report['checks'] if c['status'] == 'fail')
report['summary']['warnCount'] = sum(1 for c in report['checks'] if c['status'] == 'warn')
if report['summary']['failCount']:
    report['summary']['status'] = 'fail'
elif report['summary']['warnCount']:
    report['summary']['status'] = 'warn'
else:
    report['summary']['status'] = 'pass'

out_json = ROOT / '.policy-fabric/reports/doctor_latest.json'
out_md = ROOT / 'docs/reports/doctor_latest.md'
validation_json = ROOT / 'docs/reports/validation_report_latest.json'
validation_md = ROOT / 'docs/reports/validation_report_latest.md'
out_json.parent.mkdir(parents=True, exist_ok=True)
out_md.parent.mkdir(parents=True, exist_ok=True)

out_json.write_text(json.dumps(report, indent=2) + '\n')
validation_json.write_text(json.dumps(report, indent=2) + '\n')

lines = ['# Doctor Report', '', f"Overall status: {report['summary']['status'].upper()}", '']
for item in report['checks']:
    marker = 'OK' if item['status'] == 'pass' else ('WARN' if item['status'] == 'warn' else 'FAIL')
    lines.append(f"- [{marker}] {item['id']} — {item['code']} — {item['message']}")
out_md.write_text('\n'.join(lines) + '\n')

lines = ['# Validation Report', '', f"Overall status: {report['summary']['status'].upper()}", '']
lines.append(f"Check count: `{report['summary']['checkCount']}`; fails: `{report['summary']['failCount']}`; warnings: `{report['summary']['warnCount']}`")
lines.append('')
for item in report['checks']:
    lines.append(f"- `{item['code']}` — {item['status']} — {item['message']}")
validation_md.write_text('\n'.join(lines) + '\n')

print(json.dumps(report, indent=2))
raise SystemExit(0 if report['summary']['status'] != 'fail' else 1)
