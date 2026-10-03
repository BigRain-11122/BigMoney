import subprocess, json, io, sys
RB = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CRE = 0x08000000  # CREATE_NO_WINDOW (U060 zero-flash law)

def sh(*a):
    return subprocess.check_output(list(a), stderr=subprocess.STDOUT, creationflags=CRE)

# fleet orders on origin (ls-tree, same-口径 both sides per r446 law)
out = sh("git", "-C", RB, "ls-tree", "--name-only", "origin/main", "fleet/orders/")
origin_orders = set()
for ln in out.decode("utf-8", "replace").splitlines():
    ln = ln.strip().replace("\\", "/")
    base = ln.rsplit("/", 1)[-1]  # strip fleet/orders/ prefix (same-口径 as ack list)
    if base.startswith("O-") and base.endswith(".md"):
        origin_orders.add(base)
print("ORIGIN_ORDERS=%d" % len(origin_orders))

# heartbeat ack set (same ls-tree 口径: file names, not timestamps)
with io.open(RB + r"\fleet\machines\bm-c.json", "r", encoding="utf-8") as f:
    hb = json.load(f)
acked = set(hb.get("orders_ack", []))
print("ACKED=%d" % len(acked))

new = sorted(origin_orders - acked)
ghost = sorted(acked - origin_orders)
print("NEW_UNACKED=%s" % (json.dumps(new) if new else "NONE"))
print("GHOST_ACK=%s" % (json.dumps(ghost) if ghost else "NONE"))
