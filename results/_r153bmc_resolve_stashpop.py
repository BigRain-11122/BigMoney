# r153 bm-c stash-pop storm resolver (9-UU: HEAD=bmb r372 S6 faces 09:35-09:44 vs stash=mine r153 S6 faces 09:39-09:40)
# Reuse of _r152bmc_resolve_push.py / _r371bmb family logic, adapted for STASH-POP marker faces:
#   side-A = git show HEAD:<path>       (bmb r372, landed 258d084f)
#   side-B = git show stash@{0}:<path>  (my r153 S6 derive batch, autostash f9b82692)
# Laws: r188/r208/R209/r100/R350/r185/r140 (staged blobs only, never working-tree marker parse).
# Faces: 7 snapshots take-new-by-ts (tie -> side-A per r140) + 2 ledgers identity-union zero-loss
#   (compute_audit history + regime_state transitions = append-only union, r188 family).
import subprocess, json, re

def blob(rev, path):
    r = subprocess.run(['git', 'show', f'{rev}:{path}'], capture_output=True)
    if r.returncode != 0 or not r.stdout:
        raise SystemExit(f'blob read fail {rev}:{path}: {r.stderr.decode(errors="replace")}')
    return r.stdout

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

def probe(b):
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
    a, b = blob('HEAD', p), blob('stash@{0}', p)
    ta, tb = probe(a), probe(b)
    if ta and (not tb or ta >= tb):   # tie -> side-A/HEAD (r140)
        side, data, ts = 'HEAD', a, ta
    else:
        side, data, ts = 'stash', b, tb
    if p.endswith('.json'):
        json.loads(data.decode('utf-8'))  # parse-verify before write (r185)
    open(p, 'wb').write(data)
    verdicts.append(f'{p} | take {side} | ts {ts}')

for p, lkey in LEDGERS.items():
    a = json.loads(blob('HEAD', p).decode('utf-8'))
    b = json.loads(blob('stash@{0}', p).decode('utf-8'))
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
