import json, math
w145 = json.load(open(r'results\perpetual_faces\n1_w145_results.json', encoding='utf-8'))
print('W145 skill_line:', json.dumps(w145['skill_line_v2_k_lift'], ensure_ascii=False))
npc = w145['null_pool_cumulative']
print('W145 mu_delta key:', {k: v for k, v in npc.items() if 'mu_delta' in str(k) or 'se_mu' in str(k)})
print('W145 audit:', json.dumps(w145.get('audit')))
print('W145 ledger:', json.dumps(w145['science_gates']['ledger'])[:280])
famA = w145['families']['A_random_engine_exit']
print('W145 A p95/p99/mu:', famA['full_sharpe_p95'], famA['full_sharpe_p99'], famA['full_sharpe_mu'])
print('W145 se_mu recomputed: %.9f' % (npc['merged']['sigma'] / math.sqrt(npc['merged']['n_values'])))
w146 = json.load(open(r'results\perpetual_faces\n1_w146_results.json', encoding='utf-8'))
famA6 = w146['families']['A_random_engine_exit']
print('W146 audit:', json.dumps(w146.get('audit')))
print('W146 A p95 diff vs W145 anchor: %.4f' % (famA6['full_sharpe_p95'] - 0.3095))
print('W146 |only-mu - merged-mu| = %.6f' % abs(npc2_mu := w146['null_pool_cumulative']['w146_only']['mu'] - w146['null_pool_cumulative']['merged']['mu']))
print('W146 sigma rel change vs pre: %.5f%%' % (100.0 * (w146['null_pool_cumulative']['merged']['sigma'] / w146['null_pool_cumulative']['pre_w146_cumulative']['sigma'] - 1.0)))
