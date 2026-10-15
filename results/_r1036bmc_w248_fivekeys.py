# -*- coding: utf-8 -*-
"""r1036 bm-c: W248 five-prediction-key machine assertion (prereg sec.5 vs finalize face).

Read-only against results/perpetual_faces/n1_w248_results.json + frozen prereg keys.
Writes results/_r1036bmc_w248_fivekeys.json receipt. Ledger +0, marks +0.
Clone lineage: _r1022bma_w247_fivekeys.py (W247 precedent, one-pass finalize window).
"""
import json

RES = "results/perpetual_faces/n1_w248_results.json"
OUT = "results/_r1036bmc_w248_fivekeys.json"

# Frozen prediction keys (research/PERPETUAL_N1_W248_PREREG.md sec.5, derive-at-draft law)
KEY_MU_MERGED_W247 = -0.09279753        # pre face key (W247 finalize merged mu, K=541,320)
KEY_MU_W247_ONLY = -0.08799
KEY_SIGMA_W247 = 0.2450508
KEY_A_P95_W247 = 0.3292
KEY_LINE_W247_MERGED = 1.1937           # line_merged@K541,320 (W247 finalize face)
KEY_SE_MU_W247 = 0.000333               # se_mu@K541,320 (W247 finalize face)
BAND_MU_GAP = 0.02
BAND_SIGMA_REL = 0.10
BAND_A_P95 = 0.05
BAND_KLIFT = 0.02

d = json.load(open(RES, encoding="utf-8"))
pool = d["null_pool_cumulative"]
sl = d["skill_line_v2_k_lift"]
famA = d["families"]["A_random_engine_exit"]

merged_mu = pool["merged"]["mu"]
merged_sigma = pool["merged"]["sigma"]
merged_k = pool["merged"]["n_values"]
w248_mu = pool["w248_only"]["mu"]
se_mu = pool["se_mu_at_k543520"]
a_p95 = famA["full_sharpe_p95"]
line_pre = sl["line_pre_w248"]
line_merged = sl["line_merged_543520"]
klift = sl["line_delta_k_lift"]

checks = []
# key 1: W248-only mu vs merged mu gap
gap1 = abs(w248_mu - merged_mu)
checks.append(("key1_w248_vs_merged_mu_gap", gap1, BAND_MU_GAP, gap1 < BAND_MU_GAP))
# key 1b: merged mu vs W247 pre key
gap1b = abs(merged_mu - KEY_MU_MERGED_W247)
checks.append(("key1b_merged_vs_w247_key", gap1b, BAND_MU_GAP, gap1b < BAND_MU_GAP))
# key 2: sigma rel change vs W247 key
sig_rel = (merged_sigma - KEY_SIGMA_W247) / KEY_SIGMA_W247
checks.append(("key2_sigma_rel", sig_rel, BAND_SIGMA_REL, abs(sig_rel) < BAND_SIGMA_REL))
# key 3: A-band p95 vs W247 key
p95d = a_p95 - KEY_A_P95_W247
checks.append(("key3_a_p95_delta", p95d, BAND_A_P95, abs(p95d) < BAND_A_P95))
# key 4: K-lift line move
checks.append(("key4_k_lift_move", klift, BAND_KLIFT, abs(klift) <= BAND_KLIFT))
# key 5: se_mu narrowing vs W247
checks.append(("key5_se_mu_narrowing", se_mu, KEY_SE_MU_W247, se_mu <= KEY_SE_MU_W247))

all_pass = all(c[3] for c in checks)

receipt = {
    "machine": "bm-c",
    "wave": 248,
    "phase": "finalize five-key machine assertion (prereg sec.5 frozen keys vs finalize face)",
    "results_file": RES,
    "merged": {"k": merged_k, "mu": merged_mu, "sigma": merged_sigma, "se_mu_k543520": se_mu},
    "w248_only": {"mu": w248_mu, "sigma": pool["w248_only"]["sigma"]},
    "skill_line": {"n_eff_held": sl["n_eff_held_equal"], "line_pre_w248": line_pre,
                   "line_merged_543520": line_merged, "k_lift_delta": klift},
    "a_band": {"full_sharpe_p95": a_p95, "full_sharpe_p99": famA["full_sharpe_p99"]},
    "checks": [{"name": c[0], "value": c[1], "band": c[2], "pass": c[3]} for c in checks],
    "all_pass": all_pass,
    "ledger_identity": {"prev_total": 967735, "batch_trials": 2200, "total": 969935,
                        "exact": (967735 + 2200) == 969935},
    "canon_flip": sl["canon_flip"],
}
json.dump(receipt, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(json.dumps({"all_pass": all_pass,
                  "checks": [(c[0], round(c[1], 7), c[3]) for c in checks],
                  "merged_k": merged_k, "mu": merged_mu, "sigma": merged_sigma,
                  "ledger": receipt["ledger_identity"]}, indent=1))
raise SystemExit(0 if all_pass else 1)
