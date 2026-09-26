# r238 (bm-a): S6 maintenance chain runner -- sequential legs, per-leg exit
# code + last stdout line (fail-visible). New-bar conditional legs skipped on
# no-new-bar rounds per gate semantics (paper family legs 16-20).
import subprocess, sys

LEGS = [
    ("compute_audit", [sys.executable, "scripts/compute_audit.py"]),
    ("py_watermark", [sys.executable, "scripts/py_watermark.py", "probe"]),
    ("update_daily", [sys.executable, "scripts/update_daily.py"]),
    ("market_regime", [sys.executable, "scripts/market_regime.py"]),
    ("update_lhb", [sys.executable, "scripts/update_lhb.py"]),
    ("update_heat", [sys.executable, "scripts/update_heat.py"]),
    ("update_futures", [sys.executable, "scripts/update_futures.py"]),
    ("update_options", [sys.executable, "scripts/update_options.py"]),
    ("update_moneyflow", [sys.executable, "scripts/update_moneyflow.py"]),
    ("update_sina_mf", [sys.executable, "scripts/update_sina_mf.py"]),
    ("update_ths_panel", [sys.executable, "scripts/update_ths_panel.py"]),
    ("ah_panel", [sys.executable, "scripts/ah_panel_puller.py"]),
    ("fund_premium", [sys.executable, "scripts/update_fund_premium.py", "snapshot"]),
    ("fundamental", [sys.executable, "scripts/update_fundamental.py"]),
    ("b_layer_filter", [sys.executable, "-m", "firm.risk.b_layer_filter"]),
    ("paper_export", [sys.executable, "scripts/t35_paper_export.py", "run"]),
    ("daily_scorecard", [sys.executable, "scripts/daily_scorecard.py"]),
    ("build_status", [sys.executable, "-m", "monitor.build_status"]),
    ("token_meter", [sys.executable, "scripts/token_meter.py"]),
]

for name, cmd in LEGS:
    r = subprocess.run(cmd, capture_output=True, timeout=900)
    tail = (r.stdout.decode("utf-8", "replace").strip().splitlines() or [""])
    last = tail[-1][:180] if tail else ""
    err = r.stderr.decode("utf-8", "replace").strip().splitlines()
    print(f"[{name}] exit={r.returncode} | {last}")
    if r.returncode not in (0,) and err:
        print(f"   STDERR: {err[-1][:200]}")
