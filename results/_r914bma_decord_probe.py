# -*- coding: utf-8 -*-
"""r914 bm-a DEC/ORD group watermark recompute (python-raw canonical,
r814-family law: PS-redirect artifacts forbidden)."""
import hashlib
import io
import json
import subprocess

GIT = r"C:\Program Files\Git\cmd\git.exe"
GRP = r"C:\Users\sjs20\Desktop\FluxGroup"

subprocess.run([GIT, "-C", GRP, "fetch", "origin"], capture_output=True)


def blob(path):
    return subprocess.run([GIT, "-C", GRP, "show", "origin/main:" + path],
                          capture_output=True).stdout


def sha(b):
    return hashlib.sha256(b).hexdigest()


dec = blob("docs/decisions.md")
orders = blob("docs/orders.md")
hb = json.load(io.open("fleet/machines/bm-a.json", encoding="utf-8"))
print("DEC  now=%s" % sha(dec)[:8], "held=%s" % hb["last_decisions_sha"][:8],
      "SAME" if sha(dec) == hb["last_decisions_sha"] else "CHANGED")
print("ORD  now=%s" % sha(orders)[:8], "held=%s" % hb["last_orders_sha"][:8],
      "SAME" if sha(orders) == hb["last_orders_sha"] else "CHANGED")

# scan tail rows for BigMoney-relevant fresh dispatches (since 10-09 09:00)
txt = orders.decode("utf-8", errors="replace")
rows = [r for r in txt.splitlines()
        if r.strip().startswith("|") and "10-09" in r
        and any(k in r for k in ("BigMoney", "量化", "bm-a"))]
print("10-09 BigMoney-mentioning ORD rows: %d" % len(rows))
for r in rows[-4:]:
    print("  ROW:", r[:180])
dtxt = dec.decode("utf-8", errors="replace")
drows = [r for r in dtxt.splitlines() if r.strip().startswith("|")
         and "10-09" in r]
print("10-09 DEC rows: %d" % len(drows))
for r in drows[-5:]:
    print("  DEC:", r[:170])
