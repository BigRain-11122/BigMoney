# -*- coding: utf-8 -*-
# r1050 bm-c: derive W252 fivekeys script from committed W251 template
# (_r1048bmc_w251_fivekeys.py) via count-asserted ordered transform.
# E63 canon-clone lineage: zero hand-transcription of faces, every leg
# count-asserted, output py_compiled before write-back.
import io
import py_compile

SRC = "results/_r1048bmc_w251_fivekeys.py"
DST = "results/_r1050bmc_w252_fivekeys.py"

t = io.open(SRC, encoding="utf-8").read()
legs = [
    # (needle, replacement, expected_count)
    ('_r1048bmc_w251_fivekeys.json', '_r1050bmc_w252_fivekeys.json', 2),
    ('n1_w251_results.json', 'n1_w252_results.json', 2),
    ('r1048 bm-c: W251 five-prediction-key machine assertion (prereg sec.5 vs finalize face)',
     'r1050 bm-c: W252 five-prediction-key machine assertion (prereg sec.5 vs finalize face)', 1),
    ('_r1046bmc_w250_fivekeys.py (W250 precedent, one-pass finalize window)',
     '_r1048bmc_w251_fivekeys.py (W251 precedent, one-pass finalize window)', 1),
    # frozen keys: W251 finalize actuals (per W252 prereg sec.5 frozen keys, L44-48)
    ('KEY_MU_MERGED_W250 = -0.09276996        # pre face key (W250 finalize merged mu, K=547,920)',
     'KEY_MU_MERGED_W251 = -0.09274994        # pre face key (W251 finalize merged mu, K=550,120)', 1),
    ('KEY_MU_W250_ONLY = -0.09226', 'KEY_MU_W251_ONLY = -0.08776', 1),
    ('KEY_SIGMA_W250 = 0.2450351', 'KEY_SIGMA_W251 = 0.2450362', 1),
    ('KEY_A_P95_W250 = 0.3235', 'KEY_A_P95_W251 = 0.3153', 1),
    ('KEY_LINE_W250_MERGED = 1.1939           # line_merged@K547,920 (W250 finalize face)',
     'KEY_LINE_W251_MERGED = 1.1941           # line_merged@K550,120 (W251 finalize face)', 1),
    ('KEY_SE_MU_W250 = 0.000331               # se_mu@K547,920 (W250 finalize face)',
     'KEY_SE_MU_W251 = 0.000330               # se_mu@K550,120 (W251 finalize face)', 1),
    ('KEY_KLIFT_W250 = 0.0000                 # K-lift delta (W250 finalize face)',
     'KEY_KLIFT_W251 = 0.0001                 # K-lift delta (W251 finalize face)', 1),
    # result-face field renames (finalize product field faces)
    ('pool["w251_only"]["mu"]', 'pool["w252_only"]["mu"]', 1),
    ('pool["w251_only"]["sigma"]', 'pool["w252_only"]["sigma"]', 1),
    ('pool["se_mu_at_k550120"]', 'pool["se_mu_at_k552320"]', 1),
    ('sl["line_pre_w251"]', 'sl["line_pre_w252"]', 1),
    ('sl["line_merged_550120"]', 'sl["line_merged_552320"]', 1),
    ('"se_mu_k550120": se_mu', '"se_mu_k552320": se_mu', 1),
    # check-name + prose faces
    ('key1_w251_vs_merged_mu_gap', 'key1_w252_vs_merged_mu_gap', 1),
    ('key1b_merged_vs_w250_key', 'key1b_merged_vs_w251_key', 1),
    ('key 1: W251-only mu vs merged mu gap', 'key 1: W252-only mu vs merged mu gap', 1),
    ('w251_mu', 'w252_mu', 3),
    ('merged mu vs W250 pre key', 'merged mu vs W251 pre key', 1),
    ('gap1b = abs(merged_mu - KEY_MU_MERGED_W250)', 'gap1b = abs(merged_mu - KEY_MU_MERGED_W251)', 1),
    ('sigma rel change vs W250 key', 'sigma rel change vs W251 key', 1),
    ('sig_rel = (merged_sigma - KEY_SIGMA_W250) / KEY_SIGMA_W250', 'sig_rel = (merged_sigma - KEY_SIGMA_W251) / KEY_SIGMA_W251', 1),
    ('A-band p95 vs W250 key', 'A-band p95 vs W251 key', 1),
    ('p95d = a_p95 - KEY_A_P95_W250', 'p95d = a_p95 - KEY_A_P95_W251', 1),
    ('se_mu narrowing vs W250 (se_mu chain face, sec.5.4 prose)', 'se_mu narrowing vs W251 (se_mu chain face, sec.5.4 prose)', 1),
    ('checks.append(("key5_se_mu_narrowing", se_mu, KEY_SE_MU_W250, se_mu <= KEY_SE_MU_W250))',
     'checks.append(("key5_se_mu_narrowing", se_mu, KEY_SE_MU_W251, se_mu <= KEY_SE_MU_W251))', 1),
    # receipt faces (post-earlier-legs state: pool["w252_only"] + w252_mu already renamed)
    ('"w251_only": {"mu": w252_mu, "sigma": pool["w252_only"]["sigma"]}',
     '"w252_only": {"mu": w252_mu, "sigma": pool["w252_only"]["sigma"]}', 1),
    ('"wave": 251', '"wave": 252', 1),
    ('"n_eff_held": sl["n_eff_held_equal"], "line_pre_w251": line_pre',
     '"n_eff_held": sl["n_eff_held_equal"], "line_pre_w252": line_pre', 1),
    ('"line_merged_550120": line_merged, "k_lift_delta": klift',
     '"line_merged_552320": line_merged, "k_lift_delta": klift', 1),
    ('"prev_total": 974335, "batch_trials": 2200, "total": 976535,\n                        "exact": (974335 + 2200) == 976535',
     '"prev_total": 976535, "batch_trials": 2200, "total": 978735,\n                        "exact": (976535 + 2200) == 978735', 1),
    # sec5 projection note: W251's note was W252+ projection; W252's is W253+ (staircase-continues face per prereg sec5 item5)
    ('"sec5_item5_projection_note": ("W252+ projection key (A naive 569_501..571_500 CLEAN hops=0 / "\n                                   "B naive 569_701..569_900 CLEAN-at-naive BUT lands INSIDE W252 A "\n                                   "window = staircase re-emergence face; live re-derive governs "\n                                   "r587) = freeze-side face consumed by the W252 freeze party "\n                                   "probe leg4 re-derive (r587 law), NOT a finalize-face key; "\n                                   "recorded here for chain visibility only"),',
     '"sec5_item5_projection_note": ("W253+ projection key (A naive 571_701..573_700 CLEAN-at-naive "\n                                   "BUT start refused at registered W252 B band 571_701..571_900 = "\n                                   "staircase-affects-A 2nd consecutive hop; B own-A reservation cascade "\n                                   "~573_901..574_100-class landing; live re-derive governs r587) = "\n                                   "freeze-side face consumed by the W253 freeze party probe leg4 "\n                                   "re-derive (r587 law), NOT a finalize-face key; recorded here "\n                                   "for chain visibility only"),', 1),
]
for needle, repl, expect in legs:
    n = t.count(needle)
    assert n == expect, "leg count mismatch: %d != %d for needle: %r" % (n, expect, needle[:60])
    t = t.replace(needle, repl)

# MUST_NOT: no stale W250/W251-only faces survive in check semantics
must_not = [
    'KEY_MU_MERGED_W250', 'KEY_SIGMA_W250', 'KEY_A_P95_W250', 'KEY_SE_MU_W250',
    'KEY_KLIFT_W250', 'KEY_MU_W250_ONLY', 'KEY_LINE_W250_MERGED',
    'w251_mu', 'se_mu_at_k550120', 'line_merged_550120', '974335 + 2200',
    '"wave": 251', 'line_pre_w251',
]
for m in must_not:
    assert m not in t, "MUST_NOT survived: %r" % m

io.open(DST, "w", encoding="utf-8", newline="").write(t)
py_compile.compile(DST, doraise=True)
print("DERIVE-OK legs=%d bytes=%d" % (len(legs), len(t.encode("utf-8"))))
