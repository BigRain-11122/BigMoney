"""r831 push-race rebase resolver: 14 faces (twins/snapshots/js-wrapper), r648 sha channel.

Classes per bigmoney-conflict-resolve skill:
- twins (REPORT/LIVE x6): json side picked by deep-ts generated_at probe; .md face = byte-copy from the SAME side (r327/r329)
- snapshots x6 (attrition scan/dashboard json/scorecard v1+strategy/prospect summaries/fundamental_b_layer_filter): take-new by deep ts
- js-wrapper (dashboard_status.js): take-side whole bytes by ts (R209)
rebase semantics: :2: = origin side, :3: = replayed-side (r782/r351).
"""
import subprocess, json, io

def ls_u():
    r = subprocess.run(['git', 'ls-files', '-u'], capture_output=True, text=True, encoding='utf-8')
    stages = {}
    for ln in r.stdout.splitlines():
        p = ln.split('\t')
        if len(p) < 2:
            continue
        info = ln.split()
        sha, stage, path = info[1], info[2], '\t'.join(p[1:])
        stages.setdefault(path, {})[stage] = sha
    return stages

def catf(sha):
    return subprocess.run(['git', 'cat-file', '-p', sha], capture_output=True).stdout

def deep_ts(obj, depth=0, best=''):
    if depth > 4:
        return best
    if isinstance(obj, dict):
        for k, v in obj.items():
            kl = k.strip().replace('_', '').replace('-', '').lower()
            if isinstance(v, str) and kl in ('ts', 'generated', 'generatedat', 'generatedts', 'updated', 'asof', 'time', 'checkedat', 'scantime', 'donets') and v[:2] == '20':
                if v > best:
                    best = v
            elif isinstance(v, (dict, list)):
                b2 = deep_ts(v, depth + 1, best)
                if b2 > best:
                    best = b2
    elif isinstance(obj, list):
        for item in obj:
            b2 = deep_ts(item, depth + 1, best)
            if b2 > best:
                best = b2
    return best

st = ls_u()

def side_ts(blob_bytes):
    try:
        return deep_ts(json.loads(blob_bytes))
    except Exception:
        m = b'generated'
        return ''

def pick_newer_json(path, stages):
    s2, s3 = stages[path].get('2'), stages[path].get('3')
    if s2 and not s3:
        blob = catf(s2); side = '2'
    elif s3 and not s2:
        blob = catf(s3); side = '3'
    else:
        b2, b3 = catf(s2), catf(s3)
        t2, t3 = side_ts(b2), side_ts(b3)
        side = '2' if t2 >= t3 else '3'
        blob = b2 if side == '2' else b3
    json.loads(blob)  # parse-verify before write
    io.open(path, 'wb').write(blob)
    print(f'{path}: -> side {side} ({len(blob)}B)')
    return side

# snapshots: take-new by deep ts
for p in ('results/_attrition_guard_scan.json', 'results/dashboard_status.json',
          'results/scorecard_v1.json', 'results/strategy_scorecard.json',
          'results/prospect_paper/_summary.json', 'results/prospect_promotion/_summary.json',
          'results/fundamental_b_layer_filter.json'):
    if p in st:
        pick_newer_json(p, st)

# twins: json by ts, md byte-copy same side
TWIN = [('docs/daily_report/REPORT-2026-10-07', ),
        ('docs/live_usage/LIVE-2026-10-07', ),
        ('docs/live_usage/LIVE-latest', )]
for (base,) in TWIN:
    pj, pm = base + '.json', base + '.md'
    if pj in st:
        side = pick_newer_json(pj, st)
        if pm in st:
            blob = catf(st[pm][side])
            io.open(pm, 'wb').write(blob)
            print(f'{pm}: byte-copy from SAME side {side} ({len(blob)}B) [r327/r329 twin law]')

# js-wrapper: take-side whole bytes by ts probe inside
if 'results/dashboard_status.js' in st:
    p = 'results/dashboard_status.js'
    b2, b3 = catf(st[p]['2']), catf(st[p]['3'])
    t2, t3 = side_ts(b2), side_ts(b3)
    side = '2' if t2 >= t3 else '3'
    blob = b2 if side == '2' else b3
    assert b'window.DASH_DATA' in blob, 'wrapper missing'
    io.open(p, 'wb').write(blob)
    print(f'{p}: ts {t2 or "none"} vs {t3 or "none"} -> whole-byte side {side} ({len(blob)}B) [R209]')

# final: no UU left
rem = ls_u()
print('remaining UU:', len(rem))
