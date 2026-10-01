"""r555 helper: dump W46 finalize anchor values for W47 prereg drafting."""
import subprocess, json

d = json.loads(subprocess.check_output(['git', 'show', 'origin/main:results/perpetual_faces/n1_w46_results.json']))
print('== null_pool_cumulative ==')
npc = d.get('null_pool_cumulative', {})
print(json.dumps({k: npc[k] for k in npc if not isinstance(npc[k], (list, dict))}, ensure_ascii=False, indent=1))
print('K =', npc.get('K'), '| n_values =', npc.get('n_values'))
print('mu =', npc.get('mu'), '| sigma =', npc.get('sigma'), '| se_mu =', npc.get('se_mu'))
print('a_p95 =', npc.get('a_p95'), '| a_p99 =', npc.get('a_p99'))
print('== skill_line_v2_k_lift ==', d.get('skill_line_v2_k_lift'))
print('== ledger keys ==')
for k in npc:
    if 'ledger' in str(k) or 'prev' in str(k) or 'total' in str(k):
        print(' ', k, '=', npc[k])
print('== audit ==', json.dumps(d.get('audit', {}), ensure_ascii=False)[:400])
print('== families ==', json.dumps(d.get('families', {}), ensure_ascii=False)[:400])
print('== universe ==', json.dumps(d.get('universe', {}), ensure_ascii=False)[:400])
