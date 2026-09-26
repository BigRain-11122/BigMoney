# -*- coding: utf-8 -*-
"""r302 bm-b wrap repair pass (same-round, zero-escape): _r302bmb_wrap.py v1
wrote naive-isoformat timestamps (no +08:00 offset) into state.last_round_ts/
updated_at, round-report line prefix, and heartbeat last_seen/clock_read.
Caught by the wrap script's own R262 assert on heartbeat BEFORE commit
(epoch-int face already correct). This pass rewrites the three ts faces
with astimezone() ISO-8601 offsets and re-runs all self-verification gates.
"""
import datetime as dt
import io
import json

NOW = dt.datetime.now().astimezone().isoformat(timespec="seconds")
assert "+" in NOW and "T" in NOW, NOW

# state.json: ts faces only (round_no already 302)
SP = "logs/iteration-loop/state.json"
st = json.load(io.open(SP, encoding="utf-8-sig"))
st["last_round_ts"] = NOW
st["updated_at"] = NOW
with io.open(SP, "w", encoding="utf-8", newline="") as f:
    f.write(json.dumps(st, ensure_ascii=False, indent=1))
chk = json.load(io.open(SP, encoding="utf-8-sig"))
assert chk["round_no"] == 302 and "+" in chk["last_round_ts"]
print("state.json ts repaired:", chk["last_round_ts"])

# round_reports.md: fix last line prefix ts (content unchanged)
RP = "logs/iteration-loop/round_reports.md"
raw = io.open(RP, encoding="utf-8").read()
lines = raw.split("\n")
i = len(lines) - 1
while i >= 0 and not lines[i].strip():
    i -= 1
assert "r302 bm-b" in lines[i], lines[i][:80]
old_ts = lines[i].split(" | ", 1)[0]
assert "+" not in old_ts and "r302" in lines[i], old_ts
lines[i] = NOW + " | " + lines[i].split(" | ", 1)[1]
with io.open(RP, "w", encoding="utf-8", newline="") as f:
    f.write("\n".join(lines))
back = io.open(RP, encoding="utf-8").read().split("\n")
assert back[i].startswith(NOW) and "r302 bm-b" in back[i]
print("round_reports.md line prefix repaired (was %s)" % old_ts)

# heartbeat: last_seen/clock_read tz-aware rewrite
HB = "fleet/machines/bm-b.json"
hb = json.load(io.open(HB, encoding="utf-8-sig"))
hb["last_seen"] = NOW
hb["clock_read"] = NOW
with io.open(HB, "w", encoding="utf-8", newline="") as f:
    f.write(json.dumps(hb, ensure_ascii=False, indent=1))
v = json.load(io.open(HB, encoding="utf-8-sig"))
assert isinstance(v["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170/R178)"
assert "T" in v["clock_read"] and "+" in v["clock_read"], "R262 offset law"
assert v["round_no"] == 302
print("heartbeat repaired: epoch=%d int, clock=%s" % (
    v["heartbeat_epoch_utc"], v["clock_read"]))
