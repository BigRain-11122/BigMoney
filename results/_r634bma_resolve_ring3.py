# -*- coding: utf-8 -*-
"""r634 bm-a ring-3 resolver (merge origin/main after push-claw block, merge-state, r621/r627 laws).
ALL_FACES (6): explicit three-stage files SWAPPED per r627 (--stage2=:3: origin blob, --stage3=:2: local blob, --stage1=:1: base).
Non-ALL_FACES (12): deep wall-clock ts probe on STAGED blobs, merge orientation :2:=ours(local), :3:=theirs(origin);
  tie -> ours (r140 HEAD canon); twins take same side; js whole-bytes (R209); R350 value-shape adjudication.
Receipt: results/_r634bma_resolve_receipt.json (ring3 block).
"""
import json, subprocess, sys, re, os, tempfile

WALL = re.compile(r'^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}')
TD = os.path.join(os.environ['TEMP'], 'r634bma_ring3')
os.makedirs(TD, exist_ok=True)

def stage_bytes(stage, path):
    r = subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True)
    if r.returncode != 0:
        sys.stderr.write(f'stage read fail :{stage}: {path}: {r.stderr.decode("utf-8","replace")[:150]}\n')
        sys.exit(2)
    return r.stdout

def deep_ts(obj, path='', best=None):
    if best is None: best = [None, '']
    if isinstance(obj, dict):
        for k, v in obj.items(): deep_ts(v, f'{path}.{k}', best)
    elif isinstance(obj, list):
        for i, v in enumerate(obj): deep_ts(v, f'{path}[{i}]', best)
    elif isinstance(obj, str) and WALL.match(obj):
        n = obj.replace(' ', 'T')
        if best[0] is None or n > best[0]: best[0], best[1] = n, path
    return best

def probe(path, stage):
    return deep_ts(json.loads(stage_bytes(stage, path).decode('utf-8')))

def take(side, path):
    b = stage_bytes(side, path)
    open(path, 'wb').write(b)
    if path.endswith('.json'):
        json.loads(open(path, 'rb').read().decode('utf-8'))  # parse-verify (r185)
    return len(b)

# --- Part 1: ALL_FACES via merge_lane_views resolve with EXPLICIT SWAPPED stages (r627) ---
all_faces = ['compute_audit.json', 'regime_state.json', 'update_status.json',
             'lhb_update_status.json', 'futures_update_status.json', 'token_usage.json']
receipt = {'ring3': {'merge': 'origin/main f54c902b6 (bm-b r626/r626b/r626c + bm-c r423 x2)', 'files': {}}}
for f in all_faces:
    p = f'results/{f}'
    b1, b2, b3 = stage_bytes(1, p), stage_bytes(2, p), stage_bytes(3, p)
    f1, f2, f3 = os.path.join(TD, 'b1'), os.path.join(TD, 'b2'), os.path.join(TD, 'b3')
    open(f1, 'wb').write(b1); open(f2, 'wb').write(b2); open(f3, 'wb').write(b3)
    # merge orientation: --stage2 = ORIGIN side = :3: blob; --stage3 = LOCAL side = :2: blob (r627 swap law)
    r = subprocess.run(['python', 'scripts\\merge_lane_views.py', 'resolve', p,
                        '--stage1', f1, '--stage2', f3, '--stage3', f2],
                       capture_output=True)
    out = (r.stdout + r.stderr).decode('utf-8', 'replace')
    if r.returncode != 0:
        sys.stderr.write(f'ALL_FACES resolve fail {f}: {out[:300]}\n'); sys.exit(2)
    json.loads(open(p, 'rb').read().decode('utf-8'))  # parse-verify after write
    print(f'[ALL_FACES] {f} resolve rc=0 ({[l for l in out.splitlines() if "wrote" in l][:1]})')
    receipt['ring3']['files'][p] = {'recipe': 'merge_lane_views union/take-new (swapped stages r627)'}

# --- Part 2: non-ALL_FACES twins + snapshots ---
groups = [
    ('daily_report', 'docs/daily_report/REPORT-2026-10-03.json',
     ['docs/daily_report/REPORT-2026-10-03.json', 'docs/daily_report/REPORT-2026-10-03.md']),
    ('live_usage', 'docs/live_usage/LIVE-2026-10-03.json',
     ['docs/live_usage/LIVE-2026-10-03.json', 'docs/live_usage/LIVE-2026-10-03.md',
      'docs/live_usage/LIVE-latest.json', 'docs/live_usage/LIVE-latest.md']),
    ('dashboard', 'results/dashboard_status.json',
     ['results/dashboard_status.json', 'results/dashboard_status.js']),
]
singles = ['results/scorecard_v1.json', 'results/strategy_scorecard.json',
           'results/_attrition_guard_scan.json', 'results/fundamental_b_layer_filter.json']

for gname, probe_path, members in groups:
    o_ts = probe(probe_path, 2)   # ours
    t_ts = probe(probe_path, 3)   # theirs
    if o_ts[0] is None and t_ts[0] is None: side, why = 2, 'both no wall-clock -> tie ours (r140)'
    elif t_ts[0] is None: side, why = 2, 'theirs no wall-clock'
    elif o_ts[0] is None: side, why = 3, 'ours no wall-clock'
    elif t_ts[0] > o_ts[0]: side, why = 3, f'theirs {t_ts[0]} > ours {o_ts[0]}'
    elif o_ts[0] > t_ts[0]: side, why = 2, f'ours {o_ts[0]} > theirs {t_ts[0]}'
    else: side, why = 2, f'tie {o_ts[0]} -> ours (r140)'
    for m in members:
        n = take(side, m)
        receipt['ring3']['files'][m] = {'side': side, 'probe': probe_path, 'why': why, 'bytes': n}
    print(f'[group {gname}] side={side} ({why}) -> {len(members)} files')

for p in singles:
    o_ts = probe(p, 2); t_ts = probe(p, 3)
    if o_ts[0] is None and t_ts[0] is None: side, why = 2, 'both no wall-clock -> tie ours'
    elif t_ts[0] is None: side, why = 2, 'theirs no wall-clock'
    elif o_ts[0] is None: side, why = 3, 'ours no wall-clock'
    elif t_ts[0] > o_ts[0]: side, why = 3, f'theirs {t_ts[0]} > ours {o_ts[0]}'
    elif o_ts[0] > t_ts[0]: side, why = 2, f'ours {o_ts[0]} > theirs {t_ts[0]}'
    else: side, why = 2, f'tie -> ours'
    n = take(side, p)
    receipt['ring3']['files'][p] = {'side': side, 'why': why, 'bytes': n,
                                    'ours_ts': o_ts, 'theirs_ts': t_ts}
    print(f'[single] {p} side={side} ({why})')

rp = 'results/_r634bma_resolve_receipt.json'
rec = json.loads(open(rp, encoding='utf-8').read())
rec.update(receipt)
json.dump(rec, open(rp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('RING3 RESOLVE OK')
