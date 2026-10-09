# r919 rebase UU resolver (r918 storm canon: append-only UNION / history-array UNION / regen+host-gated take-mine)
# In rebase: stage2=ours(origin/bm-c), stage3=theirs(mine, bm-a). take-mine = checkout --theirs.
import subprocess, json, os, sys

def stage(n, path):
    r = subprocess.run(["git", "show", ":%d:%s" % (n, path)], capture_output=True)
    return r.stdout.decode("utf-8", errors="replace")

def git(*a):
    return subprocess.run(["git"] + list(a), capture_output=True)

UU = [l.strip() for l in subprocess.run(["git", "diff", "--name-only", "--diff-filter=U"],
      capture_output=True).stdout.decode().splitlines() if l.strip()]

UNION_JSONL = {"results/x2_watch_log.jsonl"}
UNION_HIST = {"results/compute_audit.json"}
report = {"resolved": [], "union": []}

for f in UU:
    if f in UNION_JSONL:
        l2 = [x for x in stage(2, f).splitlines() if x.strip()]
        l3 = [x for x in stage(3, f).splitlines() if x.strip()]
        s2 = set(l2)
        merged = l2 + [x for x in l3 if x not in s2]
        with open(f, "w", encoding="utf-8", newline="") as fh:
            fh.write("\n".join(merged) + "\n")
        report["union"].append([f, len(l2), len(l3), len(merged)])
    elif f in UNION_HIST:
        a, b = json.loads(stage(2, f)), json.loads(stage(3, f))
        ha = a.get("history", []); hb = b.get("history", [])
        keys = {json.dumps(x, sort_keys=True, ensure_ascii=True) for x in ha}
        hist = ha + [x for x in hb if json.dumps(x, sort_keys=True, ensure_ascii=True) not in keys]
        b["history"] = hist  # take-mine top level (newest regen), union history zero-loss
        with open(f, "w", encoding="utf-8", newline="") as fh:
            json.dump(b, fh, ensure_ascii=False, indent=1)
        report["union"].append([f, len(ha), len(hb), len(hist)])
    else:
        r = git("checkout", "--theirs", f)
        if r.returncode != 0:
            print("CHECKOUT FAIL", f, r.stderr.decode()[:200]); sys.exit(1)
        report["resolved"].append(f)
    git("add", f)

# MM live-wins daemon faces: stage current disk (freshest) -- ledger already auto-merged+staged
for f in ["results/saturation_engine/face_bm-a.json",
          "results/saturation_engine/history_bm-a.jsonl",
          "results/saturation_engine/state_bm-a.json",
          "results/saturation_engine/ledger_bm-a.jsonl"]:
    if os.path.exists(f):
        git("add", f)

# post-resolution integrity: no conflict markers in any staged text face
bad = []
r = subprocess.run(["git", "diff", "--cached", "--name-only"], capture_output=True)
for f in r.stdout.decode().splitlines():
    if not f.endswith((".json", ".jsonl", ".md", ".js")):
        continue
    try:
        txt = open(f, encoding="utf-8", errors="replace").read()
    except Exception:
        continue
    if "<<<<<<< " in txt or ">>>>>>> " in txt:
        bad.append(f)
report["markers"] = bad

# W199 ledger integrity post-merge
n = 0
with open("results/saturation_engine/ledger_bm-a.jsonl", encoding="utf-8", errors="replace") as fh:
    for line in fh:
        if '"wave": 199' in line and '"face": "N1"' in line:
            n += 1
report["w199_rows"] = n

print(json.dumps(report, ensure_ascii=True, indent=1))
if bad or n != 12:
    sys.exit(2)
print("RESOLVER OK")
