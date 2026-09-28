# r152 bm-c push-storm resolver (rebase UU 9-face batch, c4563d8c replay onto origin 255f021d..33e129dd)
# Reuse of in-tree _r371bmb_resolve.py (resolver-reuse priority, bm-c r149 law; same storm family:
# bm-b r371 addendum landed 09:26 vs my S6 derive batch 09:23-09:27 -- identical snapshot/ledger faces).
# Laws: r188/r208/R209/r100/R350/r185/r140/r150 (staged blobs only, never working tree).
# In rebase: :2: = upstream (origin = bm-b r371 addendum + tick), :3: = replayed (mine r152).
# Faces: 7 snapshots take-new-by-ts (tie -> stage-2 per r140) + 2 ledgers identity-union zero-loss.
#   daily_report REPORT-2026-09-28.{json,md} = idempotent same-day re-derive (S6 daily_report law);
#   fundamental_b_layer_filter = deterministic L1 re-derive; token_usage = snapshot per r371 canon.
#   compute_audit history + regime_state transitions = append-only union (r188 family).
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
    'docs/daily_report/REPORT-2026-09-28.json',
    'docs/daily_report/REPORT-2026-09-28.md',
    'results/fundamental_b_layer_filter.json',
    'results/futures_update_status.json',
    'results/lhb_update_status.json',
    'results/token_usage.json',
    'results/update_status.json',
]

LEDGERS = {'results/compute_audit.json': 'history',
           'results/regime_state.json': 'transitions'}

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
    if p.endswith('.json'):
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

print('\n'.join(verdicts))
for p in SNAPSHOTS + list(LEDGERS):
    rb = open(p, 'rb').read()
    assert b'<<<<<<<' not in rb and b'>>>>>>>' not in rb, f'marker residue {p}'
print(f'ALL {len(SNAPSHOTS)+len(LEDGERS)} FACES RESOLVED, parse-verified, marker-free')
