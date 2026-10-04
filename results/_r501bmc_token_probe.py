"""r501 bm-c token-face zero-loss probe (r456 family): verify the merged
worktree token_usage.json preserves our fresh bm-c machine face vs HEAD
(ours) and MERGE_HEAD (theirs). Fail-closed: print verdict only."""
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

def face(d, name):
    if not isinstance(d, dict):
        return None
    m = d.get("machines")
    if isinstance(m, dict) and name in m:
        return m[name]
    return d.get(name)

for nm, obj in (("ours", ours), ("theirs", theirs), ("merged", wt)):
    e = face(obj, "bm-c")
    if e is None:
        print(nm, "bm-c entry: NOT-FOUND; top-keys:", sorted(obj.keys())[:10]
              if isinstance(obj, dict) else type(obj))
    else:
        keys = sorted(e.keys()) if isinstance(e, dict) else []
        tsf = {k: e[k] for k in keys
               if any(t in k.lower() for t in ("ts", "time", "updated", "last"))}
        print(nm, "bm-c entry ts-fields:", json.dumps(tsf, ensure_ascii=True)[:400],
              "| n_keys:", len(keys))

# structural: top-level key diff
ok, tk, wk = (set(ours or {})), (set(theirs or {})), (set(wt or {}))
print("top-keys ours-theirs:", sorted(ok ^ tk)[:10])
print("merged top-keys == ours∪theirs:", wk == (ok | tk))
