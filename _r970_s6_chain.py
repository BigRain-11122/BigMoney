# r970 bm-a S6 maintenance chain runner -- sequential legs, exit-code log.
# Each leg's rc recorded; rc2/rc3 legs flagged for honest report (no masking).
import subprocess, sys, time
sys.stdout.reconfigure(encoding="utf-8")
LEGS = [
    ("pool_dualrun_reconcile", ["scripts\\pool_dualrun_reconcile.py", "run"]),
    ("compute_audit",          ["scripts\\compute_audit.py"]),
    ("py_watermark_probe",      ["scripts\\py_watermark.py", "probe"]),
    ("update_daily",            ["scripts\\update_daily.py"]),
    ("market_regime",           ["scripts\\market_regime.py"]),
    ("strategy_scorecard",      ["scripts\\strategy_scorecard.py"]),
    ("market_clock_call",       ["scripts\\market_clock_call.py", "run"]),
    ("update_lhb",              ["scripts\\update_lhb.py"]),
    ("update_zt_pool",          ["scripts\\update_zt_pool.py"]),
    ("update_heat",             ["scripts\\update_heat.py"]),
    ("update_futures",          ["scripts\\update_futures.py"]),
    ("update_repo",             ["scripts\\update_repo.py"]),
    ("update_options",          ["scripts\\update_options.py"]),
    ("update_moneyflow",        ["scripts\\update_moneyflow.py"]),
    ("update_sina_mf",          ["scripts\\update_sina_mf.py"]),
    ("update_astock_daily",     ["scripts\\update_astock_daily.py"]),
    ("update_etf_daily",        ["scripts\\update_etf_daily.py"]),
    ("regime_thermo_build",     ["scripts\\regime_thermo_build.py"]),
    ("regime_gate_dualarm",     ["scripts\\regime_gate_dualarm.py", "run"]),
    ("rev_osc_signal_export",   ["scripts\\rev_osc_signal_export.py", "run"]),
    ("update_minute_feed",      ["scripts\\update_minute_feed.py"]),
    ("update_ths_panel",        ["scripts\\update_ths_panel.py"]),
    ("ah_panel_puller",         ["scripts\\ah_panel_puller.py"]),
    ("update_fund_premium",     ["scripts\\update_fund_premium.py", "snapshot"]),
    ("update_fundamental",      ["scripts\\update_fundamental.py"]),
    ("b_layer_filter",          ["-m", "firm.risk.b_layer_filter"]),
    ("update_fund_statements",  ["scripts\\update_fund_statements.py"]),
    ("daily_scorecard",         ["scripts\\daily_scorecard.py"]),
    ("daily_report",            ["scripts\\daily_report.py", "run"]),
    ("ceo_live_usage",          ["scripts\\ceo_live_usage.py"]),
    ("monitor_build_status",    ["-m", "monitor.build_status"]),
    ("token_meter",             ["scripts\\token_meter.py"]),
]
results = []
t0 = time.time()
for name, args in LEGS:
    ts = time.strftime("%H:%M:%S")
    try:
        r = subprocess.run([sys.executable] + args, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=900)
        tail = ((r.stdout or "").strip().splitlines() or [""])[-1][:100]
        results.append((name, r.returncode, tail))
        print(f"[{ts}] {name}: rc={r.returncode} | {tail}", flush=True)
        if r.returncode not in (0,):
            # capture err tail for honest report
            err_tail = ((r.stderr or "").strip().splitlines() or [""])[-1][:200]
            print(f"    ERR-tail: {err_tail}", flush=True)
    except subprocess.TimeoutExpired:
        results.append((name, "TIMEOUT", ">900s"))
        print(f"[{ts}] {name}: TIMEOUT >900s", flush=True)
print(f"=== S6 CHAIN DONE in {time.time()-t0:.0f}s ===", flush=True)
bad = [(n, rc) for n, rc, _ in results if rc not in (0,)]
print("legs:", len(results), "| non-zero:", bad if bad else "NONE", flush=True)
