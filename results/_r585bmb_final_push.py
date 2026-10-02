# r585 bm-b final surgical push: 5-file close delta onto origin 83438cc37
# (bm-c r377 re-parented onto my d6b2952e3 mid-round). CODELY.md intersects
# (bm-c appended their lessons) -> union = origin blob + my lesson line
# appended (r581 law). Other 4 files bm-b-owned verbatim. Seat MSG move
# already landed by bm-c (their tree position kept).
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
        print(r.stderr[-400:]); sys.exit(1)
    return r

def raw(cmd, env=None):
    return subprocess.run(cmd, capture_output=True, env=env, creationflags=CREATE)

mine = run(['git', 'rev-parse', 'main']).stdout.strip()
origin = run(['git', 'rev-parse', 'origin/main']).stdout.strip()
base = run(['git', 'merge-base', 'main', 'origin/main']).stdout.strip()
print('mine=%s origin=%s base=%s' % (mine[:10], origin[:10], base[:10]))
assert base == 'd6b2952e3'[:10] or base.startswith('d6b2952'), 'unexpected base %s' % base

r = run(['git', 'diff', '--no-renames', '--name-status', base, mine])
my_files, my_del = [], []
for l in r.stdout.splitlines():
    if not l.strip(): continue
    st = l.split('\t')[0]; p = l.split('\t')[-1]
    (my_del if st.startswith('D') else my_files).append(p)
r = run(['git', 'diff', '--no-renames', '--name-status', base, origin])
their_mod = [l.split('\t')[-1] for l in r.stdout.splitlines()
             if l.strip() and not l.startswith('D')]
their_del = [l.split('\t')[-1] for l in r.stdout.splitlines()
             if l.strip() and l.startswith('D')]
inter = sorted(set(my_files) & set(their_mod))
print('my_files=%s' % my_files)
print('their_del=%s' % their_del)
print('inter=%s' % inter)

# CODELY union: origin blob + my committed added lines
if 'CODELY.md' in inter:
    rb = raw(['git', 'show', 'origin/main:CODELY.md'])
    ob = rb.stdout
    rd = raw(['git', 'diff', base, mine, '--', 'CODELY.md'])
    added = [l[1:] for l in rd.stdout.decode('utf-8').splitlines()
             if l.startswith('+') and not l.startswith('+++')]
    okeys = set(ob.splitlines())
    tail = b''
    for a in added:
        ab = a.encode('utf-8')
        if ab.strip() and ab not in okeys:
            tail += ab + b'\n'
    ub = ob if (not ob or ob.endswith(b'\n')) else ob + b'\n'
    ub += tail
    with open('CODELY.md', 'wb') as f:
        f.write(ub)
    print('CODELY union: origin_lines=%d my_tail=%d' % (len(ob.splitlines()), len(tail.splitlines())))

tmp_index = os.path.join(REPO, '.git', 'codely-tmp-index-r585final')
if os.path.exists(tmp_index):
    os.remove(tmp_index)
env = dict(os.environ, GIT_INDEX_FILE=tmp_index)
run(['git', 'read-tree', origin], env=env)
payload = 0
for f in my_files:
    ls = raw(['git', 'ls-tree', mine, '--', f]) if f != 'CODELY.md' or 'CODELY.md' not in inter else None
    if ls is None:  # unioned CODELY -> hash from working tree
        h = run(['git', 'hash-object', '-w', f], env=env).stdout.strip()
    else:
        parts = ls.stdout.decode('utf-8').split()
        assert len(parts) >= 3 and parts[1] == 'blob', 'ls-tree shape fail %s' % f
        h = parts[2]
    run(['git', 'update-index', '--add', '--cacheinfo', '100644,%s,%s' % (h, f)], env=env)
    payload += 1
tree = run(['git', 'write-tree'], env=env).stdout.strip()
msg_path = os.path.join(REPO, '.codely-cli', 'scratch', 'msg_r585_final.txt')
with open(msg_path, 'w', encoding='utf-8') as fh:
    fh.write('round 585 bm-b close: state 585 + heartbeat (epoch int, ack 143 carried) + '
             'round report + CODELY r585 lesson (CODELY union with bm-c r377 tail rows per '
             'r581 law; surgical payload onto 83438cc37 after mid-round origin advance, '
             'r374 fork artifact resolved by integration) [via bm-b r585]')
newc = raw(['git', 'commit-tree', tree, '-p', origin, '-F', msg_path], env=env).stdout.decode('utf-8').strip()
print('newc=%s' % newc[:12])
r = run(['git', 'diff', '--no-renames', '--name-status', origin, newc])
dels = [l.split('\t')[-1] for l in r.stdout.splitlines() if l.startswith('D')]
assert not dels, 'deletion-set non-empty: %s' % dels
adds = sum(1 for l in r.stdout.splitlines() if l.startswith('A'))
mods = sum(1 for l in r.stdout.splitlines() if l.startswith('M'))
assert adds + mods <= payload, 'payload-count breach'
print('tree-delta: A=%d M=%d D=0 payload=%d' % (adds, mods, payload))
r = run(['git', 'push', 'origin', '%s:refs/heads/main' % newc], check=False)
if r.returncode != 0:
    print('push rejected: %s' % r.stderr.strip()[-300:]); sys.exit(2)
print('pushed %s' % newc[:12])
run(['git', 'update-ref', 'refs/heads/main', newc, mine])
run(['git', 'reset', '--mixed', newc])
co = [f for f in sorted(set(their_mod) | set(their_del)) if f not in my_files]
for i in range(0, len(co), 40):
    run(['git', 'checkout', 'HEAD', '--'] + co[i:i + 40])
# their seat-MSG move: remove the local inbox copy (origin moved it)
inbox = 'fleet/inbox/MSG-20261002-1733-bmb-w106-seat.md'
if os.path.exists(inbox):
    os.remove(inbox)
    print('local seat MSG synced to processed (origin move)')
print(run(['git', 'status', '--porcelain']).stdout or '(clean)')
rb = raw(['git', 'ls-tree', 'origin/main', '--name-only', 'state.json'])
assert rb.stdout.strip(), 'delivery proof fail: state.json'
run(['git', 'fetch', 'origin'])
n = run(['git', 'rev-list', 'HEAD..origin/main', '--count']).stdout.strip()
print('FINAL_PUSH_OK behind=%s' % n)
