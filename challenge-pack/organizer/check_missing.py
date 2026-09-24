import json, os
manifest_path = r"c:/Users/abhin/Downloads/hackathon-timer/New folder/yit-ctf-challenge-pack/challenge-pack/challenge_manifest.json"
with open(manifest_path, 'r', encoding='utf-8') as f:
    data = json.load(f)
base = os.path.dirname(manifest_path)
missing = []
for c in data.get('challenges', []):
    for fpath in c.get('files', []):
        full = os.path.join(base, fpath.replace('/', os.sep))
        if not os.path.isfile(full):
            missing.append((c['id'], fpath))
print('Missing count:', len(missing))
for cid, fp in missing:
    print(cid, fp)
