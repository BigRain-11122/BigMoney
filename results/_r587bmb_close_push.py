# r587 bm-b surgical close push: r587 close payload onto fresh origin (r523 law).
# Local chain: 99e29877c(seat) -> f077ae11b(freeze) -> d5c8a5fc1(close); origin
# advanced past f077ae11b with bm-a 254b9d3f0 (W107 ledger append) -> pre-push
# claw would flag origin-only files as deletion set (r374 fork artifact). Rebase
# forbidden (engine live-writers dirty: n1_w109 shards, pool_core_samples,
# saturation_engine bm-b faces, p1d_gates -- r532 law). Pool_core_samples
# EXCLUDED from post-push checkout per r580 law (engine appends in flight).
import subprocess, sys, os, json
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
assert base == run(['git', 'rev-parse', 'f077ae11b']).stdout.strip(), 'unexpected base'

r = run(['git', 'diff', '--no-renames', '--name-status', base, mine])
my_files, my_del = [], []
for l in r.stdout.splitlines():
    if not l.strip(): continue
    st = l.split('\t')[0]; p = l.split('\t')[-1]
    (my_del if st.startswith('D') else my_files).append(p)
print('my payload=%d files | my_del=%s' % (len(my_files), my_del))
r = run(['git', 'diff', '--no-renames', '--name-status', base, origin])
their_mod = [l.split('\t')[-1] for l in r.stdout.splitlines()
             if l.strip() and not l.startswith('D')]
their_del = [l.split('\t')[-1] for l in r.stdout.splitlines()
             if l.strip() and l.startswith('D')]
inter = sorted(set(my_files) & set(their_mod))
print('their_mod=%d | their_del=%s | inter=%s' % (len(their_mod), their_del, inter))

# jsonl intersection union (r570/r580 dict-gated) -- expected EMPTY this window
unioned = {}
for f in inter:
    if f.endswith('.jsonl'):
        ob = raw(['git', 'show', '%s:%s' % (origin, f)]).stdout
        rd = raw(['git', 'diff', base, mine, '--', f])
        added = [l[1:] for l in rd.stdout.decode('utf-8', 'replace').splitlines()
                 if l.startswith('+') and not l.startswith('+++')]
        tail = b''
        for a in added:
            if not a.strip():
                continue
            json.loads(a)
            assert isinstance(json.loads(a), dict), 'non-dict append line in %s' % f
            ab = a.encode('utf-8')
            if ab not in ob:
                tail += ab + b'\n'
        ub = ob if (not ob or ob.endswith(b'\n')) else ob + b'\n'
        ub += tail
        unioned[f] = ub
        print('jsonl union %s: origin_lines=%d my_tail=%d' %
              (f, len(ob.splitlines()), len(tail.splitlines())))
    else:
        print('UNHANDLED INTERSECTION: %s' % f); sys.exit(1)

tmp_index = os.path.join(REPO, '.git', 'codely-tmp-index-r587close')
if os.path.exists(tmp_index):
    os.remove(tmp_index)
env = dict(os.environ, GIT_INDEX_FILE=tmp_index)
run(['git', 'read-tree', origin], env=env)
payload = 0
for f in my_files:
    if f in unioned:
        open(f, 'wb').write(unioned[f])
        h = run(['git', 'hash-object', '-w', f], env=env).stdout.strip()
    else:
        ls = raw(['git', 'ls-tree', mine, '--', f])
        parts = ls.stdout.decode('utf-8').split()
        assert len(parts) >= 3 and parts[1] == 'blob', 'ls-tree shape fail %s' % f
        h = parts[2]
    run(['git', 'update-index', '--add', '--cacheinfo', '100644,%s,%s' % (h, f)], env=env)
    payload += 1
tree = run(['git', 'write-tree'], env=env).stdout.strip()
msg_path = os.path.join(REPO, '.codely-cli', 'scratch', 'msg_r587_close.txt')
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
# r580 law: exclude live-writer/union faces from checkout restore
EXCLUDE = {'results/pool_core_samples.jsonl'}
co = [f for f in sorted(set(their_mod) | set(their_del)) if f not in my_files and f not in EXCLUDE]
for i in range(0, len(co), 40):
    run(['git', 'checkout', 'HEAD', '--'] + co[i:i + 40])
print('checkout-restored %d origin faces (excluded live-writers: %s)' % (len(co), sorted(EXCLUDE)))
run(['git', 'fetch', 'origin'])
n = run(['git', 'rev-list', 'HEAD..origin/main', '--count']).stdout.strip()
ahead = run(['git', 'rev-list', 'origin/main..HEAD', '--count']).stdout.strip()
print('delivery proof: behind=%s ahead-of-origin=%s' % (n, ahead))
assert n == '0', 'still behind origin'
print('CLOSE_PUSH_OK')
