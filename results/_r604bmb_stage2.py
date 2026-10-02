import subprocess, sys, json, glob, os

def git(*args):
    r = subprocess.run(['git'] + list(args), capture_output=True, text=True,
                       encoding='utf-8', errors='replace')
    return r

payload = [
    # bookkeeping trio
    'state.json', 'fleet/machines/bm-b.json', 'logs/iteration-loop/round_reports.md',
    # daemon claim-refresh faces from withdrawn keepalive 1f56beac6 (r598 visibility)
    'results/autofill_state.bm-b.json', 'results/runnable_pool.bm-b.json', 'results/runnable_pool.json',
    # S6 derive faces (round 604)
    'docs/daily_report/REPORT-2026-10-03.json', 'docs/daily_report/REPORT-2026-10-03.md',
    'docs/live_usage/LIVE-2026-10-03.json', 'docs/live_usage/LIVE-2026-10-03.md',
    'docs/live_usage/LIVE-latest.json', 'docs/live_usage/LIVE-latest.md',
    'results/_attrition_guard_scan.json', 'results/astock_daily_update_status.json',
    'results/compute_audit.bm-b.json', 'results/compute_audit.json',
    'results/dashboard_status.js', 'results/dashboard_status.json',
    'results/etf_daily_pull_status.json', 'results/fundamental_b_layer_filter.json',
    'results/futures_update_status.bm-b.json', 'results/futures_update_status.json',
    'results/lhb_update_status.bm-b.json', 'results/lhb_update_status.json',
    'results/pool_dualrun.bm-b.jsonl',
    'results/regime_state.bm-b.json', 'results/regime_state.json',
    'results/scorecard_v1.json', 'results/strategy_scorecard.json',
    'results/token_usage.bm-b.json', 'results/token_usage.json',
    'results/update_status.bm-b.json', 'results/update_status.json',
]
payload += sorted(glob.glob('results/prospect_promotion/PROS-*.json'))
payload += ['results/prospect_promotion/_summary.json']
# round receipts (r604)
payload += sorted(glob.glob('results/_r604bmb_*'))
payload = [p for p in payload if not p.endswith('.log')]   # s6 runner log = gitignored face (r603 precedent)
# T-152 adjudication faces
payload += [
    'scripts/fund_quality_p1_probe.py',
    'fleet/tasks/T-2026-10-03-152-P1.json',
    'fleet/inbox/MSG-2026-10-03-0548-bmb-bmc-t152-amendment-ack.md',
    'fleet/inbox/processed/MSG-2026-10-03-0500-bmc-bmb-t152-median-floor-reality.md',
]

missing = [p for p in payload if not os.path.exists(p)]
if missing:
    print('FATAL missing files:', missing); sys.exit(1)
print('payload size:', len(payload))

r = git('add', '--', *payload)
print('add rc=', r.returncode, r.stderr.strip()[:300])
if r.returncode != 0:
    sys.exit(2)

st = git('status', '--porcelain')
staged = [l for l in st.stdout.splitlines() if l.startswith(('M ', 'A ', 'D ', 'R '))]
print('staged count:', len(staged))
# r385 law: bookkeeping trio present
paths = {l[3:].strip() for l in staged}
need = {'state.json', 'fleet/machines/bm-b.json', 'logs/iteration-loop/round_reports.md'}
miss = need - paths
if miss:
    print('FATAL missing bookkeeping:', miss); sys.exit(3)
print('bookkeeping trio present OK')
# r595/r388 law: no D rows with unpaired inbox moves; audit every D row
drows = [l for l in staged if l.startswith('D ')]
print('staged D rows:', len(drows))
for l in drows:
    print('  D:', l)
# assert probe fix + ticket + MSG staged
for f in ('scripts/fund_quality_p1_probe.py', 'fleet/tasks/T-2026-10-03-152-P1.json',
          'fleet/inbox/MSG-2026-10-03-0548-bmb-bmc-t152-amendment-ack.md'):
    print('in staged:', f, f in paths)
