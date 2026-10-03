"""r427 bm-c S6 chain driver: maintenance legs in order, anomalies reported verbatim.
PYTHONUTF8=1 persisted (r425 leg-8 GBK crash fix). Lane guards make non-bm-c
owner legs honest no-ops. live.paper/t35-fill/t24-prospect-paper skipped: no new
bar (golden week, last bar 2026-09-30).
"""
import os
import subprocess

os.environ["PYTHONUTF8"] = "1"
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
    ['python', 'scripts/update_fundamental.py'],
    ['python', '-m', 'firm.risk.b_layer_filter'],
    ['python', 'scripts/t24_prospect_promotion.py', 'run'],
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

anomalies = []
for leg in LEGS:
    name = ' '.join(leg[1:])
    try:
        r = subprocess.run(leg, capture_output=True, text=True, encoding='utf-8',
                           errors='replace', timeout=600,
                           env=dict(os.environ))
        rc = r.returncode
        tail = (r.stdout or '').strip().splitlines()
        last = tail[-1] if tail else ''
        print('%-42s rc=%d %s' % (name[:42], rc, last[:110]))
        if rc != 0:
            anomalies.append((name, rc, '\n'.join((r.stdout or '').splitlines()[-8:]),
                               '\n'.join((r.stderr or '').splitlines()[-8:])))
    except subprocess.TimeoutExpired:
        print('%-42s TIMEOUT' % name[:42])
        anomalies.append((name, 'TIMEOUT', '', ''))

print('\n=== ANOMALIES (rc!=0, report verbatim) ===' if anomalies
      else '\n=== ALL LEGS rc=0 ===')
for name, rc, out, err in anomalies:
    print('---', name, 'rc=', rc)
    if out:
        print(out)
    if err:
        print('STDERR:', err)
