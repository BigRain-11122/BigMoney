# r582 bm-b surgical re-parent push (r580/_r580bmb_s0_surgery pattern):
# my commit 69248dc20 (parent 5125dc25d, file-set DISJOINT from origin movement) re-parented onto origin/main f2191688c
import subprocess, sys, os

def run(*a, **kw):
    r = subprocess.run(a, capture_output=True, text=True, **kw)
    return r

OLD_BASE = '5125dc25d'
MY = '69248dc20'
r = run('git', 'rev-parse', 'origin/main')
assert r.returncode == 0
NEW_BASE = r.stdout.strip()
print('origin/main =', NEW_BASE)

# my delta (old base -> my commit)
r = run('git', 'diff', '--name-only', OLD_BASE, MY)
mine = [l.strip() for l in r.stdout.splitlines() if l.strip()]
r = run('git', 'diff', '--diff-filter=D', '--name-only', OLD_BASE, MY)
dels = [l.strip() for l in r.stdout.splitlines() if l.strip()]
assert not dels, ('my commit has deletions: %s' % dels)
print('my delta files:', len(mine), '| deletions: 0')

# build base index from origin/main with a temp index file
tmp_idx = os.path.abspath('results/_r582bmb_tmp_index')
env = dict(os.environ, GIT_INDEX_FILE=tmp_idx)
if os.path.exists(tmp_idx): os.remove(tmp_idx)
r = run('git', 'read-tree', NEW_BASE, env=env)
assert r.returncode == 0, r.stderr

# overlay my delta blobs from MY commit tree (explicit column slice r366: mode SP type SP sha TAB path)
for p in mine:
    r = run('git', 'ls-tree', MY, '--', p)
    assert r.returncode == 0 and r.stdout.strip(), ('ls-tree miss', p)
    line = r.stdout.strip().splitlines()[0]
    parts = line.split('\t', 1)
    meta = parts[0].split()
    mode, sha = meta[0], meta[2]  # mode SP type SP sha -- explicit columns, not split()[:2]
    path = parts[1]
    r = run('git', 'update-index', '--add', '--cacheinfo', '%s,%s,%s' % (mode, sha, path), env=env)
    assert r.returncode == 0, (p, r.stderr)
print('index overlay done:', len(mine), 'files')

r = run('git', 'write-tree', env=env)
assert r.returncode == 0, r.stderr
TREE = r.stdout.strip()
print('tree =', TREE)

# assertions: deletion set empty vs origin; tree delta == my payload set
r = run('git', 'diff-tree', '--name-only', '-r', '--diff-filter=D', NEW_BASE, TREE)
d = [l.strip() for l in r.stdout.splitlines() if l.strip()]
assert not d, ('deletion set non-empty: %s' % d)
r = run('git', 'diff-tree', '--name-only', '-r', NEW_BASE, TREE)
delta = set(l.strip() for l in r.stdout.splitlines() if l.strip())
assert delta == set(mine), ('tree delta != payload', sorted(delta ^ set(mine)))
print('assertions PASS: deletion-set empty x1, tree-delta == payload %d' % len(delta))

# commit-tree with new parent
msg = run('git', 'log', '-1', '--format=%B', MY).stdout
r = run('git', 'commit-tree', TREE, '-p', NEW_BASE, '-m', msg.strip())
assert r.returncode == 0, r.stderr
NEWC = r.stdout.strip()
print('new commit =', NEWC)

# CAS update-ref: main must still be MY (r524 law: full 40-char sha, never truncated)
r = run('git', 'rev-parse', MY)
assert r.returncode == 0, r.stderr
MY_FULL = r.stdout.strip()
r = run('git', 'rev-parse', 'main')
assert r.stdout.strip() == MY_FULL, ('main moved', r.stdout)
r = run('git', 'update-ref', 'refs/heads/main', NEWC, MY_FULL)
assert r.returncode == 0, r.stderr

r = run('git', 'push')
print('push rc', r.returncode, (r.stderr or r.stdout).strip()[:200])
assert r.returncode == 0

# post-push: reset --mixed re-anchor + split-face checkout of origin-side files (r578 law)
r = run('git', 'reset', '--mixed', NEWC)
assert r.returncode == 0, r.stderr
r = run('git', 'diff', '--name-only', OLD_BASE, NEW_BASE)
theirs = [l.strip() for l in r.stdout.splitlines() if l.strip()]
r = run('git', 'checkout', '--', *theirs)
assert r.returncode == 0, r.stderr
print('split-face checkout done:', len(theirs), 'origin-side files')
os.remove(tmp_idx)

# delivery self-verify
run('git', 'fetch', 'origin')
r = run('git', 'rev-list', '--count', 'origin/main..HEAD')
print('unpushed count =', r.stdout.strip())
r = run('git', 'rev-list', '--count', 'HEAD..origin/main')
print('unpulled count =', r.stdout.strip())
r = run('git', 'status', '--porcelain')
print('status after surgery:')
print(r.stdout)
