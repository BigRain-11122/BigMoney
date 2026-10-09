# -*- coding: utf-8 -*-
"""r795 bm-c detached run supervisor: smoke -> QA pack -> S6 chain.
1-gen clone of Tools/_r794bmc_runall.py (r794 canon; session-shell 5-min
no-output kill face, pit-spawn domain, saturation-engine daemon precedent,
CEO silence law, r788 >5min wrapper-ban law).
Stage logs (house convention):
  results/_r795bmc_smoke.txt       smoke_test stdout (fresh r795 re-run)
  results/_r795bmc_qa_out.txt      qa_smoke_run --round 795 stdout
  results/_r795bmc_s6_log.txt       S6 chain full log (40 legs, in-driver)
  results/_r795bmc_s6_summary.txt   S6 chain per-leg rc summary stdout
  results/_r795bmc_runlog.txt       supervisor stage markers (poll face)
rc: first nonzero stage rc, honest. ASCII source."""
import datetime
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
PY = sys.executable.replace("pythonw.exe", "python.exe")
RUNLOG = os.path.join(ROOT, "results", "_r795bmc_runlog.txt")
ENV = dict(os.environ)
ENV["PYTHONUTF8"] = "1"

STAGES = [
    ("smoke", [PY, "-m", "smoke_test"],
     os.path.join(ROOT, "results", "_r795bmc_smoke.txt")),
    ("qa_pack", [PY, "scripts/qa_smoke_run.py", "--round", "795"],
     os.path.join(ROOT, "results", "_r795bmc_qa_out.txt")),
    ("s6_chain", [PY, "Tools/_r795bmc_s6.py"],
     os.path.join(ROOT, "results", "_r795bmc_s6_summary.txt")),
]


def log(msg):
    with open(RUNLOG, "a", encoding="utf-8") as fh:
        fh.write("%s %s\n" % (
            datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
            msg))


def main():
    log("supervisor start (smoke -> qa_pack -> s6_chain)")
    rc_final = 0
    for name, cmd, outpath in STAGES:
        log("stage %s begin" % name)
        with open(outpath, "w", encoding="utf-8") as fh:
            p = subprocess.run(cmd, cwd=ROOT, stdout=fh,
                                stderr=subprocess.STDOUT,
                                creationflags=CNW, env=ENV)
        log("stage %s end rc=%d" % (name, p.returncode))
        rc_final = rc_final or p.returncode
    log("supervisor done rc_final=%d" % rc_final)
    with open(RUNLOG + ".rc", "w", encoding="utf-8") as fh:
        fh.write(str(rc_final))
    return rc_final


if __name__ == "__main__":
    raise SystemExit(main())
