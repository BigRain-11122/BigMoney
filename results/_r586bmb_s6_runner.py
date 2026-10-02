# r586 bm-b S6 maintenance chain runner (sequential, rc capture, lane guards honest no-op)
import subprocess, sys, os, json

R = []
def run(name, args, env_extra=None, timeout=300):
    e = dict(os.environ)
    if env_extra: e.update(env_extra)
    try:
        r = subprocess.run(args, capture_output=True, text=True, timeout=timeout, env=e)
        rc = r.returncode
        tail = (r.stdout or '').strip().splitlines()
        last = tail[-1][:150] if tail else (r.stderr or '').strip()[-150:]
    except subprocess.TimeoutExpired:
        rc = 'TIMEOUT'; last = 'timeout %ss' % timeout
    R.append((name, rc, last))
    print('%-28s rc=%s | %s' % (name, rc, last), flush=True)
    return rc

py = sys.executable

# 1. dualrun reconcile (must precede compute_audit)
run('pool_dualrun_reconcile', [py, 'scripts/pool_dualrun_reconcile.py', 'run'])
# 2. compute audit
run('compute_audit', [py, 'scripts/compute_audit.py'])
# 3. watermark probe
run('py_watermark', [py, 'scripts/py_watermark.py', 'probe'])
# 4. update_daily
run('update_daily', [py, 'scripts/update_daily.py'])
# 5. market regime
run('market_regime', [py, 'scripts/market_regime.py'])
# 6. strategy scorecard (host guard bm-a)
run('strategy_scorecard', [py, 'scripts/strategy_scorecard.py'])
# 7. market clock
run('market_clock_call', [py, 'scripts/market_clock_call.py', 'run'])
# 8-13. bm-a lane collectors (honest no-op on bm-b)
run('update_lhb', [py, 'scripts/update_lhb.py'])
run('update_heat', [py, 'scripts/update_heat.py'])
run('update_futures', [py, 'scripts/update_futures.py'])
run('update_repo', [py, 'scripts/update_repo.py'])
run('update_options', [py, 'scripts/update_options.py'])
run('update_moneyflow', [py, 'scripts/update_moneyflow.py'])
run('update_sina_mf', [py, 'scripts/update_sina_mf.py'])
# 14. astock daily (bm-b lane, may spawn background)
run('update_astock_daily', [py, 'scripts/update_astock_daily.py'])
# 15. etf daily (bm-b lane, 5 members)
run('update_etf_daily', [py, 'scripts/update_etf_daily.py'])
# 16. rev osc export (bm-b lane)
run('rev_osc_signal_export', [py, 'scripts/rev_osc_signal_export.py', 'run'])
# 17. minute feed (bm-b lane)
run('update_minute_feed', [py, 'scripts/update_minute_feed.py'])
# 18-19. bm-a lane
run('update_ths_panel', [py, 'scripts/update_ths_panel.py'])
run('ah_panel_puller', [py, 'scripts/ah_panel_puller.py'])
# 20. bm-c lane
run('update_fund_premium', [py, 'scripts/update_fund_premium.py', 'snapshot'])
# 21-22
run('update_fundamental', [py, 'scripts/update_fundamental.py'])
run('b_layer_filter', [py, '-m', 'firm.risk.b_layer_filter'])

# new-bar gate
p = r'data\daily\sh510300.csv'
with open(p, 'rb') as f:
    f.seek(max(0, os.path.getsize(p) - 300))
    last_bar = f.read().decode('utf-8', 'replace').strip().splitlines()[-1].split(',')[0]
print('LAST_BAR_NOW=' + last_bar, flush=True)
new_bar = last_bar != '2026-09-30'

if new_bar:
    run('live.paper(enforce)', [py, '-m', 'live.paper'], env_extra={'BIGMONEY_REGIME_GUARD': 'enforce'})
    run('t35_open_fill_verify', [py, 'scripts/t35_open_fill_verify.py'])
    run('t24_prospect_paper', [py, 'scripts/t24_prospect_paper.py', 'run'])
    run('t24_prospect_promotion', [py, 'scripts/t24_prospect_promotion.py', 'run'])
else:
    print('new_bar=none -> paper block skipped (honest)', flush=True)

# paper observation accounts (idempotent no-op without new bar)
run('aggressive_lab', [py, 'scripts/aggressive_lab.py', 'paper'])
run('alloc_paper', [py, 'scripts/alloc_paper.py', 'run'])
run('grid_paper', [py, 'scripts/grid_paper.py', 'run'])
run('system_v1_paper', [py, 'scripts/system_v1_paper.py', 'run'])
run('t35_paper_export', [py, 'scripts/t35_paper_export.py', 'run'])
# ceo faces (host guards where applicable)
run('daily_scorecard', [py, 'scripts/daily_scorecard.py'])
run('daily_report', [py, 'scripts/daily_report.py', 'run'])
run('ceo_live_usage', [py, 'scripts/ceo_live_usage.py'])
run('build_status', [py, '-m', 'monitor.build_status'])
run('token_meter', [py, 'scripts/token_meter.py'])

bad = [(n, rc) for n, rc, _ in R if rc not in (0,)]
print('=== S6 SUMMARY: %d legs, anomalies=%s' % (len(R), bad if bad else 'NONE'), flush=True)
json.dump([{'step': n, 'rc': rc, 'last': l} for n, rc, l in R],
          open('results/_r586bmb_s6_chain.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
