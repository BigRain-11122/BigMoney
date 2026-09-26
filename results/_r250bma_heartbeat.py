# -*- coding: utf-8 -*-
"""_r250bma_heartbeat.py -- S7 heartbeat update for bm-a (epoch MUST be JSON int, R170/R178 law)."""
import json
import time
import datetime

p = "fleet/machines/bm-a.json"
d = json.load(open(p, encoding="utf-8"))
now = datetime.datetime.now()
epoch = int(time.time())

d["machine_id"] = "bm-a"
d["last_seen"] = now.strftime("%Y-%m-%d %H:%M")
d["current_task"] = ("R250 done: T-73 s3 slice-2 CN-DIV-LOWVOL-ROT prereg frozen+pushed "
                      "(commit 83ecffbb; 4 cells; seed 20260980 registered at freeze); P0 same-round "
                      "T80 battery lane unblocked (canon deep assembled 9036x2 PASS + t54 dA re-run "
                      "16588 cells, full census 121528 PASS); next=14:30 tick launch verify + harvest "
                      "per r244; runner slice cn_div_lowvol_rot_p1.py next round")
d["cpu_cores"] = 32
d["cpu_pct"] = 31.0
d["free_ram_gb"] = 58.9
d["gpu_free_vram_gb"] = 5.9
d["verdict"] = "alive"
d["heartbeat_epoch_utc"] = epoch  # python int -> JSON int (smoke F7 law)
d["clock_read"] = now.isoformat(timespec="seconds") + "+08:00"
d["round_no"] = 250
d["task"] = d["current_task"]

json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# self-verify: epoch must be int after round-trip
chk = json.load(open(p, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch not int"
print("heartbeat updated, epoch=", chk["heartbeat_epoch_utc"], "type=", type(chk["heartbeat_epoch_utc"]).__name__)
