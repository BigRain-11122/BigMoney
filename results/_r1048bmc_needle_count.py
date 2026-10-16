# -*- coding: utf-8 -*-
# needle count probe for the W251 fivekeys derive
import io
t = io.open('results/_r1046bmc_w250_fivekeys.py', encoding='utf-8').read()
ns = [
 '_r1046bmc_w250_fivekeys.json',
 'n1_w250_results.json',
 'r1046 bm-c: W250 five-prediction-key machine assertion (prereg sec.5 vs finalize face)',
 'W250 finalize face',
 'W249 fivekeys',
 'W249 precedent, one-pass finalize window',
 'KEY_MU_MERGED_W249 = -0.09277202',
 'KEY_MU_W249_ONLY = -0.08793',
 'KEY_SIGMA_W249 = 0.2450284',
 'KEY_A_P95_W249 = 0.3158',
 'KEY_LINE_W249_MERGED = 1.1938',
 'KEY_SE_MU_W249 = 0.000332',
 'KEY_KLIFT_W249 = 0.0000',
 'pool["w250_only"]["mu"]',
 'pool["w250_only"]["sigma"]',
 'se_mu_at_k547920',
 'line_pre_w250',
 'line_merged_547920',
 'key1_w250_vs_merged_mu_gap',
 'key1b_merged_vs_w249_key',
 'gap1 = abs(w250_mu',
 '"wave": 250',
 '972135',
 '"se_mu_k547920": se_mu',
 '"n_eff_held": sl["n_eff_held_equal"], "line_pre_w250": line_pre',
 '"line_merged_547920": line_merged, "k_lift_delta": klift',
 '"prev_total": 972135, "batch_trials": 2200, "total": 974335',
 '"exact": (972135 + 2200) == 974335',
 'sec5_item5_projection_note',
]
for n in ns:
    print(t.count(n), '|', n)
