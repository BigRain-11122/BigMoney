"""r501 bm-c token-face probe leg 2: byte-compare bm-c machine entry
(ours vs merged), dump entry keys + the per-key pick provenance."""
import json
import subprocess

def show(rev, path):
    r = subprocess.run(["git", "show", "%s:%s" % (rev, path)],
                       capture_output=True)
    return json.loads(r.stdout) if r.returncode == 0 else None

WT = "results/token_usage.json"
ours = show("HEAD", WT)
theirs = show("MERGE_HEAD", WT)
wt = json.load(open(WT, encoding="utf-8"))

e_o = ours["machines"]["bm-c"]
e_m = wt["machines"]["bm-c"]
e_t = theirs["machines"]["bm-c"]
print("bm-c entry keys:", sorted(e_o.keys()))
print("bm-c ours == merged:", e_o == e_m)
print("bm-c theirs == merged:", e_t == e_m)
print("bm-c ours == theirs:", e_o == e_t)
for k in sorted(e_o.keys()):
    v = e_o[k]
    print("  key=%s type=%s repr=%s" % (k, type(v).__name__, repr(v)[:150]))

# where are the ts? whole-face
def find_ts(d, path="root", depth=0):
    if depth > 3:
        return
    if isinstance(d, dict):
        for k, v in d.items():
            lk = str(k).lower()
            if isinstance(v, str) and len(v) >= 10 and (
                    "ts" in lk or "time" in lk or "updated" in lk):
                print("  ts@%s/%s = %s" % (path, k, v[:30]))
            elif isinstance(v, (dict, list)):
                find_ts(v, path + "/" + str(k), depth + 1)
    elif isinstance(d, list):
        for i, v in enumerate(d[:3]):
            find_ts(v, path + "[%d]" % i, depth + 1)

print("--- ours ts map ---")
find_ts(ours)
print("--- default key ---")
print("default:", json.dumps(ours.get("default"))[:200])
