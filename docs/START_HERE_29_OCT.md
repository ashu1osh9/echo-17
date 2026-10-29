# ECHO-17 — START HERE (29 October 2026)

## Mission and gates

- **31 Oct, 20:00 IST:** Internal target: published DEV Week 4 submission with valid working demo, GitHub repo, English write-up.
- **30 Oct, 21:00 IST:** Working real-data baseline/API/React demonstration (no synthetic predictions).
- **31 Oct, 15:00 IST:** Freeze new features; only fix bugs, test links, record demo, publish.
- Verify signed-in DEV Week 4 submission is enabled first; official public page inconsistently says `Live Ended` despite its Oct 31 deadline.

## 1. Extract ZIP on Windows

Example folder: `D:\\AI_Space\\echo-17`. Open this exact `echo-17` folder in VS Code (the folder containing `AGENTS.md`). Do not scaffold a second app.

## 2. GitHub repo (create new public `echo-17` repo first)

From project root in PowerShell:

```powershell
git init
git add .
git commit -m "Initial ECHO-17 forensic AI build"
git branch -M main
git remote add origin https://github.com/ashu1osh9/echo-17.git
git push -u origin main
```

If `origin` already exists, check `git remote -v` instead of blindly adding it. Do not upload venv, sensor files, secrets, or model weights. New repo must be created during challenge window.

## 3. Run the real-data baseline — NO GPU required

Open Terminal 1 in VS Code, at repo root:

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m pytest -q
python -m ml.download_data
python -m ml.prepare
python -m ml.train_baseline
python -m uvicorn app.main:app --reload
```

Run sequentially. **Stop and fix any error before proceeding.** If PowerShell blocks script activation, run the commands with `.\.venv\Scripts\python.exe -m ...` or use the CMD activate script; do not lower security settings unnecessarily.

Expected generated files:

- `backend/data/processed/features.csv` — 2,205 rows, 36 sensor predictors, plus `cycle_id`, cooler label, stability metadata.
- `backend/data/processed/signals.npz` — real samples for replay.
- `backend/artifacts/train_ids.csv`, `test_ids.csv` — reproducible split.
- `backend/artifacts/baseline_metrics.json` — real accuracy and macro-F1.
- `backend/artifacts/baseline_predictions.csv` — real predictions.

Check `http://127.0.0.1:8000/docs` and `http://127.0.0.1:8000/api/health` (`data_ready` should become `true`).

## 4. Frontend — CPU only

Open Terminal 2 from project root:

```powershell
cd frontend
npm install
npm run build
npm run dev
```

Open `http://localhost:5173`. Test archive → cycle → actual recorded signal → baseline diagnosis → Ghost Signature → reveal. Fix any failing API or render states.

## 5. GPU in Colab, ONLY AFTER baseline works

Use `notebooks/tabpfn_colab.ipynb` from this repo. In Colab: Runtime → Change runtime type → T4 GPU (if available); upload **this project's latest ZIP** when prompted. Accept TabPFN license if prompted, run notebook, and download `echo17_results.zip`.

Copy extracted `artifacts/*.csv` and `artifacts/*.json` into `backend/artifacts/`, and `data/processed/*` into `backend/data/processed/`. Ensure same train/test IDs for Random Forest and TabPFN. **No results should be fabricated.** Confirm license before sharing weights; don't commit large artifacts by default.

## 6. Codex prompt — paste in VS Code from repo root

```text
You are implementing ECHO-17 for the DEV Hacktoberfest Week 4 2026 challenge.
HARD DEADLINE: 31 Oct 2026 20:00 IST. P0 live demo must work by 30 Oct 21:00 IST.

Read AGENTS.md, README.md, docs/START_HERE_29_OCT.md,
docs/WINNING_BLUEPRINT_31_OCT.md, docs/31_OCT_DEADLINE_SPRINT.md,
and docs/TASK_CHECKLIST.md. This is an EXISTING project: do not scaffold or rewrite it.

START WITH P0 ONLY:
1. Inspect the repo and run backend pytest.
2. Fix setup/runtime issues, then download the real UCI 447 hydraulic dataset.
3. Validate exactly 2205 aligned cycles and the 36 sensor-statistics predictors.
4. Confirm that no label/metadata leaks into the model input.
5. Run the Random Forest baseline and record REAL accuracy, macro-F1,
   class counts, confusion matrix, split IDs, and wrong predictions.
6. Launch FastAPI, test /api/health, /api/cycles, /api/diagnose/{id},
   /api/ghost/{id}, /api/reveal/{id}, /api/evaluation against real outputs.
7. Run frontend npm install, npm run build, npm run dev, and verify
   the complete real-data UI investigation. Fix any errors.
8. Update docs/TASK_CHECKLIST.md with only verified checks.

NO fabricated data, results, metrics, screenshots, or mocked inference presented as real.
No new unrelated frameworks. Work independently through normal dependency installs
and tests, but flag any license acceptance or account-authentication step for me.
Return: changed files, exact commands and real observed outputs, current blockers,
and the next milestone to run on Colab. Do not claim success on tests you did not run.
```

## If something fails

- `py -3.12` missing: `py -0p` to list installed interpreters; use Python 3.11 or 3.12.
- `Activate.ps1` blocked: use `.\.venv\Scripts\python.exe -m pip ...` and the same Python executable for ML commands.
- Dataset download fails: download from UCI 447 manually and extract needed `PS1.txt`, `FS1.txt`, `TS1.txt`, `TS2.txt`, `VS1.txt`, `EPS1.txt`, `profile.txt` into `backend/data/raw/`.
- `npm` not recognized: install Node.js LTS, reopen VS Code terminal and test `node -v` / `npm -v`.
- `data_ready` false: run the preprocessing and baseline commands, then refresh the API.
- Do NOT paste personal tokens, keys, or full environment secrets into public logs.

## What to send back for review

The actual terminal output of `python -m ml.train_baseline` (accuracy/macro-F1), the `/api/health` JSON, and any error traceback or screenshot of the real UI. We can then evaluate model quality and choose the next change.
