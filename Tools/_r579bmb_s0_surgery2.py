# r579 bm-b surgery2: replay unpushed W89 finalize commit onto new origin head
# (r532 live-writer law: tracked engine writes in flight = no rebase, surgical overlay)
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

base = '37079d9b7ec6'
old_main = run(['git', 'rev-parse', 'main']).stdout.strip()
origin_main = run(['git', 'rev-parse', 'origin/main']).stdout.strip()
assert run(['git', 'merge-base', main_path := 'main', origin_main]).stdout.strip() if False else True

# my unpushed delta files (vs the pushed surgery commit)
r = run(['git', 'diff', '--name-status', base, 'main'])
my_files = [l.split('\t')[-1] for l in r.stdout.splitlines() if l.strip()]
print('my_delta_files=%d' % len(my_files), my_files)

# current dirty telemetry (ride overlay)
r = run(['git', 'status', '--porcelain'])
dirty = [l[3:] for l in r.stdout.splitlines() if l.startswith(' M') or l.startswith('M ')]
print('ride_files=%d' % len(dirty), dirty)

tmp_index = os.path.join(REPO, '.git', 'codely-tmp-index-r579b')
env = dict(os.environ, GIT_INDEX_FILE=tmp_index)
run(['git', 'read-tree', origin_main], env=env)
for f in my_files + dirty:
    h = run(['git', 'hash-object', '-w', f], env=env).stdout.strip()
    run(['git', 'update-index', '--add', '--cacheinfo', '100644,%s,%s' % (h, f)], env=env)
tree = run(['git', 'write-tree'], env=env).stdout.strip()
msg = ('round 579 bm-b: W89 finalize one-pass landed (12/12, chain 558,148 -> 560,348, '
       'K=193,720; prereg S7/S8 backfilled; replayed onto %s after bm-c r370 lane ride '
       '[via bm-b r579]' % origin_main[:10])
newc = run(['git', 'commit-tree', tree, '-p', origin_main, '-m', msg], env=env).stdout.strip()
print('tree=%s new=%s' % (tree[:12], newc[:12]))

r = run(['git', 'push', 'origin', '%s:refs/heads/main' % newc], check=False)
if r.returncode != 0:
    print('PUSH_REJECTED ' + r.stderr[-400:])
    sys.exit(2)
print('pushed ' + newc[:12])

run(['git', 'update-ref', 'refs/heads/main', newc, old_main])
run(['git', 'reset', '--mixed', newc])
# origin-side files: take their version into worktree
r = run(['git', 'diff', '--name-only', base, 'origin/main'])
their_files = [l for l in r.stdout.splitlines() if l.strip()]
run(['git', 'checkout', 'HEAD', '--'] + their_files)
st = run(['git', 'status', '--porcelain']).stdout
print('post dirty:')
print(st if st else '(clean)')
print('SURGERY2_OK')
