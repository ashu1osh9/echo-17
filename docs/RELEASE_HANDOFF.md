# Final release gate: RF + Gemma public candidate

Target: **31 October 2026, 20:00 IST**. No push, bundle upload, Render resource, payment, media upload or DEV publication has occurred. A local commit is prepared for review; publication still needs explicit owner authorization.

## Safety boundary

The hosted release contains genuine UCI recordings, actual Random Forest results and genuine RF-grounded precomputed Gemma reports. It contains **no TabPFN weights, metrics, predictions, probabilities or reports grounded in TabPFN outputs**. The public server also suppresses those outputs if files are accidentally copied. The public installer rejects the older full research ZIP.

Original research artifacts are unchanged. Exact earlier documents, including the full paired comparison and article, were copied with SHA-256 hashes to ignored `backend/artifacts/release-private/before-rf-gate/`. This preserves research evidence without publishing it. Public-use permission under the accepted TabPFN participant agreement remains unconfirmed; no exemption is assumed. The RF-only payload does not depend on that permission.

The exposed Prior Labs key must be revoked/rotated by its owner. Rotation remains unverified unless the owner confirms it. No credential is needed by the deployed app. Do not upload the earlier account/key screenshot or raw sessions containing credentials.

## Exact proposed payload

File: `backend/artifacts/release/echo17-public-rf.zip`

- Size: **2,971,364 bytes**, **9 members**.
- SHA-256: **`96dc5038f7526cec9aacdeb27884c0418520a5461f73a1b2ef6b455ebb9d04cd`**.
- Original six experiment input/provenance files, measured `signals.npz`, four RF-grounded Gemma reports and attributed manifest.
- All 441 held-out RF diagnoses/replays/Ghost comparisons remain usable. Saved Gemma coverage: cycles 5, 735, 2, 1467; other cycles receive an explicit non-LLM fallback.
- No raw sensor text, fitted model, checkpoint, key, environment, cache or log. The registry is a validated RF-only subset; original report files are unchanged.

**Do not publish `echo17-demo.zip` or the private research directory.** Only the new RF-only ZIP is proposed. Full file membership and the exact source-commit list are in [PUBLICATION_MANIFEST.md](PUBLICATION_MANIFEST.md).

Export/install were executed locally; both refuse overwrite:

```powershell
# From backend; reuse the already-created bundle instead of re-exporting.
& ./.venv/mission1/Scripts/python.exe -m ml.release_bundle export artifacts/release/echo17-public-rf.zip
& ./.venv/mission1/Scripts/python.exe -m ml.release_bundle install artifacts/release/echo17-public-rf.zip --destination artifacts/release/rf-public-data --sha256 96dc5038f7526cec9aacdeb27884c0418520a5461f73a1b2ef6b455ebb9d04cd
```

## Actual local URLs

- Public-mode candidate: **http://127.0.0.1:8001/**, cycle `/#/investigation/735`, evaluation `/#/evaluation`.
- Local research/live Gemma workflow: **http://127.0.0.1:5173/**, API **http://127.0.0.1:8000/docs**. It remains local and must not be exposed as the public deployment.
- Public GitHub: **https://github.com/ashu1osh9/echo-17**, HTTP 200; API confirms creation **2026-10-29T18:11:53Z**, public/non-fork. No creation date was altered.
- Render frontend/API: **not deployed; no URL exists to claim**.
- Video/DEV entry: **not published; no URL exists to claim**.

## Render Free compatibility

The final Blueprint is one **Docker Free web service**, serving the existing static React build and FastAPI on one origin. It avoids separate frontend/API URL coordination. Docker builds the frontend, installs serving dependencies and fetches only the checksum-pinned RF bundle. Runtime is non-root, one worker, no model weights, no LLM/GPU inference and no request-time data writes.

