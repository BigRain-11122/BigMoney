# -*- coding: utf-8 -*-
"""r872 bm-a S6 chain driver -- runs the maintenance legs in protocol order,
captures exit codes + compact stdout. Bar-conditioned legs self-no-op
pre-15:30 (no new bar today yet). Lane-guarded legs (bm-b/bm-c ownership)
self-no-op on bm-a per R31."""
import subprocess, sys, io, json, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

LEGS = [
    ("dualrun",      ["python", "scripts\\pool_dualrun_reconcile.py", "run"]),
    ("compute_audit",["python", "scripts\\compute_audit.py"]),
    ("watermark",    ["python", "scripts\\py_watermark.py", "probe"]),
    ("update_daily", ["python", "scripts\\update_daily.py"]),
    ("regime",       ["python", "scripts\\market_regime.py"]),
    ("scorecard",    ["python", "scripts\\strategy_scorecard.py"]),
    ("clock_call",   ["python", "scripts\\market_clock_call.py", "run"]),
    ("lhb",          ["python", "scripts\\update_lhb.py"]),
    ("zt_pool",      ["python", "scripts\\update_zt_pool.py"]),
    ("heat",         ["python", "scripts\\update_heat.py"]),
    ("futures",      ["python", "scripts\\update_futures.py"]),
    ("repo",         ["python", "scripts\\update_repo.py"]),
    ("options",      ["python", "scripts\\update_options.py"]),
    ("moneyflow",    ["python", "scripts\\update_moneyflow.py"]),
    ("sina_mf",      ["python", "scripts\\update_sina_mf.py"]),
    ("astock_daily", ["python", "scripts\\update_astock_daily.py"]),
    ("etf_daily",    ["python", "scripts\\update_etf_daily.py"]),
    ("rev_osc",      ["python", "scripts\\rev_osc_signal_export.py", "run"]),
    ("minute_feed",  ["python", "scripts\\update_minute_feed.py"]),
    ("ths_panel",    ["python", "scripts\\update_ths_panel.py"]),
    ("ah_panel",     ["python", "scripts\\ah_panel_puller.py"]),
    ("fund_premium", ["python", "scripts\\update_fund_premium.py", "snapshot"]),
    ("fundamental",  ["python", "scripts\\update_fundamental.py"]),
    ("b_layer",      ["python", "-m", "firm.risk.b_layer_filter"]),
    ("fund_stmts",   ["python", "scripts\\update_fund_statements.py"]),
    ("paper_live",   ["python", "-m", "live.paper"]),
    ("t35_openfill", ["python", "scripts\\t35_open_fill_verify.py"]),
    ("t24_prospects",["python", "scripts\\t24_prospect_paper.py", "run"]),
    ("t24_promotion",["python", "scripts\\t24_prospect_promotion.py", "run"]),
    ("aggr_paper",   ["python", "scripts\\aggressive_lab.py", "paper"]),
    ("alloc_paper",  ["python", "scripts\\alloc_paper.py", "run"]),
    ("grid_paper",   ["python", "scripts\\grid_paper.py", "run"]),
    ("sysv1_paper",  ["python", "scripts\\system_v1_paper.py", "run"]),
    ("t35_export",   ["python", "scripts\\t35_paper_export.py", "run"]),
    ("daily_score",  ["python", "scripts\\daily_scorecard.py"]),
    ("daily_report", ["python", "scripts\\daily_report.py", "run"]),
    ("ceo_live",     ["python", "scripts\\ceo_live_usage.py"]),
    ("build_status", ["python", "-m", "monitor.build_status"]),
    ("token_meter",  ["python", "scripts\\token_meter.py"]),
    ("attrition",    ["python", "scripts\\attrition_ledger_guard.py", "scan"]),
]

env_note = None
results = []
t0 = time.time()
for name, cmd in LEGS:
    t1 = time.time()
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8',
                       errors='replace', timeout=900)
    dt = time.time() - t1
    out = (r.stdout or '').strip().splitlines()
    tail = out[-1][:110] if out else ''
    results.append({'leg': name, 'rc': r.returncode, 'sec': round(dt, 1), 'tail': tail})
    print(f"{name:14s} rc={r.returncode} {dt:6.1f}s {tail}")
    if r.returncode not in (0,):
        # show more for failures
        err = (r.stderr or '').strip().splitlines()
        for e in err[-4:]:
            print('   ERR:', e[:150])

print(f"\nchain done in {time.time()-t0:.0f}s")
bad = [x for x in results if x['rc'] != 0]
print("FAILURES:", [(x['leg'], x['rc']) for x in bad] if bad else "NONE")
io.open(r'results\_r872bma_s6_chain.json', 'w', encoding='utf-8').write(
    json.dumps(results, ensure_ascii=False, indent=1))
