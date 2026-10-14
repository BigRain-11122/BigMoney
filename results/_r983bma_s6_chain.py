# -*- coding: utf-8 -*-
# r983 bm-a (clone of r980bmc per reuse-law) S6 maintenance chain batch runner (per-leg exit capture, tolerant of lane-host no-ops)
import subprocess, sys, os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable

legs = [
    ("dualrun",   [PY, "scripts\\pool_dualrun_reconcile.py", "run"], None),
    ("comp_audit",[PY, "scripts\\compute_audit.py"], None),
    ("py_wm",     [PY, "scripts\\py_watermark.py", "probe"], None),
    ("upd_daily", [PY, "scripts\\update_daily.py"], None),
    ("regime",    [PY, "scripts\\market_regime.py"], None),
    ("scorecard", [PY, "scripts\\strategy_scorecard.py"], None),
    ("mkt_clock", [PY, "scripts\\market_clock_call.py", "run"], None),
    ("lhb",       [PY, "scripts\\update_lhb.py"], None),
    ("zt_pool",   [PY, "scripts\\update_zt_pool.py"], None),
    ("heat",      [PY, "scripts\\update_heat.py"], None),
    ("futures",   [PY, "scripts\\update_futures.py"], None),
    ("repo_panel",[PY, "scripts\\update_repo.py"], None),
    ("options",   [PY, "scripts\\update_options.py"], None),
    ("moneyflow", [PY, "scripts\\update_moneyflow.py"], None),
    ("sina_mf",   [PY, "scripts\\update_sina_mf.py"], None),
    ("astock",    [PY, "scripts\\update_astock_daily.py"], None),
    ("etf_daily", [PY, "scripts\\update_etf_daily.py"], None),
    ("thermo",    [PY, "scripts\\regime_thermo_build.py"], None),
    ("dualarm",   [PY, "scripts\\regime_gate_dualarm.py", "run"], None),
    ("rev_osc",   [PY, "scripts\\rev_osc_signal_export.py", "run"], None),
    ("min_feed",  [PY, "scripts\\update_minute_feed.py"], None),
    ("ths_panel", [PY, "scripts\\update_ths_panel.py"], None),
    ("ah_panel",  [PY, "scripts\\ah_panel_puller.py"], None),
    ("fund_prem", [PY, "scripts\\update_fund_premium.py", "snapshot"], None),
    ("fundamental",[PY, "scripts\\update_fundamental.py"], None),
    ("b_layer",   [PY, "-m", "firm.risk.b_layer_filter"], None),
    ("fund_stmt", [PY, "scripts\\update_fund_statements.py"], None),
    ("live_paper",[PY, "-m", "live.paper"], "enforce"),
    ("t35_open",  [PY, "scripts\\t35_open_fill_verify.py"], "enforce"),
    ("t24_paper", [PY, "scripts\\t24_prospect_paper.py", "run"], "enforce"),
    ("t24_promo", [PY, "scripts\\t24_prospect_promotion.py", "run"], "enforce"),
    ("aggr_lab",  [PY, "scripts\\aggressive_lab.py", "paper"], "enforce"),
    ("alloc",     [PY, "scripts\\alloc_paper.py", "run"], "enforce"),
    ("grid_paper",[PY, "scripts\\grid_paper.py", "run"], "enforce"),
    ("sys_v1",    [PY, "scripts\\system_v1_paper.py", "run"], "enforce"),
    ("t35_export",[PY, "scripts\\t35_paper_export.py", "run"], "enforce"),
    ("daily_sc",  [PY, "scripts\\daily_scorecard.py"], None),
    ("daily_rep", [PY, "scripts\\daily_report.py", "run"], None),
    ("ceo_usage", [PY, "scripts\\ceo_live_usage.py"], None),
    ("build_stat",[PY, "-m", "monitor.build_status"], None),
    ("token_m",   [PY, "scripts\\token_meter.py"], None),
]

results = []
for name, cmd, env_flag in legs:
    env = dict(os.environ)
    if env_flag:
        env["BIGMONEY_REGIME_GUARD"] = env_flag
    try:
        r = subprocess.run(cmd, cwd=REPO, capture_output=True, env=env, timeout=300)
        out = (r.stdout or b"").decode("utf-8", "replace").strip().splitlines()
        err = (r.stderr or b"").decode("utf-8", "replace").strip().splitlines()
        last = out[-1] if out else ("ERR:" + err[-1] if err else "(silent)")
        rc = r.returncode
    except subprocess.TimeoutExpired:
        last, rc = "TIMEOUT-300s", 124
    results.append((name, rc, last))
    print(f"LEG {name} exit={rc} | {last[:170]}")

bad = [(n, rc, l) for n, rc, l in results if rc not in (0, 1)]
print(f"CHAIN DONE: {len(results)} legs, non-0/1 exits: {len(bad)}")
for n, rc, l in bad:
    print(f"  RED {n} exit={rc} | {l[:170]}")
