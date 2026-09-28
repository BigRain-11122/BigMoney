# r380 bm-b push-storm resolver (rebase UU 15-face batch, 5803a7f9 replay onto origin)
# Skill: bigmoney-conflict-resolve. Laws: r188/r208/R216/r185/r140/R209/R350/R210.
# Classifier (r380 run): 15/15 auto-classified, 0 UNKNOWN. Faces:
#  10 snapshot json (take-new by deep-ts probe, tie->stage-2 r140; r159 direction law: probe is
#     direction-agnostic, :2:=onto(origin) / :3:=replayed(mine r380) per r159 bm-c rebase-stage law)
#  2 daily_report twins (r373: take-new by generated ts; twins take SAME side, json key=generated_at)
#  2 rolling-ledger compute_audit.json(history) + regime_state.json(history/transitions union, r319)
#  1 js-wrapper dashboard_status.js (whole-bytes take-side, NO json.dumps re-emit R209)
#  1 anchor-insert HANDOVER.md (R210: origin first-comer bm-c r160 keeps slot; latecomer bm-b r380
#     line inserted BEFORE the '> bm-c round 155' previous-check anchor)
# Probe STAGED blobs (:2:/:3:) only, never working tree (R350).
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
                    ('asof', 'updated', 'tsgenerated', 'generatedat', 'generated', 'timestamp', 'ts', 'time', 'lasttick', 'asatscan')):
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
    'results/scorecard_v1.json',
    'results/strategy_scorecard.json',
    'results/prospect_promotion/_summary.json',
]

REPORT_JSON = 'docs/daily_report/REPORT-2026-09-28.json'
REPORT_MD = 'docs/daily_report/REPORT-2026-09-28.md'

LEDGERS = {
    'results/compute_audit.json': ['history'],
    'results/regime_state.json': ['history', 'transitions'],
}

JS_WRAPPERS = ['results/dashboard_status.js']

HANDOVER = 'research/HANDOVER.md'
ANCHOR_PREFIX = '> bm-c round 155'
LATECOMER_PREFIX = '> bm-b round 380'

def row_key(r):
    return json.dumps(r, sort_keys=True, ensure_ascii=False)

verdicts = []

for p in SNAPSHOTS:
    t2, t3 = probe_side(p, 2), probe_side(p, 3)
    if t2 and (not t3 or t2 >= t3):   # tie -> stage-2 (r140); live probe shows strict newer :3: so tie unreached
        side, ts = 2, t2
    else:
        side, ts = 3, t3
    data = staged(p, side)
    json.loads(data.decode('utf-8'))  # parse-verify before write (r185)
    open(p, 'wb').write(data)
    verdicts.append(f'{p} | take stage-{side} | ts {ts}')

# REPORT twins same-side: probe .json (key=generated_at), apply chosen side to both faces
tj2, tj3 = probe_side(REPORT_JSON, 2), probe_side(REPORT_JSON, 3)
if tj2 and (not tj3 or tj2 >= tj3):
    side, ts = 2, tj2
else:
    side, ts = 3, tj3
for p in (REPORT_JSON, REPORT_MD):
    data = staged(p, side)
    if p.endswith('.json'):
        json.loads(data.decode('utf-8'))  # parse-verify (r185)
    open(p, 'wb').write(data)
    verdicts.append(f'{p} | take stage-{side} (twin-locked with .json probe) | ts {ts}')

for p, lkeys in LEDGERS.items():
    a = json.loads(staged(p, 2).decode('utf-8'))
    b = json.loads(staged(p, 3).decode('utf-8'))
    ts_a = a.get('ts') or wallclock_max_json(a)
    ts_b = b.get('ts') or wallclock_max_json(b)
    state_src = a if (ts_a and (not ts_b or str(ts_a) >= str(ts_b))) else b   # tie -> stage-2 (r140)
    out = dict(state_src)
    for lkey in lkeys:
        la, lb = a.get(lkey, []), b.get(lkey, [])
        seen, union = set(), []
        for r in la + lb:
            k = row_key(r)
            if k not in seen:
                seen.add(k)
                union.append(r)
        out[lkey] = union
        verdicts.append(f'{p}[{lkey}] | ledger union {len(la)}+{len(lb)}->{len(union)} | state ts {state_src.get("ts")}')
    json.loads(json.dumps(out))  # parse-verify
    open(p, 'w', encoding='utf-8', newline='\n').write(json.dumps(out, ensure_ascii=False, indent=1) + '\n')

for p in JS_WRAPPERS:
    t2, t3 = probe_side(p, 2), probe_side(p, 3)
    if t2 and (not t3 or t2 >= t3):   # whole-bytes take-side, NO json.dumps re-emit (R209)
        side, ts = 2, t2
    else:
        side, ts = 3, t3
    data = staged(p, side)
    assert data.lstrip().startswith(b'window.') or b'DASH_DATA' in data, f'wrapper residue {p}'
    open(p, 'wb').write(data)
    verdicts.append(f'{p} | js-wrapper take stage-{side} whole-bytes | ts {ts}')

# HANDOVER anchor-insert (R210): origin side keeps its slot ordering (bm-c r160 first-comer at top);
# extract my bm-b r380 latecomer line from :3: and insert BEFORE the '> bm-c round 155' anchor on origin base.
h_origin = staged(HANDOVER, 2).decode('utf-8')
h_mine = staged(HANDOVER, 3).decode('utf-8')
mine_lines = [l for l in h_mine.splitlines() if l.startswith(LATECOMER_PREFIX)]
assert len(mine_lines) == 1, f'latecomer line count {len(mine_lines)} != 1'
mine_line = mine_lines[0]
assert ANCHOR_PREFIX in h_origin, 'anchor line missing on origin side'
assert LATECOMER_PREFIX not in h_origin, 'origin already carries latecomer (unexpected)'
ol = h_origin.splitlines()
aidx = next(i for i, l in enumerate(ol) if l.startswith(ANCHOR_PREFIX))
merged = ol[:aidx] + [mine_line] + ol[aidx:]
merged_txt = '\n'.join(merged) + ('\n' if h_origin.endswith('\n') else '')
# anchor law checks: origin first-comer r160 line sits ABOVE latecomer r380 line,
# latecomer r380 line sits ABOVE the r155 anchor (file head has title lines before check rows)
idx160 = next((i for i, l in enumerate(merged) if l.startswith('> bm-c round 160')), -1)
idx380 = next((i for i, l in enumerate(merged) if l.startswith(LATECOMER_PREFIX)), -1)
idx155 = next((i for i, l in enumerate(merged) if l.startswith(ANCHOR_PREFIX)), -1)
assert -1 < idx160 < idx380 < idx155, f'order broken: 160@{idx160} 380@{idx380} 155@{idx155}'
open(HANDOVER, 'w', encoding='utf-8', newline='\n').write(merged_txt)
verdicts.append(f'{HANDOVER} | anchor-insert: origin bm-c r160 keeps top, bm-b r380 inserted before r155 anchor')

print('\n'.join(verdicts))
# final sweep: no conflict markers anywhere in resolved faces
allf = SNAPSHOTS + [REPORT_JSON, REPORT_MD, HANDOVER] + list(LEDGERS) + JS_WRAPPERS
for p in allf:
    rb = open(p, 'rb').read()
    assert b'<<<<<<<' not in rb and b'>>>>>>>' not in rb, f'marker residue {p}'
print(f'ALL {len(allf)} FACES RESOLVED, parse-verified, marker-free')
