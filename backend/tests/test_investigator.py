"""Grounding tests use real UCI evidence; Ollama responses below are test doubles only."""
import json

import numpy as np
import pytest
import requests
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.main import app
from app.report_schema import ForensicReport, GemmaPlan
from app.services import archive, ghost, gemma_service as gemma, investigator


@pytest.fixture(scope="module")
def evidence():
    return investigator.build_evidence(735, "Random Forest")


def plan_dict():
    return {"observed_signal_evidence": ["PS1_summary", "TS1_summary", "FS1_summary"],
            "healthy_reference_comparison": ["ghost_PS1", "ghost_TS1"],
            "hypothesis": "physical_cause_not_established"}


class LocalOllamaDouble:
    """No inference performed by this double; never saved as an application artifact."""
    def __init__(self, output=None, models=None, failure=None, status=200):
        self.output = output if output is not None else {"model": "gemma3:1b", "done": True, "done_reason": "stop", "response": json.dumps(plan_dict())}
        self.models = models if models is not None else [{"name": "gemma3:1b", "digest": "a" * 64, "details": {"family": "gemma3"}}]
        self.failure, self.status, self.calls = failure, status, []

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        if self.failure:
            raise self.failure
        body = {"version": "TEST ONLY"} if url.endswith("/version") else {"models": self.models} if url.endswith("/tags") else self.output
        response = requests.Response()
        response.status_code = self.status
        response._content = json.dumps(body).encode()
        return response


def test_evidence_uses_real_statistics_and_train_reference(evidence):
    row = archive.features().loc[735]
    assert len(evidence["measurements"]) == 6
    assert f"{row.PS1_mean:.4f}" in evidence["measurements"]["PS1_summary"]
    assert f"{row.PS1_std:.4f}" in evidence["measurements"]["PS1_summary"]
    ref = evidence["reference"]["cycle_id"]
    assert ref in ghost.training_ids()
    assert archive.features().loc[ref, "cooler_condition"] == 100
    overlay = ghost.ghost_signature(735, "PS1")
    rmse = np.sqrt(np.mean((np.array(overlay["target_values"]) - overlay["reference_values"]) ** 2))
    assert f"{rmse:.4f}" in evidence["comparisons"]["ghost_PS1"]
    assert evidence["prediction"]["condition"] == 3  # RF prediction, not cycle 735 truth.
    assert evidence["prediction"]["probability_status"] == "uncalibrated"


def test_held_out_targets_cannot_change_report_evidence(evidence, monkeypatch):
    changed = archive.features().copy(deep=True)
    changed.loc[archive.baseline().index, "cooler_condition"] = 100
    changed.loc[archive.baseline().index, "stable"] = 1
    monkeypatch.setattr(archive, "features", lambda: changed)
    monkeypatch.setattr(ghost, "features", lambda: changed)
    assert investigator.build_evidence(735, "Random Forest") == evidence


def test_schema_grounding_and_prompt_exclude_target(evidence, monkeypatch):
    local = LocalOllamaDouble()
    monkeypatch.setattr(gemma, "local_session", lambda: local)
    plan, meta = gemma.generate_plan(evidence)
    assert plan.model_dump() == plan_dict()
    assert meta["model"] == "gemma3:1b"
    payload = local.calls[-1][2]["json"]
    assert payload["stream"] is False and payload["format"]["additionalProperties"] is False
    assert "cooler_condition" not in payload["prompt"] and '"actual"' not in payload["prompt"]
    assert "Reduced efficiency" not in payload["prompt"]
    assert all(call[2]["allow_redirects"] is False for call in local.calls)
    report = investigator.render_report(evidence, plan, meta).model_dump()
    assert ForensicReport.model_validate(report).mode == "gemma"
    assert len(report["sections"]) == 6
    assert report["sections"][1]["statements"] == [evidence["measurements"][k] for k in plan.observed_signal_evidence]
    assert "Reduced efficiency" not in json.dumps(report)


@pytest.mark.parametrize("output", [
    {"observed_signal_evidence": ["PS1_summary", "PS1_summary", "TS1_summary"], "healthy_reference_comparison": ["ghost_PS1"], "hypothesis": "physical_cause_not_established"},
    {**plan_dict(), "actual": 20},
    {**plan_dict(), "narrative": "Temperature is 9999 degrees; replace the pump"},
    {**plan_dict(), "hypothesis": "The pump caused the failure"},
])
def test_report_plan_rejects_freeform_claims_and_labels(output):
    with pytest.raises(ValidationError):
        GemmaPlan.model_validate(output)


