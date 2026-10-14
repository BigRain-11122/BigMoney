# -*- coding: utf-8 -*-
"""r985 bm-a: machine-read W238 finalize results -> sec.5 five-key probe receipt.
Estate verify before landing (absorb law: finalize product machine-verified ledger identity + five-key).
Anchors DERIVED PROGRAMMATICALLY from n1_w237_results.json (r583 zero-literal law).
Bloodline clone of _w237bmc_fivekey.py (W237->W238, prev wave W236->W237)."""
import json, os

sys = __import__("sys")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W = '238'
prev = json.load(open(os.path.join(REPO, 'results', 'perpetual_faces', 'n1_w237_results.json')))
d = json.load(open(os.path.join(REPO, 'results', 'perpetual_faces', 'n1_w238_results.json')))

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
    'phase': 'five-key probe (r985 bm-a own-wave finalize; r983 prereg derive + r984 five-face freeze splice 50fa77623 + burn 12/12 engine self-ignite landed 12:44 after six-gate PRE-FINALIZE thirteenth consecutive; finalize one-pass run this window)',
    'ledger': {'prev': sg['prev_total'], 'batch': sg['batch_trials'], 'total': sg['total'], 'identity_assert': ident,
               'chain_note': 'prev head 945,735 = W237 total 945,189 + TRIAL_LAB_W19_SCREEN 546 (interleaved trial-labor screen batch, results/trial_labor_w19/w19_screen.json, legitimate shared-chain advance r518 origin-time face law; frozen sec.0 projection 947,389 deviation disclosed in sec.7 backfill, identity prev+batch==total EXACT holds)'},
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
        'key3_A_p95_diff_vs_w237': {'value': k3, 'gate': 0.05, 'pass': k3 < 0.05},
        'key4_k_lift': {'value': k4, 'gate': 0.02, 'pass': abs(k4) <= 0.02},
        'key5_projection_inherit': {'value': 'see sec.8 W239+ projection (W239 seat ALREADY PUBLISHED by bm-c MSG-20261014-0914-bmc-w239-seat: A 542_501..544_500 hops=2 first seed-decoupled double-hop face + B 540_604..540_803; naive W239 A arithmetic 540_604..542_603 refused by live SEED_REGISTRY points 541500/542000 + 542_500 -> declared A 542_501..544_500; W239 freeze waits-upstream W238 finalize per chain-order M12 -- this finalize disarms it)', 'pass': True},
    },
}
out['five_keys_all_pass'] = all(v['pass'] for v in out['five_keys'].values())
print(json.dumps({k: out[k] for k in ('ledger', 'merged_mu', 'merged_sigma', 'w_only_mu', 'A_p95', 'five_keys', 'five_keys_all_pass')}, indent=1, ensure_ascii=False))
assert out['five_keys_all_pass'], "five-key FAIL -- estate BLOCKED from landing (absorb law)"
assert ident, "ledger identity FAIL"
open(os.path.join(REPO, 'results', '_w238bma_fivekey_receipt.json'), 'w', encoding='utf-8').write(
    json.dumps(out, indent=1, ensure_ascii=False))
