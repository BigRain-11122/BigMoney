# r979 S0 UU resolver: 10 faces per laws
# rebase context: ours=origin/main(upstream), theirs=6a8d5f58f (bm-a S0-b absorb)
# laws: ts-probe newer-wins (status faces) / history-union (compute_audit) /
#       add-add same-day regen ts-probe, tie->origin side (r140 law) /
#       token_usage per-machine union / deterministic regen newer-or-identical
import json, subprocess, sys, hashlib

def blob(side, path):
    # side: 'ours' (origin) or 'theirs' (mine)
    if side == 'ours':
        ref = 'origin/main'
    else:
        ref = '6a8d5f58f'
    out = subprocess.run(['git', 'show', f'{ref}:{path}'], capture_output=True)
    return out.stdout

def work(path):
    with open(path, 'rb') as f:
        return f.read()

def write(path, data: bytes):
    with open(path, 'wb') as f:
        f.write(data)

def jload(b):
    try:
        return json.loads(b.decode('utf-8-sig'))
    except Exception:
        return None

def ts_of(obj):
    if not isinstance(obj, dict):
        return ''
    for k in ('ts', 'generated', 'generated_at', 'updated', 'asof', 'date'):
        if k in obj and isinstance(obj[k], str):
            return obj[k]
    return ''

RESOLVED = []
EVID = []

# 1) ts-probe newer-wins faces (single-face regen, idempotent deterministic)
TS_FACES = [
    'results/_attrition_guard_scan.json',
    'results/fundamental_b_layer_filter.json',
    'docs/daily_report/REPORT-2026-10-14.json',
    'docs/live_usage/LIVE-2026-10-14.json',
    'docs/live_usage/LIVE-latest.json',
]
for p in TS_FACES:
    o = jload(blob('ours', p)); t = jload(blob('theirs', p))
    if o is None and t is None:
        # binary-ish or md; byte-compare
        ob, tb = blob('ours', p), blob('theirs', p)
        pick = 'ours' if ob == tb or len(ob) >= len(tb) else 'theirs'
        write(p, blob(pick, p)); RESOLVED.append((p, 'byte-identical-or-origin', pick)); continue
    ots, tts = ts_of(o), ts_of(t)
    if ots == tts:
        pick = 'ours'  # r140 tie law: origin side
        why = f'tie ts={ots} -> origin'
    elif ots > tts:
        pick = 'ours'; why = f'origin newer ({ots} > {tts})'
    else:
        pick = 'theirs'; why = f'local newer ({tts} > {ots})'
    write(p, blob(pick, p))
    RESOLVED.append((p, 'ts-probe', why))

# 2) md twins of the json faces: follow the json pick (same regen run writes both)
MD_TWINS = {
    'docs/daily_report/REPORT-2026-10-14.md': 'docs/daily_report/REPORT-2026-10-14.json',
    'docs/live_usage/LIVE-2026-10-14.md': 'docs/live_usage/LIVE-2026-10-14.json',
    'docs/live_usage/LIVE-latest.md': 'docs/live_usage/LIVE-latest.json',
}
for mdp, jp in MD_TWINS.items():
    pick = next(r[2] for r in RESOLVED if r[0] == jp)
    # extract pick side name from evidence tuple
    pick_side = 'ours'
    for r in RESOLVED:
        if r[0] == jp:
            pick_side = 'theirs' if 'local newer' in r[2] else 'ours'
    write(mdp, blob(pick_side, mdp))
    RESOLVED.append((mdp, 'md-twin-follow-json', pick_side))

# 3) compute_audit.json: history union by ts key
p = 'results/compute_audit.json'
o = jload(blob('ours', p)); t = jload(blob('theirs', p))
if isinstance(o, dict) and isinstance(t, dict) and 'history' in o and 'history' in t:
    key_ts = lambda h: h.get('ts', h.get('generated', ''))
    merged = {key_ts(h): h for h in o['history']}
    for h in t['history']:
        k = key_ts(h)
        if k not in merged or str(h) > str(merged[k]):
            merged[k] = h
    hist = sorted(merged.values(), key=key_ts)
    base = dict(o)
    base['history'] = hist
    # carry other top fields: newer-wins on ts
    if ts_of(t) > ts_of(o):
        for k, v in t.items():
            if k != 'history':
                base[k] = v
    base['ts'] = max(ts_of(o), ts_of(t))
    write(p, json.dumps(base, ensure_ascii=False, indent=2).encode('utf-8'))
    RESOLVED.append((p, 'history-union', f'{len(hist)} rows unioned'))
else:
    # fallback: ts newer-wins
    ots, tts = ts_of(o), ts_of(t)
    pick = 'theirs' if tts > ots else 'ours'
    write(p, blob(pick, p))
    RESOLVED.append((p, 'fallback-newer', pick))

# 4) token_usage.json: per-machine union
p = 'results/token_usage.json'
o = jload(blob('ours', p)); t = jload(blob('theirs', p))
if isinstance(o, dict) and isinstance(t, dict):
    merged = dict(o)
    for k, v in t.items():
        if k not in merged:
            merged[k] = v
        elif isinstance(v, (int, float)) and isinstance(merged[k], (int, float)):
            merged[k] = max(merged[k], v) if 'total' in k.lower() else merged[k]
        elif isinstance(v, dict) and isinstance(merged[k], dict):
            for kk, vv in v.items():
                if kk not in merged[k]:
                    merged[k][kk] = vv
                elif isinstance(vv, (int, float)) and isinstance(merged[k][kk], (int, float)):
                    merged[k][kk] = max(merged[k][kk], vv)
    write(p, json.dumps(merged, ensure_ascii=False, indent=2).encode('utf-8'))
    RESOLVED.append((p, 'per-machine-union', f'{len(merged)} keys'))
else:
    pick = 'theirs' if ts_of(t) > ts_of(o) else 'ours'
    write(p, blob(pick, p))
    RESOLVED.append((p, 'fallback-newer', pick))

for p, law, why in RESOLVED:
    EVID.append(f'{p} | {law} | {why}')
print(json.dumps(EVID, ensure_ascii=False, indent=1))
# marker check: no conflict markers in resolved files
bad = []
for p, _, _ in RESOLVED:
    if b'<<<<<<<' in work(p):
        bad.append(p)
print('CONFLICT_MARKER_CHECK:', 'FAIL ' + str(bad) if bad else 'CLEAN')
