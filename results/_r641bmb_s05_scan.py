# r641 bm-b S0.5 scan: orders diff (wt+origin vs ack), D-19 decisions watermark,
# group orders.md CEO section, watermark_red, open fleet tasks
import json, os, subprocess, hashlib, glob

def git(args):
    return subprocess.run(['git'] + args, capture_output=True, text=True, encoding='utf-8', errors='replace')

ack = set(json.load(open('fleet/machines/bm-b.json', encoding='utf-8'))['orders_ack'])
print('ack_count:', len(ack))

wt_orders = set(os.path.basename(f) for f in glob.glob('fleet/orders/O-*.md'))
r = git(['ls-tree', '-r', '--name-only', 'origin/main', 'fleet/orders/'])
origin_orders = set(os.path.basename(f) for f in r.stdout.splitlines() if f.endswith('.md'))
print('wt_orders:', len(wt_orders), 'origin_orders:', len(origin_orders))
print('origin_only_not_in_wt:', sorted(origin_orders - wt_orders))
print('UNACKED (wt):', sorted(wt_orders - ack))
print('UNACKED (origin-only):', sorted(origin_orders - ack - wt_orders))

# new-in-last-2-commits orders (HEAD..origin/main)
r2 = git(['diff', '--name-only', 'HEAD', 'origin/main', '--', 'fleet/orders/'])
print('orders_changed_in_unmerged_2:', r2.stdout.strip().splitlines())

# D-19: group decisions.md fresh read
grp = None
for p in ['K:/Fluxgroup/FluxGroup', 'C:/Fluxgroup/FluxGroup']:
    if os.path.isdir(os.path.join(p, '.git')):
        grp = p
        break
print('group_tree:', grp)
if grp:
    subprocess.run(['git', '-C', grp, 'fetch', 'origin'], capture_output=True, text=True)
    b = subprocess.run(['git', '-C', grp, 'show', 'origin/main:docs/decisions.md'], capture_output=True)
    sha = hashlib.sha256(b.stdout).hexdigest()
    state = json.load(open('state.json', encoding='utf-8'))
    print('decisions_sha:', sha[:16], 'watermark:', state['last_decisions_sha'][:16], 'MATCH:', sha == state['last_decisions_sha'])
    txt = b.stdout.decode('utf-8', errors='replace')
    if sha != state['last_decisions_sha']:
        # print tail = newest rows
        print('--- decisions.md tail (new rows to consume) ---')
        print(txt[-3000:])
    # group orders.md CEO section
    b2 = subprocess.run(['git', '-C', grp, 'show', 'origin/main:docs/orders.md'], capture_output=True)
    print('--- group orders.md tail ---')
    print(b2.stdout.decode('utf-8', errors='replace')[-1500:])

# watermark red card
try:
    wr = json.load(open('results/watermark_red.json', encoding='utf-8'))
    print('watermark_red:', json.dumps({k: wr.get(k) for k in ('red', 'reason', 'next_pick', 'ts')}, ensure_ascii=False)[:400])
except Exception as e:
    print('watermark_red read fail:', e)

# open fleet tasks
for f in sorted(glob.glob('fleet/tasks/*.json')):
    try:
        t = json.load(open(f, encoding='utf-8'))
        st = t.get('status', '?')
        if st in ('open', 'claimed'):
            print('task:', os.path.basename(f), st, t.get('claimed_by', ''), str(t.get('title', t.get('subject', '')))[:80])
    except Exception as e:
        print('task read fail:', f, e)
