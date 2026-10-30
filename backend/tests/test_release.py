"""Release checks use genuine local model outputs; no synthetic application data."""
import json
from copy import deepcopy
from pathlib import Path
from zipfile import ZipFile

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import investigator, precomputed_reports
from ml.config import ARTIFACTS, ROOT
from ml.release_bundle import FILES, unpack_bundle
from ml.experiment import sha256


@pytest.fixture(scope="module")
def genuine():
    path = ARTIFACTS / "gemma_reports.json"
    if not path.is_file():
        pytest.skip("Run the genuine Gemma precomputation before release tests")
    return json.loads(path.read_text(encoding="utf-8"))


def test_all_eight_genuine_reports_are_grounded(genuine):
    assert len(genuine["reports"]) == 8
    for value in genuine["reports"]:
        evidence = investigator.build_evidence(value["cycle_id"], value["selected_model"])
        result = precomputed_reports.validate_generated_report(value, evidence)
        assert result.mode == "gemma" and result.inference_mode == "live_local"


@pytest.mark.parametrize("change", ["number", "model", "hash", "target", "reference"])
def test_tampered_saved_reports_are_rejected(genuine, change):
    value = deepcopy(genuine["reports"][0])
    evidence = investigator.build_evidence(value["cycle_id"], value["selected_model"])
    if change == "number": value["sections"][1]["statements"][0] = "Invented temperature 99999"
    elif change == "model": value["selected_model"] = "unavailable"
    elif change == "hash": value["evidence_sha256"] = "0" * 64
    elif change == "target": value["actual"] = 3
    elif change == "reference": value["generation"]["plan"]["healthy_reference_comparison"] = ["ghost_nonexistent"]
    with pytest.raises((ValueError, KeyError)):
        precomputed_reports.validate_generated_report(value, evidence)


def test_precomputed_api_never_calls_local_llm(genuine, monkeypatch):
    monkeypatch.setenv("ECHO_REPORT_MODE", "precomputed")
    monkeypatch.setattr(investigator.gemma_service, "generate_plan", lambda *a: pytest.fail("Public mode must not invoke an LLM"))
    client = TestClient(app)
    status = client.get("/api/investigator/status").json()
    assert status["inference_mode"] == "precomputed"
    for model in ("Random Forest", "TabPFN-3.5"):
        value = client.post("/api/investigate/735", params={"model": model}).json()
        assert value["mode"] == "gemma" and value["inference_mode"] == "precomputed"
        assert value["selected_model"] == model
        assert "No live LLM" in value["warning"]
        assert "actual" not in value
    assert client.get("/api/ready").status_code == 200
    assert client.get("/api/meta", headers={"Origin": "http://127.0.0.1:5173"}).headers["access-control-allow-origin"] == "http://127.0.0.1:5173"
    assert "access-control-allow-origin" not in client.get("/api/meta", headers={"Origin": "https://untrusted.invalid"}).headers


@pytest.mark.parametrize("invalid", [False, True])
def test_missing_or_invalid_precomputed_files_remain_honest(tmp_path, monkeypatch, invalid):
    monkeypatch.setenv("ECHO_REPORT_MODE", "precomputed")
    monkeypatch.setattr(precomputed_reports, "ARTIFACTS", tmp_path)
    monkeypatch.setattr(investigator.gemma_service, "generate_plan", lambda *a: pytest.fail("No LLM call allowed"))
    if invalid:
        (tmp_path / "gemma_reports.json").write_text("not json", encoding="utf-8")
    result = investigator.investigate(735, "Random Forest")
    assert result["mode"] == "fallback" and result["inference_mode"] == "non_llm"
    assert result["fallback_reason"] == ("precomputed_report_invalid" if invalid else "precomputed_report_missing")


