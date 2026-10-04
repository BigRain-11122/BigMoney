"""r696 bm-b S0.5 orders diff probe (r477 shape law: both sides full filename with .md)."""
import json, os, subprocess, sys

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root = parent of results/

# local tree orders (ls-tree same-口径)
out = subprocess.run(["git", "ls-tree", "--name-only", "HEAD:fleet/orders"],
                     capture_output=True, cwd=root).stdout.decode("utf-8", "replace")
orders = {ln.strip() for ln in out.splitlines() if ln.strip().endswith(".md") and ln.strip().startswith("O-")}

mb = os.path.join(root, "fleet", "machines", "bm-b.json")
with open(mb, "r", encoding="utf-8") as f:
    hb = json.load(f)
ack = set(hb.get("orders_ack", []))

unacked = sorted(orders - ack)
extra = sorted(ack - orders)
report = {"orders_total": len(orders), "ack_total": len(ack),
          "unacked": unacked, "ack_extra_non_order": [x for x in extra if not x.startswith("O-")],
          "ts": "2026-10-04T21:3x"}
with open(os.path.join(root, "results", "_r696bmb_orders_check.json"), "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=1)
print("ORDERS=", len(orders), "UNACKED=", len(unacked))
for u in unacked:
    print("UNACKED:", u)
