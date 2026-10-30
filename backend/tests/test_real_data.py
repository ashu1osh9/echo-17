"""Integration checks consume genuine local pipeline outputs; skip when absent."""
import json
from functools import lru_cache

import numpy as np
import pandas as pd
import pytest
import requests
from fastapi.testclient import TestClient
from sklearn.metrics import accuracy_score, f1_score

from app.main import app
from app.services import archive, ghost, investigator
from ml.config import ARTIFACTS, PROCESSED, SENSORS
from ml.prepare import model_features
from ml.train_baseline import split_indices


@pytest.fixture
def real_data():
    if not (ARTIFACTS / "baseline_predictions.csv").exists():
        pytest.skip("Run the real UCI preparation and baseline first")
    return pd.read_csv(PROCESSED / "features.csv"), pd.read_csv(ARTIFACTS / "baseline_predictions.csv")


def test_real_split_and_metrics(real_data):
    frame, predictions = real_data
    train = pd.read_csv(ARTIFACTS / "train_ids.csv").cycle_id.tolist()
    test = pd.read_csv(ARTIFACTS / "test_ids.csv").cycle_id.tolist()
    assert len(frame) == 2205 and model_features(frame).shape == (2205, 36)
    tr, te = split_indices(frame)
    assert train == frame.iloc[tr].cycle_id.tolist()
    assert test == frame.iloc[te].cycle_id.tolist()
    assert len(train) == 1764 and len(test) == 441 and not set(train) & set(test)
    assert set(predictions.cycle_id) == set(test)
    metrics = json.loads((ARTIFACTS / "baseline_metrics.json").read_text())
    assert metrics["accuracy"] == accuracy_score(predictions.actual, predictions.predicted)
    assert metrics["macro_f1"] == f1_score(predictions.actual, predictions.predicted, average="macro")
    assert metrics["test_ids"] == test
    assert metrics["timestamp_utc"] and metrics["versions"]["scikit-learn"]


def test_all_routes_with_real_cycles(real_data, monkeypatch):
    frame, predictions = real_data
    def unavailable(*args, **kwargs):
        raise investigator.gemma_service.GemmaUnavailable("ollama_unreachable")
    monkeypatch.setattr(investigator.gemma_service, "generate_plan", unavailable)
    client = TestClient(app)
    assert client.get("/api/health").json() == {"ok": True, "data_ready": True}
    assert len(client.get("/api/meta").json()["sensors"]) == 6
    cycles = client.get("/api/cycles?limit=441").json()
    assert cycles["total"] == 441 and len(cycles["cycles"]) == 441
    assert all(set(c) == {"id"} for c in cycles["cycles"])
    ids = predictions.groupby("actual").first().cycle_id.astype(int).tolist()
    ids += predictions.loc[predictions.actual != predictions.predicted, "cycle_id"].astype(int).tolist()[:1]
    ids += predictions.loc[predictions.actual == predictions.predicted, "cycle_id"].astype(int).tolist()[:1]
    train_ids = set(pd.read_csv(ARTIFACTS / "train_ids.csv").cycle_id)
    with np.load(PROCESSED / "signals.npz") as measured:
        for cycle_id in ids:
            for sensor in SENSORS:
                response = client.get(f"/api/cycles/{cycle_id}/signals?sensor={sensor}")
                assert response.status_code == 200
                signal = response.json()
                np.testing.assert_allclose(signal["values"], measured[sensor][cycle_id - 1], atol=0.000051)
                assert len(signal["times"]) == len(signal["values"])
                response = client.get(f"/api/ghost/{cycle_id}?sensor={sensor}")
                assert response.status_code == 200
                overlay = response.json()
                ref = overlay["reference_cycle_id"]
                assert ref in train_ids
                assert frame.set_index("cycle_id").loc[ref, "cooler_condition"] == 100
                np.testing.assert_allclose(overlay["reference_values"], measured[sensor][ref - 1], atol=0.000051)
            result = client.post(f"/api/diagnose/{cycle_id}").json()
            expected = predictions.set_index("cycle_id").loc[cycle_id]
            assert result["predictions"][0]["condition"] == expected.predicted
            assert "actual" not in result and result["ground_truth_hidden"] is True
            assert result["inference_mode"] == "precomputed from model inference"
            assert len(result["feature_evidence"]) == 6
            for evidence in result["feature_evidence"]:
                assert evidence["mean"] == frame.set_index("cycle_id").loc[cycle_id, f"{evidence['sensor']}_mean"]
                assert set(evidence) == {"sensor", "unit", "mean", "std", "min", "max", "p05", "p95"}
            report = client.post(f"/api/investigate/{cycle_id}")
            assert report.status_code == 200
            assert report.json()["source"].startswith("deterministic fallback")
            assert len(report.json()["structured_evidence"]) == 6
            assert client.post(f"/api/reveal/{cycle_id}").json()["actual"] == expected.actual
    assert client.get("/api/evaluation").status_code == 200
    for path in ("/docs", "/redoc", "/openapi.json"):
        assert client.get(path).status_code == 200
    for path in ("/api/cycles/0/signals", "/api/ghost/0"):
        assert client.get(path).status_code == 404
    for path in ("/api/diagnose/0", "/api/reveal/0", "/api/investigate/0"):
        assert client.post(path).status_code == 404
    for path in (f"/api/cycles/{ids[0]}/signals?sensor=bad", f"/api/ghost/{ids[0]}?sensor=bad"):
        assert client.get(path).status_code == 404
    assert client.get("/api/cycles?limit=442").status_code == 422
    assert client.post("/api/diagnose/not-an-id").status_code == 422


def test_ghost_selection_ignores_held_out_labels(real_data, monkeypatch):
    frame, predictions = real_data
    frame = frame.set_index("cycle_id")
    cycle_id = int(predictions.iloc[0].cycle_id)
    monkeypatch.setattr(ghost, "features", lambda: frame)
    original = ghost.select_reference(cycle_id)
    frame.loc[predictions.cycle_id, "cooler_condition"] = 100
    frame.loc[predictions.cycle_id, "stable"] = 1
    assert ghost.select_reference(cycle_id) == original


def test_missing_data_routes(tmp_path, monkeypatch):
    monkeypatch.setattr(archive, "ARTIFACTS", tmp_path)
    # Isolate caches without disturbing real-data tests or requiring fake records.
    monkeypatch.setattr(archive, "baseline", lru_cache(maxsize=1)(archive.baseline.__wrapped__))
    from app import main
    monkeypatch.setattr(main, "ARTIFACTS", tmp_path)
    monkeypatch.setattr(main, "baseline", archive.baseline)
    client = TestClient(app)
    assert client.get("/api/health").json()["data_ready"] is False
    for path in ("/api/cycles", "/api/cycles/1/signals", "/api/ghost/1", "/api/evaluation"):
        assert client.get(path).status_code == 503
    for path in ("/api/diagnose/1", "/api/reveal/1", "/api/investigate/1"):
        assert client.post(path).status_code == 503
