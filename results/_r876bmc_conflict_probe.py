import json, re, subprocess, sys

FILES = [
    "docs/daily_report/REPORT-2026-10-11.json",
    "docs/daily_report/REPORT-2026-10-11.md",
    "results/_attrition_guard_scan.json",
    "results/_r686bmb_d19_check.json",
    "results/_r686bmb_orders_fresh.md",
    "results/compute_audit.json",
    "results/d19_watermark.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]

def side_text(rev, path):
    r = subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True)
    return r.stdout.decode("utf-8", errors="replace") if r.returncode == 0 else None

def norm_ts(s):
    # E52 normalization: space -> 'T', strip tz suffix for compare
    s = s.strip()
    s = s.replace(" ", "T")
    s = re.sub(r"\+08:00$", "", s)
    return s

def find_ts(txt):
    # first plausible ts field in the file
    m = re.search(r'"(?:ts|generated|updated|scan_ts)"\s*:\s*"?([0-9]{4}-[0-9]{2}-[0-9]{2}[ T][0-9:.:]{5,12}(?:\+08:00)?)', txt or "")
    return m.group(1) if m else None

for f in FILES:
    ours = side_text(":2", f)   # staged/ours side in rebase = our commit
    theirs = side_text(":3", f)  # incoming = origin/bm-b side
    if ours is None and theirs is None:
        print(f"{f}: BOTH SIDES ABSENT?")
        continue
    to, tt = find_ts(ours), find_ts(theirs)
    print(f"{f}\n  ours   ts={to}\n  theirs ts={tt}")
