"""r621 bm-b merge-conflict inspection: per UU file dump ours/theirs shape + ts fields."""
import json, subprocess, sys, io

sys.stdout = io.open("results/_r621bmb_merge_inspect.out", "w", encoding="utf-8")

UU = [
 "CODELY.md",
 "docs/daily_report/REPORT-2026-10-03.json",
 "docs/daily_report/REPORT-2026-10-03.md",
 "docs/live_usage/LIVE-2026-10-03.json",
 "docs/live_usage/LIVE-2026-10-03.md",
 "docs/live_usage/LIVE-latest.json",
 "docs/live_usage/LIVE-latest.md",
 "results/_attrition_guard_scan.json",
 "results/compute_audit.json",
 "results/dashboard_status.js",
 "results/dashboard_status.json",
 "results/fundamental_b_layer_filter.json",
 "results/futures_update_status.json",
 "results/lhb_update_status.json",
 "results/regime_state.json",
 "results/scorecard_v1.json",
 "results/strategy_scorecard.json",
 "results/token_usage.json",
 "results/update_status.json",
]

def blob(stage, path):
    r = subprocess.run(["git", "show", ":%d:%s" % (stage, path)], capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout

def shape(data):
    if data is None:
        return "MISSING"
    try:
        obj = json.loads(data.decode("utf-8"))
    except Exception:
        head = data[:160].decode("utf-8", "replace").replace("\n", "\\n")
        return "non-json head=%s len=%d" % (head, len(data))
    if isinstance(obj, dict):
        keys = sorted(obj.keys())
        tsf = {}
        for k in keys:
            v = obj[k]
            if isinstance(v, (str, int, float)) and any(t in k.lower() for t in ("ts", "time", "date", "generated", "updated", "asof", "cutoff")):
                tsf[k] = v
        lens = {k: len(v) for k, v in obj.items() if isinstance(v, (list, dict))}
        return "dict keys=%s ts=%s collens=%s" % (keys[:14], tsf, lens)
    return "type=%s" % type(obj).__name__

state = json.load(open("state.json", encoding="utf-8"))
print("STATE round_no=%s" % state.get("round_no"))
r = subprocess.run(["git", "log", "-1", "--oneline", "origin/main"], capture_output=True)
print("origin/main tip:", r.stdout.decode().strip())
r = subprocess.run(["git", "log", "--oneline", "origin/main..HEAD"], capture_output=True)
print("ahead commits:\n" + r.stdout.decode().strip())

for p in UU:
    o, t = blob(2, p), blob(3, p)
    print("\n== %s" % p)
    print("  OURS   : %s" % shape(o))
    print("  THEIRS : %s" % shape(t))

data = open("CODELY.md", "rb").read()
lines = data.split(b"\n")
print("\nCODELY.md total_lines=%d" % len(lines))
for i, ln in enumerate(lines):
    if ln.startswith(b"<<<<<<<") or ln.startswith(b"=======") or ln.startswith(b">>>>>>>"):
        print("  L%d: %s" % (i + 1, ln.decode("utf-8", "replace")))
