import subprocess, os, sys

REPO = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
os.chdir(REPO)

def git(*args, env=None, inp=None):
    r = subprocess.run(['git'] + list(args), capture_output=True, env=env, input=inp)
    if r.returncode != 0:
        print('GITFAIL', args, r.stderr.decode('utf-8', 'replace')[:500])
        sys.exit(1)
    return r.stdout.decode('utf-8', 'replace')

# 0) verify intersection empty (abort if not)
mine = set(git('diff', '--name-only', '0782e21b', '8c890c3177').split())
org = set(git('diff', '--name-only', '0782e21b', 'be7d2f90a5').split())
inter = mine & org
print('mine=%d origin=%d intersect=%s' % (len(mine), len(org), sorted(inter) if inter else 'EMPTY'))
if inter:
    print('NONEMPTY_INTERSECT_ABORT')
    sys.exit(2)

# 1) drop dead sequencer state (r1032 step2: quit keeps HEAD, drops sequencer)
git('rebase', '--quit')

# 2) temp-index tree surgery: overlay my commit diff onto origin tip tree
idx = os.path.join(REPO, '.git', '_r999_tmpidx')
if os.path.exists(idx):
    os.remove(idx)
env = dict(os.environ, GIT_INDEX_FILE=idx)
r = subprocess.run(['git', 'read-tree', 'be7d2f90a5^{tree}'], capture_output=True, env=env)
assert r.returncode == 0, r.stderr
patch = git('diff', '-M', '--binary', '--full-index', '0782e21b', '8c890c3177')
r = subprocess.run(['git', 'apply', '--cached', '--whitespace=nowarn', '-'],
                   input=patch.encode(), capture_output=True, env=env)
if r.returncode != 0:
    print('APPLYFAIL', r.stderr.decode('utf-8', 'replace')[:600])
    sys.exit(3)
tree = subprocess.run(['git', 'write-tree'], capture_output=True, env=env).stdout.decode().strip()
print('tree', tree)
if os.path.exists(idx):
    os.remove(idx)

# sanity: MSG-0216 present in new tree
ls = git('ls-tree', tree, '--', 'fleet/inbox/MSG-20261018-0216-bm-b-taskaudit.md')
print('msg0216_in_tree', bool(ls.strip()))
if not ls.strip():
    sys.exit(4)

# 3) new commit, preserve original author identity+date, reuse message verbatim
an = git('log', '-1', '--format=%an', '8c890c3177').strip()
ae = git('log', '-1', '--format=%ae', '8c890c3177').strip()
ad = git('log', '-1', '--format=%aD', '8c890c3177').strip()
msg = git('log', '-1', '--format=%B', '8c890c3177')
envc = dict(os.environ, GIT_AUTHOR_NAME=an, GIT_AUTHOR_EMAIL=ae, GIT_AUTHOR_DATE=ad)
r = subprocess.run(['git', 'commit-tree', tree, '-p', 'be7d2f90a5', '-F', '-'],
                   input=msg.encode(), capture_output=True, env=envc)
newc = r.stdout.decode().strip()
print('newc', newc)

# 4) push (pre-push claw runs; inbox-move whitelist should pass the rename)
r = subprocess.run(['git', 'push', 'origin', newc + ':refs/heads/main'], capture_output=True)
print('push_rc', r.returncode)
print('push_out', (r.stdout + r.stderr).decode('utf-8', 'replace')[:500])

# 5) verify delivery: fetch + compare
git('fetch', 'origin')
o = git('rev-parse', 'origin/main').strip()
print('origin_main', o, 'DELIVERED' if o == newc else 'MISMATCH')

if o != newc:
    sys.exit(5)

# 6) heal local main ref (zero worktree change: same tree), then checkout main
git('update-ref', 'refs/heads/main', newc)
git('checkout', 'main')
h = git('rev-parse', 'HEAD').strip()
print('HEAD_now', h, 'checkout_ok', h == newc)
print('branch', git('status', '--short', '--branch').splitlines()[0])
