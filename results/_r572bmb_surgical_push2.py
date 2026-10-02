import subprocess, os, sys

REPO = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
PAYLOAD = [
    'results/p2cal_ext/n1_w74/shard-10-of-12.json',
    'results/p2cal_ext/n1_w74/shard-11-of-12.json',
    'results/_r572bmb_surgical_push.py',
    'results/_r572bmb_sync_faces.py',
    'results/_r572bmb_sync_checkout.py',
]
MSG = 'r572 bm-b: W74 shards 10+11 engine-burned products (audit bm-b verified, 12/12 complete) + r572 surgical/sync tools'

def git(args, env=None):
    return subprocess.run(['git', '-C', REPO] + args, capture_output=True, env=env)

r = git(['fetch', 'origin'])
assert r.returncode == 0, r.stderr.decode('utf-8', 'replace')
base = git(['rev-parse', 'origin/main']).stdout.decode().strip()
print('BASE=' + base)

idx = os.path.join(REPO, '.git', 'surgical-index-r572b')
env = dict(os.environ, GIT_INDEX_FILE=idx)
if os.path.exists(idx):
    os.remove(idx)
r = git(['read-tree', base], env=env)
assert r.returncode == 0, r.stderr.decode('utf-8', 'replace')

for p in PAYLOAD:
    h = git(['hash-object', '-w', p], env=env)
    assert h.returncode == 0, h.stderr.decode('utf-8', 'replace')
    sha = h.stdout.decode().strip()
    r = git(['update-index', '--add', '--cacheinfo', '100644,' + sha + ',' + p], env=env)
    assert r.returncode == 0, r.stderr.decode('utf-8', 'replace')
    print('STAGED %s %s' % (sha[:12], p))

tree = git(['write-tree'], env=env)
assert tree.returncode == 0, tree.stderr.decode('utf-8', 'replace')
tree_sha = tree.stdout.decode().strip()

d = git(['diff-index', '--cached', '--name-status', base], env=env)
lines = [l for l in d.stdout.decode('utf-8', 'replace').splitlines() if l.strip()]
adds = [l for l in lines if l.startswith('A')]
dels = [l for l in lines if l.startswith('D')]
mods = [l for l in lines if l.startswith('M')]
print('DIFF adds=%d dels=%d mods=%d' % (len(adds), len(dels), len(mods)))
assert len(adds) == len(PAYLOAD), 'payload mismatch: %s' % lines
assert len(dels) == 0, 'DELETION SET NON-EMPTY (r519 law): %s' % dels
assert len(mods) == 0, 'unexpected mods: %s' % mods

commit = git(['commit-tree', tree_sha, '-p', base, '-m', MSG], env=env)
assert commit.returncode == 0, commit.stderr.decode('utf-8', 'replace')
csha = commit.stdout.decode().strip()
print('COMMIT=' + csha)

p = git(['push', 'origin', csha + ':refs/heads/main'])
if p.returncode != 0:
    print('PUSH_REJECTED: ' + p.stderr.decode('utf-8', 'replace')[:400])
    sys.exit(2)
print('PUSHED')

git(['fetch', 'origin'])
ls = git(['ls-tree', 'origin/main'] + PAYLOAD)
n = len([l for l in ls.stdout.decode().splitlines() if l.strip()])
print('DELIVERY_COUNT=%d' % n)
assert n == len(PAYLOAD), 'delivery incomplete'
# completeness gate for W74 (r310): 12/12 shards on origin
ls74 = git(['ls-tree', 'origin/main', 'results/p2cal_ext/n1_w74/'])
c74 = len([l for l in ls74.stdout.decode().splitlines() if l.strip()])
print('W74_ORIGIN_SHARDS=%d' % c74)
assert c74 == 12, 'W74 completeness gate FAIL: %d/12' % c74
print('W74_COMPLETE_12_OF_12')
os.remove(idx)
