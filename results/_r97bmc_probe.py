# -*- coding: utf-8 -*-
"""r97 bm-c rebase-resolve probe: per-UU-face deep-ts of both sides.
Sides: HEAD = origin/main (bm-a r344), MINE = 32b4edae (bm-c r97).
r342 wave-2 law: same-family re-derivation faces -> take-new byte-verbatim by deep-ts.
"""
import subprocess, re

MINE = "32b4edae"
UU = """docs/daily_report/REPORT-2026-09-27.json
docs/daily_report/REPORT-2026-09-27.md
results/autofill_state.json
results/compute_audit.json
results/daily_scorecard.json
results/dashboard_status.js
results/dashboard_status.json
results/fundamental_b_layer_filter.json
results/futures_update_status.json
results/heat_update_status.json
results/lhb_update_status.json
results/paper/COMPOSITE-CE-01_paper.json
results/paper/COMPOSITE-CE-02_paper.json
results/paper/DROUGHT-CE-01_paper.json
results/paper/ENGULF-CE-01_paper.json
results/paper/NEEDLE-DE-01_paper.json
results/paper/VOLATILITY-CE-01_paper.json
results/paper_export/export-2026-09-24.json
results/paper_export/latest.json
results/prospect_paper/_summary.json
results/prospect_promotion/_summary.json
results/regime_state.json
results/scorecard_v1.json
results/strategy_scorecard.json
results/t35_open_fill_verify.json
results/token_usage.json
results/update_status.json
results/x2_watch_log.jsonl""".split()

def side(ref, path):
    r = subprocess.run(["git", "show", "%s:%s" % (ref, path)], capture_output=True)
    return r.stdout

TSRE = re.compile(rb'"(ts|generated|generated_at|written_at|asof|last_run|updated|last_tick)"\s*:\s*"?([0-9T:.\- ]{8,24})')

def deepts(b):
    hits = TSRE.findall(b)
    return [h[1].decode() for h in hits[:6]]

for p in UU:
    a, m = side("HEAD", p), side(MINE, p)
    print("FACE", p, "| A_byts=%d M_byts=%d" % (len(a), len(m)))
    print("  A_ts:", deepts(a))
    print("  M_ts:", deepts(m))
