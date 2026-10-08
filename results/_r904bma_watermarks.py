# -*- coding: utf-8 -*-
"""r904 bm-a: DEC/ORD watermark check (python raw-bytes canonical, r711/
r868 law) + fleet orders ack diff scan."""
import hashlib
import json
import os
import subprocess

CAND = [
    r"K:\Fluxgroup\FluxGroup",
    r"C:\Users\sjs20\Desktop\FluxGroup",
]


def git(cwd, *a):
    r = subprocess.run(["git", "-C", cwd] + list(a), capture_output=True)
    return r.returncode, r.stdout


root = None
for c in CAND:
    if os.path.isdir(c):
        rc, _ = git(c, "rev-parse", "--git-dir")
        if rc == 0:
            root = c
            break
assert root, "no group tree real path found"
print("group tree:", root)
git(root, "fetch", "origin")
rc, dec = git(root, "show", "origin/main:docs/decisions.md")
rc2, ord_ = git(root, "show", "origin/main:docs/orders.md")
dec_sha = hashlib.sha256(dec).hexdigest()
ord_sha = hashlib.sha256(ord_).hexdigest()
print("DEC sha:", dec_sha[:16])
print("ORD sha:", ord_sha[:16])
hb_path = r"fleet\machines\bm-a.json"
hb = json.load(open(hb_path, encoding="utf-8"))
last_dec = hb.get("last_decisions_sha", "")
last_ord = hb.get("last_orders_sha", "")
print("hb DEC:", str(last_dec)[:16], "MATCH" if dec_sha == last_dec
      else "CHANGED")
print("hb ORD:", str(last_ord)[:16], "MATCH" if ord_sha == last_ord
      else "CHANGED")
# fleet orders diff scan
acks = hb.get("orders_ack", {})
if isinstance(acks, dict):
    acked = set(acks.keys())
else:
    acked = set(acks)
files = sorted(f for f in os.listdir("fleet/orders")
               if f.startswith("O-") and f.endswith(".md"))
unacked = [f for f in files if f[:-3] not in acked and f not in acked]
print("orders files:", len(files), "unacked:", unacked or "NONE")
# tail rows of orders.md mentioning BigMoney (rough scan of new rows)
rows = ord_.decode("utf-8", errors="replace").splitlines()
bm_rows = [r for r in rows if ("BigMoney" in r or "bigmoney" in r
                               or "quant" in r.lower())]
print("orders.md BigMoney rows total:", len(bm_rows))
print("orders.md tail 3 rows:")
for r in rows[-3:]:
    print("  ", r[:150])
