from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from ml.config import ARTIFACTS, SENSORS, LABELS
from app.services.archive import baseline, prediction, get_signals, evaluation, validate_cycle
from app.services.investigator import investigate
from app.services.ghost import ghost_signature

app = FastAPI(title="ECHO-17 Forensic API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
                   allow_credentials=False, allow_methods=["GET", "POST"], allow_headers=["*"])


@app.get("/api/health")
def health():
    return {"ok": True, "data_ready": (ARTIFACTS / "baseline_predictions.csv").exists()}


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


@app.post("/api/investigate/{cycle_id}")
def report(cycle_id: int):
    return investigate(cycle_id)


@app.get("/api/evaluation")
def metrics():
    return {"results": evaluation()}
