# Final Deployment Remediation Plan

The repository currently fails a full audit: only 6 of 32 challenges are solvable, 53 unintended flag leaks, and most web challenges are broken.  We need to bring the CTF to a fully playable state.

## Goal
- All 32 challenges must be solvable by participants.
- No participant‑accessible flag leaks.
- All web services (W1‑W7) must function as intended.
- Manifest, artifacts, Docker configuration, and R3 bytecode must be correct.
- Produce a clean participant package with no internal files.

## Phase 1 – Repository Inventory & Diagnosis (Research)
1. List every file in the repository.
2. Read `challenge_manifest.json` and extract each challenge definition.
3. For each challenge, identify:
   - Intended artifact(s) (files, web endpoint, etc.)
   - Expected solving method (cipher, forensic tool, etc.)
   - Where the flag is currently stored (manifest, source, artifact, Docker image, etc.)
4. Inspect the web source (`web/app.py`), Dockerfile, and `compose.web.yml`.
5. Review generation scripts (`generate_artifacts.py`, `full_audit.py`).
6. Read `qa_report.md` for historical context.
7. Produce a concise **Audit Findings** document summarising:
   - Broken challenges and why.
   - All unintended flag locations.
   - Manifest exposures.
   - Docker‑related exposures.

## Phase 2 – Flag Architecture Refactor
1. Separate *organizer‑only* files from the participant‑facing package.
   - Create a new directory `participant/` that will contain only the files participants should receive.
   - Move `challenge_manifest.json` (with flags removed) to a server‑side location `server/` for validation only.
2. Replace plaintext flags in `challenge_manifest.json` with placeholders (e.g., `"flag": "{{C1_FLAG}}"`).
3. Store the real flags in a new protected JSON `server/flags.json` that is **not** copied into Docker images or the participant package.
4. Update any internal scripts that reference flags to load them from `server/flags.json`.
5. Ensure no flag strings appear in any file that will be shipped to participants (artifacts, source, Docker context, etc.).

## Phase 3 – Web Service Corrections (Implementation)
For each web challenge (W1‑W7) we will:
- Verify the `CHALLENGE` environment variable is correctly read.
- Ensure the Flask handler returns the intended response.
- Add missing routes or logic where needed.
- Remove any hard‑coded flag literals from the source.
- Add appropriate `Set-Cookie` handling for W2 and request‑parameter handling for W6.
- Ensure static files (HTML/JS) do not expose the flag.
- Test each service individually with `curl`.
Specific actions:
- **W1**: keep HTML comment with flag placeholder; confirm flag is read from server‑side config.
- **W2**: modify cookie logic to decode Base64 role and only show flag when role == "admin".
- **W3**: implement a simple mock login that checks for injected payload `admin' --` and returns flag.
- **W4**: ensure `/robots.txt` and `/archive/` serve correct content without exposing flag directly.
- **W5**: preserve HTML comment with flag placeholder; ensure flag is inserted at runtime.
- **W6**: add query‑parameter check (`debug=true`) to reveal flag.
- **W7**: serve JavaScript that defines `flag` variable but does **not** expose it in source; participants must run the script in a browser to see it.

## Phase 4 – Non‑Web Challenge Fixes
For each category we will:
- **Cryptography (C1‑C7)**: Ensure ciphertext files exist, are correctly formatted, and flags are not in the source files. Update any broken files.
- **Forensics (F1‑F7)**: Verify each artifact (image, PCAP, zip) contains the clue. Regenerate any broken files using standard tools.
- **OSINT (O1‑O5)**: Ensure all supporting HTML/archives are present and self‑contained.
- **Reverse (R1‑R3)**: Validate bytecode files, ensure they don’t print the flag directly, and that `strings` reveals the flag as intended.
- **Misc (M1‑M3)**: Verify multi‑layer encoding files are correct.
Any challenge that is missing a file will have the file regenerated from the original description.

## Phase 5 – Leak Elimination
Using a repository‑wide search for the flag pattern `YITCTF{` we will:
- Remove all occurrences from organizer‑only files.
- Ensure no encoded versions (Base64, hex) leak.
- Scan generated Docker images (`docker save` + `strings`) for residual flags.
- Update `.dockerignore` to exclude internal files.

## Phase 6 – Docker Isolation & Clean Build
1. Review `compose.web.yml` for accidental volume mounts; ensure only the `web/` directory is copied into each image.
2. Update `web/Dockerfile` to copy only `app.py`.
3. Add `.dockerignore` entries for any server‑side files (`server/`, `generate_artifacts.py`, `qa_report.md`).
4. Run:
   ```bash
   docker compose -f compose.web.yml down
   docker compose -f compose.web.yml build --no-cache
   docker compose -f compose.web.yml up -d
   ```
5. Verify all services start and respond correctly.

## Phase 7 – Participant Package Creation
- Copy `participant/` (artifacts, web sources, README) to a clean directory `dist/`.
- Exclude all server‑side files.
- Add a `README.md` with challenge list and instructions.
- Ensure `dist/` can be zipped and distributed without exposing any internal data.

## Phase 8 – Full Verification
1. Run `python full_audit.py` against the **participant** package.
2. Perform manual participant‑perspective solving for every challenge (scripted where possible, manual for web). Verify flags match server‑side values.
3. Re‑run the leak scan on the `dist/` directory.
4. Confirm Docker containers are isolated and no internal files are present inside images.

## Phase 9 – Final Reporting
- Produce `final_report.md` summarising:
  - Challenge status table (PASS/FAIL).
  - Web results.
  - Leak counts.
  - Infrastructure checks.
- If all criteria are satisfied, declare **READY FOR DEPLOYMENT**; otherwise list remaining issues.

## Open Questions (User Review Required)
- Should the manifest with placeholders remain in the repository root, or be moved entirely to a server‑only location?
- Do you want the server‑side `flags.json` to be committed (encrypted) or kept out of version control?
- Is the participant package expected to be a separate ZIP distribution, or will the same repo be used with a `dist/` directory?

---
**Request for approval**: Please review this implementation plan. Once approved we will begin Phase 1 (research & inventory) and proceed through the phases automatically.
