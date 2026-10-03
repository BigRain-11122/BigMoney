"""r629 bm-a part-3: host_gates on shared-face divlowvol entries (r603 pattern).
Prevents data-root crash claims on cache-less machines (bm-c precedent r393).
"""
import json

POOL = 'results/runnable_pool.json'
GATE = ('   "host_gates": [{"kind": "dir_nonempty", '
        '"path": "Money02/data/cache/p1c_stock", "pattern": "*.npy"}],\r\n')
txt = open(POOL, 'rb').read().decode('utf-8')
inserted = 0
for eid in ('FUND-DIVLOWVOL-P1-NULLS', 'FUND-DIVLOWVOL-P1-SENS'):
    anchor = '   "id": "' + eid + '",\r\n'
    i = txt.find(anchor)
    assert i >= 0, f'anchor not found: {eid}'
    j = i + len(anchor)
    assert '"host_gates"' not in txt[j:j + 400], f'already gated: {eid}'
    txt = txt[:j] + GATE + txt[j:]
    inserted += 1
open(POOL, 'wb').write(txt.encode('utf-8'))
json.loads(txt)
print(f'[pool] host_gates inserted x{inserted} (shared face, parses OK)')
