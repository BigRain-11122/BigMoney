import json, subprocess, hashlib, os, sys

REPO = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
os.chdir(REPO)

def git(args, cwd=None):
    return subprocess.check_output(['git'] + args, cwd=cwd)

print('=== 1. origin heartbeat bm-b.json ===')
hb = json.loads(git(['show', 'origin/main:fleet/machines/bm-b.json']))
print('origin hb last_seen:', hb['last_seen'], '| round:', hb['round_no'])
print('origin hb current_task:', hb.get('current_task', '')[:120])

print()
print('=== 2. orders diff (worktree orders dir vs origin-hb ack set) ===')
orders = sorted(os.listdir('fleet/orders'))
acks = set(hb['orders_ack'])
unacked = [o for o in orders if o.endswith('.md') and o != 'README.md' and o not in acks]
print('UNACKED count:', len(unacked))
for o in unacked:
    print('  UNACKED:', o)

print()
print('=== 3. D-19 group decisions watermark ===')
tmp = os.path.join(os.environ.get('TEMP', ''), 'fg-dec-bmb')
if not os.path.isdir(os.path.join(tmp, '.git')):
    subprocess.run(['git', 'clone', '--depth', '1', '--filter=blob:none', '--no-checkout',
                    'git@github.com:BigRain-11122/FluxGroup.git', tmp],
                   capture_output=True)
subprocess.run(['git', '-C', tmp, 'fetch', 'origin'], capture_output=True)
dec = git(['-C', tmp, 'show', 'origin/main:docs/decisions.md'])
sha = hashlib.sha256(dec).hexdigest().upper()
state = json.load(open('state.json', encoding='utf-8'))
prev = state.get('last_decisions_sha', '')
print('decisions sha:', sha)
print('state watermark:', prev)
print('D19:', 'MATCH-unchanged' if sha == prev.upper() else 'CHANGED -> consume dispatch board')

print()
print('=== 4. orders.md (group CEO physical-items area) exists? ===')
try:
    o = git(['-C', tmp, 'show', 'origin/main:docs/orders.md']).decode('utf-8', 'replace')
    tail = o.strip().splitlines()[-15:]
    print('\n'.join(tail))
except Exception as e:
    print('orders.md read fail:', e)

print()
print('=== 5. append-only line diffs (local worktree vs origin blob) ===')
APPEND_FILES = [
    'results/pool_core_samples.jsonl',
    'results/pool_dualrun.bm-b.jsonl',
    'results/saturation_engine/history_bm-b.jsonl',
    'results/saturation_engine/ledger_bm-b.jsonl',
]
for f in APPEND_FILES:
    try:
        o_blob = git(['show', 'origin/main:' + f]).decode('utf-8', 'replace').splitlines()
    except Exception:
        o_blob = None
    if os.path.exists(f):
        local = open(f, encoding='utf-8', errors='replace').read().splitlines()
    else:
        local = []
    if o_blob is None:
        print(f, '| origin: ABSENT | local lines:', len(local))
        continue
    o_set = set(o_blob)
    new_local = [l for l in local if l not in o_set]
    print(f, '| origin lines:', len(o_blob), '| local lines:', len(local), '| local-new:', len(new_local))
    for l in new_local[-3:]:
        print('   NEW:', l[:160])

print()
print('=== 6. W49 products on disk vs origin ===')
shard_dir = 'results/p2cal_ext/n1_w49'
disk = sorted(os.listdir(shard_dir)) if os.path.isdir(shard_dir) else []
print('disk shards:', len(disk), disk)
ls_out = git(['ls-tree', '--name-only', 'origin/main', 'results/p2cal_ext/n1_w49/']).decode().split()
print('origin shards:', len(ls_out), [s.split('/')[-1] for s in ls_out])
try:
    git(['cat-file', '-e', 'origin/main:results/perpetual_faces/n1_w49_results.json'])
    print('n1_w49_results.json: ON ORIGIN')
except Exception:
    print('n1_w49_results.json: NOT on origin')
