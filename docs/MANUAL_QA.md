# Mission 2 browser verification

## Verified running URLs

- Frontend production preview: [http://127.0.0.1:5173/](http://127.0.0.1:5173/)
- Archive: [http://127.0.0.1:5173/#/archive](http://127.0.0.1:5173/#/archive)
- Investigation: [http://127.0.0.1:5173/#/investigation/735](http://127.0.0.1:5173/#/investigation/735)
- Evaluation: [http://127.0.0.1:5173/#/evaluation](http://127.0.0.1:5173/#/evaluation)
- Backend: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)
- FastAPI documentation: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

The existing background terminals were reused: Vite **preview** on port 5173 and Uvicorn on port 8000. No duplicate servers were started. Frontend HTML, direct health, proxied health and FastAPI docs returned 200. Both health responses were `{"ok":true,"data_ready":true}`.

## Latest focused visual pass

The subsequent focused pass completed the cycle 735 diagnosis/reveal, full 60-second replay with training-reference overlay, evaluation and mobile/laptop checks. The archive hero was compacted and small labels enlarged without redesign. See [VISUAL_QA.md](VISUAL_QA.md) for exact observations, tests and actual archive/diagnosis/reveal/evaluation screenshots. Earlier limitations below are retained as historical context.

## Earlier pass (historical)

Native Chrome opened the application and displayed its real archive dashboard: 441 held-out recordings, six channels, a 60-second recording window, navigation, source attribution and cycle cards. Entering `735` in archive search produced exactly one result, Cycle 0735. The dashboard was seen in a maximized window and a narrower restored window. This was not a full mobile/responsive audit.

Screenshots of those actual observations:

- [Archive dashboard](screenshots/mission2-archive.png)
- [Search result for Cycle 0735](screenshots/mission2-archive-search.png)

The browser connector host was unavailable. Native input subsequently encountered a minimized window, an off-screen result, repeated `user input was detected in this window` responses and a screenshot of an occluding application. Stopped further browser input after recovery attempts. **Replay, Ghost, diagnosis, reveal, report, evaluation and mobile behavior were not visually verified in this pass.** Their automated component/API checks passed separately; see RUN_LOG.md.

## Manual regression checklist

The following are test steps and expected values from actual saved artifacts, not claims that these steps were completed in the browser.

1. **Archive:** open the archive URL. Search `735`; confirm one Cycle 0735 card. Clear search; confirm 441 records, 12 cards on page one and 37 pages. Try Next/Previous. After opening a case, verify the opened/unopened session filters. An unmatched ID should show the no-match state.
2. **Recording and replay:** open the Cycle 735 URL directly. Confirm the selected cycle and PS1 pressure units. Before diagnosis, actual condition must be concealed and Reveal disabled. Test Reset, Play, Pause, the timeline slider and 0.25×–4× speed. Reset starts at 0; replay stops at 60 seconds. The value readout must track the last measured sample at or before the cursor. Changing browser tabs should pause playback.
3. **Sampling and responsiveness:** switch PS1 → FS1 → TS1. PS1/FS1 have 240 displayed preview points; TS1 has 60, ending at 59 seconds. Original sampling rates are 100/10/1 Hz respectively. The axis remains 0–60 seconds; previews use recorded timestamps. Switching channels resets replay and removes the old Ghost overlay.
4. **Ghost Signature:** on PS1, select Reveal Ghost Signature. For cycle 735 the current API selects TRAIN cycle 1850. Confirm both legend entries, synchronized timestamps, measured differences and the train-only explanation. Full cooler efficiency does not establish that every other component is healthy. Switch to TS1 and request a new comparison; the old PS1 overlay must not remain visible.
5. **Diagnosis and explicit reveal:** click Run AI diagnosis. Cycle 735's saved Random Forest prediction is class 3, with probabilities 0.504 for class 3, 0.496 for class 20 and 0 for class 100. Confirm the precomputed-inference label and measured feature table. Actual condition must remain concealed until Reveal Actual Condition. After that click, expect actual class 20 and an incorrect-prediction comparison.
6. **Correct case and state reset:** select cycle 5. The previous truth, prediction and report must disappear; Reveal must be disabled again. Diagnose and reveal: saved prediction 3, actual 3, predicted-class probability 0.628. Expect a matching-prediction comparison. Switch cases while a request is pending; no previous case output should appear in the new case.
7. **Investigation report:** after diagnosis click Generate investigation. In the verified local environment the API returns `deterministic fallback (Gemma unavailable)`. Confirm the UI says Rule-based / non-LLM fallback, includes measured evidence and does not claim a Gemma response.
8. **Evaluation:** open the evaluation URL. Expect accuracy **99.32%** (rounded), macro-F1 **0.9932** (rounded), 441 test and 1,764 train cycles. Confusion matrix rows/columns ordered 3/20/100: `[[146,0,1],[1,145,0],[1,0,147]]`. Audit links should include cycles 2, 735 and 1467. Confirm the random-split/unseen-machine limitation.
9. **Mobile, keyboard and error behavior:** use browser responsive mode at 390×844, 768×1024 and 1440×900. Check navigation, sensor tabs, chart, transport controls, buttons and report remain usable. Wide feature tables may scroll within their own container; the entire page should not require horizontal scrolling. Tab through controls and confirm visible focus. Open `#/investigation/0` and `#/does-not-exist`; expect explicit not-found messages. Check the browser console for application errors and capture actual investigation/reveal/evaluation screenshots.

Keep the two existing servers running for these checks. No dataset download, preparation, model training, deployment or push is needed.
