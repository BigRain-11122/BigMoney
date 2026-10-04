# -*- coding: utf-8 -*-
"""r687 bm-a S2: fleet tasks board scan (open/claimed/in_progress tickets)."""
import json, glob, io, os

rows = []
for p in glob.glob(r"fleet\tasks\*.json"):
    try:
        d = json.load(open(p, encoding="utf-8"))
    except Exception as e:
        rows.append((os.path.basename(p), "PARSE_FAIL", str(e)[:60]))
        continue
    if d.get("status") in ("open", "claimed", "in_progress", "waiting"):
        rows.append((os.path.basename(p)[:46], str(d.get("status")),
                     str(d.get("claimed_by")), str(d.get("priority"))[:8],
                     str(d.get("title"))[:60]))
rows.sort()
with io.open(r"results\_r687bma_board.txt", "w", encoding="utf-8") as f:
    for r in rows:
        f.write(" | ".join(r) + "\n")
    f.write("TOTAL %d\n" % len(rows))
print("WROTE results/_r687bma_board.txt rows=%d" % len(rows))
