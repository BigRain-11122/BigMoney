"""r448 bm-c S2: fleet/tasks board scan -- open/claimed ticket inventory."""
import glob
import json
import os

RB = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
rows = []
for p in sorted(glob.glob(os.path.join(RB, "fleet", "tasks", "*.json"))):
    try:
        d = json.loads(open(p, "rb").read().decode("utf-8"))
    except Exception as e:
        rows.append((os.path.basename(p), "PARSE-FAIL", str(e)[:60], ""))
        continue
    status = d.get("status", "?")
    if status in ("open", "claimed", "in_progress"):
        rows.append((os.path.basename(p), status, d.get("claimed_by", ""),
                     (d.get("title") or d.get("subject") or "")[:100]))
print("BOARD n=%d" % len(rows))
for name, status, owner, title in rows:
    print("%s | %s | owner=%s | %s" % (name, status, owner, title))
