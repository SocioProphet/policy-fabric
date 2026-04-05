from __future__ import annotations

import fnmatch
import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST_DIR = ROOT / 'dist'
DIST_DIR.mkdir(exist_ok=True)
BUNDLE = DIST_DIR / 'policy_fabric_contracts_bundle_latest.zip'
MANIFEST = DIST_DIR / 'policy_fabric_contracts_bundle_manifest.json'
OWNERSHIP = json.loads((ROOT / '.policy-fabric/ownership.json').read_text())
EXCLUSIONS = OWNERSHIP.get('bundleExclusions', [])

include_roots = [
    'README.md', 'CHANGELOG.md', 'BACKLOG.md', 'CONTRIBUTING.md', 'SECURITY.md', 'AGENTS.md', 'REPO_MANIFEST.json',
    'contracts', 'examples', 'docs', '.policy-fabric', '.github'
]


def excluded(rel: str) -> bool:
    return any(fnmatch.fnmatch(rel, pattern) for pattern in EXCLUSIONS)


files = []
for rel in include_roots:
    p = ROOT / rel
    if p.is_file():
        files.append(p)
    elif p.is_dir():
        files.extend([x for x in p.rglob('*') if x.is_file()])

files = sorted({f.resolve() for f in files})
manifest = {'files': []}
with zipfile.ZipFile(BUNDLE, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
    for path in files:
        arc = path.relative_to(ROOT).as_posix()
        if arc.startswith('dist/') or excluded(arc):
            continue
        data = path.read_bytes()
        sha = hashlib.sha256(data).hexdigest()
        manifest['files'].append({'path': arc, 'sha256': sha, 'bytes': len(data)})
        zf.writestr(arc, data)

MANIFEST.write_text(json.dumps(manifest, indent=2) + '\n')
print(BUNDLE)
