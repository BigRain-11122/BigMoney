# r663 bm-a: pool watch -- NULLS trio + in-flight burn states (schema: entries)
import json

with open('results/runnable_pool.json', 'r', encoding='utf-8') as f:
    pool = json.load(f)

units = pool.get('entries') or []
print(f"updated_at={pool.get('updated_at')} entries={len(units)}")
hits = 0
for u in units:
    name = str(u.get('name', u.get('batch', '?')))
    if any(k in name.upper() for k in ('NULLS', 'FUND', 'DIVLOWVOL', 'QUALITY', 'VALUE')):
        hits += 1
        keys = ('name', 'status', 'owner', 'lane_owner', 'audit', 'shards_total', 'shards_done',
                'total_shards', 'done_shards', 'progress', 'updated_at', 'ts', 'priority', 'claimed_by')
        row = {k: u.get(k) for k in keys if k in u}
        print(json.dumps(row, ensure_ascii=False)[:420])
print(f'hits={hits}')
