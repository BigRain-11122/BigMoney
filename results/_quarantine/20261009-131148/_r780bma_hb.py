import json, time, datetime

now = datetime.datetime.now().astimezone()
clock_read = now.strftime("%Y-%m-%dT%H:%M:%S") + ("+" if now.utcoffset() >= datetime.timedelta(0) else "-") + now.strftime("%H%M")[:2] + "00"
# proper ISO with offset:
iso = now.isoformat(timespec="seconds")
epoch = int(time.time())

# --- heartbeat fleet/machines/bm-a.json (single-writer: bm-a only) ---
p = "fleet/machines/bm-a.json"
hb = json.load(open(p, encoding="utf-8"))
hb["last_seen"] = now.strftime("%Y-%m-%d %H:") + "5x"
hb["ts"] = iso
hb["clock_read"] = iso
hb["heartbeat_epoch_utc"] = epoch
hb["last_heartbeat_epoch_utc"] = epoch
hb["current_task"] = "r780 recovery round complete (dead-r779 stranded W159 work preserved+pushed, O-1410 ts-field evidence landed); next = W159 freeze commit via r775 bloodline + ignition (never-dry lane <=48h)"
hb["verdict"] = "recovery: smoke 48/48, engine alive idle, no active burns; W159 seat ADMIT on origin, freeze pending"
ack = hb["orders_ack"]
if "O-20261006-1410-bm-a.md" not in ack:
    ack.append("O-20261006-1410-bm-a.md")
json.dump(hb, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# --- state-bm-a.json (single-writer: bm-a only) ---
sp = "state-bm-a.json"
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = 780  # r779 number consumed by dead session in git; recovery round = 780
st["last_round"] = "r780"
st["last_round_at"] = iso
st["last_round_ts"] = now.strftime("%Y-%m-%dT%H:") + "5x"
st["last_seen"] = now.strftime("%Y-%m-%d %H:") + "5x"
st["heartbeat_epoch_utc"] = epoch
st["current_task"] = "W159 freeze commit (r775 freeze-edits bloodline) + ignition; D-06 window 10-07"
st["did"] = "r780 recovery: dead-r779 session detected (died post-commit pre-S7: no RR/state/heartbeat), stranded W159 artifacts preserved verbatim + pushed (94eca751b rebased, merge-absorbed bm-c r625/626 + bm-b r775 churn legs, delivery verified behind=0), O-1410 item1 ts-field heartbeat evidence completed this round, orders_ack +O-1410, backlog bigstream claim line committed"
st["last_action"] = "r780 closeout: recovery commit + heartbeat ts first-evidence + state 780 + RR line"
json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# self-verify (smoke F7 face)
hb2 = json.load(open(p, encoding="utf-8"))
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in hb2["clock_read"] and "+" in hb2["clock_read"], "clock_read must be T-separated ISO8601 with offset"
assert hb2["ts"] == hb2["clock_read"], "ts must equal clock_read same-source"
assert "O-20261006-1410-bm-a.md" in hb2["orders_ack"]
st2 = json.load(open(sp, encoding="utf-8"))
assert st2["round_no"] == 780
print("HB+STATE OK | epoch int:", hb2["heartbeat_epoch_utc"], "| clock:", hb2["clock_read"], "| round_no:", st2["round_no"])
