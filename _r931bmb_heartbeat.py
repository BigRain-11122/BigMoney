# -*- coding: utf-8 -*-
# _r931bmb_heartbeat.py -- r931 bm-b heartbeat: fleet/machines/bm-b.json
# R170/R178 law: heartbeat_epoch_utc must be JSON int (python int(time.time())).
# R262 law: clock_read ISO8601 T-separated with UTC offset.
import json
import time
import datetime

P = r"C:\Fluxgroup\FluxGroup\quant\bigmoney\fleet\machines\bm-b.json"
NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())  # int, not str

d = json.load(open(P, encoding="utf-8"))
d["last_seen"] = NOW
d["ts"] = NOW
d["clock_read"] = NOW
d["heartbeat_epoch_utc"] = EPOCH
d["cpu_cores"] = 16
d["current_task"] = ("r932: W19 JUDGE burn watch -> judge-finalize -> "
                     "s4 intake")
d["verdict"] = ("GREEN: W19 screen-finalize + judge-prep landed, JUDGE "
                "enrolled+ignited (push e7b6bed96 origin-verified); smoke "
                "49/49; flags = supply_gap/supply_floor structural + GPU "
                "PSU-deferred (MODE=pause)")
d["idle_rounds"] = 0
d["agenda_starved"] = False

json.dump(d, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
# post-write self-proof: epoch must be int
chk = json.load(open(P, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch not int"
print("heartbeat written:", NOW, "epoch:", EPOCH, "int-ok")
