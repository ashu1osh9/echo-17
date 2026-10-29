# AGENTS.md — Instructions for coding agents working on ECHO-17

Read `docs/WINNING_BLUEPRINT_31_OCT.md`, `docs/31_OCT_DEADLINE_SPRINT.md`, `docs/IMPLEMENTATION_PLAN.md`, `docs/TASK_CHECKLIST.md`, `README.md` and this file before edits.

**Hard stop:** Complete and verify submission by **31 Oct 2026 20:00 IST**; code freeze 15:00 IST; end-to-end P0 by 30 Oct 21:00 IST. No P1 work before P0 works.

- Preserve the Ghost Signature API/UI: it compares a held-out cycle only against an actual full-cooler-efficiency TRAIN recording; never use held-out labels to choose the reference.

## Project boundaries
- This is a **new Hacktoberfest Week 4 research prototype**, not a production condition-monitoring product.
- Do not overwrite the starter with a fresh scaffold. Prefer minimal modular edits with tests.
- No synthetic sensor waveforms, dummy predictions, manually typed accuracy/F1 scores or hidden hardcoded demo results. Missing data must produce a truthful empty/loading/error state.
- Source truth is UCI 447 `profile.txt`; 2,205 cycle rows are aligned by row across sensor files.
- Classification MVP: cooler condition labels 3/20/100. Never claim remaining-useful-life or imminent failure prediction.
- Predictor columns are sensor summary statistics only. Never include `cycle_id`, cooler label, other condition labels, or stability flag in model X.
- Use the **same saved train/test IDs** for both Random Forest and TabPFN.
- Do not merge train/test, use random data augmentation, or invent robustness metrics.
- Preserve source attribution and respect TabPFN separate non-commercial checkpoint license. Never commit tokens, raw dataset, model weights, venv, `.env` or large generated artifacts.
- No unrelated refactors or new frameworks unless clearly justified.

## Operating mode
1. Work in priority order: eligibility/new repo → real dataset → baseline → TabPFN → API/UI → evidence narrative → demo → English submission.
2. Before edits, identify affected files and expected output. Implement a coherent unit, run tests/build, report exact command and output. Never claim a test was run if it wasn't.
3. Finish the current P0 milestone before P1 additions. If external access/license approval is needed, explain the exact blocker and continue with unrelated P0 work that is possible.
4. Prefer reproducible CLIs, small functions, typed API contracts, descriptive function names, and clear errors.
5. For every model result, save run metadata: seed, test IDs, class counts, version, timestamp, metrics. Report uncertainty and wrong predictions.
6. The UI may reveal actual label after diagnosis for narrative effect; don't describe this as an access-control security feature.
7. When model output is precomputed, label it "precomputed from model inference"; never call it a live server-side GPU prediction.
8. When Ollama/Gemma is unavailable, deterministic fallback must be labeled non-LLM; it does not count as actual Gemma integration for contest entry.
9. Mark checklist items done only with verifiable evidence.

## Verification (from repo root)
```powershell
cd backend
python -m pytest -q
# Only when actual source dataset has been downloaded:
python -m ml.prepare
python -m ml.train_baseline
python -m uvicorn app.main:app --reload
```

```powershell
cd frontend
npm install
npm run build
npm run dev
```

## Completion report format
- **Milestone:** task ID and summary
- **Changed:** file names
- **Commands actually run:** full commands + result
- **Observed output:** exact metrics/errors; no guesses
- **Remaining risks:** blockers, licensing, missing actual evaluation
- **Next task:** next P0 milestone
