"""r514 bm-a S6 deferred chain (3 windows deferred, fresh base now).
Runs the mandated leg order, captures rc + last stdout line per leg.
Exit codes 2/3 = report-verbatim law (never mask)."""
import subprocess
import sys

LEGS = [
    ("pool_dualrun_reconcile", ["python", "scripts/pool_dualrun_reconcile.py", "run"]),
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
    ("rev_osc_signal_export", ["python", "scripts/rev_osc_signal_export.py", "run"]),
    ("update_minute_feed", ["python", "scripts/update_minute_feed.py"]),
    ("update_ths_panel", ["python", "scripts/update_ths_panel.py"]),
    ("ah_panel_puller", ["python", "scripts/ah_panel_puller.py"]),
    ("update_fund_premium", ["python", "scripts/update_fund_premium.py", "snapshot"]),
    ("update_fundamental", ["python", "scripts/update_fundamental.py"]),
    ("b_layer_filter", ["python", "-m", "firm.risk.b_layer_filter"]),
]

bad = []
for name, cmd in LEGS:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=900)
        rc = p.returncode
        tail = (p.stdout or "").strip().splitlines()
        last = tail[-1][:110] if tail else (p.stderr or "").strip()[:110]
    except subprocess.TimeoutExpired:
        rc, last = 99, "TIMEOUT 900s"
    flag = "OK " if rc == 0 else "!! "
    print(f"{flag}{name}: rc={rc} | {last}")
    if rc not in (0,):
        bad.append((name, rc))

print("\n=== S6 chain summary ===")
print("all rc0" if not bad else f"non-zero legs: {bad}")
sys.exit(0 if not bad else 1)