def test_compact_bundle_installs_exact_original_bytes(tmp_path):
    source = ARTIFACTS / "release/echo17-public-rf.zip"
    if not source.exists():
        pytest.skip("Export the genuine release bundle first")
    destination = tmp_path / "demo"
    result = unpack_bundle(source, destination, sha256(source))
    assert result["test_count"] == 441 and result["gemma_reports"] == 4
    assert result["model_policy"] == "rf_only"
    assert not (destination / "artifacts/baseline_model.joblib").exists()
    assert not list(destination.rglob("*tabpfn*"))
    for name in FILES:
        if name != "artifacts/gemma_reports.json":
            assert sha256(ROOT / name) == sha256(destination / name)
    with pytest.raises(ValueError, match="Destination already exists"):
        unpack_bundle(source, destination, sha256(source))


@pytest.mark.parametrize("tamper", ["sha", "extra", "checksum"])
def test_bundle_rejects_wrong_checksum_extra_paths_and_modified_data(tmp_path, tamper):
    source = ARTIFACTS / "release/echo17-public-rf.zip"
    if not source.exists():
        pytest.skip("Export the genuine release bundle first")
    path = source
    if tamper != "sha":
        path = tmp_path / "tampered.zip"
        with ZipFile(source) as original, ZipFile(path, "w") as output:
            for name in original.namelist():
                value = original.read(name)
                if tamper == "checksum" and name == "artifacts/baseline_predictions.csv": value += b"modified"
                output.writestr(name, value)
            if tamper == "extra": output.writestr("../outside", "never extract")
    with pytest.raises(ValueError):
        unpack_bundle(path, tmp_path / "rejected", "0" * 64 if tamper == "sha" else sha256(path))
    assert not (tmp_path / "rejected").exists()


def test_public_policy_blocks_copied_restricted_outputs(genuine, tmp_path, monkeypatch):
    monkeypatch.setenv("ECHO_PUBLIC_MODEL_POLICY", "rf_only")
    monkeypatch.setenv("ECHO_REPORT_MODE", "precomputed")
    monkeypatch.setattr(investigator.gemma_service, "generate_plan", lambda *a: pytest.fail("Public mode must not invoke an LLM"))
    public = {**genuine, "reports": [row for row in genuine["reports"] if row["selected_model"] == "Random Forest"]}
    (tmp_path / "gemma_reports.json").write_text(json.dumps(public), encoding="utf-8")
    monkeypatch.setattr(precomputed_reports, "ARTIFACTS", tmp_path)
    client = TestClient(app)
    # Original local TabPFN files still exist; serving must ignore them entirely.
    diagnosis = client.post("/api/diagnose/735").json()
    assert [row["model"] for row in diagnosis["predictions"]] == ["Random Forest"]
    assert diagnosis["tabpfn_status"]["status"] == "restricted"
    assert "actual" not in diagnosis
    assert len(client.get("/api/evaluation").json()["results"]) == 1
    comparison = client.get("/api/comparison").json()
    assert comparison["available"] is False and comparison["comparison"] is None
    report = client.post("/api/investigate/735?model=Random%20Forest").json()
    assert report["inference_mode"] == "precomputed" and report["mode"] == "gemma"
    assert report["selected_model"] == "Random Forest"
    assert client.post("/api/investigate/735?model=TabPFN-3.5").status_code == 404
    assert client.get("/api/ready").status_code == 200


def test_public_registry_rejects_reports_grounded_in_restricted_model(genuine, monkeypatch):
    monkeypatch.setenv("ECHO_PUBLIC_MODEL_POLICY", "rf_only")
    with pytest.raises(ValueError, match="Random Forest reports only"):
        precomputed_reports.read_registry()


def test_old_research_bundle_is_not_a_public_release(tmp_path):
    old = ARTIFACTS / "release/echo17-demo.zip"
    if not old.is_file():
        pytest.skip("Historical research bundle is not present")
    with pytest.raises(ValueError, match="exact deployment allowlist"):
        unpack_bundle(old, tmp_path / "blocked", sha256(old))
    assert not (tmp_path / "blocked").exists()
