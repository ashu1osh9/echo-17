import os
import requests
from ml.config import LABELS, SENSORS
from .archive import prediction, features


def investigate(cycle_id):
    obj = prediction(cycle_id)
    row = features().loc[cycle_id]
    sensor_facts = [f"{sensor}: mean={float(row[f'{sensor}_mean']):.3f} {unit}, "
                    f"std={float(row[f'{sensor}_std']):.3f} {unit}"
                    for sensor, (_, unit) in SENSORS.items()]
    strongest = obj["predictions"][-1]
    base = (f"The {strongest['model']} model predicts {strongest['label'].lower()} "
            f"(cooler condition {strongest['condition']}%) with model-reported "
            f"confidence {strongest['confidence']:.1%}. This is a classification of an "
            "archived experimental recording, not proof of component failure or a "
            "real-world maintenance instruction. Measured sensor summaries: " + "; ".join(sensor_facts) + ".")
    prompt = (
        "You are a cautious forensic analyst. Write 2 short paragraphs in accessible English. "
        "Use ONLY the evidence below. Distinguish measurements from model inference. "
        "Never invent numbers, faults, causes, or safety advice. No reference to ground truth. "
        "Do not claim a causal diagnosis or future failure time.\n" + base
    )
    url = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/")
    model = os.environ.get("OLLAMA_MODEL", "gemma3:1b")
    try:
        r = requests.post(f"{url}/api/generate", json={"model": model, "prompt": prompt, "stream": False,
                                                      "options": {"temperature": 0.1}}, timeout=45)
        r.raise_for_status()
        text = r.json().get("response", "").strip()
        if text:
            return {"cycle_id": cycle_id, "source": f"ollama:{model}", "narrative": text,
                    "structured_evidence": sensor_facts,
                    "warning": "Generated interpretation; use structured evidence for quantitative verification."}
    except (requests.RequestException, ValueError, KeyError):
        pass
    return {"cycle_id": cycle_id, "source": "deterministic fallback (Gemma unavailable)",
            "narrative": base, "structured_evidence": sensor_facts,
            "warning": "No LLM used in this response. This is a simple measured-data summary."}
