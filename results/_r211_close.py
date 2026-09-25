"""R211 close: state round_no++ + heartbeat update (epoch int, clock_read)."""
import json
import time

now = time.strftime("%Y-%m-%dT%H:%M:%S")
now_disp = time.strftime("%Y-%m-%d %H:%M:%S")
epoch = int(time.time())

# --- state file: round_no +1 ---
s = json.load(open("state-bm-a.json", encoding="utf-8-sig"))
s["round_no"] = 211
s["did"] = (
    "R211 honest-idle maintenance: S6 21-leg weekend no-op family all-green "
    "(daily cutoff 09-24 next bar 09-28, regime ORANGE shadow, b_layer full-gate, "
    "paper_export idempotent equity 5,996,645); orders 74/74 both scans; smoke 25/25; "
    "post_review zero-x; cmd-parse artifact cleaned"
)
s["verdict"] = "GREEN"
s["next"] = (
    "09-28 Monday open-window new-bar full chain relay; mf/AH EM-block 30-min self-heal "
    "recheck; bm-c rebuild-or-retire ruling point 09-26 11:52 GM face; 10-01 monthly "
    "trio + REGIME_GUARD v3 date gate; T-70 midterm 10-09"
)
s["ts"] = now
s["last_round_ts"] = now
s["updated_at"] = now
s["last_round_at"] = now
s["current_task"] = "r211 done: honest-idle weekend maintenance; next: 09-28 new-bar relay, bm-c ruling 11:52"
s["last_run"] = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
json.dump(s, open("state-bm-a.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# --- heartbeat: last_seen/verdict/epoch(int)/clock_read ---
m = json.load(open("fleet/machines/bm-a.json", encoding="utf-8-sig"))
m["last_seen"] = now_disp
m["current_task"] = s["current_task"]
m["round_no"] = 211
m["verdict"] = (
    "GREEN: WM probe 03:20 py_low_board_clear legal idle (0 open/bandit 0, bars present, "
    "daily panel true; pool ready 4 all bm-b lane-pin non-local); watermark_red red=false "
    "lane healthy; smoke 25/25; orders 74/74 both scans zero diff; post_review zero-x "
    "verdict rows (REPORT-20260926); schtasks Loop Running + Watchdog Ready; heartbeat "
    "epoch int verified"
)
m["heartbeat_epoch_utc"] = epoch
m["clock_read"] = time.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
m["task"] = "weekend maintenance lane; 09-28 new-bar relay next"
json.dump(m, open("fleet/machines/bm-a.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

# --- self-verify: epoch must be JSON int ---
chk = json.load(open("fleet/machines/bm-a.json", encoding="utf-8-sig"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch not int"
print("state round_no:", s["round_no"], "| heartbeat epoch:", chk["heartbeat_epoch_utc"],
      "int-verified | clock:", chk["clock_read"])
