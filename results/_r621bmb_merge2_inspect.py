"""r621 bm-b merge-2 inspection: ours/theirs ts for the 18 UU + CODELY.md marker check + MERGE_HEAD."""
import json, subprocess, sys, io

sys.stdout = io.open("results/_r621bmb_merge2_inspect.out", "w", encoding="utf-8")

UU = [
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

mh = open(".git/MERGE_HEAD", "r").read().strip()
print("MERGE_HEAD =", mh)
r = subprocess.run(["git", "log", "-1", "--oneline", mh], capture_output=True)
print("MERGE_HEAD commit:", r.stdout.decode("utf-8", "replace").strip())

raw = open("CODELY.md", "rb").read()
print("CODELY.md markers:", raw.count(b"<<<<<<<"), raw.count(b">>>>>>>"), "bytes=%d" % len(raw))

def blob(stage, path):
    r = subprocess.run(["git", "show", ":%d:%s" % (stage, path)], capture_output=True)
    return r.stdout if r.returncode == 0 else None

def shape(data):
    if not data:
        return "MISSING/EMPTY"
    try:
        obj = json.loads(data.decode("utf-8"))
    except Exception:
        for k in ("generated_at", "generated", "ts", "updated"):
            idx = data.find(k.encode())
            if idx >= 0:
                seg = data[idx:idx+60].decode("utf-8", "replace").replace("\n", " ")
                return "non-json %s... len=%d" % (seg, len(data))
        return "non-json len=%d" % len(data)
    if isinstance(obj, dict):
        tsf = {}
        for k, v in sorted(obj.items()):
            if isinstance(v, (str, int, float)) and any(t in k.lower() for t in ("ts", "generated", "updated", "asof", "cutoff")):
                tsf[k] = v
        lens = {k: len(v) for k, v in obj.items() if isinstance(v, (list, dict))}
        return "dict ts=%s collens=%s" % (tsf, lens)

for p in UU:
    print("\n== %s\n  OURS   : %s\n  THEIRS : %s" % (p, shape(blob(2, p)), shape(blob(3, p))))
