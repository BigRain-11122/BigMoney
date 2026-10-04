"""r665 merge resolver: per-face category resolution (r661/r663 precedent).
- ts-decided faces: newer in-file ts wins (JSON twin decides, md twin follows).
- union faces: compute_audit.json / token_usage.json (row/machine union).
- host=bm-a single-writer faces: ours wins (dashboard_status.*, strategy_scorecard.json,
  scorecard_v1.json, daily_scorecard faces -- D-03 batch3 C family).
"""
import json
import re
import subprocess
import sys


def sh(*args):
    return subprocess.run(args, capture_output=True, check=True).stdout


def side_ts(rev, path):
    """Extract a timestamp from one side's blob: try common ts keys, else first ISO/ts-looking token."""
    try:
        raw = sh("git", "show", f"{rev}:{path}")
    except subprocess.CalledProcessError:
        return None, None
    txt = raw.decode("utf-8", "replace")
    ts = None
    m = re.search(r'"(?:ts|generated|generated_at|asof|updated_at|last_run)"\s*:\s*"?(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})', txt)
    if m:
        ts = m.group(1)
    return (ts, txt)


TS_DECIDED = [
    "docs/daily_report/REPORT-2026-10-04.json",
    "docs/daily_report/REPORT-2026-10-04.md",
    "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/regime_state.json",
    "results/update_status.json",
    "results/lhb_update_status.json",
    "results/futures_update_status.json",
    "results/t35_open_fill_verify.json",
    "results/fundamental_b_layer_filter.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
]
UNION = [
    "results/compute_audit.json",
    "results/token_usage.json",
]
OURS_HOST = [
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/strategy_scorecard.json",
    "results/scorecard_v1.json",
]

for path in TS_DECIDED:
    o_ts, _ = side_ts("HEAD", path)
    t_ts, _ = side_ts("origin/main", path)
    if o_ts and t_ts:
        side = "ours" if o_ts >= t_ts else "theirs"
    else:
        side = "ours" if o_ts else ("theirs" if t_ts else "ours")
    print(f"{path}: ours={o_ts} theirs={t_ts} -> {side}")
    subprocess.run(["git", "checkout", f"--{side}", "--", path], check=True)
    subprocess.run(["git", "add", "--", path], check=True)

for path in OURS_HOST:
    print(f"{path}: host=bm-a single-writer -> ours")
    subprocess.run(["git", "checkout", "--ours", "--", path], check=True)
    subprocess.run(["git", "add", "--", path], check=True)

for path in UNION:
    o_raw = sh("git", "show", f"HEAD:{path}")
    t_raw = sh("git", "show", f"origin/main:{path}")
    o = json.loads(o_raw.decode("utf-8"))
    t = json.loads(t_raw.decode("utf-8"))
    if path == "results/compute_audit.json":
        # union by machine rows under "machines" (or list); keep both machines' latest rows
        merged = o
        om = o.get("machines", {})
        tm = t.get("machines", {})
        for k, v in tm.items():
            if k not in om or str(v) > str(om.get(k, "")):
                om[k] = v
        merged["machines"] = om
        merged["ts"] = max(o.get("ts", ""), t.get("ts", ""))
    else:
        # token_usage: union of per-machine blocks under "machines"/top-level keys
        merged = o
        for k, v in t.items():
            if k not in merged:
                merged[k] = v
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(merged, f, ensure_ascii=False, indent=1)
    subprocess.run(["git", "add", "--", path], check=True)
    print(f"{path}: union merged ({o.get('ts')} + {t.get('ts')})")
print("resolver done")
