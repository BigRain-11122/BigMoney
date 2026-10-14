# r1008 rebase conflict resolver: ts-newer-wins + host-law override (bm-c)
import subprocess, re, sys

GIT = r"C:\Program Files\Git\cmd\git.exe"
HOST_BM_A = {  # r378 host=bm-a single-writer faces: bm-a side wins on ties
    "results/daily_scorecard.json", "results/daily_scorecard.html",
    "results/dashboard_status.json", "results/dashboard_status.js",
}

def run(*a):
    r = subprocess.run([GIT] + list(a), capture_output=True)
    return r.stdout.decode("utf-8", errors="replace")

conflicts = [l for l in run("diff", "--name-only", "--diff-filter=U").splitlines() if l.strip()]
print("total conflicts:", len(conflicts))
for f in conflicts[40:]:
    print("REST:", f)

TS_RE = re.compile(r'"(?:ts|updated|updated_at|generated_at|asof|written_at)"\s*:\s*"([^"]+)"')

def side_blob(stage, path):
    return run("show", ":%d:%s" % (stage, path))

def side_ts(stage, path):
    blob = side_blob(stage, path)
    m = TS_RE.search(blob)
    return (m.group(1) if m else None), len(blob)

report = []
take_mine, take_theirs = [], []
for f in conflicts:
    ts_o, len_o = side_ts(2, f)   # ours = bm-a base
    ts_t, len_t = side_ts(3, f)   # theirs = my commit
    if f in HOST_BM_A:
        winner = "base"  # host law: bm-a is single writer for these faces
    elif ts_o and ts_t:
        winner = "mine" if ts_t >= ts_o else "base"
    elif ts_t and not ts_o:
        winner = "mine"
    elif ts_o and not ts_t:
        winner = "base"
    else:
        winner = "mine"  # no ts on either: my later window run (default per r948 precedent)
    if winner == "mine":
        take_mine.append(f)
    else:
        take_theirs.append(f)
    report.append("%s -> %s (base_ts=%s len=%d | mine_ts=%s len=%d)" % (f, winner, ts_o, len_o, ts_t, len_t))

for f in take_theirs:
    run("checkout", "--ours", "--", f)
    run("add", "--", f)
for f in take_mine:
    run("checkout", "--theirs", "--", f)
    run("add", "--", f)

with open(r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r1008bmc_rebase_resolve_report.txt", "w", encoding="utf-8") as fh:
    fh.write("\n".join(report) + "\n")
print("resolved: mine=%d base=%d" % (len(take_mine), len(take_theirs)))
print("RESOLVE_DONE")
