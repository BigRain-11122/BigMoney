import subprocess, sys, json, hashlib, os

def git(*args):
    r = subprocess.run(['git'] + list(args), capture_output=True, text=True,
                       encoding='utf-8', errors='replace')
    return r

st = json.load(open('results/_r604bmb_ring_state.json'))
d_restore = st['d_restore']
origin_m_restore = [
    'CODELY.md',
    'fleet/tasks/T-2026-10-02-147-P1.json',
    'fleet/tasks/T-2026-10-03-152-P1.json',
    'knowledge/METHODOLOGY_ASSETS.md',
    'research/CLOSED_FAMILIES.md',
    'research/LOWAMP-DEEP-P1.md',
    'scripts/perpetual_faces_n4.py',
    'scripts/science_gates.py',
]
restore_all = d_restore + origin_m_restore
print('total restore faces:', len(restore_all))

# r595 law: verify each restore face is present in ORIGIN tree first
ls = git('ls-tree', 'origin/main', '--name-only', '--', *restore_all)
present = set(l for l in ls.stdout.splitlines() if l.strip())
missing = [p for p in restore_all if p not in present]
if missing:
    print('FATAL: faces NOT in origin tree (true deletions?), abort:', missing)
    sys.exit(4)
print('all restore faces present in origin tree OK')

# inbox stale-twin blob identity check (r586 law) before deleting local copies
pairs = [
    ('fleet/inbox/MSG-2026-10-03-0350-bmb-bmc-quality-faces-transfer.md',
     'fleet/inbox/processed/MSG-2026-10-03-0350-bmb-bmc-quality-faces-transfer.md'),
    ('fleet/inbox/MSG-2026-10-03-0436-bma-bmc-w14-entry-verdict.md',
     'fleet/inbox/processed/MSG-2026-10-03-0436-bma-bmc-w14-entry-verdict.md'),
]
for local, processed in pairs:
    if not os.path.exists(local):
        print('local already gone:', local)
        continue
    h_local = hashlib.sha256(open(local, 'rb').read()).hexdigest()[:16]
    r = git('show', 'origin/main:' + processed)
    h_origin = hashlib.sha256(r.stdout.encode('utf-8', 'replace')).hexdigest()[:16]
    same = h_local == h_origin
    print(os.path.basename(local), 'local=' + h_local, 'origin=' + h_origin,
          'IDENTICAL' if same else 'DIFFERS')
    if same:
        os.remove(local)
        print('  local stale copy deleted (zero-info-loss r586)')
    else:
        print('  KEEP local (differs -- needs adjudication)')

# restore: index already re-anchored at NEW; working tree lacks D faces / holds old M faces
r = git('checkout', '--', *restore_all)
print('checkout restore rc=', r.returncode, r.stderr.strip()[:300])

r = git('status', '--porcelain')
lines = [l for l in r.stdout.splitlines() if l.strip()]
bad_d = [l for l in lines if 'D' in l[:2]]
print('remaining D rows after restore:', len(bad_d))
for l in bad_d[:10]:
    print('  still-D:', l)
still = [l for l in lines if l[3:].strip() in origin_m_restore and not l.startswith('?')]
print('origin-M faces still dirty after restore:', len(still))
for l in still[:10]:
    print('  still-M:', l)
print('phase B restore complete')
