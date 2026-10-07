# -*- coding: utf-8 -*-
"""r842 bm-a S6 chain driver. Runs legs in protocol order, captures rc + tail
line per leg. Holiday window: no new bar expected -> live.paper family skipped
(update_daily verdict checked and logged honestly)."""
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

LEGS = [
    ("dualrun",    ["python", "scripts\\pool_dualrun_reconcile.py", "run"]),
    ("comp_audit", ["python", "scripts\\compute_audit.py"]),
    ("py_watermark", ["python", "scripts\\py_watermark.py", "probe"]),
    ("update_daily", ["python", "scripts\\update_daily.py"]),
    ("regime",     ["python", "scripts\\market_regime.py"]),
    ("scorecard",  ["python", "scripts\\strategy_scorecard.py"]),
    ("mkt_clock",  ["python", "scripts\\market_clock_call.py", "run"]),
    ("lhb",        ["python", "scripts\\update_lhb.py"]),
    ("heat",       ["python", "scripts\\update_heat.py"]),
    ("futures",    ["python", "scripts\\update_futures.py"]),
    ("repo",       ["python", "scripts\\update_repo.py"]),
    ("options",    ["python", "scripts\\update_options.py"]),
    ("moneyflow",  ["python", "scripts\\update_moneyflow.py"]),
    ("sina_mf",    ["python", "scripts\\update_sina_mf.py"]),
    ("astock_daily", ["python", "scripts\\update_astock_daily.py"]),
    ("etf_daily",  ["python", "scripts\\update_etf_daily.py"]),
    ("rev_osc",    ["python", "scripts\\rev_osc_signal_export.py", "run"]),
    ("minute_feed", ["python", "scripts\\update_minute_feed.py"]),
    ("ths_panel",  ["python", "scripts\\update_ths_panel.py"]),
    ("ah_panel",   ["python", "scripts\\ah_panel_puller.py"]),
    ("fund_prem",  ["python", "scripts\\update_fund_premium.py", "snapshot"]),
    ("fundamental", ["python", "scripts\\update_fundamental.py"]),
    ("b_layer",    ["python", "-m", "firm.risk.b_layer_filter"]),
    ("fund_stmt",  ["python", "scripts\\update_fund_statements.py"]),
    ("ceo_live",   ["python", "scripts\\ceo_live_usage.py"]),
    ("build_status", ["python", "-m", "monitor.build_status"]),
    ("token_meter", ["python", "scripts\\token_meter.py"]),
]

rows = []
t0 = time.time()
for name, cmd in LEGS:
    t1 = time.time()
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=180)
        rc = r.returncode
        out = (r.stdout or b"").decode("utf-8", "replace").strip().splitlines()
        tail = out[-1][:150] if out else (r.stderr or b"").decode("utf-8", "replace").strip()[:150]
    except subprocess.TimeoutExpired:
        rc = "TIMEOUT"
        tail = "180s timeout"
    dt = time.time() - t1
    rows.append((name, rc, round(dt, 1), tail))
    print("%-13s rc=%-4s %5.1fs | %s" % (name, rc, dt, tail))

n_ok = sum(1 for _, rc, _, _ in rows if rc == 0)
print("S6 TOTAL %d legs, rc0=%d, elapsed %.0fs" % (len(rows), n_ok, time.time() - t0))
bad = [(n, rc) for n, rc, _, _ in rows if rc != 0]
print("NON-ZERO:", bad if bad else "none")
