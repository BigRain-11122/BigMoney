# r379 bm-c S0.5 orders scan (R13 programmatic full-set diff, no name-sort windows)
import json, os, glob
orders_dir = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\fleet\orders"
acked = set()
try:
    with open(r"K:\Fluxgroup\FluxGroup\quant\bigmoney\fleet\machines\bm-c.json", encoding="utf-8") as f:
        hb = json.load(f)
    acked = set(hb.get("orders_ack", []))
except Exception as e:
    print("HB-READ-FAIL", e)
all_orders = set()
for p in glob.glob(os.path.join(orders_dir, "O-*.md")):
    all_orders.add(os.path.basename(p))
unacked = sorted(all_orders - acked)
print("total_orders", len(all_orders), "acked", len(acked & all_orders), "unacked", len(unacked))
for u in unacked:
    print("UNACKED:", u)
stale = sorted(acked - all_orders)
if stale:
    print("stale_ack_entries", len(stale))
# inbox unprocessed listing
inbox = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\fleet\inbox"
for p in sorted(glob.glob(os.path.join(inbox, "*"))):
    print("INBOX:", os.path.basename(p))
