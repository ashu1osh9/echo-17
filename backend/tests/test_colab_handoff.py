"""Handoff checks use existing measured UCI/RF artifacts, never fake model inference."""
import ast
import hashlib
import io
import json
import shutil
import sys
from pathlib import Path, PurePosixPath
from zipfile import ZipFile

import pandas as pd
import pytest

from ml import colab_bundle, train_tabpfn
from ml.colab_bundle import BUNDLE_FILES, MANIFEST, export_inputs, import_results, validate_results, verify_bundle
from ml.config import ROOT
from ml.experiment import INPUT_FILES, load_inputs, score_predictions


@pytest.fixture
def experiment(tmp_path):
    if not (ROOT / "artifacts/baseline_predictions.csv").exists():
        pytest.skip("Requires the real UCI preparation and RF baseline")
    root = tmp_path / "project" / "backend"
    for name in BUNDLE_FILES:
        destination = root.parent / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT.parent / name, destination)
    return root


def notebook_unpacker():
    notebook = json.loads((ROOT.parent / "notebooks/tabpfn_colab.ipynb").read_text(encoding="utf-8"))
    function = None
    for cell in notebook["cells"]:
        if cell["cell_type"] == "code":
            assert cell["execution_count"] is None and cell["outputs"] == []
            tree = ast.parse("".join(cell["source"]))
            for node in tree.body:
                if isinstance(node, ast.FunctionDef) and node.name == "unpack_bundle":
                    function = node
    assert function is not None
    namespace = {"Path": Path, "PurePosixPath": PurePosixPath, "ZipFile": ZipFile,
                 "io": io, "hashlib": hashlib, "json": json}
    exec(compile(ast.Module(body=[function], type_ignores=[]), "notebook-unpacker", "exec"), namespace)
    return namespace["unpack_bundle"]


def test_real_input_bundle_and_notebook_roundtrip(experiment, tmp_path):
    before = load_inputs(experiment)
    output = tmp_path / "input.zip"
    report = export_inputs(output, experiment)
    assert report["files"] == len(BUNDLE_FILES)
    assert verify_bundle(output)["status"] == "input bundle verified; inference not run"
    with ZipFile(output) as archive:
        assert set(archive.namelist()) == {f"echo-17/{name}" for name in BUNDLE_FILES} | {MANIFEST}
        assert not any(name.endswith((".joblib", ".npz", ".safetensors", ".env")) for name in archive.namelist())
    unpack = notebook_unpacker()
    root = unpack({"input.zip": output.read_bytes()}, tmp_path / "colab" / "echo-17")
    after = load_inputs(root)
    assert before.hashes == after.hashes
    assert before.train_ids == after.train_ids and before.test_ids == after.test_ids
    assert list(after.frame.loc[after.train_ids].filter(regex="_(mean|std|min|max|p05|p95)$").columns) == list(
        before.frame.filter(regex="_(mean|std|min|max|p05|p95)$").columns)
    with pytest.raises(FileExistsError):
        export_inputs(output, experiment)
    with pytest.raises(ValueError, match="Destination exists"):
        unpack({"input.zip": output.read_bytes()}, root.parent)


def test_bundle_checksum_corruption_is_rejected_before_extraction(experiment, tmp_path):
    source = tmp_path / "source.zip"
    export_inputs(source, experiment)
    damaged = tmp_path / "damaged.zip"
    with ZipFile(source) as original, ZipFile(damaged, "w") as target:
        for name in original.namelist():
            value = original.read(name)
            target.writestr(name, value + b"\n" if name.endswith("features.csv") else value)
    with pytest.raises(ValueError, match="checksum mismatch"):
        verify_bundle(damaged)
    destination = tmp_path / "not-created"
    with pytest.raises(ValueError, match="Checksum mismatch"):
        notebook_unpacker()({"damaged.zip": damaged.read_bytes()}, destination)
    assert not destination.exists()


def test_unexpected_bundle_member_is_rejected(experiment, tmp_path):
    output = tmp_path / "input.zip"
    export_inputs(output, experiment)
    with ZipFile(output, "a") as archive:
        archive.writestr("echo-17/backend/.env", "not a credential; rejection test")
    with pytest.raises(ValueError, match="unexpected"):
        verify_bundle(output)


