"""Create CTFd challenge metadata, flags, and hints from challenge_manifest.json.

Usage: python import_ctfd_api.py http://127.0.0.1:8000 ADMIN_ACCESS_TOKEN
Participant files are intentionally not uploaded by this script: CTFd's upload
endpoint and storage policy vary. Use the printed upload checklist afterwards.
"""
import json, sys
from pathlib import Path
import requests

if len(sys.argv) != 3:
    raise SystemExit("Usage: python import_ctfd_api.py CTFD_URL ADMIN_ACCESS_TOKEN")
base, token = sys.argv[1].rstrip("/"), sys.argv[2]
root = Path(__file__).resolve().parent.parent
data = json.loads((root / "challenge_manifest.json").read_text())
s = requests.Session(); s.headers.update({"Authorization": f"Token {token}", "Content-Type": "application/json"})

for item in data["challenges"]:
    body = {"name": item["name"], "category": item["category"], "description": "\n".join([
        f"**{item['id']}** — {item['name']}",
        "Connection: `" + item["connection"] + "`" if "connection" in item else "Download the attached participant file(s).",
        "Submit the flag in the form `YITCTF{...}`."
    ]), "value": item["value"], "type": "standard", "state": "visible", "max_attempts": 0}
    r = s.post(base + "/api/v1/challenges", json=body); r.raise_for_status()
    cid = r.json()["data"]["id"]
    for endpoint, payload in (("flags", {"challenge_id": cid, "type": "static", "content": item["flag"], "data": "case_insensitive"}), ("hints", {"challenge_id": cid, "content": item["hint"], "cost": 0})):
        r = s.post(base + "/api/v1/" + endpoint, json=payload); r.raise_for_status()
    print(f"Created {item['id']} (id {cid})")

print("\nUpload these files manually in each challenge's Files tab:")
for item in data["challenges"]:
    for f in item.get("files", []): print(f"{item['id']}: {root / 'artifacts' / f}")
