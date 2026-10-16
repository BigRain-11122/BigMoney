# -*- coding: utf-8 -*-
# r1053 bm-c: derive W253 fivekeys script from committed W252 template
# (_r1050bmc_w252_fivekeys.py) via count-asserted ordered transform.
# E63 canon-clone lineage: zero hand-transcription of faces, every leg
# count-asserted, output py_compiled before write-back. Key values verified
# against frozen W253 prereg sec.5 lines (L45/L47/L48) BEFORE this transform:
# merged mu -0.09273968 / W252-only -0.09018 / sigma 0.2450479 / A p95 0.3199 /
# line_merged@K552,320 1.1943 / se_mu 0.000330 / K-lift 0.0001.
import io
import py_compile

SRC = "results/_r1050bmc_w252_fivekeys.py"
DST = "results/_r1053bmc_w253_fivekeys.py"

t = io.open(SRC, encoding="utf-8").read()
legs = [
    ('_r1050bmc_w252_fivekeys.json', '_r1053bmc_w253_fivekeys.json', 2),
    ('n1_w252_results.json', 'n1_w253_results.json', 2),
    ('r1050 bm-c: W252 five-prediction-key machine assertion (prereg sec.5 vs finalize face)',
     'r1053 bm-c: W253 five-prediction-key machine assertion (prereg sec.5 vs finalize face)', 1),
    ('_r1048bmc_w251_fivekeys.py (W251 precedent, one-pass finalize window)',
     '_r1050bmc_w252_fivekeys.py (W252 precedent, one-pass finalize window)', 1),
    ('# Frozen prediction keys (research/PERPETUAL_N1_W250_PREREG.md sec.5, derive-at-draft law)',
     '# Frozen prediction keys (research/PERPETUAL_N1_W253_PREREG.md sec.5, derive-at-draft law; W252 finalize actuals)', 1),
    ('KEY_MU_MERGED_W251 = -0.09274994        # pre face key (W251 finalize merged mu, K=550,120)',
     'KEY_MU_MERGED_W252 = -0.09273968        # pre face key (W252 finalize merged mu, K=552,320)', 1),
    ('KEY_MU_W251_ONLY = -0.08776', 'KEY_MU_W252_ONLY = -0.09018', 1),
    ('KEY_SIGMA_W251 = 0.2450362', 'KEY_SIGMA_W252 = 0.2450479', 1),
    ('KEY_A_P95_W251 = 0.3153', 'KEY_A_P95_W252 = 0.3199', 1),
    ('KEY_LINE_W251_MERGED = 1.1941           # line_merged@K550,120 (W251 finalize face)',
     'KEY_LINE_W252_MERGED = 1.1943           # line_merged@K552,320 (W252 finalize face)', 1),
    ('KEY_SE_MU_W251 = 0.000330               # se_mu@K550,120 (W251 finalize face)',
     'KEY_SE_MU_W252 = 0.000330               # se_mu@K552,320 (W252 finalize face)', 1),
    ('KEY_KLIFT_W251 = 0.0001                 # K-lift delta (W251 finalize face)',
     'KEY_KLIFT_W252 = 0.0001                 # K-lift delta (W252 finalize face)', 1),
    ('pool["w252_only"]["mu"]', 'pool["w253_only"]["mu"]', 1),
    ('pool["w252_only"]["sigma"]', 'pool["w253_only"]["sigma"]', 1),
    ('pool["se_mu_at_k552320"]', 'pool["se_mu_at_k554520"]', 1),
    ('sl["line_pre_w252"]', 'sl["line_pre_w253"]', 1),
    ('sl["line_merged_552320"]', 'sl["line_merged_554520"]', 1),
    ('"se_mu_k552320": se_mu', '"se_mu_k554520": se_mu', 1),
    ('key1_w252_vs_merged_mu_gap', 'key1_w253_vs_merged_mu_gap', 1),
    ('key1b_merged_vs_w251_key', 'key1b_merged_vs_w252_key', 1),
    ('key 1: W252-only mu vs merged mu gap', 'key 1: W253-only mu vs merged mu gap', 1),
    ('w252_mu', 'w253_mu', 3),
    ('merged mu vs W251 pre key', 'merged mu vs W252 pre key', 1),
    ('gap1b = abs(merged_mu - KEY_MU_MERGED_W251)', 'gap1b = abs(merged_mu - KEY_MU_MERGED_W252)', 1),
    ('sigma rel change vs W251 key', 'sigma rel change vs W252 key', 1),
    ('sig_rel = (merged_sigma - KEY_SIGMA_W251) / KEY_SIGMA_W251', 'sig_rel = (merged_sigma - KEY_SIGMA_W252) / KEY_SIGMA_W252', 1),
    ('A-band p95 vs W251 key', 'A-band p95 vs W252 key', 1),
    ('p95d = a_p95 - KEY_A_P95_W251', 'p95d = a_p95 - KEY_A_P95_W252', 1),
    ('se_mu narrowing vs W251 (se_mu chain face, sec.5.4 prose)', 'se_mu narrowing vs W252 (se_mu chain face, sec.5.4 prose)', 1),
    ('checks.append(("key5_se_mu_narrowing", se_mu, KEY_SE_MU_W251, se_mu <= KEY_SE_MU_W251))',
     'checks.append(("key5_se_mu_narrowing", se_mu, KEY_SE_MU_W252, se_mu <= KEY_SE_MU_W252))', 1),
    ('"w252_only": {"mu": w253_mu, "sigma": pool["w253_only"]["sigma"]}',
     '"w253_only": {"mu": w253_mu, "sigma": pool["w253_only"]["sigma"]}', 1),
    ('"wave": 252', '"wave": 253', 1),
    ('"n_eff_held": sl["n_eff_held_equal"], "line_pre_w252": line_pre',
     '"n_eff_held": sl["n_eff_held_equal"], "line_pre_w253": line_pre', 1),
    ('"line_merged_552320": line_merged, "k_lift_delta": klift',
     '"line_merged_554520": line_merged, "k_lift_delta": klift', 1),
    ('"prev_total": 976535, "batch_trials": 2200, "total": 978735,\n                        "exact": (976535 + 2200) == 978735',
     '"prev_total": 978735, "batch_trials": 2200, "total": 980935,\n                        "exact": (978735 + 2200) == 980935', 1),
    ('"sec5_item5_projection_note": ("W253+ projection key (A naive 571_701..573_700 CLEAN-at-naive "\n                                   "BUT start refused at registered W252 B band 571_701..571_900 = "\n                                   "staircase-affects-A 2nd consecutive hop; B own-A reservation cascade "\n                                   "~573_901..574_100-class landing; live re-derive governs r587) = "\n                                   "freeze-side face consumed by the W253 freeze party probe leg4 "\n                                   "re-derive (r587 law), NOT a finalize-face key; recorded here "\n                                   "for chain visibility only"),',
     '"sec5_item5_projection_note": ("W254+ projection key (A naive 573_901..575_900 CLEAN-at-naive "\n                                   "pre-W253 BUT start refused at registered W253 B band 573_901..574_100 "\n                                   "= staircase-affects-A 3rd consecutive A-hop expected; B own-A "\n                                   "reservation cascade lands inside W254p A naive window; live "\n                                   "re-derive governs r587) = freeze-side face consumed by the W254 "\n                                   "freeze party probe leg4 re-derive (r587 law), NOT a finalize-face "\n                                   "key; recorded here for chain visibility only"),', 1),
]
for needle, repl, expect in legs:
    n = t.count(needle)
    assert n == expect, "leg count mismatch: %d != %d for needle: %r" % (n, expect, needle[:60])
    t = t.replace(needle, repl)

must_not = [
    'KEY_MU_MERGED_W251', 'KEY_SIGMA_W251', 'KEY_A_P95_W251', 'KEY_SE_MU_W251',
    'KEY_KLIFT_W251', 'KEY_MU_W251_ONLY', 'KEY_LINE_W251_MERGED',
    'w252_mu', 'se_mu_at_k552320', 'line_merged_552320', '976535 + 2200',
    '"wave": 252', 'line_pre_w252', '_r1050bmc_w252_fivekeys.json',
]
for m in must_not:
    assert m not in t, "MUST_NOT survived: %r" % m

io.open(DST, "w", encoding="utf-8", newline="").write(t)
py_compile.compile(DST, doraise=True)
print("DERIVE-OK legs=%d bytes=%d" % (len(legs), len(t.encode("utf-8"))))
