# -*- coding: utf-8 -*-
"""r832 bm-a resolver batch 2 -- closeout-commit replay vs bm-c r688 (21-UU).
Canon per bigmoney-conflict-resolve skill: ALL_FACES via merge_lane_views resolve
(done separately); here = twins (json deep-ts take-new + md same-side byte-copy,
r327/r329), js-wrapper snapshot (take-side whole bytes, R209), snapshots deep-ts
take-new (r311/r100; tie->:2: r140). Stage law: :2: = origin side, :3: = replay."""
import json, re, subprocess

def blob(stage, path):
    r = subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True)
    return r.stdout if r.returncode == 0 else None

DT_RE = re.compile(r'^20\d{2}-\d{2}-\d{2}')
KEY_HINTS = ('ts', 'updated', 'generated', 'cutoff', 'date', 'time', 'asof', 'seen', 'at')

def deep_ts(obj, best=''):
    if isinstance(obj, dict):
        for k, v in obj.items():
            nk = str(k).replace('_', '').replace('-', '').lower()
            if any(nk.startswith(h) for h in KEY_HINTS) and isinstance(v, str) and DT_RE.match(v):
                if v > best:
                    best = v
            best = deep_ts(v, best)
    elif isinstance(obj, list):
        for v in obj:
            best = deep_ts(v, best)
    return best

def side_of(j2, j3):
    t2, t3 = deep_ts(j2), deep_ts(j3)
    return (2, t2, t3) if t2 >= t3 else (3, t2, t3)

def w(path, data):
    open(path, 'wb').write(data)

rep = []
# twins: json decides side, md byte-copy same side
for tj, tm in [('docs/daily_report/REPORT-2026-10-07.json', 'docs/daily_report/REPORT-2026-10-07.md'),
               ('docs/live_usage/LIVE-2026-10-07.json', 'docs/live_usage/LIVE-2026-10-07.md'),
               ('docs/live_usage/LIVE-latest.json', 'docs/live_usage/LIVE-latest.md')]:
    b2, b3 = blob(2, tj), blob(3, tj)
    side, t2, t3 = side_of(json.loads(b2), json.loads(b3))
    w(tj, b2 if side == 2 else b3)
    w(tm, blob(side, tm))
    rep.append(f'{tj}: t2={t2 or "-"} t3={t3 or "-"} -> :{side}: (+md same-side bytes)')
# js-wrapper: same side as its .json twin (single generator, R209 whole-bytes)
b2, b3 = blob(2, 'results/dashboard_status.json'), blob(3, 'results/dashboard_status.json')
side, t2, t3 = side_of(json.loads(b2), json.loads(b3))
w('results/dashboard_status.js', blob(side, 'results/dashboard_status.js'))
w('results/dashboard_status.json', b2 if side == 2 else b3)
rep.append(f'dashboard_status.js/.json: -> :{side}: whole bytes (js wrapper R209)')
# snapshots: deep-ts take-new
for p in ['results/_attrition_guard_scan.json', 'results/daily_scorecard.json',
          'results/fundamental_b_layer_filter.json', 'results/scorecard_v1.json',
          'results/strategy_scorecard.json', 'results/prospect_paper/_summary.json',
          'results/prospect_promotion/_summary.json']:
    b2, b3 = blob(2, p), blob(3, p)
    try:
        side, t2, t3 = side_of(json.loads(b2), json.loads(b3))
    except Exception:
        side, t2, t3 = 2, 'parse-fail-take-2', ''
    w(p, b2 if side == 2 else b3)
    rep.append(f'{p}: t2={t2 or "-"} t3={t3 or "-"} -> :{side}:')
for r in rep:
    print(r)
# parse-verify jsons (r185)
for p in ['results/_attrition_guard_scan.json', 'results/daily_scorecard.json',
          'results/fundamental_b_layer_filter.json', 'results/scorecard_v1.json',
          'results/strategy_scorecard.json', 'results/prospect_paper/_summary.json',
          'results/prospect_promotion/_summary.json', 'results/dashboard_status.json',
          'docs/daily_report/REPORT-2026-10-07.json', 'docs/live_usage/LIVE-2026-10-07.json',
          'docs/live_usage/LIVE-latest.json']:
    json.load(open(p, encoding='utf-8'))
print('PARSE-VERIFY OK (11 json)')
