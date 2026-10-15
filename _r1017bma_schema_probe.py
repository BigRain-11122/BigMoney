# -*- coding: utf-8 -*-
# r1017 bm-a scratch: inspect n1_w245_results.json schema for fivekeys key names
import json
import io

d = json.load(io.open('results/perpetual_faces/n1_w245_results.json', encoding='utf-8'))
print('top:', sorted(d.keys()))
pool = d['null_pool_cumulative']
print('pool keys:', sorted(pool.keys()))
print('merged:', {k: pool['merged'][k] for k in ('mu', 'sigma', 'n_values')})
print('w245_only:', {k: pool['w245_only'][k] for k in ('mu', 'sigma', 'n_values')})
print('se_mu keys:', [k for k in pool if k.startswith('se_mu')])
sl = d['skill_line_v2_k_lift']
print('sl keys:', sorted(sl.keys()))
famA = d['families']['A_random_engine_exit']
print('famA p95/p99:', famA['full_sharpe_p95'], famA['full_sharpe_p99'])
led = d['science_gates']['ledger']
print('ledger:', led)
