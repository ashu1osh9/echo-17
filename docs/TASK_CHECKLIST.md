# ECHO-17 — TASK CHECKLIST (working board)

Legend: `[x]` = present and locally verified, `[~]` = code exists but **not run against real data**, `[ ]` = not done. This is **not** a claim that the hackathon submission is ready.

**HARD DEADLINE: 31 Oct, 20:00 IST. Code freeze: 31 Oct, 15:00 IST. Working demo gate: 30 Oct, 21:00 IST.** Follow [31_OCT_DEADLINE_SPRINT.md](31_OCT_DEADLINE_SPRINT.md).

## Day 0 — Competition + repository
- [ ] **P0 / C01** Verify signed-in DEV Week 4 submission is open; page currently has inconsistent `Live Ended` status. **Done when:** entrant can see working submission flow.
- [ ] **P0 / C02** Create a NEW GitHub repository during Oct 26–31, push project with real dated commit. **Done when:** commit date and repo URL verifiable.
- [x] **P0 / C03** Starter project files present. **Evidence:** backend, frontend, notebook, README exist.
- [x] **P0 / C04** Smoke test backend. **Evidence:** 5 tests passed locally on Oct 29; no dataset run.

## Day 1 — Data + baseline (finish before UI extras)
- [~] **P0 / D01** `backend/ml/download_data.py` downloads raw UCI. **Done when:** real dataset exists on user's machine/Colab; count confirmed.
- [~] **P0 / D02** `backend/ml/prepare.py` extracts real features + replay samples. **Done when:** 2,205 records, 36 predictors, no target leakage, generated files exist.
- [~] **P0 / D03** `backend/ml/train_baseline.py` trains on CPU. **Done when:** exact real accuracy/F1 and prediction CSV saved; train/test split reproducible.
- [ ] **P0 / D04** Write dataset alignment, leakage and split tests. **Done when:** tests pass and intentional bad alignment test fails appropriately.

## Day 2 — TabPFN & integration
- [~] **P0 / M01** `notebooks/tabpfn_colab.ipynb` Colab experiment. **Done when:** real GPU run (if available), model license accepted, artifacts exported.
- [~] **P0 / M02** `backend/ml/train_tabpfn.py` same split. **Done when:** TabPFN metrics + prediction files exist from actual inference.
- [ ] **P0 / M03** Compare macro-F1 and confusion matrix honestly; include failure cases. **Done when:** report in `docs/MODEL_RESULTS.md` with observed numbers, no fabricated scores.
- [~] **P0 / A01** API routes exist. **Done when:** 3 real held-out cycles pass end-to-end API checks.

## Day 3 — UI + optional AI report
- [~] **P1 / U00** Ghost Signature overlay in React / FastAPI. **Code present, isolated unit test passed.** Done when verified against actual measured UCI data, reference is from saved TRAIN IDs with full cooler efficiency, and frontend build passes.
- [~] **P0 / U01** React interface exists. **Done when:** `npm install && npm run build` and local actual-data workflow work.
- [ ] **P1 / U02** Actual replay controls (play/pause/scrub) using recorded samples. **Done when:** chart progressively shows only measured points.
- [ ] **P0 / U03** Ground-truth reveal, misclassification, error states verified. **Done when:** screenshot/video of real output.
- [~] **P1 / G01** Gemma hook exists. **Done when:** real Gemma response shown with `ollama:gemma3:1b` source; otherwise clearly labeled fallback.
- [ ] **P1 / G02** Numeric statement checks. **Done when:** unsupported numbers are flagged/rejected and source evidence preserved.

## Submission day
- [ ] **P0 / S01** Build reliable hosted demo OR record reproducible local demo. **Done when:** every link works; precomputed outputs labeled.
- [ ] **P1 / S02** Render category: hosted frontend/backend on Render. **Done when:** actual public URL can be opened.
- [ ] **P0 / S03** Capture real screenshots/60-second video, no dummy values.
- [ ] **P0 / S04** Publish polished DEV post in English with required tags, actual metrics and links.
- [ ] **P0 / S05** Submit post via challenge page and verify entry before internal target **Oct 31 20:00 IST**.

## When running Codex
- Update items only after executing verification commands; cite filenames and observed results.
- Never mark a feature complete just because code was written.
- Do not let UI, animations or extra components block the P0 ML pipeline.
