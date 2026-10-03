# r630 bm-a rebase conflict resolver: snapshot take-new + twin-side coupling + js-wrapper faces
# classifier: snapshot/twin-regen-md/js-wrapper-snapshot classes; probe staged blobs (:2: origin-side / :3: replay-side)
import json, re, subprocess, sys

def stage_blob(path, stage):
    return subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True).stdout

def deep_ts(obj, best=None):
    # hardened probe r100/R350: strip _/- from keys, value must look like a wall-clock ts
    if isinstance(obj, dict):
        for k, v in obj.items():
            nk = k.replace('_', '').replace('-', '')
            if isinstance(v, str) and re.match(r'^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}', v):
                if best is None or v > best[0]:
                    best = (v, k)
            r = deep_ts(v, best)
            if r and (best is None or r[0] > best[0]):
                best = r
    elif isinstance(obj, list):
        for it in obj:
            r = deep_ts(it, best)
            if r and (best is None or r[0] > best[0]):
                best = r
    return best

SNAPSHOTS = [
    'results/fundamental_b_layer_filter.json',
    'results/dashboard_status.json',
    'results/scorecard_v1.json',
    'results/strategy_scorecard.json',
    'results/_attrition_guard_scan.json',
]
TWINS = [
    ('docs/daily_report/REPORT-2026-10-03.json', 'docs/daily_report/REPORT-2026-10-03.md'),
    ('docs/live_usage/LIVE-2026-10-03.json', 'docs/live_usage/LIVE-2026-10-03.md'),
    ('docs/live_usage/LIVE-latest.json', 'docs/live_usage/LIVE-latest.md'),
]

report = {}
for p in SNAPSHOTS:
    b2, b3 = stage_blob(p, 2), stage_blob(p, 3)
    try:
        j2, j3 = json.loads(b2), json.loads(b3)
    except Exception as e:
        report[p] = f'PARSE-FAIL {e}'; continue
    t2, t3 = deep_ts(j2), deep_ts(j3)
    side = 3 if (t2 is None or (t3 and t3[0] > t2[0])) else 2
    data = b3 if side == 3 else b2
    with open(p, 'wb') as f:
        f.write(data)
    json.loads(data)  # parse-verify
    report[p] = f'take :{side}: (origin_ts={t2} replay_ts={t3})'

for jp, mp in TWINS:
    b2, b3 = stage_blob(jp, 2), stage_blob(jp, 3)
    try:
        j2, j3 = json.loads(b2), json.loads(b3)
    except Exception as e:
        report[jp] = f'PARSE-FAIL {e}'; continue
    t2, t3 = deep_ts(j2), deep_ts(j3)
    side = 3 if (t2 is None or (t3 and t3[0] > t2[0])) else 2
    for path in (jp, mp):  # twin-side coupling: BOTH files from same side, whole bytes
        data = stage_blob(path, side)
        with open(path, 'wb') as f:
            f.write(data)
    report[jp] = f'take :{side}: (origin_ts={t2} replay_ts={t3}) +md twin same side'

# js-wrapper: dashboard_status.js take-side whole bytes (coupled with dashboard_status.json verdict)
b2j, b3j = stage_blob('results/dashboard_status.js', 2), stage_blob('results/dashboard_status.js', 3)
verdict_side = report['results/dashboard_status.json']
side = 3 if ':3:' in verdict_side else 2
with open('results/dashboard_status.js', 'wb') as f:
    f.write(b3j if side == 3 else b2j)
report['results/dashboard_status.js'] = f'take :{side}: whole bytes (coupled with json verdict)'
# wrapper sanity: must contain window.DASH_DATA
assert b'window.DASH_DATA' in (b3j if side == 3 else b2j)

print(json.dumps(report, indent=1, ensure_ascii=False))
