# -*- coding: utf-8 -*-
"""r821 bm-a rebase resolver: remaining UU twin/snapshot faces (post
merge_lane_views 6-ALL_FACES batch). Whole-side byte writes by deep-ts probe
(max ISO-like timestamp per side wins; r819/r788 precedent family).
Exit 0 = all resolved + staged; non-zero = bail for manual adjudication."""
import re
import subprocess
import sys

FILES = [
    "docs/daily_report/REPORT-2026-10-07.json",
    "docs/daily_report/REPORT-2026-10-07.md",
    "docs/live_usage/LIVE-2026-10-07.json",
    "docs/live_usage/LIVE-2026-10-07.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/fundamental_b_layer_filter.json",
]
TS = re.compile(r"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}")


def side(path, spec):
    r = subprocess.run(["git", "show", spec + path], capture_output=True)
    if r.returncode != 0:
        return None, None
    b = r.stdout
    m = TS.findall(b.decode("utf-8", "replace"))
    return b, (max(m) if m else "")


ok = True
for f in FILES:
    st = subprocess.run(["git", "status", "--porcelain", "--", f],
                        capture_output=True, text=True).stdout.strip()
    if not st.startswith("UU"):
        print("skip (not UU):", f, st[:12])
        continue
    ours_b, ours_ts = side(f, ":2:")
    theirs_b, theirs_ts = side(f, ":3:")
    if ours_b is None or theirs_b is None:
        print("MISSING SIDE:", f, ours_b is None, theirs_b is None)
        ok = False
        continue
    if ours_ts >= theirs_ts:
        win, wts, wside = ours_b, ours_ts, "LOCAL"
    else:
        win, wts, wside = theirs_b, theirs_ts, "ORIGIN"
    open(f, "wb").write(win)
    subprocess.run(["git", "add", "--", f], check=True)
    print(f"resolved {wside:6s} ts={wts or 'none'} : {f}")
sys.exit(0 if ok else 3)
