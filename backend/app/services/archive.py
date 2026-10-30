import json
from functools import lru_cache
import numpy as np
import pandas as pd
from fastapi import HTTPException
from ml.config import PROCESSED, ARTIFACTS, SENSORS, LABELS


@lru_cache(maxsize=1)
def baseline():
    p = ARTIFACTS / "baseline_predictions.csv"
    if not p.exists():
        raise HTTPException(503, "ML data not prepared. Run download_data, prepare, and train_baseline first.")
    return pd.read_csv(p).set_index("cycle_id")


@lru_cache(maxsize=1)
def additional():
    p = ARTIFACTS / "tabpfn_predictions.csv"
    return pd.read_csv(p).set_index("cycle_id") if p.exists() else None


@lru_cache(maxsize=1)
def features():
    p = PROCESSED / "features.csv"
    if not p.exists():
        raise HTTPException(503, "Features missing. Run python -m ml.prepare")
    return pd.read_csv(p).set_index("cycle_id")


def validate_cycle(cycle_id):
    if cycle_id not in baseline().index:
        raise HTTPException(404, "Cycle not in held-out evaluation archive")


def prediction(cycle_id):
    validate_cycle(cycle_id)
    def rec(df, name):
        row = df.loc[cycle_id]
        return {"model": name, "condition": int(row["predicted"]), "label": LABELS.get(int(row["predicted"]), "Unknown"),
                "confidence": float(row["confidence"]),
                "probabilities": {str(k): float(row[f"p_{k}"]) for k in LABELS if f"p_{k}" in row.index}}
    result = [rec(baseline(), "Random Forest")]
    tab = additional()
    if tab is not None and cycle_id in tab.index:
        result.append(rec(tab, "TabPFN-3.5"))
    row = features().loc[cycle_id]
    evidence = [{"sensor": sensor, "unit": unit,
                 **{stat: float(row[f"{sensor}_{stat}"]) for stat in ("mean", "std", "min", "max", "p05", "p95")}}
                for sensor, (_, unit) in SENSORS.items()]
    return {"cycle_id": cycle_id, "predictions": result, "ground_truth_hidden": True,
            "inference_mode": "precomputed from model inference", "feature_evidence": evidence}


def get_signals(cycle_id, sensor):
    validate_cycle(cycle_id)
    if sensor not in SENSORS:
        raise HTTPException(404, "Unknown sensor")
    p = PROCESSED / "signals.npz"
    if not p.exists():
        raise HTTPException(503, "Replay file missing. Run python -m ml.prepare")
    with np.load(p) as arr:
        values = arr[sensor][cycle_id - 1].astype(float).tolist()
        times = arr[f"{sensor}_time"].astype(float).round(3).tolist() if f"{sensor}_time" in arr else np.linspace(0, 60, len(values), endpoint=False).round(3).tolist()
    return {"cycle_id": cycle_id, "sensor": sensor, "unit": SENSORS[sensor][1],
            "rate_hz_original": SENSORS[sensor][0], "times": times,
            "values": [round(v, 4) for v in values], "source": "UCI original recorded samples (downsampled for display)"}


def evaluation():
    output = []
    for name in ("baseline_metrics.json", "tabpfn_metrics.json"):
        p = ARTIFACTS / name
        if p.exists():
            output.append(json.loads(p.read_text()))
    if not output:
        raise HTTPException(503, "Train baseline model first")
    return output
