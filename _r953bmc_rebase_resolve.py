# r953 conflict-marker repair (post-rebase): resolve 3 runtime JSON faces from parents
# - origin side = e202ebdf3 (parent of replayed commit 27967cfdd)
# - mine side   = 702bc6a8c (pre-rebase original r953 commit)
# - compute_audit.json: top-level = mine (bm-c 03:53 fresher), history = union-by-ts
# - other two: mine wholesale (bm-c single-state evidence)
import json, subprocess

def side(rev, path):
    r = subprocess.run(["git", "show", "%s:%s" % (rev, path)], capture_output=True)
    if r.returncode != 0 or not r.stdout:
        return None
    return json.loads(r.stdout.decode("utf-8-sig"))

ORIGIN = "27967cfdd^"   # e202ebdf3
MINE = "702bc6a8c"

for path in ["results/_attrition_guard_scan.json", "results/_r686bmb_d19_check.json"]:
    mine = side(MINE, path)
    assert mine is not None, path
    with open(path, "w", encoding="utf-8", newline="") as f:
        json.dump(mine, f, ensure_ascii=False, indent=1)
    print("REPAIRED-WHOLESALE", path)

p = "results/compute_audit.json"
ours, mine = side(ORIGIN, p), side(MINE, p)
assert ours and mine, p
merged = dict(mine)
ho = ours.get("history", [])
hm = mine.get("history", [])
idx = {}
for e in ho + hm:
    k = e.get("ts")
    if k is not None:
        idx[k] = e
merged["history"] = sorted(idx.values(), key=lambda e: e.get("ts", ""))
print("HISTORY-UNION origin=%d mine=%d merged=%d" % (len(ho), len(hm), len(merged["history"])))
with open(p, "w", encoding="utf-8", newline="") as f:
    json.dump(merged, f, ensure_ascii=False, indent=1)
print("REPAIRED-UNION", p)
