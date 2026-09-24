import json, os, sys
from pathlib import Path
root = Path(__file__).resolve().parent.parent
manifest_path = root / "challenge_manifest.json"
with open(manifest_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

missing = []
for chal in data.get('challenges', []):
    # check files list if present
    for rel in chal.get('files', []):
        abs_path = os.path.join(os.path.dirname(__file__), 'artifacts', rel.replace('/', os.sep))
        if not os.path.exists(abs_path):
            missing.append((chal['id'], rel, abs_path))

if missing:
    print('Missing files:')
    for cid, rel, path in missing:
        print(f"  {cid}: {rel} -> {path}")
    sys.exit(1)
else:
    print('All referenced files exist.')
    sys.exit(0)
