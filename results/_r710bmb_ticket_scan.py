import json, glob
for f in glob.glob('fleet/tasks/*.json'):
    t = json.load(open(f, encoding='utf-8'))
    if t.get('status') == 'open':
        print(t.get('id'), t.get('priority'), t.get('immediate'), t.get('title', '')[:100])
print('--- open scan done ---')
