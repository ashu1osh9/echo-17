# ECHO-17 — TASK CHECKLIST (working board)

Legend: `[x]` = present and locally verified, `[~]` = code exists but **not run against real data**, `[ ]` = not done. This is **not** a claim that the hackathon submission is ready.

**HARD DEADLINE: 31 Oct, 20:00 IST. Code freeze: 31 Oct, 15:00 IST. Working demo gate: 30 Oct, 21:00 IST.** Follow [31_OCT_DEADLINE_SPRINT.md](31_OCT_DEADLINE_SPRINT.md).

## Day 0 — Competition + repository
- [ ] **P0 / C01** Verify signed-in DEV Week 4 submission is open; page currently has inconsistent `Live Ended` status. **Done when:** entrant can see working submission flow.
- [ ] **P0 / C02** Create a NEW GitHub repository during Oct 26–31, push project with real dated commit. **Done when:** commit date and repo URL verifiable.
- [x] **P0 / C03** Starter project files present. **Evidence:** backend, frontend, notebook, README exist.
- [x] **P0 / C04** Smoke test backend. **Evidence:** 5 tests passed locally on Oct 29; no dataset run.

## Day 1 — Data + baseline (finish before UI extras)
- [x] **P0 / D01** Real UCI archive downloaded locally. **Evidence:** [RUN_LOG.md](RUN_LOG.md); profile `(2205, 5)` and all six sensor matrices validated.
- [x] **P0 / D02** Real features/replay generated: 2,205 rows, 36 sensor-only predictors; source hashes in `backend/data/processed/preparation_metadata.json` (gitignored).
- [x] **P0 / D03** CPU Random Forest executed: accuracy `0.9931972789115646`, macro-F1 `0.9932124418669938`; saved predictions, metadata and shared 1,764/441 split. See [MODEL_RESULTS.md](MODEL_RESULTS.md).
- [x] **P0 / D04** Alignment/sampling rejection, feature allowlist, deterministic disjoint split and real-artifact checks pass. **Evidence:** 12 tests passed, no skips after training; run log records command.

## Day 2 — TabPFN & integration
- [~] **P0 / M01** `notebooks/tabpfn_colab.ipynb` Colab experiment. **Done when:** real GPU run (if available), model license accepted, artifacts exported.
- [~] **P0 / M02** `backend/ml/train_tabpfn.py` same split. **Done when:** TabPFN metrics + prediction files exist from actual inference.
- [ ] **P0 / M03** Compare macro-F1 and confusion matrix honestly; include failure cases. **Done when:** report in `docs/MODEL_RESULTS.md` with observed numbers, no fabricated scores.
- [x] **P0 / A01** All nine API routes verified over HTTP on real cycles 2, 735, 1467, 5; 44 checks passed, including incorrect predictions and invalid input. Missing-artifact behavior also passed in pytest. Investigator returned labeled non-LLM fallback. See [RUN_LOG.md](RUN_LOG.md).

## Day 3 — UI + optional AI report
- [x] **P1 / U00** Ghost overlay verified with measured UCI data and full-cooler-efficiency TRAIN references; aligned preview differences and stale-sensor/cycle rejection tested. Cycle 735/TRAIN 1850 overlay visually inspected through a complete 1× replay; [actual screenshots](VISUAL_QA.md).
- [x] **P0 / U01** Dependencies installed, production build passed; real-API React component investigation passed on correct cycle 5 and incorrect cycle 735. Archive, laboratory and evaluation routes implemented. Browser visual QA remains a separate unverified gate.
- [x] **P1 / U02** Play/pause/reset, scrub and speed controls implemented and component-tested; progressive points use actual timestamps at 1/10/100 Hz source sampling rates. Browser 60-second cycle 735 replay at 1× completed and stopped at 60.0 with 240/240 aligned target/reference points; [visual QA evidence](VISUAL_QA.md).
- [x] **P0 / U03** Correct/incorrect reveal, stale requests, hidden labels and retry/error states verified by component/API tests. Cycle 735 diagnosis, concealed label, explicit reduced-efficiency reveal and incorrect comparison visually verified; actual diagnosis/reveal screenshots saved. Correct cycle 5 remains covered by real-API component tests. [Focused visual QA](VISUAL_QA.md).
- **Mission 2 recheck:** existing preview/API terminals reused; 11 frontend tests, 12 backend tests, 9 preview checks and 44 API checks passed again. Archive dashboard/search now inspected in native Chrome with [actual screenshots and manual QA steps](MANUAL_QA.md). Full investigation/reveal/evaluation/mobile visual checks remain pending after repeated native window/input interruptions; U03 remains incomplete.
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
