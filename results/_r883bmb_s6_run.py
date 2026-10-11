# r883 bm-b: S6 maintenance chain driver (38 legs, Sunday no-op heavy)
# pit-encoding law: subprocess capture decode errors='replace'
import subprocess, sys, time, json

LEGS = [
    ("pool_dualrun",   ["python", "scripts\\pool_dualrun_reconcile.py", "run"]),
    ("compute_audit",  ["python", "scripts\\compute_audit.py"]),
    ("py_watermark",   ["python", "scripts\\py_watermark.py", "probe"]),
    ("update_daily",   ["python", "scripts\\update_daily.py"]),
    ("market_regime",  ["python", "scripts\\market_regime.py"]),
    ("strat_scorecard",["python", "scripts\\strategy_scorecard.py"]),
    ("mkt_clock_call", ["python", "scripts\\market_clock_call.py", "run"]),
    ("update_lhb",     ["python", "scripts\\update_lhb.py"]),
    ("update_zt_pool", ["python", "scripts\\update_zt_pool.py"]),
    ("update_heat",    ["python", "scripts\\update_heat.py"]),
    ("update_futures", ["python", "scripts\\update_futures.py"]),
    ("update_repo",    ["python", "scripts\\update_repo.py"]),
    ("update_options", ["python", "scripts\\update_options.py"]),
    ("update_moneyflow",["python","scripts\\update_moneyflow.py"]),
    ("update_sina_mf", ["python", "scripts\\update_sina_mf.py"]),
    ("update_astock",  ["python", "scripts\\update_astock_daily.py"]),
    ("update_etf_daily",["python","scripts\\update_etf_daily.py"]),
    ("regime_thermo",  ["python", "scripts\\regime_thermo_build.py"]),
    ("regime_dualarm", ["python", "scripts\\regime_gate_dualarm.py", "run"]),
    ("rev_osc_export", ["python", "scripts\\rev_osc_signal_export.py", "run"]),
    ("minute_feed",    ["python", "scripts\\update_minute_feed.py"]),
    ("ths_panel",      ["python", "scripts\\update_ths_panel.py"]),
    ("ah_panel",       ["python", "scripts\\ah_panel_puller.py"]),
    ("fund_premium",   ["python", "scripts\\update_fund_premium.py", "snapshot"]),
    ("fundamental",    ["python", "scripts\\update_fundamental.py"]),
    ("b_layer_filter", ["python", "-m", "firm.risk.b_layer_filter"]),
    ("fund_statements",["python", "scripts\\update_fund_statements.py"]),
    ("aggr_lab_paper", ["python", "scripts\\aggressive_lab.py", "paper"]),
    ("alloc_paper",    ["python", "scripts\\alloc_paper.py", "run"]),
    ("grid_paper",     ["python", "scripts\\grid_paper.py", "run"]),
    ("system_v1_paper",["python", "scripts\\system_v1_paper.py", "run"]),
    ("t35_paper_export",["python", "scripts\\t35_paper_export.py", "run"]),
    ("daily_scorecard",["python", "scripts\\daily_scorecard.py"]),
    ("daily_report",   ["python", "scripts\\daily_report.py", "run"]),
    ("ceo_live_usage", ["python", "scripts\\ceo_live_usage.py"]),
    ("build_status",   ["python", "-m", "monitor.build_status"]),
    ("token_meter",    ["python", "scripts\\token_meter.py"]),
]

rows = []
fails = []
for name, cmd in LEGS:
    t0 = time.time()
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=420)
        rc = r.returncode
        tail = (r.stdout or b'').decode('utf-8', errors='replace').strip().splitlines()
        last = tail[-1][:150] if tail else ((r.stderr or b'').decode('utf-8', errors='replace').strip().splitlines() or [''])[-1][:150]
    except subprocess.TimeoutExpired:
        rc, last = 99, 'TIMEOUT 420s'
    except Exception as e:
        rc, last = 98, str(e)[:150]
    dt = round(time.time() - t0, 1)
    flag = 'OK' if rc == 0 else 'FAIL'
    if rc != 0:
        fails.append((name, rc))
    print(f"[{flag}] {name} rc={rc} {dt}s | {last}", flush=True)
    rows.append({"leg": name, "rc": rc, "sec": dt, "tail": last})

with open('results\\_r883bmb_s6_log.jsonl', 'w', encoding='utf-8') as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')

print(f"S6 SUMMARY: {len(rows)} legs, {len(rows)-len(fails)} rc0, fails={fails}", flush=True)
sys.exit(0 if not fails else 2)
