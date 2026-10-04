"""r671 bm-a orders diff: all O-*.md vs heartbeat orders_ack list."""
import json, glob, os, io
REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
out = io.StringIO()
orders = sorted(os.path.basename(p)[:-3] for p in glob.glob(REPO + r"\fleet\orders\O-*.md"))
hb = json.load(open(REPO + r"\fleet\machines\bm-a.json", encoding="utf-8"))
ack = hb.get("orders_ack", [])
ack_set = set(ack if isinstance(ack, list) else ack.keys())
missing = [o for o in orders if o not in ack_set]
w = open(r"C:\Users\sjs20\AppData\Local\Temp\r671_orders_diff.txt", "w", encoding="utf-8")
w.write(f"total orders: {len(orders)}\nacked: {len(ack_set)}\nmissing ({len(missing)}):\n")
for m in missing:
    w.write(m + "\n")
w.close()
print(f"total={len(orders)} acked={len(ack_set)} missing={len(missing)}")
