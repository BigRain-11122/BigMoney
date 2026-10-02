# -*- coding: utf-8 -*-
"""r592 bm-a S6 maintenance chain driver (compact: name | rc | tail-line)."""
import subprocess, sys

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
    ("update_astock_daily(bm-b lane)", [sys.executable, "scripts/update_astock_daily.py"]),
    ("update_etf_daily(bm-b lane)", [sys.executable, "scripts/update_etf_daily.py"]),
    ("rev_osc(bm-b lane)", [sys.executable, "scripts/rev_osc_signal_export.py", "run"]),
    ("update_minute_feed(bm-b lane)", [sys.executable, "scripts/update_minute_feed.py"]),
    ("update_ths_panel", [sys.executable, "scripts/update_ths_panel.py"]),
    ("ah_panel_puller", [sys.executable, "scripts/ah_panel_puller.py"]),
    ("update_fund_premium(bm-c lane)", [sys.executable, "scripts/update_fund_premium.py", "snapshot"]),
    ("update_fundamental", [sys.executable, "scripts/update_fundamental.py"]),
    ("b_layer_filter", [sys.executable, "-m", "firm.risk.b_layer_filter"]),
]

for name, cmd in LEGS:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                           creationflags=0x08000000, timeout=600)
        tail = (r.stdout or "").strip().splitlines()
        last = tail[-1][:110] if tail else (r.stderr or "").strip()[-110:]
        print(f"{name} | rc={r.returncode} | {last}")
    except Exception as e:
        print(f"{name} | EXC | {e}")
