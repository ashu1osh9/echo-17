"""Record sanitized, actual local report invocations; never fabricate model execution."""
import argparse
import json
import time
from datetime import datetime, timezone

import requests

from app.report_schema import ForensicReport, GemmaPlan
from app.services.investigator import build_evidence, render_report
from .config import ARTIFACTS


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--model", default="Random Forest")
    parser.add_argument("--require-gemma", action="store_true")
    parser.add_argument("--output", default="mission4_gemma_verification.json")
    args = parser.parse_args()
    output = ARTIFACTS / args.output
    if output.parent.resolve() != ARTIFACTS.resolve() or output.exists():
        parser.error("Choose a new evidence filename inside artifacts; previous evidence is preserved")
    records = []
    with requests.Session() as session:
        session.trust_env = False
        status = session.get(args.base_url.rstrip("/") + "/api/investigator/status", timeout=15)
        status.raise_for_status()
        for cycle_id in (735, 5):
            started = time.perf_counter()
            response = session.post(args.base_url.rstrip("/") + f"/api/investigate/{cycle_id}",
                                    params={"model": args.model}, timeout=190)
            response.raise_for_status()
            report = ForensicReport.model_validate(response.json())
            assert report.cycle_id == cycle_id and report.selected_model == args.model
            if args.require_gemma:
                assert report.mode == "gemma" and report.inference_mode == "live_local", f"Cycle {cycle_id}: live Gemma required; got {report.inference_mode} / {report.fallback_reason}"
            evidence = build_evidence(cycle_id, args.model)
            if report.mode == "gemma":
                plan = GemmaPlan.model_validate(report.generation["plan"])
                assert set(plan.observed_signal_evidence) <= set(evidence["measurements"])
                assert set(plan.healthy_reference_comparison) <= set(evidence["comparisons"])
                expected = render_report(evidence, plan, report.generation)
                if report.inference_mode == "precomputed":
                    from app.services.precomputed_reports import PRECOMPUTED_WARNING
                    expected.inference_mode, expected.warning = "precomputed", PRECOMPUTED_WARNING
                assert report.model_dump() == expected.model_dump()
            records.append({"verification_seconds": round(time.perf_counter() - started, 3), "report": report.model_dump()})
            print(json.dumps({"cycle_id": cycle_id, "mode": report.mode, "source": report.source,
                              "response_seconds": report.generation.get("response_seconds"),
                              "fallback_reason": report.fallback_reason, "plan": report.generation.get("plan")}), flush=True)
    output.write_text(json.dumps({"timestamp_utc": datetime.now(timezone.utc).isoformat(), "base_url": args.base_url,
                                  "status": status.json(), "records": records}, indent=2), encoding="utf-8")
    print(f"Saved sanitized evidence: {output.name}")


if __name__ == "__main__":
    main()
