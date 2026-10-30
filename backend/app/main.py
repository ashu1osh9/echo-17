from fastapi import FastAPI, Query
import os
from pathlib import Path
from fastapi import HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from ml.config import ARTIFACTS, SENSORS, LABELS
from app.services.archive import baseline, prediction, get_signals, evaluation, validate_cycle, comparison, tabpfn_state
from app.services.investigator import investigate, investigator_status as report_status
from app.services.ghost import ghost_signature
from app.services.gemma_service import service_status
from app.report_schema import ForensicReport

app = FastAPI(title="ECHO-17 Forensic API", version="0.1.0")
origins = os.environ.get("ECHO_CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
app.add_middleware(CORSMiddleware, allow_origins=[value.strip() for value in origins if value.strip()],
                   allow_credentials=False, allow_methods=["GET", "POST"], allow_headers=["*"])


@app.get("/api/health")
def health():
    return {"ok": True, "data_ready": (ARTIFACTS / "baseline_predictions.csv").exists()}


@app.get("/api/ready")
def readiness():
    from ml.config import PROCESSED
    from ml.experiment import load_inputs
    try:
        load_inputs(ARTIFACTS.parent)
    except (ValueError, KeyError, TypeError, OSError):
        raise HTTPException(503, "Validated baseline data is not ready") from None
    if not (PROCESSED / "signals.npz").is_file():
        raise HTTPException(503, "Validated demo data is not ready")
    return {"ready": True, "predictions": "precomputed", "reports": os.environ.get("ECHO_REPORT_MODE", "live_local"),
            "model_policy": os.environ.get("ECHO_PUBLIC_MODEL_POLICY", "research")}


@app.get("/api/meta")
def meta():
    return {"sensors": [{"name": name, "unit": unit, "rate_hz": rate} for name, (rate, unit) in SENSORS.items()],
            "condition_labels": LABELS, "task": "cooler condition classification", "dataset": "UCI 447"}


@app.get("/api/cycles")
def cycles(limit: int = Query(default=80, ge=1, le=441)):
    ids = [int(x) for x in baseline().index[:limit]]
    return {"total": len(baseline()), "cycles": [{"id": i} for i in ids],
            "note": "Real held-out evaluation cycles only. Ground truth is hidden until reveal."}


@app.get("/api/cycles/{cycle_id}/signals")
def signals(cycle_id: int, sensor: str = "PS1"):
    return get_signals(cycle_id, sensor)


@app.get("/api/ghost/{cycle_id}")
def ghost(cycle_id: int, sensor: str = "PS1"):
    return ghost_signature(cycle_id, sensor)


@app.post("/api/diagnose/{cycle_id}")
def diagnose(cycle_id: int):
    return prediction(cycle_id)


@app.post("/api/reveal/{cycle_id}")
def reveal(cycle_id: int):
    validate_cycle(cycle_id)
    actual = int(baseline().loc[cycle_id, "actual"])
    return {"cycle_id": cycle_id, "actual": actual, "label": LABELS[actual]}


@app.get("/api/investigator/status")
def investigator_status():
    return report_status()


@app.post("/api/investigate/{cycle_id}", response_model=ForensicReport)
def report(cycle_id: int, model: str | None = None):
    return investigate(cycle_id, model)


@app.get("/api/evaluation")
def metrics():
    return {"results": evaluation(), "tabpfn_status": tabpfn_state()[0]}


@app.get("/api/comparison")
def model_comparison():
    return comparison()


# Optional single-service fallback. Hash-based frontend routing needs no catch-all rewrite.
static_dir = os.environ.get("ECHO_STATIC_DIR")
if static_dir:
    app.mount("/", StaticFiles(directory=Path(static_dir).resolve(), html=True), name="frontend")
