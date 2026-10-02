# -*- coding: utf-8 -*-
"""r589 bm-a surgical push: W110 freeze payload onto advanced origin/main.

Context: local commit 1699ff61e (W110 five-face freeze) built on ad932f6b8;
origin advanced to 7ade4d28a (bm-b r588: W106 finalize landed + W109 12/12
delivered + W110 seat archived). Tracked engine live-write files present in
the worktree -> rebase forbidden (r532 law) -> surgical payload path (r523).
Payload = my commit's ls-tree blobs MINUS the attrition scan evidence file
(intersection with origin's r588; keep origin side, both verdicts CLEAN,
re-derived every scan). Deletion-set must be empty (pre-push claw parity).
"""
import subprocess, sys, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREAT = 0x08000000

def run(cmd, input=None):
    r = subprocess.run(cmd, capture_output=True, input=input)
    if r.returncode != 0:
        sys.exit('FAIL %s\n%s' % (cmd[:4], r.stderr.decode('utf-8', 'replace')[-500:]))
    return r.stdout

os.chdir(REPO)
run(['git', 'fetch', 'origin'])
ORIGIN = run(['git', 'rev-parse', 'origin/main']).decode().strip()
MINE = '1699ff61e'
print('origin/main:', ORIGIN)

# payload = my commit's touched files, minus the origin-side-kept intersection
mine_names = set(run(['git', 'diff', '--name-only', MINE + '^', MINE]).decode().split())
drop = {'results/_attrition_guard_scan.json'}
payload = sorted(mine_names - drop)
print('payload files:', len(payload))

# temp index = origin tree
IDX = os.path.join(REPO, '.git', 'surgical_idx_r589')
env = dict(os.environ, GIT_INDEX_FILE=IDX)
def ridx(cmd, input=None):
    r = subprocess.run(cmd, capture_output=True, input=input, env=env)
    if r.returncode != 0:
        sys.exit('FAIL %s\n%s' % (cmd[:5], r.stderr.decode('utf-8', 'replace')[-500:]))
    return r.stdout

ridx(['git', 'read-tree', ORIGIN])
origin_tree_files = set(ridx(['git', 'ls-files']).decode().split())

# stage payload blobs from MY commit (ls-tree blob sha, explicit columns r366 law)
for p in payload:
    out = run(['git', 'ls-tree', MINE, '--', p]).decode()
    line = out.strip()
    assert line, 'payload file not in my commit: ' + p
    parts = line.split('\t')
    meta = parts[0].split()          # [mode, type, sha] then TAB path (r366 explicit columns)
    mode, typ, sha = meta[0], meta[1], meta[2]
    assert typ == 'blob', 'non-blob payload: ' + p
    ridx(['git', 'update-index', '--add', '--cacheinfo', f'{mode},{sha},{p}'])
print('payload staged from my commit blobs')

TREE = ridx(['git', 'write-tree']).decode().strip()
print('tree:', TREE)

# deletion-set assertion: origin files minus new tree must be EMPTY
new_files = set(ridx(['git', 'ls-files']).decode().split())
deletions = origin_tree_files - new_files
assert not deletions, 'DELETION SET NON-EMPTY: %s' % sorted(deletions)[:8]
print('deletion-set: EMPTY (pre-push claw parity)')

# tree-delta assertion: new tree vs origin == payload exactly
delta = set(ridx(['git', 'diff-tree', '--name-only', '-r', ORIGIN, TREE]).decode().split())
assert delta == set(payload), 'TREE DELTA MISMATCH: %s vs payload' % sorted(delta ^ set(payload))
print('tree-delta == payload:', len(delta), 'files exact')

MSG = ('r589 bm-a W110 freeze surgical push (origin advanced bm-b r588 mid-window: W106 finalize landed '
       'chain head 597,748 K=231,120 + W109 12/12 delivered + my W110 seat archived consumed; '
       'payload = 1699ff61e five-face freeze 13 files minus attrition scan evidence kept origin-side '
       'both-CLEAN re-derived-every-scan; live-write rebase forbidden r532 -> r523 surgical; '
       'deletion-set EMPTY + tree-delta==payload asserted; W110 prereg sec.5 anchor=W105 draft-window '
       'latest-landed per r576 -- W106 landed mid-window after draft, disclosed, runtime finalize '
       'FAIL-CLOSED derives from registry keys r307). [via bm-a r589]')
SHA = run(['git', 'commit-tree', TREE, '-p', ORIGIN], input=MSG.encode()).decode().strip()
print('new commit:', SHA)

# pre-push verify: FF from origin
run(['git', 'merge-base', '--is-ancestor', ORIGIN, SHA])
print('FF check ok (origin is ancestor)')

r = subprocess.run(['git', 'push', 'origin', SHA + ':refs/heads/main'],
                   capture_output=True)
print('push rc:', r.returncode)
print((r.stdout + r.stderr).decode('utf-8', 'replace')[-400:])
if r.returncode != 0:
    sys.exit(1)
# delivery self-verify (O-20261001-1108)
run(['git', 'fetch', 'origin'])
now = run(['git', 'rev-parse', 'origin/main']).decode().strip()
print('origin/main now:', now, '| delivered:', now == SHA)
