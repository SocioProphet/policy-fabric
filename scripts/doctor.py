from __future__ import annotations
import json
from pathlib import Path
import sys

try:
    import yaml
    import jsonschema
except Exception as exc:
    print(f"dependency error: {exc}", file=sys.stderr)
    raise

ROOT = Path(__file__).resolve().parents[1]

required = [
    ROOT / 'contracts/policy_fabric_policy_v2.schema.json',
    ROOT / 'contracts/policy_fabric_execution_plan_ir_v1.schema.json',
    ROOT / 'contracts/policy_fabric_openapi_v2.yaml',
    ROOT / 'contracts/policy_fabric_release_pack_v1.schema.json',
    ROOT / 'contracts/policy_fabric_validation_report_v1.schema.json',
    ROOT / 'contracts/policy_fabric_replay_report_v1.schema.json',
    ROOT / 'examples/policy_fabric_policy_v2_enhanced_example.json',
    ROOT / 'examples/policy_fabric_compiled_plan_example.json',
    ROOT / 'examples/policy_fabric_release_pack_example.json',
    ROOT / 'examples/policy_fabric_validation_report_example.json',
    ROOT / 'examples/policy_fabric_replay_report_example.json',
    ROOT / '.policy-fabric/config.json',
    ROOT / '.policy-fabric/WORKFLOW.md',
]

report = {'ok': True, 'checks': []}

def add(name: str, ok: bool, detail: str) -> None:
    report['checks'].append({'name': name, 'ok': ok, 'detail': detail})
    if not ok:
        report['ok'] = False

for path in required:
    add(
        f'exists:{path.relative_to(ROOT)}',
        path.exists(),
        'required file present' if path.exists() else 'missing required file',
    )

pairs = [
    ('validate:policy-example', 'contracts/policy_fabric_policy_v2.schema.json', 'examples/policy_fabric_policy_v2_enhanced_example.json', 'policy example validates against policy schema'),
    ('validate:plan-example', 'contracts/policy_fabric_execution_plan_ir_v1.schema.json', 'examples/policy_fabric_compiled_plan_example.json', 'compiled plan validates against plan schema'),
    ('validate:release-pack-example', 'contracts/policy_fabric_release_pack_v1.schema.json', 'examples/policy_fabric_release_pack_example.json', 'release pack example validates against release pack schema'),
    ('validate:validation-report-example', 'contracts/policy_fabric_validation_report_v1.schema.json', 'examples/policy_fabric_validation_report_example.json', 'validation report example validates against validation report schema'),
    ('validate:replay-report-example', 'contracts/policy_fabric_replay_report_v1.schema.json', 'examples/policy_fabric_replay_report_example.json', 'replay report example validates against replay report schema'),
]
for name, schema_rel, example_rel, ok_msg in pairs:
    try:
        schema = json.loads((ROOT / schema_rel).read_text())
        example = json.loads((ROOT / example_rel).read_text())
        jsonschema.validate(example, schema)
        add(name, True, ok_msg)
    except Exception as exc:
        add(name, False, str(exc))

try:
    spec = yaml.safe_load((ROOT / 'contracts/policy_fabric_openapi_v2.yaml').read_text())
    paths = spec.get('paths', {})
    ok = spec.get('openapi') == '3.1.0' and '/v2/process' in paths and '/v2/explain' in paths
    add('parse:openapi', ok, 'openapi parses and contains expected core surfaces' if ok else 'openapi missing expected core surfaces')
except Exception as exc:
    add('parse:openapi', False, str(exc))

out_json = ROOT / '.policy-fabric/reports/doctor_latest.json'
out_md = ROOT / 'docs/reports/doctor_latest.md'
out_json.parent.mkdir(parents=True, exist_ok=True)
out_md.parent.mkdir(parents=True, exist_ok=True)
out_json.write_text(json.dumps(report, indent=2) + '\n')

lines = ['# Doctor Report', '', f"Overall status: {'PASS' if report['ok'] else 'FAIL'}", '']
for item in report['checks']:
    lines.append(f"- [{'OK' if item['ok'] else 'FAIL'}] {item['name']} — {item['detail']}")
out_md.write_text('\n'.join(lines) + '\n')

print(json.dumps(report, indent=2))
raise SystemExit(0 if report['ok'] else 1)
