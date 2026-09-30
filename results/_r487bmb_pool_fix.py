import json
from datetime import datetime

PATH = r'results\runnable_pool.json'
now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
LAW = ('ProcessPoolExecutor code-backed, default=cpu_count at launch (O-2026-09-30-2355 '
       'law-1, r486 conversion + parity serial-vs-pool byte-equal PASS); BLAS 1/worker cap; '
       '--workers override')

raw = open(PATH, 'rb').read()
pool = json.loads(raw.decode('utf-8'))
n_wp = n_claim = 0
for e in pool['entries']:
    if 'PERPETUAL-N1-W2-SHARD' not in str(e.get('id', '')):
        continue
    wp = dict(e.get('workers_plan') or {})
    wp['workers'] = 8
    wp['priority'] = 'BelowNormal'
    wp['workers_law'] = LAW
    e['workers_plan'] = wp
    n_wp += 1
    s = e['shards'][0]
    if s.get('owner') in (None, '', 'None'):
        s['owner'] = 'bm-b'
        s['owner_since'] = now
        s['note'] = (s.get('note') or '') + ' | r487 bm-b inline short-burn claim (claim-to-saturation, each shard ~1-2min multicore)'
        n_claim += 1

out = json.dumps(pool, ensure_ascii=False, indent=2).replace('\n', '\r\n')
open(PATH, 'w', encoding='utf-8', newline='').write(out)
print('workers_plan updated:', n_wp, '| shards claimed:', n_claim)
