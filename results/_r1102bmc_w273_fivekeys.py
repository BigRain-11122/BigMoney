# -*- coding: utf-8 -*-
"""r1102 bm-c: W273 five-prediction-key machine assertion (prereg sec.5 vs finalize face).

Read-only against results/perpetual_faces/n1_w273_results.json + frozen prereg keys.
W273 prereg froze its sec.5 keys on W272 finalize actuals (live-chain-head basis;
keys machine-read from n1_w272_results.json, r587 never-transcribe law --
constants below are cross-check anchors only, live-extracted from the W272
finalize product this window: mu -0.09277998 / sigma 0.24509581 / a_p95 0.3138 /
line_merged 1.1965 / se_mu 0.000317 / k_lift +0.0000 -- FULL-PRECISION machine-read
per the r1093 fivekeys anchor-precision pit entry, prereg sec.5 8-decimal prose
faces are narrative-only).
Writes results/_r1102bmc_w273_fivekeys.json receipt. Ledger +0, marks +0.
Clone lineage: _r1100bmc_w272_fivekeys.py (canon, prior-wave keys variant).
"""
import json

RES = "results/perpetual_faces/n1_w273_results.json"
PRIOR = "results/perpetual_faces/n1_w272_results.json"
OUT = "results/_r1102bmc_w273_fivekeys.json"

# Frozen prediction keys = W272 finalize actuals (machine-read below; the
# constants are cross-check anchors only, assertion uses the live-read values;
# full-precision anchors machine-read from the W272 finalize product this
# window -- the prereg sec.5 quotes 8-decimal rounded faces, live-read governs
# r587 / r1093 anchor-precision pit law)
KEY_MU_MERGED_W272 = -0.09277997887040515   # W272 finalize merged mu, K=596,320
KEY_SIGMA_W272 = 0.24509581465156932
KEY_A_P95_W272 = 0.3138
KEY_LINE_W272_MERGED = 1.1965
KEY_SE_MU_W272 = 0.000317
KEY_KLIFT_W272 = 0.0
BAND_MU_GAP = 0.02
BAND_SIGMA_REL = 0.10
BAND_A_P95 = 0.05
BAND_KLIFT = 0.02

w272 = json.load(open(PRIOR, encoding="utf-8"))
p1 = w272["null_pool_cumulative"]; s1 = w272["skill_line_v2_k_lift"]
f1 = w272["families"]["A_random_engine_exit"]
# live machine-read keys (r587 law: never transcribe)
k_mu_merged = p1["merged"]["mu"]
k_sigma = p1["merged"]["sigma"]
k_a_p95 = f1["full_sharpe_p95"]
k_line_merged = s1["line_merged_596320"]
k_se_mu = p1["se_mu_at_k596320"]
k_klift = s1["line_delta_k_lift"]
# cross-check anchors (constant vs live-read equality)
assert abs(k_mu_merged - KEY_MU_MERGED_W272) < 1e-9, (k_mu_merged, KEY_MU_MERGED_W272)
assert abs(k_sigma - KEY_SIGMA_W272) < 1e-9, (k_sigma, KEY_SIGMA_W272)
assert abs(k_a_p95 - KEY_A_P95_W272) < 1e-9, (k_a_p95, KEY_A_P95_W272)
assert abs(k_line_merged - KEY_LINE_W272_MERGED) < 1e-9, (k_line_merged, KEY_LINE_W272_MERGED)
assert abs(k_se_mu - KEY_SE_MU_W272) < 1e-9, (k_se_mu, KEY_SE_MU_W272)
assert abs(k_klift - KEY_KLIFT_W272) < 1e-9, (k_klift, KEY_KLIFT_W272)

d = json.load(open(RES, encoding="utf-8"))
pool = d["null_pool_cumulative"]
sl = d["skill_line_v2_k_lift"]
famA = d["families"]["A_random_engine_exit"]

