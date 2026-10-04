import json
from collections import Counter

# pit-encoding tolerant read law for shared ledgers
raw = open('results/runnable_pool.json', 'rb').read()
d = json.loads(raw.decode('utf-8', errors='replace'))
items = d if isinstance(d, list) else d.get('items', d.get('shards', []))
if isinstance(items, dict):
    items = list(items.values())
c = Counter(str(i.get('status', '?')) for i in items if isinstance(i, dict))
print('pool status counts:', dict(c))
for i in items:
    if isinstance(i, dict) and str(i.get('status', '')).lower() in ('pending', 'ready', 'queued'):
        print(str(i.get('id', i.get('shard_id', '?')))[:90], '|', i.get('status'), '|', str(i.get('owner', i.get('owner_machine', '')))[:12])
