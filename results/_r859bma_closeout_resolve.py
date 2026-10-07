import json, subprocess

# 14 plain regen faces: take-theirs (my r859 commit side, newer regen)
plain = [
    'docs/daily_report/REPORT-2026-10-08.json', 'docs/daily_report/REPORT-2026-10-08.md',
    'docs/live_usage/LIVE-2026-10-08.json', 'docs/live_usage/LIVE-2026-10-08.md',
    'docs/live_usage/LIVE-latest.json', 'docs/live_usage/LIVE-latest.md',
    'results/_attrition_guard_scan.json', 'results/_orphan_face_probe.json',
    'results/compute_audit.json', 'results/fundamental_b_layer_filter.json',
    'results/futures_update_status.json', 'results/lhb_update_status.json',
    'results/regime_state.json', 'results/update_status.json',
]
subprocess.run(['git', 'checkout', '--theirs', '--'] + plain, check=True)
subprocess.run(['git', 'add', '--'] + plain, check=True)
print('14 plain faces: take-theirs staged')

# token_usage.json: per-machine union (mine=bm-a fresh, theirs-side r722=bm-c fresh)
def side(n):
    r = subprocess.run(['git', 'show', f':{n}:results/token_usage.json'],
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    return json.loads(r.stdout)

mine = side(3)   # my r859 commit (replay side)
theirs = side(2)  # r722 base side
mm, tm = mine.get('machines', {}), theirs.get('machines', {})
merged = dict(tm)  # start with r722 (bm-c-fresh)
for k, v in mm.items():
    if 'bm-c' in k:
        continue  # keep r722's fresh bm-c sections
    merged[k] = v  # bm-a/default sections from my fresh run
mine['machines'] = merged
with open('results/token_usage.json', 'w', encoding='utf-8', newline='') as fh:
    json.dump(mine, fh, ensure_ascii=False, indent=1)
subprocess.run(['git', 'add', 'results/token_usage.json'], check=True)
print('token_usage: per-machine union written (bm-a=mine, bm-c=r722)')

r = subprocess.run(['git', 'ls-files', '-u'], capture_output=True, text=True)
print('unmerged remaining:', len(r.stdout.strip().splitlines()) if r.stdout.strip() else 0)
