import sys
from pathlib import Path
import requests


if len(sys.argv) != 3:
    raise SystemExit(
        "Usage: python organizer\\upload_c5.py "
        "http://127.0.0.1:8000 YOUR_PRIVATE_ADMIN_TOKEN"
    )

base = sys.argv[1].rstrip("/")
token = sys.argv[2]

root = Path(__file__).resolve().parent.parent
artifact = root / "artifacts" / "crypto" / "c5_rot13.txt"

headers = {
    "Authorization": f"Token {token}",
    "Accept": "application/json",
}


# Find the C5 challenge by its actual CTFd name.
print("Finding C5 challenge...")

page = 1
c5_id = None

while True:
    r = requests.get(
        base + "/api/v1/challenges",
        headers=headers,
        params={"page": page},
        timeout=30,
    )
    r.raise_for_status()

    response = r.json()
    challenges = response.get("data", [])

    for challenge in challenges:
        if challenge.get("name") == "ROT13 Rendezvous":
            c5_id = challenge.get("id")
            break

    if c5_id:
        break

    pagination = response.get("meta", {}).get("pagination", {})

    if not pagination.get("next"):
        break

    page += 1


if c5_id is None:
    raise SystemExit("ERROR: C5 'ROT13 Rendezvous' was not found.")


print(f"Found C5: CTFd ID {c5_id}")


# Verify artifact exists.
if not artifact.is_file():
    raise SystemExit(
        f"ERROR: C5 artifact not found:\n{artifact}"
    )


print(f"Artifact: {artifact}")
print()


# Upload ONLY C5.
with artifact.open("rb") as f:
    response = requests.post(
        base + "/api/v1/files",
        headers=headers,
        data={
            "challenge_id": str(c5_id),
            "type": "challenge",
        },
        files={
            "file": (
                artifact.name,
                f,
                "text/plain",
            )
        },
        timeout=60,
    )


if not response.ok:
    print("C5 UPLOAD FAILED")
    print("HTTP:", response.status_code)
    print("Response:", response.text)
    response.raise_for_status()


result = response.json()

print("========================================")
print("C5 UPLOAD SUCCESS")
print("========================================")
print("Challenge : ROT13 Rendezvous")
print("CTFd ID   :", c5_id)
print("File      :", artifact.name)

data = result.get("data") if isinstance(result, dict) else None

if isinstance(data, dict):
    print("File ID   :", data.get("id"))
elif isinstance(data, list) and data:
    if isinstance(data[0], dict):
        print("File ID   :", data[0].get("id"))

print("========================================")