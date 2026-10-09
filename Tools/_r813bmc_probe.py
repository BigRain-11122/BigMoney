# -*- coding: utf-8 -*-
"""r813 bm-c recon probe: group-tree state, register-fleet-link v1.1 presence,
queue faces, pool ready count. Read-only."""
import subprocess
import json
import os
import io

CNW = 0x08000000
G = "K:/Fluxgroup/FluxGroup"
R = "K:/Fluxgroup/FluxGroup/quant/bigmoney"
sysenc = lambda b: b.decode("utf-8", "replace")


def gb(args, t=60):
    r = subprocess.run(["git", "-C", G] + args, capture_output=True,
                       creationflags=CNW, timeout=t)
    return r.returncode, sysenc(r.stdout or b""), sysenc(r.stderr or b"")


out = io.open(os.path.join(R, "results", "_r813bmc_probe.txt"), "w",
              encoding="utf-8")
w = out.write
rc, o, e = gb(["status", "--porcelain"])
lines = [l.strip() for l in o.splitlines() if l.strip()]
w("GROUP dirty_n=%d\n" % len(lines))
w("GROUP dirty sample: %s\n" % " | ".join(lines[:15]))
rc, o, e = gb(["rev-parse", "HEAD", "origin/main"])
w("HEAD/origin: %s\n" % o.replace("\n", " "))
rc, o, e = gb(["rev-list", "--left-right", "--count", "HEAD...origin/main"])
w("behind-ahead(local-side left): %s\n" % o.strip())
rc, o, e = gb(["show", "origin/main:Tools/register-fleet-link.ps1"])
w("register-fleet-link.ps1 rc=%d bytes=%d\n" % (rc, len(o.encode("utf-8"))))
w("  MultipleInstances=%s  ver-1.1=%s  selfupgrade=%s\n" % (
    "MultipleInstances" in o, "1.1" in o, "kill" in o.lower()))
rc2, o2, e2 = gb(["show", "origin/main:Tools/fleet-workspace-audit.ps1"])
w("fleet-workspace-audit.ps1 rc=%d bytes=%d\n" % (rc2, len(o2.encode("utf-8"))))
w("queue files: %s\n" % sorted(os.listdir(os.path.join(R, "state", "queue"))))
try:
    pool = json.load(open(os.path.join(R, "results", "runnable_pool.json"),
                          encoding="utf-8"))
    entries = pool.get("entries", pool if isinstance(pool, list) else [])
    if isinstance(entries, dict):
        entries = list(entries.values())
    ready = [x for x in entries if isinstance(x, dict)
             and x.get("status") == "ready"]
    w("pool entries=%d ready=%d\n" % (len(entries), len(ready)))
    for x in entries:
        if isinstance(x, dict) and x.get("status") == "ready":
            w("  ready: %s\n" % x.get("id", x.get("task_id", "?")))
except Exception as ex:
    w("pool read err: %s\n" % ex)
out.close()
print("probe written")
