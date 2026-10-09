"""r815 bm-c H3 download DETACHED ignite (1-gen clone of
_r814bmc_h3_ignite.py, pointed at the r815 FIX-RELEASE driver; r814 driver
was DOA -- urllib tuple-timeout TypeError + file2 10x byte typo, zero
bytes in 22min). Output pair redirected to
results/_r815bmc_h3_runner.{out,err}; state/receipt under
results/_r815bmc_h3_*.{json}. DETACHED_PROCESS -- survives the 25-min
wrapper kill window; receipt verified in-round or next round."""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "_r815bmc_h3_runner.out")
ERR = os.path.join(ROOT, "results", "_r815bmc_h3_runner.err")
o = open(OUT, "w", encoding="utf-8")
e = open(ERR, "w", encoding="utf-8")
flags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
p = subprocess.Popen([sys.executable,
                      os.path.join(ROOT, "Tools", "_r815bmc_h3_download.py")],
                     cwd=ROOT, stdout=o, stderr=e, creationflags=flags,
                     close_fds=True)
print("H3 r815 fix-release download detached pid=%d" % p.pid)
