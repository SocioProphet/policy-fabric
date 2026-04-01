from __future__ import annotations

import fnmatch
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OWNERSHIP = json.loads((ROOT / '.policy-fabric/ownership.json').read_text())

CATEGORY_MAP = {
    'frameworkManaged': OWNERSHIP['frameworkManagedPaths'],
    'generated': OWNERSHIP['generatedPaths'],
    'localOverride': OWNERSHIP['localOverridePaths'],
    'archiveProtected': OWNERSHIP['archiveProtectedPaths'],
}

IGNORE_PREFIXES = ['.git/']
EXCLUDE_FROM_MANIFEST = {'REPO_MANIFEST.json'}
EXCLUDE_FROM_MANIFEST_PREFIXES = ['dist/']


def git_info() -> tuple[str, bool]:
    try:
        rev = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'], cwd=ROOT, text=True).strip()
        dirty = bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip())
        return rev, dirty
    except Exception:
        return 'UNKNOWN', True


def classify(rel: str) -> list[str]:
    matched = []
    for category, patterns in CATEGORY_MAP.items():
        for pattern in patterns:
            if fnmatch.fnmatch(rel, pattern):
                matched.append(category)
                break
    return matched


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


for rel in ['docs/reports', '.policy-fabric/reports', '.policy-fabric/local-notes', 'dist']:
    (ROOT / rel).mkdir(parents=True, exist_ok=True)

files = []
for path in sorted(p for p in ROOT.rglob('*') if p.is_file()):
    rel = path.relative_to(ROOT).as_posix()
    if any(rel.startswith(prefix) for prefix in IGNORE_PREFIXES):
        continue
    if rel in EXCLUDE_FROM_MANIFEST or any(rel.startswith(prefix) for prefix in EXCLUDE_FROM_MANIFEST_PREFIXES):
        continue
    files.append({
        'path': rel,
        'sha256': sha256(path),
        'bytes': path.stat().st_size,
        'categories': classify(rel),
    })

rev, dirty = git_info()
manifest = {
    'generatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
    'git': {'rev': rev, 'dirty': dirty},
    'fileCount': len(files),
    'files': files,
}
(ROOT / 'REPO_MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n')

report = {
    'generatedAt': manifest['generatedAt'],
    'git': manifest['git'],
    'fileCount': len(files),
    'localOverridePaths': OWNERSHIP['localOverridePaths'],
    'generatedPaths': OWNERSHIP['generatedPaths'],
}
(ROOT / '.policy-fabric/reports/reconcile_latest.json').write_text(json.dumps(report, indent=2) + '\n')
(ROOT / 'docs/reports/reconcile_latest.md').write_text(
    '# Reconcile Report\n\n'
    f"Generated at: `{manifest['generatedAt']}`\n\n"
    f"Current HEAD: `{rev}`\n\n"
    f"Dirty working tree: `{'yes' if dirty else 'no'}`\n\n"
    f"Tracked file count in manifest: `{len(files)}`\n"
)
print(json.dumps(report, indent=2))
