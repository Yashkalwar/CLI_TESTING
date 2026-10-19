import os
import shutil
import socket
import subprocess
import time
from pathlib import Path

import pytest

HOST, PORT = "127.0.0.1", 3838
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _port_open():
    with socket.socket() as s:
        s.settimeout(0.5)
        return s.connect_ex((HOST, PORT)) == 0


def _rscript():
    path = os.environ.get("RSCRIPT") or shutil.which("Rscript")
    if not path:
        pytest.exit("Rscript not found. Add it to PATH or set the RSCRIPT env var.", returncode=2)
    return path


@pytest.fixture(scope="session", autouse=True)
def shiny_app():
    if _port_open():
        pytest.exit(f"Port {PORT} is already in use; stop the other process first.", returncode=2)
    cmd = [_rscript(), "-e",
           f"shiny::runApp('app', port={PORT}, host='{HOST}', launch.browser=FALSE)"]
    proc = subprocess.Popen(cmd, cwd=PROJECT_ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    try:
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            if proc.poll() is not None:
                err = proc.stderr.read().decode(errors="replace")
                pytest.exit(f"Shiny app exited early (code {proc.returncode}):\n{err}", returncode=2)
            if _port_open():
                break
            time.sleep(0.25)
        else:
            pytest.exit(f"Shiny app did not accept connections on {HOST}:{PORT} within 60s.", returncode=2)
        yield proc
    finally:
        if os.name == "nt":
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)], capture_output=True)
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()


@pytest.fixture(scope="session")
def base_url():
    return f"http://{HOST}:{PORT}"