@pytest.mark.parametrize("mutation", ["unknown_id", "bad_json", "nonobject", "extra_numbers", "wrong_model", "incomplete", "truncated"])
def test_bad_model_output_produces_safe_fallback(evidence, monkeypatch, mutation):
    local = LocalOllamaDouble()
    if mutation == "unknown_id":
        p = plan_dict();p["observed_signal_evidence"][0] = "made_up_reading_9999";local.output["response"] = json.dumps(p)
    elif mutation == "bad_json": local.output["response"] = "not json SECRET TEST VALUE"
    elif mutation == "nonobject": local.output = []
    elif mutation == "extra_numbers": local.output["response"] = json.dumps({**plan_dict(), "actual": 20})
    elif mutation == "wrong_model": local.output["model"] = "different-model"
    elif mutation == "incomplete": local.output["done"] = False
    elif mutation == "truncated": local.output["done_reason"] = "length"
    monkeypatch.setattr(gemma, "local_session", lambda: local)
    monkeypatch.setattr(investigator, "build_evidence", lambda *args: evidence)
    report = investigator.investigate(735, "Random Forest")
    assert report["mode"] == "fallback" and report["source"].startswith("deterministic fallback")
    assert "SECRET TEST VALUE" not in json.dumps(report) and "9999" not in json.dumps(report)
    assert "actual" not in report and len(report["sections"]) == 6


@pytest.mark.parametrize("failure,code", [(requests.ConnectionError("SECRET TEST"), "invalid_or_unavailable_output"), (requests.Timeout("SECRET TEST"), "ollama_timeout")])
def test_connection_and_timeout_are_transparent(evidence, monkeypatch, failure, code):
    monkeypatch.setattr(gemma, "local_session", lambda: LocalOllamaDouble(failure=failure))
    monkeypatch.setattr(investigator, "build_evidence", lambda *args: evidence)
    report = investigator.investigate(735)
    assert report["fallback_reason"] == code and report["mode"] == "fallback"
    assert "SECRET TEST" not in json.dumps(report)


def test_unavailable_model_status_and_redirect_rejection(evidence, monkeypatch):
    missing = LocalOllamaDouble(models=[])
    monkeypatch.setattr(gemma, "local_session", lambda: missing)
    assert gemma.service_status()["status"] == "model_not_installed"
    with pytest.raises(gemma.GemmaUnavailable, match="model_not_installed"):
        gemma.generate_plan(evidence)
    assert len(missing.calls) == 4 and not any(url.endswith("/generate") for _, url, _ in missing.calls)
    monkeypatch.setattr(gemma, "local_session", lambda: LocalOllamaDouble(status=302))
    with pytest.raises(gemma.GemmaUnavailable, match="ollama_http_error"):
        gemma.generate_plan(evidence)


@pytest.mark.parametrize("env,value", [("OLLAMA_URL", "https://external.example"), ("OLLAMA_URL", "http://user:secret@127.0.0.1:11434"), ("OLLAMA_URL", "http://127.0.0.1:11434/redirect"), ("OLLAMA_MODEL", "gemma3:4b-cloud"), ("OLLAMA_TIMEOUT_SECONDS", "nan"), ("OLLAMA_TIMEOUT_SECONDS", "999")])
def test_external_or_invalid_config_never_sends_evidence(monkeypatch, env, value):
    monkeypatch.setenv(env, value)
    monkeypatch.setattr(gemma, "local_session", lambda: pytest.fail("No request permitted"))
    assert gemma.service_status()["status"] == "invalid_configuration"


def test_local_http_client_ignores_proxies():
    with gemma.local_session() as session:
        assert session.trust_env is False


def test_busy_status_does_not_queue_another_inference(evidence):
    assert gemma._generation_lock.acquire(blocking=False)
    try:
        with pytest.raises(gemma.GemmaUnavailable, match="ollama_busy"):
            gemma.generate_plan(evidence)
    finally:
        gemma._generation_lock.release()


def test_report_route_validates_schema_and_never_calls_reveal(evidence, monkeypatch):
    local = LocalOllamaDouble()
    monkeypatch.setattr(gemma, "local_session", lambda: local)
    client = TestClient(app)
    assert client.get("/api/investigator/status").json()["available"] is True
    report = client.post("/api/investigate/735?model=Random%20Forest")
    assert report.status_code == 200
    assert report.json()["selected_model"] == "Random Forest"
    assert ForensicReport.model_validate(report.json()).mode == "gemma"
    assert "Reduced efficiency" not in report.text
    assert '"actual"' not in report.text
    assert client.post("/api/investigate/735?model=missing").status_code == 404
