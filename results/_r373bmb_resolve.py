# r373 bm-b push-storm resolver (rebase UU 9-face batch, 01453499 replay onto origin 258d084f..150ac762)
# Skill: bigmoney-conflict-resolve. Laws: r188/r208/R216/r185/r140 (resolver-reuse: _r371bmb_resolve.py pattern).
# Classifier: 7 auto + 2 UNKNOWN fail-closed -> hand-qualified below.
#   UNKNOWN docs/daily_report/REPORT-2026-09-28.json + .md:
#   same-day in-place idempotent re-derive (daily_report.py T-75 contract: 当日重复运行
#   原地再生幂等), probed both sides -> differing keys = generated_at/token_line/rd runtime
#   metadata only, content otherwise identical => snapshot semantics take-new by generated ts.
# Probe STAGED blobs (:2:/:3:) only, never working tree. In rebase: :2:=upstream(origin=bm-a r398), :3:=replayed(mine r373).
import subprocess, json, re, difflib

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
    'results/futures_update_status.json',
    'results/lhb_update_status.json',
    'results/token_usage.json',
    'results/update_status.json',
    'results/fundamental_b_layer_filter.json',
    'docs/daily_report/REPORT-2026-09-28.json',   # classifier UNKNOWN -> hand-qualified snapshot (probe-verified)
    'docs/daily_report/REPORT-2026-09-28.md',    # classifier UNKNOWN -> hand-qualified snapshot (probe-verified)
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
# final sweep: no conflict markers anywhere in resolved faces
for p in SNAPSHOTS + list(LEDGERS):
    rb = open(p, 'rb').read()
    assert b'<<<<<<<' not in rb and b'>>>>>>>' not in rb, f'marker residue {p}'
print(f'ALL {len(SNAPSHOTS)+len(LEDGERS)} FACES RESOLVED, parse-verified, marker-free')
