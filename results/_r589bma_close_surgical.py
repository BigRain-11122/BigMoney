# -*- coding: utf-8 -*-
"""r589 bm-a closing surgical push: payload = my closing commit (HEAD) minus
11 shared-derived faces resolved take-origin (newest committed; AA resolver
disclosure per r499 family). Host/lane=bm-a faces stay MINE (scorecard family
+ dashboard + lhb/futures lane faces -- my post-W107-finalize derives are the
current science face; bm-c r380's writes were legal r378 stale-takeover from
a pre-W107 view). Deletion-set must stay EMPTY; tree-delta == payload.
"""
import subprocess, sys, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(REPO)
CREAT = 0x08000000

def run(cmd, input=None, check=True):
    r = subprocess.run(cmd, capture_output=True, input=input)
    if check and r.returncode != 0:
        sys.exit('FAIL %s\n%s' % (cmd[:4], r.stderr.decode('utf-8', 'replace')[-500:]))
    return r.stdout

run(['git', 'fetch', 'origin'])
ORIGIN = run(['git', 'rev-parse', 'origin/main']).decode().strip()
MINE = run(['git', 'rev-parse', 'HEAD']).decode().strip()
print('origin:', ORIGIN[:9], '| mine:', MINE[:9])

TAKE_ORIGIN = {
    'docs/daily_report/REPORT-2026-10-02.json', 'docs/daily_report/REPORT-2026-10-02.md',
    'docs/live_usage/LIVE-2026-10-02.json', 'docs/live_usage/LIVE-2026-10-02.md',
    'docs/live_usage/LIVE-latest.json', 'docs/live_usage/LIVE-latest.md',
    'results/compute_audit.json', 'results/regime_state.json',
    'results/token_usage.json', 'results/update_status.json',
}
mine_names = set(run(['git', 'diff', '--name-only', MINE + '^', MINE]).decode().split())
# drop no-op faces (my blob == origin blob -> staging changes nothing);
# files absent from origin tree = additions, always kept
effective = []
for p in sorted(mine_names - TAKE_ORIGIN):
    a = run(['git', 'rev-parse', MINE + ':' + p]).decode().strip()
    rb = subprocess.run(['git', 'rev-parse', ORIGIN + ':' + p], capture_output=True)
    if rb.returncode != 0:
        effective.append(p)          # addition
        continue
    if a != rb.stdout.decode().strip():
        effective.append(p)           # genuine modification
payload = effective
print('payload:', len(payload), '(take-origin dropped:', len(mine_names & TAKE_ORIGIN),
      '| no-op identical dropped:', len((mine_names - TAKE_ORIGIN)) - len(payload), ')')

IDX = os.path.join(REPO, '.git', 'surgical_idx_r589b')
env = dict(os.environ, GIT_INDEX_FILE=IDX)
def ridx(cmd, input=None, check=True):
    r = subprocess.run(cmd, capture_output=True, input=input, env=env)
    if check and r.returncode != 0:
        sys.exit('FAIL %s\n%s' % (cmd[:5], r.stderr.decode('utf-8', 'replace')[-500:]))
    return r.stdout

ridx(['git', 'read-tree', ORIGIN])
origin_files = set(ridx(['git', 'ls-files']).decode().split())
for p in payload:
    out = run(['git', 'ls-tree', MINE, '--', p]).decode().strip()
    assert out, 'payload missing from my commit: ' + p
    meta = out.split('\t')[0].split()
    mode, typ, sha = meta[0], meta[1], meta[2]
    assert typ == 'blob'
    ridx(['git', 'update-index', '--add', '--cacheinfo', f'{mode},{sha},{p}'])
print('payload staged')

TREE = ridx(['git', 'write-tree']).decode().strip()
new_files = set(ridx(['git', 'ls-files']).decode().split())
deletions = origin_files - new_files
assert not deletions, 'DELETION SET NON-EMPTY: %s' % sorted(deletions)[:8]
delta = set(ridx(['git', 'diff-tree', '--name-only', '-r', ORIGIN, TREE]).decode().split())
assert delta == set(payload), 'TREE DELTA MISMATCH: %s' % sorted(delta ^ set(payload))
print('deletion-set EMPTY | tree-delta == payload:', len(delta))

MSG = ('r589 bm-a closing surgical push (origin advanced bm-c r380 mid-window: T-144(c) data-domain split + '
       'closeout; payload = closing commit %s minus 10 shared-derived faces resolved take-origin-newest per '
       'r499 AA family -- daily report / live usage / compute_audit / regime_state / token_usage / update_status; '
       'host+lane=bm-a faces kept mine (strategy_scorecard / scorecard_v1 / dashboard_status x2 / '
       'fundamental_b_layer_filter / lhb / futures status -- my post-W107-finalize derives are the current '
       'science face; bm-c r380 writes were legal r378 stale-takeover from a pre-W107 view, disclosed); '
       'deletion-set EMPTY + tree-delta==payload asserted; W110 12/12 + W107 finalize products + wrap ride. '
       '[via bm-a r589]') % MINE[:9]
SHA = run(['git', 'commit-tree', TREE, '-p', ORIGIN], input=MSG.encode()).decode().strip()
run(['git', 'merge-base', '--is-ancestor', ORIGIN, SHA])
print('new commit:', SHA)
r = subprocess.run(['git', 'push', 'origin', SHA + ':refs/heads/main'], capture_output=True)
print('push rc:', r.returncode)
print((r.stdout + r.stderr).decode('utf-8', 'replace')[-300:])
if r.returncode != 0:
    sys.exit(1)
run(['git', 'fetch', 'origin'])
now = run(['git', 'rev-parse', 'origin/main']).decode().strip()
print('delivered:', now == SHA, '|', now[:9])
# local realign (r578): move ref, reset --mixed, restore stale faces, keep live-write
run(['git', 'update-ref', 'refs/heads/main', SHA])
run(['git', 'reset', '--mixed', SHA])
out = run(['git', 'status', '--porcelain']).decode('utf-8', 'replace')
restore, keep = [], []
for line in out.splitlines():
    if not line.strip():
        continue
    st, path = line[:2], line[3:].strip().strip('"')
    if st.endswith('D'):
        restore.append(path)
        continue
    if st.endswith('M'):
        r2 = subprocess.run(['git', 'diff', '--quiet', MINE, '--', path], capture_output=True)
        if r2.returncode == 0:
            restore.append(path)
        else:
            keep.append(path)
print('restore:', len(restore), '| live-write keep:', len(keep))
for k in keep:
    print('  KEEP', k)
if restore:
    run(['git', 'checkout', SHA, '--'] + restore)
out2 = run(['git', 'status', '--porcelain']).decode('utf-8', 'replace')
print('post-realign dirty:')
print(out2.strip())
