"""Downloads UCI 447. Extracts only required sensors and profile.txt."""
import io
import shutil
import zipfile
from pathlib import Path
import requests
from .config import ARCHIVE_URL, RAW, SENSORS

REQUIRED = {f"{sensor}.txt" for sensor in SENSORS} | {"profile.txt"}


def extract_archive(blob, target: Path):
    found = set()
    with zipfile.ZipFile(io.BytesIO(blob)) as archive:
        for entry in archive.infolist():
            name = Path(entry.filename).name
            if name in REQUIRED and not entry.is_dir():
                with archive.open(entry) as source, (target / name).open("wb") as dest:
                    shutil.copyfileobj(source, dest)
                found.add(name)
        for entry in archive.infolist():
            if entry.filename.lower().endswith(".zip"):
                with archive.open(entry) as nested:
                    found |= extract_archive(nested.read(), target)
    return found


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    missing = REQUIRED - {x.name for x in RAW.glob("*.txt")}
    if not missing:
        print("All required UCI sensor files exist.")
        return
    print("Downloading the original UCI hydraulic-systems archive...")
    try:
        response = requests.get(ARCHIVE_URL, timeout=180)
        response.raise_for_status()
        extract_archive(response.content, RAW)
    except Exception as exc:
        raise RuntimeError(
            "Download failed. Obtain UCI dataset 447 manually, extract the required *.txt "
            "files into backend/data/raw and rerun."
        ) from exc
    missing = REQUIRED - {x.name for x in RAW.glob("*.txt")}
    if missing:
        raise RuntimeError(f"Incomplete UCI archive; missing {sorted(missing)}")
    print("UCI files downloaded successfully.")


if __name__ == "__main__":
    main()
