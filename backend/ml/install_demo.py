"""Build-time download of a public, checksum-pinned demo bundle. No weights or keys."""
import os
import re
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import urlsplit

import requests

from .config import ROOT
from .release_bundle import MAX_ZIP_BYTES, unpack_bundle


def main():
    url = os.environ.get("ECHO_BUNDLE_URL", "")
    checksum = os.environ.get("ECHO_BUNDLE_SHA256", "")
    parsed = urlsplit(url)
    if (parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment
            or not re.fullmatch(r"[a-f0-9]{64}", checksum)):
        raise SystemExit("Set a public HTTPS ECHO_BUNDLE_URL (no credentials/query) and trusted ECHO_BUNDLE_SHA256. No download attempted.")
    destination = Path(os.environ.get("ECHO_DATA_ROOT", str(ROOT / ".runtime/demo-data"))).resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise SystemExit("Demo destination already exists; preserve it or select a new ECHO_DATA_ROOT.")
    with TemporaryDirectory(dir=destination.parent) as temporary:
        archive = Path(temporary) / "demo.zip"
        with requests.Session() as session:
            session.trust_env = False
            # Release hosts may redirect to their CDN; checksum and exact member allowlist remain mandatory.
            with session.get(url, stream=True, timeout=(10, 120)) as response:
                response.raise_for_status()
                size = 0
                with archive.open("xb") as stream:
                    for chunk in response.iter_content(1024 * 1024):
                        size += len(chunk)
                        if size > MAX_ZIP_BYTES:
                            raise SystemExit("Demo bundle exceeds the allowed size")
                        stream.write(chunk)
        result = unpack_bundle(archive, destination, checksum)
    print(f"Validated demo installed: {result['test_count']} held-out cycles, {result['gemma_reports']} genuine saved Gemma reports. No weights installed.")


if __name__ == "__main__":
    main()
