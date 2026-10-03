import json

SP = 'results/compute_audit.json'
LP = 'results/compute_audit.bm-b.json'
KEY = '2026-10-03 17:26:59'

sh = json.load(open(SP, encoding='utf-8'))
lane_row = next(r for r in json.load(open(LP, encoding='utf-8'))['history'] if r['ts'] == KEY)
hist = sh['history']
if any(r['ts'] == KEY for r in hist):
    print('row already present, no-op')
else:
    hist.append(lane_row)
    hist.sort(key=lambda r: r['ts'])  # contiguity (set-state complete per r619)
    sh['history'] = hist
    # mirror existing file formatting (detect indent from second line's leading spaces)
    lines = open(SP, encoding='utf-8').read().splitlines()
    indent = len(lines[1]) - len(lines[1].lstrip()) if len(lines) > 1 else 1
    json.dump(sh, open(SP, 'w', encoding='utf-8'), ensure_ascii=False, indent=indent)
    json.loads(open(SP, 'rb').read().decode('utf-8'))
    print(f'backfilled row {KEY} into shared face; history rows now {len(hist)}; parse-verified; indent={indent}')
