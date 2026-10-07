import subprocess, json

FILES = [
    'docs/daily_report/REPORT-2026-10-08.json',
    'docs/live_usage/LIVE-2026-10-08.json',
    'results/_attrition_guard_scan.json',
    'results/fundamental_b_layer_filter.json',
]

def blob(stage, path):
    r = subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True)
    return r.stdout

def deep_ts(obj):
    """Find newest ^20xx- timestamp anywhere (deep scan, r311 law)."""
    best = None
    def walk(o):
        nonlocal best
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, str) and len(v) >= 19 and v[:2] == '20' and v[4] == '-' and (':' in v):
                    if best is None or v > best:
                        best = v
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(obj)
    return best

for p in FILES:
    o2 = blob(2, p)
    o3 = blob(3, p)
    try:
        d2 = json.loads(o2)
        d3 = json.loads(o3)
        t2, t3 = deep_ts(d2), deep_ts(d3)
        print(f'{p}\n  origin(:2:) ts={t2}  local(:3:) ts={t3}')
        if t2 and t3:
            print(f'  -> take {"ORIGIN" if t2 > t3 else "LOCAL" if t3 > t2 else "TIE->HEAD(local)"}')
    except Exception as e:
        print(f'{p}\n  parse issue: {e}; len2={len(o2)} len3={len(o3)}')
