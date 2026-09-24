import json, os, subprocess, sys, zipfile, re, base64, binascii
from pathlib import Path

# Helper to run a command and capture output
def run_cmd(cmd, cwd=None):
    result = subprocess.run(cmd, cwd=cwd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.stdout.strip(), result.stderr.strip(), result.returncode

# Load manifest
manifest_path = Path('challenge_manifest.json')
with manifest_path.open(encoding='utf-8') as f:
    data = json.load(f)
challenges = data.get('challenges', [])
base_dir = manifest_path.parent

# Collect flags
flags = {c['id']: c['flag'] for c in challenges}

# Report sections
report = []

def add(section):
    report.append(section)

# 1. Manifest sanity
ids = [c['id'] for c in challenges]
duplicate_ids = [i for i, cnt in __import__('collections').Counter(ids).items() if cnt > 1]
duplicate_flags = [f for f, cnt in __import__('collections').Counter(flags.values()).items() if cnt > 1]
add('## Manifest sanity')
add(f'Duplicate IDs: {duplicate_ids}')
add(f'Duplicate flags: {duplicate_flags}')

# 2. Artifact checks
add('\n## Artifact checks')
flag_pattern = re.compile(r'YITCTF\{[^}]+\}')
for c in challenges:
    cid = c['id']
    for rel_path in c.get('files', []):
        fpath = base_dir / rel_path.replace('/', os.sep)
        if not fpath.exists():
            add(f'- [ERROR] {cid}: missing file {rel_path}')
            continue
        # Determine type by extension
        ext = fpath.suffix.lower()
        # Read binary for analysis when needed
        try:
            content = fpath.read_bytes()
        except Exception as e:
            add(f'- [ERROR] {cid}: cannot read {rel_path}: {e}')
            continue
        # Basic non-empty check (except allowed empty e.g., placeholder files)
        if len(content) == 0:
            add(f'- [NOTE] {cid}: file {rel_path} is empty')
        # Search for any flag strings inside file (plaintext)
        text = ''
        try:
            text = content.decode('utf-8', errors='ignore')
        except Exception:
            pass
        for fflag in flags.values():
            if fflag in text:
                # If this is the same challenge, it's ok, otherwise leak
                if fflag != c['flag']:
                    add(f'- [LEAK] {cid}: flag {fflag} found in file {rel_path} (not intended)')
        # Specific checks per type
        if ext == '.txt' or ext == '.html' or ext == '.csv' or ext == '.log' or ext == '.md':
            # For cryptographic txt files, ensure they do not contain the plaintext flag
            if c['category'].lower() == 'cryptography' and c['flag'] in text:
                add(f'- [LEAK] {cid}: plaintext flag present in {rel_path}')
        elif ext in {'.png', '.jpg', '.jpeg'}:
            # Use strings to extract any embedded flag
            out, err, rc = run_cmd(f'strings "{fpath}"')
            for fflag in flags.values():
                if fflag in out:
                    if fflag != c['flag']:
                        add(f'- [LEAK] {cid}: flag {fflag} found in image {rel_path}')
        elif ext == '.pyc':
            out, err, rc = run_cmd(f'strings "{fpath}"')
            for fflag in flags.values():
                if fflag in out:
                    if fflag != c['flag']:
                        add(f'- [LEAK] {cid}: flag {fflag} found in bytecode {rel_path}')
        elif ext == '.zip':
            try:
                with zipfile.ZipFile(fpath, 'r') as z:
                    namelist = z.namelist()
                add(f'- [INFO] {cid}: zip contains {len(namelist)} entries')
            except zipfile.BadZipFile:
                add(f'- [ERROR] {cid}: zip file corrupted {rel_path}')
        elif ext == '.pcap':
            # Simple size check
            add(f'- [INFO] {cid}: pcap size {len(content)} bytes')
        # Additional types can be added

# 3. Web challenge testing
add('\n## Web challenge testing')
# Build and start Docker services
add('Building Docker images...')
stdout, stderr, rc = run_cmd('docker compose -f compose.web.yml build')
add(f'Build rc={rc}')
if rc == 0:
    add('Starting Docker containers...')
    stdout, stderr, rc = run_cmd('docker compose -f compose.web.yml up -d')
    add(f'Up rc={rc}')
    # Give containers a moment to start
    import time; time.sleep(5)
    # Test each web challenge
    for c in challenges:
        if c['category'].lower() != 'web':
            continue
        conn = c.get('connection', '')
        # Replace SERVER placeholder with localhost
        url = conn.replace('SERVER', 'localhost')
        out, err, rc = run_cmd(f'curl -s {url}')
        flag = c['flag']
        if flag in out:
            add(f'- [PASS] {c["id"]}: flag found via HTTP')
        else:
            # Try common shortcuts like comment, query param, etc.
            if c['id'] == 'W5':
                # Look for HTML comment
                if f'<!-- {flag} -->' in out or f'<!--{flag}-->' in out:
                    add(f'- [PASS] {c["id"]}: flag in comment')
                else:
                    add(f'- [FAIL] {c["id"]}: flag not found')
            elif c['id'] == 'W6':
                # Try debug param
                out2, _, _ = run_cmd(f'curl -s "{url}?debug=true"')
                if flag in out2:
                    add(f'- [PASS] {c["id"]}: flag via debug param')
                else:
                    add(f'- [FAIL] {c["id"]}: flag not found')
            elif c['id'] == 'W7':
                # Try login via POST (simple simulation) – not implemented, just note
                add(f'- [INFO] {c["id"]}: manual login required; flag presence not auto‑checked')
    # Tear down containers
    add('Tearing down Docker containers...')
    run_cmd('docker compose -f compose.web.yml down')
else:
    add('Docker build failed; skipping web tests')

# 4. Summary
add('\n## Summary')
add('Audit completed.')

# Write report
report_path = Path('qa_report.md')
report_path.write_text('\n'.join(report), encoding='utf-8')
print('Report written to', report_path)
