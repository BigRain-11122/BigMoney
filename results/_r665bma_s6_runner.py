"""r665 S6 maintenance chain driver (37 legs, r664 order verbatim).
Fail-soft: every leg's rc recorded; rc!=0 legs reported, chain continues.
Log -> results/_r665bma_s6_log.txt
"""
import subprocess
import sys
import time
import io

LEGS = [
    ("pool_dualrun",          [sys.executable, r"scripts\pool_dualrun_reconcile.py", "run"]),
    ("compute_audit",         [sys.executable, r"scripts\compute_audit.py"]),
    ("py_watermark",          [sys.executable, r"scripts\py_watermark.py", "probe"]),
    ("update_daily",          [sys.executable, r"scripts\update_daily.py"]),
    ("market_regime",         [sys.executable, r"scripts\market_regime.py"]),
    ("strategy_scorecard",    [sys.executable, r"scripts\strategy_scorecard.py"]),
    ("market_clock_call",     [sys.executable, r"scripts\market_clock_call.py", "run"]),
    ("update_lhb",            [sys.executable, r"scripts\update_lhb.py"]),
    ("update_heat",           [sys.executable, r"scripts\update_heat.py"]),
    ("update_futures",        [sys.executable, r"scripts\update_futures.py"]),
    ("update_repo",           [sys.executable, r"scripts\update_repo.py"]),
    ("update_options",        [sys.executable, r"scripts\update_options.py"]),
    ("update_moneyflow",      [sys.executable, r"scripts\update_moneyflow.py"]),
    ("update_sina_mf",        [sys.executable, r"scripts\update_sina_mf.py"]),
    ("update_astock_daily",   [sys.executable, r"scripts\update_astock_daily.py"]),
    ("update_etf_daily",      [sys.executable, r"scripts\update_etf_daily.py"]),
    ("rev_osc_signal_export", [sys.executable, r"scripts\rev_osc_signal_export.py", "run"]),
    ("update_minute_feed",    [sys.executable, r"scripts\update_minute_feed.py"]),
    ("update_ths_panel",      [sys.executable, r"scripts\update_ths_panel.py"]),
    ("ah_panel_puller",       [sys.executable, r"scripts\ah_panel_puller.py"]),
    ("update_fund_premium",   [sys.executable, r"scripts\update_fund_premium.py", "snapshot"]),
    ("update_fundamental",    [sys.executable, r"scripts\update_fundamental.py"]),
    ("b_layer_filter",        [sys.executable, "-m", "firm.risk.b_layer_filter"]),
    ("update_fund_statements", [sys.executable, r"scripts\update_fund_statements.py"]),
    ("t35_open_fill_verify",  [sys.executable, r"scripts\t35_open_fill_verify.py"]),
    ("t24_prospect_paper",    [sys.executable, r"scripts\t24_prospect_paper.py", "run"]),
    ("t24_prospect_promotion", [sys.executable, r"scripts\t24_prospect_promotion.py", "run"]),
    ("aggressive_lab_paper",  [sys.executable, r"scripts\aggressive_lab.py", "paper"]),
    ("alloc_paper",           [sys.executable, r"scripts\alloc_paper.py", "run"]),
    ("grid_paper",            [sys.executable, r"scripts\grid_paper.py", "run"]),
    ("system_v1_paper",       [sys.executable, r"scripts\system_v1_paper.py", "run"]),
    ("t35_paper_export",      [sys.executable, r"scripts\t35_paper_export.py", "run"]),
    ("daily_scorecard",       [sys.executable, r"scripts\daily_scorecard.py"]),
    ("daily_report",          [sys.executable, r"scripts\daily_report.py", "run"]),
    ("ceo_live_usage",        [sys.executable, r"scripts\ceo_live_usage.py"]),
    ("build_status",          [sys.executable, "-m", "monitor.build_status"]),
    ("token_meter",           [sys.executable, r"scripts\token_meter.py"]),
]

LOG = r"results\_r665bma_s6_log.txt"
T0 = time.time()
bad = []
with io.open(LOG, "w", encoding="utf-8", newline="\n") as lf:
    for name, argv in LEGS:
        t0 = time.time()
        try:
            p = subprocess.run(argv, capture_output=True, timeout=1800)
            rc = p.returncode
            out = (p.stdout or b"").decode("utf-8", "replace")
            err = (p.stderr or b"").decode("utf-8", "replace")
        except Exception as e:  # mechanism failure of the driver itself
            rc, out, err = -1, "", f"driver-exception: {e}"
        el = time.time() - t0
        first = (out.strip().splitlines() or [""])[0][:180]
        lf.write(f"{name:24s} rc={rc:2d} {el:6.1f}s | {first}\n")
        if rc != 0:
            bad.append((name, rc, (err.strip().splitlines() or [""])[0][:180]))
        lf.flush()
    lf.write(f"chain: {len(LEGS)} legs, non-zero-rc: {len(bad)}, elapsed {time.time()-T0:.1f}s\n")

print(f"legs={len(LEGS)} non_zero_rc={len(bad)}")
for name, rc, e in bad:
    print(f"  NONZERO {name} rc={rc} :: {e}")
