import json, glob, os
for p in glob.glob('fleet/tasks/*.json'):
    try:
        d = json.load(open(p, encoding='utf-8'))
        print(os.path.basename(p), '|', d.get('status'), '|', d.get('claimed_by'))
    except Exception as e:
        print(os.path.basename(p), 'ERR', e)
print('total tickets:', len(glob.glob('fleet/tasks/*.json')))
