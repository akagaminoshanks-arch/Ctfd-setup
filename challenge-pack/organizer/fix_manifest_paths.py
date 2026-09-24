import json, os
manifest_path = r"c:/Users/abhin/Downloads/hackathon-timer/New folder/yit-ctf-challenge-pack/challenge-pack/challenge_manifest.json"
with open(manifest_path, 'r', encoding='utf-8') as f:
    data = json.load(f)
changed = 0
for challenge in data.get('challenges', []):
    files = challenge.get('files')
    if files:
        new_files = []
        for f in files:
            if not f.startswith('artifacts/'):
                new_files.append('artifacts/' + f)
                changed += 1
            else:
                new_files.append(f)
        challenge['files'] = new_files
# Write back with pretty formatting
with open(manifest_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)
print('Manifest updated, entries changed:', changed)
