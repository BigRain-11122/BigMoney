# -*- coding: utf-8 -*-
"""r1202 bm-c closeout: state round_no + heartbeat (int epoch / ISO clock / ts)."""
import io
import json
import time
from datetime import datetime, timedelta, timezone

NOW = datetime.now(timezone.utc)
LOCAL = NOW.astimezone(timezone(timedelta(hours=8)))

st_path = "state-bm-c.json"
st = json.load(io.open(st_path, encoding="utf-8"))
prev = st.get("round_no")
st["round_no"] = int(prev) + 1
assert st["round_no"] == 1202, "round_no drift: %r -> %r" % (prev, st["round_no"])
io.open(st_path, "w", encoding="utf-8", newline="\n").write(
    json.dumps(st, ensure_ascii=False, indent=1))

hb_path = "fleet/machines/bm-c.json"
hb = json.load(io.open(hb_path, encoding="utf-8"))
hb["round_no"] = st["round_no"]
hb["last_seen"] = LOCAL.strftime("%Y-%m-%dT%H:%M:%S+08:00")
hb["ts"] = hb["last_seen"]
hb["clock_read"] = hb["last_seen"]
hb["heartbeat_epoch_utc"] = int(time.time())
hb["current_task"] = "W312 five-face splice landed (A 701_701..703_700 / B 703_701..703_900); engine self-burn in flight; S6 39-leg chain running headless"
hb["verdict"] = "active"
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
io.open(hb_path, "w", encoding="utf-8", newline="\n").write(
    json.dumps(hb, ensure_ascii=False, indent=1))
chk = json.load(io.open(hb_path, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
print("state round_no=%d heartbeat=%s epoch=%d" % (chk["round_no"], chk["clock_read"], chk["heartbeat_epoch_utc"]))