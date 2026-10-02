import json
p = 'results/saturation_engine/ledger_bm-a.jsonl'
b = open(p, 'rb').read()
lines = b.split(b'\n')
out = [l for l in lines if b'"wave": 59,' not in l]
removed = len(lines) - len(out)
open(p, 'wb').write(b'\n'.join(out))
print('rows removed =', removed, '| remaining lines =', len(out))
rows = [json.loads(l) for l in open(p, encoding='utf-8') if l.strip()]
w59 = [r for r in rows if r.get('wave') == 59]
print('w59 rows left =', len(w59))
print('tail row =', rows[-1].get('wave'), rows[-1].get('shard'), rows[-1].get('done_at'))
