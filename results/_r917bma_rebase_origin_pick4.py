# -*- coding: utf-8 -*-
# r917 bm-a rebase origin pick-4 (engine absorb-1 15737cfb6 replay) resolve:
# engine faces = three-way newest-ts wins (S2/S3/marker-free WT); history jsonl
# = line-union. Same laws as pick-2 (r294/r910).
import json, subprocess

GIT = r'C:\Program Files\Git\cmd\git.exe'
MARKERS = ('<<<<<<<', '=======', '>>>>>>>')
FLAT = ['results/saturation_engine/face_bm-a.json',
        'results/saturation_engine/state_bm-a.json']
HIST = 'results/saturation_engine/history_bm-a.jsonl'

def raw(stage, path):
    r = subprocess.run([GIT, 'show', ':%s:%s' % (stage, path)], capture_output=True)
    return r.stdout if r.returncode == 0 else b''

def parse(rawb):
    if not rawb:
        return None
    for enc in ('utf-8', 'utf-16'):
        try:
            return json.loads(rawb.decode(enc))
        except Exception:
            pass
    return None

def ts_of(d):
    for k in ('ts', 'time', 'generated', 'updated', 'asof'):
        v = (d or {}).get(k) if isinstance(d, dict) else None
        if isinstance(v, str) and v:
            return v
    return ''

def wt_bytes(path):
    try:
        return open(path, 'rb').read()
    except Exception:
        return b''

for p in FLAT:
    cands = []
    for label, rawb in (('S2', raw(2, p)), ('S3', raw(3, p))):
        d = parse(rawb)
        if d:
            cands.append((ts_of(d), label, rawb))
    wtb = wt_bytes(p)
    if wtb and not any(l.encode() in wtb for l in MARKERS):
        d = parse(wtb)
        if d:
            cands.append((ts_of(d), 'WT', wtb))
    assert cands, '%s no candidate' % p
    best_ts, label, best_raw = max(cands, key=lambda c: c[0])
    open(p, 'wb').write(best_raw)
    print('%s: %s wins ts=%s' % (p, label, best_ts[:19]))

seen, union = set(), []
for stage in (2, 3):
    txt = raw(stage, HIST).decode('utf-8', 'replace')
    for ln in txt.splitlines():
        s = ln.strip()
        if s and s not in seen and not s.startswith(MARKERS):
            seen.add(s)
            union.append(s)
wtb = wt_bytes(HIST)
if wtb and not any(l.encode() in wtb for l in MARKERS):
    for ln in wtb.decode('utf-8', 'replace').splitlines():
        s = ln.strip()
        if s and s not in seen and not s.startswith(MARKERS):
            seen.add(s)
            union.append(s)
def ts_key(s):
    try:
        return ts_of(json.loads(s))
    except Exception:
        return ''
union.sort(key=ts_key)
open(HIST, 'wb').write(('\n'.join(union) + ('\n' if union else '')).encode('utf-8'))
print('%s: line-union %d' % (HIST, len(union)))

r = subprocess.run([GIT, 'add'] + FLAT + [HIST], capture_output=True)
assert r.returncode == 0, r.stderr.decode('utf-8', 'replace')[:300]
print('pick-4 faces resolved + staged')
