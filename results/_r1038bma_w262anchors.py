import json, io
d = json.load(io.open('results/perpetual_faces/n1_w262_results.json', encoding='utf-8'))
led = (d.get('science_gates') or {}).get('ledger') or {}
pool = d.get('null_pool_cumulative') or {}
merged = pool.get('merged') or {}
print('ledger:', led.get('total'), '| batch:', led.get('batch_trials') or led.get('last_batch'), '| file:', led.get('file_name'))
print('merged n_values:', merged.get('n_values'), '| mu:', merged.get('mu'), '| sigma:', merged.get('sigma'))
print('w262_only mu:', (pool.get('w262_only') or {}).get('mu'))
s1 = d.get('skill_line_v2_k_lift') or {}
print('skill keys:', {k: s1[k] for k in s1 if k in ('line_pre_w262', 'line_merged_574320', 'line_delta_k_lift', 'n_eff_held_equal', 'canon_flip')})
print('se_mu field:', [k for k in pool if k.startswith('se_mu')])
famA = (d.get('families') or {}).get('A_random_engine_exit') or {}
print('A p95:', famA.get('full_sharpe_p95'), '| p99:', famA.get('full_sharpe_p99'))
print('evidence_cutoff:', d.get('evidence_cutoff'))
print('audit machine:', (d.get('audit') or {}).get('machine'))
