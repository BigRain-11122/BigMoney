# r500 bm-c S0.5: orders diff (same-shape full-filename sets, r477/r696b law)
# + inbox unread scan for bm-c/ALL. Output to file only (r446/r458 laws).
import json, subprocess, sys

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"

def git(*args):
    p = subprocess.run(["git", "-C", REPO] + list(args), capture_output=True)
    return p.stdout.decode("utf-8", "replace"), p.returncode

# 1) orders set from tree-ish (r696b: directory pathspec returns the tree entry itself;
#    correct form = HEAD:fleet/orders)
out, rc = git("ls-tree", "--name-only", "HEAD:fleet/orders")
orders = sorted(ln for ln in out.splitlines() if ln.startswith("O-") and ln.endswith(".md"))

# 2) heartbeat ack set (full filenames with .md, r477 law)
with open(REPO + r"\fleet\machines\bm-c.json", "r", encoding="utf-8") as f:
    hb = json.load(f)
acked = set(hb.get("orders_ack", []) or [])
unacked = [o for o in orders if o not in acked]
ack_extra = sorted(a for a in acked if a not in set(orders))

# 3) inbox unread for bm-c / ALL
out, rc = git("ls-tree", "--name-only", "HEAD:fleet/inbox")
inbox = [ln for ln in out.splitlines() if ln.startswith("MSG-")]
mine = []
for m in inbox:
    body, rc2 = git("show", "HEAD:fleet/inbox/" + m)
    low = body.lower()
    if ("bm-c" in low) or ("all" in low):
        mine.append(m)

receipt = {
    "orders_total": len(orders),
    "acked_total": len(acked),
    "unacked": unacked,
    "ack_extra_note": ack_extra,
    "inbox_unread_mine_or_all": mine,
}
with open(REPO + r"\results\_r500bmc_s05.txt", "w", encoding="utf-8") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print("S05-OK " + json.dumps(receipt, ensure_ascii=False))
