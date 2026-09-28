import json, glob, os
rows = []
for f in sorted(glob.glob("fleet/tasks/*.json")):
    try:
        d = json.load(open(f, encoding="utf-8"))
    except Exception as e:
        rows.append((f, "PARSE_FAIL", str(e)))
        continue
    st = d.get("status")
    if st in ("open", "claimed", "in_progress"):
        rows.append((f, st, d.get("claimed_by"), d.get("id"), d.get("title", "")[:80]))
for r in rows:
    print(" | ".join(str(x) for x in r))
print("TOTAL_OPEN_CLAIMED=", len(rows))
