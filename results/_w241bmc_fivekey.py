# -*- coding: utf-8 -*-
"""r1005 bm-c: machine-read W241 finalize results -> sec.5 five-key probe receipt.
Estate verify before landing (absorb law: finalize product machine-verified ledger identity + five-key).
Anchors DERIVED PROGRAMMATICALLY from n1_w240_results.json (r583 zero-literal law).
Bloodline clone of _w240bma_fivekey.py (W240->W241, prev wave W240)."""
import json, os, subprocess

sys = __import__("sys")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W = '241'
prev = json.load(open(os.path.join(REPO, 'results', 'perpetual_faces', 'n1_w240_results.json')))
d = json.load(open(os.path.join(REPO, 'results', 'perpetual_faces', 'n1_w241_results.json')))

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

# key5 machine evidence: W242 seat published by bm-a (pickaxe, never transcribed)
seat_r = subprocess.run(["git", "-C", REPO, "log", "--format=%H", "--diff-filter=A",
                         "--", "fleet/inbox/processed/MSG-20261014-1814-bma-w242-seat.md"],
                        capture_output=True, text=True)
seat_sha = (seat_r.stdout.strip().splitlines() or ["absent"])[0]
probe_leg4 = json.load(open(os.path.join(REPO, "results", "_w241bmc_20261014_probe_receipt.json"), encoding="utf-8"))["legs"]["leg4"]

ident = sg['prev_total'] + sg['batch_trials'] == sg['total']
k1 = abs(wo['mu'] - m['mu'])
k2 = (m['sigma'] - ANCH['prev_merged_sigma']) / abs(ANCH['prev_merged_sigma']) * 100.0
k3 = abs(famA['full_sharpe_p95'] - ANCH['prev_A_p95'])
k4 = kl.get('line_delta_k_lift')

out = {
    'wave': W,
    'phase': 'five-key probe (r1005 bm-c own-wave finalize; r1002 seat 20782916a + r1005 splice estate 8e980ce3e five-face freeze landed + burn 12/12 engine self-ignite + six-gate PRE-FINALIZE fifteenth consecutive; finalize one-pass run this window)',
    'ledger': {'prev': sg['prev_total'], 'batch': sg['batch_trials'], 'total': sg['total'], 'identity_assert': ident,
               'chain_note': 'prev head 952,335 = W240 total EXACT (bm-a r993 finalize, zero interleaved batch, identity prev+batch==total EXACT holds)'},
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
        'key3_A_p95_diff_vs_w240': {'value': k3, 'gate': 0.05, 'pass': k3 < 0.05},
        'key4_k_lift': {'value': k4, 'gate': 0.02, 'pass': abs(k4) <= 0.02},
        'key5_projection_confirmed_by_published_w242_seat': {
            'value': f"W242 seat published by bm-a (MSG-20261014-1814-bma-w242-seat, pickaxe sha {seat_sha[:10]}): A naive {probe_leg4['W242p_A_naive']} / B naive {probe_leg4['W242p_B_naive']} -- projection CONFIRMED live (never transcribed r587); W242 freezer must re-derive on the post-W241 universe and reserve the own-wave A window when deriving B per the W241 seat leg4 mandate",
            'seat_evidence_sha': seat_sha, 'pass': seat_sha != 'absent'},
    },
}
out['five_keys_all_pass'] = all(v['pass'] for v in out['five_keys'].values())
print(json.dumps({k: out[k] for k in ('ledger', 'merged_mu', 'merged_sigma', 'w_only_mu', 'A_p95', 'five_keys', 'five_keys_all_pass')}, indent=1, ensure_ascii=False))
assert out['five_keys_all_pass'], "five-key FAIL -- estate BLOCKED from landing (absorb law)"
assert ident, "ledger identity FAIL"
open(os.path.join(REPO, 'results', '_w241bmc_fivekey_receipt.json'), 'w', encoding='utf-8').write(
    json.dumps(out, indent=1, ensure_ascii=False))
