import json
d = json.load(open('results/runnable_pool.json', encoding='utf-8'))
for e in d['entries']:
    if e['id'] == 'FUSION-GRID-P1':
        print(json.dumps(e, ensure_ascii=False, indent=1))
