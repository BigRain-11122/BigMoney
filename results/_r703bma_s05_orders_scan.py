# r703 bm-a S0.5 orders scan: full-name set-diff (r477 law) + new-order content dump
import json, os, glob

orders = sorted(os.path.basename(p) for p in glob.glob("fleet/orders/O-*.md"))
hb = json.load(open("fleet/machines/bm-a.json", encoding="utf-8"))
ack = hb.get("orders_ack", [])
if isinstance(ack, dict):
    ack = list(ack.keys())
ack_set = set(ack)
unacked = [o for o in orders if o not in ack_set]
print(f"orders total={len(orders)} acked={len(ack_set & set(orders))} UNACKED={len(unacked)}")
for o in unacked:
    print("== UNACKED ORDER:", o, "==")
    try:
        txt = open(os.path.join("fleet/orders", o), encoding="utf-8", errors="replace").read()
        print(txt[:2600])
    except Exception as e:
        print("READ-FAIL", e)
