# -*- coding: utf-8 -*-
"""r305 bm-c S0.5/S2 board scan: orders_ack diff, inbox unread, open tasks, pool state."""
import json, os, glob

root = os.getcwd()
ev = {}

# 1) heartbeat orders_ack
hb = json.load(open('fleet/machines/bm-c.json', encoding='utf-8'))
ack = hb.get('orders_ack', [])
ev['orders_ack_count'] = len(ack)
ev['orders_ack_tail'] = ack[-6:] if isinstance(ack, list) else ack
orders = sorted(os.path.basename(p) for p in glob.glob('fleet/orders/O-*.md'))
if isinstance(ack, list):
    ackset = set(ack)
    unacked = [o for o in orders if o not in ackset]
else:
    unacked = ['(ack not a list)']
ev['orders_unacked'] = unacked

# 2) inbox unread
inbox = []
for p in glob.glob('fleet/inbox/*.md') + glob.glob('fleet/inbox/*.json'):
    inbox.append(os.path.basename(p))
ev['inbox_unread'] = sorted(inbox)

# 3) open tickets
tickets = []
for p in sorted(glob.glob('fleet/tasks/*.json')):
    try:
        t = json.load(open(p, encoding='utf-8'))
        if t.get('status') in ('open', 'claimed', 'in_progress'):
            tickets.append({'file': os.path.basename(p), 'status': t.get('status'),
                            'claimed_by': t.get('claimed_by'), 'title': (t.get('title') or '')[:80],
                            'shards_ct': len(t.get('shards', []) or []),
                            'lane': t.get('lane')})
    except Exception as e:
        tickets.append({'file': os.path.basename(p), 'err': str(e)[:60]})
ev['tickets'] = tickets

# 4) runnable pool state
try:
    pool = json.load(open('results/runnable_pool.json', encoding='utf-8'))
    entries = pool.get('entries', pool if isinstance(pool, list) else [])
    if isinstance(entries, dict):
        entries = list(entries.values())
    ready = []
    for e in entries:
        st = e.get('status')
        lane = e.get('lane') or e.get('lane_free', '')
        if st in ('ready', 'claimed', 'running'):
            ready.append({'id': e.get('id') or e.get('name'), 'status': st,
                          'lane': lane, 'owner': e.get('owner') or e.get('claimed_by'),
                          'shards': len(e.get('shards', []) or [])})
    ev['pool_ready'] = ready[:20]
    ev['pool_total'] = len(entries)
except Exception as e:
    ev['pool_err'] = str(e)[:100]

print(json.dumps(ev, ensure_ascii=False, indent=1))
