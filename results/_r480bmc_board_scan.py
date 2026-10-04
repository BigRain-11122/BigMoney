"""r480 bm-c S2: fleet task board scan (open/claimed tickets)."""
import json
import glob
import os

open_t = []
claimed = []
for f in glob.glob("fleet/tasks/*.json"):
    try:
        d = json.load(open(f, encoding="utf-8"))
    except Exception as e:
        print("PARSE_FAIL", f, e)
        continue
    st = d.get("status", "")
    tid = d.get("id") or os.path.basename(f)
    label = d.get("title") or d.get("subject") or ""
    who = d.get("claimed_by")
    if st == "open":
        open_t.append((tid, label))
    elif st in ("claimed", "in_progress"):
        claimed.append((tid, st, who, label))

print("OPEN", open_t)
print("ACTIVE", claimed)
