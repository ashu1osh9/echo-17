# ECHO-17 final RF + Gemma release gate

This is the publication-safe log. Full Missions 1-5 research logs, the complete model comparison and earlier article were preserved byte-for-byte with a SHA-256 manifest in ignored `backend/artifacts/release-private/before-rf-gate/`. Original raw/processed data, model artifacts and evaluation files remain unchanged. No research result was fabricated, replaced or retrained.

## Scope and permission

Read AGENTS.md, planning/deadline docs, README, release handoff/article/media, current source, Docker/Render config and git status before edits. Existing uncommitted Mission 3-5 work was retained. The user authorized a clean local release commit but explicitly withheld authorization to push, deploy, spend or publish. No external write was performed.

Reviewed the official TabPFN-3.5 license. Public-use permission is not confirmed. Therefore the release uses **Random Forest + RF-grounded precomputed Gemma**, excluding restricted model/output files and numerical research disclosures from the public source documents and data bundle. A policy guard also blocks restricted outputs if files are accidentally copied. Offline reproduction/validation code and private evidence are preserved.

The exposed Prior Labs key must be rotated by the owner; this task never reads or prints it. Rotation is still unverified. GitHub API recheck confirms the existing public, non-fork repository was created `2026-10-29T18:11:53Z`, inside the challenge window. The public DEV challenge page still says Live Ended; signed-in access and personal eligibility require owner verification.

## Actual data packaging

Exported `backend/artifacts/release/echo17-public-rf.zip`: **2,971,364 bytes**, **9 members**, SHA-256 **`96dc5038f7526cec9aacdeb27884c0418520a5461f73a1b2ef6b455ebb9d04cd`**. It contains the original six RF experiment input/provenance files, measured NPZ, four genuine RF-grounded Gemma reports and an attributed manifest. Original input bytes are unchanged; the report registry is an RF-only subset of the genuine local runs, not regenerated text.

The installer validates the allowlist, SHA-256, member checksums, size bounds, original baseline split/metrics, measured signal shapes/times and all saved report evidence in isolation. It rejects the older research ZIP and mixed-model report registries. Installed into a new `artifacts/release/rf-public-data`; previous bundles/data were not overwritten.

## Commands actually run

From `D:\AI_Space\echo-17\backend`:

```powershell
& ./.venv/mission1/Scripts/python.exe -m ml.audit_release --history --output artifacts/final_gate_security_audit.json
& ./.venv/mission1/Scripts/python.exe -m ml.release_bundle export artifacts/release/echo17-public-rf.zip
& ./.venv/mission1/Scripts/python.exe -m ml.release_bundle install artifacts/release/echo17-public-rf.zip --destination artifacts/release/rf-public-data --sha256 96dc5038f7526cec9aacdeb27884c0418520a5461f73a1b2ef6b455ebb9d04cd
& ./.venv/mission1/Scripts/python.exe -m pytest -q
& ./.venv/mission1/Scripts/python.exe -m ml.verify_api --base-url http://127.0.0.1:8001 --rf-only --output final_gate_rf_api_verification.json
```

- Backend: **85 passed, 1 warning in 38.14s**, no skips/failures. Starlette/httpx deprecation remains. New tests verify the policy blocks restricted predictions, evaluation, comparison and reports even when original local research files exist; mixed registries and old bundles are rejected.
- RF-only HTTP: **52 checks passed** on cycles **2, 735, 1467, 5**. All four genuine report sources are `ollama:gemma3:1b`, served in precomputed mode. No restricted result was returned; explicit restricted-model report requests were 404. Original RF evaluation, Reveal and Ghost behavior matched the actual artifacts.
- Serving-only profile with isolated RF data and precomputed/rf_only settings: **66 checks**, **167.34 MiB peak Windows working set**, **6.394 seconds after imports**. No weights or live LLM loaded. This is not a Render/Linux capacity or latency guarantee.

From `frontend`:

```powershell
npm.cmd run build
npm.cmd test
$env:ECHO_PREVIEW_URL='http://127.0.0.1:8001'
npm.cmd run check:preview
```

- Production build: **exit 0**, Vite 6.4.5, **2,205 modules, 9.79s**. Initial JS 178.98 kB, evaluation 9.83 kB, replay 425.89 kB, CSS 32.95 kB. No styling redesign or large-chunk warning.
- Frontend: **14 passed**, zero failures/skips, **52349.319 ms**. New actual-API test confirms one RF model, one RF evaluation, no restricted comparison, rejected restricted report request, genuine precomputed Gemma presentation and concealed truth. Existing full replay, timestamp/Ghost alignment, errors, selected-model workflow and Reveal tests remain green. Chart layout is stubbed; this is not visual QA.
- Asset checks: **9 passed** on RF-only same-origin preview; served hashes and real metrics match disk. Node experimental TypeScript-stripping warning remains.

## Deployment and media

Changed the Blueprint to one **Docker Free service**, same-origin static React + FastAPI, automatic deploy off, `/api/ready`, pinned RF bundle hash and `ECHO_PUBLIC_MODEL_POLICY=rf_only`. Docker uses a non-root runtime and only serving dependencies; no weights are copied. Render's official JSON schema accepted the one-service config. Read official Docker docs confirming public URL/hash environment values are translated to build arguments. No credential is required as a build argument.

Docker image build, Linux dependencies, hosted startup and actual mobile behavior remain unverified. No paid resources, Render service or external URL was created. Free-plan cold-start/quota/ephemeral limits and exact Blueprint steps are in RELEASE_HANDOFF.md.

The former local full-research preview was stopped. Current RF-only preview runs on **http://127.0.0.1:8001**, using isolated RF data, precomputed reports and rf_only policy; the original local research/live workflow remains on 5173/8000. These are localhost URLs, not public hosting.

Browser/native inventory remains unavailable (browser access host/native pipe unavailable). No fresh screenshot/video or mobile visual pass is claimed. Ten existing RF screenshots are unchanged from prior visual/security review and contain no visible credential. New report/desktop/mobile/video captures remain owner tasks. The public storyboard and article now show RF's incorrect cycle 735 case, genuine Gemma evidence, explicit Reveal, complete RF evaluation and a correct cycle 5 example. Restricted comparison media stays private.

## Publication record

PUBLICATION_MANIFEST.md lists exact source files and RF ZIP members. The article remains `published: false` with `devchallenge` and `hf26challenge`, real credits and no invented public/video URL. The full earlier comparison/article are private, not deleted. No DEV entry is claimed.

Source/history and generated-asset audit results, staged-file verification and local commit identity will be recorded in the final publication manifest/evidence. Key rotation, explicit push/bundle/deployment/media/article approval, signed-in entry access, actual hosted URL checks and published entry confirmation remain outstanding. Target remains **31 Oct 2026 20:00 IST**.
