# r674 bm-a: origin-truth pool claim check for fund trio NULLS entries (r489/r457 law before any pool face action)
import json, subprocess

r = subprocess.run(['git', 'show', 'origin/main:results/runnable_pool.json'], capture_output=True)
d = json.loads(r.stdout)
ents = d.get('entries', d if isinstance(d, list) else [])
out = {}
for e in ents:
    if isinstance(e, dict) and 'NULLS' in str(e.get('id', e.get('name', ''))):
        out[e.get('id', e.get('name'))] = {k: e.get(k) for k in ('status', 'owner', 'claimed_by', 'owner_since', 'shards', 'note') if k in e}
res = {'origin_tip_pool_nulls_entries': out}
open('results/_r674bma_pool_origin_truth.json', 'wb').write(json.dumps(res, ensure_ascii=False, indent=1).encode('utf-8'))
print(json.dumps(res, ensure_ascii=False)[:1500])
