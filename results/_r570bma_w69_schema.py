# -*- coding: utf-8 -*-
# r570 bm-a: dump W69 finalize numeric anchor face (schema-aware)
import json

r = json.load(open('results/perpetual_faces/n1_w69_results.json', encoding='utf-8'))
print('TOP KEYS:', sorted(r.keys()))
for k in sorted(r.keys()):
    v = r[k]
    if isinstance(v, dict):
        print('  [%s] dict keys:' % k, sorted(v.keys())[:20])
    elif isinstance(v, list):
        print('  [%s] list len' % k, len(v))
