import json, math
d = json.load(open('results/perpetual_faces/n1_w98_results.json', encoding='utf-8'))
npc = d['null_pool_cumulative']
for k in ['pre_w98_cumulative', 'w98_only', 'merged']:
    v = npc[k]
    print(k, 'n=%d mu=%.10f sigma=%.10f' % (v['n_values'], v['mu'], v['sigma']))
print('mu_delta field:', npc.get('mu_delta_w98_vs_w97ext'))
print('se_mu:', npc.get('se_mu_at_k213520'))
sl = d['skill_line_v2_k_lift']
print('skill:', json.dumps(sl, ensure_ascii=False)[:260])
a = d['families']['A_random_engine_exit']['runs']
full = sorted(r['full']['sharpe'] for r in a)
p95 = full[int(math.ceil(0.95 * len(full))) - 1]
print('A n:', len(full), 'p95:', p95, 'gate diff vs 0.3256:', abs(p95 - 0.3256))
