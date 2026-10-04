# Round 661 closeout: state round_no++ + heartbeat update (r645 json.dump+loads self-check, R170/R178 epoch int law, R262 clock T-separator law)
import json, time, datetime

# 1) state.json round_no 660 -> 661
s = json.load(open("state.json", encoding="utf-8"))
s["round_no"] = 661
s["last_round_at"] = datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S+08:00")
s["updated"] = datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S+08:00")
s["ts"] = datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S+08:00")
s["last_seen"] = "2026-10-04T09:41:00+08:00"
s["round_no_label"] = "bm-b round 661 (golden-week watch; QUALITY adoption confirmed dba59ee9c; trio V682/Q521/D378; S6 38-leg chain rc0)"
with open("state.json", "w", encoding="utf-8", newline="") as f:
    json.dump(s, f, ensure_ascii=False, indent=1)
chk = json.load(open("state.json", encoding="utf-8"))
assert chk["round_no"] == 661, "round_no write failed"
print("state.json round_no ->", chk["round_no"], "| self-check PASS")

# 2) heartbeat fleet/machines/bm-b.json
epoch = int(time.time())
clock = datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S+08:00")
h = json.load(open("fleet/machines/bm-b.json", encoding="utf-8"))
h["last_seen"] = clock
h["heartbeat_epoch_utc"] = epoch  # python int, NOT string (R170/R178)
h["clock_read"] = clock  # T-separator ISO 8601 (R262)
h["current_task"] = "golden-week watch r661: FUND trio NULLS canonical burns (V682/Q521/D378 of 2000) + QUALITY adoption confirmed"
h["verdict"] = "healthy"
h["cpu_cores"] = 16
h["orders_ack_count"] = len(h.get("orders_ack", []))
with open("fleet/machines/bm-b.json", "w", encoding="utf-8", newline="") as f:
    json.dump(h, f, ensure_ascii=False, indent=1)
chk2 = json.load(open("fleet/machines/bm-b.json", encoding="utf-8"))
assert isinstance(chk2["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in chk2["clock_read"], "clock must be T-separated"
print("heartbeat epoch=", chk2["heartbeat_epoch_utc"], "clock=", chk2["clock_read"], "| self-check PASS (int + T)")
