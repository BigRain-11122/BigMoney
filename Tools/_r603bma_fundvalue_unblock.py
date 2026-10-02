"""r603 bm-a: MSG-0230 response -- clear 5 FUND-VALUE-P1 fuse sigs
(data_fixed tombstones) + add claim-time host_gates to the 5 ready pool
entries (r509 raw-text anchored insertion, no re-serialization)."""
import json, os, subprocess, sys

FUSE = 'results/crash_fuse.json'
POOL = 'results/runnable_pool.json'
REASON = ("data_fixed: data present on this machine (p1c_stock cache "
          "verified 15 npy); bm-c data-root crash per "
          "MSG-2026-10-03-0230")
GATE = ('   "host_gates": [{"kind": "dir_nonempty", '
        '"path": "Money02/data/cache/p1c_stock", "pattern": "*.npy"}],\r\n')
TARGET_IDS = [
    'FUND-VALUE-P1-CELL-VALUEPE-X2',
    'FUND-VALUE-P1-CELL-VALUEPB-X1',
    'FUND-VALUE-P1-CELL-VALUEPB-X2',
    'FUND-VALUE-P1-NULLS',
    'FUND-VALUE-P1-SENS',
]

# --- 1. fuse clear (shared face only, r504 session-one-off law;
# tombstones suppress stale-lane resurrection per D-03(2)) ---
from datetime import datetime
now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
with open(FUSE, encoding='utf-8') as fh:
    fuse = json.load(fh)
moved = []
for key in list(fuse.get('sigs', {})):
    if 'fund_value_p1' not in key:
        continue
    sig = fuse['sigs'].pop(key)
    tomb = {
        'cleared_ts': now, 'cleared_by': 'bm-a', 'reason': REASON,
        'crashes': int(sig.get('count', 0)),
        'old_code_sha256': sig.get('code_sha256'),
        'bm_c_note': sig.get('note'),
    }
    fuse.setdefault('cleared', {})[key] = tomb
    moved.append(key)
assert len(moved) == 5, f'expected 5 FUND sigs, moved {len(moved)}'
# tombstone must beat every suppressed sig's last event (merge rule)
for k in moved:
    t = fuse['cleared'][k]['cleared_ts']
    assert t > '2026-10-03 02:30:04', k
tmp = FUSE + '.tmp'
with open(tmp, 'w', encoding='utf-8') as fh:  # text mode -> CRLF, indent=1
    json.dump(fuse, fh, ensure_ascii=False, indent=1)
os.replace(tmp, FUSE)
with open(FUSE, encoding='utf-8') as fh:
    chk = json.load(fh)
fv_sigs = [k for k in chk['sigs'] if 'fund_value_p1' in k]
fv_tombs = [k for k in chk.get('cleared', {}) if 'fund_value_p1' in k]
print(f'[fuse] moved {len(moved)} sigs -> cleared; remaining FUND sigs: '
      f'{len(fv_sigs)}; FUND tombstones: {len(fv_tombs)}')
assert not fv_sigs and len(fv_tombs) == 5

# --- 2. pool host_gates: raw-text anchored insertion (r509) ---
raw = open(POOL, 'rb').read()
assert raw.count(b'\r\n') and b'"id": "FUND-VALUE' in raw
txt = raw.decode('utf-8')
inserted = 0
for eid in TARGET_IDS:
    anchor = f'   "id": "{eid}",\r\n'
    i = txt.find(anchor)
    assert i >= 0, f'anchor not found: {eid}'
    j = i + len(anchor)
    assert '"host_gates"' not in txt[j:j + 400], f'already gated: {eid}'
    txt = txt[:j] + GATE + txt[j:]
    inserted += 1
assert inserted == 5
new_raw = txt.encode('utf-8')
open(POOL, 'wb').write(new_raw)
json.loads(new_raw.decode('utf-8'))  # parse gate
print('[pool] host_gates inserted x5 (raw-text, CRLF preserved)')

# --- 3. surgical diff assertion ---
r = subprocess.run(['git', 'diff', '--stat', '--', POOL, FUSE],
                   capture_output=True)
print(r.stdout.decode('utf-8', 'replace'))
rc = subprocess.run(['git', 'diff', '--numstat', '--', POOL],
                    capture_output=True)
line = rc.stdout.decode('utf-8', 'replace').strip()
add = int(line.split()[0]); dele = int(line.split()[1])
assert (add, dele) == (5, 0), f'pool diff not surgical: {line}'
print(f'[assert] pool numstat 5/0 OK; fuse diff = clear move')
