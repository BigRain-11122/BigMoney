import json
d = json.load(open('results/perpetual_faces/n1_w47_results.json', encoding='utf-8'))
print('cum:', json.dumps(d['null_pool_cumulative'], ensure_ascii=False, indent=1))
print('skill:', json.dumps(d['skill_line_v2_k_lift'], ensure_ascii=False, indent=1))
fa = d['families']['A_random_engine_exit']
print('A stats: p95=%s p99=%s mu=%s n=%s' % (fa['full_sharpe_p95'], fa['full_sharpe_p99'], fa['full_sharpe_mu'], fa['n']))
print('B n:', d['families']['B_random_entry_random_exit']['n'])
print('ledger:', json.dumps(d['science_gates']['ledger'], ensure_ascii=False))
print('audit:', d['audit'])
w46 = json.load(open('results/perpetual_faces/n1_w46_results.json', encoding='utf-8'))
fa46 = w46['families']['A_random_engine_exit']
print('W46 A stats: p95=%s mu=%s' % (fa46['full_sharpe_p95'], fa46['full_sharpe_mu']))
w46only = w46['null_pool_cumulative']['w46_only']
print('W46 only:', json.dumps(w46only))
