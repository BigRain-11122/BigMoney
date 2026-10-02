import json
d = json.load(open('results/perpetual_faces/n1_w96_results.json', encoding='utf-8'))
npc = d.get('null_pool_cumulative', {})
for k, v in npc.items():
    print('NPC', k, json.dumps(v, ensure_ascii=False)[:200])
sl = d.get('skill_line_v2_k_lift', {})
print('SKILL', json.dumps(sl, ensure_ascii=False)[:400])
sgb = d.get('science_gates', {})
print('SG ledger', json.dumps(sgb.get('ledger'), ensure_ascii=False)[:260])
fams = d.get('families', {})
a = fams.get('A_random_engine_exit', {})
runs = a.get('runs', [])
import statistics
full = [r['full']['sharpe'] for r in runs]
full.sort()
import math
p95 = full[int(math.ceil(0.95 * len(full))) - 1]
print('A n:', len(full), 'p95(sort):', p95)
print('keys:', list(d.keys()))
