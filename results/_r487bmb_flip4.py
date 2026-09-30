import json
from datetime import datetime

PATH = r'results\runnable_pool.json'
now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
DONE = {8, 9, 10, 11}

raw = open(PATH, 'rb').read()
pool = json.loads(raw.decode('utf-8'))
n = 0
for e in pool['entries']:
    eid = str(e.get('id', ''))
    if 'PERPETUAL-N1-W2-SHARD' not in eid:
        continue
    try:
        idx = int(eid.rsplit('-', 1)[1])
    except ValueError:
        continue
    if idx not in DONE:
        continue
    s = e['shards'][0]
    assert s.get('owner') == 'bm-b', eid
    s['status'] = 'done'
    s['done_at'] = now
    s['done_by'] = 'bm-b r487 inline multicore burn (22s @ 8 workers vs ~2min serial decl)'
    n += 1

out = json.dumps(pool, ensure_ascii=False, indent=2).replace('\n', '\r\n')
open(PATH, 'w', encoding='utf-8', newline='').write(out)
print('flipped done:', n)
