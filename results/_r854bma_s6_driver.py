# -*- coding: utf-8 -*-
"""r854 bm-a S6 chain driver (r853 bloodline copy) (r850 bloodline + full paper/report family = 38 legs).
10-08 market-reopen day ~01:40 pre-market: no new bar expected yet -> bar-conditioned
paper family honest no-ops; REGIME_GUARD enforce env set per protocol (v3 date gate
passed 10-01; no-new-bar = anchor no-op face)."""
import os
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
    ("live_paper", ["python", "-m", "live.paper"]),
    ("t35_open",   ["python", "scripts\\t35_open_fill_verify.py"]),
    ("t24_prosp",  ["python", "scripts\\t24_prospect_paper.py", "run"]),
    ("t24_promo",  ["python", "scripts\\t24_prospect_promotion.py", "run"]),
    ("aggr_lab",   ["python", "scripts\\aggressive_lab.py", "paper"]),
    ("alloc_paper", ["python", "scripts\\alloc_paper.py", "run"]),
    ("grid_paper",  ["python", "scripts\\grid_paper.py", "run"]),
    ("sysv1_paper", ["python", "scripts\\system_v1_paper.py", "run"]),
    ("t35_export", ["python", "scripts\\t35_paper_export.py", "run"]),
    ("d_scorecard", ["python", "scripts\\daily_scorecard.py"]),
    ("d_report",   ["python", "scripts\\daily_report.py", "run"]),
    ("ceo_live",   ["python", "scripts\\ceo_live_usage.py"]),
    ("build_status", ["python", "-m", "monitor.build_status"]),
    ("token_meter", ["python", "scripts\\token_meter.py"]),
]

rows = []
t0 = time.time()
for name, cmd in LEGS:
    t1 = time.time()
    env = dict(os.environ)
    if name == "live_paper":
        env["BIGMONEY_REGIME_GUARD"] = "enforce"
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=300, env=env)
        rc = r.returncode
        out = (r.stdout or b"").decode("utf-8", "replace").strip().splitlines()
        tail = out[-1][:150] if out else (r.stderr or b"").decode("utf-8", "replace").strip()[:150]
    except subprocess.TimeoutExpired:
        rc = "TIMEOUT"
        tail = "300s timeout"
    dt = time.time() - t1
    rows.append((name, rc, round(dt, 1), tail))
    print("%-13s rc=%-4s %5.1fs | %s" % (name, rc, dt, tail))

n_ok = sum(1 for _, rc, _, _ in rows if rc == 0)
print("S6 TOTAL %d legs, rc0=%d, elapsed %.0fs" % (len(rows), n_ok, time.time() - t0))
bad = [(n, rc) for n, rc, _, _ in rows if rc != 0]
print("NON-ZERO:", bad if bad else "none")
