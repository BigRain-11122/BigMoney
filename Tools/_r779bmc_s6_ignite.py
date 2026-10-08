"""r779 bm-c S6 chain detached igniter (r640 detached law family: the chain
must survive the 25-min wrapper kill; all 40 legs are idempotent gate/no-op
designs with checkpoint resume -- full re-run from leg 1 is safe and rewrites
the log as one complete honest pass).
Output pair: results/_r779bmc_s6_runner.{out,err}; poll LOG for DONE marker.
Pattern credit: Tools/_r778bmc_s6_ignite.py."""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "_r779bmc_s6_runner.out")
ERR = os.path.join(ROOT, "results", "_r779bmc_s6_runner.err")
o = open(OUT, "w", encoding="utf-8")
e = open(ERR, "w", encoding="utf-8")
flags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
p = subprocess.Popen([sys.executable, os.path.join(ROOT, "Tools", "_r779bmc_s6.py")],
                     cwd=ROOT, stdout=o, stderr=e, creationflags=flags,
                     close_fds=True)
print("S6 chain detached pid=%d" % p.pid)
