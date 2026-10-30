import json
import os
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


def tabpfn_state():
    if os.environ.get("ECHO_PUBLIC_MODEL_POLICY") == "rf_only":
        return {"available": False, "status": "restricted", "detail": "Public demo serves Random Forest only. TabPFN remains an offline research experiment; public-output permission is unconfirmed."}, None, None
    paths = [ARTIFACTS / name for name in ("tabpfn_predictions.csv", "tabpfn_metrics.json")]
    if not any(p.exists() for p in paths):
        return {"available": False, "status": "missing", "detail": "No validated TabPFN GPU outputs imported."}, None, None
    try:
        from ml.colab_bundle import read_validated_results
        metric, frame = read_validated_results(ARTIFACTS.parent)
        return {"available": True, "status": "validated", "model": metric["model"],
                "model_version": metric["model_version"], "inference_mode": metric["inference_mode"]}, metric, frame
    except (ValueError, KeyError, TypeError, OSError):
        return {"available": False, "status": "invalid", "detail": "TabPFN outputs rejected by provenance, split or prediction validation."}, None, None


def additional():
    _, _, frame = tabpfn_state()
    return frame.set_index("cycle_id") if frame is not None else None


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
    state, metric, tab = tabpfn_state()
    if tab is not None:
        result.append(rec(tab.set_index("cycle_id"), metric["model"]))
    row = features().loc[cycle_id]
    evidence = [{"sensor": sensor, "unit": unit,
                 **{stat: float(row[f"{sensor}_{stat}"]) for stat in ("mean", "std", "min", "max", "p05", "p95")}}
                for sensor, (_, unit) in SENSORS.items()]
    return {"cycle_id": cycle_id, "predictions": result, "ground_truth_hidden": True,
            "inference_mode": "precomputed from model inference", "feature_evidence": evidence,
            "tabpfn_status": state}


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
    for name in ("baseline_metrics.json",):
        p = ARTIFACTS / name
        if p.exists():
            output.append(json.loads(p.read_text()))
    if not output:
        raise HTTPException(503, "Train baseline model first")
    _, metric, _ = tabpfn_state()
    if metric is not None:
        output.append(metric)
    return output


def comparison():
    state, metric, candidate = tabpfn_state()
    if candidate is None:
        return {"available": False, "tabpfn_status": state, "comparison": None}
    from ml.comparison import compare_predictions
    from ml.experiment import load_inputs
    result = compare_predictions(baseline().reset_index(), candidate, load_inputs(ARTIFACTS.parent))
    return {"available": True, "tabpfn_status": state, "comparison": result}
