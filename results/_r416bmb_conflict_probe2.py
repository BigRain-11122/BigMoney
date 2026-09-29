import json
import subprocess

def stage(side, path):
    out = subprocess.run(['git', 'show', f':{side}:{path}'], capture_output=True)
    return out.stdout

deep = [
    'results/update_status.json',
    'results/lhb_update_status.json',
    'results/fundamental_b_layer_filter.json',
    'results/dashboard_status.json',
    'docs/daily_report/REPORT-2026-09-29.json',
    'results/regime_state.json',
    'results/runnable_pool.json',
]

for path in deep:
    print('=====', path)
    for side, label in ((2, 'ours(bm-c)'), (3, 'theirs(bm-b)')):
        d = json.loads(stage(side, path))
        ks = list(d.keys())
        print(f'  {label} keys: {ks[:18]}')
        # hunt for any ts-ish field values at top level or one level deep
        for k, v in d.items():
            if isinstance(v, str) and ('2026-09' in v or '2026/09' in v):
                print(f'    {k} = {v}')
            elif isinstance(v, dict):
                for k2, v2 in list(v.items())[:6]:
                    if isinstance(v2, str) and '2026-09' in v2:
                        print(f'    {k}.{k2} = {v2}')
