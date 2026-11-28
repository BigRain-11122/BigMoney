"""Run the full smoke suite without a console and without dying with the caller.

Why: a full suite takes ~14 minutes. An agent tool shell kills its children when
the call is cancelled (job object, r2194), and a scheduled task that starts a
console program flashes a window (zero-window law). pythonw has no console at
all, so this wrapper is started by pythonw and reaps one `python -m smoke_test`
with CREATE_NO_WINDOW, writing the whole transcript to the path it is given.

Usage (no console; run from the repo root):
  pythonw Tools/run_smoke_detached.py results/_smoke_r<round>.out.txt
"""
from __future__ import annotations

import os
import subprocess
import sys
import time

CREATE_NO_WINDOW = 0x08000000


def main(argv=None):
    argv = list(argv or sys.argv[1:])
    if not argv:
        return 2
    out = os.path.abspath(argv[0])
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    started = time.time()
    with open(out, "wb") as fo:
        p = subprocess.Popen(
            [sys.executable if sys.executable.lower().endswith("pythonw.exe")
             else r"C:\Users\Dasheng\AppData\Local\Programs\Python\Python313\python.exe",
             "-m", "smoke_test"],
            cwd=root, stdout=fo, stderr=subprocess.STDOUT,
            creationflags=CREATE_NO_WINDOW, env=env,
        )
        rc = p.wait()
    with open(out, "a", encoding="utf-8") as fo:
        fo.write("\n[run_smoke_detached] rc=%d elapsed=%.1fs\n" % (rc, time.time() - started))
    return rc


if __name__ == "__main__":
    sys.exit(main())
