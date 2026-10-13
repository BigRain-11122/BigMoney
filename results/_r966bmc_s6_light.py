# -*- coding: utf-8 -*-
"""r966 bm-c S6 light chain (pre-15:30 Tuesday window: bars not landed yet for today).
Runs the standing collectors sequentially with lane guards honest no-op; reports rc per leg.
Exit codes 2/3 must surface honestly (never masked)."""
import subprocess, sys, time
sys.stdout.reconfigure(encoding="utf-8")
PY = sys.executable
LEGS = [
    ("dualrun", [PY, "scripts/pool_dualrun_reconcile.py", "run"], 120),
    ("compute_audit", [PY, "scripts/compute_audit.py"], 120),
    ("wm_probe", [PY, "scripts/py_watermark.py", "probe"], 120),
    ("update_daily", [PY, "scripts/update_daily.py"], 300),
    ("market_regime", [PY, "scripts/market_regime.py"], 120),
    ("market_clock", [PY, "scripts/market_clock_call.py", "run"], 120),
    ("update_lhb", [PY, "scripts/update_lhb.py"], 300),
    ("update_zt_pool", [PY, "scripts/update_zt_pool.py"], 300),
    ("update_heat", [PY, "scripts/update_heat.py"], 300),
    ("update_futures", [PY, "scripts/update_futures.py"], 300),
    ("update_repo", [PY, "scripts/update_repo.py"], 300),
    ("update_options", [PY, "scripts/update_options.py"], 120),
    ("update_moneyflow", [PY, "scripts/update_moneyflow.py"], 120),
    ("update_sina_mf", [PY, "scripts/update_sina_mf.py"], 120),
    ("update_astock_daily", [PY, "scripts/update_astock_daily.py"], 120),
    ("update_etf_daily", [PY, "scripts/update_etf_daily.py"], 120),
    ("regime_thermo", [PY, "scripts/regime_thermo_build.py"], 300),
    ("regime_gate_dualarm", [PY, "scripts/regime_gate_dualarm.py", "run"], 120),
    ("rev_osc_export", [PY, "scripts/rev_osc_signal_export.py", "run"], 120),
    ("update_minute_feed", [PY, "scripts/update_minute_feed.py"], 120),
    ("update_ths_panel", [PY, "scripts/update_ths_panel.py"], 120),
    ("ah_panel", [PY, "scripts/ah_panel_puller.py"], 120),
    ("fund_premium", [PY, "scripts/update_fund_premium.py", "snapshot"], 300),
    ("fundamental", [PY, "scripts/update_fundamental.py"], 300),
    ("b_layer", [PY, "-m", "firm.risk.b_layer_filter"], 120),
    ("fund_statements", [PY, "scripts/update_fund_statements.py"], 120),
    ("t24_prospect", [PY, "scripts/t24_prospect_paper.py", "run"], 300),
    ("t24_promotion", [PY, "scripts/t24_prospect_promotion.py", "run"], 300),
    ("aggr_paper", [PY, "scripts/aggressive_lab.py", "paper"], 300),
    ("alloc_paper", [PY, "scripts/alloc_paper.py", "run"], 300),
    ("grid_paper", [PY, "scripts/grid_paper.py", "run"], 300),
    ("system_v1_paper", [PY, "scripts/system_v1_paper.py", "run"], 300),
    ("t35_export", [PY, "scripts/t35_paper_export.py", "run"], 300),
    ("daily_report", [PY, "scripts/daily_report.py", "run"], 300),
    ("ceo_live_usage", [PY, "scripts/ceo_live_usage.py"], 300),
    ("token_meter", [PY, "scripts/token_meter.py"], 120),
]
bad = []
for name, cmd, to in LEGS:
    t0 = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=to)
        rc, tail = p.returncode, (p.stdout or "").strip().splitlines()[-1:] 
    except subprocess.TimeoutExpired:
        rc, tail = "TIMEOUT", []
    line = "%s rc=%s %.0fs %s" % (name, rc, time.time() - t0, (tail[-1][:110] if tail else ""))
    print(line)
    if str(rc) not in ("0",):
        bad.append(line)
print("S6-LIGHT-DONE bad=%d %s" % (len(bad), "; ".join(bad) if bad else "ALL-RC0"))
