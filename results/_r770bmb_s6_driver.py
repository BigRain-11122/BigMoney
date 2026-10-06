import subprocess, sys, io, json, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

LEGS = [
    ("reconcile",  ["python", "scripts/pool_dualrun_reconcile.py", "run"]),
    ("compute_audit", ["python", "scripts/compute_audit.py"]),
    ("py_watermark", ["python", "scripts/py_watermark.py", "probe"]),
    ("update_daily", ["python", "scripts/update_daily.py"]),
    ("market_regime", ["python", "scripts/market_regime.py"]),
    ("strategy_scorecard", ["python", "scripts/strategy_scorecard.py"]),
    ("market_clock_call", ["python", "scripts/market_clock_call.py", "run"]),
    ("update_lhb", ["python", "scripts/update_lhb.py"]),
    ("update_heat", ["python", "scripts/update_heat.py"]),
    ("update_futures", ["python", "scripts/update_futures.py"]),
    ("update_repo", ["python", "scripts/update_repo.py"]),
    ("update_options", ["python", "scripts/update_options.py"]),
    ("update_moneyflow", ["python", "scripts/update_moneyflow.py"]),
    ("update_sina_mf", ["python", "scripts/update_sina_mf.py"]),
    ("update_astock_daily", ["python", "scripts/update_astock_daily.py"]),
    ("update_etf_daily", ["python", "scripts/update_etf_daily.py"]),
    ("rev_osc_export", ["python", "scripts/rev_osc_signal_export.py", "run"]),
    ("update_minute_feed", ["python", "scripts/update_minute_feed.py"]),
    ("update_ths_panel", ["python", "scripts/update_ths_panel.py"]),
    ("ah_panel_puller", ["python", "scripts/ah_panel_puller.py"]),
    ("update_fund_premium", ["python", "scripts/update_fund_premium.py", "snapshot"]),
    ("update_fundamental", ["python", "scripts/update_fundamental.py"]),
    ("b_layer_filter", ["python", "-m", "firm.risk.b_layer_filter"]),
    ("update_fund_statements", ["python", "scripts/update_fund_statements.py"]),
    ("t24_prospect_promotion", ["python", "scripts/t24_prospect_promotion.py", "run"]),
    ("aggressive_lab", ["python", "scripts/aggressive_lab.py", "paper"]),
    ("alloc_paper", ["python", "scripts/alloc_paper.py", "run"]),
    ("grid_paper", ["python", "scripts/grid_paper.py", "run"]),
    ("system_v1_paper", ["python", "scripts/system_v1_paper.py", "run"]),
    ("t35_paper_export", ["python", "scripts/t35_paper_export.py", "run"]),
    ("daily_scorecard", ["python", "scripts/daily_scorecard.py"]),
    ("daily_report", ["python", "scripts/daily_report.py", "run"]),
    ("ceo_live_usage", ["python", "scripts/ceo_live_usage.py"]),
    ("build_status", ["python", "-m", "monitor.build_status"]),
    ("token_meter", ["python", "scripts/token_meter.py"]),
]

results = []
t0 = time.time()
for name, cmd in LEGS:
    ts = time.time()
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=900, cwd=".")
        rc = r.returncode
        out = (r.stdout or b"").decode('utf-8', 'replace')
        err = (r.stderr or b"").decode('utf-8', 'replace')
    except subprocess.TimeoutExpired:
        rc, out, err = 124, "", "TIMEOUT"
    dt = time.time() - ts
    tail = (out.strip().splitlines() or [''])[-1][:160] if out.strip() else (err.strip().splitlines() or [''])[-1][:160]
    results.append({"leg": name, "rc": rc, "sec": round(dt,1), "tail": tail})
    print(f"[{name}] rc={rc} {dt:.0f}s | {tail}")

print()
print(f"TOTAL {time.time()-t0:.0f}s, legs={len(results)}, rc0={sum(1 for r in results if r['rc']==0)}, nonzero={[r['leg']+':'+str(r['rc']) for r in results if r['rc']!=0]}")
json.dump(results, open('results/_r770bmb_s6_chain.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
