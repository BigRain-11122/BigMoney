# -*- coding: utf-8 -*-
"""r382 bm-c: extract W112 finalize headline (chain head after FF integration)."""
import json

d = json.load(open('results/perpetual_faces/n1_w112_results.json', encoding='utf-8'))
s = d['science_gates']
np_ = d['null_pool_cumulative']
sl = d['skill_line_v2_k_lift']
print('ledger', s['ledger']['prev_total'], '+', s['ledger']['batch_trials'], '=',
      s['ledger']['total'])
print('merged mu', np_['merged']['mu'], 'sigma', np_['merged']['sigma'],
      'K', np_['merged']['n_values'])
print('w112_only mu', np_.get('w112_only', {}).get('mu'))
print('p95', d['families']['A_random_engine_exit']['full_sharpe_p95'])
print('se_mu', np_.get('se_mu_at_k%s' % np_['merged']['n_values']))
for k in sl:
    print('sl:', k, '=', sl[k])
print('audit', d['audit']['machine'])
