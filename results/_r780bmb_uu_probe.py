# r780 bm-b rebase 17-UU per-face ts probe (r756 normalize law / r773 per-face evidence law)
# rebase window: stage2 = onto(origin/bm-a side), stage3 = replayed bm-b commit (r782 law)
import subprocess, json, re, sys
from datetime import datetime

FILES = [
 "docs/daily_report/REPORT-2026-10-06.json", "docs/daily_report/REPORT-2026-10-06.md",
 "docs/live_usage/LIVE-2026-10-06.json", "docs/live_usage/LIVE-2026-10-06.md",
 "docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md",
 "results/compute_audit.json", "results/dashboard_status.js", "results/dashboard_status.json",
 "results/fundamental_b_layer_filter.json", "results/futures_update_status.json",
 "results/lhb_update_status.json", "results/regime_state.json", "results/scorecard_v1.json",
 "results/strategy_scorecard.json", "results/token_usage.json", "results/update_status.json",
]

TS_PAT = re.compile(r'"(ts|timestamp|generated_at|updated|last_run|clock_read)"\s*:\s*"([^"]+)"')
FREE_PAT = re.compile(r'2026-10-\d\d[T ]\d\d:\d\d:\d\d')

def blob(ref):
    r = subprocess.run(["git", "show", ref], capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout.decode("utf-8", "replace")

def norm(ts):
    # r756: space -> T unify, then strptime; naive -> +08:00 aware (fleet faces are Beijing time)
    t = ts.strip().replace(" ", "T")
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S"):
        try:
            d = datetime.strptime(t, fmt)
        except ValueError:
            continue
        if d.tzinfo is None:
            from datetime import timezone, timedelta
            d = d.replace(tzinfo=timezone(timedelta(hours=8)))
        return d
    return None

def max_ts(text):
    best = None
    for m in TS_PAT.finditer(text):
        d = norm(m.group(2))
        if d and (best is None or d > best):
            best = d
    if best is None:
        for m in FREE_PAT.finditer(text):
            d = norm(m.group(0))
            if d and (best is None or d > best):
                best = d
    return best

rows = []
for p in FILES:
    a, b = blob(":2:" + p), blob(":3:" + p)
    if a is None or b is None:
        rows.append((p, "STAGE_MISSING", None, None, len(a or ""), len(b or "")))
        continue
    ta, tb = max_ts(a), max_ts(b)
    if ta is None or tb is None:
        verdict = "NO_TS_TAKE_ORIGIN"  # cannot evidence newer -> conservative: keep origin authoritative face
    elif ta >= tb:
        verdict = "TAKE_ORIGIN"
    else:
        verdict = "TAKE_MINE"
    rows.append((p, verdict, ta, tb, len(a), len(b)))

for p, v, ta, tb, la, lb in rows:
    print("%-46s %-16s origin_ts=%s mine_ts=%s bytes=%d/%d" % (
        p, v, ta.strftime("%H:%M:%S") if ta else "none", tb.strftime("%H:%M:%S") if tb else "none", la, lb))
