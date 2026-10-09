# -*- coding: utf-8 -*-
"""r795 bm-c runall supervisor ignite: detached spawn of
Tools/_r795bmc_runall.py (smoke -> QA -> S6 chain, ~3-5 min total).
DETACHED_PROCESS so the supervisor survives the session-shell kill
faces (r640 law, r788 >5min wrapper-ban law); stdout/stderr pair to
results/_r795bmc_supervisor.{out,err}. Poll face =
results/_r795bmc_runlog.txt + runlog.txt.rc terminal marker.
Pattern credit: Tools/_r794bmc_ignite.py (1-gen clone)."""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "_r795bmc_supervisor.out")
ERR = os.path.join(ROOT, "results", "_r795bmc_supervisor.err")
o = open(OUT, "w", encoding="utf-8")
e = open(ERR, "w", encoding="utf-8")
flags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
p = subprocess.Popen([sys.executable, os.path.join(ROOT, "Tools", "_r795bmc_runall.py")],
                     cwd=ROOT, stdout=o, stderr=e, creationflags=flags,
                     close_fds=True)
print("runall supervisor detached pid=%d round=795 out=%s" % (p.pid, OUT))
