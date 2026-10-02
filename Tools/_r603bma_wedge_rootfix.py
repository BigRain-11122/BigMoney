"""r603 bm-a part-2: wedge root-fix -- strip the 4 phantom bm-c claim
rows (resurrected from bm-b's stale lane by its 0951ab44a settle) from
the shared pool AND bm-b's lane (resurrection source), insert
claim-time host_gates on the 5 FUND-VALUE-P1 entries, preserve bm-b's
fresh SENS claim. Raw-text surgical (r509), origin-blob base (r388
execution-time truth), byte-level assertions."""
import json, os, subprocess, sys

PHANTOM_SINCE = ['02:06:04', '02:07:12', '02:08:04', '02:09:11']
STRIP = [',\r\n     "owner": "bm-c",\r\n     "owner_since": '
         f'"2026-10-03 {v}"' for v in PHANTOM_SINCE]
GATE = ('   "host_gates": [{"kind": "dir_nonempty", '
        '"path": "Money02/data/cache/p1c_stock", "pattern": "*.npy"}],\r\n')
GATE_IDS = [
    'FUND-VALUE-P1-CELL-VALUEPE-X2',
    'FUND-VALUE-P1-CELL-VALUEPB-X1',
    'FUND-VALUE-P1-CELL-VALUEPB-X2',
    'FUND-VALUE-P1-NULLS',
    'FUND-VALUE-P1-SENS',
]
POOL = 'results/runnable_pool.json'
LANE_B = 'results/runnable_pool.bm-b.json'


def blob(path):
    r = subprocess.run(['git', 'show', f'origin/main:{path}'],
                       capture_output=True)
    assert r.returncode == 0, r.stderr.decode()[:200]
    return r.stdout.decode('utf-8')


def strip_phantoms(txt, label):
    for pat in STRIP:
        n = txt.count(pat)
        assert n == 1, f'{label}: pattern not unique ({n}): {pat[:60]}'
        txt = txt.replace(pat, '')
    return txt


# --- shared pool: origin base -> strip phantoms + insert gates ---
pool = blob(POOL)
assert pool.count('"owner_since": "2026-10-03 02:0') == 4
pool = strip_phantoms(pool, 'shared')
ins = 0
for eid in GATE_IDS:
    anchor = f'   "id": "{eid}",\r\n'
    i = pool.find(anchor)
    assert i >= 0, f'anchor missing {eid}'
    j = i + len(anchor)
    assert '"host_gates"' not in pool[j:j + 400], f'already gated {eid}'
    pool = pool[:j] + GATE + pool[j:]
    ins += 1
assert ins == 5
with open(POOL, 'wb') as fh:
    fh.write(pool.encode('utf-8'))
p = json.loads(pool)
for e in p['entries']:
    if 'FUND-VALUE' in e['id']:
        s = e['shards'][0]
        print(' shared:', e['id'][:38], '| gates', ('host_gates' in e),
              '| owner', s.get('owner'), '| since', s.get('owner_since'),
              '| status', s.get('status'))
        if e['id'] == 'FUND-VALUE-P1-CELL-VALUEPE-X1':
            assert s.get('status') == 'done' and s.get('owner') == 'bm-c'
        elif e['id'] == 'FUND-VALUE-P1-SENS':
            assert s.get('owner') == 'bm-b' and s.get('owner_since')
        else:
            assert s.get('owner') is None and s.get('owner_since') is None, \
                f'phantom survived: {e["id"]}'
            assert 'host_gates' in e

# --- bm-b lane: strip phantoms only (resurrection source) ---
lane = blob(LANE_B)
assert lane.count('"owner_since": "2026-10-03 02:0') == 4
lane = strip_phantoms(lane, 'lane-bm-b')
with open(LANE_B, 'wb') as fh:
    fh.write(lane.encode('utf-8'))
lb = json.loads(lane)
rows = {(e['id']): (e['shards'][0].get('owner'),
                    e['shards'][0].get('owner_since'))
        for e in lb['entries'] if 'FUND-VALUE' in e['id']}
print(' lane-bm-b FUND rows:', {k[17:30]: v for k, v in rows.items()})
for k, (ow, since) in rows.items():
    if k == 'FUND-VALUE-P1-SENS':
        assert ow == 'bm-b'
    elif k != 'FUND-VALUE-P1-CELL-VALUEPE-X1':
        assert ow is None and since is None, f'lane phantom survived {k}'

# --- bm-a lane: re-mirror from fixed shared bytes ---
sys.path.insert(0, 'Tools')
import autofill
autofill._pool_lane_sync()
la = json.loads(open('results/runnable_pool.bm-a.json', 'rb')
                .read().decode('utf-8'))
frows = [e for e in la['entries'] if 'FUND-VALUE' in e['id']]
assert len(frows) == 6 and all('host_gates' in e for e in frows
                               if e['id'] != 'FUND-VALUE-P1-CELL-VALUEPE-X1')
print(' lane-bm-a re-mirrored (gates carried)')
print('[OK] wedge stripped in shared + bm-b lane; gates x5; bm-b SENS kept')
