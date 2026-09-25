# -*- coding: utf-8 -*-
"""r226 (bm-b) S6 maintenance chain runner (weekend face).
Runs each leg, captures exit code, prints compact one-line verdicts.
Legs with new-bar dependency (live.paper family) are skipped on
no-new-bar rounds per loop protocol (cutoff 09-24 -> next bar 09-28).
"""
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

LEGS = [
    ("compute_audit",   [sys.executable, "scripts/compute_audit.py"]),
    ("py_watermark",    [sys.executable, "scripts/py_watermark.py", "probe"]),
    ("update_daily",    [sys.executable, "scripts/update_daily.py"]),
    ("update_lhb",      [sys.executable, "scripts/update_lhb.py"]),
    ("update_heat",     [sys.executable, "scripts/update_heat.py"]),
    ("update_futures",  [sys.executable, "scripts/update_futures.py"]),
    ("update_options",  [sys.executable, "scripts/update_options.py"]),
    ("update_moneyflow",[sys.executable, "scripts/update_moneyflow.py"]),
    ("update_ths_panel",[sys.executable, "scripts/update_ths_panel.py"]),
    ("ah_panel_puller",[sys.executable, "scripts/ah_panel_puller.py"]),
    ("fund_premium",   [sys.executable, "scripts/update_fund_premium.py", "snapshot"]),
    ("fundamental",    [sys.executable, "scripts/update_fundamental.py"]),
    ("b_layer_filter", [sys.executable, "-m", "firm.risk.b_layer_filter"]),
    ("daily_scorecard",[sys.executable, "scripts/daily_scorecard.py"]),
    ("build_status",   [sys.executable, "-m", "monitor.build_status"]),
    ("token_meter",    [sys.executable, "scripts/token_meter.py"]),
    ("regime_recheck", [sys.executable, "scripts/market_regime.py"]),
]

env = dict(os.environ)
fails = []
for name, cmd in LEGS:
    try:
        p = subprocess.run(cmd, capture_output=True, timeout=600, env=env,
                           cwd=os.getcwd())
        code = p.returncode
        out = (p.stdout or b"").decode("utf-8", errors="replace").strip()
        err = (p.stderr or b"").decode("utf-8", errors="replace").strip()
        lines = [l for l in (out + "\n" + err).splitlines() if l.strip()]
        tail = lines[-1][:180] if lines else "(no output)"
    except subprocess.TimeoutExpired:
        code, tail = -99, "TIMEOUT 600s"
    print(f"[{name}] exit={code} | {tail}")
    if code not in (0,):
        fails.append(name)
print()
print("FAILS:", fails if fails else "none (all exit 0)")
