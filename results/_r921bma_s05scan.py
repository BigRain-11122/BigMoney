import json, hashlib, subprocess, os
from pathlib import Path
ROOT = Path(r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney")
GR = r"C:\Users\sjs20\Desktop\FluxGroup"
out = {}

# 1) orders diff: fleet/orders O-*.md vs heartbeat orders_ack
hb = json.loads((ROOT/"fleet/machines/bm-a.json").read_text(encoding="utf-8"))
ack = set(hb.get("orders_ack", []))
disk = {p.name for p in (ROOT/"fleet/orders").glob("O-*.md")}
unacked = sorted(disk - ack)
out["orders_disk"] = len(disk)
out["orders_unacked"] = unacked

# 2) inbox unread (not in processed)
inbox = ROOT/"fleet/inbox"; proc = ROOT/"fleet/inbox/processed"
proc_names = {p.name for p in proc.glob("*.md")} if proc.exists() else set()
unread = [p.name for p in inbox.glob("*.md") if p.name not in proc_names]
out["inbox_unread"] = unread

# 3) group decisions/orders sha (raw bytes canonical)
r = subprocess.run(["git","-C",GR,"fetch","origin"],capture_output=True)
res = {}
for f,key in [("docs/decisions.md","dec"),("docs/orders.md","ord")]:
    g = subprocess.run(["git","-C",GR,"show","origin/main:"+f],capture_output=True)
    b = g.stdout
    res[key] = hashlib.sha256(b).hexdigest()
    res[key+"_len"] = len(b)
out["group"] = res
out["expect_dec"] = "bd94a27ba4ac39bc9a05037ddcfaf693cd78126aa6189711e8f7f1848a8ac522"
out["expect_ord"] = "b38eaaf8aec9e64ce9d1c7caa12aa5aebc50ae1d22e0eac8745994d960052507"

print(json.dumps(out, ensure_ascii=False, indent=1))
