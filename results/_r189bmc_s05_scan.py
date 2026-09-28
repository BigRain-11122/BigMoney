import glob, io, json, os, re

root = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
orders_dir = os.path.join(root, "fleet", "orders")
hb_path = os.path.join(root, "fleet", "machines", "bm-c.json")

hb = json.load(io.open(hb_path, encoding="utf-8"))
acked = set(hb.get("orders_ack", []))
all_orders = set()
for p in glob.glob(os.path.join(orders_dir, "*.md")):
    all_orders.add(os.path.basename(p))

unacked = sorted(all_orders - acked)
print(f"orders total={len(all_orders)} acked={len(acked)} unacked={len(unacked)}")
for o in unacked:
    print("UNACKED:", o)

# decisions tail: new rows beyond D-20260928-06
dec = os.path.join(root, "..", "..", "docs", "decisions.md")
if os.path.exists(dec):
    txt = io.open(dec, encoding="utf-8").read()
    rows = re.findall(r"D-20\d{6}-\d+", txt)
    from collections import Counter
    c = Counter(rows)
    print("decisions distinct ids (last 8 by order of first appearance):")
    seen = []
    for r in rows:
        if r not in seen:
            seen.append(r)
    print(seen[-8:])
else:
    print("decisions.md NOT FOUND at", dec)
