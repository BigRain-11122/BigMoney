# -*- coding: utf-8 -*-
# r658 bm-c QA pack ignition (detached, explicit --round 658 per r758/r640 law)
# Output tee: results/_r658bmc_qa_runner.{out,err}; poller reads these files.
import subprocess, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "_r658bmc_qa_runner.out")
ERR = os.path.join(ROOT, "results", "_r658bmc_qa_runner.err")

fo = open(OUT, "w", encoding="utf-8")
fe = open(ERR, "w", encoding="utf-8")
DETACHED = 0x00000008 | 0x00000200  # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
p = subprocess.Popen(
    [sys.executable, os.path.join(ROOT, "scripts", "qa_smoke_run.py"), "--round", "658"],
    cwd=ROOT, stdout=fo, stderr=fe, creationflags=DETACHED,
    stdin=subprocess.DEVNULL, close_fds=True,
)
print("IGNITED pid=%d round=658" % p.pid)
