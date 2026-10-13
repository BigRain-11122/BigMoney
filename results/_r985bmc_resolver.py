# r985 rebase resolver: 3 shared regen faces (S6-regen conflict family, r947/r756 laws)
# attrition: newer-ts wholesale; compute_audit: latest newer-wins + history union-by-ts; token_usage: newer-generated wholesale + top-key union
import json, subprocess, os

def stage(f, s):
    out = subprocess.run(["git", "show", ":%d:%s" % (s, f)], capture_output=True)
    return json.loads(out.stdout.decode("utf-8"))

def put(f, obj):
    with open(f, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1)

# 1) attrition: newer-wins wholesale
f = "results/_attrition_guard_scan.json"
mine, theirs = stage(f, 2), stage(f, 3)
assert mine["rc"] == theirs["rc"] == "CLEAN" or mine.get("rc") == theirs.get("rc"), (mine.get("rc"), theirs.get("rc"))
win = theirs if theirs["ts"] > mine["ts"] else mine
put(f, win)
print("attrition ->", win["ts"])

# 2) compute_audit: latest newer-wins + history union-by-ts
f = "results/compute_audit.json"
mine, theirs = stage(f, 2), stage(f, 3)
lm, lt = mine["latest"], theirs["latest"]
latest = lm if str(lm.get("ts", "")) > str(lt.get("ts", "")) else lt
hist = {str(h.get("ts")): h for h in mine["history"]}
for h in theirs["history"]:
    k = str(h.get("ts"))
    if k not in hist or str(hist[k].get("ts", "")) < k:
        hist[k] = h
merged = {"latest": latest, "history": [hist[k] for k in sorted(hist)]}
put(f, merged)
print("compute_audit latest ->", latest.get("ts"), "history", len(merged["history"]))

# 3) token_usage: newer-generated side wholesale + top-level key union (older-only keys preserved)
f = "results/token_usage.json"
mine, theirs = stage(f, 2), stage(f, 3)
newer, older = (mine, theirs) if str(mine.get("generated", "")) > str(theirs.get("generated", "")) else (theirs, mine)
merged = dict(newer)
for k, v in older.items():
    if k not in merged:
        merged[k] = v
put(f, merged)
print("token_usage newer ->", newer.get("generated"), "keys union", len(merged))
