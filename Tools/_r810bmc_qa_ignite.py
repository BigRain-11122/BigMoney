"""r810 bm-c QA pack ignite: detached spawn of scripts/qa_smoke_run.py with
EXPLICIT --round 810 (r758/r640/r644 law family: explicit round label is the
canon; state is in-flight during this round so default state+1 would mislabel
the pack). Output pair redirected to results/_r810bmc_qa_runner.{out,err};
runner survives the 25-min wrapper kill (DETACHED_PROCESS, r640 law). Poll via
runner .out terminal state before close advances state (r640 round-label race law).
Pre-ignition name-collision pre-check done separately (origin qa/ tree has
zero r810 files before net-write; det-99th clean first-write).
Pattern credit: Tools/_r809bmc_qa_ignite.py (1-gen clone)."""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "_r810bmc_qa_runner.out")
ERR = os.path.join(ROOT, "results", "_r810bmc_qa_runner.err")
o = open(OUT, "w", encoding="utf-8")
e = open(ERR, "w", encoding="utf-8")
flags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
p = subprocess.Popen([sys.executable, os.path.join(ROOT, "scripts", "qa_smoke_run.py"),
                      "--round", "810"],
                     cwd=ROOT, stdout=o, stderr=e, creationflags=flags,
                     close_fds=True)
print("QA runner detached pid=%d round=810 out=%s" % (p.pid, OUT))
