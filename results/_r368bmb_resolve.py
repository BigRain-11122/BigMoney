# r368 bm-b push-storm resolver (rebase UU 23-face batch)
# Skill: bigmoney-conflict-resolve. Laws: r188/r208/R209/R216/r100/R350/r185/r367.
# Probe STAGED blobs (:2:/:3:) only, never working tree.
import subprocess, json, re, sys, os

def staged(path, stage):
    b = subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True).stdout
    if not b:
        r = subprocess.run(['git', 'cat-file', '-p', f':{stage}:{path}'], capture_output=True)
        b = r.stdout
    return b

TS_RE = re.compile(r'20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2})?')

def wallclock_max_json(obj, best=None):
    """Deep-scan: keys normalized (strip _ and -) prefix-match asof/updated/ts/
    generated/time; value must be ts-shaped WITH time-of-day (R350: date-only
    values never feed the wall-clock max; no key-exclusion lists)."""
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
    if path.endswith('.js'):
        return wallclock_max_text(b.decode('utf-8', errors='replace'))
    try:
        return wallclock_max_json(json.loads(b.decode('utf-8')))
    except Exception:
        return wallclock_max_text(b.decode('utf-8', errors='replace'))

SNAPSHOTS = [
    'docs/daily_report/REPORT-2026-09-28.json',
    'docs/daily_report/REPORT-2026-09-28.md',
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
    'results/prospect_paper/_summary.json',
    'results/prospect_promotion/_summary.json',
    'results/scorecard_v1.json',
    'results/strategy_scorecard.json',
    'results/t35_open_fill_verify.json',
    'results/token_usage.json',
    'results/update_status.json',
]

LEDGERS = {'results/compute_audit.json': 'history',
           'results/regime_state.json': 'transitions'}
APPEND_LOG = 'results/x2_watch_log.jsonl'
JS_WRAPPER = 'results/dashboard_status.js'

def row_key(r):
    return json.dumps(r, sort_keys=True, ensure_ascii=False)

verdicts = []

for p in SNAPSHOTS:
    t2, t3 = probe_side(p, 2), probe_side(p, 3)
    if t2 and (not t3 or t2 >= t3):   # tie -> HEAD/stage-2 (r140)
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

# js-wrapper: whole-byte take-side by embedded ts probe
t2, t3 = probe_side(JS_WRAPPER, 2), probe_side(JS_WRAPPER, 3)
side = 2 if (t2 and (not t3 or t2 >= t3)) else 3
data = staged(JS_WRAPPER, side)
assert b'<<<<<<<' not in data and b'window.DASH_DATA' in data
open(JS_WRAPPER, 'wb').write(data)
verdicts.append(f'{JS_WRAPPER} | take stage-{side} whole bytes | ts {t2 if side==2 else t3}')

print('\n'.join(verdicts))
# final sweep: no conflict markers anywhere in resolved faces
for p in SNAPSHOTS + list(LEDGERS) + [APPEND_LOG, JS_WRAPPER]:
    rb = open(p, 'rb').read()
    assert b'<<<<<<<' not in rb and b'>>>>>>>' not in rb, f'marker残留 {p}'
print('ALL 23 FACES RESOLVED, parse-verified, marker-free')
