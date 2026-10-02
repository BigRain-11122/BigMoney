# r585 bm-b S0 integration: origin 5 commits ahead, merge-base == my HEAD
# (my r584 fully pushed) -> NO payload commit needed, pure FF + working-tree
# reconciliation. r532 law still applies (no rebase on live writers), r578
# law (update-ref -> reset --mixed -> per-face checkout), r581 union law for
# append-only faces. CODELY.md = take origin verbatim (post engine-domain-split
# canon, zero-loss audited probe2/probe3: every local-only row verified on
# origin in CODELY or pit-engine/pit-git).
import subprocess, sys, os, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
REPO = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
os.chdir(REPO)
CREATE = 0x08000000

def run(cmd, check=True):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8',
                       errors='replace', creationflags=CREATE)
    if check and r.returncode != 0:
        print('FAIL rc=%d: %s' % (r.returncode, ' '.join(cmd)))
        print(r.stdout[-400:]); print(r.stderr[-600:])
        sys.exit(1)
    return r

# 0. stale untracked inbox duplicate (archived copy is on origin in processed/)
dup = os.path.join('fleet', 'inbox', 'MSG-20261002-1642-bmc-w102-seat.md')
if os.path.exists(dup):
    os.remove(dup)
    print('removed stale inbox duplicate: %s' % dup)

old_main = run(['git', 'rev-parse', 'main']).stdout.strip()
origin_main = run(['git', 'rev-parse', 'origin/main']).stdout.strip()
base = run(['git', 'merge-base', 'main', 'origin/main']).stdout.strip()
print('old_main=%s origin=%s base=%s' % (old_main[:12], origin_main[:12], base[:12]))
assert base == old_main, 'NOT a pure FF window: base != main'

r = run(['git', 'diff', '--no-renames', '--name-status', base, origin_main])
their_mod, their_del = [], []
for l in r.stdout.splitlines():
    if not l.strip():
        continue
    st = l.split('\t')[0]
    p = l.split('\t')[-1]
    (their_del if st.startswith('D') else their_mod).append(p)
print('their_mod=%d their_del=%d' % (len(their_mod), len(their_del)))
assert not their_del, 'deletions in origin window: %s' % their_del[:5]

# 1. union append-only jsonl dirty∩their_mod (EOL-tolerant, r581 canonical form)
APPEND_ONLY = {'results/pool_core_samples.jsonl',
               'results/saturation_engine/history_bm-a.jsonl'}

def union_jsonl(path):
    rb = subprocess.run(['git', 'show', 'origin/main:%s' % path],
                        capture_output=True, creationflags=CREATE)
    assert rb.returncode == 0, 'origin blob missing %s' % path
    ob = rb.stdout
    with open(path, 'rb') as f:
        lb = f.read()
    ol = ob.splitlines()
    okeys = set(l.rstrip(b'\r\n') for l in ol if l.strip())
    new_rows = []
    for l in lb.splitlines(keepends=True):
        if not l.strip() or l.rstrip(b'\r\n') in okeys:
            continue
        obj = json.loads(l)
        assert isinstance(obj, dict), 'non-dict row in local append set: %s' % path
        new_rows.append(l.rstrip(b'\r\n'))
    ub = ob if (not ob or ob.endswith(b'\n')) else ob + b'\n'
    ub += b''.join(nr + b'\n' for nr in new_rows)
    with open(path, 'wb') as f:
        f.write(ub)
    # post-verify: all rows dict + origin rows intact
    for l in ub.splitlines():
        if l.strip():
            assert isinstance(json.loads(l), dict), 'post-verify non-dict %s' % path
    return len(ol), len(new_rows)

unioned = set()
for f in sorted(APPEND_ONLY):
    if os.path.exists(f) and f in their_mod:
        n_o, n_new = union_jsonl(f)
        print('union %s: origin_rows=%d local_new=%d' % (f, n_o, n_new))
        unioned.add(f)

# 2. FF main to origin (r578: update-ref CAS -> reset --mixed)
run(['git', 'update-ref', 'refs/heads/main', origin_main, old_main])
run(['git', 'reset', '--mixed', origin_main])
print('main FF -> %s (reset --mixed done)' % origin_main[:12])

# 3. checkout origin side for their_mod files (shared regen faces + CODELY canon)
#    EXCEPT unioned files (keep union result). bm-b active-write faces are not
#    in their_mod and stay dirty for round-end ride.
co = [f for f in their_mod if f not in unioned]
for i in range(0, len(co), 40):
    run(['git', 'checkout', 'HEAD', '--'] + co[i:i + 40])
print('checkout origin side: %d files' % len(co))

# 4. verify final state
st = run(['git', 'status', '--porcelain']).stdout
print('post status:')
print(st if st else '(clean)')
# assertions: no staged debris, engine telemetry still live-dirty (ride later)
lines = [l for l in st.splitlines() if l[:2] not in (' M', '??')]
assert not lines, 'unexpected staged/merge state: %s' % lines[:5]
keep_dirty = [l[3:] for l in st.splitlines() if l[:2] == ' M']
keep_untracked = [l[3:] for l in st.splitlines() if l[:2] == '??']
print('ride-at-round-end: dirty=%d untracked=%d' % (len(keep_dirty), len(keep_untracked)))
print('S0_R585_OK')
