# r827 deep-ts freshest-side resolver v2 (second rebase window UU set)
# (r819/r825 lineage; rebase stage law r351: :2:=origin/base, :3:=replay/local)
import subprocess, re, sys

FACES = [
    "docs/daily_report/REPORT-2026-10-07.json",
    "docs/daily_report/REPORT-2026-10-07.md",
    "docs/live_usage/LIVE-2026-10-07.json",
    "docs/live_usage/LIVE-2026-10-07.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/daily_scorecard.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/paper_export/export-2026-09-30.json",
    "results/paper_export/latest.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
]

TS_RE = re.compile(r"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}")

def blob(stage, rel):
    r = subprocess.run(["git", "show", f":{stage}:{rel}"], capture_output=True)
    return r.stdout if r.returncode == 0 else None

def freshest_ts(raw):
    hits = TS_RE.findall(raw.decode("utf-8", "replace"))
    return max(hits) if hits else None

for rel in FACES:
    b2, b3 = blob(2, rel), blob(3, rel)
    if b2 is None or b3 is None:
        print(f"SKIP {rel}: stage blob missing"); continue
    if b2 == b3:
        open(rel, "wb").write(b2); print(f"EQUAL {rel} -> :2:"); continue
    t2, t3 = freshest_ts(b2), freshest_ts(b3)
    if t2 and t3:
        side = ":2:" if t2 >= t3 else ":3:"
    elif t2: side = ":2:"
    elif t3: side = ":3:"
    else: side = ":2:"
    open(rel, "wb").write(b2 if side == ":2:" else b3)
    print(f"RESOLVED {rel}: origin_ts={t2} replay_ts={t3} -> {side}")
