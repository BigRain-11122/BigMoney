"""r778 bm-c QA pack ignite: detached spawn of scripts/qa_smoke_run.py with
EXPLICIT --round 778 (r765/r640/r644 law family: explicit round label is the
canon; state is in-flight during this round so default state+1 would mislabel
the pack). Output pair redirected to results/_r778bmc_qa_runner.{out,err};
runner survives the 25-min wrapper kill (DETACHED_PROCESS, r640 law). Poll via
runner .out terminal state before close advances state (r640 round-label race law).
Pre-ignite collision probe result: qa/smoke-r778.md NOT on origin/main
(r778 ls-tree probe 20:5x window; det-97th clean first-write, zero collision).
r780 slot OCCUPIED by another machine's pack (qa/smoke-r780.md + equity-
curve-r780.png on origin/main) -- future-face disclosure: bm-c round 780
must defer/skip its own QA pack (overwrite forbidden, r669 law).
Pattern credit: Tools/_r775bmc_qa_ignite.py."""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "_r778bmc_qa_runner.out")
ERR = os.path.join(ROOT, "results", "_r778bmc_qa_runner.err")
o = open(OUT, "w", encoding="utf-8")
e = open(ERR, "w", encoding="utf-8")
flags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
p = subprocess.Popen([sys.executable, os.path.join(ROOT, "scripts", "qa_smoke_run.py"),
                      "--round", "778"],
                     cwd=ROOT, stdout=o, stderr=e, creationflags=flags,
                     close_fds=True)
print("QA runner detached pid=%d round=778 out=%s" % (p.pid, OUT))
