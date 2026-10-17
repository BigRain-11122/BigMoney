# -*- coding: utf-8 -*-
"""r1041 bm-a closeout: state round_no advance + heartbeat write (R170/R178 epoch int law, T-04 clock law)."""
import datetime
import json
import time

now = datetime.datetime.now().astimezone()
iso = now.isoformat(timespec="seconds")  # T separator, +08:00 offset
epoch = int(time.time())

# state: round_no advance + honest D-19 descriptive fields (shas untouched -- tool-owned)
sp = "state-bm-a.json"
s = json.load(open(sp, encoding="utf-8"))
prev = s.get("round_no", 0)
s["round_no"] = 1041
s["last_decisions_seen"] = "r1041: dec 1d4741e4 hold (identical to watermark, d19 probe NOOP)"
s["last_orders_seen"] = ("r1041: ORD e0dcbd80 hold (d19 probe NOOP zero delta; "
                         "zero BigMoney rows; dec 1d4741e4 hold)")
s["last_decisions_read_at"] = iso
s["last_orders_read_at"] = iso
json.dump(s, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# heartbeat
hp = "fleet/machines/bm-a.json"
h = json.load(open(hp, encoding="utf-8"))
h["last_seen"] = iso
h["current_task"] = ("r1041 waits-upstream closeout: W264 seat published (bm-c own-wave, prereg derive = "
                     "bm-c r1076 first action); bm-a N1 engine alive queue_depth=0 awaiting W264 freeze; "
                     "S6 43/43 rc0; CEO gaming window CPU-only standing")
h["cpu_cores"] = 32
h["free_ram_pct"] = 25.5
h["gpu_free_vram_mb"] = 722
h["gpu_total_vram_mb"] = 12282
h["verdict"] = "GREEN"
h["idle_rounds"] = 0
h["agenda_starved"] = False
h["heartbeat_epoch_utc"] = epoch
h["clock_read"] = iso
h["ts"] = iso
h["orders_ack"] = ["O-20261017-0131-bm-c.md"]
json.dump(h, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# self-verify (R170/R178 + T-04 laws)
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in chk["clock_read"] and "+" in chk["clock_read"], "clock_read must be ISO T-sep with offset"
assert abs(chk["heartbeat_epoch_utc"] - int(time.time())) < 120, "epoch freshness"
s2 = json.load(open(sp, encoding="utf-8"))
assert s2["round_no"] == 1041
print("state round_no %d->%d; heartbeat epoch=%d clock=%s rc0" % (prev, s2["round_no"], chk["heartbeat_epoch_utc"], chk["clock_read"]))
