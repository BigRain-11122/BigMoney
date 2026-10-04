"""r475 bm-c S3 probe: extract satengine key fields + watermark red (file-out, r446 law)."""
import datetime
import json
import os

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
OUT = os.path.join(ROOT, "results", "_r475bmc_s3probe.json")
ev = {"ts": datetime.datetime.now().isoformat(timespec="seconds")}

p1 = os.path.join(ROOT, "results", "saturation_engine_state.bm-c.json")
if os.path.exists(p1):
    with open(p1, encoding="utf-8-sig") as f:
        d = json.load(f)
    ev["satengine"] = {
        "alive": d.get("alive"),
        "verdict": d.get("verdict"),
        "burns_active": d.get("burns_active"),
        "queue_next": d.get("queue_next"),
        "last_tick": d.get("last_tick"),
        "now": d.get("now"),
        "keys": sorted(d.keys())[:20],
    }
else:
    ev["satengine"] = "FILE-MISSING"

p2 = os.path.join(ROOT, "results", "watermark_red.json")
if os.path.exists(p2):
    with open(p2, encoding="utf-8-sig") as f:
        w = json.load(f)
    ev["watermark"] = {"red": w.get("red"), "reason": w.get("reason", ""),
                       "ts": w.get("ts", w.get("generated", ""))}
else:
    ev["watermark"] = "FILE-MISSING (probe: no results/watermark_red.json; py_watermark probe runs in S6 chain)"

with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    json.dump(ev, f, ensure_ascii=False, indent=1)
print(json.dumps(ev, ensure_ascii=False, indent=1))
