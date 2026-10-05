# r762 rebase UU batch: probe both stages' internal ts fields for UNKNOWN-class files
# fail-closed manual classification helper (skill: bigmoney-conflict-resolve)
import subprocess, json, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

UNKNOWN = [
    "docs/daily_report/REPORT-2026-10-06.json",
    "docs/daily_report/REPORT-2026-10-06.md",
    "docs/live_usage/LIVE-2026-10-06.json",
    "docs/live_usage/LIVE-2026-10-06.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/p1d_gates.json",
    "results/saturation_engine/face_bm-b.json",
    "results/saturation_engine/state_bm-b.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
]

TS_KEYS = ["generated", "generated_at", "ts", "updated", "asof", "as_of", "scan_ts",
           "last_scan", "run_ts", "cutoff", "evidence_cutoff", "epoch", "elapsed",
           "generated_utc", "now", "tick_ts", "last_tick_ts", "scan_at"]

def stage_bytes(path, stage):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    return r.stdout if r.returncode == 0 else None

def find_ts(obj, depth=0):
    """recursively find first ts-like key in dict, return (key, val)"""
    if depth > 3 or not isinstance(obj, dict):
        return None
    for k in TS_KEYS:
        if k in obj:
            return (k, obj[k])
    for v in obj.values():
        if isinstance(v, dict):
            got = find_ts(v, depth + 1)
            if got:
                return got
    return None

for path in UNKNOWN:
    raw2 = stage_bytes(path, 2)  # ours
    raw3 = stage_bytes(path, 3)  # theirs
    print("=" * 8, path)
    for stage, raw in (("ours", raw2), ("theirs", raw3)):
        if raw is None:
            print(f"  {stage}: <absent>")
            continue
        if path.endswith(".json"):
            try:
                obj = json.loads(raw)
                got = find_ts(obj)
                print(f"  {stage}: ts={got}")
            except Exception as e:
                print(f"  {stage}: PARSE-FAIL {e}; head={raw[:80]!r}")
        else:
            # md: first 3 lines
            head = raw[:200].decode("utf-8", "replace")
            print(f"  {stage}: md head={head!r}")
