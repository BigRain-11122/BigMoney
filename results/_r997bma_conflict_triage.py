"""r997 rebase conflict triage: compare base(ours=bm-c) vs replayed(theirs=mine)
versions of the 15 UU runtime faces. Print freshness-relevant fields."""
import subprocess, json, io

GIT = r"C:\Program Files\Git\cmd\git.exe"
FILES = [
    "docs/daily_report/REPORT-2026-10-14.json",
    "docs/daily_report/REPORT-2026-10-14.md",
    "docs/live_usage/LIVE-2026-10-14.json",
    "docs/live_usage/LIVE-2026-10-14.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/_r686bmb_d19_check.json",
    "results/compute_audit.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/token_usage.json",
    "results/update_status.json",
]

def side(fname, which):
    r = subprocess.run([GIT, "show", ":%s:%s" % (which, fname)], capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout.decode("utf-8", "replace")

def field(text, keys):
    out = {}
    if not text:
        return out
    try:
        d = json.loads(text)
        for k in keys:
            if k in d:
                out[k] = str(d[k])[:60]
    except Exception:
        # md: first ts-like line
        for line in text.splitlines()[:12]:
            if "2026-10-14" in line and ("：" in line or ":" in line):
                out["head"] = line.strip()[:80]
                break
    return out

out = io.open(r"results/_r997bma_conflict_triage.txt", "w", encoding="utf-8")
for f in FILES:
    a = side(f, "1")  # ours = bm-c base
    b = side(f, "2")  # theirs = my replay
    keys = ("updated", "ts", "asof", "data_cutoff", "generated", "run_at", "machine")
    out.write("== %s ==\n  BASE(bm-c): %s\n  MINE(r997): %s\n" % (f, field(a, keys) or ("len=%d" % len(a or "")), field(b, keys) or ("len=%d" % len(b or ""))))
out.close()
print(io.open(r"results/_r997bma_conflict_triage.txt", encoding="utf-8").read())
