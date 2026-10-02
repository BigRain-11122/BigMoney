# -*- coding: utf-8 -*-
# r375 bm-c W102 freeze + ignition shards surgical re-parent push (v2).
# Pre-push claw correctly blocked the direct push (bm-b cd2610688 wrap
# landed on origin after my seat push); rebase refused by tracked
# live-write dirty tree per r532.  Payload = 7 freeze files (blobs from
# my freeze commit ac078162d, git add clean-filtered LF) + ALL W102
# shard products present in HEAD's tree at run time (engine appender
# commits, science products).  bm-b's delta touches ZERO of my shared
# edit targets (verified).  CAS update-ref (old = run-time HEAD) makes
# the resident-engine appender race abort-safe (retry = re-run).
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREAT = 0x08000000
FREEZE_COMMIT = 'ac078162d'
FIXED_PAYLOAD = [
    'research/PERPETUAL_FACES.md',
    'scripts/perpetual_faces.py',
    'scripts/perpetual_faces_n1.py',
    'research/PERPETUAL_N1_W102_PREREG.md',
    'results/_r375bmc_w102_band_gate.py',
    'results/_r375bmc_w102_freeze_edits.py',
    'results/_r374bmc_coda_push.py',
]


def run(*a, **kw):
    return subprocess.run(a, capture_output=True, text=True, cwd=REPO,
                          creationflags=CREAT, **kw)


def ls_tree_blobs(commit, pathspec):
    r = run('git', 'ls-tree', commit, '--', pathspec)
    assert r.returncode == 0, r.stderr
    out = []
    for line in r.stdout.strip().splitlines():
        if not line.strip():
            continue
        left, _sep, path = line.partition('\t')      # r366 explicit columns
        mode, typ, sha = left.split()                  # [mode, type, sha]
        assert typ == 'blob' and len(sha) == 40, (path, left)
        out.append((mode, sha, path))
    return out


r = run('git', 'rev-parse', 'HEAD'); assert r.returncode == 0, r.stderr
OLD = r.stdout.strip()
r = run('git', 'rev-parse', 'origin/main'); assert r.returncode == 0, r.stderr
NEW_BASE = r.stdout.strip()
print('old local HEAD =', OLD)
print('origin/main    =', NEW_BASE)

# freshness re-verify: bm-b delta still does not touch my shared targets
r = run('git', 'diff', '--name-only', 'a369ae045', NEW_BASE)
touched = set(l.strip() for l in r.stdout.splitlines() if l.strip())
overlap = touched & {'scripts/perpetual_faces.py',
                     'scripts/perpetual_faces_n1.py',
                     'research/PERPETUAL_FACES.md'}
assert not overlap, 'origin touched my shared targets: %s' % overlap
print('overlap re-verify: zero shared-target overlap with origin delta')

payload = []
for p in FIXED_PAYLOAD:
    blobs = ls_tree_blobs(FREEZE_COMMIT, p)
    assert len(blobs) == 1, (p, blobs)
    payload.append(blobs[0])
shards = ls_tree_blobs(OLD, 'results/p2cal_ext/n1_w102/')
payload.extend(shards)
paths = [b[2] for b in payload]
assert len(set(paths)) == len(paths), 'duplicate payload paths'
print('payload: %d freeze files + %d W102 shard products'
      % (len(FIXED_PAYLOAD), len(shards)))

tmp_idx = os.path.abspath(os.path.join(
    REPO, 'results', '_r375bmc_tmp_index'))
env = dict(os.environ, GIT_INDEX_FILE=tmp_idx)
if os.path.exists(tmp_idx):
    os.remove(tmp_idx)
assert run('git', 'read-tree', NEW_BASE, env=env).returncode == 0
for mode, sha, path in payload:
    r2 = run('git', 'update-index', '--add', '--cacheinfo',
             '%s,%s,%s' % (mode, sha, path), env=env)
    assert r2.returncode == 0, (path, r2.stderr)

r = run('git', 'write-tree', env=env); assert r.returncode == 0, r.stderr
TREE = r.stdout.strip()

r = run('git', 'diff-tree', '--name-only', '-r', '--diff-filter=D', NEW_BASE, TREE)
dels = [l for l in r.stdout.splitlines() if l.strip()]
assert not dels, ('deletion set non-empty', dels)
r = run('git', 'diff-tree', '--name-only', '-r', NEW_BASE, TREE)
delta = set(l.strip() for l in r.stdout.splitlines() if l.strip())
assert delta == set(paths), ('delta != payload', sorted(delta ^ set(paths)))
print('assertions PASS: deletion-set empty, tree-delta == payload (%d)' % len(delta))

msg_path = os.path.abspath(os.path.join(
    REPO, '..', '.codely-cli', 'scratch', '_r375bmc_w102_msg.txt'))
MSG = open(msg_path, encoding='utf-8').read().strip()
r = run('git', 'commit-tree', TREE, '-p', NEW_BASE, '-m', MSG)
assert r.returncode == 0, r.stderr
NEWC = r.stdout.strip()
print('new commit =', NEWC)

r = run('git', 'rev-parse', 'main')
assert r.stdout.strip() == OLD, ('main moved mid-surgery (CAS abort, re-run)',
                                 r.stdout, OLD)
r = run('git', 'update-ref', 'refs/heads/main', NEWC, OLD)
assert r.returncode == 0, r.stderr
r = run('git', 'push', 'origin', 'main')
print('push rc =', r.returncode)
if r.returncode != 0:
    print(r.stdout); print(r.stderr)
    sys.exit(1)

# r578 law: update-ref leaves index at OLD tree -- reset --mixed re-anchor,
# then face-by-face worktree sync (never trust a same-name checkout).
assert run('git', 'reset', '--mixed', NEWC).returncode == 0
r = run('git', 'status', '--porcelain')
missing = [l[3:].strip() for l in r.stdout.splitlines()
           if l.startswith(' D') or l.startswith('D ')]
if missing:
    r2 = run('git', 'checkout', 'HEAD', '--', *missing)
    assert r2.returncode == 0, (missing[:4], r2.stderr)
print('worktree synced: %d missing faces checked out' % len(missing))

# stale untracked inbox copies of seat MSGs bm-b archived to processed/
for stale in ('fleet/inbox/MSG-20261002-1615-bmb-w100-seat.md',
              'fleet/inbox/MSG-20261002-1625-bma-w101-seat.md'):
    fp = os.path.join(REPO, stale)
    if os.path.exists(fp):
        os.remove(fp)
        print('stale inbox copy removed:', stale)

r = run('git', 'fetch', 'origin')
assert r.returncode == 0, r.stderr
r = run('git', 'ls-tree', '--name-only', 'origin/main', '--',
        'research/PERPETUAL_N1_W102_PREREG.md')
assert r.stdout.strip(), 'delivery verify failed: prereg not on origin'
r = run('git', 'ls-tree', '--name-only', 'origin/main', '--',
        'results/p2cal_ext/n1_w102/')
n_on_origin = len([l for l in r.stdout.splitlines() if l.strip()])
r = run('git', 'rev-parse', 'origin/main')
print('delivery verify PASS: prereg on origin + %d W102 shards; origin/main = %s'
      % (n_on_origin, r.stdout.strip()))
print('SURGERY_OK')
