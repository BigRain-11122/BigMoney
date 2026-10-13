import json, glob, re

# 1. fleet tasks open/claimed scan
print('--- fleet tasks non-done ---')
for f in sorted(glob.glob('fleet/tasks/*.json')):
    try:
        d = json.load(open(f, encoding='utf-8'))
    except Exception as e:
        print('PARSE-FAIL', f, e); continue
    st = d.get('status', '?')
    if st not in ('done', 'closed', 'verified', 'void'):
        print(f.split('\\')[-1], '|', st, '|', d.get('claimed_by'))

# 2. P2 queue live rows
print('--- P2 tech queue live rows ---')
for line in open('state/queue/tech.md', encoding='utf-8'):
    if line.startswith('| T') or line.startswith('| E'):
        if 'done' not in line and 'claimed' not in line:
            print(line.rstrip())

# 3. P3 explore queue live rows
print('--- P3 explore queue live rows ---')
try:
    for line in open('state/queue/explore.md', encoding='utf-8'):
        if line.startswith('| T') or line.startswith('| E') or line.startswith('| X'):
            if 'done' not in line:
                print(line.rstrip())
except FileNotFoundError:
    print('NO P3 FILE')

# 4. queue heads declared-intent scan (bm-b/bm-a lanes)
print('--- queue head collision probe ---')