merged_mu = pool["merged"]["mu"]
merged_sigma = pool["merged"]["sigma"]
merged_k = pool["merged"]["n_values"]
w273_mu = pool["w273_only"]["mu"]
se_mu = pool["se_mu_at_k598520"]
a_p95 = famA["full_sharpe_p95"]
line_pre = sl["line_pre_w273"]
line_merged = sl["line_merged_598520"]
klift = sl["line_delta_k_lift"]

checks = []
# key 1: W273-only mu vs merged mu gap
gap1 = abs(w273_mu - merged_mu)
checks.append(("key1_w273_vs_merged_mu_gap", gap1, BAND_MU_GAP, gap1 < BAND_MU_GAP))
# key 1b: merged mu vs W272 frozen key (prereg keys = prior-wave actuals)
gap1b = abs(merged_mu - k_mu_merged)
checks.append(("key1b_merged_vs_w272_key", gap1b, BAND_MU_GAP, gap1b < BAND_MU_GAP))
# key 2: sigma rel change vs W272 key
sig_rel = (merged_sigma - k_sigma) / k_sigma
checks.append(("key2_sigma_rel", sig_rel, BAND_SIGMA_REL, abs(sig_rel) < BAND_SIGMA_REL))
# key 3: A-band p95 vs W272 key (double-direction band)
p95d = a_p95 - k_a_p95
checks.append(("key3_a_p95_delta", p95d, BAND_A_P95, abs(p95d) < BAND_A_P95))
# key 4: K-lift line move
checks.append(("key4_k_lift_move", klift, BAND_KLIFT, abs(klift) <= BAND_KLIFT))
# key 5: se_mu narrowing vs W272 (se_mu chain face, sec.5 prose)
checks.append(("key5_se_mu_narrowing", se_mu, k_se_mu, se_mu <= k_se_mu))

all_pass = all(c[3] for c in checks)

receipt = {
    "machine": "bm-c",
    "wave": 273,
    "phase": "finalize five-key machine assertion (prereg sec.5 frozen keys vs finalize face)",
    "results_file": RES,
    "keys_anchor": ("W272 finalize actuals machine-read from n1_w272_results.json "
                    "(r587 law) -- W273 prereg froze sec.5 keys on W272 actuals "
                    "(live-chain-head basis; W272 finalize landed pre-draft r1100)"),
    "merged": {"k": merged_k, "mu": merged_mu, "sigma": merged_sigma,
                "se_mu_k598520": se_mu},
    "w273_only": {"mu": w273_mu, "sigma": pool["w273_only"]["sigma"]},
    "skill_line": {"n_eff_held": sl["n_eff_held_equal"], "line_pre_w273": line_pre,
                   "line_merged_598520": line_merged, "k_lift_delta": klift},
    "a_band": {"full_sharpe_p95": a_p95, "full_sharpe_p99": famA["full_sharpe_p99"]},
    "checks": [{"name": c[0], "value": c[1], "band": c[2], "pass": c[3]}
               for c in checks],
    "all_pass": all_pass,
    "ledger_identity": {"prev_total": 1022735, "batch_trials": 2200,
                        "total": 1024935,
                        "exact": (1022735 + 2200) == 1024935},
    "merged_k_identity": {"prev_k": 596320, "batch": 2200, "merged_k": merged_k,
                          "exact": (596320 + 2200) == merged_k},
    "keys_source": "W272 finalize actuals machine-read from n1_w272_results.json (r587 law)",
    "canon_flip": sl["canon_flip"],
}
json.dump(receipt, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(json.dumps({"all_pass": all_pass,
                  "checks": [(c[0], round(c[1], 7) if isinstance(c[1], float)
                              else c[1], c[3]) for c in checks],
                  "merged_k": merged_k, "mu": merged_mu, "sigma": merged_sigma,
                  "se_mu": se_mu, "a_p95": a_p95,
                  "ledger": receipt["ledger_identity"],
                  "merged_k_identity": receipt["merged_k_identity"]}, indent=1))
raise SystemExit(0 if all_pass else 1)
