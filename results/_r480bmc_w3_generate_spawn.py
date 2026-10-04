"""r480 bm-c: detached spawn driver for MASS_TRIAL_W3 generate (post-freeze
c2141d6c1, R99 order). Log -> results/_r480bmc_w3_generate_log.txt."""
import io
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(ROOT, "results", "_r480bmc_w3_generate_log.txt")

flags = (subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
         | subprocess.CREATE_NO_WINDOW)
with io.open(LOG, "a", encoding="utf-8") as lf:
    p = subprocess.Popen(
        [sys.executable, "-u",
         os.path.join(ROOT, "scripts", "mass_trial_w1.py"),
         "generate", "--wave", "3"],
        stdout=lf, stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL, creationflags=flags, close_fds=False,
        cwd=ROOT)
print("SPAWNED_W3_GENERATE pid", p.pid, "log", LOG)
