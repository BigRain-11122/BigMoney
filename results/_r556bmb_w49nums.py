import json
d = json.load(open('results/perpetual_faces/n1_w49_results.json', encoding='utf-8'))
c = d['null_pool_cumulative']
print('w49_only:', json.dumps(c['w49_only']))
print('merged:', json.dumps(c['merged']))
print('mu_delta:', c.get('mu_delta_w49_vs_w47ext'))
print('se_mu:', c.get('se_mu_at_k103520'))
fa = d['families']['A_random_engine_exit']
print('A p95=%s p99=%s mu=%s' % (fa['full_sharpe_p95'], fa['full_sharpe_p99'], fa['full_sharpe_mu']))
print('skill:', json.dumps({k: v for k, v in d['skill_line_v2_k_lift'].items() if k != 'formula'}))
print('ledger:', json.dumps(d['science_gates']['ledger']))
w47 = json.load(open('results/perpetual_faces/n1_w47_results.json', encoding='utf-8'))
print('W47-only mu/sigma:', w47['null_pool_cumulative']['w47_only']['mu'], w47['null_pool_cumulative']['w47_only']['sigma'])
print('W47 A p95:', w47['families']['A_random_engine_exit']['full_sharpe_p95'])
print('W47 se_mu:', w47['null_pool_cumulative'].get('se_mu_at_k101320'))
