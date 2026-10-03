# r663 bm-a: pool face diagnosis after r437 checkout -- entries by status + lane mirror states
import json, glob, os

with open('results/runnable_pool.json', 'r', encoding='utf-8') as f:
    pool = json.load(f)
units = pool.get('entries') or []
print(f"pool.updated_at={pool.get('updated_at')} n={len(units)}")
from collections import Counter
st = Counter(str(u.get('status')) for u in units)
print('status counts:', dict(st))
recent = [u for u in units if str(u.get('status')) in ('ready', 'burning', 'in_flight', 'claimed', 'running')]
for u in recent[:25]:
    name = str(u.get('name', '?'))
    print(json.dumps({k: u.get(k) for k in ('name', 'status', 'owner', 'owner_since', 'shards', 'shards_done',
                                             'total_shards', 'updated_at') if k in u}, ensure_ascii=False)[:300])
print('---lane mirror files---')
for fp in sorted(glob.glob('results/*lane*') + glob.glob('results/runnable_pool.*') + glob.glob('results/pool*mirror*')):
    print(fp, os.path.getmtime(fp))
