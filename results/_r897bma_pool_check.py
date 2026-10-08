import json, collections, sys
d = json.load(open('results/runnable_pool.json', encoding='utf-8'))
if isinstance(d, dict):
    items = d.get('items', d.get('entries', []))
else:
    items = d
print('total', len(items))
c = collections.Counter(i.get('status') for i in items)
print(dict(c))
claimable = [i for i in items if i.get('status') == 'ready']
waiting = [i for i in items if i.get('status') == 'waiting']
print('claimable(ready):', len(claimable))
for i in items:
    print(i.get('status'), '|', i.get('id'), '|', str(i.get('lane_owner'))[:40], '|', str(i.get('description') or i.get('title') or '')[:80])
