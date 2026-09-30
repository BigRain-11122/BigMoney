import json, glob, os, datetime
pool = json.load(open('results/runnable_pool.json', encoding='utf-8'))
entries = pool.get('entries', pool) if isinstance(pool, dict) else pool
if isinstance(entries, dict):
    entries = list(entries.values())
print('=== POOL ENTRIES (status overview) ===')
for e in entries:
    eid = e.get('id', e.get('name', '?'))
    st = e.get('status', '?')
    owner = e.get('owner', e.get('claimed_by', ''))
    shards = e.get('shards', [])
    shard_sts = {}
    for s in shards:
        ss = s.get('status', '?')
        shard_sts[ss] = shard_sts.get(ss, 0) + 1
    print(eid, '| entry_status=', st, '| owner=', owner, '| shards=', dict(shard_sts), '| total_shards=', len(shards))
