"""Attach generated participant files to existing CTFd challenges.

Run only after import_ctfd_api.py has completed successfully on a fresh CTFd
instance. It uses the importer's sequential IDs (C1=1 through M2=20), which
avoids CTFd's public challenge-list route that is unavailable before an event.
Usage: python upload_ctfd_files_api.py http://127.0.0.1:8000 ADMIN_ACCESS_TOKEN
"""
import json
import sys
from pathlib import Path

import requests

if len(sys.argv) != 3:
    raise SystemExit("Usage: python upload_ctfd_files_api.py CTFD_URL ADMIN_ACCESS_TOKEN")

base, token = sys.argv[1].rstrip("/"), sys.argv[2]
root = Path(__file__).resolve().parent.parent
manifest = json.loads((root / "challenge_manifest.json").read_text())
headers = {"Authorization": f"Token {token}"}

for cid, challenge in enumerate(manifest["challenges"], start=1):
    for relative in challenge.get("files", []):
        path = root / relative
        if not path.is_file():
            raise FileNotFoundError(f"Missing generated artifact: {path}")
        with path.open("rb") as f:
            r = requests.post(
                base + "/api/v1/files",
                headers=headers,
                data={"challenge_id": str(cid), "type": "challenge"},
                files={"file": (path.name, f)},
            )
        r.raise_for_status()
        print(f"Attached {challenge['id']}: {path.name}")

print("Finished attaching participant files.")
