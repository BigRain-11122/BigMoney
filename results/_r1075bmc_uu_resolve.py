# -*- coding: utf-8 -*-
"""r1075 push-recovery UU resolver: 16 shared regenerable faces, per-file ts newer-wins
(r1073/r1028 precedent; rebase semantics: stage-2 = ours = origin/bm-a side, stage-3 =
theirs = my rebased commit side). Zero data loss by ts-field comparison; fallback =
stage-3 (my fresh S6 run 19:52) when no ts parsable."""
import subprocess, json, re, sys, io

GIT = r"C:\Program Files\Git\cmd\git.exe"
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
FILES = [
    "docs/daily_report/REPORT-2026-10-17.json",
    "docs/daily_report/REPORT-2026-10-17.md",
    "docs/live_usage/LIVE-2026-10-17.json",
    "docs/live_usage/LIVE-2026-10-17.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/token_usage.json",
    "results/update_status.json",
    "results/watermark_red.json",
    "results/zt_pool_crosscheck.json",
]

TS_RE = re.compile(r"20\d{2}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}")

def get(stage, path):
    r = subprocess.run([GIT, "show", f":{stage}:{path}"], cwd=ROOT,
                       capture_output=True)
    return r.stdout.decode("utf-8", "replace") if r.returncode == 0 else None

def ts_of(text):
    if not text:
        return ""
    m = TS_RE.findall(text)
    return max(m) if m else ""

report = []
for f in FILES:
    ours = get(2, f)      # origin/bm-a side
    theirs = get(3, f)    # my rebased side
    t_ours, t_theirs = ts_of(ours), ts_of(theirs)
    if t_ours and t_theirs:
        pick = "theirs" if t_theirs >= t_ours else "ours"
    elif t_theirs:
        pick = "theirs"
    elif t_ours:
        pick = "ours"
    else:
        pick = "theirs"   # fallback: my fresh S6 chain face
    side = get(2 if pick == "ours" else 3, f)
    with io.open(f, "w", encoding="utf-8", newline="") as fh:
        fh.write(side)
    report.append((f, t_ours or "-", t_theirs or "-", pick))
    print(f"{f:52s} origin_ts={t_ours or '-':20s} mine_ts={t_theirs or '-':20s} -> {pick}")

bad = [r for r in report if r[3] not in ("ours", "theirs")]
print("resolved", len(report), "faces, bad", len(bad))
