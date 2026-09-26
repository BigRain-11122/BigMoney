# -*- coding: utf-8 -*-
"""R281 bm-a S6 maintenance chain batch (22 legs this round; live.paper
family legitimately skipped = no new bar on Sunday weekend; monthly/
quarterly legs not due this round). Prints name + rc; non-zero rc tails
are surfaced verbatim (no masking law)."""
import subprocess
import sys

LEGS = [
    ("compute_audit", [sys.executable, "scripts/compute_audit.py"]),
    ("py_watermark", [sys.executable, "scripts/py_watermark.py", "probe"]),
    ("update_daily", [sys.executable, "scripts/update_daily.py"]),
    ("market_regime", [sys.executable, "scripts/market_regime.py"]),
    ("strategy_scorecard", [sys.executable, "scripts/strategy_scorecard.py"]),
    ("market_clock_call", [sys.executable, "scripts/market_clock_call.py",
                            "run"]),
    ("update_lhb", [sys.executable, "scripts/update_lhb.py"]),
    ("update_heat", [sys.executable, "scripts/update_heat.py"]),
    ("update_futures", [sys.executable, "scripts/update_futures.py"]),
    ("update_options", [sys.executable, "scripts/update_options.py"]),
    ("update_moneyflow", [sys.executable, "scripts/update_moneyflow.py"]),
    ("update_sina_mf", [sys.executable, "scripts/update_sina_mf.py"]),
    ("update_astock_daily(bmb-lane)", [sys.executable,
                                       "scripts/update_astock_daily.py"]),
    ("update_ths_panel", [sys.executable, "scripts/update_ths_panel.py"]),
    ("ah_panel_puller", [sys.executable, "scripts/ah_panel_puller.py"]),
    ("fund_premium(bmc-lane)", [sys.executable,
                                "scripts/update_fund_premium.py",
                                "snapshot"]),
    ("update_fundamental", [sys.executable, "scripts/update_fundamental.py"]),
    ("b_layer_filter", [sys.executable, "-m", "firm.risk.b_layer_filter"]),
    ("daily_scorecard", [sys.executable, "scripts/daily_scorecard.py"]),
    ("daily_report", [sys.executable, "scripts/daily_report.py", "run"]),
    ("build_status", [sys.executable, "-m", "monitor.build_status"]),
    ("token_meter", [sys.executable, "scripts/token_meter.py"]),
]

bad = []
for name, cmd in LEGS:
    r = subprocess.run(cmd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=900)
    tag = "rc=0" if r.returncode == 0 else f"rc={r.returncode} <<<<"
    print(f"{name}: {tag}", flush=True)
    if r.returncode != 0:
        bad.append(name)
        tail = (r.stdout or "").strip().splitlines()[-6:]
        for l in tail:
            print(f"    | {l}")
        et = (r.stderr or "").strip().splitlines()[-4:]
        for l in et:
            print(f"    ! {l}")
print("CHAIN:", "ALL rc=0" if not bad else f"NONZERO: {bad}")
