# -*- coding: utf-8 -*-
"""r590 bm-a surgical push of the W112 freeze commit e867471ed onto origin 07e8b2ebc.
Payload = the 11 freeze files (zero overlap with bm-b's two finalize commits).
Assertions: deletion-set EMPTY + tree-delta == payload (r523 law)."""
import subprocess, sys, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREAT = 0x08000000

def run(args, **kw):
    r = subprocess.run(args, cwd=REPO, capture_output=True, creationflags=CREAT, **kw)
    return r

MINE = 'e867471ed'
run(['git', 'fetch', 'origin'])
ORIGIN = run(['git', 'rev-parse', 'origin/main']).stdout.decode().strip()
print('origin:', ORIGIN)

# payload file list from my commit
diff = run(['git', 'diff', '--name-status', ORIGIN, MINE]).stdout.decode('utf-8')
raw = []
for ln in diff.splitlines():
    st, p = ln.split('\t')
    raw.append((st, p))
# stale-base artifacts: files my local base never had (landed on origin after
# my base commit) show as D vs MINE but are NOT deletion intent -- the surgical
# index starts from the ORIGIN tree so they stay. Real payload = M/A only.
stale_d = [p for st, p in raw if st == 'D']
payload = [(st, p) for st, p in raw if st != 'D']
for p in stale_d:
    o = run(['git', 'ls-tree', ORIGIN, '--', p]).stdout.decode().strip()
    assert o, f'stale-base D entry not on origin: {p} (real deletion? ABORT)'
print('stale-base D artifacts (kept from origin tree):', stale_d)
print('payload files:')
for st, p in payload:
    print(' ', st, p)
deletions = [p for st, p in payload if st == 'D']
assert not deletions, f'DELETION-SET not empty: {deletions}'

# temp index: origin tree + my blobs
idx = os.path.join(REPO, '.codely-cli', 'scratch', 'idx_r590_freeze')
env = dict(os.environ, GIT_INDEX_FILE=idx)
run(['git', 'read-tree', ORIGIN], env=env)
for st, p in payload:
    sha = run(['git', 'rev-parse', f'{MINE}:{p}'], env=env).stdout.decode().strip()
    mode = run(['git', 'ls-tree', MINE, '--', p], env=env).stdout.decode().split()[0]
    r = run(['git', 'update-index', '--add', '--cacheinfo', f'{mode},{sha},{p}'], env=env)
    assert r.returncode == 0, r.stderr.decode()
tree = run(['git', 'write-tree'], env=env).stdout.decode().strip()
print('tree:', tree)

# assertions: tree-delta vs origin == payload exactly
d2 = run(['git', 'diff', '--name-status', ORIGIN, tree]).stdout.decode('utf-8')
got = sorted(ln.split('\t')[1] for ln in d2.splitlines())
want = sorted(p for _, p in payload)
assert got == want, f'tree-delta != payload: {set(got) ^ set(want)}'
print(f'assert OK: tree-delta == payload ({len(want)} files), deletion-set EMPTY')

sha = run(['git', 'commit-tree', tree, '-p', ORIGIN,
           '-F', os.path.join(REPO, '.codely-cli', 'scratch', 'msg_r590_freeze.txt')],
          env=env).stdout.decode().strip()
print('surgical commit:', sha)
r = run(['git', 'push', 'origin', f'{sha}:main'], env=env)
print('push rc:', r.returncode, r.stdout.decode()[-200:], r.stderr.decode()[-200:])
sys.exit(r.returncode)
