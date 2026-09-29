# S6 maintenance-chain runner (37 legs, fixed order per standing prompt).
# r236 pitfall law: reconfigure stdout/stderr to utf-8 replace at entry.
import subprocess, sys, io, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

LEGS = [
    ("pool_dualrun_reconcile", [sys.executable, "scripts/pool_dualrun_reconcile.py", "run"]),
    ("compute_audit", [sys.executable, "scripts/compute_audit.py"]),
    ("py_watermark", [sys.executable, "scripts/py_watermark.py", "probe"]),
    ("update_daily", [sys.executable, "scripts/update_daily.py"]),
    ("market_regime", [sys.executable, "scripts/market_regime.py"]),
    ("strategy_scorecard", [sys.executable, "scripts/strategy_scorecard.py"]),
    ("market_clock_call", [sys.executable, "scripts/market_clock_call.py", "run"]),
    ("update_lhb", [sys.executable, "scripts/update_lhb.py"]),
    ("update_heat", [sys.executable, "scripts/update_heat.py"]),
    ("update_futures", [sys.executable, "scripts/update_futures.py"]),
    ("update_repo", [sys.executable, "scripts/update_repo.py"]),
    ("update_options", [sys.executable, "scripts/update_options.py"]),
    ("update_moneyflow", [sys.executable, "scripts/update_moneyflow.py"]),
    ("update_sina_mf", [sys.executable, "scripts/update_sina_mf.py"]),
    ("update_astock_daily", [sys.executable, "scripts/update_astock_daily.py"]),
    ("update_etf_daily", [sys.executable, "scripts/update_etf_daily.py"]),
    ("rev_osc_signal_export", [sys.executable, "scripts/rev_osc_signal_export.py", "run"]),
    ("update_minute_feed", [sys.executable, "scripts/update_minute_feed.py"]),
    ("update_ths_panel", [sys.executable, "scripts/update_ths_panel.py"]),
    ("ah_panel_puller", [sys.executable, "scripts/ah_panel_puller.py"]),
    ("update_fund_premium", [sys.executable, "scripts/update_fund_premium.py", "snapshot"]),
    ("update_fundamental", [sys.executable, "scripts/update_fundamental.py"]),
    ("b_layer_filter", [sys.executable, "-m", "firm.risk.b_layer_filter"]),
]

results = {}
for name, cmd in LEGS:
    t0 = time.time()
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=900)
        rc = r.returncode
        tail = (r.stdout or "").strip().splitlines()[-3:]
        err = (r.stderr or "").strip().splitlines()[-3:]
    except subprocess.TimeoutExpired:
        rc = -9
        tail = ["TIMEOUT 900s"]
        err = []
    results[name] = {"rc": rc, "sec": round(time.time() - t0, 1), "tail": tail, "err": err}
    print(f"[{rc}] {name} ({results[name]['sec']}s)")
    for l in tail[-2:]:
        print("    ", l[:220])

io.open("results/_r441bmb_s6_legs.json", "w", encoding="utf-8").write(
    __import__("json").dumps(results, ensure_ascii=False, indent=1))
print("== S6 phase A done ==")
