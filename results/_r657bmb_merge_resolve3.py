import subprocess, json, os

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FACES = [
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]

def show(rev, path):
    r = subprocess.run(["git", "show", rev + ":" + path], capture_output=True, cwd=R, timeout=60)
    if r.returncode != 0:
        raise RuntimeError("git show %s:%s failed: %s" % (rev, path, r.stderr.decode("utf-8", "replace")[:300]))
    return r.stdout

def tskey(d):
    for k in ("generated", "ts", "updated", "updated_at", "generated_at", "as_of"):
        if k in d:
            return str(d[k])
    return ""

for P in FACES:
    ours = json.loads(show("HEAD", P).decode("utf-8"))
    theirs = json.loads(show("MERGE_HEAD", P).decode("utf-8"))
    o, t = tskey(ours), tskey(theirs)
    if o and (not t or o >= t):
        merged, pick = ours, "ours"
    else:
        merged, pick = theirs, "theirs"
    with open(os.path.join(R, P), "w", encoding="utf-8", newline="\n") as f:
        json.dump(merged, f, indent=1, ensure_ascii=False)
    json.loads(open(os.path.join(R, P), "rb").read().decode("utf-8"))
    print("%s resolved pick=%s (ours_ts=%s theirs_ts=%s) reparse PASS" % (P, pick, o or "?", t or "?"))
print("RESOLVE DONE")
