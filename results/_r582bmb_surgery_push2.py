# r582 bm-b seat-commit surgical re-parent push (shared parent 1ffa07210, disjoint file sets)
import subprocess, os

def run(*a, **kw):
    return subprocess.run(a, capture_output=True, text=True, **kw)

OLD_BASE = '1ffa07210'
MY = '4ad0e0973'
r = run('git', 'rev-parse', 'origin/main'); assert r.returncode == 0
NEW_BASE = r.stdout.strip()
print('origin/main =', NEW_BASE)
assert NEW_BASE != OLD_BASE

r = run('git', 'diff', '--name-only', OLD_BASE, MY)
mine = [l.strip() for l in r.stdout.splitlines() if l.strip()]
r = run('git', 'diff', '--diff-filter=D', '--name-only', OLD_BASE, MY)
dels = [l.strip() for l in r.stdout.splitlines() if l.strip()]
assert not dels, dels
print('my delta:', len(mine), 'files, deletions 0')

tmp_idx = os.path.abspath('results/_r582bmb_tmp_index2')
env = dict(os.environ, GIT_INDEX_FILE=tmp_idx)
if os.path.exists(tmp_idx): os.remove(tmp_idx)
assert run('git', 'read-tree', NEW_BASE, env=env).returncode == 0
for p in mine:
    r = run('git', 'ls-tree', MY, '--', p)
    assert r.returncode == 0 and r.stdout.strip(), p
    line = r.stdout.strip().splitlines()[0]
    parts = line.split('\t', 1)
    meta = parts[0].split()
    mode, sha = meta[0], meta[2]  # r366 explicit columns
    r = run('git', 'update-index', '--add', '--cacheinfo', '%s,%s,%s' % (mode, sha, parts[1]), env=env)
    assert r.returncode == 0, (p, r.stderr)
r = run('git', 'write-tree', env=env); assert r.returncode == 0, r.stderr
TREE = r.stdout.strip()
r = run('git', 'diff-tree', '--name-only', '-r', '--diff-filter=D', NEW_BASE, TREE)
assert not [l for l in r.stdout.splitlines() if l.strip()], 'deletion set non-empty'
r = run('git', 'diff-tree', '--name-only', '-r', NEW_BASE, TREE)
delta = set(l.strip() for l in r.stdout.splitlines() if l.strip())
assert delta == set(mine), ('delta != payload', sorted(delta ^ set(mine)))
print('assertions PASS: deletion-set empty, tree-delta == payload', len(delta))

msg = run('git', 'log', '-1', '--format=%B', MY).stdout
r = run('git', 'commit-tree', TREE, '-p', NEW_BASE, '-m', msg.strip())
assert r.returncode == 0, r.stderr
NEWC = r.stdout.strip()
print('new commit =', NEWC)

r = run('git', 'rev-parse', MY)
MY_FULL = r.stdout.strip()
r = run('git', 'rev-parse', 'main')
assert r.stdout.strip() == MY_FULL, ('main moved', r.stdout)
r = run('git', 'update-ref', 'refs/heads/main', NEWC, MY_FULL)
assert r.returncode == 0, r.stderr
r = run('git', 'push')
print('push rc', r.returncode, (r.stderr or r.stdout).strip()[:200])
assert r.returncode == 0
r = run('git', 'reset', '--mixed', NEWC)
assert r.returncode == 0, r.stderr
r = run('git', 'diff', '--name-only', OLD_BASE, NEW_BASE)
theirs = [l.strip() for l in r.stdout.splitlines() if l.strip()]
r = run('git', 'checkout', '--', *theirs)
assert r.returncode == 0, r.stderr
print('split-face checkout:', len(theirs), 'origin-side files')
os.remove(tmp_idx)
run('git', 'fetch', 'origin')
print('unpushed:', run('git', 'rev-list', '--count', 'origin/main..HEAD').stdout.strip())
print('unpulled:', run('git', 'rev-list', '--count', 'HEAD..origin/main').stdout.strip())
print(run('git', 'status', '--porcelain').stdout)
