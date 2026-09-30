import json, sys
from collections import Counter

p = json.load(open(r'results\runnable_pool.json', encoding='utf-8'))
e0 = p['entries'][0]
print('entry keys:', sorted(e0.keys()))
for e in p['entries']:
    nm = str(e.get('name') or e.get('id') or e.get('entry') or e.get('ticket') or '')
    low = nm.lower()
    if any(x in low for x in ('n1', 'lowamp', 'faceb', 'exclusion')):
        sh = e.get('shards', [])
        cnt = Counter((s.get('status') if isinstance(s, dict) else s) for s in sh) if sh else {}
        print('%s | entry_status=%s | shards=%s | wp=%s' % (
            nm, e.get('status'), dict(cnt), (e.get('workers_plan') or {}).get('workers')))