def test_notebook_rejects_parent_traversal_before_writes(tmp_path):
    payload = b"path rejection check"
    unsafe_name = "echo-17/../outside.txt"
    buffer = io.BytesIO()
    with ZipFile(buffer, "w") as archive:
        archive.writestr(unsafe_name, payload)
        archive.writestr(MANIFEST, json.dumps({"schema_version": 1, "files": {
            unsafe_name: hashlib.sha256(payload).hexdigest()}}))
    destination = tmp_path / "not-created"
    with pytest.raises(ValueError, match="Unsafe bundle path"):
        notebook_unpacker()({"unsafe.zip": buffer.getvalue()}, destination)
    assert not destination.exists()


def test_invalid_zip_has_a_clear_cli_error(tmp_path, monkeypatch, capsys):
    output = tmp_path / "invalid.zip"
    output.write_bytes(b"not a ZIP")
    monkeypatch.setattr(sys, "argv", ["colab_bundle", "verify", str(output)])
    with pytest.raises(SystemExit) as stopped:
        colab_bundle.main()
    assert stopped.value.code == 2
    assert "Colab handoff stopped: File is not a zip file" in capsys.readouterr().err


def test_overlapping_split_is_rejected(experiment):
    train_path = experiment / "artifacts/train_ids.csv"
    train = pd.read_csv(train_path)
    train.loc[0, "cycle_id"] = pd.read_csv(experiment / "artifacts/test_ids.csv").cycle_id.iloc[0]
    train.to_csv(train_path, index=False)
    with pytest.raises(ValueError, match="disjoint"):
        load_inputs(experiment)


def test_changed_test_order_is_rejected(experiment):
    path = experiment / "artifacts/test_ids.csv"
    pd.read_csv(path).iloc[::-1].to_csv(path, index=False)
    with pytest.raises(ValueError, match="baseline run metadata"):
        load_inputs(experiment)


def test_real_rf_predictions_score_without_relabeling(experiment):
    predictions = pd.read_csv(experiment / "artifacts/baseline_predictions.csv")
    metrics = json.loads((experiment / "artifacts/baseline_metrics.json").read_text())
    scores = score_predictions(predictions, load_inputs(experiment))
    for key in ("accuracy", "macro_f1", "confusion_matrix", "classification_report", "wrong_cycle_ids"):
        assert scores[key] == metrics[key]


@pytest.mark.parametrize("damage", ["duplicate", "label", "probability", "confidence", "nan"])
def test_corrupted_real_prediction_table_is_rejected(experiment, damage):
    predictions = pd.read_csv(experiment / "artifacts/baseline_predictions.csv")
    if damage == "duplicate":
        predictions.loc[0, "cycle_id"] = predictions.loc[1, "cycle_id"]
    elif damage == "label":
        predictions.loc[0, "actual"] = -1
    elif damage == "probability":
        predictions.loc[0, "p_3"] = -1
    elif damage == "confidence":
        predictions.loc[0, "confidence"] = -1
    else:
        predictions.loc[0, "p_3"] = float("nan")
    with pytest.raises(ValueError):
        score_predictions(predictions, load_inputs(experiment))


def test_rf_outputs_cannot_be_imported_as_tabpfn(experiment, tmp_path):
    output = tmp_path / "wrong-model.zip"
    with ZipFile(output, "w") as archive:
        archive.write(experiment / "artifacts/baseline_metrics.json", "artifacts/tabpfn_metrics.json")
        archive.write(experiment / "artifacts/baseline_predictions.csv", "artifacts/tabpfn_predictions.csv")
    with pytest.raises(ValueError, match="not an explicitly selected TabPFN"):
        import_results(output, experiment)
    assert not (experiment / "artifacts/tabpfn_metrics.json").exists()
    assert not (experiment / "artifacts/tabpfn_predictions.csv").exists()


def test_result_input_fingerprints_must_match(experiment):
    malformed_manifest = {"model": "TabPFN-3.5", "model_version": "V3_5", "input_sha256": {}}
    with pytest.raises(ValueError, match="input_sha256 differs"):
        validate_results({"tabpfn_metrics.json": json.dumps(malformed_manifest).encode()}, experiment)


def test_missing_optional_model_packages_leave_no_outputs(experiment, monkeypatch, capsys):
    monkeypatch.setattr(train_tabpfn, "load_inputs", lambda: load_inputs(experiment))
    monkeypatch.setattr(train_tabpfn, "ARTIFACTS", experiment / "artifacts")
    monkeypatch.setitem(sys.modules, "torch", None)
    monkeypatch.setattr(sys, "argv", ["train_tabpfn", "--device", "cuda"])
    with pytest.raises(SystemExit) as stopped:
        train_tabpfn.main()
    assert stopped.value.code == 2
    assert "TabPFN/PyTorch unavailable" in capsys.readouterr().err
    assert not (experiment / "artifacts/tabpfn_predictions.csv").exists()


