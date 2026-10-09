# -*- coding: utf-8 -*-
"""r814 bm-c: group orders.md added rows -> UTF-8 file (console mojibake
bypass, r813 h3_recon paradigm) + inbound commit subjects + group-tree
Tools/poke-worker + fleet-link v1.2 presence probe. Read-only."""
import subprocess

CNW = 0x08000000
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
GROUP = r"K:\Fluxgroup\FluxGroup"
OUT = ROOT + r"\results\_r814bmc_orders_delta.txt"


def g(cwd, args, timeout=60):
    try:
        r = subprocess.run(["git", "-C", cwd] + args, capture_output=True,
                           creationflags=CNW, timeout=timeout)
        return r.returncode, (r.stdout or b"").decode("utf-8", "replace"), \
            (r.stderr or b"").decode("utf-8", "replace")
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"


lines = []
rc, rl, _ = g(GROUP, ["reflog", "show", "origin/main", "-n", "4",
                      "--format=%H %gs"], timeout=30)
tips = [l.split(" ", 1)[0] for l in rl.splitlines()
        if l.strip() and len(l.split(" ", 1)[0]) == 40]
lines.append("GROUP-REFLOG tips=%s" % ",".join(t[:8] for t in tips))
rc, new, _ = g(GROUP, ["show", "origin/main:docs/orders.md"], timeout=30)
old = ""
for t in tips[1:]:
    rc2, ob, _ = g(GROUP, ["show", t + ":docs/orders.md"], timeout=30)
    if rc2 == 0 and ob:
        old = ob
        lines.append("OLD-TIP %s (added rows vs this tip)" % t[:8])
        break
if old:
    old_set = set(old.splitlines())
    added = [l for l in new.splitlines() if l not in old_set and l.strip()]
    lines.append("ORDERS-ADDED %d (verbatim below)" % len(added))
    for l in added:
        lines.append("ADD| " + l)
else:
    lines.append("OLD-BLOB-UNAVAILABLE")
# recent bigmoney commits (delivery face context)
rc, o, _ = g(ROOT, ["log", "-6", "--format=%h %an %s"], timeout=30)
lines.append("--- bigmoney log -6 ---")
for l in o.splitlines():
    if l.strip():
        lines.append("LOG| " + l)
# group-tree fleet tool faces (v1.2 materialized upstream already?)
for p in ("Tools/fleet-link.ps1", "Tools/poke-worker.ps1",
          "Tools/register-fleet-link.ps1"):
    rc, o, _ = g(GROUP, ["show", "origin/main:" + p], timeout=30)
    tag = "rc=%d bytes=%d" % (rc, len(o.encode("utf-8")))
    v12 = "1.2" in o
    hot = "HOT" in o
    cold = "COLD" in o
    lines.append("GROUPFACE %s %s v1.2=%s HOT=%s COLD=%s"
                 % (p, tag, v12, hot, cold))
# group-tree dirty face (is the GM/bm-a mid-work on the group tree?)
rc, o, _ = g(GROUP, ["status", "--porcelain"], timeout=30)
dirty = [l.strip() for l in o.splitlines() if l.strip()]
lines.append("GROUP-DIRTY %d %s" % (len(dirty), " | ".join(dirty[:6])))
with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("orders-delta written: %d lines" % len(lines))
