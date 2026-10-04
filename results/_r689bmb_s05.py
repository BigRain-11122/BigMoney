# r689 S0.5: orders ack diff (same-caliber both-side set compare, r646/r477 law) + round number truth read (r672 law: round_reports tail is truth)
import json, glob, os, io

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ack = set(json.load(open(os.path.join(root, "fleet", "machines", "bm-b.json"), encoding="utf-8"))["orders_ack"])
orders = set()
for p in glob.glob(os.path.join(root, "fleet", "orders", "O-*.md")):
    orders.add(os.path.basename(p))
unacked = sorted(orders - ack)
extra = sorted(ack - orders)
print("orders_total", len(orders), "ack_total", len(ack))
print("UNACKED:", json.dumps(unacked, ensure_ascii=False))
print("ACK_EXTRA:", json.dumps(extra, ensure_ascii=False))

# round number truth: bm-b uses logs/iteration-loop/round_reports.md tail
rp = os.path.join(root, "logs", "iteration-loop", "round_reports.md")
with io.open(rp, "rb") as f:
    lines = f.read().decode("utf-8", "replace").splitlines()
print("round_reports total_lines", len(lines))
print("TAIL5:")
for ln in lines[-5:]:
    print("  ", ln[:300])

st = json.load(open(os.path.join(root, "state.json"), encoding="utf-8"))
print("state.round_no", st.get("round_no"), "state.next", st.get("next"))
print("last_decisions_sha", st.get("last_decisions_sha"))
print("last_orders_sha", st.get("last_orders_sha"))
