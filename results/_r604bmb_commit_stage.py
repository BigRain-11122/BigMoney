import subprocess, sys

adds = [
    'state.json',
    'fleet/machines/bm-b.json',
    'logs/iteration-loop/round_reports.md',
    'results/_r604bmb_s6_runner.ps1',
    'results/_r604bmb_hb_refresh.py',
    'docs/daily_report/REPORT-2026-10-03.json',
    'docs/daily_report/REPORT-2026-10-03.md',
    'docs/live_usage/LIVE-2026-10-03.json',
    'docs/live_usage/LIVE-2026-10-03.md',
    'docs/live_usage/LIVE-latest.json',
    'docs/live_usage/LIVE-latest.md',
    'results/_attrition_guard_scan.json',
    'results/astock_daily_update_status.json',
    'results/compute_audit.bm-b.json',
    'results/compute_audit.json',
    'results/dashboard_status.js',
    'results/dashboard_status.json',
    'results/etf_daily_pull_status.json',
    'results/fundamental_b_layer_filter.json',
    'results/futures_update_status.bm-b.json',
    'results/futures_update_status.json',
    'results/lhb_update_status.bm-b.json',
    'results/lhb_update_status.json',
    'results/pool_dualrun.bm-b.jsonl',
    'results/prospect_promotion/PROS-ANTS-01.json',
    'results/prospect_promotion/PROS-ANTS-CE-01.json',
    'results/prospect_promotion/PROS-BBS-01.json',
    'results/prospect_promotion/PROS-BBS-CE-01.json',
    'results/prospect_promotion/PROS-DOJI-01.json',
    'results/prospect_promotion/PROS-DOJI-CE-01.json',
    'results/prospect_promotion/PROS-DUCK-01.json',
    'results/prospect_promotion/PROS-DUCK-CE-01.json',
    'results/prospect_promotion/PROS-HAM-01.json',
    'results/prospect_promotion/PROS-HAM-CE-01.json',
    'results/prospect_promotion/PROS-IBB-01.json',
    'results/prospect_promotion/PROS-IBB-CE-01.json',
    'results/prospect_promotion/PROS-IMM-01.json',
    'results/prospect_promotion/PROS-IMM-CE-01.json',
    'results/prospect_promotion/PROS-MCB-01.json',
    'results/prospect_promotion/PROS-MCB-CE-01.json',
    'results/prospect_promotion/PROS-OVB-01.json',
    'results/prospect_promotion/PROS-OVB-CE-01.json',
    'results/prospect_promotion/PROS-RSRS-CE-01.json',
    'results/prospect_promotion/PROS-TMU-01.json',
    'results/prospect_promotion/PROS-TMU-CE-01.json',
    'results/prospect_promotion/PROS-VOB-CE-01.json',
    'results/prospect_promotion/_summary.json',
    'results/regime_state.bm-b.json',
    'results/regime_state.json',
    'results/scorecard_v1.json',
    'results/strategy_scorecard.json',
    'results/token_usage.bm-b.json',
    'results/token_usage.json',
    'results/update_status.bm-b.json',
    'results/update_status.json',
]

r = subprocess.run(['git', 'add', '--'] + adds, capture_output=True, text=True,
                    encoding='utf-8', errors='replace')
print('add rc=', r.returncode)
if r.stdout.strip():
    print('stdout:', r.stdout.strip()[:500])
if r.returncode != 0:
    print('stderr:', r.stderr.strip()[:1000])
    sys.exit(1)

st = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True,
                    encoding='utf-8', errors='replace')
staged = [l for l in st.stdout.splitlines() if l and l[1] not in (' ', '?') and l[0] != '?']
staged = [l for l in st.stdout.splitlines() if l.startswith(('M ', 'A ', 'D ', 'R '))]
print('staged count:', len(staged))
for l in staged:
    print(' ', l)
# r385 law: assert bookkeeping trio present in staged set before commit
paths = {l[3:].strip() for l in staged}
need = {'state.json', 'fleet/machines/bm-b.json', 'logs/iteration-loop/round_reports.md'}
missing = need - paths
if missing:
    print('MISSING BOOKKEEPING:', missing)
    sys.exit(1)
print('bookkeeping trio present OK')