def test_missing_real_inputs_are_an_error(tmp_path):
    with pytest.raises(ValueError, match="Missing data/processed/features.csv"):
        load_inputs(tmp_path)


def test_nonobject_result_json_cannot_break_rf(experiment):
    with pytest.raises(ValueError, match="JSON object"):
        validate_results({"tabpfn_metrics.json": b"[]"}, experiment)


def structural_result_fixture(experiment):
    """TEST ONLY: RF rows plus schema metadata exercise validation, never genuine TabPFN inference.

    These bytes only enter pytest temp directories; never the application's artifact directory.
    A consistent manifest is not proof of execution, as the handoff documentation explains.
    """
    from ml.prepare import FEATURE_COLUMNS
    from ml.config import LABELS
    inputs = load_inputs(experiment)
    prediction_bytes = (experiment / "artifacts/baseline_predictions.csv").read_bytes()
    metric = {**score_predictions(pd.read_csv(io.BytesIO(prediction_bytes)), inputs),
              "model": "TabPFN-3.5", "model_version": "V3_5", "requested_model_version": "V3_5",
              "attempts": [{"model_version": "V3_5", "status": "completed"}], "fallback_reason": None,
              "input_sha256": inputs.hashes, "dataset_sha256": inputs.hashes[INPUT_FILES[0]],
              "train_ids": inputs.train_ids, "test_ids": inputs.test_ids, "feature_columns": list(FEATURE_COLUMNS),
              "seed": 42, "class_counts": inputs.class_counts, "train_count": 1764, "test_count": 441,
              "checkpoint": train_tabpfn.CHECKPOINT, "checkpoint_sha256": "0" * 64,
              "inference_mode": "precomputed from model inference", "timestamp_utc": "2026-10-30T00:00:00+00:00",
              "versions": {key: "TEST ONLY" for key in ("python", "torch", "tabpfn", "numpy", "pandas", "scikit-learn")},
              "devices_used": ["cuda:0"], "device_requested": "cuda", "gpu_name": "TEST ONLY; no GPU run",
              "cuda_version": "TEST ONLY", "uncertainty_note": "TEST ONLY", "model_license": "TEST ONLY",
              "class_mapping": {str(k): v for k, v in LABELS.items()},
              "fit_seconds": 0, "predict_seconds": 0, "predict_proba_seconds": 0, "fit_predict_seconds": 0}
    return prediction_bytes, metric


@pytest.mark.parametrize("damage, message", [
    ("train_ids", "train_ids differs"), ("test_ids", "test_ids differs"),
    ("classes", "classes disagrees"), ("class_mapping", "class_mapping differs"),
    ("dataset_sha256", "dataset_sha256 differs"), ("device", "requires recorded CUDA"),
    ("time", "runtime measurement"), ("fallback", "fallback"), ("checkpoint", "checkpoint differs")])
def test_inconsistent_result_metadata_is_rejected(experiment, damage, message):
    prediction_bytes, metric = structural_result_fixture(experiment)
    if damage in ("train_ids", "test_ids"):
        metric[damage] = metric[damage][::-1]
    elif damage == "classes":
        metric["classes"] = [0, 1, 2]
    elif damage in ("class_mapping", "dataset_sha256"):
        metric[damage] = {}
    elif damage == "device":
        metric["devices_used"] = ["cpu"]
    elif damage == "time":
        metric["predict_seconds"] = float("nan")
    elif damage == "checkpoint":
        metric["checkpoint"] = "another-model.safetensors"
    else:
        metric["requested_model_version"] = "V3_5_FAST"
    contents = {"tabpfn_predictions.csv": prediction_bytes, "tabpfn_metrics.json": json.dumps(metric).encode()}
    with pytest.raises(ValueError, match=message):
        validate_results(contents, experiment)


