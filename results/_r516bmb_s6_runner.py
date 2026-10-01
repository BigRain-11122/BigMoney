"""r516 bm-b S6 maintenance chain runner (sequential, rc captured per leg)."""
import subprocess
import sys

LEGS = [
    ("dualrun", [sys.executable, "scripts/pool_dualrun_reconcile.py", "run"]),
    ("compute_audit", [sys.executable, "scripts/compute_audit.py"]),
    ("py_watermark", [sys.executable, "scripts/py_watermark.py", "probe"]),
    ("update_daily", [sys.executable, "scripts/update_daily.py"]),
    ("market_regime", [sys.executable, "scripts/market_regime.py"]),
    ("strategy_scorecard", [sys.executable, "scripts/strategy_scorecard.py"]),
    ("market_clock", [sys.executable, "scripts/market_clock_call.py", "run"]),
    ("update_lhb", [sys.executable, "scripts/update_lhb.py"]),
    ("update_heat", [sys.executable, "scripts/update_heat.py"]),
    ("update_futures", [sys.executable, "scripts/update_futures.py"]),
    ("update_repo", [sys.executable, "scripts/update_repo.py"]),
    ("update_options", [sys.executable, "scripts/update_options.py"]),
    ("update_moneyflow", [sys.executable, "scripts/update_moneyflow.py"]),
    ("update_sina_mf", [sys.executable, "scripts/update_sina_mf.py"]),
    ("update_astock_daily", [sys.executable, "scripts/update_astock_daily.py"]),
    ("update_etf_daily", [sys.executable, "scripts/update_etf_daily.py"]),
    ("rev_osc_export", [sys.executable, "scripts/rev_osc_signal_export.py", "run"]),
    ("update_minute_feed", [sys.executable, "scripts/update_minute_feed.py"]),
    ("update_ths_panel", [sys.executable, "scripts/update_ths_panel.py"]),
    ("ah_panel_puller", [sys.executable, "scripts/ah_panel_puller.py"]),
    ("fund_premium", [sys.executable, "scripts/update_fund_premium.py", "snapshot"]),
    ("update_fundamental", [sys.executable, "scripts/update_fundamental.py"]),
    ("b_layer_filter", [sys.executable, "-m", "firm.risk.b_layer_filter"]),
    ("live_paper", [sys.executable, "-m", "live.paper"]),
    ("t35_open_fill", [sys.executable, "scripts/t35_open_fill_verify.py"]),
    ("t24_prospect_paper", [sys.executable, "scripts/t24_prospect_paper.py", "run"]),
    ("t24_promotion", [sys.executable, "scripts/t24_prospect_promotion.py", "run"]),
    ("aggressive_lab", [sys.executable, "scripts/aggressive_lab.py", "paper"]),
    ("alloc_paper", [sys.executable, "scripts/alloc_paper.py", "run"]),
    ("grid_paper", [sys.executable, "scripts/grid_paper.py", "run"]),
    ("system_v1_paper", [sys.executable, "scripts/system_v1_paper.py", "run"]),
    ("t35_paper_export", [sys.executable, "scripts/t35_paper_export.py", "run"]),
    ("daily_scorecard", [sys.executable, "scripts/daily_scorecard.py"]),
    ("daily_report", [sys.executable, "scripts/daily_report.py", "run"]),
    ("ceo_live_usage", [sys.executable, "scripts/ceo_live_usage.py"]),
    ("build_status", [sys.executable, "-m", "monitor.build_status"]),
    ("token_meter", [sys.executable, "scripts/token_meter.py"]),
]

fails = []
for name, cmd in LEGS:
    r = subprocess.run(cmd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace",
                       cwd=r"C:\Fluxgroup\FluxGroup\quant\bigmoney")
    tail = (r.stdout or "").strip().splitlines()[-1:] or [""]
    tail_err = (r.stderr or "").strip().splitlines()[-1:] or [""]
    print(f"[{name}] rc={r.returncode} | {tail[0][:120]}{'| ERR: '+tail_err[0][:100] if r.stderr.strip() else ''}")
    if r.returncode not in (0,):
        fails.append((name, r.returncode))

print(f"\nS6 chain done: {len(LEGS)} legs, non-zero rc: {len(fails)}")
for n, rc in fails:
    print(f"  FAIL {n} rc={rc}")
