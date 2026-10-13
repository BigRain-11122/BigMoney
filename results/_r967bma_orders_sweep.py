# r967: fleet orders ack diff sweep (round-start full scan per law, no ts filtering)
import json, os, re

ORD_DIR = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney\fleet\orders"
HB = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney\fleet\machines\bm-a.json"

files = sorted(f for f in os.listdir(ORD_DIR) if f.startswith("O-") and f.endswith(".md"))
with open(HB, encoding="utf-8") as f:
    hb = json.load(f)
acked = hb.get("orders_ack", [])
acked_set = set(acked)
print("O-files:", len(files), "acked:", len(acked_set))
unacked = [f[:-3] for f in files if f[:-3] not in acked_set]
print("UNACKED:", len(unacked))
for u in unacked:
    print("  -", u)
# also check for newest orders by mtime
import time
mt = sorted(((os.path.getmtime(os.path.join(ORD_DIR, f)), f) for f in files), reverse=True)[:5]
for t, f in mt:
    print("NEWEST:", f, time.strftime("%m-%d %H:%M", time.localtime(t)))
