# -*- coding: utf-8 -*-
"""r813 bm-c FleetLink v1.1 upgrade executor (O-20261009-1750 dispatch,
'pull 本批后下一轮执行' = THIS round):
Step A: materialize v1.1 faces from group-tree origin/main into the working
  tree (git checkout origin/main -- <paths>): fleet-link.ps1 (v1.1 listener,
  11827B w/ poke-worker+repo_heads+self-upgrade), fleet-poke-worker.ps1 (NEW,
  4851B), register-fleet-link.ps1 (MultipleInstances Parallel). All three are
  tracked-clean locally -> zero in-flight clobber; fleet-nodes.json local
  dirty face NOT touched (bm-c host=FLUXGROUP already correct in both).
Step B: kill running v1.0 listener (pid found via psutil cmdline match
  'fleet-link' among powershell procs; THIS python host cmdline contains
  'fleetlink' WITHOUT hyphen -> self-match impossible by construction).
Step C: verify port 8790 is free / old instance gone (receipt precondition).
Register + health verification happen in the follow-up shell legs."""
import subprocess
import io
import os
import time

CNW = 0x08000000
G = "K:/Fluxgroup/FluxGroup"
R = "K:/Fluxgroup/FluxGroup/quant/bigmoney"
log = io.open(os.path.join(R, "results", "_r813bmc_fleetlink_upgrade.log"), "w",
              encoding="utf-8")
w = lambda s: (log.write(s + "\n"), log.flush())


def g(args, t=60):
    r = subprocess.run(["git", "-C", G] + args, capture_output=True,
                       creationflags=CNW, timeout=t)
    return r.returncode, r.stdout.decode("utf-8", "replace"), \
        r.stderr.decode("utf-8", "replace")


# --- Step A: materialize v1.1 faces ---
faces = ["Tools/fleet-link.ps1", "Tools/fleet-poke-worker.ps1",
         "Tools/register-fleet-link.ps1"]
rc, o, e = g(["checkout", "origin/main", "--"] + faces)
w("checkout rc=%d err=%s" % (rc, e.strip()[:200]))
for f in faces:
    p = os.path.join(G, f.replace("/", "\\"))
    w("  face %s exists=%s bytes=%d" % (f, os.path.exists(p),
                                        os.path.getsize(p) if os.path.exists(p) else -1))
rc, o, e = g(["status", "--porcelain", "--"] + faces)
w("status faces after checkout: %s" % " | ".join(
    [l.strip() for l in o.splitlines() if l.strip()]))

# --- Step B: kill v1.0 listener (self-match safe) ---
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

# --- Step C: confirm gone ---
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
print("upgrade steps A-C done: killed=%d still=%s" % (
    len(killed), still or "none"))
