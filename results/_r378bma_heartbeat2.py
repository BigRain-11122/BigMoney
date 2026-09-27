# -*- coding: utf-8 -*-
"""r378 final heartbeat refresh (post-addendum)."""
import datetime as dt
import json
import time

f = "fleet/machines/bm-a.json"
j = json.load(open(f, encoding="utf-8-sig"))
now = dt.datetime.now().astimezone()
j["last_seen"] = now.isoformat(timespec="seconds")
j["clock_read"] = now.isoformat(timespec="seconds")
j["heartbeat_epoch_utc"] = int(time.time())
j["current_task"] = ("r378 done+addendum: D-03(1) batch-3 C-family slice-1 single-writer "
                     "guards (6 faces) + obs-window catches #4 (pool defer marker law + "
                     "runnable_pool mirror family) AND #5 (update_heat full host-guard, "
                     "non-host zero-write zero-fetch) landed same round; push-storm 16-UU "
                     "vs bmc r130 canon-resolved (resolve x8 + staged-blob take-new x8); "
                     "pushed e9baa08c + 07205aa5")
j["verdict"] = ("py_low_board_clear legal-idle round-closed (reconcile 14/14 zero-drift; "
                "next = batch-3 slice-2 paper family + TODAY 15:30 first bar -> T-91 s3 "
                "first-marks auto-fire + W2B finalize watch -> V2-P1 un-defer RAM window)")
json.dump(j, open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
k = json.load(open(f, encoding="utf-8-sig"))
ok = isinstance(k["heartbeat_epoch_utc"], int) and "T" in k["clock_read"]
print("epoch int ok=", ok, "| clock=", k["clock_read"], "| round=", k["round_no"])
assert ok
