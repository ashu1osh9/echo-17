"""Evidence compiler shared by genuine local Gemma and transparent fallback reports."""
import hashlib
import json
import os

import numpy as np
from fastapi import HTTPException

from app.report_schema import ForensicReport, GemmaPlan, ReportSection
from .archive import prediction
from .ghost import ghost_signature
from . import gemma_service


def build_evidence(cycle_id, model=None):
    obj = prediction(cycle_id)  # This contract excludes recorded target labels.
    candidates = [p for p in obj["predictions"] if model is None or p["model"] == model]
    if not candidates:
        raise HTTPException(404, "Requested model has no validated prediction for this cycle")
    selected = candidates[-1]
    measurements, comparisons = {}, {}
    reference = None
    for row in obj["feature_evidence"]:
        sensor, unit = row["sensor"], row["unit"]
        statistics = "; ".join(f"{stat}={row[stat]:.4f}" for stat in ("mean", "std", "min", "max", "p05", "p95"))
        measurements[f"{sensor}_summary"] = f"{sensor}: {statistics} {unit} (measured full-recording statistics; every value uses this unit)."
        overlay = ghost_signature(cycle_id, sensor)
        if reference is not None and reference != overlay["reference_cycle_id"]:
            raise HTTPException(503, "Training reference alignment is unavailable")
        reference = overlay["reference_cycle_id"]
        delta = np.asarray(overlay["target_values"]) - np.asarray(overlay["reference_values"])
        rmse = float(np.sqrt(np.mean(delta ** 2)))
        comparisons[f"ghost_{sensor}"] = (
            f"{sensor}: aligned preview mean difference {overlay['mean_difference']:+.4f} {unit}; "
            f"RMSE {rmse:.4f} {unit} against TRAIN recording {reference}."
        )
    return {"cycle_id": cycle_id, "recording_seconds": 60, "source": "UCI 447 measured recordings",
            "prediction": {**selected, "probability_status": "uncalibrated", "inference_mode": obj["inference_mode"]},
            "measurements": measurements, "comparisons": comparisons,
            "reference": {"cycle_id": reference, "split": "TRAIN", "definition": "Full cooler efficiency; other components may differ",
                          "selection": "Nearest eligible TRAIN sensor-summary profile, without held-out target labels"}}


def render_report(evidence, plan, generation, reason=None):
    selected = evidence["prediction"]
    observed = [evidence["measurements"][key] for key in plan.observed_signal_evidence]
    compared = [evidence["comparisons"][key] for key in plan.healthy_reference_comparison]
    diagnosis = (f"The {selected['model']} model predicts {selected['label'].lower()} "
                 f"(cooler condition {selected['condition']}%) with model-reported confidence {selected['confidence']:.1%}. "
                 "This is precomputed from model inference, not a measured condition label.")
    hypothesis = {
        "descriptive_profile_difference": "Hypothesis for inspection: the sensor profile may help characterize this recording. Reference differences do not establish a physical fault cause.",
        "physical_cause_not_established": "Hypothesis remains unconfirmed: the supplied measurements and model output do not establish a physical fault cause.",
    }[plan.hypothesis]
    sections = [
        ReportSection(title="Case summary", kind="context", statements=[f"Historical UCI hydraulic recording {evidence['cycle_id']}; a measured 60-second experimental cycle. This report does not use its recorded condition label."]),
        ReportSection(title="Observed signal evidence", kind="measurement", statements=observed, evidence_ids=plan.observed_signal_evidence),
        ReportSection(title="Comparison to training reference", kind="measurement", statements=compared + ["The reference has full cooler efficiency in TRAIN; other components may differ. Differences are descriptive."], evidence_ids=plan.healthy_reference_comparison),
        ReportSection(title="Model diagnosis", kind="model_prediction", statements=[diagnosis]),
        ReportSection(title="Hypothesis and uncertainty", kind="hypothesis", statements=[hypothesis, "Model probabilities are uncalibrated, not failure risks. No calibrated probabilities are available in the saved model outputs."]),
        ReportSection(title="Limitations", kind="limitation", statements=["A random cycle split from one test rig does not establish unseen-machine generalization. No remaining-useful-life estimate, future failure time or maintenance recommendation is supported."]),
    ]
    return ForensicReport(
        cycle_id=evidence["cycle_id"], source="deterministic fallback (Gemma unavailable)" if reason else f"ollama:{generation['model']}",
        mode="fallback" if reason else "gemma", inference_mode="non_llm" if reason else "live_local", narrative=diagnosis,
        structured_evidence=list(evidence["measurements"].values()), sections=sections,
        selected_model=selected["model"], generation=generation, fallback_reason=reason,
        evidence_sha256=hashlib.sha256(json.dumps(evidence, sort_keys=True).encode()).hexdigest(),
        warning="No LLM used in this response. Deterministic measured-evidence summary." if reason else
                "Gemma selected evidence references and an uncertainty framing. All factual text and numbers are rendered by the backend; this is not an unrestricted LLM narrative.",
    )


def investigate(cycle_id, model=None):
    evidence = build_evidence(cycle_id, model)
    report_mode = os.environ.get("ECHO_REPORT_MODE", "live_local")
    try:
        if report_mode == "precomputed":
            from .precomputed_reports import saved_report
            try:
                return saved_report(evidence)
            except FileNotFoundError:
                raise gemma_service.GemmaUnavailable("precomputed_report_missing") from None
            except (ValueError, KeyError, TypeError, OSError, AttributeError):
                raise gemma_service.GemmaUnavailable("precomputed_report_invalid") from None
        if report_mode != "live_local":
            raise gemma_service.GemmaUnavailable("invalid_configuration")
        plan, generation = gemma_service.generate_plan(evidence)
        reason = None
    except gemma_service.GemmaUnavailable as exc:
        reason = str(exc)
        plan = GemmaPlan(observed_signal_evidence=[f"{sensor}_summary" for sensor in ("PS1", "TS1", "FS1")],
                         healthy_reference_comparison=["ghost_PS1", "ghost_TS1"], hypothesis="physical_cause_not_established")
        generation = {"status": reason, "grounding": "Deterministic evidence selection; no LLM output used."}
    return render_report(evidence, plan, generation, reason).model_dump()


def investigator_status():
    if os.environ.get("ECHO_REPORT_MODE", "live_local") == "precomputed":
        from .precomputed_reports import read_registry
        try:
            registry = read_registry()
            return {"available": bool(registry["reports"]), "status": "precomputed", "local_only": True,
                    "inference_mode": "precomputed", "model": "Saved Gemma reports",
                    "detail": "Precomputed genuine Gemma reports; each is revalidated against current evidence before serving. No live LLM inference."}
        except (ValueError, KeyError, TypeError, OSError, AttributeError):
            return {"available": False, "status": "precomputed_reports_unavailable", "local_only": True,
                    "detail": "Saved Gemma reports are unavailable. The labeled non-LLM fallback remains available."}
    return gemma_service.service_status()