The RF-only Windows serving smoke check exercised **66 checks**, peak **167.34 MiB**, 6.394 seconds after imports. This suggests the documented 512 MB free instance is a reasonable trial, not a Linux/Render performance guarantee. Cold startup, Linux package installation and Docker image build remain unverified. Free services can sleep after 15 idle minutes, take about a minute to wake, lose runtime filesystem writes and hit usage quotas; review [current Render limits](https://render.com/docs/free). Do not upgrade or add a payment method without separate authorization.

The bundle is installed at image build time, so runtime ephemeral storage is not used to persist investigations. Missing/invalid data fails readiness; missing/invalid reports produce a labeled fallback. Model outputs never silently become fabricated demo data.

## Exact approval and Blueprint steps

1. Confirm key rotation, inspect the publication manifest and clean local commit, and verify signed-in DEV access. The public [Week 4 challenge page](https://dev.to/challenges/hacktoberfest-week4-2026-10-26) still says Live Ended despite an Oct 31 due date. Age/location eligibility and the actual signed-in submission flow require owner verification.
2. **Authorize the source push explicitly.** Review `git show --stat HEAD`, `git show --name-only HEAD` and the recorded commit hash. No force push or history rewrite is needed. Only after authorization: `git push origin main`.
3. **Authorize RF-bundle publication explicitly.** Create a GitHub release for that reviewed commit and attach only `echo17-public-rf.zip`. Download the asset and recheck its SHA-256. Copy the actual public asset URL from GitHub; no asset URL is invented here. Do not attach research ZIPs, private evidence, source datasets or weights.
4. **Authorize deployment explicitly.** In Render: New -> Blueprint, connect the existing GitHub repository, select the reviewed branch/commit and `render.yaml`. It declares one Docker Free service, automatic deployment off, `/api/ready` health check and the fixed RF checksum. Creation triggers an initial deployment even with auto-deploy off; stop before applying unless authorized.
5. Supply **`ECHO_BUNDLE_URL`** with the actual public HTTPS asset URL, without credentials/query parameters. The Blueprint pins `ECHO_BUNDLE_SHA256` to the value above and sets `ECHO_REPORT_MODE=precomputed`, `ECHO_PUBLIC_MODEL_POLICY=rf_only`, empty cross-origin allowlist and single-thread numerical libraries. No key or Ollama endpoint is needed. Render translates the public URL/hash environment variables to Docker build arguments. Do not put credentials in build arguments.
6. Review the resource summary: one Free web service, no database/disk/paid resources. Deploy only after approval. Use the Dockerfile CMD; it binds Render's `$PORT`. `ECHO_STATIC_DIR` and data root are set in the image; no `VITE_API_BASE_URL` is needed for same-origin requests.
7. Once the assigned HTTPS URL actually exists, open it, `/api/ready` and `/api/investigator/status`. Confirm policy `rf_only`, precomputed report status and no TabPFN results. Run:

```powershell
# PUBLIC_API_URL must be the actual assigned origin; no placeholder URL is supplied.
cd backend
& ./.venv/mission1/Scripts/python.exe -m ml.verify_api --base-url $env:PUBLIC_API_URL --rf-only --output final_gate_hosted_api_verification.json
```

8. Perform real browser QA on desktop and mobile: archive/search, full 60-second replay, synchronized Ghost, RF diagnosis on 735, concealed-to-Reveal transition, correct cycle 5, four genuine precomputed reports, honest fallback on other cycles and RF evaluation. Confirm TabPFN selection/report requests are unavailable. Inspect cold-start/retry behavior; record actual URLs/statuses and defects.
9. If Docker/Free deployment fails, preserve the error. Native fallback: separate static frontend plus the same RF-only FastAPI using `requirements-demo.txt`, `ml.install_demo`, `ECHO_DATA_ROOT`, `ECHO_REPORT_MODE=precomputed` and `ECHO_PUBLIC_MODEL_POLICY=rf_only`; set the exact real HTTPS API origin in `VITE_API_BASE_URL` and the exact frontend origin in `ECHO_CORS_ORIGINS`. Do not switch to a paid plan without approval. If hosting cannot finish, use a genuine local recording and honest reproducibility instructions if the challenge allows it.
10. Capture the actual media in [RELEASE_MEDIA.md](RELEASE_MEDIA.md), review [DEV_SUBMISSION.md](DEV_SUBMISSION.md), upload only with approval, and replace editorial media tasks with verified working links. Keep `devchallenge` and `hf26challenge`. Claim Gemma based on genuine execution; claim Render only after verified hosting. Do not claim a DEV entry until the owner provides the published entry URL and entry confirmation is checked.

## Evidence and current limits

Final commands/results are in [RUN_LOG.md](RUN_LOG.md). The old article/comparison remain private; no numerical research result was changed or retrained. The source/history scanner reports locations only. Ten existing screenshots are unchanged and were previously visually reviewed; no visible credential was found. Browser/native automation is still unavailable, so no new screenshots/video or current mobile visual verification is claimed.
