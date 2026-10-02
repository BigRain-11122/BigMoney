import subprocess, os, sys

REPO = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
ADDS = [
    'results/perpetual_faces/n1_w74_results.json',
    'results/_r572bmb_w74_backfill_extract.py',
    'results/_r572bmb_w74_gates.py',
    'results/_r572bmb_w74_backfill.py',
]
MODS = ['research/PERPETUAL_N1_W74_PREREG.md']
PAYLOAD = ADDS + MODS
MSG = 'r572 bm-b: W74 FINALIZE one-pass (prev 525,148 W73 bm-a + 2,200 = 527,348 net head, K=160,720, S5 4/4, skill_line 1.1642, r538 no-rerun) + prereg s7/s8 mechanical backfill (r307 two-state green)'

def git(args, env=None):
    return subprocess.run(['git', '-C', REPO] + args, capture_output=True, env=env)

r = git(['fetch', 'origin'])
assert r.returncode == 0, r.stderr.decode('utf-8', 'replace')
base = git(['rev-parse', 'origin/main']).stdout.decode().strip()
print('BASE=' + base)

idx = os.path.join(REPO, '.git', 'surgical-index-r572c')
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
tree_sha = tree.stdout.decode().strip()
assert tree.returncode == 0, tree.stderr.decode('utf-8', 'replace')

d = git(['diff-index', '--cached', '--name-status', base], env=env)
lines = [l for l in d.stdout.decode('utf-8', 'replace').splitlines() if l.strip()]
adds = [l.split('\t')[-1] for l in lines if l.startswith('A')]
mods = [l.split('\t')[-1] for l in lines if l.startswith('M')]
dels = [l for l in lines if l.startswith('D')]
print('DIFF adds=%d mods=%d dels=%d' % (len(adds), len(mods), len(dels)))
assert sorted(adds) == sorted(ADDS), 'adds mismatch: %s' % adds
assert sorted(mods) == sorted(MODS), 'mods mismatch: %s' % mods
assert len(dels) == 0, 'DELETION SET NON-EMPTY (r519 law): %s' % dels

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
print('DELIVERY_OK')
os.remove(idx)
