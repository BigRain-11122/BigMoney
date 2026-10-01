# r520 bm-a S6 chain batch (fast legs; gated network legs self-no-op intraday)
import subprocess, sys, hashlib

ROOT = r'C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney'

def run(name, args, timeout=120):
    try:
        p = subprocess.run([sys.executable] + args, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
        tail = (p.stdout or '').strip().splitlines()[-1][:80] if (p.stdout or '').strip() else ''
        err = (p.stderr or '').strip().splitlines()[-1][:80] if (p.stderr or '').strip() else ''
        print(f'{name}: rc={p.returncode} | {tail}' + (f' | ERR: {err}' if p.returncode != 0 and err else ''))
    except subprocess.TimeoutExpired:
        print(f'{name}: TIMEOUT({timeout}s)')

# D-19 decisions watermark (r292 raw-bytes law, r503 upper-normalize law)
dec = subprocess.check_output(['git','-C',r'C:\Users\sjs20\Desktop\FluxGroup','show','origin/main:docs/decisions.md'])
sha = hashlib.sha256(dec).hexdigest().upper()
print(f'D-19 decisions sha: {sha[:16]} (state key: 753F99E8...)')

run('dualrun', ['scripts\\pool_dualrun_reconcile.py','run'])
run('compute_audit', ['scripts\\compute_audit.py'])
run('py_watermark', ['scripts\\py_watermark.py','probe'])
run('update_daily', ['scripts\\update_daily.py'])
run('market_regime', ['scripts\\market_regime.py'])
run('strategy_scorecard', ['scripts\\strategy_scorecard.py'])
run('market_clock_call', ['scripts\\market_clock_call.py','run'])
run('update_lhb', ['scripts\\update_lhb.py'])
run('update_heat', ['scripts\\update_heat.py'])
run('update_futures', ['scripts\\update_futures.py'])
run('update_repo', ['scripts\\update_repo.py'])
run('update_options', ['scripts\\update_options.py'])
run('update_moneyflow', ['scripts\\update_moneyflow.py'])
run('update_sina_mf', ['scripts\\update_sina_mf.py'])
run('update_astock_daily', ['scripts\\update_astock_daily.py'])
run('update_etf_daily', ['scripts\\update_etf_daily.py'])
run('rev_osc_export', ['scripts\\rev_osc_signal_export.py','run'])
run('minute_feed', ['scripts\\update_minute_feed.py'])
run('ths_panel', ['scripts\\update_ths_panel.py'])
run('ah_panel', ['scripts\\ah_panel_puller.py'])
run('fund_premium', ['scripts\\update_fund_premium.py','snapshot'])
run('fundamental', ['scripts\\update_fundamental.py'])
run('b_layer_filter', ['-m','firm.risk.b_layer_filter'])
run('aggr_paper', ['scripts\\aggressive_lab.py','paper'])
run('alloc_paper', ['scripts\\alloc_paper.py','run'])
run('grid_paper', ['scripts\\grid_paper.py','run'])
run('system_v1_paper', ['scripts\\system_v1_paper.py','run'])
run('t35_export', ['scripts\\t35_paper_export.py','run'])
run('daily_scorecard', ['scripts\\daily_scorecard.py'])
run('daily_report', ['scripts\\daily_report.py','run'])
run('ceo_live_usage', ['scripts\\ceo_live_usage.py'])
run('build_status', ['-m','monitor.build_status'])
run('token_meter', ['scripts\\token_meter.py'])
