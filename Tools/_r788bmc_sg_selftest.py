# -*- coding: utf-8 -*-
"""r788 bm-c: detached science_gates selftest driver (pythonw face).

Why detached: session-shell 5-min no-output timeout killed the buffered
wrapper child mid-selftest on first attempt (r788 live fire; the wrapper
holds all stdout until exit so the shell sees five silent minutes).
Driver self-logs to results/_r788bmc_sg_selftest.txt and never prints
(pythonw stdout=None face). Read-only guarantee verified r788:
append_ledger is a PURE function (returns dict, caller writes the file),
so a killed selftest cannot corrupt the DSR chain -- zero disk writes.
Post-berth-edit verification face for the W17 freeze (W16 freeze
precedent: science_gates selftest after SEED_REGISTRY edit)."""
import datetime
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
PY = sys.executable.replace("pythonw.exe", "python.exe")
OUT = os.path.join(ROOT, "results", "_r788bmc_sg_selftest.txt")
ENV = dict(os.environ)
ENV["PYTHONUTF8"] = "1"


def main():
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("r788 bm-c science_gates selftest detached %s\n"
                 % datetime.datetime.now().astimezone().isoformat(
                     timespec="seconds"))
        fh.flush()
        p = subprocess.run([PY, "-m", "scripts.science_gates", "selftest"],
                            cwd=ROOT, stdout=fh, stderr=subprocess.STDOUT,
                            creationflags=CNW, env=ENV)
        fh.write("\n[rc=%d]\n" % p.returncode)
    with open(OUT + ".rc", "w", encoding="utf-8") as fh:
        fh.write(str(p.returncode))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
