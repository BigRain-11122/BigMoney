# -*- coding: utf-8 -*-
# r396 bm-c S6 chain runner (full 37 legs incl. paper family; detached + per-leg flush log per r324/r385 precedent)
import subprocess, os, sys, time
os.chdir(r'K:\Fluxgroup\FluxGroup\quant\bigmoney')
NW = 0x08000000
LOG = os.path.join('results', '_r396bmc_s6_log.txt')

def log(msg):
    with open(LOG, 'a', encoding='utf-8') as fh:
        fh.write(msg + '\n')
        fh.flush()

LEGS = [
    ('pool_dualrun_reconcile', ['scripts\\pool_dualrun_reconcile.py', 'run'], 300, None),
    ('compute_audit', ['scripts\\compute_audit.py'], 240, None),
    ('py_watermark', ['scripts\\py_watermark.py', 'probe'], 240, None),
    ('update_daily', ['scripts\\update_daily.py'], 300, None),
    ('market_regime', ['scripts\\market_regime.py'], 180, None),
    ('strategy_scorecard', ['scripts\\strategy_scorecard.py'], 240, None),
    ('market_clock_call', ['scripts\\market_clock_call.py', 'run'], 180, None),
    ('update_lhb', ['scripts\\update_lhb.py'], 300, None),
    ('update_heat', ['scripts\\update_heat.py'], 300, None),
    ('update_futures', ['scripts\\update_futures.py'], 300, None),
    ('update_repo', ['scripts\\update_repo.py'], 600, None),
    ('update_options', ['scripts\\update_options.py'], 300, None),
    ('update_moneyflow', ['scripts\\update_moneyflow.py'], 300, None),
    ('update_sina_mf', ['scripts\\update_sina_mf.py'], 300, None),
    ('update_astock_daily', ['scripts\\update_astock_daily.py'], 300, None),
    ('update_etf_daily', ['scripts\\update_etf_daily.py'], 300, None),
    ('rev_osc_signal_export', ['scripts\\rev_osc_signal_export.py', 'run'], 180, None),
    ('update_minute_feed', ['scripts\\update_minute_feed.py'], 300, None),
    ('update_ths_panel', ['scripts\\update_ths_panel.py'], 300, None),
    ('ah_panel_puller', ['scripts\\ah_panel_puller.py'], 600, None),
    ('update_fund_premium', ['scripts\\update_fund_premium.py', 'snapshot'], 300, None),
    ('update_fundamental', ['scripts\\update_fundamental.py'], 600, None),
    ('b_layer_filter', ['-m', 'firm.risk.b_layer_filter'], 240, None),
    ('live_paper', ['-m', 'live.paper'], 300, {'BIGMONEY_REGIME_GUARD': 'enforce'}),
    ('t35_open_fill_verify', ['scripts\\t35_open_fill_verify.py'], 180, None),
    ('t24_prospect_paper', ['scripts\\t24_prospect_paper.py', 'run'], 300, None),
    ('t24_prospect_promotion', ['scripts\\t24_prospect_promotion.py', 'run'], 300, None),
    ('aggressive_lab_paper', ['scripts\\aggressive_lab.py', 'paper'], 300, None),
    ('alloc_paper', ['scripts\\alloc_paper.py', 'run'], 300, None),
    ('grid_paper', ['scripts\\grid_paper.py', 'run'], 300, None),
    ('system_v1_paper', ['scripts\\system_v1_paper.py', 'run'], 300, None),
    ('t35_paper_export', ['scripts\\t35_paper_export.py', 'run'], 180, None),
    ('daily_scorecard', ['scripts\\daily_scorecard.py'], 180, None),
    ('daily_report', ['scripts\\daily_report.py', 'run'], 300, None),
    ('ceo_live_usage', ['scripts\\ceo_live_usage.py'], 300, None),
    ('build_status', ['-m', 'monitor.build_status'], 180, None),
    ('token_meter', ['scripts\\token_meter.py'], 120, None),
]

def main():
    log('=== r396 bm-c S6 chain start %s legs=%d ===' % (time.strftime('%Y-%m-%d %H:%M:%S'), len(LEGS)))
    bad = []
    for i, (name, args, to, extra_env) in enumerate(LEGS, 1):
        env = dict(os.environ)
        if extra_env:
            env.update(extra_env)
        t0 = time.time()
        try:
            r = subprocess.run(['python', '-X', 'utf8'] + args, capture_output=True,
                               timeout=to, creationflags=NW, env=env)
            rc = r.returncode
            out = (r.stdout or b'').decode('utf-8', 'replace').strip()
            err = (r.stderr or b'').decode('utf-8', 'replace').strip()
        except subprocess.TimeoutExpired:
            rc, out, err = 'TIMEOUT', '', ''
        sec = round(time.time() - t0, 1)
        tail = (out or err).splitlines()[-1][:200] if (out or err) else ''
        log('=== %s rc=%s %.1fs | %s' % (name, rc, sec, tail))
        if rc != 0:
            bad.append((name, rc))
    log('S6 SUMMARY: legs=%d rc0=%d nonzero=%d %s' % (
        len(LEGS), len(LEGS) - len(bad), len(bad), 'ALL-RC0' if not bad else 'BAD=' + str(bad)))
    return 0

if __name__ == '__main__':
    sys.exit(main())
