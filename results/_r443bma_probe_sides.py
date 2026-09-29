import subprocess, json, re

def blob(stage, path):
    r = subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True)
    return r.stdout.decode('utf-8', errors='replace') if r.returncode == 0 else None

TS_RE = re.compile(r'20\d{2}-\d{2}-\d{2}[ T]\d{2}:\d{2}')

def deep_ts(obj, best=''):
    """r100/R350 hardened deep probe: any key matching (gen|updated|ts|asof|
    last|time|created) with timestamp-shaped value containing time-of-day."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            kn = str(k).replace('_', '').replace('-', '').lower()
            if isinstance(v, str) and TS_RE.search(v) and v.strip():
                if any(p in kn for p in ('gen', 'updated', 'asof', 'timestamp',
                                         'created', 'written', 'ts', 'time',
                                         'last_seen', 'last')):
                    if v > best:
                        best = v
            best = deep_ts(v, best)
    elif isinstance(obj, list):
        for it in obj:
            best = deep_ts(it, best)
    return best

pairs = [
    ('docs/daily_report/REPORT-2026-09-29.json', 'REPORT'),
    ('docs/live_usage/LIVE-2026-09-29.json', 'LIVE0929'),
    ('docs/live_usage/LIVE-latest.json', 'LIVElatest'),
    ('results/scorecard_v1.json', 'scorecard_v1'),
    ('results/strategy_scorecard.json', 'strat_scorecard'),
    ('results/fundamental_b_layer_filter.json', 'b_layer'),
    ('results/dashboard_status.json', 'dash'),
    ('results/dashboard_status.js', 'dash_js'),
]
for p, tag in pairs:
    a, b = blob(2, p), blob(3, p)
    ta, tb = None, None
    if a and p.endswith('.json'):
        try: ta = deep_ts(json.loads(a))
        except Exception as e: ta = 'PARSE_FAIL'
    if b and p.endswith('.json'):
        try: tb = deep_ts(json.loads(b))
        except Exception as e: tb = 'PARSE_FAIL'
    print(tag, '| origin(:2) ts=', ta, '| mine(:3) ts=', tb,
          '-> take', 'ORIGIN' if (ta or '') > (tb or '') else 'MINE')
    if p.endswith('.js'):
        for side, s in (('origin', a), ('mine', b)):
            m = re.search(r'20\d{2}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}', s or '')
            print('   ', side, 'embedded ts:', m.group(0) if m else None)
