# -*- coding: utf-8 -*-
"""r1048 bm-c: W251 five-prediction-key machine assertion (prereg sec.5 vs finalize face).

Read-only against results/perpetual_faces/n1_w251_results.json + frozen prereg keys.
Writes results/_r1048bmc_w251_fivekeys.json receipt. Ledger +0, marks +0.
Clone lineage: _r1046bmc_w250_fivekeys.py (W250 precedent, one-pass finalize window).
"""
import json

RES = "results/perpetual_faces/n1_w251_results.json"
OUT = "results/_r1048bmc_w251_fivekeys.json"

# Frozen prediction keys (research/PERPETUAL_N1_W250_PREREG.md sec.5, derive-at-draft law)
KEY_MU_MERGED_W250 = -0.09276996        # pre face key (W250 finalize merged mu, K=547,920)
KEY_MU_W250_ONLY = -0.09226
KEY_SIGMA_W250 = 0.2450351
KEY_A_P95_W250 = 0.3235
KEY_LINE_W250_MERGED = 1.1939           # line_merged@K547,920 (W250 finalize face)
KEY_SE_MU_W250 = 0.000331               # se_mu@K547,920 (W250 finalize face)
KEY_KLIFT_W250 = 0.0000                 # K-lift delta (W250 finalize face)
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
w251_mu = pool["w251_only"]["mu"]
se_mu = pool["se_mu_at_k550120"]
a_p95 = famA["full_sharpe_p95"]
line_pre = sl["line_pre_w251"]
line_merged = sl["line_merged_550120"]
klift = sl["line_delta_k_lift"]

checks = []
# key 1: W251-only mu vs merged mu gap
gap1 = abs(w251_mu - merged_mu)
checks.append(("key1_w251_vs_merged_mu_gap", gap1, BAND_MU_GAP, gap1 < BAND_MU_GAP))
# key 1b: merged mu vs W250 pre key
gap1b = abs(merged_mu - KEY_MU_MERGED_W250)
checks.append(("key1b_merged_vs_w250_key", gap1b, BAND_MU_GAP, gap1b < BAND_MU_GAP))
# key 2: sigma rel change vs W250 key
sig_rel = (merged_sigma - KEY_SIGMA_W250) / KEY_SIGMA_W250
checks.append(("key2_sigma_rel", sig_rel, BAND_SIGMA_REL, abs(sig_rel) < BAND_SIGMA_REL))
# key 3: A-band p95 vs W250 key
p95d = a_p95 - KEY_A_P95_W250
checks.append(("key3_a_p95_delta", p95d, BAND_A_P95, abs(p95d) < BAND_A_P95))
# key 4: K-lift line move
checks.append(("key4_k_lift_move", klift, BAND_KLIFT, abs(klift) <= BAND_KLIFT))
# key 5: se_mu narrowing vs W250 (se_mu chain face, sec.5.4 prose)
checks.append(("key5_se_mu_narrowing", se_mu, KEY_SE_MU_W250, se_mu <= KEY_SE_MU_W250))

all_pass = all(c[3] for c in checks)

receipt = {
    "machine": "bm-c",
    "wave": 251,
    "phase": "finalize five-key machine assertion (prereg sec.5 frozen keys vs finalize face)",
    "results_file": RES,
    "merged": {"k": merged_k, "mu": merged_mu, "sigma": merged_sigma, "se_mu_k550120": se_mu},
    "w251_only": {"mu": w251_mu, "sigma": pool["w251_only"]["sigma"]},
    "skill_line": {"n_eff_held": sl["n_eff_held_equal"], "line_pre_w251": line_pre,
                   "line_merged_550120": line_merged, "k_lift_delta": klift},
    "a_band": {"full_sharpe_p95": a_p95, "full_sharpe_p99": famA["full_sharpe_p99"]},
    "checks": [{"name": c[0], "value": c[1], "band": c[2], "pass": c[3]} for c in checks],
    "all_pass": all_pass,
    "ledger_identity": {"prev_total": 974335, "batch_trials": 2200, "total": 976535,
                        "exact": (974335 + 2200) == 976535},
    "sec5_item5_projection_note": ("W252+ projection key (A naive 569_501..571_500 CLEAN hops=0 / "
                                   "B naive 569_701..569_900 CLEAN-at-naive BUT lands INSIDE W252 A "
                                   "window = staircase re-emergence face; live re-derive governs "
                                   "r587) = freeze-side face consumed by the W252 freeze party "
                                   "probe leg4 re-derive (r587 law), NOT a finalize-face key; "
                                   "recorded here for chain visibility only"),
    "canon_flip": sl["canon_flip"],
}
json.dump(receipt, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(json.dumps({"all_pass": all_pass,
                  "checks": [(c[0], round(c[1], 7), c[3]) for c in checks],
                  "merged_k": merged_k, "mu": merged_mu, "sigma": merged_sigma,
                  "ledger": receipt["ledger_identity"]}, indent=1))
raise SystemExit(0 if all_pass else 1)
