import json, os, re
from pathlib import Path

manifest_path = Path('challenge_manifest.json')
with manifest_path.open(encoding='utf-8') as f:
    data = json.load(f)
challenges = data.get('challenges', [])
base = manifest_path.parent
flags = {c['id']: c['flag'] for c in challenges}

rows = []
for c in challenges:
    cid = c['id']
    cat = c.get('category','')
    files = c.get('files',[])
    artifact_status = []
    for rel in files:
        path = base / rel.replace('/', os.sep)
        if path.exists():
            artifact_status.append('OK')
        else:
            artifact_status.append('MISSING')
    artifact = ','.join(artifact_status) if artifact_status else 'N/A'
    intended = c.get('hint','')
    # placeholder for problem/fix
    rows.append(f"{cid} | {cat} | {artifact} | {intended} |  | ")

report = "ID | Category | Artifact | Intended Solve | Current Problem | Fix Required\n" + "---|---|---|---|---|---\n" + "\n".join(rows)

out_path = Path('inventory_report.md')
out_path.write_text(report, encoding='utf-8')
print('Inventory report written to', out_path)
