# -*- coding: utf-8 -*-
"""r634 bm-a ring-1 resolver: 11 non-ALL_FACES UU files, rebase state (r351: :2:=origin side, :3:=local pick 6c6d85646).
Probe law R350/r100: staged blobs ONLY (never working tree), value-shape adjudication (no key-exclude lists),
wall-clock requires time-of-day (date-only must not feed max), normalize ' '->'T' before compare (mixed-format guard),
same-value tie -> :2: origin side (r140 canon via r627 rebase orientation).
Twins: json decides side, md byte-copy from SAME side (r327/r329); dashboard js whole-bytes same side as json (R209);
LIVE family all-4-same-side (r439bmb).
Whole-side take = byte copy of chosen stage blob (ts-diffpick whole-bytes; no re-dump).
Receipt: results/_r634bma_resolve_receipt.json
"""
import json, subprocess, sys, re

WALL = re.compile(r'^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}')

def stage_bytes(stage, path):
    r = subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True)
    if r.returncode != 0:
        sys.stderr.write(f'stage read fail {stage} {path}: {r.stderr.decode("utf-8","replace")}\n')
        sys.exit(2)
    return r.stdout

def deep_ts(obj, path='', best=None):
    if best is None:
        best = [None, '']
    if isinstance(obj, dict):
        for k, v in obj.items():
            deep_ts(v, f'{path}.{k}', best)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            deep_ts(v, f'{path}[{i}]', best)
    elif isinstance(obj, str) and WALL.match(obj):
        norm = obj.replace(' ', 'T')
        if best[0] is None or norm > best[0]:
            best[0] = norm
            best[1] = path
    return best

def probe_side(stage, path):
    b = stage_bytes(stage, path)
    try:
        obj = json.loads(b.decode('utf-8'))
    except Exception as e:
        sys.stderr.write(f'json parse fail {stage} {path}: {e}\n')
        sys.exit(2)
    return deep_ts(obj)

def decide(path):
    ts2, p2 = probe_side(2, path)
    ts3, p3 = probe_side(3, path)
    if ts2 is None and ts3 is None:
        side = 2  # both date-only/no-ts: tie -> origin (r140)
        why = 'both sides no wall-clock ts -> tie origin'
    elif ts3 is None:
        side, why = 2, 'local side no wall-clock ts'
    elif ts2 is None:
        side, why = 3, 'origin side no wall-clock ts'
    elif ts3 > ts2:
        side, why = 3, f'local {ts3} > origin {ts2}'
    elif ts2 > ts3:
        side, why = 2, f'origin {ts2} > local {ts3}'
    else:
        side, why = 2, f'tie {ts2} -> origin (r140)'
    return side, why, (ts2, p2), (ts3, p3)

def take(side, path):
    """Whole-bytes take from chosen side into worktree."""
    b = stage_bytes(side, path)
    with open(path, 'wb') as f:
        f.write(b)
    if path.endswith('.json'):
        json.loads(open(path, 'rb').read().decode('utf-8'))  # parse-verify before add (r185)
    return len(b)

receipt = {'generated': 'r634 bm-a ring-1 (rebase pick 6c6d85646 onto 40cc5a1f3)', 'files': {}}

# twin groups: probe json -> side applies to whole group
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
    side, why, o, l = decide(probe_path)
    for m in members:
        n = take(side, m)
        receipt['files'][m] = {'side': side, 'probe': probe_path, 'why': why, 'bytes': n,
                               'origin_ts': o, 'local_ts': l}
    print(f'[group {gname}] side={side} ({why}) -> {len(members)} files')

for p in singles:
    side, why, o, l = decide(p)
    n = take(side, p)
    receipt['files'][p] = {'side': side, 'probe': p, 'why': why, 'bytes': n,
                          'origin_ts': o, 'local_ts': l}
    print(f'[single] {p} side={side} ({why})')

with open('results/_r634bma_resolve_receipt.json', 'w', encoding='utf-8') as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print('receipt: results/_r634bma_resolve_receipt.json')
print('RESOLVE OK')
