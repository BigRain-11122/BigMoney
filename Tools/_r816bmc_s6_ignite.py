"""r816 bm-c S6 chain DETACHED ignite (bm-a r919 evening-chain precedent:
25-min wrapper kill window is near, chain runs to completion regardless of
session fate; receipt verified in-round or next round). Output pair
redirected to results/_r816bmc_s6_runner.{out,err}; chain log stays at
results/_r816bmc_s6_log.txt (written incrementally by the driver).
Pattern credit: Tools/_r815bmc_s6_ignite.py (1-gen clone)."""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "_r816bmc_s6_runner.out")
ERR = os.path.join(ROOT, "results", "_r816bmc_s6_runner.err")
o = open(OUT, "w", encoding="utf-8")
e = open(ERR, "w", encoding="utf-8")
flags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
p = subprocess.Popen([sys.executable, os.path.join(ROOT, "Tools", "_r816bmc_s6.py")],
                     cwd=ROOT, stdout=o, stderr=e, creationflags=flags,
                     close_fds=True)
print("S6 chain detached pid=%d log=results/_r816bmc_s6_log.txt" % p.pid)
