"""r818 bm-c DETACHED ignite for BOTH long-runners (S6 chain + H3 768P
T2V test client). bm-a r919 evening-chain precedent: detached so the run
survives any session/wrapper fate; receipts verified in-round or next
round. Output pairs -> results/_r818bmc_s6_runner.{out,err} and
results/_r818bmc_h3_client.{out,err}. Pattern credit:
Tools/_r817bmc_s6_ignite.py (1-gen clone, second Popen added)."""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
flags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP

for name, script in (("s6_runner", "_r818bmc_s6.py"),
                     ("h3_client", "_r818bmc_h3_client.py")):
    o = open(os.path.join(ROOT, "results", "_r818bmc_%s.out" % name), "w",
             encoding="utf-8")
    e = open(os.path.join(ROOT, "results", "_r818bmc_%s.err" % name), "w",
             encoding="utf-8")
    p = subprocess.Popen([sys.executable, os.path.join(ROOT, "Tools", script)],
                         cwd=ROOT, stdout=o, stderr=e, creationflags=flags,
                         close_fds=True)
    print("%s detached pid=%d" % (name, p.pid))
