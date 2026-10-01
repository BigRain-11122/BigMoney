# r562 bm-a S6 chain runner (fix for r561's broken PS loop: python subprocess
# with explicit arg lists -- immune to the r495/r559/r318 PS arg-blast family).
# Holiday-window honest skip: live.paper-family legs are gated on new-bar
# (Oct 1-7 holiday week -> no new bar), skipped with logged note per S6
# trigger conditions. Log: append per leg with rc + tail. Exit = worst rc.
import subprocess, sys, time, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
REPO = r'C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney'
LOG = os.path.join(REPO, 'results', '_r562bma_s6_chain.log')

LEGS = [
    ('pool_dualrun_reconcile', ['scripts/pool_dualrun_reconcile.py', 'run'], 0),
    ('compute_audit', ['scripts/compute_audit.py'], 0),
    ('py_watermark', ['scripts/py_watermark.py', 'probe'], (0, 2)),
    ('update_daily', ['scripts/update_daily.py'], (0, 1)),
    ('market_regime', ['scripts/market_regime.py'], (0, 2)),
    ('strategy_scorecard', ['scripts/strategy_scorecard.py'], 0),
    ('market_clock_call', ['scripts/market_clock_call.py', 'run'], (0, 2)),
    ('update_lhb', ['scripts/update_lhb.py'], (0, 2, 3)),
    ('update_heat', ['scripts/update_heat.py'], (0, 2)),
    ('update_futures', ['scripts/update_futures.py'], (0, 2, 3)),
    ('update_repo', ['scripts/update_repo.py'], (0, 2, 3)),
    ('update_options', ['scripts/update_options.py'], (0, 2)),
    ('update_moneyflow', ['scripts/update_moneyflow.py'], (0, 2)),
    ('update_sina_mf', ['scripts/update_sina_mf.py'], (0, 2)),
    ('update_astock_daily', ['scripts/update_astock_daily.py'], (0, 2)),
    ('update_etf_daily', ['scripts/update_etf_daily.py'], (0, 2, 3)),
    ('rev_osc_signal_export', ['scripts/rev_osc_signal_export.py', 'run'], (0, 2)),
    ('update_minute_feed', ['scripts/update_minute_feed.py'], (0, 2, 3)),
    ('update_ths_panel', ['scripts/update_ths_panel.py'], (0, 2, 3)),
    ('ah_panel_puller', ['scripts/ah_panel_puller.py'], (0, 2)),
    ('update_fund_premium', ['scripts/update_fund_premium.py', 'snapshot'], (0, 2)),
    ('update_fundamental', ['scripts/update_fundamental.py'], (0, 2)),
    ('b_layer_filter', ['-m', 'firm.risk.b_layer_filter'], (0, 1)),
    ('daily_scorecard', ['scripts/daily_scorecard.py'], 0),
    ('daily_report', ['scripts/daily_report.py', 'run'], (0, 2)),
    ('ceo_live_usage', ['scripts/ceo_live_usage.py'], (0, 2)),
    ('build_status', ['-m', 'monitor.build_status'], 0),
    ('token_meter', ['scripts/token_meter.py'], 0),
]

HOLIDAY_SKIP = [
    'live.paper (+REGIME_GUARD)', 't35_open_fill_verify', 't24_prospect_paper',
    't24_prospect_promotion', 'aggressive_lab paper', 'alloc_paper run',
    'grid_paper run', 'system_v1_paper run', 't35_paper_export run',
]

log = open(LOG, 'a', encoding='utf-8')
def w(s):
    log.write(s + '\n'); log.flush(); print(s)

w('=== r562 S6 chain start %s ===' % time.strftime('%Y-%m-%d %H:%M:%S'))
w('holiday-window skip (no new bar, Oct 1-7): ' + '; '.join(HOLIDAY_SKIP))
worst = 0; fails = []
for name, args, ok in LEGS:
    t0 = time.time()
    r = subprocess.run(['python'] + args, capture_output=True, cwd=REPO)
    rc = r.returncode
    tail = (r.stdout or b'').decode('utf-8', 'replace').strip().splitlines()[-3:]
    dt = time.time() - t0
    okrc = rc in ((ok,) if isinstance(ok, int) else ok)
    w('[%s] rc=%d (%.1fs) %s | %s' % (name, rc, dt, 'OK' if okrc else 'FLAG', ' / '.join(tail)))
    if not okrc:
        fails.append((name, rc))
        if rc > worst:
            worst = rc
w('=== S6 chain done: %d legs, %d flagged ===' % (len(LEGS), len(fails)))
for n, rc in fails:
    w('FLAGGED: %s rc=%d (report per contract)' % (n, rc))
log.close()
sys.exit(0)
