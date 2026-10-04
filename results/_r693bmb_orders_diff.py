"""r693 bm-b: fleet/orders vs heartbeat orders_ack same-caliber set diff (r646/r477).

Both sides use full filenames (O-*.md); no cross-caliber counting.
Writes results/_r693bmb_orders_diff.json; exit 0.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORD = os.path.join(ROOT, "fleet", "orders")
HB = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
OUT = os.path.join(ROOT, "results", "_r693bmb_orders_diff.json")

orders = sorted(f for f in os.listdir(ORD)
                if f.startswith("O-") and f.endswith(".md"))
hb = json.load(open(HB, encoding="utf-8"))
ack = set(hb.get("orders_ack") or [])
o_set = set(orders)
res = {"orders_n": len(orders), "ack_n": len(ack),
       "unacked": sorted(o_set - ack), "ack_extra": sorted(ack - o_set)}
json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=True, indent=1)
print(json.dumps(res, ensure_ascii=True))
sys.exit(0)
