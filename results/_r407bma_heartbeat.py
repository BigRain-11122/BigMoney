# -*- coding: utf-8 -*-
"""r407 bm-a heartbeat update + epoch-int self-verify (R170/R178 law)."""
import io, json, time
from datetime import datetime

p = "fleet/machines/bm-a.json"
d = json.load(io.open(p, encoding="utf-8"))

epoch = int(time.time())
clock = datetime.now().astimezone().isoformat(timespec="seconds")

d["machine_id"] = "bm-a"
d["last_seen"] = clock
d["current_task"] = "r407 closed: T-115 pool_worker claims-face origin read landed + W5 generate fix-first (double face bug) landed + autofill relaunch burning; watch W5-SCREEN entry next"
d["cpu_cores"] = 32
d["task"] = "round-closed"
d["verdict"] = ("r407: T-115 done (e3622792, selftest 25/25, live-fire GRID=occupied-closed) "
                "+ W5 generate fix-first (777e2b5e, selftest 73/73, gate anchors exact) "
                "+ autofill 01:50 relaunch alive + S6 36/36 rc=0")
d["heartbeat_epoch_utc"] = epoch
d["clock_read"] = clock
d["round_no"] = 407
d["round"] = 407
d["loop_round"] = 407
d["cores"] = 32

with io.open(p, "w", encoding="utf-8", newline="") as f:
    json.dump(d, f, ensure_ascii=False, indent=1)

# self-verify (smoke F7 face)
chk = json.load(io.open(p, encoding="utf-8"))
e = chk.get("heartbeat_epoch_utc")
c = chk.get("clock_read")
assert isinstance(e, int) and not isinstance(e, bool), f"epoch not int: {type(e)}"
assert "T" in c and ("+" in c or "-" in c.split("T")[1]), f"clock not T-sep ISO: {c}"
print("heartbeat OK: epoch=", e, "int; clock=", c)