def test_import_schema_roundtrip_only_in_temp_and_preserves_baseline(experiment, tmp_path, monkeypatch):
    prediction_bytes, metric = structural_result_fixture(experiment)
    before = load_inputs(experiment).hashes
    path = tmp_path / "TEST_ONLY_schema.zip"
    with ZipFile(path, "w") as archive:
        archive.writestr("artifacts/tabpfn_predictions.csv", prediction_bytes)
        archive.writestr("artifacts/tabpfn_metrics.json", json.dumps(metric))
    from ml.colab_bundle import check_results
    assert check_results(path, experiment)["test_count"] == 441
    assert not (experiment / "artifacts/tabpfn_predictions.csv").exists()
    import_results(path, experiment)
    assert load_inputs(experiment).hashes == before
    comparison = json.loads((experiment / "artifacts/model_comparison.json").read_text())
    assert comparison["counts"] == {"both_correct": 438, "both_wrong": 3, "tabpfn_improved": 0,
                                    "tabpfn_worse": 0, "disagreements": 0}
    from app.services import archive
    from app.main import app
    from fastapi.testclient import TestClient
    monkeypatch.setattr(archive, "ARTIFACTS", experiment / "artifacts")
    client = TestClient(app)
    diagnosis = client.post("/api/diagnose/735").json()
    assert diagnosis["tabpfn_status"]["available"] is True
    assert len(diagnosis["predictions"]) == 2 and "actual" not in diagnosis
    assert client.get("/api/comparison").json()["comparison"]["counts"] == comparison["counts"]


def test_fast_retry_only_on_cuda_oom(monkeypatch):
    from types import SimpleNamespace
    class TestOnlyCudaOOM(Exception):
        pass
    visited = []
    def attempt(inputs, variant, *unused):
        visited.append(variant)
        if variant == "V3_5":
            raise TestOnlyCudaOOM()
        return "control-flow-test-only"
    torch_stub = SimpleNamespace(cuda=SimpleNamespace(OutOfMemoryError=TestOnlyCudaOOM, empty_cache=lambda: None))
    monkeypatch.setattr(train_tabpfn, "run_inference", attempt)
    selected, _, attempts = train_tabpfn.infer_with_fallback(None, "V3_5", "cuda", True, torch_stub, None, None)
    assert selected == "V3_5_FAST" and visited == ["V3_5", "V3_5_FAST"]
    assert attempts[0]["status"] == "cuda_out_of_memory"
    def access_failure(*args):
        raise ValueError("License/authentication required")
    monkeypatch.setattr(train_tabpfn, "run_inference", access_failure)
    with pytest.raises(ValueError, match="License"):
        train_tabpfn.infer_with_fallback(None, "V3_5", "cuda", True, torch_stub, None, None)


def test_comparison_reports_improvements_and_regressions_without_actual_labels(experiment):
    from ml.comparison import compare_predictions
    inputs = load_inputs(experiment)
    baseline = pd.read_csv(experiment / "artifacts/baseline_predictions.csv")
    # Test-only candidate: modify a copy of real RF rows to exercise comparison branches.
    candidate = baseline.copy()
    wrong = candidate.index[candidate.actual != candidate.predicted][0]
    correct = candidate.index[candidate.actual == candidate.predicted][0]
    for index, chosen in ((wrong, int(candidate.loc[wrong, "actual"])),
                          (correct, 100 if candidate.loc[correct, "actual"] != 100 else 3)):
        candidate.loc[index, "predicted"] = chosen
        for label in (3, 20, 100):
            candidate.loc[index, f"p_{label}"] = float(label == chosen)
        candidate.loc[index, "confidence"] = 1.
    result = compare_predictions(baseline, candidate, inputs)
    assert result["counts"]["tabpfn_improved"] == 1 and result["counts"]["tabpfn_worse"] == 1
    assert result["counts"]["disagreements"] == 2
    assert all("actual" not in row for cases in result["cases"].values() for row in cases)


def test_serving_rejects_unvalidated_files_and_keeps_rf_available(experiment, monkeypatch):
    from app.services import archive
    from app.main import app
    from fastapi.testclient import TestClient
    monkeypatch.setattr(archive, "ARTIFACTS", experiment / "artifacts")
    client = TestClient(app)
    assert client.get("/api/comparison").json()["tabpfn_status"]["status"] == "missing"
    (experiment / "artifacts/tabpfn_predictions.csv").write_text("invalid")
    response = client.post("/api/diagnose/735").json()
    assert len(response["predictions"]) == 1
    assert response["tabpfn_status"]["status"] == "invalid"
    assert len(client.get("/api/evaluation").json()["results"]) == 1
    assert client.post("/api/investigate/735?model=TabPFN-3.5").status_code == 404
