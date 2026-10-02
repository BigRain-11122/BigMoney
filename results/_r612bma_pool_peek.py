import json
p = json.load(open('results/runnable_pool.json', encoding='utf-8'))
entries = p if isinstance(p, list) else p.get('entries', p)
for e in entries:
    if e.get('status') != 'done':
        print('ENTRY', e.get('id'), 'entry_status=', e.get('status'), 'lane_owner=', e.get('lane_owner'))
        for s in e.get('shards', []):
            print('  shard', s.get('key'), 'status=', s.get('status'), 'owner=', s.get('owner'), 'owner_since=', s.get('owner_since'), 'heartbeat=', s.get('owner_heartbeat'))
