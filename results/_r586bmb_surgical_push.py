# r586 bm-b surgical push: payload re-commit onto fresh origin (r523 law, r374 fork artifact)
# origin advanced mid-round with 3 bm-a commits (W101 FINALIZE + W104 delivery + W107 seat).
# Intersection = results/pool_core_samples.jsonl only -> dict-gated line union (r570/r580 law):
# origin blob verbatim base + my 12 dict-only appended burn-sample lines.
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
        print(r.stderr[-400:]); sys.exit(1)
    return r

def raw(cmd, env=None):
    return subprocess.run(cmd, capture_output=True, env=env, creationflags=CREATE)

mine = run(['git', 'rev-parse', 'main']).stdout.strip()
origin = run(['git', 'rev-parse', 'origin/main']).stdout.strip()
base = run(['git', 'merge-base', 'main', 'origin/main']).stdout.strip()
print('mine=%s origin=%s base=%s' % (mine[:10], origin[:10], base[:10]))
assert base.startswith('e79dcf6b'), 'unexpected base %s' % base

r = run(['git', 'diff', '--no-renames', '--name-status', base, mine])
my_files, my_del = [], []
for l in r.stdout.splitlines():
    if not l.strip(): continue
    st = l.split('\t')[0]; p = l.split('\t')[-1]
    (my_del if st.startswith('D') else my_files).append(p)
assert not my_del, 'my payload has deletions: %s' % my_del
r = run(['git', 'diff', '--no-renames', '--name-status', base, origin])
their_mod = [l.split('\t')[-1] for l in r.stdout.splitlines()
             if l.strip() and not l.startswith('D')]
their_del = [l.split('\t')[-1] for l in r.stdout.splitlines()
             if l.strip() and l.startswith('D')]
inter = sorted(set(my_files) & set(their_mod))
print('my payload=%d files | their_mod=%d | their_del=%s | inter=%s'
      % (len(my_files), len(their_mod), their_del, inter))

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
            json.loads(a)  # parse gate
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

tmp_index = os.path.join(REPO, '.git', 'codely-tmp-index-r586surg')
if os.path.exists(tmp_index):
    os.remove(tmp_index)
env = dict(os.environ, GIT_INDEX_FILE=tmp_index)
run(['git', 'read-tree', origin], env=env)
payload = 0
for f in my_files:
    if f in unioned:
        open(f, 'wb').write(unioned[f])  # persist union to working tree too
        h = run(['git', 'hash-object', '-w', f], env=env).stdout.strip()
    else:
        ls = raw(['git', 'ls-tree', mine, '--', f])
        parts = ls.stdout.decode('utf-8').split()
        assert len(parts) >= 3 and parts[1] == 'blob', 'ls-tree shape fail %s' % f
        h = parts[2]
    run(['git', 'update-index', '--add', '--cacheinfo', '100644,%s,%s' % (h, f)], env=env)
    payload += 1
tree = run(['git', 'write-tree'], env=env).stdout.strip()
msg_path = os.path.join(REPO, '.codely-cli', 'scratch', 'msg_r586_surg.txt')
with open(msg_path, 'w', encoding='utf-8') as fh:
    fh.write('round 586 bm-b: W106 burn products 12/12 delivered to origin (2,200 backtests, workers=8, '
             '96th engine wave; engine ledger 12 rows + faces ride) + pool_core_samples union '
             '(origin verbatim + 12 bm-b dict-only burn-sample appends, r570/r580 law) + S0 pure-FF '
             'surgical integration (e79dcf6b4 base, 55 faces checkout-restored, W106 seat MSG '
             'displacement healed via blob-identity) + W14 governance-park verified per r483 (zero '
             'action) + S6 33 legs rc0 (ZERO-DRIFT 30/3, REPORT/LIVE regen) + WM py_low_board_clear '
             'legal idle + S7 self-heal 5/5 + CODELY r586 lesson + state/heartbeat r586. Surgical '
             'payload onto origin %s after mid-round bm-a advance (W101 FINALIZE + W104 delivery + '
             'W107 seat), r374 fork artifact resolved by integration per r523 law. [via bm-b r586]'
             % origin[:10])
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
st = run(['git', 'status', '--porcelain']).stdout
print('status now:'); print(st or '(clean)')
# delivery proofs
run(['git', 'fetch', 'origin'])
n = run(['git', 'rev-list', 'HEAD..origin/main', '--count']).stdout.strip()
rb = raw(['git', 'ls-tree', 'origin/main', '--name-only', 'results/p2cal_ext/n1_w106/'])
w106 = len(rb.stdout.decode('utf-8').split())
rb2 = raw(['git', 'ls-tree', 'origin/main', '--name-only', 'state.json', 'CODELY.md', 'fleet/machines/bm-b.json'])
print('delivery proof: n1_w106 files on origin=%d | core faces=%d | behind=%s'
      % (w106, len(rb2.stdout.decode('utf-8').split()), n))
assert w106 == 12, 'W106 delivery incomplete: %d' % w106
print('FINAL_PUSH_OK behind=%s' % n)
