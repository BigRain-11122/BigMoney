# r372 bm-b push-storm resolver (rebase UU 2-face batch, round-372 commit replay)
# Skill: bigmoney-conflict-resolve. Laws: r188/R208/r185/r140/r311(deep-scan ts)/r319(probe key existence).
# Reuse of in-tree _r369bmb_resolve.py ledger recipe (resolver-reuse priority, bm-c r149 law).
# Faces: results/compute_audit.json (history union) + results/regime_state.json (transitions union).
# In rebase: :2:=upstream(origin, newer), :3:=replayed(ours r372). Probe STAGED blobs only, never working tree.
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

def row_key(r):
    return json.dumps(r, sort_keys=True, ensure_ascii=False)

LEDGERS = {'results/compute_audit.json': 'history',
           'results/regime_state.json': 'transitions'}

verdicts = []
for p, lkey in LEDGERS.items():
    a = json.loads(staged(p, 2).decode('utf-8'))
    b = json.loads(staged(p, 3).decode('utf-8'))
    # r319: dedup/ledger key must exist inside entries on BOTH sides before union (probe per-face)
    assert lkey in a, f'{p}: stage-2 missing ledger key {lkey}'
    assert lkey in b, f'{p}: stage-3 missing ledger key {lkey}'
    la, lb = a[lkey], b[lkey]
    seen, union = set(), []
    for r in la + lb:
        k = row_key(r)
        if k not in seen:
            seen.add(k)
            union.append(r)
    # r311: deep-scan nested ts for take-side probe (top-level miss != no ts)
    ts_a = a.get('ts') or wallclock_max_json(a)
    ts_b = b.get('ts') or wallclock_max_json(b)
    state_src = a if (ts_a and (not ts_b or str(ts_a) >= str(ts_b))) else b   # tie -> stage-2 (r140)
    out = dict(state_src)
    out[lkey] = union
    json.loads(json.dumps(out))  # parse-verify before write (r185)
    open(p, 'w', encoding='utf-8', newline='\n').write(json.dumps(out, ensure_ascii=False, indent=1) + '\n')
    verdicts.append(f'{p} | ledger[{lkey}] union {len(la)}+{len(lb)}->{len(union)} zero-loss | state ts {ts_a} vs {ts_b} -> {"stage-2" if state_src is a else "stage-3"}')

print('\n'.join(verdicts))
# final sweep: no conflict markers anywhere in resolved faces
for p in LEDGERS:
    rb = open(p, 'rb').read()
    assert b'<<<<<<<' not in rb and b'>>>>>>>' not in rb, f'marker residual {p}'
print(f'ALL {len(LEDGERS)} FACES RESOLVED, parse-verified, marker-free')
