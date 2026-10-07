"""r802 bm-b: detached igniter for S6 chain clone + QA pack.

r662 law: bare-number clone ('801'->'802' catches _r801bmb_ prefix and r801
labels alike) + mandatory residual-number check before ignition.
r705/r737 canon: DETACHED_PROCESS zero-window (U060), BelowNormal priority
(CEO margin law), both-redirect to log.
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "results", "_r801bmb_s6_chain.py")
DST = os.path.join(ROOT, "results", "_r802bmb_s6_chain.py")

raw = open(SRC, encoding="utf-8").read()
cloned = raw.replace("801", "802")
if "801" in cloned:
    print("RESIDUAL '801' after clone -- ABORT")
    sys.exit(1)
open(DST, "w", encoding="utf-8", newline="\n").write(cloned)
print("clone ok residual=0 ->", DST)

FLAGS = (subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
         | subprocess.CREATE_NO_WINDOW)
ENV = dict(os.environ)

jobs = [
    ("s6_chain", [sys.executable, "-u", DST],
     os.path.join(ROOT, "results", "_r802bmb_s6_chain.log")),
    ("qa_pack", [sys.executable, "-u", os.path.join(ROOT, "scripts", "qa_smoke_run.py"),
                 "--round", "802"],
     os.path.join(ROOT, "results", "_r802bmb_qa.log")),
]
for name, cmd, log in jobs:
    with open(log, "ab") as lf:
        p = subprocess.Popen(cmd, cwd=ROOT, stdout=lf,
                             stderr=subprocess.STDOUT,
                             creationflags=FLAGS, close_fds=True, env=ENV)
    try:
        import psutil
        psutil.Process(p.pid).nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
        pri = "BelowNormal"
    except Exception as ex:
        pri = "nice-skip (%s)" % ex
    print("ignited %s pid=%d pri=%s log=%s" % (name, p.pid, pri, log))
print("first-line check: S6 log header + QA round label (r662 law #3)")
