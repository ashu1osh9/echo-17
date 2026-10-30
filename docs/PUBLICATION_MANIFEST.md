# Exact publication proposal: RF + Gemma

No push, upload or deployment is authorized yet. The clean local release commit proposes the following source/config/docs/tests, retaining existing project files. The data ZIP is a separate proposed asset, not Git-tracked.

## Proposed public asset

`backend/artifacts/release/echo17-public-rf.zip`: **2,971,364 bytes / 9 members**.

SHA-256: `96dc5038f7526cec9aacdeb27884c0418520a5461f73a1b2ef6b455ebb9d04cd`.

```text
artifacts/baseline_metrics.json
artifacts/baseline_predictions.csv
artifacts/gemma_reports.json
artifacts/test_ids.csv
artifacts/train_ids.csv
data/processed/features.csv
data/processed/preparation_metadata.json
data/processed/signals.npz
manifest.json
```

The registry contains four genuine RF-grounded Gemma reports. No restricted model output, weight, fitted model, raw text, credential, environment, cache or log is included. The manifest retains UCI attribution and preprocessing changes. Empty tracked `.gitkeep` files merely retain directories; they contain no dataset or artifact.

Do not publish the older `echo17-demo.zip`, original restricted artifacts, local weights or `backend/artifacts/release-private/`. Full earlier research documents were preserved with hashes there. The public article reports RF + Gemma and withholds the quantitative restricted-model comparison.

## Changed/added files in the proposed commit

```text
.dockerignore
.gitignore
Dockerfile
README.md
THIRD_PARTY_NOTICES.md
backend/app/main.py
backend/app/report_schema.py
backend/app/services/archive.py
backend/app/services/gemma_service.py
backend/app/services/investigator.py
backend/app/services/precomputed_reports.py
backend/ml/audit_release.py
backend/ml/colab_bundle.py
backend/ml/comparison.py
backend/ml/config.py
backend/ml/experiment.py
backend/ml/install_demo.py
backend/ml/precompute_reports.py
backend/ml/profile_demo.py
backend/ml/release_bundle.py
backend/ml/start_ollama.py
backend/ml/train_tabpfn.py
backend/ml/verify_api.py
backend/ml/verify_investigator.py
backend/requirements-demo.txt
backend/requirements.txt
backend/tests/test_colab_handoff.py
backend/tests/test_investigator.py
backend/tests/test_real_data.py
backend/tests/test_release.py
docs/ARCHITECTURE.md
docs/DEMO_SCRIPT.md
docs/DEV_SUBMISSION.md
docs/DEV_SUBMISSION_DRAFT.md
docs/GEMMA_INVESTIGATOR.md
docs/MODEL_RESULTS.md
docs/PUBLICATION_MANIFEST.md
docs/RELEASE_HANDOFF.md
docs/RELEASE_MEDIA.md
docs/RUN_LOG.md
docs/TABPFN_HANDOFF.md
docs/TASK_CHECKLIST.md
frontend/src/api.ts
frontend/src/components/Comparison.tsx
frontend/src/components/Evaluation.tsx
frontend/src/components/ForensicReport.tsx
frontend/src/components/Investigation.tsx
frontend/src/vite-env.d.ts
frontend/tests/ui.test.tsx
notebooks/tabpfn_colab.ipynb
render.yaml
```

## Complete resulting repository file list

```text
.dockerignore
.gitignore
AGENTS.md
Dockerfile
LICENSE
README.md
THIRD_PARTY_NOTICES.md
backend/.env.example
backend/app/__init__.py
backend/app/main.py
backend/app/report_schema.py
backend/app/services/__init__.py
backend/app/services/archive.py
backend/app/services/gemma_service.py
backend/app/services/ghost.py
backend/app/services/investigator.py
backend/app/services/precomputed_reports.py
backend/artifacts/.gitkeep
backend/data/processed/.gitkeep
backend/data/raw/.gitkeep
backend/ml/__init__.py
backend/ml/audit_release.py
backend/ml/colab_bundle.py
backend/ml/comparison.py
backend/ml/config.py
backend/ml/download_data.py
backend/ml/experiment.py
backend/ml/install_demo.py
backend/ml/precompute_reports.py
backend/ml/prepare.py
backend/ml/profile_demo.py
backend/ml/release_bundle.py
backend/ml/start_ollama.py
backend/ml/train_baseline.py
backend/ml/train_tabpfn.py
backend/ml/verify_api.py
backend/ml/verify_investigator.py
backend/requirements-demo.txt
backend/requirements.txt
backend/tests/test_api.py
backend/tests/test_colab_handoff.py
backend/tests/test_features.py
backend/tests/test_ghost.py
backend/tests/test_investigator.py
backend/tests/test_real_data.py
backend/tests/test_release.py
docs/31_OCT_DEADLINE_SPRINT.md
docs/ARCHITECTURE.md
docs/CODEX_MASTER_PROMPT.md
docs/CODEX_TASK.md
docs/DEMO_SCRIPT.md
docs/DEV_SUBMISSION.md
docs/DEV_SUBMISSION_DRAFT.md
docs/GEMMA_INVESTIGATOR.md
docs/IMPLEMENTATION_PLAN.md
docs/MANUAL_QA.md
docs/MODEL_RESULTS.md
docs/PUBLICATION_MANIFEST.md
docs/RELEASE_HANDOFF.md
docs/RELEASE_MEDIA.md
docs/RUN_LOG.md
docs/START_HERE_29_OCT.md
docs/TABPFN_HANDOFF.md
docs/TASK_CHECKLIST.md
docs/VISUAL_QA.md
docs/WINNING_BLUEPRINT_31_OCT.md
docs/screenshots/mission2-archive-search.png
docs/screenshots/mission2-archive.png
docs/screenshots/polish-archive.png
docs/screenshots/polish-diagnosis-735.png
docs/screenshots/polish-evaluation.png
docs/screenshots/polish-ghost-735.png
docs/screenshots/polish-laptop-1366x768.png
docs/screenshots/polish-mobile-replay-390.png
docs/screenshots/polish-replay-complete-735.png
docs/screenshots/polish-reveal-735.png
frontend/.env.example
frontend/index.html
frontend/package-lock.json
frontend/package.json
frontend/src/App.tsx
frontend/src/api.ts
frontend/src/components/Archive.tsx
frontend/src/components/Comparison.tsx
frontend/src/components/Evaluation.tsx
frontend/src/components/ForensicReport.tsx
frontend/src/components/Investigation.tsx
frontend/src/components/Replay.tsx
frontend/src/domain.ts
frontend/src/main.tsx
frontend/src/style.css
frontend/src/vite-env.d.ts
frontend/tests/domain.test.mjs
frontend/tests/run-tests.mjs
frontend/tests/ui.test.tsx
frontend/tests/verify-preview.mjs
frontend/tsconfig.json
frontend/vite.config.ts
notebooks/tabpfn_colab.ipynb
render.yaml
```

## Approval gates

Owner confirmation of key rotation and explicit source-push, RF-asset, deployment and publication approval remain required. No paid resource or DEV entry is authorized. No public/video URL has been invented. Current images are genuine historical RF evidence; fresh report/mobile/video captures remain pending.

The scanner found only the intentional invalid-URL test fixture; public generated-asset scans found no secret pattern. This is a scoped audit, not exhaustive certification. The final commit hash fixes the exact proposed source contents; consult RUN_LOG.md and RELEASE_HANDOFF.md for observed checks and precise owner steps.
