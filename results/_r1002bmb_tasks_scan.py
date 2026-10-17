import json, glob, os
REPO = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
rows = []
for p in sorted(glob.glob(REPO + r"\fleet\tasks\*.json")):
    try:
        j = json.loads(open(p, "rb").read().decode("utf-8-sig"))
    except Exception as e:
        rows.append(("PARSE_ERR", os.path.basename(p), str(e)[:80]))
        continue
    st = j.get("status", "?")
    if st not in ("done", "failed", "closed"):
        rows.append((st, j.get("id", os.path.basename(p)), (j.get("title") or j.get("type") or "")[:80]))
print("NON_DONE_COUNT=%d" % len(rows))
for r in rows:
    print("%s | %s | %s" % r)
