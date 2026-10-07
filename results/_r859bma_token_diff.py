import json, subprocess, sys

def side(n):
    r = subprocess.run(['git', 'show', f':{n}:results/token_usage.json'],
                        capture_output=True, text=True, encoding='utf-8', errors='replace')
    return json.loads(r.stdout)

o = side(2)  # ours = bm-c r721 base side
t = side(3)  # theirs = bm-a r858 replay side
print('ours(bm-c-r721) gen:', o.get('generated'))
print('theirs(bm-a-r858) gen:', t.get('generated'))
om, tm = o.get('machines', {}), t.get('machines', {})
for k in sorted(set(om) | set(tm)):
    if om.get(k) == tm.get(k):
        print(k, 'identical')
    else:
        print(k, 'DIFF', 'ours_ts=', om.get(k, {}).get('ts', '?'), 'theirs_ts=', tm.get(k, {}).get('ts', '?'))
