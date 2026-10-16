# -*- coding: utf-8 -*-
# r1048 bm-c: derive W251 fivekeys script from committed W250 template
# (_r1046bmc_w250_fivekeys.py) via count-asserted ordered transform.
# E63 canon-clone lineage: zero hand-transcription of faces, every leg
# count-asserted, output py_compiled before write-back.
import io
import py_compile

SRC = "results/_r1046bmc_w250_fivekeys.py"
DST = "results/_r1048bmc_w251_fivekeys.py"

t = io.open(SRC, encoding="utf-8").read()
legs = [
    # (needle, replacement, expected_count)
    ('_r1046bmc_w250_fivekeys.json', '_r1048bmc_w251_fivekeys.json', 2),
    ('n1_w250_results.json', 'n1_w251_results.json', 2),
    ('r1046 bm-c: W250 five-prediction-key machine assertion (prereg sec.5 vs finalize face)',
     'r1048 bm-c: W251 five-prediction-key machine assertion (prereg sec.5 vs finalize face)', 1),
    ('_r1043bmc_w249_fivekeys.py (W249 precedent, one-pass finalize window)',
     '_r1046bmc_w250_fivekeys.py (W250 precedent, one-pass finalize window)', 1),
    # frozen keys: W250 finalize actuals (per W251 prereg sec.5 frozen keys)
    ('KEY_MU_MERGED_W249 = -0.09277202        # pre face key (W249 finalize merged mu, K=545,720)',
     'KEY_MU_MERGED_W250 = -0.09276996        # pre face key (W250 finalize merged mu, K=547,920)', 1),
    ('KEY_MU_W249_ONLY = -0.08793', 'KEY_MU_W250_ONLY = -0.09226', 1),
    ('KEY_SIGMA_W249 = 0.2450284', 'KEY_SIGMA_W250 = 0.2450351', 1),
    ('KEY_A_P95_W249 = 0.3158', 'KEY_A_P95_W250 = 0.3235', 1),
    ('KEY_LINE_W249_MERGED = 1.1938           # line_merged@K545,720 (W249 finalize face)',
     'KEY_LINE_W250_MERGED = 1.1939           # line_merged@K547,920 (W250 finalize face)', 1),
    ('KEY_SE_MU_W249 = 0.000332               # se_mu@K545,720 (W249 finalize face)',
     'KEY_SE_MU_W250 = 0.000331               # se_mu@K547,920 (W250 finalize face)', 1),
    ('KEY_KLIFT_W249 = 0.0000                 # K-lift delta (W249 finalize face)',
     'KEY_KLIFT_W250 = 0.0000                 # K-lift delta (W250 finalize face)', 1),
    # result-face field renames (finalize product field faces)
    ('pool["w250_only"]["mu"]', 'pool["w251_only"]["mu"]', 1),
    ('pool["w250_only"]["sigma"]', 'pool["w251_only"]["sigma"]', 1),
    ('pool["se_mu_at_k547920"]', 'pool["se_mu_at_k550120"]', 1),
    ('sl["line_pre_w250"]', 'sl["line_pre_w251"]', 1),
    ('sl["line_merged_547920"]', 'sl["line_merged_550120"]', 1),
    ('"se_mu_k547920": se_mu', '"se_mu_k550120": se_mu', 1),
    # check-name + prose faces
    ('key1_w250_vs_merged_mu_gap', 'key1_w251_vs_merged_mu_gap', 1),
    ('key1b_merged_vs_w249_key', 'key1b_merged_vs_w250_key', 1),
    ('key 1: W250-only mu vs merged mu gap', 'key 1: W251-only mu vs merged mu gap', 1),
    ('w250_mu', 'w251_mu', 3),
    ('merged mu vs W249 pre key', 'merged mu vs W250 pre key', 1),
    ('gap1b = abs(merged_mu - KEY_MU_MERGED_W249)', 'gap1b = abs(merged_mu - KEY_MU_MERGED_W250)', 1),
    ('sigma rel change vs W249 key', 'sigma rel change vs W250 key', 1),
    ('sig_rel = (merged_sigma - KEY_SIGMA_W249) / KEY_SIGMA_W249', 'sig_rel = (merged_sigma - KEY_SIGMA_W250) / KEY_SIGMA_W250', 1),
    ('A-band p95 vs W249 key', 'A-band p95 vs W250 key', 1),
    ('p95d = a_p95 - KEY_A_P95_W249', 'p95d = a_p95 - KEY_A_P95_W250', 1),
    ('se_mu narrowing vs W249 (se_mu chain face, sec.5.4 prose)', 'se_mu narrowing vs W250 (se_mu chain face, sec.5.4 prose)', 1),
    ('checks.append(("key5_se_mu_narrowing", se_mu, KEY_SE_MU_W249, se_mu <= KEY_SE_MU_W249))',
     'checks.append(("key5_se_mu_narrowing", se_mu, KEY_SE_MU_W250, se_mu <= KEY_SE_MU_W250))', 1),
    # receipt faces (post-earlier-legs state: pool["w251_only"] already renamed)
    ('"w250_only": {"mu": w251_mu, "sigma": pool["w251_only"]["sigma"]}',
     '"w251_only": {"mu": w251_mu, "sigma": pool["w251_only"]["sigma"]}', 1),
    ('"wave": 250', '"wave": 251', 1),
    ('"n_eff_held": sl["n_eff_held_equal"], "line_pre_w250": line_pre',
     '"n_eff_held": sl["n_eff_held_equal"], "line_pre_w251": line_pre', 1),
    ('"line_merged_547920": line_merged, "k_lift_delta": klift',
     '"line_merged_550120": line_merged, "k_lift_delta": klift', 1),
    ('"prev_total": 972135, "batch_trials": 2200, "total": 974335,\n                        "exact": (972135 + 2200) == 974335',
     '"prev_total": 974335, "batch_trials": 2200, "total": 976535,\n                        "exact": (974335 + 2200) == 976535', 1),
    # sec5 projection note: W250's note was W251+ projection; W251's is W252+ (staircase face)
    ('"sec5_item5_projection_note": ("W251+ projection key (A naive 567_501..569_500 CLEAN / "\n                                   "B first-clean 565_501..565_700 hops=11 lands-inside-A=false) "\n                                   "= freeze-side face consumed by the W251 freeze party "\n                                   "probe leg4 re-derive (r587 law), NOT a finalize-face key; "\n                                   "recorded here for chain visibility only"),',
     '"sec5_item5_projection_note": ("W252+ projection key (A naive 569_501..571_500 CLEAN hops=0 / "\n                                   "B naive 569_701..569_900 CLEAN-at-naive BUT lands INSIDE W252 A "\n                                   "window = staircase re-emergence face; live re-derive governs "\n                                   "r587) = freeze-side face consumed by the W252 freeze party "\n                                   "probe leg4 re-derive (r587 law), NOT a finalize-face key; "\n                                   "recorded here for chain visibility only"),', 1),
]
for needle, repl, expect in legs:
    n = t.count(needle)
    assert n == expect, f"leg count mismatch: {n} != {expect} for needle: {needle[:60]!r}"
    t = t.replace(needle, repl)

# MUST_NOT: no stale W249/W250-only faces survive in check semantics
must_not = [
    'KEY_MU_MERGED_W249', 'KEY_SIGMA_W249', 'KEY_A_P95_W249', 'KEY_SE_MU_W249',
    'w250_mu', 'se_mu_at_k547920', 'line_merged_547920', '972135 + 2200',
    '"wave": 250',
]
for m in must_not:
    assert m not in t, f"MUST_NOT survived: {m!r}"

io.open(DST, "w", encoding="utf-8", newline="").write(t)
py_compile.compile(DST, doraise=True)
print("DERIVE-OK legs=%d bytes=%d" % (len(legs), len(t.encode("utf-8"))))
