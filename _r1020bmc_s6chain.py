import subprocess
import sys

LEGS = [
    ("dualrun", [sys.executable, "scripts/pool_dualrun_reconcile.py", "run"]),
    ("compute_audit", [sys.executable, "scripts/compute_audit.py"]),
    ("wm_probe", [sys.executable, "scripts/py_watermark.py", "probe"]),
    ("update_daily", [sys.executable, "scripts/update_daily.py"]),
    ("regime", [sys.executable, "scripts/market_regime.py"]),
    ("scorecard", [sys.executable, "scripts/strategy_scorecard.py"]),
    ("clock", [sys.executable, "scripts/market_clock_call.py", "run"]),
    ("lhb", [sys.executable, "scripts/update_lhb.py"]),
    ("zt_pool", [sys.executable, "scripts/update_zt_pool.py"]),
    ("heat", [sys.executable, "scripts/update_heat.py"]),
    ("futures", [sys.executable, "scripts/update_futures.py"]),
    ("repo", [sys.executable, "scripts/update_repo.py"]),
    ("fund_prem", [sys.executable, "scripts/update_fund_premium.py", "snapshot"]),
    ("fundamental", [sys.executable, "scripts/update_fundamental.py"]),
    ("b_layer", [sys.executable, "-m", "firm.risk.b_layer_filter"]),
    ("fund_stmt", [sys.executable, "scripts/update_fund_statements.py"]),
    ("daily_scorecard", [sys.executable, "scripts/daily_scorecard.py"]),
    ("daily_report", [sys.executable, "scripts/daily_report.py", "run"]),
    ("live_usage", [sys.executable, "scripts/ceo_live_usage.py"]),
    ("dashboard", [sys.executable, "-m", "monitor.build_status"]),
    ("token_meter", [sys.executable, "scripts/token_meter.py"]),
]

results = []
for name, cmd in LEGS:
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=600)
        rc = r.returncode
        tail = (r.stdout or b'').decode('utf-8', 'replace').strip().splitlines()
        last = tail[-1][:110] if tail else ''
        err = (r.stderr or b'').decode('utf-8', 'replace').strip().splitlines()
        lasterr = err[-1][:110] if err else ''
    except subprocess.TimeoutExpired:
        rc, last, lasterr = 99, 'TIMEOUT', ''
    results.append((name, rc, last, lasterr))
    print(f"{name:16s} rc={rc:2d} | {last}")

bad = [r for r in results if r[1] not in (0,)]
print("---")
print("ALL-RC0" if not bad else f"NONZERO LEGS: {[(b[0],b[1]) for b in bad]}")
