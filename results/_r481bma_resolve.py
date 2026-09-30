"""r481 rebase storm resolver — twin-regen + snapshot faces (per bigmoney-conflict-resolve SKILL).

Scope: 14-UU storm vs bm-b r471 (W14 FREEZE landed mid-round).
 - 6 ALL_FACES resolved beforehand via scripts/merge_lane_views.py resolve (union/take-new recipes, parse-verified)
 - this script handles: REPORT-20260930 twin pair, LIVE-20260930 twin pair, LIVE-latest twin pair
   (json side = deep ts probe -> pick side; md side = byte-copy from the SAME side blob; r327/r329 law),
   fundamental_b_layer_filter.json + _attrition_guard_scan.json (snapshot take-new by embedded ts;
   _attrition_guard_scan = UNKNOWN from classifier -> manual classification = snapshot: guard evidence
   face, both sides scanned same ledgers CLEAN, newer scan supersedes).
Stage law: :2: = origin side (bm-b), :3: = replay side (bm-a, mine). Read blobs via subprocess bytes (r209).
"""
import subprocess, sys, json, io, re

def blob(stage, path):
    r = subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout

def deep_ts(obj):
    """recursive probe for the newest timestamp-ish string value; return best (key, value) or None."""
    best = None
    def walk(o, path):
        nonlocal best
        if isinstance(o, dict):
            for k, v in o.items():
                walk(v, path + [k])
        elif isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, path + [str(i)])
        elif isinstance(o, str) and re.search(r'20\d\d-\d\d-\d\d[T ]\d\d:\d\d', o):
            if best is None or o > best[1]:
                best = ('.'.join(path), o)
    walk(obj, [])
    return best

TWIN_PAIRS = [
    ('docs/daily_report/REPORT-2026-09-30.json', 'docs/daily_report/REPORT-2026-09-30.md'),
    ('docs/live_usage/LIVE-2026-09-30.json', 'docs/live_usage/LIVE-2026-09-30.md'),
    ('docs/live_usage/LIVE-latest.json', 'docs/live_usage/LIVE-latest.md'),
]
SNAPSHOTS = ['results/fundamental_b_layer_filter.json', 'results/_attrition_guard_scan.json']

report = {}
for js, md in TWIN_PAIRS:
    b2, b3 = blob(2, js), blob(3, js)
    j2, j3 = json.loads(b2), json.loads(b3)
    t2, t3 = deep_ts(j2), deep_ts(j3)
    side = 3 if (t3 and (not t2 or t3[1] >= t2[1])) else 2
    (jpick, tpick) = (j3, t3) if side == 3 else (j2, t2)
    # write json from the picked side verbatim (bytes)
    with open(js, 'wb') as f:
        f.write(b3 if side == 3 else b2)
    # md byte-copy from the SAME side (r329: md twin is not JSON)
    mdpick = blob(side, md)
    assert mdpick is not None, f'md stage missing for {md} side {side}'
    with open(md, 'wb') as f:
        f.write(mdpick)
    # parse-verify json
    json.loads(io.open(js, encoding='utf-8').read())
    report[js] = {'side': ('bm-a' if side == 3 else 'bm-b(origin)'), 'ts': tpick, 'other_ts': (t2 if side == 3 else t3)}

for path in SNAPSHOTS:
    b2, b3 = blob(2, path), blob(3, path)
    j2, j3 = json.loads(b2), json.loads(b3)
    t2, t3 = deep_ts(j2), deep_ts(j3)
    side = 3 if (t3 and (not t2 or t3[1] >= t2[1])) else 2
    with open(path, 'wb') as f:
        f.write(b3 if side == 3 else b2)
    json.loads(io.open(path, encoding='utf-8').read())
    report[path] = {'side': ('bm-a' if side == 3 else 'bm-b(origin)'), 'ts': (t3 if side == 3 else t2), 'other_ts': (t2 if side == 3 else t3)}

print(json.dumps(report, ensure_ascii=False, indent=1))
io.open('results/_r481bma_resolve_report.json', 'w', encoding='utf-8').write(json.dumps(report, ensure_ascii=False, indent=1))
print('resolver done: 6 twin files + 2 snapshots, all parse-verified')
