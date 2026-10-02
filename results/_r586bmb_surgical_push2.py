# r586 bm-b surgical push #2: finalize payload onto fresh origin (r523 law)
# Handles .jsonl dict-gated union AND CODELY.md line-level union in intersections.
import subprocess, sys, os, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
os.chdir(r'C:\Fluxgroup\FluxGroup\quant\bigmoney')
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

run(['git', 'fetch', 'origin'])
mine = run(['git', 'rev-parse', 'main']).stdout.strip()
origin = run(['git', 'rev-parse', 'origin/main']).stdout.strip()
base = run(['git', 'merge-base', 'main', 'origin/main']).stdout.strip()
print('mine=%s origin=%s base=%s' % (mine[:10], origin[:10], base[:10]))
assert base.startswith('e875d4a1'), 'unexpected base %s' % base

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
print('my payload=%d | their_mod=%d | their_del=%s | inter=%s'
      % (len(my_files), len(their_mod), their_del, inter))

unioned = {}
for f in inter:
    ob = raw(['git', 'show', '%s:%s' % (origin, f)]).stdout
    rd = raw(['git', 'diff', base, mine, '--', f])
    added = [l[1:] for l in rd.stdout.decode('utf-8', 'replace').splitlines()
             if l.startswith('+') and not l.startswith('+++')]
    if f.endswith('.jsonl'):
        tail = b''
        for a in added:
            if not a.strip(): continue
            try:
                v = json.loads(a)
            except Exception:
                continue
            assert isinstance(v, dict), 'non-dict append in %s' % f
            ab = a.encode('utf-8')
            if ab not in ob:
                tail += ab + b'\n'
        ub = ob if (not ob or ob.endswith(b'\n')) else ob + b'\n'
        ub += tail
        unioned[f] = ub
        print('jsonl union %s: origin=%d +mine=%d' % (f, len(ob.splitlines()), len(tail.splitlines())))
    elif f == 'CODELY.md':
        okeys = set(ob.splitlines())
        tail = b''
        for a in added:
            ab = a.encode('utf-8')
            if ab.strip() and ab not in okeys:
                tail += ab + b'\n'
        ub = ob if (not ob or ob.endswith(b'\n')) else ob + b'\n'
        ub += tail
        unioned[f] = ub
        print('CODELY union: origin_lines=%d +mine=%d' % (len(ob.splitlines()), len(tail.splitlines())))
    else:
        print('UNHANDLED INTERSECTION: %s' % f); sys.exit(1)

tmp_index = os.path.join(os.getcwd(), '.git', 'codely-tmp-index-r586surg2')
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
msg_path = os.path.join(os.getcwd(), '.codely-cli', 'scratch', 'msg_r586_surg2.txt')
with open(msg_path, 'w', encoding='utf-8') as fh:
    fh.write('round 586 bm-b: W103 FINALIZE landed one-pass (chain head 588,948 W102 bm-c landed + 2,200 = 591,148, '
             'K=224,520; w103-only mu=-0.09905036 sigma=0.25578541; merged mu=-0.09289408 sigma=0.24490355; '
             'skill_line_v2 @n_eff 588,948: 1.169 -> 1.1695, K-lift delta +0.0005; voids_applied LOWAMP-P1/P2; '
             'S5 four gates ALL PASS on the W98 freeze anchor; prereg S7/S8 mechanical backfill r307 same-round law; '
             'n1 default-wave selftest PASS + pf 9/9; downstream W104 bm-a finalize UNBLOCKED. Surgical payload onto '
             'origin %s after the mid-round bm-a W107-freeze advance, r374 fork artifact resolved by integration per '
             'r523 law. [via bm-b r586]' % origin[:10])
newc = raw(['git', 'commit-tree', tree, '-p', origin, '-F', msg_path]).stdout.decode('utf-8').strip()
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
print('checkout-restored %d origin faces' % len(co))
st = run(['git', 'status', '--porcelain']).stdout
print('status now:'); print(st or '(clean)')
run(['git', 'fetch', 'origin'])
n = run(['git', 'rev-list', 'HEAD..origin/main', '--count']).stdout.strip()
rb = raw(['git', 'ls-tree', 'origin/main', '--name-only', 'results/perpetual_faces/n1_w103_results.json'])
print('delivery proof: n1_w103_results on origin=%d | behind=%s' % (len(rb.stdout.decode().split()), n))
print('FINAL_PUSH_OK behind=%s' % n)
