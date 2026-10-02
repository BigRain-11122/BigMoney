# -*- coding: utf-8 -*-
"""_r585bma_s6_driver.py -- S6 maintenance chain driver for bm-a r585.
Runs the S6 legs in protocol order (dualrun BEFORE compute_audit per T-116 s3),
captures rc + tail line per leg. Holiday (2026-10-02): no-new-bar conditional
legs (live.paper / t35_open_fill_verify / t24_*) are skipped by design.
PS-pit laws honored (r495/r559/r571/r318): python subprocess argv lists, no
shell redirection, per-leg UTF-8 log capture.
"""
import subprocess, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEGS = [
    ("dualrun",   [sys.executable, "scripts/pool_dualrun_reconcile.py", "run"]),
    ("audit",     [sys.executable, "scripts/compute_audit.py"]),
    ("wm_probe",  [sys.executable, "scripts/py_watermark.py", "probe"]),
    ("daily",     [sys.executable, "scripts/update_daily.py"]),
    ("regime",    [sys.executable, "scripts/market_regime.py"]),
    ("scorecard", [sys.executable, "scripts/strategy_scorecard.py"]),
    ("clock",     [sys.executable, "scripts/market_clock_call.py", "run"]),
    ("lhb",       [sys.executable, "scripts/update_lhb.py"]),
    ("heat",      [sys.executable, "scripts/update_heat.py"]),
    ("futures",   [sys.executable, "scripts/update_futures.py"]),
    ("repo",      [sys.executable, "scripts/update_repo.py"]),
    ("options",   [sys.executable, "scripts/update_options.py"]),
    ("moneyflow", [sys.executable, "scripts/update_moneyflow.py"]),
    ("sina_mf",   [sys.executable, "scripts/update_sina_mf.py"]),
    ("astock",    [sys.executable, "scripts/update_astock_daily.py"]),
    ("etf_daily", [sys.executable, "scripts/update_etf_daily.py"]),
    ("rev_osc",   [sys.executable, "scripts/rev_osc_signal_export.py", "run"]),
    ("minute",    [sys.executable, "scripts/update_minute_feed.py"]),
    ("ths",       [sys.executable, "scripts/update_ths_panel.py"]),
    ("ah_panel",  [sys.executable, "scripts/ah_panel_puller.py"]),
    ("fund_prem", [sys.executable, "scripts/update_fund_premium.py", "snapshot"]),
    ("fundament", [sys.executable, "scripts/update_fundamental.py"]),
    ("blayer",    [sys.executable, "-m", "firm.risk.b_layer_filter"]),
    ("aggr",      [sys.executable, "scripts/aggressive_lab.py", "paper"]),
    ("alloc",     [sys.executable, "scripts/alloc_paper.py", "run"]),
    ("grid",      [sys.executable, "scripts/grid_paper.py", "run"]),
    ("sysv1",     [sys.executable, "scripts/system_v1_paper.py", "run"]),
    ("t35_export",[sys.executable, "scripts/t35_paper_export.py", "run"]),
    ("day_score", [sys.executable, "scripts/daily_scorecard.py"]),
    ("day_report",[sys.executable, "scripts/daily_report.py", "run"]),
    ("ceo_live",  [sys.executable, "scripts/ceo_live_usage.py"]),
    ("build_stat",[sys.executable, "-m", "monitor.build_status"]),
    ("token",     [sys.executable, "scripts/token_meter.py"]),
]

def main():
    results = []
    for name, cmd in LEGS:
        try:
            r = subprocess.run(cmd, cwd=ROOT, capture_output=True, timeout=580)
            rc = r.returncode
            out = (r.stdout or b'').decode('utf-8', 'replace').strip().splitlines()
            err = (r.stderr or b'').decode('utf-8', 'replace').strip().splitlines()
            tail = out[-1] if out else (err[-1] if err else '(no output)')
        except subprocess.TimeoutExpired:
            rc, tail = 'TIMEOUT', 'killed at 580s'
        results.append((name, rc, tail[:110]))
        print(f"{name:10s} rc={rc} | {tail[:110]}", flush=True)
    bad = [(n, rc) for n, rc, _ in results if rc not in (0,)]
    print(f"\nS6 SUMMARY: {len(results)} legs, non-zero-rc: {len(bad)}")
    for n, rc in bad:
        print(f"  RED: {n} rc={rc}")
    return 0 if not bad else 1

if __name__ == '__main__':
    sys.exit(main())
