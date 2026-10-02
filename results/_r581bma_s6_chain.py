# -*- coding: utf-8 -*-
"""r581 bm-a S6 maintenance chain driver (prescribed order, compact rc/tail)."""
import subprocess
import sys

CHAIN = [
    ("pool_dualrun", [sys.executable, "scripts\\pool_dualrun_reconcile.py", "run"]),
    ("compute_audit", [sys.executable, "scripts\\compute_audit.py"]),
    ("py_watermark", [sys.executable, "scripts\\py_watermark.py", "probe"]),
    ("update_daily", [sys.executable, "scripts\\update_daily.py"]),
    ("market_regime", [sys.executable, "scripts\\market_regime.py"]),
    ("strategy_scorecard", [sys.executable, "scripts\\strategy_scorecard.py"]),
    ("market_clock_call", [sys.executable, "scripts\\market_clock_call.py", "run"]),
    ("update_lhb", [sys.executable, "scripts\\update_lhb.py"]),
    ("update_heat", [sys.executable, "scripts\\update_heat.py"]),
    ("update_futures", [sys.executable, "scripts\\update_futures.py"]),
    ("update_repo", [sys.executable, "scripts\\update_repo.py"]),
    ("update_options", [sys.executable, "scripts\\update_options.py"]),
    ("update_moneyflow", [sys.executable, "scripts\\update_moneyflow.py"]),
    ("update_sina_mf", [sys.executable, "scripts\\update_sina_mf.py"]),
    ("update_astock_daily", [sys.executable, "scripts\\update_astock_daily.py"]),
    ("update_etf_daily", [sys.executable, "scripts\\update_etf_daily.py"]),
    ("rev_osc_export", [sys.executable, "scripts\\rev_osc_signal_export.py", "run"]),
    ("update_minute_feed", [sys.executable, "scripts\\update_minute_feed.py"]),
    ("update_ths_panel", [sys.executable, "scripts\\update_ths_panel.py"]),
    ("ah_panel_puller", [sys.executable, "scripts\\ah_panel_puller.py"]),
    ("fund_premium", [sys.executable, "scripts\\update_fund_premium.py", "snapshot"]),
    ("update_fundamental", [sys.executable, "scripts\\update_fundamental.py"]),
    ("b_layer_filter", [sys.executable, "-m", "firm.risk.b_layer_filter"]),
    ("aggressive_lab", [sys.executable, "scripts\\aggressive_lab.py", "paper"]),
    ("alloc_paper", [sys.executable, "scripts\\alloc_paper.py", "run"]),
    ("grid_paper", [sys.executable, "scripts\\grid_paper.py", "run"]),
    ("system_v1_paper", [sys.executable, "scripts\\system_v1_paper.py", "run"]),
    ("t35_paper_export", [sys.executable, "scripts\\t35_paper_export.py", "run"]),
    ("daily_scorecard", [sys.executable, "scripts\\daily_scorecard.py"]),
    ("daily_report", [sys.executable, "scripts\\daily_report.py", "run"]),
    ("ceo_live_usage", [sys.executable, "scripts\\ceo_live_usage.py"]),
    ("build_status", [sys.executable, "-m", "monitor.build_status"]),
    ("token_meter", [sys.executable, "scripts\\token_meter.py"]),
]

fails = []
for name, cmd in CHAIN:
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=300, cwd=".")
        rc = r.returncode
        tail = (r.stdout or b"").decode("utf-8", "replace").strip().splitlines()
        last = tail[-1][:110] if tail else (r.stderr or b"").decode("utf-8", "replace").strip()[:110]
    except subprocess.TimeoutExpired:
        rc, last = "TIMEOUT", ">300s"
    flag = "" if rc == 0 else f"  <-- rc={rc}"
    print(f"{name:20s} rc={rc if rc == 0 else rc} | {last}{flag}")
    if rc not in (0,):
        fails.append((name, rc, last))

print()
print("S6 CHAIN SUMMARY:", "ALL rc=0" if not fails else f"{len(fails)} leg(s) non-zero: {fails}")
