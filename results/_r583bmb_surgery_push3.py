# r583 bm-b surgical re-parent push #3 (round-close commit onto W102 seat commit)
import subprocess, os

def run(*a, **kw):
    return subprocess.run(a, capture_output=True, text=True, **kw)

r = run('git', 'rev-parse', 'HEAD'); assert r.returncode == 0
OLD = r.stdout.strip()
r = run('git', 'rev-parse', 'origin/main'); assert r.returncode == 0
NEW_BASE = r.stdout.strip()
BASE = run('git', 'merge-base', OLD, NEW_BASE).stdout.strip()
print('old local HEAD =', OLD[:9], '| new base =', NEW_BASE[:9], '| merge-base =', BASE[:9])

r = run('git', 'diff', '--name-only', BASE, OLD)
mine = sorted(set(l.strip() for l in r.stdout.splitlines() if l.strip()))
r = run('git', 'diff', '--diff-filter=D', '--name-only', BASE, OLD)
dels = [l.strip() for l in r.stdout.splitlines() if l.strip()]
assert not dels, dels
r = run('git', 'diff', '--name-only', BASE, NEW_BASE)
theirs = set(l.strip() for l in r.stdout.splitlines() if l.strip())
overlap = set(mine) & theirs
print('my delta:', len(mine), 'files | their delta:', len(theirs), '| overlap:', sorted(overlap) or 'NONE')
assert not overlap, overlap

tmp_idx = os.path.abspath('results/_r583bmb_tmp_index3')
env = dict(os.environ, GIT_INDEX_FILE=tmp_idx)
if os.path.exists(tmp_idx): os.remove(tmp_idx)
assert run('git', 'read-tree', NEW_BASE, env=env).returncode == 0
for p in mine:
    r = run('git', 'ls-tree', OLD, '--', p)
    assert r.returncode == 0 and r.stdout.strip(), p
    line = r.stdout.strip().splitlines()[0]
    parts = line.split('\t', 1)
    meta = parts[0].split()
    mode, sha = meta[0], meta[2]
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

msg = run('git', 'log', '-1', '--format=%B', OLD).stdout
r = run('git', 'commit-tree', TREE, '-p', NEW_BASE, '-m', msg.strip())
assert r.returncode == 0, r.stderr
NEWC = r.stdout.strip()
print('new commit =', NEWC[:9])

r = run('git', 'rev-parse', 'main')
assert r.stdout.strip() == OLD, ('main moved', r.stdout)
assert run('git', 'update-ref', 'refs/heads/main', NEWC, OLD).returncode == 0
r = run('git', 'push')
print('push rc', r.returncode, (r.stderr or r.stdout).strip()[:200])
assert r.returncode == 0
assert run('git', 'reset', '--mixed', NEWC).returncode == 0
# restore origin-side files in worktree (their delta)
if theirs:
    r = run('git', 'checkout', '--', *sorted(theirs))
    assert r.returncode == 0, r.stderr
    print('split-face checkout:', len(theirs), 'origin-side files')
run('git', 'fetch', 'origin')
print('unpushed:', run('git', 'rev-list', '--count', 'origin/main..HEAD').stdout.strip())
print('unpulled:', run('git', 'rev-list', '--count', 'HEAD..origin/main').stdout.strip())
print(run('git', 'status', '--porcelain').stdout)
os.remove(tmp_idx)
