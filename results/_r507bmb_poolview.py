import json
from collections import Counter

p = json.load(open('results/runnable_pool.json', encoding='utf-8'))
ents = p.get('entries', p) if isinstance(p, dict) else p
if isinstance(ents, dict):
    ents = list(ents.values())
c = Counter(e.get('status', '?') for e in ents)
print('POOL_STATUS_COUNTS', dict(c))
for e in ents:
    eid = str(e.get('id', ''))
    st = e.get('status', '?')
    if st in ('ready', 'in_progress', 'running') or 'W9' in eid or 'LOWAMP-P2' in eid or 'N1-W9' in eid:
        sh = e.get('shards', [])
        shst = dict(Counter(s.get('status', '?') for s in sh)) if sh else {}
        owner = e.get('owner_since') or e.get('owner') or ''
        print(eid, '| entry=', st, '| shards=', shst, '| owner=', owner)
