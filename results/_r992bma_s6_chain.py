"""r992 bm-a S6 maintenance chain (detached, self-logging per 10-14 pit law).
Runs each leg via subprocess, records exit codes + output tails to the log.
Paper/marks legs activate only if today's bar (2026-10-14) landed in the
core daily panel (post-15:30 catch). Lane-guarded legs self-no-op honestly.
"""
import subprocess, sys, os, json, datetime

LOG = r'C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney\results\_r992bma_s6_chain.log'
def w(s):
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(s + '\n')

if sys.stdout:
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

w('=== r992 bm-a S6 chain start %s ===' % datetime.datetime.now().isoformat(timespec='seconds'))
TODAY = '2026-10-14'
os.chdir(r'C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney')
env = dict(os.environ)
env['PYTHONIOENCODING'] = 'utf-8'

LEGS = [
    ['python', 'scripts\\pool_dualrun_reconcile.py', 'run'],
    ['python', 'scripts\\compute_audit.py'],
    ['python', 'scripts\\py_watermark.py', 'probe'],
    ['python', 'scripts\\update_daily.py'],
    ['python', 'scripts\\market_regime.py'],
    ['python', 'scripts\\strategy_scorecard.py'],
    ['python', 'scripts\\market_clock_call.py', 'run'],
    ['python', 'scripts\\update_lhb.py'],
    ['python', 'scripts\\update_zt_pool.py'],
    ['python', 'scripts\\update_heat.py'],
    ['python', 'scripts\\update_futures.py'],
    ['python', 'scripts\\update_repo.py'],
    ['python', 'scripts\\update_options.py'],
    ['python', 'scripts\\update_moneyflow.py'],
    ['python', 'scripts\\update_sina_mf.py'],
    ['python', 'scripts\\update_astock_daily.py'],
    ['python', 'scripts\\update_etf_daily.py'],
    ['python', 'scripts\\regime_thermo_build.py'],
    ['python', 'scripts\\regime_gate_dualarm.py', 'run'],
    ['python', 'scripts\\rev_osc_signal_export.py', 'run'],
    ['python', 'scripts\\update_minute_feed.py'],
    ['python', 'scripts\\update_ths_panel.py'],
    ['python', 'scripts\\ah_panel_puller.py'],
    ['python', 'scripts\\update_fund_premium.py', 'snapshot'],
    ['python', 'scripts\\update_fundamental.py'],
    ['python', '-m', 'firm.risk.b_layer_filter'],
    ['python', 'scripts\\update_fund_statements.py'],
]

bad = []
for leg in LEGS:
    name = ' '.join(leg[1:]) or leg[0]
    try:
        r = subprocess.run(leg, capture_output=True, env=env, timeout=600)
        rc = r.returncode
        tail = (r.stdout or b'')[-300:].decode('utf-8', 'replace').strip()
        w('[%s] exit=%d | %s' % (name, rc, tail.replace('\n', ' | ')))
        if rc not in (0,):
            bad.append((name, rc))
    except Exception as e:
        w('[%s] EXC %s' % (name, e))
        bad.append((name, 'EXC'))

# new-bar gate for paper/marks legs
new_bar = False
try:
    p = r'data\daily\sh510300.csv'
    if os.path.exists(p):
        with open(p, encoding='utf-8', errors='replace') as f:
            last = [l for l in f if l.strip()][-1]
        new_bar = last.startswith(TODAY)
except Exception as e:
    w('bar-check EXC %s' % e)
w('new_bar_today=%s' % new_bar)

if new_bar:
    penv = dict(env)
    penv['BIGMONEY_REGIME_GUARD'] = 'enforce'
    PAPER_LEGS = [
        ['python', '-m', 'live.paper'],
        ['python', 'scripts\\t35_open_fill_verify.py'],
        ['python', 'scripts\\t24_prospect_paper.py', 'run'],
        ['python', 'scripts\\t24_prospect_promotion.py', 'run'],
        ['python', 'scripts\\aggressive_lab.py', 'paper'],
        ['python', 'scripts\\alloc_paper.py', 'run'],
        ['python', 'scripts\\grid_paper.py', 'run'],
        ['python', 'scripts\\system_v1_paper.py', 'run'],
        ['python', 'scripts\\t35_paper_export.py', 'run'],
    ]
    for leg in PAPER_LEGS:
        name = ' '.join(leg[1:]) or leg[0]
        try:
            r = subprocess.run(leg, capture_output=True, env=penv, timeout=900)
            w('[paper:%s] exit=%d | %s' % (name, r.returncode,
                (r.stdout or b'')[-300:].decode('utf-8', 'replace').strip().replace('\n', ' | ')))
            if r.returncode != 0:
                bad.append(('paper:' + name, r.returncode))
        except Exception as e:
            w('[paper:%s] EXC %s' % (name, e))
            bad.append(('paper:' + name, 'EXC'))

CEO_LEGS = [
    ['python', 'scripts\\daily_scorecard.py'],
    ['python', 'scripts\\daily_report.py', 'run'],
    ['python', 'scripts\\ceo_live_usage.py'],
    ['python', '-m', 'monitor.build_status'],
    ['python', 'scripts\\token_meter.py'],
]
for leg in CEO_LEGS:
    name = ' '.join(leg[1:]) or leg[0]
    try:
        r = subprocess.run(leg, capture_output=True, env=env, timeout=600)
        w('[ceo:%s] exit=%d | %s' % (name, r.returncode,
            (r.stdout or b'')[-300:].decode('utf-8', 'replace').strip().replace('\n', ' | ')))
        if r.returncode != 0:
            bad.append(('ceo:' + name, r.returncode))
    except Exception as e:
        w('[ceo:%s] EXC %s' % (name, e))
        bad.append(('ceo:' + name, 'EXC'))

w('=== chain done %s | bad=%d %s ===' % (datetime.datetime.now().isoformat(timespec='seconds'),
    len(bad), json.dumps(bad, ensure_ascii=False)))
