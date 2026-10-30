"""Reuse localhost Ollama or start only the prepared workspace portable runtime."""
import os
import subprocess
import time

import requests

from .config import ARTIFACTS, ROOT


def main():
    with requests.Session() as session:
        session.trust_env = False
        try:
            response = session.get("http://127.0.0.1:11434/api/version", timeout=3)
            response.raise_for_status()
            print(f"Reusing localhost Ollama {response.json()['version']}; no new process started.")
            return
        except (requests.RequestException, ValueError, KeyError):
            pass
        runtime = ARTIFACTS / "ollama"
        executable = runtime / "runtime/v0.40.13/ollama.exe"
        if not executable.is_file():
            raise SystemExit("Prepared portable runtime missing. Follow docs/GEMMA_INVESTIGATOR.md; nothing was downloaded or installed.")
        environment = {**os.environ, "OLLAMA_HOST": "127.0.0.1:11434", "OLLAMA_MODELS": str(runtime / "models"),
                       "OLLAMA_NO_CLOUD": "1", "OLLAMA_NUM_PARALLEL": "1", "OLLAMA_MAX_LOADED_MODELS": "1",
                       "OLLAMA_CONTEXT_LENGTH": "4096", "OLLAMA_KEEP_ALIVE": "2m"}
        with (runtime / "portable.stdout.log").open("ab") as stdout, (runtime / "portable.stderr.log").open("ab") as stderr:
            process = subprocess.Popen([str(executable), "serve"], cwd=ROOT, env=environment, stdin=subprocess.DEVNULL,
                                       stdout=stdout, stderr=stderr, creationflags=subprocess.CREATE_NO_WINDOW)
        for _ in range(15):
            try:
                response = session.get("http://127.0.0.1:11434/api/version", timeout=1)
                response.raise_for_status()
                print(f"Workspace Ollama ready: PID {process.pid}, version {response.json()['version']}.")
                return
            except (requests.RequestException, ValueError, KeyError):
                if process.poll() is not None:
                    raise SystemExit("Workspace Ollama exited; inspect ignored runtime logs locally.") from None
                time.sleep(1)
        raise SystemExit("Ollama is still starting; check the local status endpoint before retrying.")


if __name__ == "__main__":
    main()
