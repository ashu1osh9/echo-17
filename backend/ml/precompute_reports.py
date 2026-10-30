"""Prepare genuine Gemma reports for a bounded public demo; never accept fallback."""
import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from app.services.investigator import build_evidence, investigate
from app.services.precomputed_reports import validate_generated_report
from .config import ARTIFACTS

DEMO_CYCLES = (5, 735, 2, 1467)
DEMO_MODELS = ("Random Forest", "TabPFN-3.5")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ARTIFACTS / "gemma_reports.json")
    args = parser.parse_args()
    if args.output.exists() or args.output.resolve().parent != ARTIFACTS.resolve():
        parser.error("Choose a new file inside artifacts; existing reports are preserved")
    if os.environ.get("ECHO_REPORT_MODE", "live_local") != "live_local":
        parser.error("Precomputation requires genuine live_local generation")
    reusable = {}
    existing = ARTIFACTS / "mission4_gemma_final_verification.json"
    if existing.exists():
        for record in json.loads(existing.read_text(encoding="utf-8"))["records"]:
            value = record["report"]
            reusable[(value["cycle_id"], value["selected_model"])] = value
    reports = []
    for cycle_id in DEMO_CYCLES:
        for model in DEMO_MODELS:
            evidence = build_evidence(cycle_id, model)
            value = reusable.get((cycle_id, model))
            reused = value is not None
            if value is None:
                value = investigate(cycle_id, model)
            report = validate_generated_report(value, evidence)
            reports.append(report.model_dump())
            print(json.dumps({"cycle_id": cycle_id, "model": model, "source": report.source, "reused_verified_run": reused,
                              "response_seconds": report.generation["response_seconds"]}), flush=True)
    registry = {"schema_version": 1, "exported_at_utc": datetime.now(timezone.utc).isoformat(),
                "note": "Genuine local Gemma plans, prevalidated against measured UCI evidence. No model weights included.", "reports": reports}
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(registry, stream, indent=2)
    print(f"Saved {len(reports)} validated genuine reports: {args.output.name}")


if __name__ == "__main__":
    main()
