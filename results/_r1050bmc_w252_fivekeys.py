# -*- coding: utf-8 -*-
"""r1050 bm-c: W252 five-prediction-key machine assertion (prereg sec.5 vs finalize face).

Read-only against results/perpetual_faces/n1_w252_results.json + frozen prereg keys.
Writes results/_r1050bmc_w252_fivekeys.json receipt. Ledger +0, marks +0.
Clone lineage: _r1048bmc_w251_fivekeys.py (W251 precedent, one-pass finalize window).
"""
import json

RES = "results/perpetual_faces/n1_w252_results.json"
OUT = "results/_r1050bmc_w252_fivekeys.json"

# Frozen prediction keys (research/PERPETUAL_N1_W250_PREREG.md sec.5, derive-at-draft law)
KEY_MU_MERGED_W251 = -0.09274994        # pre face key (W251 finalize merged mu, K=550,120)
KEY_MU_W251_ONLY = -0.08776
KEY_SIGMA_W251 = 0.2450362
KEY_A_P95_W251 = 0.3153
KEY_LINE_W251_MERGED = 1.1941           # line_merged@K550,120 (W251 finalize face)
KEY_SE_MU_W251 = 0.000330               # se_mu@K550,120 (W251 finalize face)
KEY_KLIFT_W251 = 0.0001                 # K-lift delta (W251 finalize face)
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
w252_mu = pool["w252_only"]["mu"]
se_mu = pool["se_mu_at_k552320"]
a_p95 = famA["full_sharpe_p95"]
line_pre = sl["line_pre_w252"]
line_merged = sl["line_merged_552320"]
klift = sl["line_delta_k_lift"]

checks = []
# key 1: W252-only mu vs merged mu gap
gap1 = abs(w252_mu - merged_mu)
checks.append(("key1_w252_vs_merged_mu_gap", gap1, BAND_MU_GAP, gap1 < BAND_MU_GAP))
# key 1b: merged mu vs W251 pre key
gap1b = abs(merged_mu - KEY_MU_MERGED_W251)
checks.append(("key1b_merged_vs_w251_key", gap1b, BAND_MU_GAP, gap1b < BAND_MU_GAP))
# key 2: sigma rel change vs W251 key
sig_rel = (merged_sigma - KEY_SIGMA_W251) / KEY_SIGMA_W251
checks.append(("key2_sigma_rel", sig_rel, BAND_SIGMA_REL, abs(sig_rel) < BAND_SIGMA_REL))
# key 3: A-band p95 vs W251 key
p95d = a_p95 - KEY_A_P95_W251
checks.append(("key3_a_p95_delta", p95d, BAND_A_P95, abs(p95d) < BAND_A_P95))
# key 4: K-lift line move
checks.append(("key4_k_lift_move", klift, BAND_KLIFT, abs(klift) <= BAND_KLIFT))
# key 5: se_mu narrowing vs W251 (se_mu chain face, sec.5.4 prose)
checks.append(("key5_se_mu_narrowing", se_mu, KEY_SE_MU_W251, se_mu <= KEY_SE_MU_W251))

all_pass = all(c[3] for c in checks)

receipt = {
    "machine": "bm-c",
    "wave": 252,
    "phase": "finalize five-key machine assertion (prereg sec.5 frozen keys vs finalize face)",
    "results_file": RES,
    "merged": {"k": merged_k, "mu": merged_mu, "sigma": merged_sigma, "se_mu_k552320": se_mu},
    "w252_only": {"mu": w252_mu, "sigma": pool["w252_only"]["sigma"]},
    "skill_line": {"n_eff_held": sl["n_eff_held_equal"], "line_pre_w252": line_pre,
                   "line_merged_552320": line_merged, "k_lift_delta": klift},
    "a_band": {"full_sharpe_p95": a_p95, "full_sharpe_p99": famA["full_sharpe_p99"]},
    "checks": [{"name": c[0], "value": c[1], "band": c[2], "pass": c[3]} for c in checks],
    "all_pass": all_pass,
    "ledger_identity": {"prev_total": 976535, "batch_trials": 2200, "total": 978735,
                        "exact": (976535 + 2200) == 978735},
    "sec5_item5_projection_note": ("W253+ projection key (A naive 571_701..573_700 CLEAN-at-naive "
                                   "BUT start refused at registered W252 B band 571_701..571_900 = "
                                   "staircase-affects-A 2nd consecutive hop; B own-A reservation cascade "
                                   "~573_901..574_100-class landing; live re-derive governs r587) = "
                                   "freeze-side face consumed by the W253 freeze party probe leg4 "
                                   "re-derive (r587 law), NOT a finalize-face key; recorded here "
                                   "for chain visibility only"),
    "canon_flip": sl["canon_flip"],
}
json.dump(receipt, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(json.dumps({"all_pass": all_pass,
                  "checks": [(c[0], round(c[1], 7), c[3]) for c in checks],
                  "merged_k": merged_k, "mu": merged_mu, "sigma": merged_sigma,
                  "ledger": receipt["ledger_identity"]}, indent=1))
raise SystemExit(0 if all_pass else 1)
