# r701 probe: ts reachability for regen faces (pre-resolver sanity)
import subprocess, json
TS_KEYS = ("generated", "generated_at", "written_at", "updated_at", "updated",
           "last_run", "asof", "ts", "written", "date", "last_refusal_ts",
           "last_crash_ts", "last_seen", "scanned_at")


def pick_ts(obj, depth=0):
    best = ""
    if isinstance(obj, dict):
        for k, v in obj.items():
            lk = str(k).lower()
            if any(t in lk for t in TS_KEYS) and isinstance(v, str) and len(v) >= 10:
                n = v.strip().replace("T", " ")[:19]
                if n > best:
                    best = n
            elif depth < 1 and isinstance(v, (dict, list)):
                sub = pick_ts(v, depth + 1)
                if sub > best:
                    best = sub
    elif isinstance(obj, list) and depth < 1:
        for v in obj:
            sub = pick_ts(v, depth + 1)
            if sub > best:
                best = sub
    return best


FACES = [
    "results/_attrition_guard_scan.json",
    "results/daily_scorecard.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/update_status.json",
    "results/dashboard_status.json",
    "docs/daily_report/REPORT-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-latest.json",
]

for p in FACES:
    o = json.loads(subprocess.run(["git", "show", "HEAD:" + p],
                                  capture_output=True).stdout)
    t = json.loads(subprocess.run(["git", "show", "MERGE_HEAD:" + p],
                                  capture_output=True).stdout)
    no, nt = pick_ts(o), pick_ts(t)
    pick = "ours" if no > nt else ("theirs" if nt > no else "TIE(no-ts?)")
    print(p, "| ours", repr(no), "theirs", repr(nt), "->", pick)
