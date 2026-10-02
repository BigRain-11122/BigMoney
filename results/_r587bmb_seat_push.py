# r587 bm-b surgical push: W109 seat MSG payload onto fresh origin (r523 law).
# Local commit d9a4a96de (seat MSG only, 1 file) was orphaned by the mid-window
# bm-c advance (W108 freeze 3a3c51b73 + ledger 9508c34ae) -> pre-push claw
# flagged origin-only files as deletion set (r374 fork artifact). Rebase forbidden
# (tracked live-writer lane files dirty, r532 law) -> surgical commit-tree onto
# origin/main. Payload = 1 file (fleet/inbox/MSG-20261002-1817-bmb-w109-seat.md).
import subprocess, sys, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
REPO = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
os.chdir(REPO)
CREATE = 0x08000000

def run(cmd, env=None, check=True):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8',
                       errors='replace', env=env, creationflags=CREATE)
    if check and r.returncode != 0:
        print('FAIL rc=%d: %s' % (r.returncode, ' '.join(cmd[:4])))
        print(r.stderr[-500:]); sys.exit(1)
    return r

def raw(cmd, env=None):
    return subprocess.run(cmd, capture_output=True, env=env, creationflags=CREATE)

run(['git', 'fetch', 'origin'])
mine = run(['git', 'rev-parse', 'main']).stdout.strip()
origin = run(['git', 'rev-parse', 'origin/main']).stdout.strip()
base = run(['git', 'merge-base', 'main', 'origin/main']).stdout.strip()
print('mine=%s origin=%s base=%s' % (mine[:10], origin[:10], base[:10]))

r = run(['git', 'diff', '--no-renames', '--name-status', base, mine])
my_files, my_del = [], []
for l in r.stdout.splitlines():
    if not l.strip(): continue
    st = l.split('\t')[0]; p = l.split('\t')[-1]
    (my_del if st.startswith('D') else my_files).append(p)
assert not my_del, 'payload has deletions: %s' % my_del
r = run(['git', 'diff', '--no-renames', '--name-status', base, origin])
their_mod = [l.split('\t')[-1] for l in r.stdout.splitlines()
             if l.strip() and not l.startswith('D')]
their_del = [l.split('\t')[-1] for l in r.stdout.splitlines()
             if l.strip() and l.startswith('D')]
inter = sorted(set(my_files) & set(their_mod))
print('payload=%s | their_mod=%d | their_del=%d | inter=%s'
      % (my_files, len(their_mod), len(their_del), inter))
assert my_files == ['fleet/inbox/MSG-20261002-1817-bmb-w109-seat.md'], my_files
assert not inter, 'unexpected intersection: %s' % inter

tmp_index = os.path.join(REPO, '.git', 'codely-tmp-index-r587seat')
if os.path.exists(tmp_index):
    os.remove(tmp_index)
env = dict(os.environ, GIT_INDEX_FILE=tmp_index)
run(['git', 'read-tree', origin], env=env)
payload = 0
for f in my_files:
    ls = raw(['git', 'ls-tree', mine, '--', f])
    parts = ls.stdout.decode('utf-8').split()
    assert len(parts) >= 3 and parts[1] == 'blob', 'ls-tree shape fail %s' % f
    h = parts[2]
    run(['git', 'update-index', '--add', '--cacheinfo', '100644,%s,%s' % (h, f)], env=env)
    payload += 1
tree = run(['git', 'write-tree'], env=env).stdout.strip()
msg_path = os.path.join(REPO, '.codely-cli', 'scratch', 'msg_r587_seat.txt')
os.makedirs(os.path.dirname(msg_path), exist_ok=True)
body = run(['git', 'log', '--format=%B', '-1', mine]).stdout
with open(msg_path, 'w', encoding='utf-8') as fh:
    fh.write(body)
newc = raw(['git', 'commit-tree', tree, '-p', origin, '-F', msg_path]).stdout.decode('utf-8').strip()
print('newc=%s' % newc[:12])
r = run(['git', 'diff', '--no-renames', '--name-status', origin, newc])
dels = [l.split('\t')[-1] for l in r.stdout.splitlines() if l.startswith('D')]
assert not dels, 'deletion-set non-empty: %s' % dels
adds = sum(1 for l in r.stdout.splitlines() if l.startswith('A'))
mods = sum(1 for l in r.stdout.splitlines() if l.startswith('M'))
assert adds + mods <= payload, 'payload-count breach: A=%d M=%d payload=%d' % (adds, mods, payload)
print('tree-delta vs origin: A=%d M=%d D=0 payload=%d' % (adds, mods, payload))
r = run(['git', 'push', 'origin', '%s:refs/heads/main' % newc], check=False)
if r.returncode != 0:
    print('push rejected: %s' % r.stderr.strip()[-300:]); sys.exit(2)
print('pushed %s' % newc[:12])
run(['git', 'update-ref', 'refs/heads/main', newc, mine])
run(['git', 'reset', '--mixed', newc])
co = [f for f in sorted(set(their_mod) | set(their_del)) if f not in my_files]
for i in range(0, len(co), 40):
    run(['git', 'checkout', 'HEAD', '--'] + co[i:i + 40])
print('checkout-restored %d origin faces' % len(co))
# delivery proof
run(['git', 'fetch', 'origin'])
n = run(['git', 'rev-list', 'HEAD..origin/main', '--count']).stdout.strip()
rb = raw(['git', 'ls-tree', 'origin/main', '--name-only',
          'fleet/inbox/MSG-20261002-1817-bmb-w109-seat.md'])
on_origin = bool(rb.stdout.decode('utf-8').strip())
print('seat on origin=%s | behind=%s' % (on_origin, n))
assert on_origin and n == '0', 'delivery proof failed'
print('SEAT_PUSH_OK')
