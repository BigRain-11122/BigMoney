# -*- coding: utf-8 -*-
# r920 W219 burn-window poller: watch results/p2cal_ext/n1_w219 shard growth
# (r325 law: product-growth face = the only ignition/completion evidence).
import json, os, time, sys
sys.stdout.reconfigure(encoding="utf-8")
REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
d = os.path.join(REPO, "results", "p2cal_ext", "n1_w219")
for attempt in range(60):
    files = set(os.listdir(d)) if os.path.isdir(d) else set()
    done = len([f for f in files if f.startswith("shard-") and f.endswith(".json")])
    try:
        s = json.load(open(os.path.join(REPO, "results", "saturation_engine_state.bm-c.json"), encoding="utf-8"))
        burns = len(s.get("burns_active") or [])
    except Exception:
        burns = -1
    print(f"poll {attempt}: shards={done}/12 burns_active={burns} ts={time.strftime('%H:%M:%S')}", flush=True)
    if done >= 12:
        print("BURN COMPLETE 12/12")
        break
    time.sleep(20)
else:
    print("TIMEOUT: 12/12 not reached in 20min -- investigate")
