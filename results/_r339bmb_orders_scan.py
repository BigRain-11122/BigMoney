# r291 bm-b S0.5: orders full-scan diff vs heartbeat ack + round_no + decisions probe
import json, os, glob

hb_path = "fleet/machines/bm-b.json"
with open(hb_path, encoding="utf-8") as f:
    hb = json.load(f)
acked = set(hb.get("orders_ack", []))
all_orders = sorted(os.path.basename(p) for p in glob.glob("fleet/orders/O-*.md"))
unacked = [o for o in all_orders if o not in acked]
print("total_orders:", len(all_orders), "acked:", len(acked), "unacked:", len(unacked))
for o in unacked:
    print("UNACKED:", o)

state_path = "logs/iteration-loop/state.json"
if os.path.exists(state_path):
    with open(state_path, encoding="utf-8") as f:
        st = json.load(f)
    print("state round_no:", st.get("round_no"), "| keys:", sorted(st.keys()))
else:
    print("state.json MISSING at", state_path)

dp = r"..\..\docs\decisions.md"
print("decisions.md exists:", os.path.exists(dp), "| size:", os.path.getsize(dp) if os.path.exists(dp) else None)
if os.path.exists(dp):
    with open(dp, encoding="utf-8", errors="replace") as f:
        lines = f.readlines()
    print("decisions total lines:", len(lines))
    print("".join(lines[-12:]))
