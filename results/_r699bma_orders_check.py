"""r699 bm-a orders diff probe (r477 full-name same-shape law + r696 ls-tree
tree-ish form)."""
import json
import subprocess

r = subprocess.run(
    ["git", "ls-tree", "--name-only", "HEAD:fleet/orders"],
    capture_output=True, timeout=30)
orders = {x.decode("utf-8") for x in r.stdout.splitlines()
          if x.decode("utf-8", "replace").startswith("O-")}
h = json.load(open("fleet/machines/bm-a.json", encoding="utf-8"))
acked = {x for x in (h.get("orders_ack") or [])}
unacked = sorted(orders - acked)
extra = sorted(acked - orders)
print("orders_total=", len(orders), "acked=", len(acked),
      "unacked=", len(unacked), "ack_extra=", len(extra))
for x in unacked:
    print("UNACKED:", x)
for x in extra[:5]:
    print("ACK_EXTRA:", x)
