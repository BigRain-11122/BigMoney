"""r688 bm-a S2: fleet task board scan -- open/claimed tickets."""
import json
import os

d = r"fleet\tasks"
rows = []
for f in sorted(os.listdir(d)):
    if not f.endswith(".json"):
        continue
    p = os.path.join(d, f)
    try:
        t = json.load(open(p, encoding="utf-8-sig"))
    except Exception as e:
        rows.append((f, "PARSE-ERR", str(e)[:60]))
        continue
    rows.append((f, t.get("status", "?"), t.get("claimed_by", "-"), (t.get("title") or t.get("subject") or "")[:70]))

open_rows = [r for r in rows if r[1] == "open"]
claimed_by_me = [r for r in rows if r[1] == "claimed" and r[2] == "bm-a"]
in_prog = [r for r in rows if r[1] == "in_progress"]
print("total:", len(rows), "open:", len(open_rows), "in_progress:", len(in_prog), "claimed-by-bm-a:", len(claimed_by_me))
for r in open_rows:
    print("OPEN:", r[0], "|", r[3])
for r in claimed_by_me:
    print("MINE:", r[0], "|", r[3])
# w3 judge tickets status
for r in rows:
    if "W3" in r[0] or "w3" in r[0]:
        print("W3:", r[0], r[1], r[2])
