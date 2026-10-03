import json, glob, os

files = sorted(glob.glob('fleet/tasks/*.json'))
print('total tickets:', len(files))
open_count = 0
for f in files:
    d = json.load(open(f, encoding='utf-8'))
    s = d.get('status', '?')
    if s in ('open', 'claimed'):
        open_count += 1
        print(os.path.basename(f), '|', s, '| claimed_by=', d.get('claimed_by'),
              '|', str(d.get('title', d.get('subject', '')))[:110])
if open_count == 0:
    print('NO open/claimed tickets on board')
