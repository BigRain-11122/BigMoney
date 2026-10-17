import json
d = json.load(open(r'results/perpetual_faces/n1_w265_results.json', encoding='utf-8'))
p = d['null_pool_cumulative']; s = d['skill_line_v2_k_lift']; f = d['families']['A_random_engine_exit']
print('TOPKEYS', sorted(d.keys()))
print('POOLKEYS', sorted(p.keys()))
print('SKLKEYS', sorted(s.keys()))
print('merged', p['merged'])
print('w265_only', p['w265_only'])
print('semu_keys', [k for k in p if 'se_mu' in k])
print('A_p95', f['full_sharpe_p95'], 'A_p99', f['full_sharpe_p99'])
for k in sorted(s): print('SKL', k, '=', s[k])
