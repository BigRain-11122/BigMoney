import json, os, re
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # results/ -> repo root
hb_path = os.path.join(root, "fleet", "machines", "bm-a.json")
orders_dir = os.path.join(root, "fleet", "orders")
hb = json.load(open(hb_path, encoding="utf-8"))
ack = hb.get("orders_ack") or []
if isinstance(ack, dict):
    ack_keys = set(ack.keys())
else:
    ack_keys = set(ack)
files = sorted(f for f in os.listdir(orders_dir) if re.match(r"O-.*\.md$", f))
print("hb keys:", sorted(hb.keys())[:30])
print("ack count:", len(ack_keys), "orders files:", len(files))
unacked = [f for f in files if f not in ack_keys]
print("UNACKED:", unacked)
print("ack-but-missing:", sorted(k for k in ack_keys if k + ".md" not in files and k not in files)[:10])
