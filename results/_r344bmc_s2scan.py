import json, glob, os
repo = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
# 1. watermark red flag
wm_path = os.path.join(repo, "results", "watermark_red.json")
if os.path.exists(wm_path):
    d = json.load(open(wm_path, "rb"))
    print("WM_RED:", json.dumps({k: d.get(k) for k in ("red", "reason", "ts", "verdict", "next_pick")}, ensure_ascii=False)[:400])
else:
    print("WM_RED: file absent")
# 2. ticket board status scan
rows = []
for f in sorted(glob.glob(os.path.join(repo, "fleet", "tasks", "*.json"))):
    try:
        t = json.load(open(f, "rb"))
    except Exception as e:
        rows.append((os.path.basename(f), "PARSE_ERR", str(e)[:60]))
        continue
    st = t.get("status", "?")
    if st in ("open", "claimed", "in_progress"):
        rows.append((os.path.basename(f), st, t.get("claimed_by", "")))
print("ACTIVE_TICKETS:", len(rows))
for r in rows:
    print("TICKET:", r[0], "|", r[1], "|", r[2])
# 3. post_review verdict face
pr = os.path.join(repo, "results", "post_review.jsonl")
if os.path.exists(pr):
    bad = 0; last = ""
    for line in open(pr, "rb"):
        line = line.strip()
        if not line: continue
        try:
            j = json.loads(line)
        except Exception:
            continue
        v = j.get("verdict")
        if v and v != "pass":
            bad += 1; last = json.dumps(j, ensure_ascii=False)[:200]
    print("POST_REVIEW_NONPASS:", bad, "| last:", last if bad else "-")
else:
    print("POST_REVIEW: file absent")
