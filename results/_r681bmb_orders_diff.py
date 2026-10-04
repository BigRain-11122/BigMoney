"""r681 bm-b: S0.5 orders ledger diff (same-caliber set comparison, r646 law).

Compares fleet/orders/O-*.md disk set (full filenames) vs heartbeat
orders_ack set (full filenames). Zero timestamp filtering (R13 law).
Writes results/_r681bmb_orders_diff.json; prints unacked list.
"""
import json
import os
import re

REPO = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(REPO)
ORDERS_DIR = os.path.join(ROOT, "fleet", "orders")
HB = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
PAT = re.compile(r"^O-.*\.md$")

disk = {fn for fn in os.listdir(ORDERS_DIR) if PAT.match(fn)}
ack = set(json.load(open(HB, encoding="utf-8"))["orders_ack"])
unacked = sorted(disk - ack)
extra_ack = sorted(ack - disk)
out = {"disk_count": len(disk), "ack_count": len(ack),
       "unacked": unacked, "extra_ack": extra_ack}
json.dump(out, open(os.path.join(REPO, "_r681bmb_orders_diff.json"), "w",
                    encoding="utf-8"), ensure_ascii=True, indent=1)
print(json.dumps(out, ensure_ascii=True))
