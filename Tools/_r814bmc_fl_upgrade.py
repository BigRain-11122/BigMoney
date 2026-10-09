# -*- coding: utf-8 -*-
"""r814 bm-c FleetLink v1.2 upgrade executor (O-20261009-1755 Git 分级同步令,
bm-c action per the order row: kill old instance + re-register = v1.2 install;
1-gen clone of _r813bmc_fl_upgrade.py v1.1 procedure):
Step A: materialize v1.2 faces from group-tree origin/main (git checkout
  origin/main -- paths): fleet-link.ps1 (12266B, v1.2 three-tier HOT/WARM/COLD
  poke_repos='.'), fleet-poke-worker.ps1, register-fleet-link.ps1.
Step B: kill running v1.1 listener (psutil cmdline match 'fleet-link' among
  powershell procs; THIS python host cmdline = '_r814bmc_fl_upgrade' without
  hyphen -> self-match impossible by construction).
Register + /health v1.2 receipt happen in the follow-up legs."""
import subprocess
import io
import os
import time

CNW = 0x08000000
G = "K:/Fluxgroup/FluxGroup"
R = "K:/Fluxgroup/FluxGroup/quant/bigmoney"
log = io.open(os.path.join(R, "results", "_r814bmc_fleetlink_upgrade.log"), "w",
              encoding="utf-8")
w = lambda s: (log.write(s + "\n"), log.flush())


def g(args, t=60):
    r = subprocess.run(["git", "-C", G] + args, capture_output=True,
                       creationflags=CNW, timeout=t)
    return r.returncode, r.stdout.decode("utf-8", "replace"), \
        r.stderr.decode("utf-8", "replace")


faces = ["Tools/fleet-link.ps1", "Tools/fleet-poke-worker.ps1",
         "Tools/register-fleet-link.ps1"]
rc, o, e = g(["checkout", "origin/main", "--"] + faces)
w("checkout rc=%d err=%s" % (rc, e.strip()[:200]))
for f in faces:
    p = os.path.join(G, f.replace("/", "\\"))
    data = open(p, "rb").read() if os.path.exists(p) else b""
    w("  face %s exists=%s bytes=%d v1.2=%s" % (
        f, os.path.exists(p), len(data), b"1.2" in data))
rc, o, e = g(["status", "--porcelain", "--"] + faces)
w("status faces after checkout: %s" % " | ".join(
    [l.strip() for l in o.splitlines() if l.strip()]))

import psutil
killed = []
for pr in psutil.process_iter(["pid", "name", "cmdline"]):
    try:
        cl = " ".join(pr.info["cmdline"] or [])
        nm = (pr.info["name"] or "").lower()
        if "fleet-link" in cl and nm.startswith("powershell"):
            pr.kill()
            killed.append((pr.pid, cl[:120]))
            w("KILL pid=%d cmd=%s" % (pr.pid, cl[:120]))
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass
w("killed=%d" % len(killed))
time.sleep(2)
still = []
for pr in psutil.process_iter(["pid", "name", "cmdline"]):
    try:
        cl = " ".join(pr.info["cmdline"] or [])
        nm = (pr.info["name"] or "").lower()
        if "fleet-link" in cl and nm.startswith("powershell"):
            still.append(pr.pid)
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass
w("still_running=%s" % (still or "none"))
log.close()
print("v1.2 upgrade steps A-B done: killed=%d still=%s" % (
    len(killed), still or "none"))
