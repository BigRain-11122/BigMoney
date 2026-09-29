# -*- coding: utf-8 -*-
"""_r459bma_s6_chain.py -- r459 bm-a S6 chain stage runner: execute legs in
the prompt's fixed order, print rc + one-line tail per leg, fail-open to the
next leg (exit codes reported verbatim in round report per no-mask law)."""
import subprocess
import sys

LEGS = [
    ["python", "scripts/pool_dualrun_reconcile.py", "run"],
    ["python", "scripts/compute_audit.py"],
    ["python", "scripts/py_watermark.py", "probe"],
    ["python", "scripts/update_daily.py"],
    ["python", "scripts/market_regime.py"],
    ["python", "scripts/strategy_scorecard.py"],
    ["python", "scripts/market_clock_call.py", "run"],
    ["python", "scripts/update_lhb.py"],
    ["python", "scripts/update_heat.py"],
    ["python", "scripts/update_futures.py"],
    ["python", "scripts/update_repo.py"],
    ["python", "scripts/update_options.py"],
    ["python", "scripts/update_moneyflow.py"],
    ["python", "scripts/update_sina_mf.py"],
    ["python", "scripts/update_astock_daily.py"],
    ["python", "scripts/update_etf_daily.py"],
    ["python", "scripts/rev_osc_signal_export.py", "run"],
    ["python", "scripts/update_minute_feed.py"],
    ["python", "scripts/update_ths_panel.py"],
    ["python", "scripts/ah_panel_puller.py"],
    ["python", "scripts/update_fund_premium.py", "snapshot"],
    ["python", "scripts/update_fundamental.py"],
    ["python", "-m", "firm.risk.b_layer_filter"],
]

only = sys.argv[1:] if len(sys.argv) > 1 else None
fails = []
for leg in LEGS:
    name = " ".join(leg[1:])
    if only and not any(o in name for o in only):
        continue
    try:
        p = subprocess.run(leg, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=900)
        rc, out = p.returncode, (p.stdout or "").strip().splitlines()
    except subprocess.TimeoutExpired:
        rc, out = 124, ["TIMEOUT 900s"]
    tail = out[-1][:220] if out else "(no stdout)"
    print(f"RC={rc} | {name} | {tail}", flush=True)
    if rc not in (0,):
        fails.append((name, rc))
print("STAGE_FAILS:", fails if fails else "none")
