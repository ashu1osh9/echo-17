"""Read-only publication audit. Report locations/categories, never matched secrets."""
import argparse
import json
import re
import subprocess
from zipfile import ZipFile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATTERNS = {
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "provider_token": re.compile(r"(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{30,}|hf_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9_-]{20,}|AKIA[A-Z0-9]{16})"),
    "credential_assignment": re.compile(r'''(?i)(?:api[_-]?key|access[_-]?token|auth[_-]?token|password|secret)\s*[=:]\s*["']([A-Za-z0-9_./+\-=]{16,})["']'''),
    "url_credentials": re.compile(r"https?://[^\s/:@]+:[^\s/@]+@"),
    "personal_path": re.compile(r"[A-Za-z]:[/\\]Users[/\\][^/\\\s]+"),
    "private_network_url": re.compile(r"https?://(?:10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+|172\.(?:1[6-9]|2\d|3[01])\.\d+\.\d+)"),
}


def audit():
    files = subprocess.check_output(["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"], cwd=ROOT).decode().split("\0")
    findings, images, checked = [], [], 0
    for name in sorted(set(files) - {""}):
        path = ROOT / name
        if not path.is_file():
            continue
        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
            images.append(name)
            continue
        if any(part in {".venv", "node_modules", "__pycache__", ".aws", ".codex", ".agents"} for part in path.relative_to(ROOT).parts) or path.name.startswith(".env") and path.name != ".env.example":
            findings.append({"file": name, "category": "forbidden_publication_path"})
        try:
            content = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            findings.append({"file": name, "category": "unreviewed_binary"})
            continue
        checked += 1
        for number, line in enumerate(content.splitlines(), 1):
            for category, pattern in PATTERNS.items():
                if pattern.search(line):
                    # Detection patterns and deliberate negative tests are still reported for review.
                    findings.append({"file": name, "line": number, "category": category})
    return {"text_files_checked": checked, "findings": findings, "images_require_visual_review": images,
            "scope": "Tracked and nonignored untracked working-tree files; ignored credentials/weights are excluded, not certified safe. History and images require separate review."}


def audit_history():
    entries = subprocess.check_output(["git", "rev-list", "--objects", "--all"], cwd=ROOT).decode().splitlines()
    checked, findings = 0, []
    for entry in entries:
        parts = entry.split(" ", 1)
        if len(parts) != 2:
            continue
        identifier, name = parts
        if Path(name).suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
            continue
        result = subprocess.run(["git", "cat-file", "blob", identifier], cwd=ROOT, capture_output=True)
        if result.returncode:
            continue
        try:
            content = result.stdout.decode("utf-8")
        except UnicodeDecodeError:
            findings.append({"object": identifier[:12], "file": name, "category": "unreviewed_historical_binary"})
            continue
        checked += 1
        for number, line in enumerate(content.splitlines(), 1):
            for category, pattern in PATTERNS.items():
                if pattern.search(line):
                    findings.append({"object": identifier[:12], "file": name, "line": number, "category": category})
    return {"text_blobs_checked": checked, "findings": findings, "note": "All locally reachable Git objects; no remote/private account audit or historical image OCR."}


def audit_generated():
    findings, checked = [], 0
    values = []
    for path in (ROOT / "frontend/dist").rglob("*"):
        if path.is_file():
            values.append((path.relative_to(ROOT).as_posix(), path.read_text(encoding="utf-8")))
    bundle = ROOT / "backend/artifacts/release/echo17-public-rf.zip"
    with ZipFile(bundle) as archive:
        from .release_bundle import FILES
        if set(archive.namelist()) != set(FILES) | {"manifest.json"}:
            raise ValueError("Generated public bundle has unexpected members")
        registry = json.loads(archive.read("artifacts/gemma_reports.json"))
        if len(registry["reports"]) != 4 or any(row["selected_model"] != "Random Forest" for row in registry["reports"]):
            raise ValueError("Generated public reports include a restricted model")
        for name in archive.namelist():
            if not name.endswith(".npz"):
                values.append(("public-bundle/" + name, archive.read(name).decode("utf-8")))
    for name, value in values:
        checked += 1
        for number, line in enumerate(value.splitlines(), 1):
            for category, pattern in PATTERNS.items():
                if pattern.search(line):
                    findings.append({"file": name, "line": number, "category": category})
    return {"text_assets_checked": checked, "findings": findings, "model_policy": "rf_only", "genuine_reports": 4}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--history", action="store_true")
    parser.add_argument("--generated", action="store_true")
    args = parser.parse_args()
    report = audit()
    if args.history:
        report["history"] = audit_history()
    if args.generated:
        report["generated"] = audit_generated()
    if args.output:
        destination = args.output.resolve()
        if not destination.is_relative_to((ROOT / "backend/artifacts").resolve()):
            parser.error("Audit evidence belongs inside ignored backend/artifacts")
        destination.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
