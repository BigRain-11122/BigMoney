import subprocess, os, sys

REPO = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
ADDS = [
    'research/PERPETUAL_N1_W76_PREREG.md',
    'fleet/inbox/MSG-20261002-1130-bmb-w76-seat.md',
    'results/_r572bmb_w76_band_gate.py',
    'results/_r572bmb_w76_freeze_edits.py',
]
MODS = [
    'scripts/perpetual_faces.py',
    'scripts/perpetual_faces_n1.py',
    'research/PERPETUAL_FACES.md',
]
PAYLOAD = ADDS + MODS
MSG = 'r572 bm-b: W76 FREEZE (SIXTY-FIFTH engine wave, bm-b 25th owned; A 195_004..197_003 / B 52_401..52_600 BOTH SIDES ARITHMETIC CONTINUATION zero skip, both CLEAN == W75 row W76+ projection verbatim; gate ADMIT results/_r572bmb_w76_band_gate.py + banned gate ADMIT + full selftest W2..W76 PASS; seat MSG-20261002-1130-bmb published=reserved; W75 bm-a = ONE in-flight upstream seat FAIL-CLOSED r307; chain W1..W74 ALL LANDED head 527,348 K=160,720; MSG-0640 FIX-A/B/C pure-insertion verified)'

def git(args, env=None):
    return subprocess.run(['git', '-C', REPO] + args, capture_output=True, env=env)

r = git(['fetch', 'origin'])
assert r.returncode == 0, r.stderr.decode('utf-8', 'replace')
base = git(['rev-parse', 'origin/main']).stdout.decode().strip()
print('BASE=' + base)

idx = os.path.join(REPO, '.git', 'surgical-index-r572d')
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
print('FREEZE_COMMIT=' + csha)

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
print('FREEZE_DELIVERY_OK')
os.remove(idx)
