import json, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

d = json.load(open('results/perpetual_faces/n1_w20_results.json', encoding='utf-8'))
c = d['null_pool_cumulative']
print('batch:', d['batch'])
print('K merged:', c['merged']['n_values'])
print('merged mu:', c['merged']['mu'])
print('merged sigma:', c['merged']['sigma'])
print('se_mu:', {k: v for k, v in c.items() if 'se_mu' in k})
print('A p95:', d['families']['A_random_engine_exit']['full_sharpe_p95'])
print('A p99:', d['families']['A_random_engine_exit']['full_sharpe_p99'])
print('w20_only mu:', c.get('w20_only', {}).get('mu'))
print('mu_delta:', {k: v for k, v in c.items() if 'delta' in k})
kl = d['skill_line_v2_k_lift']
print('K-lift:', {k: v for k, v in kl.items()})
print('ledger:', d['science_gates']['ledger']['prev_total'], '->',
      d['science_gates']['ledger']['total'])
print('audit:', d.get('audit'))
