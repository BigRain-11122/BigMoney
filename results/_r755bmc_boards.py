# -*- coding: utf-8 -*-
"""r755 bm-c board probe: fleet/tasks non-done ticket scan + watermark_red
face read. Compact stdout receipt, no files written."""
import glob
import json
import os

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
tasks = []
for f in sorted(glob.glob(os.path.join(ROOT, "fleet", "tasks", "*.json"))):
    try:
        d = json.load(open(f, encoding="utf-8"))
    except Exception as e:
        tasks.append({"file": os.path.basename(f), "err": str(e)[:100]})
        continue
    st = d.get("status", "?")
    if st in ("open", "claimed", "in_progress"):
        tasks.append({"file": os.path.basename(f), "status": st,
                      "claimed_by": d.get("claimed_by", ""),
                      "subject": str(d.get("subject", d.get("title", "")))[:90]})
print("nondone_tasks=%d" % len(tasks))
for t in tasks:
    print(json.dumps(t, ensure_ascii=False))

wr = os.path.join(ROOT, "results", "watermark_red.json")
if os.path.exists(wr):
    print("watermark_red:", open(wr, encoding="utf-8").read()[:400])
else:
    print("watermark_red: ABSENT")
