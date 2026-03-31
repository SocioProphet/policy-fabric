from __future__ import annotations
import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST_DIR = ROOT / 'dist'
DIST_DIR.mkdir(exist_ok=True)
BUNDLE = DIST_DIR / 'policy_fabric_contracts_bundle_latest.zip'
MANIFEST = DIST_DIR / 'policy_fabric_contracts_bundle_manifest.json'

include_roots = [
    'README.md', 'CHANGELOG.md', 'BACKLOG.md', 'REPO_MANIFEST.json',
    'contracts', 'examples', 'docs', '.policy-fabric'
]

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
        arc = path.relative_to(ROOT)
        if 'dist/' in str(arc):
            continue
        data = path.read_bytes()
        sha = hashlib.sha256(data).hexdigest()
        manifest['files'].append({'path': str(arc), 'sha256': sha, 'bytes': len(data)})
        zf.writestr(str(arc), data)

MANIFEST.write_text(json.dumps(manifest, indent=2) + '\n')
print(BUNDLE)
