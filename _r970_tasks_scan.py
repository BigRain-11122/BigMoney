import json, glob, os

rows = []
for p in sorted(glob.glob(r"fleet\tasks\*.json")):
    try:
        d = json.load(open(p, encoding="utf-8"))
    except Exception as e:
        rows.append((os.path.basename(p), "PARSE_ERR", str(e)[:40])); continue
    st = d.get("status", "?")
    if st in ("open", "claimed", "in_progress"):
        rows.append((os.path.basename(p), st, (d.get("claimed_by") or "-"), (d.get("title") or d.get("subject") or "")[:60]))
for r in rows:
    print(" | ".join(str(x) for x in r))
print("total open/claimed/in_progress:", len(rows))
