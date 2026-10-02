import subprocess, os, sys

REPO = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
PAYLOAD = [
    'results/p2cal_ext/n1_w74/shard-8-of-12.json',
    'results/p2cal_ext/n1_w74/shard-9-of-12.json',
    'results/_r572bmb_verify_shards.py',
]
MSG = 'r572 bm-b: W74 shards 8+9 engine-burned products (audit bm-b verified), pre-finalize delivery (surgical, dirty-lane window)'

def git(args, **kw):
    return subprocess.run(['git', '-C', REPO] + args, capture_output=True, **kw)

r = git(['fetch', 'origin'])
assert r.returncode == 0, r.stderr.decode('utf-8', 'replace')
base = git(['rev-parse', 'origin/main']).stdout.decode().strip()
print('BASE=' + base)

idx = os.path.join(REPO, '.git', 'surgical-index-r572')
env = dict(os.environ, GIT_INDEX_FILE=idx)
if os.path.exists(idx):
    os.remove(idx)
r = subprocess.run(['git', '-C', REPO, 'read-tree', base], capture_output=True, env=env)
assert r.returncode == 0, r.stderr.decode('utf-8', 'replace')

for p in PAYLOAD:
    full = os.path.join(REPO, p)
    h = subprocess.run(['git', '-C', REPO, 'hash-object', '-w', p], capture_output=True, env=env)
    assert h.returncode == 0, h.stderr.decode('utf-8', 'replace')
    sha = h.stdout.decode().strip()
    r = subprocess.run(['git', '-C', REPO, 'update-index', '--add', '--cacheinfo', '100644,' + sha + ',' + p],
                       capture_output=True, env=env)
    assert r.returncode == 0, r.stderr.decode('utf-8', 'replace')
    print('STAGED %s %s' % (sha[:12], p))

tree = subprocess.run(['git', '-C', REPO, 'write-tree'], capture_output=True, env=env)
assert tree.returncode == 0, tree.stderr.decode('utf-8', 'replace')
tree_sha = tree.stdout.decode().strip()

# r343: diff-index MUST use --cached; r530: deletion-set assertion; r516: payload count assertion
d = subprocess.run(['git', '-C', REPO, 'diff-index', '--cached', '--name-status', base],
                   capture_output=True, env=env, text=True)
lines = [l for l in d.stdout.splitlines() if l.strip()]
adds = [l for l in lines if l.startswith('A')]
dels = [l for l in lines if l.startswith('D')]
mods = [l for l in lines if l.startswith('M')]
print('DIFF adds=%d dels=%d mods=%d' % (len(adds), len(dels), len(mods)))
assert len(adds) == len(PAYLOAD), 'payload count mismatch: %s' % lines
assert len(dels) == 0, 'DELETION SET NON-EMPTY (r519 law): %s' % dels
assert len(mods) == 0, 'unexpected modifications: %s' % mods

commit = subprocess.run(['git', '-C', REPO, 'commit-tree', tree_sha, '-p', base, '-m', MSG],
                         capture_output=True, env=env)
assert commit.returncode == 0, commit.stderr.decode('utf-8', 'replace')
csha = commit.stdout.decode().strip()
print('COMMIT=' + csha)

p = git(['push', 'origin', csha + ':refs/heads/main'])
if p.returncode != 0:
    print('PUSH_REJECTED: ' + p.stderr.decode('utf-8', 'replace')[:400])
    sys.exit(2)
print('PUSHED')

# delivery verification (r531/r516): ls-tree assertions on origin after fetch
git(['fetch', 'origin'])
new = git(['rev-parse', 'origin/main']).stdout.decode().strip()
print('NEW_ORIGIN=' + new)
ls = git(['ls-tree', 'origin/main'] + PAYLOAD)
out = ls.stdout.decode()
print('DELIVERY_COUNT=' + str(len([l for l in out.splitlines() if l.strip()])))
assert len([l for l in out.splitlines() if l.strip()]) == len(PAYLOAD), 'delivery incomplete'
print('DELIVERY_OK')
os.remove(idx)
