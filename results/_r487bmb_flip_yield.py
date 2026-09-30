"""r487 bm-b rebase step-3 pool merge: yield my shard 8-11 claims to bm-a (commit-time
order 01:34-01:36 origin vs my 01:40 local-unpushed, fleet/README sec.4), but record
the honest done state: checkpoints for shards 8-11 are committed in this very commit
(bm-b inline multicore burn 01:41-01:42, 22s each @ 8 workers, deterministic
byte-equal vs bm-a's parallel burn). owner stays bm-a; done flip + attribution note.
"""
import json
from datetime import datetime

PATH = r'results\runnable_pool.json'
NOW = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
DONE = {8, 9, 10, 11}

pool = json.loads(open(PATH, 'rb').read().decode('utf-8'))
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
    assert s.get('owner') == 'bm-a', (eid, s.get('owner'))  # yield: bm-a claim stands
    s['status'] = 'done'
    s['done_at'] = NOW
    s['done_by'] = ('bm-b r487 inline multicore burn 01:41-01:42 (22s each @ 8 workers, '
                    'checkpoints in-commit byte-equal; claim race yielded to bm-a per '
                    'fleet/README sec.4 commit-time order)')
    n += 1

out = json.dumps(pool, ensure_ascii=False, indent=2).replace('\n', '\r\n')
open(PATH, 'w', encoding='utf-8', newline='').write(out)
json.loads(open(PATH, 'rb').read().decode('utf-8'))
print('yield-merge flipped done:', n)
