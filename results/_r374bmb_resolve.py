# r374 bm-b push-storm resolver (rebase UU 26-face batch, 13141922 replay onto origin e5196a72..02ea7663)
# Skill: bigmoney-conflict-resolve. Laws: r188/r208/R216/r185/r140 (resolver-reuse: _r373bmb_resolve.py pattern).
# Classifier: 10 auto + 16 UNKNOWN fail-closed -> hand-qualified below.
#   UNKNOWN hand-qualification (all snapshot-class, take-new by internal ts, tie->stage-2 r140):
#   - docs/daily_report/REPORT-2026-09-28.json/.md: r373 pit-law entry (CODELY) = snapshot take-new by
#     generated ts; .md text twin whole-bytes take-side, same law.
#   - results/daily_scorecard.json + scorecard_v1.json + strategy_scorecard.json: C-family deterministic
#     idempotent re-derives (D-03(1) batch-3), drift = generated/elapsed envelope only.
#   - results/paper/*_paper.json x6 + paper_export twins + prospect_* _summary x2 + t35_open_fill_verify:
#     bar-gated deterministic idempotent re-derives / per-run verdict snapshots (same cutoff 09-24 both sides).
# Probe STAGED blobs (:2:/:3:) only, never working tree. In rebase: :2:=upstream(origin=bm-a r397), :3:=replayed(mine r374).
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
    'results/futures_update_status.json',
    'results/lhb_update_status.json',
    'results/token_usage.json',
    'results/update_status.json',
    'results/fundamental_b_layer_filter.json',
    'results/dashboard_status.json',
    # classifier UNKNOWN -> hand-qualified snapshot (idempotent re-derive / per-run verdict, take-new by ts)
    'results/daily_scorecard.json',
    'results/scorecard_v1.json',
    'results/strategy_scorecard.json',
    'results/t35_open_fill_verify.json',
    'results/prospect_paper/_summary.json',
    'results/prospect_promotion/_summary.json',
    'results/paper/COMPOSITE-CE-01_paper.json',
    'results/paper/COMPOSITE-CE-02_paper.json',
    'results/paper/DROUGHT-CE-01_paper.json',
    'results/paper/ENGULF-CE-01_paper.json',
    'results/paper/NEEDLE-DE-01_paper.json',
    'results/paper/VOLATILITY-CE-01_paper.json',
    'results/paper_export/export-2026-09-24.json',
    'results/paper_export/latest.json',
    # r373 pit-law: daily_report twins = snapshot take-new by generated ts; .md whole-bytes take-side
    'docs/daily_report/REPORT-2026-09-28.json',
    'docs/daily_report/REPORT-2026-09-28.md',
]

LEDGERS = {'results/compute_audit.json': 'history',
           'results/regime_state.json': 'transitions'}

APPEND_LOGS = ['results/x2_watch_log.jsonl']

JS_WRAPPERS = ['results/dashboard_status.js']

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

for p in APPEND_LOGS:
    la = staged(p, 2).decode('utf-8', errors='replace').splitlines()
    lb = staged(p, 3).decode('utf-8', errors='replace').splitlines()
    seen, union = set(), []
    for ln in la + lb:
        k = ln.strip()
        if k and k not in seen:
            seen.add(k)
            union.append(ln)
    for ln in union:  # parse-verify each jsonl line (r185)
        json.loads(ln)
    open(p, 'w', encoding='utf-8', newline='\n').write('\n'.join(union) + '\n')
    verdicts.append(f'{p} | append-log union {len(la)}+{len(lb)}->{len(union)}')

for p in JS_WRAPPERS:
    t2, t3 = probe_side(p, 2), probe_side(p, 3)
    if t2 and (not t3 or t2 >= t3):   # tie -> stage-2 (r140); whole-bytes take-side, NO json.dumps re-emit (R209)
        side, ts = 2, t2
    else:
        side, ts = 3, t3
    data = staged(p, side)
    rb = data
    assert rb.lstrip().startswith(b'window.') or b'DASH_DATA' in rb, f'wrapper residue {p}'
    open(p, 'wb').write(data)
    verdicts.append(f'{p} | js-wrapper take stage-{side} whole-bytes | ts {ts}')

print('\n'.join(verdicts))
# final sweep: no conflict markers anywhere in resolved faces
for p in SNAPSHOTS + list(LEDGERS) + APPEND_LOGS + JS_WRAPPERS:
    rb = open(p, 'rb').read()
    assert b'<<<<<<<' not in rb and b'>>>>>>>' not in rb, f'marker residue {p}'
print(f'ALL {len(SNAPSHOTS)+len(LEDGERS)+len(APPEND_LOGS)+len(JS_WRAPPERS)} FACES RESOLVED, parse-verified, marker-free')
