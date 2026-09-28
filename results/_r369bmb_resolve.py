# r369 bm-b push-storm wave-1 resolver (rebase UU 25-face batch, fef51148 replay)
# Skill: bigmoney-conflict-resolve. Laws: r188/r208/R209/R216/r100/R350/r185/r367/r140.
# Reuse of in-tree _r368bmb_resolve.py (resolver-reuse priority, bm-c r149 law).
# New faces this wave: results/paper_export/export-2026-09-24.json + latest.json
#   (diff = state_updated wall-clock only, 08:23:05 vs 08:17:20 -> snapshot take-new).
# Probe STAGED blobs (:2:/:3:) only, never working tree. In rebase: :2:=upstream(origin, newer), :3:=replayed(ours r368).
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
    'results/daily_scorecard.json',
    'results/dashboard_status.json',
    'results/fundamental_b_layer_filter.json',
    'results/futures_update_status.json',
    'results/lhb_update_status.json',
    'results/paper/COMPOSITE-CE-01_paper.json',
    'results/paper/COMPOSITE-CE-02_paper.json',
    'results/paper/DROUGHT-CE-01_paper.json',
    'results/paper/ENGULF-CE-01_paper.json',
    'results/paper/NEEDLE-DE-01_paper.json',
    'results/paper/VOLATILITY-CE-01_paper.json',
    'results/paper_export/export-2026-09-24.json',   # new face r369
    'results/paper_export/latest.json',              # new face r369
    'results/prospect_paper/_summary.json',
    'results/prospect_promotion/_summary.json',
    'results/scorecard_v1.json',
    'results/strategy_scorecard.json',
    'results/t35_open_fill_verify.json',
    'results/token_usage.json',
    'results/update_status.json',
]

# .md/.json twin pair: same-day idempotent regen, MUST take same side (r98/r99/r100)
TWINS = ['docs/daily_report/REPORT-2026-09-28.json', 'docs/daily_report/REPORT-2026-09-28.md']

LEDGERS = {'results/compute_audit.json': 'history',
           'results/regime_state.json': 'transitions'}
APPEND_LOG = 'results/x2_watch_log.jsonl'

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

# twins: same-side enforced (max probe per stage across both twins)
t2 = max(probe_side(TWINS[0], 2), probe_side(TWINS[1], 2))
t3 = max(probe_side(TWINS[0], 3), probe_side(TWINS[1], 3))
side = 2 if (t2 and (not t3 or t2 >= t3)) else 3
for p in TWINS:
    data = staged(p, side)
    if p.endswith('.json'):
        json.loads(data.decode('utf-8'))
    open(p, 'wb').write(data)
verdicts.append(f'twins {TWINS[0]} + {TWINS[1]} | BOTH take stage-{side} | ts2 {t2} ts3 {t3}')

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

# x2_watch_log.jsonl: line-level union, strip residual \r, CRLF join, binary asserts (r367)
ba, bb = staged(APPEND_LOG, 2), staged(APPEND_LOG, 3)
sa = [l.rstrip('\r').strip() for l in ba.decode('utf-8', errors='replace').split('\n') if l.strip()]
sb = [l.rstrip('\r').strip() for l in bb.decode('utf-8', errors='replace').split('\n') if l.strip()]
seen, union = set(), []
for l in sa + sb:
    if l not in seen:
        seen.add(l)
        union.append(l)
for l in union:
    json.loads(l)  # parse-verify every ledger row
raw = ('\r\n'.join(union) + '\r\n').encode('utf-8')
assert raw.count(b'\r\r') == 0 and raw.count(b'\r\n') == len(union)
open(APPEND_LOG, 'wb').write(raw)
verdicts.append(f'{APPEND_LOG} | line union {len(sa)}+{len(sb)}->{len(union)} | CRCR=0 CRLF=={len(union)}')

print('\n'.join(verdicts))
# final sweep: no conflict markers anywhere in resolved faces
for p in SNAPSHOTS + TWINS + list(LEDGERS) + [APPEND_LOG]:
    rb = open(p, 'rb').read()
    assert b'<<<<<<<' not in rb and b'>>>>>>>' not in rb, f'marker残留 {p}'
print(f'ALL {len(SNAPSHOTS)+len(TWINS)+len(LEDGERS)+1} FACES RESOLVED, parse-verified, marker-free')
