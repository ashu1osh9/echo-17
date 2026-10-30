"""Validate genuine saved Gemma plans against the current measured evidence."""
import json
import math
import re
import os

from app.report_schema import ForensicReport, GemmaPlan
from ml.config import ARTIFACTS

PRECOMPUTED_WARNING = ("Precomputed from genuine local Gemma inference. No live LLM or GPU inference occurs on this server. "
                       "Gemma selected evidence references; the backend rendered factual statements from measured evidence.")


def validate_generated_report(value, evidence):
    from .investigator import render_report
    report = ForensicReport.model_validate(value)
    generation = report.generation
    plan = GemmaPlan.model_validate(generation["plan"])
    if (report.mode != "gemma" or report.inference_mode != "live_local"
            or report.source != "ollama:" + generation["model"]
            or not re.fullmatch(r"gemma3:[a-z0-9._-]+", generation["model"])
            or "cloud" in generation["model"]
            or not re.fullmatch(r"[a-f0-9]{64}", generation["model_digest"])
            or not math.isfinite(generation["response_seconds"]) or generation["response_seconds"] < 0
            or not set(plan.observed_signal_evidence) <= set(evidence["measurements"])
            or not set(plan.healthy_reference_comparison) <= set(evidence["comparisons"])):
        raise ValueError("Saved Gemma report provenance or evidence references are invalid")
    expected = render_report(evidence, plan, generation).model_dump()
    if report.model_dump() != expected:
        raise ValueError("Saved Gemma report differs from current measured evidence")
    return report


def read_registry():
    registry = json.loads((ARTIFACTS / "gemma_reports.json").read_text(encoding="utf-8"))
    if registry.get("schema_version") != 1 or not isinstance(registry.get("reports"), list):
        raise ValueError("Invalid report registry")
    keys = [(row["cycle_id"], row["selected_model"]) for row in registry["reports"]]
    if len(keys) != len(set(keys)):
        raise ValueError("Duplicate saved report")
    if os.environ.get("ECHO_PUBLIC_MODEL_POLICY") == "rf_only" and any(model != "Random Forest" for _, model in keys):
        raise ValueError("Public registry must contain Random Forest reports only")
    return registry


def saved_report(evidence):
    registry = read_registry()
    for row in registry["reports"]:
        if row["cycle_id"] == evidence["cycle_id"] and row["selected_model"] == evidence["prediction"]["model"]:
            report = validate_generated_report(row, evidence)
            report.inference_mode = "precomputed"
            report.warning = PRECOMPUTED_WARNING
            return report.model_dump()
    raise FileNotFoundError("No saved report for selected cycle/model")
