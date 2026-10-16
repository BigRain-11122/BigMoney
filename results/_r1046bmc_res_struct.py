# -*- coding: utf-8 -*-
# r1046 bm-c: inspect n1_w250_results.json structure faces for fivekeys build.
import json

d = json.load(open('results/perpetual_faces/n1_w250_results.json', encoding='utf-8'))
print('top keys:', sorted(d.keys()))
pool = d['null_pool_cumulative']
print('pool keys:', sorted(pool.keys()))
print('merged:', {k: pool['merged'][k] for k in sorted(pool['merged'])})
print('w250_only keys:', sorted(pool['w250_only'].keys()))
sl = d['skill_line_v2_k_lift']
print('sl keys:', sorted(sl.keys()))
famA = d['families']['A_random_engine_exit']
print('A fam keys:', sorted(famA.keys()))
for k in sorted(d.keys()):
    if 'se_mu' in k or 'audit' in k or 'cutoff' in k:
        print(k, '=', d[k] if not isinstance(d[k], dict) else sorted(d[k].keys()))
