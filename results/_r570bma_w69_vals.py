# -*- coding: utf-8 -*-
# r570 bm-a: extract W69 finalize numeric anchors for W72 prereg section 5
import json

r = json.load(open('results/perpetual_faces/n1_w69_results.json', encoding='utf-8'))
npc = r['null_pool_cumulative']
w69 = npc['w69_only']
merged = npc['merged']
sk = r['skill_line_v2_k_lift']
famA = r['families']['A_random_engine_exit']
famB = r['families']['B_random_entry_random_exit']
print('W69_ONLY:', json.dumps({k: w69[k] for k in w69 if isinstance(w69[k], (int, float))}, indent=1))
print('MERGED:', json.dumps({k: merged[k] for k in merged if isinstance(merged[k], (int, float))}, indent=1))
print('K_LIFT:', json.dumps({k: sk[k] for k in sk if isinstance(sk[k], (int, float))}, indent=1))
print('PRE_W69:', json.dumps({k: npc['pre_w69_cumulative'][k] for k in npc['pre_w69_cumulative'] if isinstance(npc['pre_w69_cumulative'][k], (int, float))}, indent=1))
print('FAM_A:', json.dumps({k: famA[k] for k in famA if isinstance(famA[k], (int, float))}, indent=1))
print('LEDGER:', json.dumps(r['science_gates']['ledger'], ensure_ascii=False))
print('SE_MU_at_K149720:', npc.get('se_mu_at_k149720'))
print('mu_delta_w69_vs_w68ext:', npc.get('mu_delta_w69_vs_w68ext'))
