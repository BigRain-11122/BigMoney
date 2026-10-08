"""r880 bm-a W186 buildgen facts extraction (r876 bloodline, W185->W186). Emits
the single facts file the W186 buildgen (r877 bloodline _r877bma_w185_buildgen.py
-> next-round _r88Xbma_w186_buildgen.py) consumes. All values DERIVED from
on-disk result files -- zero hand transcription (r587)."""
import json, hashlib, os, subprocess

R = {}

# --- leg A: W185 finalize anchors (from n1_w185_results.json) ---
w185 = json.load(open('results/perpetual_faces/n1_w185_results.json', encoding='utf-8'))
cum = w185['null_pool_cumulative']
R['w185_finalize'] = {
    'k_merged': cum['merged']['n_values'],                    # 404,920
    'ledger_head': w185['science_gates']['ledger']['total'],   # 814,328
    'ledger_prev': w185['science_gates']['ledger']['prev_total'],
    'merged_mu': cum['merged']['mu'],
    'w185_only_mu': cum['w185_only']['mu'],
    'w185_only_sigma': cum['w185_only']['sigma'],
    'sigma': cum['merged']['sigma'],
    'se_mu': cum['se_mu_at_k404920'],
    'a_p95': w185['families']['A_random_engine_exit']['full_sharpe_p95'],
    'a_p99': w185['families']['A_random_engine_exit']['full_sharpe_p99'],
    'skill_line': w185['skill_line_v2_k_lift']['line_merged_404920'],
    'skill_line_pre': w185['skill_line_v2_k_lift']['line_pre_w185'],
    'k_lift': w185['skill_line_v2_k_lift']['line_delta_k_lift'],
    'n_eff_held_equal': w185['skill_line_v2_k_lift']['n_eff_held_equal'],
    'evidence_cutoff': w185['evidence_cutoff'],
}

# --- leg B: W186 seat/probe bands (from r880 probe receipt) ---
pr = json.load(open('results/_r880bma_w186_probe_receipt.json', encoding='utf-8'))
assert pr['verdict'] == 'ADMIT'
R['w186_bands'] = {
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

# --- leg C: W187+ projection (leg4 verbatim) ---
R['w187p_projection'] = pr['legs']['leg4']

# --- leg D: src extract (origin blob raw bytes, r877 binary-identity law) + seat presence ---
src = 'results/_r880bma_w186_prereg_src.txt'
blob = subprocess.run(['git', 'show', 'origin/main:research/PERPETUAL_N1_W185_PREREG.md'],
                       capture_output=True, check=True).stdout
open(src, 'wb').write(blob)
seat_inbox = 'fleet/inbox/MSG-2026-10-08-1354-bma-w186-seat.md'
seat_processed = 'fleet/inbox/processed/MSG-2026-10-08-1354-bma-w186-seat.md'
R['inputs'] = {
    'src_extract': {'path': src, 'bytes': os.path.getsize(src),
                   'sha256': hashlib.sha256(open(src, 'rb').read()).hexdigest()},
    'seat_msg_inbox_present': os.path.exists(seat_inbox),
    'seat_msg_processed_present': os.path.exists(seat_processed),
    'probe_receipt': 'results/_r880bma_w186_probe_receipt.json',
    'bloodline_buildgen': 'results/_r877bma_w185_buildgen.py',
    'bloodline_build': 'results/_r877bma_w185_prereg_build.py',
}

# --- leg E: ordinal count check ---
# pre-W186 registry must be 183 rows tail W185 (leg0 machine-verified above);
# engine_owner==bm-a rows 101 -> W186 = 102nd own wave; engine line ordinal 176.
assert R['w186_bands']['leg0_rows'] == 183 and R['w186_bands']['leg0_tail'] == 'W185'
assert R['w186_bands']['ordinal'] == 176 and R['w186_bands']['bma_ordinal'] == 102
assert R['w186_bands']['conflicts'] == 0 and R['w186_bands']['origin_vacancy'] is True
assert R['w185_finalize']['k_merged'] == 404920 and R['w185_finalize']['ledger_head'] == 814328
R['ordinal_count_check'] = 'PASS (183 rows tail W185 / ordinal 176 / bma 102nd own / conflicts 0 / vacancy True / K 404,920 / head 814,328)'

out = 'results/_r880bma_w186_facts.json'
json.dump(R, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('WROTE', out)
print('check:', R['ordinal_count_check'])
print('bands A=%s B=%s | K=%d head=%d merged_mu=%.6f sigma=%.6f se_mu=%.6f a_p95=%.4f line=%.4f k_lift=%+.4f' % (
    R['w186_bands']['A'], R['w186_bands']['B'], R['w185_finalize']['k_merged'],
    R['w185_finalize']['ledger_head'], R['w185_finalize']['merged_mu'],
    R['w185_finalize']['sigma'], R['w185_finalize']['se_mu'],
    R['w185_finalize']['a_p95'], R['w185_finalize']['skill_line'], R['w185_finalize']['k_lift']))
