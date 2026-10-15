# -*- coding: utf-8 -*-
"""r1017 bm-a: W246 five-prediction-key machine assertion (prereg sec.5 vs finalize face).

Read-only against results/perpetual_faces/n1_w246_results.json + frozen prereg keys.
Writes results/_r1017bma_w246_fivekeys.json receipt. Ledger +0, marks +0.
Clone lineage: _r1015bma_w245_fivekeys.py (W245 precedent, one-pass finalize window).
"""
import json

RES = "results/perpetual_faces/n1_w246_results.json"
OUT = "results/_r1017bma_w246_fivekeys.json"

# Frozen prediction keys (research/PERPETUAL_N1_W246_PREREG.md sec.5, derive-at-draft law)
KEY_MU_MERGED_W245 = -0.09281866        # pre face key (W245 finalize merged mu, K=536,920)
KEY_MU_W245_ONLY = -0.09621
KEY_SIGMA_W245 = 0.2450379
KEY_A_P95_W245 = 0.3020
KEY_LINE_W245_MERGED = 1.1934           # line_merged@K536,920 (W245 finalize face)
KEY_SE_MU_W245 = 0.000334               # se_mu@K536,920 (W245 finalize face)
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
w246_mu = pool["w246_only"]["mu"]
se_mu = pool["se_mu_at_k539120"]
a_p95 = famA["full_sharpe_p95"]
line_pre = sl["line_pre_w246"]
line_merged = sl["line_merged_539120"]
klift = sl["line_delta_k_lift"]

checks = []
# key 1: W246-only mu vs merged mu gap
gap1 = abs(w246_mu - merged_mu)
checks.append(("key1_w246_vs_merged_mu_gap", gap1, BAND_MU_GAP, gap1 < BAND_MU_GAP))
# key 1b: merged mu vs W245 pre key
gap1b = abs(merged_mu - KEY_MU_MERGED_W245)
checks.append(("key1b_merged_vs_w245_key", gap1b, BAND_MU_GAP, gap1b < BAND_MU_GAP))
# key 2: sigma rel change vs W245 key
sig_rel = (merged_sigma - KEY_SIGMA_W245) / KEY_SIGMA_W245
checks.append(("key2_sigma_rel", sig_rel, BAND_SIGMA_REL, abs(sig_rel) < BAND_SIGMA_REL))
# key 3: A-band p95 vs W245 key
p95d = a_p95 - KEY_A_P95_W245
checks.append(("key3_a_p95_delta", p95d, BAND_A_P95, abs(p95d) < BAND_A_P95))
# key 4: K-lift line move
checks.append(("key4_k_lift_move", klift, BAND_KLIFT, abs(klift) <= BAND_KLIFT))
# key 5: se_mu narrowing vs W245
checks.append(("key5_se_mu_narrowing", se_mu, KEY_SE_MU_W245, se_mu <= KEY_SE_MU_W245))

all_pass = all(c[3] for c in checks)

receipt = {
    "machine": "bm-a",
    "wave": 246,
    "phase": "finalize five-key machine assertion (prereg sec.5 frozen keys vs finalize face)",
    "results_file": RES,
    "merged": {"k": merged_k, "mu": merged_mu, "sigma": merged_sigma, "se_mu_k539120": se_mu},
    "w246_only": {"mu": w246_mu, "sigma": pool["w246_only"]["sigma"]},
    "skill_line": {"n_eff_held": sl["n_eff_held_equal"], "line_pre_w246": line_pre,
                   "line_merged_539120": line_merged, "k_lift_delta": klift},
    "a_band": {"full_sharpe_p95": a_p95, "full_sharpe_p99": famA["full_sharpe_p99"]},
    "checks": [{"name": c[0], "value": c[1], "band": c[2], "pass": c[3]} for c in checks],
    "all_pass": all_pass,
    "ledger_identity": {"prev_total": 963335, "batch_trials": 2200, "total": 965535,
                        "exact": (963335 + 2200) == 965535},
    "canon_flip": sl["canon_flip"],
}
json.dump(receipt, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(json.dumps({"all_pass": all_pass,
                  "checks": [(c[0], round(c[1], 7), c[3]) for c in checks],
                  "merged_k": merged_k, "mu": merged_mu, "sigma": merged_sigma,
                  "ledger": receipt["ledger_identity"]}, indent=1))
raise SystemExit(0 if all_pass else 1)
