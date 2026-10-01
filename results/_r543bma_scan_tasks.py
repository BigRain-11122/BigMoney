import json, glob
for p in sorted(glob.glob('fleet/tasks/*.json')):
    try:
        d = json.load(open(p, encoding='utf-8'))
    except Exception as e:
        print('ERR', p, e)
        continue
    s = d.get('status', '?')
    if s in ('open', 'claimed', 'in_progress'):
        print(s, '|', d.get('claimed_by', ''), '|', d.get('title', '')[:70], '|', p)
