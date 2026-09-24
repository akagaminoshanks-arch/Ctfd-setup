import json, os
from pathlib import Path

manifest_path = Path('challenge_manifest.json')
with manifest_path.open(encoding='utf-8') as f:
    data = json.load(f)
challenges = data.get('challenges', [])
base_dir = manifest_path.parent
missing = []
for c in challenges:
    for rel_path in c.get('files', []):
        fpath = base_dir / rel_path.replace('/', os.sep)
        if not fpath.exists():
            missing.append((c['id'], rel_path))

if missing:
    print('Missing files:')
    for cid, path in missing:
        print(f'- {cid}: {path}')
else:
    print('All referenced artifact files exist.')
