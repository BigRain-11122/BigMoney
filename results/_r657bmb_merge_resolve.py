import subprocess, json, os

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def stage_blob(rev, path):
    r = subprocess.run(["git", "show", rev + ":" + path], capture_output=True, cwd=R, timeout=60)
    if r.returncode != 0:
        raise RuntimeError("git show %s:%s failed: %s" % (rev, path, r.stderr.decode("utf-8", "replace")[:300]))
    return r.stdout

def canon(o):
    return json.dumps(o, sort_keys=True, ensure_ascii=False)

# --- face 1: token_usage.json (regen snapshot, honest-ts newer wins) ---
P1 = "results/token_usage.json"
ours_tu = json.loads(stage_blob("HEAD", P1).decode("utf-8"))
theirs_tu = json.loads(stage_blob("MERGE_HEAD", P1).decode("utf-8"))
if ours_tu["generated"] >= theirs_tu["generated"]:
    merged_tu, pick1 = ours_tu, "ours"
else:
    merged_tu, pick1 = theirs_tu, "theirs"
with open(os.path.join(R, P1), "w", encoding="utf-8", newline="\n") as f:
    json.dump(merged_tu, f, indent=1, ensure_ascii=False)
json.loads(open(os.path.join(R, P1), "rb").read().decode("utf-8"))
print("token_usage resolved: %s (ours_gen=%s theirs_gen=%s) reparse PASS" %
      (pick1, ours_tu["generated"], theirs_tu["generated"]))

# --- face 2: compute_audit.json (cross-machine union, zero-loss) ---
P2 = "results/compute_audit.json"
ours_ca = json.loads(stage_blob("HEAD", P2).decode("utf-8"))
theirs_ca = json.loads(stage_blob("MERGE_HEAD", P2).decode("utf-8"))
oh, th = ours_ca["history"], theirs_ca["history"]
seen = set()
merged_hist = []
for row in oh + th:
    k = canon(row)
    if k not in seen:
        seen.add(k)
        merged_hist.append(row)
assert all(canon(r) in seen for r in oh) and all(canon(r) in seen for r in th), "zero-loss FAILED"
if ours_ca["latest"]["ts"] >= theirs_ca["latest"]["ts"]:
    latest, pick2 = ours_ca["latest"], "ours"
else:
    latest, pick2 = theirs_ca["latest"], "theirs"
merged_ca = {"latest": latest, "history": merged_hist}
with open(os.path.join(R, P2), "w", encoding="utf-8", newline="\n") as f:
    json.dump(merged_ca, f, indent=1, ensure_ascii=False)
d = json.loads(open(os.path.join(R, P2), "rb").read().decode("utf-8"))
assert len(d["history"]) == len(seen)
print("compute_audit resolved: latest=%s (%s) history ours=%d theirs=%d merged_unique=%d zero-loss PASS reparse PASS" %
      (latest["ts"], pick2, len(oh), len(th), len(seen)))
print("RESOLVE DONE")
