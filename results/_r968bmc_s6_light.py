# -*- coding: utf-8 -*-
"""r968 bm-c S6 light chain (post-15:30 Tuesday window: today's bars landing).
Runs the standing collectors sequentially with lane guards honest no-op; reports rc per leg.
live.paper + t35_open_fill legs run with BIGMONEY_REGIME_GUARD=enforce per the chain law
(new-bar days; REGIME_GUARD v3 enforces the anchor gate, drift = abort).
Exit codes 2/3 must surface honestly (never masked)."""
import os, subprocess, sys, time
sys.stdout.reconfigure(encoding="utf-8")
PY = sys.executable
ENV_ENFORCE = {**os.environ, "BIGMONEY_REGIME_GUARD": "enforce"}
LEGS = [
    ("dualrun", [PY, "scripts/pool_dualrun_reconcile.py", "run"], None, 120),
    ("compute_audit", [PY, "scripts/compute_audit.py"], None, 120),
    ("wm_probe", [PY, "scripts/py_watermark.py", "probe"], None, 120),
    ("update_daily", [PY, "scripts/update_daily.py"], None, 900),
    ("live_paper", [PY, "-m", "live.paper"], ENV_ENFORCE, 900),
    ("t35_open_fill", [PY, "scripts/t35_open_fill_verify.py"], ENV_ENFORCE, 300),
    ("market_regime", [PY, "scripts/market_regime.py"], None, 120),
    ("market_clock", [PY, "scripts/market_clock_call.py", "run"], None, 120),
    ("update_lhb", [PY, "scripts/update_lhb.py"], None, 300),
    ("update_zt_pool", [PY, "scripts/update_zt_pool.py"], None, 300),
    ("update_heat", [PY, "scripts/update_heat.py"], None, 300),
    ("update_futures", [PY, "scripts/update_futures.py"], None, 300),
    ("update_repo", [PY, "scripts/update_repo.py"], None, 300),
    ("update_options", [PY, "scripts/update_options.py"], None, 120),
    ("update_moneyflow", [PY, "scripts/update_moneyflow.py"], None, 120),
    ("update_sina_mf", [PY, "scripts/update_sina_mf.py"], None, 120),
    ("update_astock_daily", [PY, "scripts/update_astock_daily.py"], None, 120),
    ("update_etf_daily", [PY, "scripts/update_etf_daily.py"], None, 120),
    ("regime_thermo", [PY, "scripts/regime_thermo_build.py"], None, 300),
    ("regime_gate_dualarm", [PY, "scripts/regime_gate_dualarm.py", "run"], None, 120),
    ("rev_osc_export", [PY, "scripts/rev_osc_signal_export.py", "run"], None, 120),
    ("update_minute_feed", [PY, "scripts/update_minute_feed.py"], None, 120),
    ("update_ths_panel", [PY, "scripts/update_ths_panel.py"], None, 120),
    ("ah_panel", [PY, "scripts/ah_panel_puller.py"], None, 120),
    ("fund_premium", [PY, "scripts/update_fund_premium.py", "snapshot"], None, 300),
    ("fundamental", [PY, "scripts/update_fundamental.py"], None, 300),
    ("b_layer", [PY, "-m", "firm.risk.b_layer_filter"], None, 120),
    ("fund_statements", [PY, "scripts/update_fund_statements.py"], None, 120),
    ("t24_prospect", [PY, "scripts/t24_prospect_paper.py", "run"], None, 300),
    ("t24_promotion", [PY, "scripts/t24_prospect_promotion.py", "run"], None, 300),
    ("aggr_paper", [PY, "scripts/aggressive_lab.py", "paper"], None, 300),
    ("alloc_paper", [PY, "scripts/alloc_paper.py", "run"], None, 300),
    ("grid_paper", [PY, "scripts/grid_paper.py", "run"], None, 300),
    ("system_v1_paper", [PY, "scripts/system_v1_paper.py", "run"], None, 300),
    ("t35_export", [PY, "scripts/t35_paper_export.py", "run"], None, 300),
    ("daily_report", [PY, "scripts/daily_report.py", "run"], None, 300),
    ("ceo_live_usage", [PY, "scripts/ceo_live_usage.py"], None, 300),
    ("token_meter", [PY, "scripts/token_meter.py"], None, 120),
]
bad = []
for name, cmd, env, to in LEGS:
    t0 = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=to, env=env)
        rc, tail = p.returncode, (p.stdout or "").strip().splitlines()[-1:]
    except subprocess.TimeoutExpired:
        rc, tail = "TIMEOUT", []
    line = "%s rc=%s %.0fs %s" % (name, rc, time.time() - t0, (tail[-1][:110] if tail else ""))
    print(line)
    if str(rc) not in ("0",):
        bad.append(line)
print("S6-LIGHT-DONE bad=%d %s" % (len(bad), "; ".join(bad) if bad else "ALL-RC0"))
