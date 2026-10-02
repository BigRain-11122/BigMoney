# -*- coding: utf-8 -*-
# r385 bm-c S6 chain runner (Golden Week: paper block honest skip per r588/r592/r595 precedent)
import subprocess, os
os.chdir(r'K:\Fluxgroup\FluxGroup\quant\bigmoney')
NW = 0x08000000
LEGS = [
    ('dualrun', ['scripts\\pool_dualrun_reconcile.py', 'run'], 300),
    ('compute_audit', ['scripts\\compute_audit.py'], 240),
    ('py_watermark', ['scripts\\py_watermark.py', 'probe'], 240),
    ('update_daily', ['scripts\\update_daily.py'], 300),
    ('market_regime', ['scripts\\market_regime.py'], 180),
    ('strategy_scorecard', ['scripts\\strategy_scorecard.py'], 180),
    ('market_clock_call', ['scripts\\market_clock_call.py', 'run'], 180),
    ('update_lhb', ['scripts\\update_lhb.py'], 240),
    ('update_heat', ['scripts\\update_heat.py'], 240),
    ('update_futures', ['scripts\\update_futures.py'], 240),
    ('update_repo', ['scripts\\update_repo.py'], 240),
    ('update_options', ['scripts\\update_options.py'], 240),
    ('update_moneyflow', ['scripts\\update_moneyflow.py'], 240),
    ('update_sina_mf', ['scripts\\update_sina_mf.py'], 240),
    ('update_astock_daily', ['scripts\\update_astock_daily.py'], 240),
    ('update_etf_daily', ['scripts\\update_etf_daily.py'], 240),
    ('rev_osc_signal_export', ['scripts\\rev_osc_signal_export.py', 'run'], 180),
    ('update_minute_feed', ['scripts\\update_minute_feed.py'], 240),
    ('update_ths_panel', ['scripts\\update_ths_panel.py'], 240),
    ('ah_panel_puller', ['scripts\\ah_panel_puller.py'], 240),
    ('update_fund_premium', ['scripts\\update_fund_premium.py', 'snapshot'], 300),
    ('update_fundamental', ['scripts\\update_fundamental.py'], 300),
    ('b_layer_filter', ['-m', 'firm.risk.b_layer_filter'], 240),
    ('daily_scorecard', ['scripts\\daily_scorecard.py'], 180),
    ('daily_report', ['scripts\\daily_report.py', 'run'], 240),
    ('ceo_live_usage', ['scripts\\ceo_live_usage.py'], 240),
    ('build_status', ['-m', 'monitor.build_status'], 180),
    ('token_meter', ['scripts\\token_meter.py'], 120),
]
bad = []
for i, (name, args, to) in enumerate(LEGS, 1):
    try:
        r = subprocess.run(['python', '-X', 'utf8'] + args, capture_output=True, timeout=to, creationflags=NW)
        rc = r.returncode
        out = (r.stdout or b'').decode('utf-8', 'replace').strip()
        err = (r.stderr or b'').decode('utf-8', 'replace').strip()
    except subprocess.TimeoutExpired:
        rc, out, err = 'TIMEOUT', '', ''
    tail = (out or err).splitlines()[-1][:160] if (out or err) else ''
    print('LEG %02d %-22s rc=%s | %s' % (i, name, rc, tail))
    if rc != 0:
        bad.append((name, rc, tail))
print('S6 SUMMARY: legs=%d rc0=%d nonzero=%d' % (len(LEGS), len(LEGS) - len(bad), len(bad)))
for b in bad:
    print('NONZERO: %s rc=%s %s' % b)
