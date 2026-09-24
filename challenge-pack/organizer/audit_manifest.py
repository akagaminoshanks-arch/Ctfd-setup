import json, os, collections, sys
manifest_path = r"c:/Users/abhin/Downloads/hackathon-timer/New folder/yit-ctf-challenge-pack/challenge-pack/challenge_manifest.json"
with open(manifest_path, 'r', encoding='utf-8') as f:
    data = json.load(f)
challenges = data.get('challenges', [])
print('Total challenges:', len(challenges))
ids = [c.get('id') for c in challenges]
flags = [c.get('flag') for c in challenges]
dup_ids = [i for i, cnt in collections.Counter(ids).items() if cnt > 1]
dup_flags = [f for f, cnt in collections.Counter(flags).items() if cnt > 1]
print('Duplicate IDs:', dup_ids)
print('Duplicate flags:', dup_flags)
missing = []
base_dir = os.path.dirname(manifest_path)
for c in challenges:
    for f in c.get('files', []):
        p = os.path.join(base_dir, f.replace('/', os.sep))
        if not os.path.isfile(p):
            missing.append((c.get('id'), f))
print('Missing files count:', len(missing))
if missing:
    print('First missing:', missing[:5])
