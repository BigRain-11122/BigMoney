# -*- coding: utf-8 -*-
# r846 bm-c: W206 §5 four pre-keys machine verification (per W204 §7 precedent)
import io, json
d = json.load(io.open('results/perpetual_faces/n1_w206_results.json', encoding='utf-8'))
w204 = json.load(io.open('results/perpetual_faces/n1_w204_results.json', encoding='utf-8'))
npc = d['null_pool_cumulative']
skl = d['skill_line_v2_k_lift']
fams = d['families']

# anchors from frozen prereg §5 (W204 landed keys)
KEY_MU = -0.092697      # W204 merged pool mu
KEY_SIGMA = 0.245097    # W204 merged sigma
KEY_A_P95 = 0.3053      # W204 A-band full_sharpe_p95

w_only_mu = npc['w206_only']['mu']
merged_mu = npc['merged']['mu']
merged_sigma = npc['merged']['sigma']
pre_sigma = npc['pre_w206_cumulative']['sigma']
a_runs = fams['A_random_engine_exit']['runs']
fulls = sorted(r['full']['sharpe'] for r in a_runs)
import math
n = len(fulls)
a_p95 = fulls[max(0, int(round(0.95 * n)) - 1)]

keys = {}
keys['k1_mu_delta_lt_0p02'] = abs(w_only_mu - KEY_MU) < 0.02
keys['k1_mu_delta_value'] = round(w_only_mu - KEY_MU, 6)
keys['k1_machine_field_delta'] = npc.get('mu_delta_w206_vs_w205ext')
keys['k2_sigma_rel_change_lt_10pct'] = abs(merged_sigma / KEY_SIGMA - 1) < 0.10
keys['k2_sigma_rel_change_value'] = round(merged_sigma / KEY_SIGMA - 1, 6)
keys['k3_A_p95_diff_lt_0p05'] = abs(a_p95 - KEY_A_P95) < 0.05
keys['k3_A_p95_diff_value'] = round(a_p95 - KEY_A_P95, 4)
keys['k4_k_lift_le_0p02'] = abs(skl['line_delta_k_lift']) <= 0.02
keys['k4_k_lift_value'] = skl['line_delta_k_lift']
se_mu = npc['se_mu_at_k451120']
ok = all(v for k, v in keys.items() if isinstance(v, bool))
res = {'wave': 206, 'keys': keys, 'a_p95': a_p95, 'se_mu': se_mu,
       'merged_mu': merged_mu, 'merged_sigma': merged_sigma,
       'w_only_mu': w_only_mu, 'w204_key_mu': KEY_MU,
       'verdict': 'ALL_PASS' if ok else 'FAIL'}
io.open('results/_r846bmc_w206_s5fourkeys.json', 'w', encoding='utf-8').write(
    json.dumps(res, ensure_ascii=False, indent=1))
print(json.dumps(keys, ensure_ascii=False))
print('se_mu chain: W204 0.000367 -> W206', se_mu)
print('VERDICT:', res['verdict'])
