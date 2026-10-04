# r670 bm-a S0 probe: origin round_no + local state read (subprocess raw bytes per pit-encoding)
import json, subprocess, sys

def read_blob(path, ref="origin/main"):
    b = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True).stdout
    return b.decode("utf-8", errors="replace")

origin_state = json.loads(read_blob("state-bm-a.json"))
local_state = json.loads(open("state-bm-a.json", encoding="utf-8").read())
print("origin round_no:", origin_state.get("round_no"))
print("local  round_no:", local_state.get("round_no"))
print("origin last_decisions_sha:", origin_state.get("last_decisions_sha"))
print("local  last_decisions_sha:", local_state.get("last_decisions_sha"))
print("origin last_orders_sha:", origin_state.get("last_orders_sha"))
print("local  last_orders_sha:", local_state.get("last_orders_sha"))
ack_o = origin_state.get("orders_ack", {})
ack_l = local_state.get("orders_ack", {})
print("origin orders_ack count:", len(ack_o), "local:", len(ack_l))
diff = set(ack_o) ^ set(ack_l)
if diff:
    print("ack key diff:", sorted(diff))
else:
    print("ack keys identical")
hb_o = origin_state.get("heartbeat_epoch_utc"); hb_l = local_state.get("heartbeat_epoch_utc")
print("origin hb_epoch:", hb_o, type(hb_o).__name__)
print("local  hb_epoch:", hb_l, type(hb_l).__name__)
