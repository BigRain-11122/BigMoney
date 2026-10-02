# r585 bm-b surgical push (r523 law): payload = origin/main tree + my commit's
# blobs (my_files minus the 13 shared derive faces taken origin-side) + 2
# whitelisted fleet/inbox MSG moves (processed copies carried in payload).
# Deletion-set assertion: exactly the 2 inbox files, whitelisted move pattern
# (processed/ copies present in push tree). Working-tree live-write faces stay
# out of the payload (ride the freeze commit).
import subprocess, sys, os, time
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

mine = run(['git', 'rev-parse', 'main']).stdout.strip()
old_main = mine
origin = run(['git', 'rev-parse', 'origin/main']).stdout.strip()
base = '565a6b254'
print('mine=%s origin=%s' % (mine[:10], origin[:10]))

r = run(['git', 'diff', '--no-renames', '--name-status', base, mine])
my_files = [l.split('\t')[-1] for l in r.stdout.splitlines()
            if l.strip() and not l.startswith('D')]
r = run(['git', 'diff', '--no-renames', '--name-status', base, origin])
their_mod = [l.split('\t')[-1] for l in r.stdout.splitlines()
             if l.strip() and not l.startswith('D')]
inter = sorted(set(my_files) & set(their_mod))
INBOX_MOVES = ['fleet/inbox/MSG-20261002-1712-bma-w104-seat.md',
               'fleet/inbox/MSG-20261002-1738-bmc-w105-seat.md']
# processed copies must be in my_files (they carry the move whitelist)
for f in INBOX_MOVES:
    assert f.replace('inbox/', 'inbox/processed/') in my_files, \
        'processed copy missing from my delta: %s' % f
payload_files = [f for f in my_files if f not in inter]
print('my_files=%d inter(origin-side)=%d payload_files=%d inbox_moves=%d'
      % (len(my_files), len(inter), len(payload_files), len(INBOX_MOVES)))

tmp_index = os.path.join(REPO, '.git', 'codely-tmp-index-r585push')
if os.path.exists(tmp_index):
    os.remove(tmp_index)
env = dict(os.environ, GIT_INDEX_FILE=tmp_index)
run(['git', 'read-tree', origin], env=env)

payload = 0
for f in payload_files:
    # blob from MY commit tree (not working tree: live-write faces stay out)
    ls = raw(['git', 'ls-tree', mine, '--', f])
    parts = ls.stdout.decode('utf-8').split()
    assert len(parts) >= 3 and parts[1] == 'blob', \
        'ls-tree shape fail (r366 law) for %s: %r' % (f, ls.stdout[:80])
    sha = parts[2]
    run(['git', 'update-index', '--add', '--cacheinfo',
         '100644,%s,%s' % (sha, f)], env=env)
    payload += 1
for f in INBOX_MOVES:
    run(['git', 'update-index', '--force-remove', f], env=env)
tree = run(['git', 'write-tree'], env=env).stdout.strip()

msg_path = os.path.join(REPO, '.codely-cli', 'scratch', 'msg_r585_surgery.txt')
with open(msg_path, 'w', encoding='utf-8') as fh:
    fh.write('round 585 bm-b: surgical payload onto origin/main (r523 law; '
             'claw r374 fork-base artifact resolved by integration not bypass) '
             '-- carry W100 finalize + W103 shards 8-11 + W106 seat + telemetry '
             'rides + tools; 13 shared derive faces taken origin-side (fresher '
             're-derive, next round re-derives); fleet/inbox W104/W105 seat MSGs '
             'consumed+archived to processed (whitelisted move pattern, processed '
             'copies in tree) [via bm-b r585]')
newc = raw(['git', 'commit-tree', tree, '-p', origin, '-F', msg_path],
           env=env).stdout.decode('utf-8').strip()
assert len(newc) == 40, 'commit-tree sha shape fail: %r' % newc
print('newc=%s' % newc[:12])

# r532/r366 assertions: tree-delta vs origin
r = run(['git', 'diff', '--no-renames', '--name-status', origin, newc])
dels, adds, mods = [], 0, 0
for l in r.stdout.splitlines():
    if not l.strip(): continue
    st = l.split('\t')[0]; p = l.split('\t')[-1]
    if st.startswith('D'): dels.append(p)
    elif st.startswith('A'): adds += 1
    else: mods += 1
assert sorted(dels) == sorted(INBOX_MOVES), \
    'deletion-set drift: %s' % dels
assert adds + mods <= payload, 'payload-count breach: %d+%d > %d' % (adds, mods, payload)
print('tree-delta: A=%d M=%d D=%d (D==inbox moves whitelist) payload=%d'
      % (adds, mods, len(dels), payload))

r = run(['git', 'push', 'origin', '%s:refs/heads/main' % newc], check=False)
if r.returncode != 0:
    print('push rejected: %s' % r.stderr.strip()[-400:])
    sys.exit(2)
print('pushed %s' % newc[:12])
run(['git', 'update-ref', 'refs/heads/main', newc, old_main])
run(['git', 'reset', '--mixed', newc])
# working-tree reconciliation (r578 law): checkout origin-side for their_mod
# faces not in my payload (their W104/W105 freeze five-faces + inter derive
# faces) so the tree matches the pushed state for the freeze work next.
co = [f for f in sorted(set(their_mod)) if f not in payload_files]
for i in range(0, len(co), 40):
    run(['git', 'checkout', 'HEAD', '--'] + co[i:i + 40])
print('checkout synced: %d their-side files' % len(co))
st = run(['git', 'status', '--porcelain']).stdout
print('post status:')
print(st if st else '(clean)')
# delivery proof
rb = raw(['git', 'ls-tree', 'origin/main', '--name-only',
          'results/perpetual_faces/n1_w100_results.json'])
assert rb.stdout.strip(), 'DELIVERY PROOF FAIL: W100 finalize not on origin'
print('delivery proof: n1_w100_results.json on origin')
print('SURGERY_PUSH_R585_OK')
