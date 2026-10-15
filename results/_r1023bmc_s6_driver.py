import subprocess, sys, time

LEGS = [
    ("pool_dualrun", ["python", "scripts/pool_dualrun_reconcile.py", "run"]),
    ("compute_audit", ["python", "scripts/compute_audit.py"]),
    ("py_watermark", ["python", "scripts/py_watermark.py", "probe"]),
    ("update_daily", ["python", "scripts/update_daily.py"]),
    ("market_regime", ["python", "scripts/market_regime.py"]),
    ("strategy_scorecard", ["python", "scripts/strategy_scorecard.py"]),
    ("market_clock_call", ["python", "scripts/market_clock_call.py", "run"]),
    ("update_lhb", ["python", "scripts/update_lhb.py"]),
    ("update_zt_pool", ["python", "scripts/update_zt_pool.py"]),
    ("update_heat", ["python", "scripts/update_heat.py"]),
    ("update_futures", ["python", "scripts/update_futures.py"]),
    ("update_repo", ["python", "scripts/update_repo.py"]),
    ("update_options", ["python", "scripts/update_options.py"]),
    ("update_moneyflow", ["python", "scripts/update_moneyflow.py"]),
    ("update_sina_mf", ["python", "scripts/update_sina_mf.py"]),
    ("update_astock_daily", ["python", "scripts/update_astock_daily.py"]),
    ("update_etf_daily", ["python", "scripts/update_etf_daily.py"]),
    ("regime_thermo_build", ["python", "scripts/regime_thermo_build.py"]),
    ("regime_gate_dualarm", ["python", "scripts/regime_gate_dualarm.py", "run"]),
    ("rev_osc_signal_export", ["python", "scripts/rev_osc_signal_export.py", "run"]),
    ("update_minute_feed", ["python", "scripts/update_minute_feed.py"]),
    ("update_ths_panel", ["python", "scripts/update_ths_panel.py"]),
    ("ah_panel_puller", ["python", "scripts/ah_panel_puller.py"]),
    ("update_fund_premium", ["python", "scripts/update_fund_premium.py", "snapshot"]),
    ("update_fundamental", ["python", "scripts/update_fundamental.py"]),
    ("b_layer_filter", ["python", "-m", "firm.risk.b_layer_filter"]),
    ("update_fund_statements", ["python", "scripts/update_fund_statements.py"]),
    ("aggressive_lab", ["python", "scripts/aggressive_lab.py", "paper"]),
    ("alloc_paper", ["python", "scripts/alloc_paper.py", "run"]),
    ("grid_paper", ["python", "scripts/grid_paper.py", "run"]),
    ("system_v1_paper", ["python", "scripts/system_v1_paper.py", "run"]),
    ("t24_prospect_paper", ["python", "scripts/t24_prospect_paper.py", "run"]),
    ("t24_prospect_promotion", ["python", "scripts/t24_prospect_promotion.py", "run"]),
    ("t35_paper_export", ["python", "scripts/t35_paper_export.py", "run"]),
    ("daily_report", ["python", "scripts/daily_report.py", "run"]),
    ("ceo_live_usage", ["python", "scripts/ceo_live_usage.py"]),
    ("token_meter", ["python", "scripts/token_meter.py"]),
]

fails = []
t0 = time.time()
for i, (name, cmd) in enumerate(LEGS, 1):
    ts = time.time()
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600)
        rc = r.returncode
        out = ((r.stdout or "") + (r.stderr or "")).strip().splitlines()
        first = out[-1][:110] if out else ""
    except subprocess.TimeoutExpired:
        rc, first = 99, "TIMEOUT"
    print("LEG %02d %-22s rc=%d %5.1fs | %s" % (i, name, rc, time.time() - ts, first), flush=True)
    if rc not in (0,):
        fails.append((name, rc, first))

print("TOTAL %.1fs FAILS=%d %s" % (time.time() - t0, len(fails), [(f[0], f[1]) for f in fails]), flush=True)
sys.exit(2 if fails else 0)
