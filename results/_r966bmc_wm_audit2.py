# -*- coding: utf-8 -*-
"""r966 watermark audit v2: skip missing-path commits; verify DEC phantom;
dump ORD diff 7fe46f3eb..origin/main (last genuine consumed face)."""
import io, json, subprocess, hashlib

GROUP = r"K:\Fluxgroup\FluxGroup"
state = json.load(io.open(r"state-bm-c.json", encoding="utf-8"))
W_DEC = state["last_decisions_sha"]

def sh(cmd):
    p = subprocess.run(["git", "-C", GROUP] + cmd, capture_output=True)
    return p.stdout, p.returncode

# --- DEC: walk history, tolerate missing path ---
commits = sh(["log", "--format=%H", "-20", "--", "docs/decisions.md"])[0].decode().split()
print("== DEC faces (want %s...)" % W_DEC[:16])
dec_hit = None
for c in commits:
    b, rc = sh(["show", c + ":docs/decisions.md"])
    if rc != 0:
        print("   %s (path absent, skipped)" % c[:9])
        continue
    s = hashlib.sha256(b).hexdigest()
    mark = "  <== MATCH" if s == W_DEC else ""
    print("   %s %s%s" % (c[:9], s[:16], mark))
    if s == W_DEC:
        dec_hit = c
print("DEC phantom confirmed" if dec_hit is None else "DEC match at " + dec_hit[:9])

# commit time of the current DEC face holder
out, _ = sh(["log", "--format=%H %ci", "-3", "--", "docs/decisions.md"])
print("DEC recent commits:", out.decode()[:500])

# --- ORD: diff last genuine face (7fe46f3eb) .. origin/main ---
b, rc = sh(["show", "7fe46f3eb:docs/orders.md"])
assert rc == 0
old_sha = hashlib.sha256(b).hexdigest()
print("\nORD base 7fe46f3eb face sha256:", old_sha[:16], "(state r963 watermark was 29c2ba65:",
      old_sha.startswith("29c2ba65"), ")")
d, rc = sh(["diff", "7fe46f3eb", "origin/main", "--", "docs/orders.md"])
io.open(r"results\_r966bmc_orddiff.txt", "wb").write(d)
print("ORD diff lines:", len(d.decode('utf-8', 'replace').splitlines()))

# also verify r965's ORD phantom against history
W_ORD = state["last_orders_sha"]
ord_hit = None
oc = sh(["log", "--format=%H", "-20", "--", "docs/orders.md"])[0].decode().split()
for c in oc:
    b2, rc2 = sh(["show", c + ":docs/orders.md"])
    if rc2 == 0 and hashlib.sha256(b2).hexdigest() == W_ORD:
        ord_hit = c
print("ORD phantom confirmed" if ord_hit is None else "ORD match at " + ord_hit[:9])
