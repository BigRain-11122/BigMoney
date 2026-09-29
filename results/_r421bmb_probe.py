# -*- coding: utf-8 -*-
import json
p = json.load(open('results/runnable_pool.json', encoding='utf-8'))
for x in p['entries']:
    if x['id'] in ('TRIAL-LABOR-W6-JUDGE', 'TRIAL-LABOR-W7-SCREEN'):
        print(json.dumps(x, ensure_ascii=False, indent=1))
        print('---')
