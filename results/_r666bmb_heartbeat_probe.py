# -*- coding: utf-8 -*-
# r666 bm-b fleet heartbeat probe: staleness of three machines
import json, time, io

now = int(time.time())
out = {"probe": "r666bmb_heartbeat", "now_epoch": now, "machines": {}}
for mid in ("bm-a", "bm-b", "bm-c"):
    try:
        d = json.load(io.open(r"fleet\machines\%s.json" % mid, encoding="utf-8"))
        ep = d.get("heartbeat_epoch_utc")
        age = (now - ep) / 60.0 if isinstance(ep, int) else None
        out["machines"][mid] = {
            "epoch": ep, "age_min": round(age, 1) if age is not None else None,
            "verdict": d.get("verdict"), "task": (d.get("current_task") or "")[:80],
            "clock_read": d.get("clock_read"),
        }
    except Exception as e:
        out["machines"][mid] = {"error": str(e)[:150]}
with io.open(r"results\_r666bmb_heartbeat_probe.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print(json.dumps(out["machines"], ensure_ascii=False)[:500])
