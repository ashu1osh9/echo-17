"""Local-only Ollama adapter. No raw responses/errors are returned to the client."""
import json
import os
import re
import threading
import time
from dataclasses import dataclass
from urllib.parse import urlsplit

import requests

from app.report_schema import GemmaPlan


class GemmaUnavailable(Exception):
    pass


@dataclass(frozen=True)
class Settings:
    url: str
    model: str
    timeout: float


def settings():
    url = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/")
    model = os.environ.get("OLLAMA_MODEL", "gemma3:1b")
    try:
        parsed = urlsplit(url)
        timeout = float(os.environ.get("OLLAMA_TIMEOUT_SECONDS", "120"))
        valid = (parsed.scheme == "http" and parsed.hostname in {"localhost", "127.0.0.1", "::1"}
                 and parsed.port is not None and not parsed.username and not parsed.password
                 and not parsed.path and not parsed.query and not parsed.fragment and 5 <= timeout <= 180
                 and re.fullmatch(r"gemma3:[a-z0-9._-]+", model) and "cloud" not in model)
    except (ValueError, TypeError):
        valid = False
    if not valid:
        raise GemmaUnavailable("invalid_configuration")
    return Settings(url, model, timeout)


def local_session():
    session = requests.Session()
    session.trust_env = False
    return session


def request_json(session, config, method, path, **kwargs):
    response = session.request(method, config.url + path, allow_redirects=False, **kwargs)
    if response.status_code != 200:
        raise GemmaUnavailable("ollama_http_error")
    return response.json()


def inspect_service(session, config):
    version = request_json(session, config, "GET", "/api/version", timeout=(2, 3))
    tags = request_json(session, config, "GET", "/api/tags", timeout=(2, 3))
    for entry in tags["models"]:
        if entry.get("name", entry.get("model")) == config.model:
            family = entry.get("details", {}).get("family", "")
            digest = entry.get("digest", "")
            if family != "gemma3" or not re.fullmatch(r"[a-f0-9]{64}", digest):
                raise GemmaUnavailable("unverified_model_identity")
            return {"available": True, "status": "ready", "model": config.model,
                    "model_digest": digest, "ollama_version": str(version["version"]),
                    "timeout_seconds": config.timeout, "local_only": True,
                    "detail": "Local Gemma is installed. Report output must still pass grounding checks."}
    raise GemmaUnavailable("model_not_installed")


def service_status():
    try:
        config = settings()
        with local_session() as session:
            return inspect_service(session, config)
    except GemmaUnavailable as exc:
        code = str(exc)
    except (requests.RequestException, ValueError, KeyError, TypeError, AttributeError):
        code = "ollama_unreachable"
    return {"available": False, "status": code, "local_only": True,
            "detail": "Local Gemma is unavailable. A labeled deterministic report remains available."}


_generation_lock = threading.Lock()


def generate_plan(evidence):
    """Return a real, validated Gemma plan plus identity/timing, or a safe reason code."""
    config = settings()
    if not _generation_lock.acquire(blocking=False):
        raise GemmaUnavailable("ollama_busy")
    started = time.perf_counter()
    try:
        with local_session() as session:
            identity = inspect_service(session, config)
            schema = GemmaPlan.model_json_schema()
            for field, group in (("observed_signal_evidence", "measurements"), ("healthy_reference_comparison", "comparisons")):
                schema["properties"][field]["items"]["enum"] = list(evidence[group])
            prompt = (
                "You are an evidence-only forensic investigator reviewing one historical hydraulic recording. "
                "Select the most informative supplied evidence identifiers for a concise report. "
                "Choose three to six distinct sensor summaries and one to three "
                "training-reference comparisons. Prioritize observable differences without claiming causality. "
                "Model probabilities are uncalibrated; they are not failure risks. "
                "No recorded target label is supplied. Do not infer or assert one. "
                "Return only a JSON plan matching this schema. No prose, readings, probabilities, causes or advice "
                "may be added. The backend renders numerical statements from original evidence.\n"
                + json.dumps(schema, separators=(",", ":")) + "\nEVIDENCE:\n"
                + json.dumps(evidence, separators=(",", ":"))
            )
            result = request_json(session, config, "POST", "/api/generate", json={
                "model": config.model, "prompt": prompt, "format": schema, "stream": False,
                "keep_alive": "2m", "options": {"temperature": 0, "seed": 42, "num_ctx": 4096, "num_predict": 256},
            }, timeout=(3, config.timeout))
            if result.get("model") != config.model or result.get("done") is not True or result.get("done_reason") != "stop":
                raise GemmaUnavailable("incomplete_or_wrong_model_output")
            plan = GemmaPlan.model_validate_json(result["response"])
            if (not set(plan.observed_signal_evidence) <= set(evidence["measurements"])
                    or not set(plan.healthy_reference_comparison) <= set(evidence["comparisons"])):
                raise GemmaUnavailable("ungrounded_output")
            return plan, {**identity, "response_seconds": round(time.perf_counter() - started, 3),
                          "grounding": "Gemma selects evidence IDs; backend renders all facts and numbers.",
                          "plan": plan.model_dump()}
    except requests.Timeout:
        raise GemmaUnavailable("ollama_timeout") from None
    except GemmaUnavailable:
        raise
    except (requests.RequestException, ValueError, KeyError, TypeError, AttributeError):
        raise GemmaUnavailable("invalid_or_unavailable_output") from None
    finally:
        _generation_lock.release()
