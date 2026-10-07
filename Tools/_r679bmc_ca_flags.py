# -*- coding: utf-8 -*-
# r679 bm-c: compute_audit flag extractor (log line JSON parse, no regex)
import json

path = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r679bmc_s6_log.txt"
lines = open(path, encoding="utf-8").read().splitlines()
for ln in lines:
    if ln.startswith('{"ts": "2026-10-07 13:47:28"'):
        d = json.loads(ln)
        print("flags =", d.get("flags"))
        print("load_state =", d.get("load_state"))
        print("pool_ready_count =", d.get("pool_ready_count"),
              "unclaimed =", d.get("pool_ready_unclaimed"))
        print("supply_floor =", d.get("supply_floor"))
        print("stale_min =", d.get("result_stale_min"))
        break
