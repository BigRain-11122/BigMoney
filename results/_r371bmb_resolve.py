# r371 bm-b push-storm resolver (rebase UU 10-face batch, cb1bc4dd replay onto origin 255f521d..ff77a9d0)
# Skill: bigmoney-conflict-resolve. Laws: r188/r208/R209/R216/r100/R350/r185/r140.
# Reuse of in-tree _r369bmb_resolve.py (resolver-reuse priority, bm-c r149 law).
# Classifier: 8 auto-classified + 2 UNKNOWN fail-closed -> hand-qualified below.
#   UNKNOWN results/scorecard_v1.json + results/strategy_scorecard.json:
#   deterministic L1 re-derive idempotent faces (S6 chain law: only generated/
#   elapsed_sec runtime metadata drift), snapshot semantics take-new by ts --
#   exact precedent = r369 resolver SNAPSHOTS list (same two files, same storm shape).
# Probe STAGED blobs (:2:/:3:) only, never working tree. In rebase: :2:=upstream(origin=bm-a r395), :3:=replayed(mine r371).
import subprocess, json, re

def staged(path, stage):
    b = subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True).stdout
    if not b:
        r = subprocess.run(['git', 'cat-file', '-p', f':{stage}:{path}'], capture_output=True)
        b = r.stdout
    return b

TS_RE = re.compile(r'20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2})?')

def wallclock_max_json(obj, best=None):
    if best is None:
        best = ['']
    if isinstance(obj, dict):
        for k, v in obj.items():
            nk = re.sub(r'[_\-]', '', str(k)).lower()
            if isinstance(v, str) and any(nk.startswith(p) for p in
                    ('asof', 'updated', 'tsgenerated', 'generated', 'timestamp', 'ts', 'time', 'lasttick', 'asatscan')):
                m = TS_RE.search(v)
                if m and re.match(r'^20\d{2}-', m.group(0)):
                    s = m.group(0).replace(' ', 'T')
                    if s > best[0]:
                        best[0] = s
            else:
                wallclock_max_json(v, best)
    elif isinstance(obj, list):
        for v in obj:
            wallclock_max_json(v, best)
    return best[0]

def wallclock_max_text(raw):
    cands = [m.group(0).replace(' ', 'T') for m in TS_RE.finditer(raw)]
    return max(cands) if cands else ''

def probe_side(path, stage):
    b = staged(path, stage)
    try:
        return wallclock_max_json(json.loads(b.decode('utf-8')))
    except Exception:
        return wallclock_max_text(b.decode('utf-8', errors='replace'))

SNAPSHOTS = [
    'results/dashboard_status.json',
    'results/futures_update_status.json',
    'results/lhb_update_status.json',
    'results/scorecard_v1.json',       # classifier UNKNOWN -> hand-qualified snapshot (r369 precedent)
    'results/strategy_scorecard.json',  # classifier UNKNOWN -> hand-qualified snapshot (r369 precedent)
    'results/token_usage.json',
    'results/update_status.json',
]

LEDGERS = {'results/compute_audit.json': 'history',
           'results/regime_state.json': 'transitions'}

JS_WRAPPER = 'results/dashboard_status.js'   # R209: whole-bytes take-side, NEVER strip wrapper

def row_key(r):
    return json.dumps(r, sort_keys=True, ensure_ascii=False)

verdicts = []

for p in SNAPSHOTS:
    t2, t3 = probe_side(p, 2), probe_side(p, 3)
    if t2 and (not t3 or t2 >= t3):   # tie -> stage-2 (r140)
        side, ts = 2, t2
    else:
        side, ts = 3, t3
    data = staged(p, side)
    json.loads(data.decode('utf-8'))  # parse-verify before write (r185)
    open(p, 'wb').write(data)
    verdicts.append(f'{p} | take stage-{side} | ts {ts}')

for p, lkey in LEDGERS.items():
    a = json.loads(staged(p, 2).decode('utf-8'))
    b = json.loads(staged(p, 3).decode('utf-8'))
    la, lb = a.get(lkey, []), b.get(lkey, [])
    seen, union = set(), []
    for r in la + lb:
        k = row_key(r)
        if k not in seen:
            seen.add(k)
            union.append(r)
    ts_a = a.get('ts') or wallclock_max_json(a)
    ts_b = b.get('ts') or wallclock_max_json(b)
    state_src = a if (ts_a and (not ts_b or str(ts_a) >= str(ts_b))) else b
    out = dict(state_src)
    out[lkey] = union
    json.loads(json.dumps(out))  # parse-verify
    open(p, 'w', encoding='utf-8', newline='\n').write(json.dumps(out, ensure_ascii=False, indent=1) + '\n')
    verdicts.append(f'{p} | ledger union {len(la)}+{len(lb)}->{len(union)} | state ts {state_src.get("ts")}')

# js-wrapper-snapshot (R209): whole-bytes take-side by internal ts probe; wrapper preserved verbatim
t2, t3 = probe_side(JS_WRAPPER, 2), probe_side(JS_WRAPPER, 3)
if t2 and (not t3 or t2 >= t3):
    side, ts = 2, t2
else:
    side, ts = 3, t3
data = staged(JS_WRAPPER, side)
raw = data.decode('utf-8')
assert 'window.DASH_DATA' in raw, 'wrapper missing after take-side'
open(JS_WRAPPER, 'wb').write(data)
verdicts.append(f'{JS_WRAPPER} | whole-bytes take stage-{side} | ts {ts} | wrapper intact')

print('\n'.join(verdicts))
# final sweep: no conflict markers anywhere in resolved faces
for p in SNAPSHOTS + list(LEDGERS) + [JS_WRAPPER]:
    rb = open(p, 'rb').read()
    assert b'<<<<<<<' not in rb and b'>>>>>>>' not in rb, f'marker residue {p}'
print(f'ALL {len(SNAPSHOTS)+len(LEDGERS)+1} FACES RESOLVED, parse-verified, marker-free')
