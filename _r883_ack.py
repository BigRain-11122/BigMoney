import json, hashlib, subprocess, datetime
p = r"fleet\machines\bm-c.json"
h = json.load(open(p, encoding="utf-8"))
if "O-20261011-1811-bm-c" not in h.get("orders_ack", []):
    h["orders_ack"].append("O-20261011-1811-bm-c")
json.dump(h, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("ack appended, total:", len(h["orders_ack"]))
