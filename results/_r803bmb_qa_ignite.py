"""r803 bm-b: detached QA pack igniter (S6 chain NOT re-run -- absorbed from dead r802 per white-run 60min law).

r737 canon: DETACHED_PROCESS zero-window (U060), BelowNormal priority, both-redirect.
r758 law: --round explicit. r640 law: poll terminal state before close.
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FLAGS = (subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
         | subprocess.CREATE_NO_WINDOW)
ENV = dict(os.environ)

log = os.path.join(ROOT, "results", "_r803bmb_qa.log")
cmd = [sys.executable, "-u", os.path.join(ROOT, "scripts", "qa_smoke_run.py"), "--round", "803"]
with open(log, "ab") as lf:
    p = subprocess.Popen(cmd, cwd=ROOT, stdout=lf, stderr=subprocess.STDOUT,
                         creationflags=FLAGS, close_fds=True, env=ENV)
try:
    import psutil
    psutil.Process(p.pid).nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    pri = "BelowNormal"
except Exception as ex:
    pri = "nice-skip (%s)" % ex
print("ignited qa_pack r803 pid=%d pri=%s log=%s" % (p.pid, pri, log))
