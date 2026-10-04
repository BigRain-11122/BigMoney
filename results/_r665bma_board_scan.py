"""r665 ticket board scan: status + immediate + title for all fleet/tasks/*.json."""
import json, glob, io

rows = []
for p in sorted(glob.glob(r"fleet\tasks\*.json")):
    try:
        with io.open(p, "r", encoding="utf-8") as f:
            t = json.load(f)
    except Exception as e:
        rows.append((p, "PARSE-FAIL", "", str(e)[:60]))
        continue
    st = t.get("status", "?")
    if st in ("open", "claimed", "in_progress"):
        rows.append((t.get("id", "?"), st, "IMM" if t.get("immediate") else "", (t.get("title") or t.get("type") or "")[:70]))

for r in rows:
    print(" | ".join(str(x) for x in r))
print("total_open_or_claimed:", len(rows))
