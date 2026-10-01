import json, io, os, glob
pool = json.load(io.open('results/runnable_pool.json', encoding='utf-8'))
entries = pool.get('entries') or pool
if isinstance(entries, dict):
    entries = list(entries.values())
for e in entries:
    eid = str(e.get('id') or e.get('entry_id') or '')
    if 'LOWAMP-P3' in eid:
        shards = e.get('shards') or []
        shard_states = [(s.get('id') or s.get('shard') or '?', s.get('status'), (s.get('owner') or '')) for s in shards]
        print('ENTRY', eid, '| status:', e.get('status'), '| owner:', e.get('owner'), '| shards:', shard_states)
print('--- products on disk ---')
for d in sorted(glob.glob('results/lowamp_p3/*')):
    print(os.path.basename(d), os.path.getmtime(d) and round(os.path.getmtime(d)))
