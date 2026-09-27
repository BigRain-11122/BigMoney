# r370 bm-a S7: state round_no++ + heartbeat update (epoch MUST be int per R170/R178; clock_read T-separated per R262)
import json, time, datetime, platform

# state
sd = json.load(open("state-bm-a.json", encoding="utf-8"))
sd["round_no"] = 370
json.dump(sd, open("state-bm-a.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# heartbeat
now_iso = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())
hb = json.load(open("fleet/machines/bm-a.json", encoding="utf-8"))
hb.update({
    "last_seen": now_iso,
    "heartbeat_epoch_utc": epoch,
    "clock_read": now_iso,
    "current_task": "r370 done: V2-P1 lane pin re-adopt (r348-family 3rd swallow case) + D-20260928-03(1) S1 lane-migration census + hot-cold archive 25th batch",
    "cpu_cores": 32,
    "verdict": "py_low_board_clear (legal idle: local board closed, bandit empty, pool 2-ready both pinned bm-b lanes)",
})
json.dump(hb, open("fleet/machines/bm-a.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# self-verify per R170/R178/R262
chk = json.load(open("fleet/machines/bm-a.json", encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in chk["clock_read"] and " " not in chk["clock_read"], "clock_read must be T-separated ISO"
print("state round_no=370 | heartbeat epoch(int)=", chk["heartbeat_epoch_utc"], "| clock=", chk["clock_read"])
