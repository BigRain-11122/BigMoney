# -*- coding: utf-8 -*-
import json, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
for w in (167, 168):
    r = json.load(open(f'results/perpetual_faces/n1_w{w}_results.json', encoding='utf-8'))
    npc = r['null_pool_cumulative']; kl = r['skill_line_v2_k_lift']
    a = r['families'].get('A_random_engine_exit', {})
    K = npc['merged']['n_values']
    se_key = f'se_mu_at_k{K}'
    pre_key = f'line_pre_w{w}'
    mrg_key = f'line_merged_{K}'
    print(f'== W{w}:')
    print(' merged n:', K, 'mu:', round(npc['merged']['mu'], 6), 'sigma:', round(npc['merged']['sigma'], 6))
    wo = npc[f'w{w}_only']
    print(' w-only n:', wo['n_values'], 'mu:', round(wo['mu'], 6), 'sigma:', round(wo['sigma'], 6))
    print(' mu_delta:', npc.get(f'mu_delta_w{w}_vs_w{w-1}ext'))
    print(' se_mu:', npc.get(se_key))
    print(' A p95:', a.get('full_sharpe_p95'), 'p99:', a.get('full_sharpe_p99'))
    print(' k_lift:', {k: kl.get(k) for k in (pre_key, mrg_key, 'line_delta_k_lift', 'n_eff_held_equal')})
    print(' canon_flip:', kl.get('canon_flip'))
