# -*- coding: utf-8 -*-
"""r814 bm-c occupancy probe (same-repo single-executor yield law): who
refreshed README.md, is the tree holding another body's in-flight faces,
is a tick round live right now (codely/wscript/powershell chain), tick
lock age. Read-only."""
import os
import subprocess
import time
from datetime import datetime

CNW = 0x08000000
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"


def g(args, t=45):
    r = subprocess.run(["git", "-C", ROOT] + args, capture_output=True,
                       creationflags=CNW, timeout=t)
    return r.returncode, (r.stdout or b"").decode("utf-8", "replace"), \
        (r.stderr or b"").decode("utf-8", "replace")


rc, o, _ = g(["log", "-4", "--format=%h %an %ad %s", "--date=format:%H:%M",
             "--", "README.md"])
print("README log:")
print(o or "(none)")
rc, o, _ = g(["status", "--porcelain"])
print("DIRTY now:")
for l in o.splitlines():
    if l.strip():
        print("  " + l.strip()[:150])
rc, o, _ = g(["log", "-3", "--format=%h %an %ad %s", "--date=format:%H:%M"])
print("HEAD log:")
print(o)
# tick lock face
for cand in (os.path.join(ROOT, "engine-tick"), os.path.join(ROOT, "Tools",
             "engine-tick"), os.path.join(ROOT, ".engine-tick")):
    if os.path.isdir(cand):
        for f in sorted(os.listdir(cand)):
            p = os.path.join(cand, f)
            if os.path.isfile(p):
                age = time.time() - os.path.getmtime(p)
                print("LOCKDIR %s %s age=%.1fmin" % (cand, f, age / 60))
# live process chain scan (tick = wscript->powershell->codely|node)
import psutil
for pr in psutil.process_iter(["pid", "name", "cmdline", "create_time"]):
    try:
        cl = " ".join(pr.info["cmdline"] or [])
        nm = (pr.info["name"] or "").lower()
        if ("tick" in cl.lower() or "codely" in cl.lower()) and \
                "orphan_face" not in cl and "_r814bmc" not in cl:
            ct = datetime.fromtimestamp(pr.info["create_time"]).strftime("%H:%M:%S")
            print("PROC %s pid=%d born=%s cmd=%s" % (nm, pr.pid, ct, cl[:110]))
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass
print("probe done")
