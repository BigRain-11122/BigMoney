"""r629 bm-a part-2: lane-mirror ghost-claim release (r616 sweep law).
Shared face already released (comma bug fixed). Raw-text per r509.
Note becomes last shard field after owner-row removal -> no trailing comma.
"""
import json
from datetime import datetime

NOW = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
POOLS = ['results/runnable_pool.bm-a.json', 'results/runnable_pool.bm-b.json',
         'results/runnable_pool.bm-c.json']
NULLS_NOTE_OLD = ('     "note": "K=2000 same-mask random-selection nulls '
                  '(headline DIVLOWVOL-YIELDVOL rank universe: yield>0 + '
                  'low-vol half + full eligibility, G-MASK identity), eq '
                  'weights, N=20, rng([20520000,k]); feeds skill_line_v2 '
                  'null_pool",\r\n')
SENS_NOTE_OLD = ('     "note": "K=500 space-filling draws over N{10,15,20} '
                 'x vol_screen_frac{0.5,1.0} (1.0 = no-screen ablation), '
                 'rng([20520500,k]); descriptive face only, no verdict",\r\n')
NULLS_OWNER = ('     "owner": "bm-a",\r\n     "owner_since": '
               '"2026-10-03 13:34:07"\r\n')
SENS_OWNER = ('     "owner": "bm-a",\r\n     "owner_since": '
              '"2026-10-03 13:38:15"\r\n')
NULLS_TRAIL = (f' | rel-bm-a-r629 {NOW}: ghost-claim release (burn killed '
               '13:48 r625 off-caliber era; cache T-156 verified 14:39) -- '
               'bm-b rightful burner in flight per division (r617-r620); '
               'fuse keep-blocked on bm-a')
SENS_TRAIL = (f' | rel-bm-a-r629 {NOW}: ghost-claim release (burn killed '
              '13:48 r625 off-caliber era; cache T-156 verified 14:39; fuse '
              'CLEARED r629) -- first claimer re-burns via daemon')

for POOL in POOLS:
    raw = open(POOL, 'rb').read()
    txt = raw.decode('utf-8')
    assert '\r\n' in txt, f'{POOL}: expected CRLF'
    for anchor, name in ((NULLS_NOTE_OLD, 'nulls note'), (SENS_NOTE_OLD, 'sens note'),
                         (NULLS_OWNER, 'nulls owner'), (SENS_OWNER, 'sens owner')):
        c = txt.count(anchor)
        assert c == 1, f'{POOL}: {name} anchor x{c}'
    txt = txt.replace(NULLS_NOTE_OLD, NULLS_NOTE_OLD[:-5] + NULLS_TRAIL + '"\r\n')
    txt = txt.replace(SENS_NOTE_OLD, SENS_NOTE_OLD[:-5] + SENS_TRAIL + '"\r\n')
    txt = txt.replace(NULLS_OWNER, '')
    txt = txt.replace(SENS_OWNER, '')
    open(POOL, 'wb').write(txt.encode('utf-8'))
    json.loads(txt)
    print(f'[pool] {POOL}: 2 ghost claims released (raw-text, parses OK)')
print('[done] lane sweep complete')
