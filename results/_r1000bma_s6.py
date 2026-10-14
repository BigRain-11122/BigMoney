# -*- coding: utf-8 -*-
"""r1000 bm-a S6 chain driver (32 legs, log-to-file, exit-code capture).
Runs the standing maintenance chain per the S6 SOP order; each leg's
stdout/stderr tee'd to results/_r1000bma_s6_chain.log; nonzero rc (except
documented no-op/guarded exits recorded verbatim) counted as bad.
"""
import subprocess, sys, os, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(ROOT, 'results', '_r1000bma_s6_chain.log')
PY = sys.executable

LEGS = [
    ("pool_dualrun_reconcile", [PY, "scripts/pool_dualrun_reconcile.py", "run"], None),
    ("compute_audit", [PY, "scripts/compute_audit.py"], None),
    ("py_watermark", [PY, "scripts/py_watermark.py", "probe"], None),
    ("update_daily", [PY, "scripts/update_daily.py"], None),
    ("market_regime", [PY, "scripts/market_regime.py"], None),
    ("strategy_scorecard", [PY, "scripts/strategy_scorecard.py"], None),
    ("market_clock_call", [PY, "scripts/market_clock_call.py", "run"], None),
    ("update_lhb", [PY, "scripts/update_lhb.py"], None),
    ("update_zt_pool", [PY, "scripts/update_zt_pool.py"], None),
    ("update_heat", [PY, "scripts/update_heat.py"], None),
    ("update_futures", [PY, "scripts/update_futures.py"], None),
    ("update_repo", [PY, "scripts/update_repo.py"], None),
    ("update_options", [PY, "scripts/update_options.py"], None),
    ("update_moneyflow", [PY, "scripts/update_moneyflow.py"], None),
    ("update_sina_mf", [PY, "scripts/update_sina_mf.py"], None),
    # update_astock_daily / update_etf_daily: bm-b lane (R31) -> honest stdout-only no-op on bm-a, still run for exit-code
    ("update_astock_daily(bmb-lane)", [PY, "scripts/update_astock_daily.py"], None),
    ("update_etf_daily(bmb-lane)", [PY, "scripts/update_etf_daily.py"], None),
    ("regime_thermo_build", [PY, "scripts/regime_thermo_build.py"], None),
    ("regime_gate_dualarm(bmb-lane)", [PY, "scripts/regime_gate_dualarm.py", "run"], None),
    ("rev_osc_signal_export(bmb-lane)", [PY, "scripts/rev_osc_signal_export.py", "run"], None),
    ("update_minute_feed(bmb-lane)", [PY, "scripts/update_minute_feed.py"], None),
    ("update_ths_panel", [PY, "scripts/update_ths_panel.py"], None),
    ("ah_panel_puller", [PY, "scripts/ah_panel_puller.py"], None),
    ("update_fund_premium(bmc-lane)", [PY, "scripts/update_fund_premium.py", "snapshot"], None),
    ("update_fundamental", [PY, "scripts/update_fundamental.py"], None),
    ("b_layer_filter", [PY, "-m", "firm.risk.b_layer_filter"], None),
    ("update_fund_statements", [PY, "scripts/update_fund_statements.py"], None),
    ("t35_open_fill_verify", [PY, "scripts/t35_open_fill_verify.py"], None),
    ("t24_prospect_paper", [PY, "scripts/t24_prospect_paper.py", "run"], None),
    ("t24_prospect_promotion", [PY, "scripts/t24_prospect_promotion.py", "run"], None),
    ("aggressive_lab_paper", [PY, "scripts/aggressive_lab.py", "paper"], None),
    ("alloc_paper", [PY, "scripts/alloc_paper.py", "run"], None),
    ("grid_paper", [PY, "scripts/grid_paper.py", "run"], None),
    ("system_v1_paper", [PY, "scripts/system_v1_paper.py", "run"], None),
    ("t35_paper_export", [PY, "scripts/t35_paper_export.py", "run"], None),
    ("daily_scorecard", [PY, "scripts/daily_scorecard.py"], None),
    ("daily_report", [PY, "scripts/daily_report.py", "run"], None),
    ("ceo_live_usage", [PY, "scripts/ceo_live_usage.py"], None),
    ("build_status", [PY, "-m", "monitor.build_status"], None),
    ("token_meter", [PY, "scripts/token_meter.py"], None),
]

log = open(LOG, 'w', encoding='utf-8', newline='\n')
bad = []
t0 = time.time()
for i, (name, cmd, env) in enumerate(LEGS, 1):
    log.write(f"\n=== leg {i}/{len(LEGS)} {name} start {time.strftime('%H:%M:%S')} ===\n")
    log.flush()
    try:
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, timeout=600,
                           env={**os.environ, **(env or {})})
        out = (r.stdout or b'').decode('utf-8', 'replace')
        err = (r.stderr or b'').decode('utf-8', 'replace')
        tail = (out.strip().splitlines() or [''])[-1]
        log.write(out[-2000:] + ("\n[stderr] " + err[-800:] if err.strip() else "") + "\n")
        log.write(f"=== leg {i} {name} rc={r.returncode} tail={tail[:180]} ===\n")
        if r.returncode != 0:
            bad.append(f"{name} rc={r.returncode}")
    except Exception as e:
        log.write(f"EXC {name}: {e}\n")
        bad.append(f"{name} EXC {type(e).__name__}")
    log.flush()
log.write(f"\nCHAIN DONE legs={len(LEGS)} bad={len(bad)} elapsed={time.time()-t0:.0f}s\n")
log.close()
print(f"S6 chain: {len(LEGS)} legs, bad={len(bad)}: {bad}")
print("log:", LOG)
