"""r876 bm-a W185 buildgen facts extraction (dead-session carry: the 10:38 firing
was killed at 11:03 mid 'final ordinal count check before writing W185 buildgen';
this script completes that check and emits the single facts file the W185 buildgen
(r872 bloodline _r872bma_w184_buildgen.py -> _r877bma_w185_buildgen.py) consumes.
All values DERIVED from on-disk result files -- zero hand transcription (r587)."""
import json, hashlib, os

R = {}

# --- leg A: W184 finalize anchors (from n1_w184_results.json) ---
w184 = json.load(open('results/perpetual_faces/n1_w184_results.json', encoding='utf-8'))
cum = w184['null_pool_cumulative']
R['w184_finalize'] = {
    'k_merged': cum['merged']['n_values'],                    # 402,720
    'ledger_head': w184['science_gates']['ledger']['total'],   # 812,128
    'ledger_prev': w184['science_gates']['ledger']['prev_total'],
    'merged_mu': cum['merged']['mu'],
    'w184_only_mu': cum['w184_only']['mu'],
    'w184_only_sigma': cum['w184_only']['sigma'],
    'sigma': cum['merged']['sigma'],
    'se_mu': cum['se_mu_at_k402720'],
    'a_p95': w184['families']['A_random_engine_exit']['full_sharpe_p95'],
    'a_p99': w184['families']['A_random_engine_exit']['full_sharpe_p99'],
    'skill_line': w184['skill_line_v2_k_lift']['line_merged_402720'],
    'skill_line_pre': w184['skill_line_v2_k_lift']['line_pre_w184'],
    'k_lift': w184['skill_line_v2_k_lift']['line_delta_k_lift'],
    'n_eff_held_equal': w184['skill_line_v2_k_lift']['n_eff_held_equal'],
    'evidence_cutoff': w184['evidence_cutoff'],
}

# --- leg B: W185 seat/probe bands (from r875 probe receipt) ---
pr = json.load(open('results/_r875bma_w185_probe_receipt.json', encoding='utf-8'))
assert pr['verdict'] == 'ADMIT'
R['w185_bands'] = {
    'A': pr['bands']['A'], 'B': pr['bands']['B'],
    'hops_A': pr['legs']['leg1']['hops_A'], 'hops_B': pr['legs']['leg1']['hops_B'],
    'A_semantics': pr['legs']['leg1']['A_semantics'],
    'B_semantics': pr['legs']['leg1']['B_semantics'],
    'leg0_rows': pr['legs']['leg0']['rows'],
    'leg0_tail': pr['legs']['leg0']['tail'],
    'owner_rows': pr['legs']['leg0']['owner_rows'],
    'bma_rows': pr['legs']['leg0']['bma_rows'],
    'ordinal': pr['legs']['leg0']['ordinal'],
    'bma_ordinal': pr['legs']['leg0']['bma_ordinal'],
    'conflicts': pr['legs']['leg2']['conflicts'],
    'origin_vacancy': pr['legs']['leg3']['origin_vacancy'],
}

# --- leg C: W186+ projection (leg4 verbatim) ---
R['w186p_projection'] = pr['legs']['leg4']

# --- leg D: src + seat presence (dead-session extract face) ---
src = 'results/_r876bma_w185_prereg_src.txt'
seat_processed = 'fleet/inbox/processed/MSG-2026-10-08-1032-bma-w185-seat.md'
R['inputs'] = {
    'src_extract': {'path': src, 'bytes': os.path.getsize(src),
                   'sha256': hashlib.sha256(open(src, 'rb').read()).hexdigest()},
    'seat_msg_processed_present': os.path.exists(seat_processed),
    'probe_receipt': 'results/_r875bma_w185_probe_receipt.json',
    'bloodline_buildgen': 'results/_r872bma_w184_buildgen.py',
    'bloodline_build': 'results/_r872bma_w184_prereg_build.py',
}

# --- leg E: ordinal count check (the dead session's pending step) ---
# pre-W185 registry must be 182 rows tail W184 (leg0 machine-verified above);
# engine_owner==bm-a rows 100 -> W185 = 101st own wave; engine line ordinal 175.
assert R['w185_bands']['leg0_rows'] == 182 and R['w185_bands']['leg0_tail'] == 'W184'
assert R['w185_bands']['ordinal'] == 175 and R['w185_bands']['bma_ordinal'] == 101
assert R['w185_bands']['conflicts'] == 0 and R['w185_bands']['origin_vacancy'] is True
assert R['w184_finalize']['k_merged'] == 402720 and R['w184_finalize']['ledger_head'] == 812128
R['ordinal_count_check'] = 'PASS (182 rows tail W184 / ordinal 175 / bma 101st own / conflicts 0 / vacancy True / K 402,720 / head 812,128)'

out = 'results/_r876bma_w185_facts.json'
json.dump(R, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('WROTE', out)
print('check:', R['ordinal_count_check'])
print('bands A=%s B=%s | K=%d head=%d merged_mu=%.6f sigma=%.6f se_mu=%.6f a_p95=%.4f line=%.4f k_lift=%+.4f' % (
    R['w185_bands']['A'], R['w185_bands']['B'], R['w184_finalize']['k_merged'],
    R['w184_finalize']['ledger_head'], R['w184_finalize']['merged_mu'],
    R['w184_finalize']['sigma'], R['w184_finalize']['se_mu'],
    R['w184_finalize']['a_p95'], R['w184_finalize']['skill_line'], R['w184_finalize']['k_lift']))
