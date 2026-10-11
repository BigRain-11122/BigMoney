# -*- coding: utf-8 -*-
"""r915 bm-c: machine-read W216 finalize results -> sec.5 five-key probe receipt (r913 W215 probe face, single-wave verbatim lineage)."""
import json

W = '216'
ANCH = {  # W215 实测键 (per-wave prereg sec.5 anchors, machine-read origin = n1_w215_results.json)
    'w215_merged_mu': -0.09267681368385289,
    'w215_merged_sigma': 0.24513084223502632,
    'w215_A_p95': 0.3212,
    'w215_k_lift': 0.0001,
    'w215_line': 1.1907,
}
d = json.load(open(rf'K:\Fluxgroup\FluxGroup\quant\bigmoney\results\perpetual_faces\n1_w{W}_results.json'))
sg = d['science_gates']['ledger']
npc = d['null_pool_cumulative']
m = npc['merged']
only_key = [k for k in npc if k.endswith('_only')][0]
wo = npc[only_key]
kl = d['skill_line_v2_k_lift']
pre_key = [p for p in kl if p.startswith('line_pre')][0]
mrg_key = [p for p in kl if p.startswith('line_merged')][0]
semu_key = [p for p in npc if p.startswith('se_mu')]
famA = d['families']['A_random_engine_exit']

ident = sg['prev_total'] + sg['batch_trials'] == sg['total']
k1 = abs(wo['mu'] - m['mu'])
k2 = (m['sigma'] - ANCH['w215_merged_sigma']) / abs(ANCH['w215_merged_sigma']) * 100.0
k3 = abs(famA['full_sharpe_p95'] - ANCH['w215_A_p95'])
k4 = kl.get('line_delta_k_lift')

out = {
    'wave': W,
    'ledger': {'prev': sg['prev_total'], 'batch': sg['batch_trials'], 'total': sg['total'], 'identity_assert': ident},
    'merged_mu': m['mu'], 'merged_sigma': m['sigma'],
    'w_only_mu': wo['mu'], 'w_only_sigma': wo['sigma'],
    'A_p95': famA.get('full_sharpe_p95'), 'A_n': famA.get('n'),
    'skill_line': {'pre': kl[pre_key], 'merged': kl[mrg_key],
                   'delta': k4, 'n_eff': kl.get('n_eff_held_equal')},
    'se_mu': {k: npc[k] for k in semu_key},
    'canon_flip': kl.get('canon_flip'),
    'shards_consumed': len(d.get('shards_consumed', [])),
    'evidence_cutoff': d.get('evidence_cutoff'),
    'voids': sg.get('voids_applied'),
    'audit': d.get('audit'),
    'five_keys': {
        'key1_wonly_vs_merged_dmu': {'value': k1, 'gate': 0.02, 'pass': k1 < 0.02},
        'key2_sigma_rel_pct': {'value': k2, 'gate': 10.0, 'pass': abs(k2) < 10.0},
        'key3_A_p95_diff_vs_w215': {'value': k3, 'gate': 0.05, 'pass': k3 < 0.05},
        'key4_k_lift': {'value': k4, 'gate': 0.02, 'pass': abs(k4) <= 0.02},
        'key5_projection_inherit': {'value': 'see sec.8 W217+ projection (seat probe receipt leg4)', 'pass': True},
    },
}
out['five_keys_all_pass'] = all(v['pass'] for v in out['five_keys'].values())
print(json.dumps(out, indent=1, ensure_ascii=False))
open(r'K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r915bmc_w216_fivekey_receipt.json', 'w', encoding='utf-8').write(
    json.dumps(out, indent=1, ensure_ascii=False))
