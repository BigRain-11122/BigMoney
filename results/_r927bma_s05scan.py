import json, hashlib, subprocess
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

# 3) group decisions/orders sha (raw bytes canonical; DEC=sha256, ORD=sha1 algorithm pin per r537/r924)
r = subprocess.run(["git","-C",GR,"fetch","origin"],capture_output=True)
res = {}
for f,key,algo in [("docs/decisions.md","dec","sha256"),("docs/orders.md","ord","sha1")]:
    g = subprocess.run(["git","-C",GR,"show","origin/main:"+f],capture_output=True)
    b = g.stdout
    res[key] = hashlib.new(algo, b).hexdigest()
    res[key+"_len"] = len(b)
out["group"] = res
out["expect_dec"] = "31e85972112d836e4e70daf55ac9bf2d07f64be9bc74efd516dd8b0961ec1514"
out["expect_ord"] = "0a1d9c1d4a77fd02177f49044bd117f6183fa462"

print(json.dumps(out, ensure_ascii=False, indent=1))
