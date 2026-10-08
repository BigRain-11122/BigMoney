# -*- coding: utf-8 -*-
"""r789 bm-c W17 runner three-command identity-face first-run supervisor
(r446bmb/r467bma surgical pit law; detached zero-window channel per
pit-spawn domain + r788 runall precedent -- the session shell kills any
command silent for 5.0 minutes, Invoke-SilentExe buffers until exit).

Stages (prereg sec.9 sequencing: identity faces BEFORE runner-landed
declaration is complete; GENERATE is NOT here -- the pool owns the
generate burn, autofill execution-face separation O-2100):
  1. screen-prep       real-data identity face (panel/census/starts/
                       passive; rc=0 expected -- cells PRESENT since
                       generate... NO: cells file absent pre-pool ->
                       honest rc=2 at the TAIL is the expected identity
                       face per the identity-first-run law)
  2. screen-finalize   honest refuse face (incomplete checkpoint ->
                       rc=2; G-ENTRY/G-EXITCFG gates exercised)
  3. judge-prep        honest refuse face (screen absent -> rc=2;
                       T18 manifest gate exercised)
rc: first nonzero stage rc, honest. ASCII source."""
import datetime
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
PY = sys.executable.replace("pythonw.exe", "python.exe")
RUNLOG = os.path.join(ROOT, "results", "_r789bmc_runner_first_run.txt")

STAGES = [
    ("screen-prep", [PY, "scripts/trial_labor_w17.py", "screen-prep"],
     os.path.join(ROOT, "results", "_r789bmc_sprep_out.txt")),
    ("screen-finalize",
     [PY, "scripts/trial_labor_w17.py", "screen-finalize"],
     os.path.join(ROOT, "results", "_r789bmc_sfin_out.txt")),
    ("judge-prep", [PY, "scripts/trial_labor_w17.py", "judge-prep"],
     os.path.join(ROOT, "results", "_r789bmc_jprep_out.txt")),
]


def log(msg):
    with open(RUNLOG, "a", encoding="utf-8") as fh:
        fh.write("%s %s\n" % (
            datetime.datetime.now().astimezone().isoformat(
                timespec="seconds"), msg))


def main():
    log("supervisor start (three-command identity-face first-run)")
    rc_final = 0
    for name, cmd, outpath in STAGES:
        log("stage %s begin" % name)
        with open(outpath, "w", encoding="utf-8") as fh:
            p = subprocess.run(cmd, cwd=ROOT, stdout=fh,
                               stderr=subprocess.STDOUT,
                               creationflags=CNW)
        log("stage %s end rc=%d" % (name, p.returncode))
        rc_final = rc_final or p.returncode
    log("supervisor done rc_final=%d" % rc_final)
    with open(RUNLOG + ".rc", "w", encoding="utf-8") as fh:
        fh.write(str(rc_final))
    return rc_final


if __name__ == "__main__":
    raise SystemExit(main())
