# -*- coding: utf-8 -*-
"""r1068 bm-c: W262 five-prediction-key machine assertion (prereg sec.5 vs finalize face).

Read-only against results/perpetual_faces/n1_w262_results.json + frozen prereg keys
(W261 finalize actuals, machine-read from n1_w261_results.json this window per r587
never-transcribe law; values cross-checked against the W262 prereg sec.5 carried faces).
Writes results/_r1068bmc_w262_fivekeys.json receipt. Ledger +0, marks +0.
Clone lineage: _r1064bmc_w259_fivekeys.py (canon) <- _r1062bmc_w258_fivekeys.py.
"""
import json

RES = "results/perpetual_faces/n1_w262_results.json"
PRIOR = "results/perpetual_faces/n1_w261_results.json"
OUT = "results/_r1068bmc_w262_fivekeys.json"

# Frozen prediction keys = W261 finalize actuals (machine-read below; the constants are
# cross-check anchors only, assertion uses the live-read values)
KEY_MU_MERGED_W261 = -0.09273606970565615   # W261 finalize merged mu, K=572,120
KEY_SIGMA_W261 = 0.24503320458531583
KEY_A_P95_W261 = 0.2994
KEY_LINE_W261_MERGED = 1.1951
KEY_SE_MU_W261 = 0.000324
KEY_KLIFT_W261 = -0.0001
BAND_MU_GAP = 0.02
BAND_SIGMA_REL = 0.10
BAND_A_P95 = 0.05
BAND_KLIFT = 0.02

w261 = json.load(open(PRIOR, encoding="utf-8"))
p1 = w261["null_pool_cumulative"]; s1 = w261["skill_line_v2_k_lift"]
f1 = w261["families"]["A_random_engine_exit"]
# live machine-read keys (r587 law: never transcribe)
k_mu_merged = p1["merged"]["mu"]
k_sigma = p1["merged"]["sigma"]
k_a_p95 = f1["full_sharpe_p95"]
k_line_merged = s1["line_merged_572120"]
k_se_mu = p1["se_mu_at_k572120"]
k_klift = s1["line_delta_k_lift"]
# cross-check anchors (constant vs live-read equality)
assert k_mu_merged == KEY_MU_MERGED_W261, (k_mu_merged, KEY_MU_MERGED_W261)
assert k_sigma == KEY_SIGMA_W261
assert k_a_p95 == KEY_A_P95_W261
assert k_line_merged == KEY_LINE_W261_MERGED
assert k_se_mu == KEY_SE_MU_W261
assert k_klift == KEY_KLIFT_W261

d = json.load(open(RES, encoding="utf-8"))
pool = d["null_pool_cumulative"]
sl = d["skill_line_v2_k_lift"]
famA = d["families"]["A_random_engine_exit"]

merged_mu = pool["merged"]["mu"]
merged_sigma = pool["merged"]["sigma"]
merged_k = pool["merged"]["n_values"]
w262_mu = pool["w262_only"]["mu"]
se_mu = pool["se_mu_at_k574320"]
a_p95 = famA["full_sharpe_p95"]
line_pre = sl["line_pre_w262"]
line_merged = sl["line_merged_574320"]
klift = sl["line_delta_k_lift"]

checks = []
# key 1: W262-only mu vs merged mu gap
gap1 = abs(w262_mu - merged_mu)
checks.append(("key1_w262_vs_merged_mu_gap", gap1, BAND_MU_GAP, gap1 < BAND_MU_GAP))
# key 1b: merged mu vs W261 pre key
gap1b = abs(merged_mu - k_mu_merged)
checks.append(("key1b_merged_vs_w261_key", gap1b, BAND_MU_GAP, gap1b < BAND_MU_GAP))
# key 2: sigma rel change vs W261 key
sig_rel = (merged_sigma - k_sigma) / k_sigma
checks.append(("key2_sigma_rel", sig_rel, BAND_SIGMA_REL, abs(sig_rel) < BAND_SIGMA_REL))
# key 3: A-band p95 vs W261 key (double-direction band)
p95d = a_p95 - k_a_p95
checks.append(("key3_a_p95_delta", p95d, BAND_A_P95, abs(p95d) < BAND_A_P95))
# key 4: K-lift line move
checks.append(("key4_k_lift_move", klift, BAND_KLIFT, abs(klift) <= BAND_KLIFT))
# key 5: se_mu narrowing vs W261 (se_mu chain face, sec.5.4 prose)
checks.append(("key5_se_mu_narrowing", se_mu, k_se_mu, se_mu <= k_se_mu))

all_pass = all(c[3] for c in checks)

receipt = {
    "machine": "bm-c",
    "wave": 262,
    "phase": "finalize five-key machine assertion (prereg sec.5 frozen keys vs finalize face)",
    "results_file": RES,
    "merged": {"k": merged_k, "mu": merged_mu, "sigma": merged_sigma, "se_mu_k574320": se_mu},
    "w262_only": {"mu": w262_mu, "sigma": pool["w262_only"]["sigma"]},
    "skill_line": {"n_eff_held": sl["n_eff_held_equal"], "line_pre_w262": line_pre,
                   "line_merged_574320": line_merged, "k_lift_delta": klift},
    "a_band": {"full_sharpe_p95": a_p95, "full_sharpe_p99": famA["full_sharpe_p99"]},
    "checks": [{"name": c[0], "value": c[1], "band": c[2], "pass": c[3]} for c in checks],
    "all_pass": all_pass,
    "ledger_identity": {"prev_total": 998535, "batch_trials": 2200, "total": 1000735,
                        "exact": (998535 + 2200) == 1000735},
    "merged_k_identity": {"prev_k": 572120, "batch": 2200, "merged_k": merged_k,
                          "exact": (572120 + 2200) == merged_k},
    "keys_source": "W261 finalize actuals machine-read from n1_w261_results.json (r587 law)",
    "canon_flip": sl["canon_flip"],
}
json.dump(receipt, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(json.dumps({"all_pass": all_pass,
                  "checks": [(c[0], round(c[1], 7), c[3]) for c in checks],
                  "merged_k": merged_k, "mu": merged_mu, "sigma": merged_sigma,
                  "se_mu": se_mu, "a_p95": a_p95,
                  "ledger": receipt["ledger_identity"],
                  "merged_k_identity": receipt["merged_k_identity"]}, indent=1))
raise SystemExit(0 if all_pass else 1)
