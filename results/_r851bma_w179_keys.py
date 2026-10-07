# -*- coding: utf-8 -*-
import json, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
r = json.load(open('results/perpetual_faces/n1_w179_results.json', encoding='utf-8'))
npc = r['null_pool_cumulative']
kl = r['skill_line_v2_k_lift']
out = {
 'npc_keys': sorted(npc.keys()),
 'merged': npc['merged'],
 'w_only_key': [k for k in npc if 'only' in k],
 'pre_key': [k for k in npc if k.startswith('pre_')],
 'kl_keys': sorted(kl.keys()),
 'kl': kl,
 'se_mu_key': [k for k in npc if 'se_mu' in k],
 'mu_delta_key': [k for k in npc if 'mu_delta' in k],
 'A_p95': r['families']['A_random_engine_exit']['full_sharpe_p95'],
 'ledger': (r.get('science_gates') or {}).get('ledger'),
}
json.dump(out, open('results/_r851bma_w179_keys.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
print('written results/_r851bma_w179_keys.json')
