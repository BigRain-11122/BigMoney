"""r771 bm-c QA pack ignite: detached spawn of scripts/qa_smoke_run.py with
EXPLICIT --round 771 (r765/r640/r644 law family: explicit round label is the
canon; state is in-flight during this round so default state+1 would mislabel
the pack). Output pair redirected to results/_r771bmc_qa_runner.{out,err};
runner survives the 25-min wrapper kill (DETACHED_PROCESS, r640 law). Poll via
runner .out terminal state before close advances state (r640 round-label race law).
Pre-ignite collision probe result: qa/smoke-r771.md ALREADY on origin/main
(blob 9bf1dcfb, bm-b pack) -> collision case #8, follow
r761/r764/r766/r767/r768/r770 disclosure canon (deterministic same frozen
numbers, same-path overwrite, bm-b version git-preserved via its own commit).
Pattern credit: Tools/_r770bmc_qa_ignite.py."""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "_r771bmc_qa_runner.out")
ERR = os.path.join(ROOT, "results", "_r771bmc_qa_runner.err")
o = open(OUT, "w", encoding="utf-8")
e = open(ERR, "w", encoding="utf-8")
flags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
p = subprocess.Popen([sys.executable, os.path.join(ROOT, "scripts", "qa_smoke_run.py"),
                      "--round", "771"],
                     cwd=ROOT, stdout=o, stderr=e, creationflags=flags,
                     close_fds=True)
print("QA runner detached pid=%d round=771 out=%s" % (p.pid, OUT))
