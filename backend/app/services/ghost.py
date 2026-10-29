"""Evidence-only comparison against an actual full-cooler-efficiency TRAIN cycle.

The reference is selected from the training split, never from held-out labels.
Similarity is descriptive; it is not a causal or calibrated anomaly score.
"""
from functools import lru_cache

import numpy as np
import pandas as pd
from fastapi import HTTPException

from ml.config import ARTIFACTS, PROCESSED, SENSORS
from .archive import features, validate_cycle


@lru_cache(maxsize=1)
def training_ids():
    file = ARTIFACTS / "train_ids.csv"
    if not file.exists():
        raise HTTPException(503, "Training split not prepared. Run the baseline pipeline first.")
    return pd.read_csv(file)["cycle_id"].astype(int).tolist()


def select_reference(cycle_id: int):
    """Select the nearest measured training cycle whose cooler is fully efficient."""
    validate_cycle(cycle_id)
    frame = features()
    ids = frame.index.intersection(training_ids())
    train = frame.loc[ids]
    candidates = train[(train["cooler_condition"] == 100) & (train["stable"] == 0)]
    if candidates.empty:
        candidates = train[train["cooler_condition"] == 100]
    if candidates.empty:
        raise HTTPException(503, "No full-cooler-efficiency training reference is available")
    cols = [c for c in frame.columns if c not in {"cooler_condition", "stable"}]
    scale = train[cols].std(axis=0).replace(0, 1).fillna(1).to_numpy(dtype=float)
    q = frame.loc[cycle_id, cols].to_numpy(dtype=float)
    pool = candidates[cols].to_numpy(dtype=float)
    distances = np.sqrt((((pool - q) / scale) ** 2).mean(axis=1))
    idx = int(np.argmin(distances))
    return int(candidates.index[idx]), float(distances[idx])


def ghost_signature(cycle_id: int, sensor: str):
    if sensor not in SENSORS:
        raise HTTPException(404, "Unknown sensor")
    ref_id, distance = select_reference(cycle_id)
    file = PROCESSED / "signals.npz"
    if not file.exists():
        raise HTTPException(503, "Measured signals missing. Run python -m ml.prepare")
    with np.load(file) as data:
        target = data[sensor][cycle_id - 1].astype(float)
        reference = data[sensor][ref_id - 1].astype(float)
        times = data[f"{sensor}_time"].astype(float).round(3).tolist() if f"{sensor}_time" in data else np.linspace(0, 60, len(target), endpoint=False).round(3).tolist()
    if target.shape != reference.shape:
        raise HTTPException(503, "Sensor sampling alignment mismatch")
    rate, unit = SENSORS[sensor]
    return {
        "cycle_id": cycle_id,
        "sensor": sensor,
        "unit": unit,
        "reference_cycle_id": ref_id,
        "reference_definition": "Real training recording with full cooler efficiency (100%); other components may differ",
        "selection_method": "Nearest standardized sensor-summary profile among eligible training cycles",
        "distance": round(distance, 5),
        "times": times,
        "target_values": np.round(target, 4).tolist(),
        "reference_values": np.round(reference, 4).tolist(),
        "mean_difference": round(float(target.mean() - reference.mean()), 4),
        "interpretation": "Descriptive measured comparison, not a proven cause or anomaly probability",
        "rate_hz_original": rate,
    }
