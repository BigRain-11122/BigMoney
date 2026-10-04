"""r684 bm-a S7 bookkeeping: state round_no 683->684 (programmatic write +
json.loads self-verify per r645 law) + heartbeat epoch/clock update.
Zero canon faces touched beyond these two bookkeeping files."""
import json
import time
from datetime import datetime, timezone, timedelta

# state
p = "state-bm-a.json"
s = json.load(open(p, encoding="utf-8"))
assert s.get("round_no") == 683, f"unexpected round_no {s.get('round_no')}"
s["round_no"] = 684
s["next"] = ("r685+: W117 finalize window (GATED on bm-b W116 finalize landing -- "
             "rehearsal PASS r684, guards green + chain gate FAIL-CLOSED verified, "
             "zero-write x2; fire finalize --wave 117 the round W116 lands) + "
             "W116 burn watch (bm-b RAM-floor hold, engine lane) + fund trio NULLS "
             "finalize 10-05..09 watch (bm-b canonical in-flight) + 10-06+ next-wave "
             "candidate drafting (style-rotation family form, needs bm-b astock_daily "
             "panel per r681 pointer)")
json.dump(s, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(p, encoding="utf-8"))
assert chk["round_no"] == 684 and isinstance(chk["round_no"], int)
print("state: 683->684 ok, reparse ok")

# heartbeat
hp = "fleet/machines/bm-a.json"
h = json.load(open(hp, encoding="utf-8"))
epoch = int(time.time())
clock = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%dT%H:%M:%S+08:00")
h["last_seen"] = clock
h["heartbeat_epoch_utc"] = epoch
h["clock_read"] = clock
h["current_task"] = ("r684: W117 finalize rehearsal PASS (one-shot protection, r633 "
                     "pattern) + S6 37/37 rc0; W117 finalize armed on W116 landing")
h["verdict"] = "green"
json.dump(h, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in chk["clock_read"] and "+" in chk["clock_read"], "clock must be T-form with offset"
print(f"heartbeat: epoch={epoch} int ok, clock={clock} T-form ok")
