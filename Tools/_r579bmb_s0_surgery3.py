# r579 bm-b surgery3: replay unpushed yield/W93-seat commit onto new origin head
# (origin moved 6: bm-c W92 freeze + bm-a W90 finalize; zero file intersection)
import os, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(REPO)

def run(cmd, env=None, check=True):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
    if check and r.returncode != 0:
        print('FAIL rc=%d: %s' % (r.returncode, ' '.join(cmd)))
        print(r.stderr[-600:])
        sys.exit(1)
    return r

base = '0ea213e8b786'   # last pushed bm-b commit
old_main = run(['git', 'rev-parse', 'main']).stdout.strip()
origin_main = run(['git', 'rev-parse', 'origin/main']).stdout.strip()

r = run(['git', 'diff', '--name-status', base, 'main'])
my_files = [l.split('\t')[-1] for l in r.stdout.splitlines() if l.strip()]
print('my_delta_files=%d' % len(my_files), my_files)

r = run(['git', 'status', '--porcelain'])
dirty = [l[3:] for l in r.stdout.splitlines() if l[:2] in (' M', 'M ', '??')]
print('ride_files=%d' % len(dirty))

# zero-intersection assertion (r570/r507 union law pre-check)
r = run(['git', 'diff', '--name-only', base, origin_main])
their = set(l for l in r.stdout.splitlines() if l.strip())
inter = their & (set(my_files) | set(dirty))
assert not inter, 'INTERSECTION needs union merge: %s' % inter
print('intersection=none (origin-side take via checkout)')

tmp_index = os.path.join(REPO, '.git', 'codely-tmp-index-r579')
env = dict(os.environ, GIT_INDEX_FILE=tmp_index)
run(['git', 'read-tree', origin_main], env=env)
for f in my_files + dirty:
    h = run(['git', 'hash-object', '-w', f], env=env).stdout.strip()
    run(['git', 'update-index', '--add', '--cacheinfo', '100644,%s,%s' % (h, f)], env=env)
tree = run(['git', 'write-tree'], env=env).stdout.strip()
msg = ('round 579 bm-b: W92 zero-cost yield receipt + W93 seat published '
       '(replayed onto %s after bm-c W92 freeze + bm-a W90 finalize window; '
       'S6 chain lane faces ridden) [via bm-b r579]' % origin_main[:10])
newc = run(['git', 'commit-tree', tree, '-p', origin_main, '-m', msg], env=env).stdout.strip()
print('tree=%s new=%s' % (tree[:12], newc[:12]))

r = run(['git', 'push', 'origin', '%s:refs/heads/main' % newc], check=False)
if r.returncode != 0:
    print('PUSH_REJECTED ' + r.stderr[-400:])
    sys.exit(2)
print('pushed ' + newc[:12])

run(['git', 'update-ref', 'refs/heads/main', newc, old_main])
run(['git', 'reset', '--mixed', newc])
run(['git', 'checkout', 'HEAD', '--'] + sorted(their))
st = run(['git', 'status', '--porcelain']).stdout
print('post dirty:')
print(st if st else '(clean)')

# W91 finalize unblock check: W90 results on origin + local
ok = run(['git', 'cat-file', '-e', 'origin/main:results/perpetual_faces/n1_w90_results.json'], check=False)
print('w90_on_origin=%s' % (ok.returncode == 0))
print('SURGERY3_OK')
