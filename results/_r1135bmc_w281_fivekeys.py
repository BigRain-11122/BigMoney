# -*- coding: utf-8 -*-
"""r1135 bm-c: W281 five-prediction-key machine assertion (prereg sec.5 vs finalize face).

Read-only against results/perpetual_faces/n1_w281_results.json + frozen prereg keys.
W281 prereg froze its sec.5 keys on W280 finalize actuals (live-chain-head basis;
keys machine-read from n1_w280_results.json, r587 never-transcribe law --
constants below are cross-check anchors only, live-extracted from the W280
finalize product this window, FULL-PRECISION per the r1093 anchor-precision pit
entry; prereg sec.5 8-decimal prose faces are narrative-only).
Writes results/_r1135bmc_w281_fivekeys.json receipt. Ledger +0, marks +0.
Clone lineage: _r1132bmc_w280_fivekeys.py (canon, prior-wave keys variant).
"""
import json

RES = "results/perpetual_faces/n1_w281_results.json"
PRIOR = "results/perpetual_faces/n1_w280_results.json"
OUT = "results/_r1135bmc_w281_fivekeys.json"

# Frozen prediction keys = W280 finalize actuals (machine-read below; the
# constants are cross-check anchors only, assertion uses the live-read values)
KEY_MU_MERGED_W280 = -0.09284668784206411
KEY_SIGMA_W280 = 0.24507970539684695
KEY_A_P95_W280 = 0.3294
KEY_LINE_W280_MERGED = 1.1972
KEY_SE_MU_W280 = 0.000313
KEY_KLIFT_W280 = 0.0001
BAND_MU_GAP = 0.02
BAND_SIGMA_REL = 0.10
BAND_A_P95 = 0.05
BAND_KLIFT = 0.02

w280 = json.load(open(PRIOR, encoding="utf-8"))
p1 = w280["null_pool_cumulative"]; s1 = w280["skill_line_v2_k_lift"]
f1 = w280["families"]["A_random_engine_exit"]
# live machine-read keys (r587 law: never transcribe)
k_mu_merged = p1["merged"]["mu"]
k_sigma = p1["merged"]["sigma"]
k_a_p95 = f1["full_sharpe_p95"]
k_line_merged = s1["line_merged_613920"]
k_se_mu = p1["se_mu_at_k613920"]
k_klift = s1["line_delta_k_lift"]
# cross-check anchors (constant vs live-read equality)
assert abs(k_mu_merged - KEY_MU_MERGED_W280) < 1e-9, (k_mu_merged, KEY_MU_MERGED_W280)
assert abs(k_sigma - KEY_SIGMA_W280) < 1e-9, (k_sigma, KEY_SIGMA_W280)
assert abs(k_a_p95 - KEY_A_P95_W280) < 1e-9, (k_a_p95, KEY_A_P95_W280)
assert abs(k_line_merged - KEY_LINE_W280_MERGED) < 1e-9, (k_line_merged, KEY_LINE_W280_MERGED)
assert abs(k_se_mu - KEY_SE_MU_W280) < 1e-9, (k_se_mu, KEY_SE_MU_W280)
assert abs(k_klift - KEY_KLIFT_W280) < 1e-9, (k_klift, KEY_KLIFT_W280)

d = json.load(open(RES, encoding="utf-8"))
pool = d["null_pool_cumulative"]
sl = d["skill_line_v2_k_lift"]
famA = d["families"]["A_random_engine_exit"]

merged_mu = pool["merged"]["mu"]
merged_sigma = pool["merged"]["sigma"]
merged_k = pool["merged"]["n_values"]
w281_mu = pool["w281_only"]["mu"]
se_mu = pool["se_mu_at_k616120"]
a_p95 = famA["full_sharpe_p95"]
line_pre = sl["line_pre_w281"]
line_merged = sl["line_merged_616120"]
klift = sl["line_delta_k_lift"]

checks = []
# key 1: W281-only mu vs merged mu gap
gap1 = abs(w281_mu - merged_mu)
checks.append(("key1_w281_vs_merged_mu_gap", gap1, BAND_MU_GAP, gap1 < BAND_MU_GAP))
# key 1b: merged mu vs W280 frozen key (prereg keys = prior-wave actuals)
gap1b = abs(merged_mu - k_mu_merged)
checks.append(("key1b_merged_vs_w280_key", gap1b, BAND_MU_GAP, gap1b < BAND_MU_GAP))
# key 2: sigma rel change vs W280 key
sig_rel = (merged_sigma - k_sigma) / k_sigma
checks.append(("key2_sigma_rel", sig_rel, BAND_SIGMA_REL, abs(sig_rel) < BAND_SIGMA_REL))
# key 3: A-band p95 vs W280 key (double-direction band)
p95d = a_p95 - k_a_p95
checks.append(("key3_a_p95_delta", p95d, BAND_A_P95, abs(p95d) < BAND_A_P95))
# key 4: K-lift line move
checks.append(("key4_k_lift_move", klift, BAND_KLIFT, abs(klift) <= BAND_KLIFT))
# key 5: se_mu narrowing vs W280 (se_mu chain face, sec.5 prose)
checks.append(("key5_se_mu_narrowing", se_mu, k_se_mu, se_mu <= k_se_mu))

all_pass = all(c[3] for c in checks)

receipt = {
    "machine": "bm-c",
    "wave": 281,
    "phase": "finalize five-key machine assertion (prereg sec.5 frozen keys vs finalize face)",
    "results_file": RES,
    "keys_anchor": ("W280 finalize actuals machine-read from n1_w280_results.json "
                    "(r587 law) -- W281 prereg froze sec.5 keys on W280 actuals "
                    "(live-chain-head basis; W280 finalize landed pre-draft r1131)"),
    "merged": {"k": merged_k, "mu": merged_mu, "sigma": merged_sigma,
                "se_mu_k616120": se_mu},
    "w281_only": {"mu": w281_mu, "sigma": pool["w281_only"]["sigma"]},
    "skill_line": {"n_eff_held": sl["n_eff_held_equal"], "line_pre_w281": line_pre,
                   "line_merged_616120": line_merged, "k_lift_delta": klift},
    "a_band": {"full_sharpe_p95": a_p95, "full_sharpe_p99": famA["full_sharpe_p99"]},
    "checks": [{"name": c[0], "value": c[1], "band": c[2], "pass": c[3]}
               for c in checks],
    "all_pass": all_pass,
    "ledger_identity": {"prev_total": 1040335, "batch_trials": 2200,
                        "total": 1042535,
                        "exact": (1040335 + 2200) == 1042535},
    "merged_k_identity": {"prev_k": 613920, "batch": 2200, "merged_k": merged_k,
                          "exact": (613920 + 2200) == merged_k},
    "keys_source": "W280 finalize actuals machine-read from n1_w280_results.json (r587 law)",
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