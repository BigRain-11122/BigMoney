# -*- coding: utf-8 -*-
"""r832 bm-a S6 maintenance chain batch runner (37-gate golden-week face; r819/r823/r828 bloodline verbatim).
Runs every chain gate in order, captures exit codes + one-line tails.
Exit-code contract per gate documented in the loop prompt; non-zero
codes surface verbatim (no masking)."""
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
GATES = [
    ("pool_dualrun_reconcile", ["python", "scripts\\pool_dualrun_reconcile.py", "run"]),
    ("compute_audit", ["python", "scripts\\compute_audit.py"]),
    ("py_watermark", ["python", "scripts\\py_watermark.py", "probe"]),
    ("update_daily", ["python", "scripts\\update_daily.py"]),
    ("market_regime", ["python", "scripts\\market_regime.py"]),
    ("strategy_scorecard", ["python", "scripts\\strategy_scorecard.py"]),
    ("market_clock_call", ["python", "scripts\\market_clock_call.py", "run"]),
    ("update_lhb", ["python", "scripts\\update_lhb.py"]),
    ("update_heat", ["python", "scripts\\update_heat.py"]),
    ("update_futures", ["python", "scripts\\update_futures.py"]),
    ("update_repo", ["python", "scripts\\update_repo.py"]),
    ("update_options", ["python", "scripts\\update_options.py"]),
    ("update_moneyflow", ["python", "scripts\\update_moneyflow.py"]),
    ("update_sina_mf", ["python", "scripts\\update_sina_mf.py"]),
    ("update_astock_daily", ["python", "scripts\\update_astock_daily.py"]),
    ("update_etf_daily", ["python", "scripts\\update_etf_daily.py"]),
    ("rev_osc_signal_export", ["python", "scripts\\rev_osc_signal_export.py", "run"]),
    ("update_minute_feed", ["python", "scripts\\update_minute_feed.py"]),
    ("update_ths_panel", ["python", "scripts\\update_ths_panel.py"]),
    ("ah_panel_puller", ["python", "scripts\\ah_panel_puller.py"]),
    ("update_fund_premium", ["python", "scripts\\update_fund_premium.py", "snapshot"]),
    ("update_fundamental", ["python", "scripts\\update_fundamental.py"]),
    ("b_layer_filter", ["python", "-m", "firm.risk.b_layer_filter"]),
    ("update_fund_statements", ["python", "scripts\\update_fund_statements.py"]),
    ("t24_prospect_paper", ["python", "scripts\\t24_prospect_paper.py", "run"]),
    ("t24_prospect_promotion", ["python", "scripts\\t24_prospect_promotion.py", "run"]),
    ("aggressive_lab", ["python", "scripts\\aggressive_lab.py", "paper"]),
    ("alloc_paper", ["python", "scripts\\alloc_paper.py", "run"]),
    ("grid_paper", ["python", "scripts\\grid_paper.py", "run"]),
    ("system_v1_paper", ["python", "scripts\\system_v1_paper.py", "run"]),
    ("t35_paper_export", ["python", "scripts\\t35_paper_export.py", "run"]),
    ("daily_scorecard", ["python", "scripts\\daily_scorecard.py"]),
    ("daily_report", ["python", "scripts\\daily_report.py", "run"]),
    ("ceo_live_usage", ["python", "scripts\\ceo_live_usage.py"]),
    ("build_status", ["python", "-m", "monitor.build_status"]),
    ("token_meter", ["python", "scripts\\token_meter.py"]),
    ("attrition_guard", ["python", "scripts\\attrition_ledger_guard.py", "scan"]),
]
fails = []
for name, cmd in GATES:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=900,
                           cwd=".")
        tail = (r.stdout or "").strip().splitlines()
        last = tail[-1][:150] if tail else (r.stderr or "").strip()[-150:]
        print(f"[{r.returncode}] {name}: {last}")
        if r.returncode != 0:
            fails.append((name, r.returncode))
    except subprocess.TimeoutExpired:
        print(f"[TIMEOUT] {name}")
        fails.append((name, "timeout"))
print(f"\nS6 chain summary: {len(GATES)} gates, {len(fails)} non-zero")
if fails:
    print("FAILS:", fails)
    sys.exit(1)
print("ALL RC0")

