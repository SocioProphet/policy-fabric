from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

FORBIDDEN_ENV_TOKENS = {
    'dev',
    'stage',
    'staging',
    'prod',
    'production',
    'canary',
}

FORBIDDEN_ROLE_TOKENS = {
    'sensor',
    'planner',
    'governor',
    'auditor',
    'actuator',
    'broker',
    'steward',
}

TOPOLOGY_HINT_FIELDS = {
    'topology',
    'region',
    'site',
    'customer',
    'cell',
    'fleet',
}

OSIMAGE_FORBIDDEN_FIELDS = {
    'deploymentEnvironmentName',
    'serviceIdentity',
    'policyRefs',
    'relations',
    'objectives',
}

CYBERNETIC_SUBSTRATE_FIELDS = {
    'osRelease',
    'ociAnnotations',
    'substrateCapabilities',
    'provenance',
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def walk_strings(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from walk_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from walk_strings(item)


def detect_kind(doc: dict[str, Any]) -> str:
    kind = doc.get('type')
    if isinstance(kind, str):
        return kind
    return 'Unknown'


def find_token_hits(strings: list[str], tokens: set[str]) -> list[str]:
    hits: list[str] = []
    for text in strings:
        lowered = text.lower()
        for token in tokens:
            if re.search(rf'(^|[^a-z]){re.escape(token)}([^a-z]|$)', lowered):
                hits.append(f'{token}: {text}')
    return hits


def check_osimage(doc: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    for field in OSIMAGE_FORBIDDEN_FIELDS:
        if field in doc:
            failures.append(f'OSImage contains forbidden runtime field: {field}')

    strings = list(walk_strings(doc))
    failures.extend(
        f'OSImage contains forbidden environment token in value: {hit}'
        for hit in find_token_hits(strings, FORBIDDEN_ENV_TOKENS)
    )
    failures.extend(
        f'OSImage contains forbidden cybernetic role token in value: {hit}'
        for hit in find_token_hits(strings, FORBIDDEN_ROLE_TOKENS)
    )

    short_id = doc.get('shortId')
    if isinstance(short_id, str):
        lowered = short_id.lower()
        for token in FORBIDDEN_ENV_TOKENS | FORBIDDEN_ROLE_TOKENS:
            if token in lowered:
                failures.append(f'OSImage.shortId leaks forbidden token: {token}')

    for field in TOPOLOGY_HINT_FIELDS:
        if field in doc:
            failures.append(f'OSImage contains forbidden mutable/topology field: {field}')

    return failures


def check_nodebinding(doc: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    for field in CYBERNETIC_SUBSTRATE_FIELDS:
        if field in doc:
            failures.append(f'NodeBinding redefines substrate-only field: {field}')
    return failures


def check_cybernetic_assignment(doc: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    for field in CYBERNETIC_SUBSTRATE_FIELDS:
        if field in doc:
            failures.append(f'CyberneticAssignment contains substrate-only field: {field}')
    return failures


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print('usage: python scripts/check_os_cybernetic_boundary.py <json-file>', file=sys.stderr)
        return 2

    path = Path(argv[1])
    doc = load_json(path)
    if not isinstance(doc, dict):
        print(json.dumps({'status': 'fail', 'reason': 'document root must be an object'}, indent=2))
        return 1

    kind = detect_kind(doc)
    failures: list[str]
    if kind == 'OSImage':
        failures = check_osimage(doc)
    elif kind == 'NodeBinding':
        failures = check_nodebinding(doc)
    elif kind == 'CyberneticAssignment':
        failures = check_cybernetic_assignment(doc)
    else:
        failures = [f'unsupported document type: {kind}']

    report = {
        'status': 'pass' if not failures else 'fail',
        'kind': kind,
        'subject': str(path),
        'failures': failures,
    }
    print(json.dumps(report, indent=2))
    return 0 if not failures else 1


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
