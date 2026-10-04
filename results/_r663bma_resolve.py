# r663 bm-a UU resolver: deep-ts take-new for snapshot/twin faces (skill recipes)
# - probe STAGED blobs (:2 ours=bm-a, :3 theirs=origin wave) never worktree (R350)
# - ts probe: recursive, key normalized (strip _/-), value must match ^20\d{2}- AND contain time-of-day (r100)
# - tie same-second -> HEAD/ours (r140)
# - twin coupling: json side decides; md twin byte-copied from SAME side (r327/r329)
# - js wrapper: whole-byte take-side (R209)
import subprocess, re, sys

TS_RE = re.compile(r'20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}')

def blob(stage, path):
    p = subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True)
    if p.returncode != 0:
        return None
    return p.stdout

def deep_ts(obj, best=''):
    """recursive max ISO ts scan over str values anywhere in the JSON tree."""
    if isinstance(obj, dict):
        for v in obj.values():
            best = deep_ts(v, best)
    elif isinstance(obj, list):
        for v in obj:
            best = deep_ts(v, best)
    elif isinstance(obj, str):
        m = TS_RE.search(obj)
        if m and m.group(0) > best:
            best = m.group(0)
    return best

def side_ts(raw):
    if raw is None:
        return ''
    try:
        import json
        return deep_ts(json.loads(raw.decode('utf-8')))
    except Exception:
        # non-JSON (md/js): scan raw text
        m = TS_RE.findall(raw.decode('utf-8', errors='replace'))
        return max(m) if m else ''

def decide(path):
    ours, theirs = blob(2, path), blob(3, path)
    to, tt = side_ts(ours), side_ts(theirs)
    if not to and not tt:
        side = 2  # no ts anywhere: keep ours (single-writer lean, r140 tie)
    elif tt > to:
        side = 3
    else:
        side = 2  # ours newer or same-second tie
    return side, to, tt

SNAPSHOTS = [
    'results/_attrition_guard_scan.json',
    'results/dashboard_status.json',
    'results/fundamental_b_layer_filter.json',
    'results/prospect_paper/_summary.json',
    'results/prospect_promotion/_summary.json',
    'results/scorecard_v1.json',
    'results/strategy_scorecard.json',
    'results/t35_open_fill_verify.json',
]
TWINS = [  # (json decider, md follower)
    ('docs/daily_report/REPORT-2026-10-04.json', 'docs/daily_report/REPORT-2026-10-04.md'),
    ('docs/live_usage/LIVE-2026-10-04.json', 'docs/live_usage/LIVE-2026-10-04.md'),
    ('docs/live_usage/LIVE-latest.json', 'docs/live_usage/LIVE-latest.md'),
]
JS_TWIN = ('results/dashboard_status.json', 'results/dashboard_status.js')

log = []
for path in SNAPSHOTS:
    side, to, tt = decide(path)
    raw = blob(side, path)
    import json as _j
    _j.loads(raw.decode('utf-8'))  # parse-verify before write (r185)
    with open(path, 'wb') as f:
        f.write(raw)
    log.append(f'{path}: side={side} ours_ts={to} theirs_ts={tt}')

for jpath, mpath in TWINS:
    side, to, tt = decide(jpath)
    jraw = blob(side, jpath)
    mraw = blob(side, mpath)  # md from SAME side (twin coupling)
    import json as _j
    _j.loads(jraw.decode('utf-8'))  # json parse-verify; md is text (no parse)
    with open(jpath, 'wb') as f:
        f.write(jraw)
    with open(mpath, 'wb') as f:
        f.write(mraw)
    log.append(f'{jpath}+md: side={side} ours_ts={to} theirs_ts={tt}')

# js wrapper twin follows its json decision (whole-byte take-side, R209)
side, to, tt = decide(JS_TWIN[0])
jraw = blob(side, JS_TWIN[0])
jsraw = blob(side, JS_TWIN[1])
import json as _j
_j.loads(jraw.decode('utf-8'))
with open(JS_TWIN[0], 'wb') as f:
    f.write(jraw)
with open(JS_TWIN[1], 'wb') as f:
    f.write(jsraw)
log.append(f'dashboard_status.json+js: side={side} ours_ts={to} theirs_ts={tt}')

for l in log:
    print(l)

# zero-marker assertion across all resolved faces (write-back gate)
MARK = b'<<<<<<<'
for p in SNAPSHOTS + [x for t in TWINS for x in t] + list(JS_TWIN):
    with open(p, 'rb') as f:
        if MARK in f.read():
            print(f'MARKER-FAIL {p}')
            sys.exit(2)
print('ALL-RESOLVED zero-markers parse-verified')
