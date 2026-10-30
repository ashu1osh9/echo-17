# Focused visual QA and polish

The existing premium dark forensic design was preserved. This pass changed only spacing, small-label readability, human-readable condition comparisons and their regression coverage. Real browser screenshots were captured with native Chrome; no screenshot was generated, composited or altered.

## Verified behavior

| Check | Observed result |
|---|---|
| Archive density | At the same 1536×912 browser-window size, the first card row starts around y=727 versus y=837 in the earlier archive screenshot, roughly 110 pixels higher. Palette, navigation, emblem and card composition retained. |
| Laptop replay visibility | Waveform and transport visible above the fold in the native maximized window and Chrome emulation at 1366×768. Verified after the compact title/chart spacing changes. |
| Mobile layout | Chrome responsive viewport width 390; automatic height about 738. Navigation fits, sensor tabs scroll within their strip, waveform stays within the panel, and play/reset/speed/timeline controls fit without clipping. Also inspected the restored narrower desktop window. |
| Full replay | Started cycle 735 PS1 from the full preview at 1×. At about 22 seconds wall time the cursor read about 21.8 seconds and both traces had progressed together. At about 65.7 seconds wall time it had automatically stopped at 60.0, displayed Play again and showed 240/240 preview samples. No scrubbing or speed change during that browser run. |
| Ghost Signature | Selected real full-cooler-efficiency TRAIN recording 1850. Dashed amber reference and cyan target share the supplied time axis and advance together. Displayed preview mean difference −4.102 bar; aligned preview RMSE 4.815 bar. These describe displayed measurements, not causality. |
| Diagnosis before reveal | Cycle 735 predicted **Near failure (3%)**. Model probabilities: 50.4% near failure, 49.6% reduced efficiency, 0.0% full efficiency. The actual condition remained concealed. Precomputed-inference label and measured feature evidence retained. |
| Explicit reveal | Clicking Reveal Actual Condition displayed **Reduced efficiency (20%)**, with **Prediction differs**. The comparison now names both conditions, rather than using unexplained numeric codes. |
| Evaluation | Browser displayed accuracy 99.32%, macro-F1 0.9932, 441 test and 1,764 train cycles. Matrix `[[146,0,1],[1,145,0],[1,0,147]]`; actual saved error links 2, 735, 1467. Class-name legend is populated from API metadata. |

The 1366×768 screenshot includes Chrome's responsive toolbar, which establishes the emulated dimensions; its on-screen preview uses Fit to window scaling. These checks cover the named sizes and workflows, not every device, browser or accessibility mode. The browser console showed no logged application exceptions during the responsive inspection; DevTools indicated two issues, which were not diagnosed as application exceptions or investigated in this focused pass.

## Actual screenshots

- [Polished archive](screenshots/polish-archive.png)
- [Cycle 735 diagnosis, before actual-label reveal](screenshots/polish-diagnosis-735.png)
- [Cycle 735 explicit reveal and incorrect prediction](screenshots/polish-reveal-735.png)
- [Evaluation metrics, full confusion matrix and error cases](screenshots/polish-evaluation.png)
- [Measured Ghost overlay](screenshots/polish-ghost-735.png)
- [Completed 60-second replay at 1×](screenshots/polish-replay-complete-735.png)
- [390-pixel mobile replay controls](screenshots/polish-mobile-replay-390.png)
- [1366×768 laptop replay visibility](screenshots/polish-laptop-1366x768.png)

## Changes and verification

Changed `frontend/src/style.css`, `frontend/src/components/Investigation.tsx`, `frontend/src/components/Evaluation.tsx`, `frontend/src/App.tsx` and `frontend/tests/ui.test.tsx`. The styles compact the archive hero and laptop investigation header/chart while raising small-label sizes. API-provided condition names are included in the reveal comparison and evaluation legend. The existing real-data React test now drives the animation clock through a complete recording, asserting the 60-second endpoint, stopped animation and all 240 aligned overlay points. That controlled-clock regression test is separate from the actual 1× browser replay above.

Commands actually run from `frontend`:

```powershell
npm.cmd run build
npm.cmd test
npm.cmd run check:preview
```

Results: build passed, Vite 6.4.5, 2,203 modules, 4.60s; 11 frontend tests passed, no failures/skips, 2890.4896 ms; 9 production asset/proxy checks passed. Build JS sizes: initial 175.16 kB, evaluation 5.32 kB, replay 425.89 kB; CSS 32.95 kB. No chunk-size warning.

Commands actually run from `backend`:

```powershell
& ./.venv/mission1/Scripts/python.exe -m pytest -q
& ./.venv/mission1/Scripts/python.exe -m ml.verify_api --base-url http://127.0.0.1:5173 --output polish_api_verification.json
```

Results: 12 backend tests passed, one existing Starlette/httpx deprecation warning, 4.53s; 44 HTTP checks passed through the production preview proxy. All four investigator responses were explicitly labeled deterministic fallback; no actual Gemma run is claimed. Node's test runner also emits its existing experimental TypeScript-stripping warning.

Both original background terminals were reused. The model, baseline metrics, predictions and train/test IDs all passed SHA-256 equality checks against the earlier recorded hashes. No raw data, processed data, model or saved model-output file was changed. New HTTP verification evidence has a separate ignored filename. No training, download, deployment, commit or push occurred.

Frontend remains [http://127.0.0.1:5173/](http://127.0.0.1:5173/); backend docs remain [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs). DevTools was closed after inspection. Broader browser/device coverage, TabPFN execution, actual Gemma, demo video and submission remain separate work.
