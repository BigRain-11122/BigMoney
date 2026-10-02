# r588 bm-b S6 driver: maintenance chain legs, exit codes to log (Golden Week face: no new bar)
import subprocess, sys, time

LEGS = [
    ['python', 'scripts/pool_dualrun_reconcile.py', 'run'],
    ['python', 'scripts/compute_audit.py'],
    ['python', 'scripts/py_watermark.py', 'probe'],
    ['python', 'scripts/update_daily.py'],
    ['python', 'scripts/market_regime.py'],
    ['python', 'scripts/strategy_scorecard.py'],
    ['python', 'scripts/market_clock_call.py', 'run'],
    ['python', 'scripts/update_lhb.py'],
    ['python', 'scripts/update_heat.py'],
    ['python', 'scripts/update_futures.py'],
    ['python', 'scripts/update_repo.py'],
    ['python', 'scripts/update_options.py'],
    ['python', 'scripts/update_moneyflow.py'],
    ['python', 'scripts/update_sina_mf.py'],
    ['python', 'scripts/update_astock_daily.py'],
    ['python', 'scripts/update_etf_daily.py'],
    ['python', 'scripts/rev_osc_signal_export.py', 'run'],
    ['python', 'scripts/update_minute_feed.py'],
    ['python', 'scripts/update_ths_panel.py'],
    ['python', 'scripts/ah_panel_puller.py'],
    ['python', 'scripts/update_fund_premium.py', 'snapshot'],
    ['python', 'scripts/update_fundamental.py'],
    ['python', '-m', 'firm.risk.b_layer_filter'],
    ['python', 'scripts/aggressive_lab.py', 'paper'],
    ['python', 'scripts/alloc_paper.py', 'run'],
    ['python', 'scripts/grid_paper.py', 'run'],
    ['python', 'scripts/system_v1_paper.py', 'run'],
    ['python', 'scripts/t35_paper_export.py', 'run'],
    ['python', 'scripts/daily_scorecard.py'],
    ['python', 'scripts/daily_report.py', 'run'],
    ['python', 'scripts/ceo_live_usage.py'],
    ['python', '-m', 'monitor.build_status'],
    ['python', 'scripts/token_meter.py'],
]

fails = 0
t0 = time.time()
for leg in LEGS:
    ts = time.strftime('%H:%M:%S')
    r = subprocess.run(leg, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=600)
    tail = (r.stdout or '').strip().splitlines()
    last = tail[-1][:160] if tail else ''
    err = (r.stderr or '').strip().splitlines()
    lasterr = err[-1][:160] if err else ''
    print(f'[{ts}] rc={r.returncode} {" ".join(leg[1:])} :: {last}' + (f' :: ERR {lasterr}' if r.returncode != 0 else ''), flush=True)
    if r.returncode != 0:
        fails += 1
print(f'S6 driver done: {len(LEGS)} legs, {fails} nonzero rc, {time.time()-t0:.0f}s')
sys.exit(1 if fails else 0)
