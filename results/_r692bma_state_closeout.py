"""r692 bm-a state + heartbeat closeout (programmatic write + self-proof)."""
import json
import time
from datetime import datetime, timezone, timedelta

root = "C:/Users/sjs20/Desktop/FluxGroup/quant/bigmoney"

# --- state-bm-a.json: round_no 691 -> 692 ---
sp = f"{root}/state-bm-a.json"
st = json.load(open(sp, encoding="utf-8"))
assert st["round_no"] == 691, f"unexpected round_no {st['round_no']}"
st["round_no"] = 692
st["last_round"] = "r692"
st["last_round_at"] = datetime.now(timezone(timedelta(hours=8))).strftime(
    "%Y-%m-%dT%H:%M:%S+08:00")
st["last_round_ts"] = st["last_round_at"]
st["current_task"] = ("N2-W15 slice-2 build landed (Plan A adoption per "
                      "MSG-1845); W3 judge verdict watch (bm-c ~22:1x)")
st["last_action"] = ("r692: N2 slice-2 five legs + selftest 17/17 + "
                     "real-panel smoke; freeze-gated R99/R250")
st["updated"] = st["last_round_at"]
with open(sp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
chk = json.load(open(sp, encoding="utf-8"))
assert chk["round_no"] == 692, "round_no write failed"
print("state ok: round_no=692, reparse PASS")

# --- heartbeat fleet/machines/bm-a.json ---
hp = f"{root}/fleet/machines/bm-a.json"
h = json.load(open(hp, encoding="utf-8"))
epoch = int(time.time())
clock = datetime.now(timezone(timedelta(hours=8))).strftime(
    "%Y-%m-%dT%H:%M:%S+08:00")
h["last_seen"] = clock
h["heartbeat_epoch_utc"] = epoch
h["clock_read"] = clock
h["current_task"] = ("N2-W15 slice-2 landed; bm-b review window; W3 "
                      "judge verdict watch (bm-c ~22:1x); trio finalize "
                      "10-05..09")
h["verdict"] = ("slice-2 build delivered r692; satengine alive; "
                "watermark green; S6 34/34 rc0")
h["round_no"] = 692
with open(hp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(h, f, ensure_ascii=False, indent=1)
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch not int"
assert "T" in chk["clock_read"] and "+08:00" in chk["clock_read"], \
    "clock not T-format"
print(f"heartbeat ok: epoch={chk['heartbeat_epoch_utc']} (int) "
      f"clock={chk['clock_read']}")
