"""r779 bm-c QA pack ignite: detached spawn of scripts/qa_smoke_run.py with
EXPLICIT --round 779 (r765/r640/r644 law family: explicit round label is the
canon; state is in-flight during this round so default state+1 would mislabel
the pack). Output pair redirected to results/_r779bmc_qa_runner.{out,err};
runner survives the 25-min wrapper kill (DETACHED_PROCESS, r640 law). Poll via
runner .out terminal state before close advances state (r640 round-label race law).
Pre-ignite collision probe result: qa/smoke-r779.{md,png} NOT on local tree
and NOT on origin/main (probe results/_r779bmc_qa_probe.json verdict_zero_
collision=true); det-98th clean first-write. Slot uniqueness by counters:
bm-b counter passed r779 on 10-06 (its r780 pack committed 10-06 19:15,
counters only move forward, no retro r779 possible), bm-a at r89x --
r779 uniquely claimable by bm-c. Neighbor r780/r781 = bm-b packs (F-03
cross-machine collision family, charter-pinned face, r669 defer law applies
when slot occupied; r779 not occupied).
Pattern credit: Tools/_r778bmc_qa_ignite.py."""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "_r779bmc_qa_runner.out")
ERR = os.path.join(ROOT, "results", "_r779bmc_qa_runner.err")
o = open(OUT, "w", encoding="utf-8")
e = open(ERR, "w", encoding="utf-8")
flags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
p = subprocess.Popen([sys.executable, os.path.join(ROOT, "scripts", "qa_smoke_run.py"),
                      "--round", "779"],
                     cwd=ROOT, stdout=o, stderr=e, creationflags=flags,
                     close_fds=True)
print("QA runner detached pid=%d round=779 out=%s" % (p.pid, OUT))
