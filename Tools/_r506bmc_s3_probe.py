"""r506 bm-c S3 probe: watermark verdict + fleet task board open tickets."""
import glob
import io
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.loads(io.open(os.path.join(ROOT, "results", "watermark_red.json"), encoding="utf-8").read())
print("watermark:", {k: d.get(k) for k in ("red", "reason", "next_pick", "verdict", "ts", "machine") if k in d})
rows = []
for f in glob.glob(os.path.join(ROOT, "fleet", "tasks", "*.json")):
    try:
        t = json.loads(io.open(f, encoding="utf-8").read())
        rows.append((os.path.basename(f), t.get("status"), t.get("claimed_by")))
    except Exception as e:
        rows.append((os.path.basename(f), "PARSE_ERR", str(e)[:60]))
print("tasks total:", len(rows))
print("open:", [x for x in rows if x[1] == "open"])
print("claimed_by bm-c:", [x for x in rows if x[2] == "bm-c"])
