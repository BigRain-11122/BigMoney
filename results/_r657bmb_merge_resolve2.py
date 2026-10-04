import subprocess, json, os

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = "docs/daily_report/REPORT-2026-10-04.json"

def show(rev, path):
    r = subprocess.run(["git", "show", rev + ":" + path], capture_output=True, cwd=R, timeout=60)
    if r.returncode != 0:
        raise RuntimeError("git show %s:%s failed: %s" % (rev, path, r.stderr.decode("utf-8", "replace")[:300]))
    return r.stdout

def tskey(d):
    for k in ("generated", "ts", "updated", "updated_at", "generated_at", "as_of"):
        if k in d:
            return k, str(d[k])
    return None, ""

ours = json.loads(show("HEAD", P).decode("utf-8"))
theirs = json.loads(show("MERGE_HEAD", P).decode("utf-8"))
k, o = tskey(ours)
_, t = tskey(theirs)
print("ts_field=%s ours=%s theirs=%s" % (k, o, t))
merged = ours if (o and (not t or o >= t)) else theirs
with open(os.path.join(R, P), "w", encoding="utf-8", newline="\n") as f:
    json.dump(merged, f, indent=1, ensure_ascii=False)
json.loads(open(os.path.join(R, P), "rb").read().decode("utf-8"))
print("REPORT resolved pick=%s reparse PASS" % ("ours" if merged is ours else "theirs"))
print("RESOLVE DONE")
