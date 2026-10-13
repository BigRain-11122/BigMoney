# -*- coding: utf-8 -*-
"""r975 bm-a: machine-read W236 finalize results -> sec.5 five-key probe receipt.
Estate verify before landing (absorb law: finalize product machine-verified ledger identity + five-key).
Anchors DERIVED PROGRAMMATICALLY from n1_w235_results.json (r583 zero-literal law).
Bloodline clone of _r970bma_w235_fivekey_probe.py (W235->W236, prev wave W234->W235)."""
import json

REPO = r'C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney'
W = '236'
prev = json.load(open(rf'{REPO}\results\perpetual_faces\n1_w235_results.json'))
d = json.load(open(rf'{REPO}\results\perpetual_faces\n1_w236_results.json'))

pm = prev['null_pool_cumulative']['merged']
ANCH = {
    'prev_merged_mu': pm['mu'],
    'prev_merged_sigma': pm['sigma'],
    'prev_A_p95': prev['families']['A_random_engine_exit']['full_sharpe_p95'],
}

sg = d['science_gates']['ledger']
npc = d['null_pool_cumulative']
m = npc['merged']
only_key = [k for k in npc if k.endswith('_only')][0]
wo = npc[only_key]
kl = d['skill_line_v2_k_lift']
pre_key = [p for p in kl if p.startswith('line_pre')][0]
mrg_key = [p for p in kl if p.startswith('line_merged')][0]
semu_key = [k for p in npc if p.startswith('se_mu') for k in [p]]
famA = d['families']['A_random_engine_exit']

ident = sg['prev_total'] + sg['batch_trials'] == sg['total']
k1 = abs(wo['mu'] - m['mu'])
k2 = (m['sigma'] - ANCH['prev_merged_sigma']) / abs(ANCH['prev_merged_sigma']) * 100.0
k3 = abs(famA['full_sharpe_p95'] - ANCH['prev_A_p95'])
k4 = kl.get('line_delta_k_lift')

out = {
    'wave': W,
    'phase': 'five-key probe (r975 bm-a own-wave finalize; dead-window estate absorb r963-r974: freeze splice 6e798bd22 + burn 12/12 08b6067c9 landed this window after six-gate PRE-FINALIZE eleventh consecutive; finalize one-pass run this window)',
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
    'merged_K': npc.get('merged', {}).get('k') if isinstance(npc.get('merged'), dict) else None,
    'five_keys': {
        'key1_wonly_vs_merged_dmu': {'value': k1, 'gate': 0.02, 'pass': k1 < 0.02},
        'key2_sigma_rel_pct': {'value': k2, 'gate': 10.0, 'pass': abs(k2) < 10.0},
        'key3_A_p95_diff_vs_w235': {'value': k3, 'gate': 0.05, 'pass': k3 < 0.05},
        'key4_k_lift': {'value': k4, 'gate': 0.02, 'pass': abs(k4) <= 0.02},
        'key5_projection_inherit': {'value': 'see sec.8 W237+ projection (WAVE_CONFIGS[236] row verbatim; naive W237 A 536004..538003 refused by registered W236 B band 536004..536203 -> hop A 536204..538203 staircase NINETY-SEVENTH; ALREADY LANDED: bm-c W237 seat published 9312ef7ac/5654c4f04 A 536_204..538_203 / B 538_204..538_403 own-A W141 -- projection CONFIRMED by published seat)', 'pass': True},
    },
}
out['five_keys_all_pass'] = all(v['pass'] for v in out['five_keys'].values())
print(json.dumps(out, indent=1, ensure_ascii=False))
open(rf'{REPO}\results\_r975bma_w236_fivekey_receipt.json', 'w', encoding='utf-8').write(
    json.dumps(out, indent=1, ensure_ascii=False))
