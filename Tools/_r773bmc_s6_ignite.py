"""r773 bm-c S6 chain ignite: detached spawn of Tools/_r773bmc_s6.py
(r770 blocking-call pattern adapted to detached r773 form so the chain
survives any shell-host cap and runs parallel to QA pack; poll completion
via results/_r773bmc_s6_log.txt tail DONE marker + _r773bmc_s6.out compact
summary. DETACHED_PROCESS + redirected handles = zero desktop flash,
r640 law family). Pattern credit: Tools/_r770bmc_qa_ignite.py."""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "_r773bmc_s6.out")
ERR = os.path.join(ROOT, "results", "_r773bmc_s6.err")
o = open(OUT, "w", encoding="utf-8")
e = open(ERR, "w", encoding="utf-8")
flags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
p = subprocess.Popen([sys.executable, os.path.join(ROOT, "Tools", "_r773bmc_s6.py")],
                     cwd=ROOT, stdout=o, stderr=e, creationflags=flags,
                     close_fds=True)
print("S6 chain detached pid=%d out=%s" % (p.pid, OUT))
