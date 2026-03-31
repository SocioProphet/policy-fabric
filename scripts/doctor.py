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
    ROOT / 'examples/policy_fabric_policy_v2_enhanced_example.json',
    ROOT / 'examples/policy_fabric_compiled_plan_example.json',
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

try:
    policy_schema = json.loads((ROOT / 'contracts/policy_fabric_policy_v2.schema.json').read_text())
    policy_example = json.loads((ROOT / 'examples/policy_fabric_policy_v2_enhanced_example.json').read_text())
    jsonschema.validate(policy_example, policy_schema)
    add('validate:policy-example', True, 'policy example validates against policy schema')
except Exception as exc:
    add('validate:policy-example', False, str(exc))

try:
    plan_schema = json.loads((ROOT / 'contracts/policy_fabric_execution_plan_ir_v1.schema.json').read_text())
    plan_example = json.loads((ROOT / 'examples/policy_fabric_compiled_plan_example.json').read_text())
    jsonschema.validate(plan_example, plan_schema)
    add('validate:plan-example', True, 'compiled plan validates against plan schema')
except Exception as exc:
    add('validate:plan-example', False, str(exc))

try:
    spec = yaml.safe_load((ROOT / 'contracts/policy_fabric_openapi_v2.yaml').read_text())
    ok = spec.get('openapi') == '3.1.0' and '/v2/process' in spec.get('paths', {})
    add('parse:openapi', ok, 'openapi parses and contains /v2/process' if ok else 'openapi missing expected core surface')
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
