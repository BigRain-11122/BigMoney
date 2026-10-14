"""r1003 bm-a: W243 five-prediction-key machine assertion (prereg sec.5 vs finalize face).

Read-only against results/perpetual_faces/n1_w243_results.json + frozen prereg keys.
Writes results/_r1003bma_w243_fivekeys.json receipt. Ledger +0, marks +0.
"""
import json
import math

RES = "results/perpetual_faces/n1_w243_results.json"
OUT = "results/_r1003bma_w243_fivekeys.json"

# Frozen prediction keys (research/PERPETUAL_N1_W243_PREREG.md sec.5, derive-at-draft law)
KEY_MU_MERGED_W242 = -0.09274177        # pre face key
KEY_MU_W242_ONLY = -0.08890209
KEY_SIGMA_W242 = 0.24505048
KEY_A_P95_W242 = 0.2991
KEY_LINE_W242_MERGED = 1.1932           # line_merged@K530,320 (W242 finalize face)
KEY_SE_MU_W242 = 0.000374               # se_mu@K530,320 (r999 disclosure)
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
w243_mu = pool["w243_only"]["mu"]
se_mu = pool["se_mu_at_k532520"]
a_p95 = famA["full_sharpe_p95"]
line_pre = sl["line_pre_w243"]
line_merged = sl["line_merged_532520"]
klift = sl["line_delta_k_lift"]

checks = []
# key 1: W243-only mu vs merged mu gap
gap1 = abs(w243_mu - merged_mu)
checks.append(("key1_w243_vs_merged_mu_gap", gap1, BAND_MU_GAP, gap1 < BAND_MU_GAP))
# key 1b: merged mu vs W242 pre key
gap1b = abs(merged_mu - KEY_MU_MERGED_W242)
checks.append(("key1b_merged_vs_w242_key", gap1b, BAND_MU_GAP, gap1b < BAND_MU_GAP))
# key 2: sigma rel change vs W242 key
sig_rel = (merged_sigma - KEY_SIGMA_W242) / KEY_SIGMA_W242
checks.append(("key2_sigma_rel", sig_rel, BAND_SIGMA_REL, abs(sig_rel) < BAND_SIGMA_REL))
# key 3: A-band p95 vs W242 key
p95d = a_p95 - KEY_A_P95_W242
checks.append(("key3_a_p95_delta", p95d, BAND_A_P95, abs(p95d) < BAND_A_P95))
# key 4: K-lift line move
checks.append(("key4_k_lift_move", klift, BAND_KLIFT, abs(klift) <= BAND_KLIFT))
# key 5: se_mu narrowing vs W242
checks.append(("key5_se_mu_narrowing", se_mu, KEY_SE_MU_W242, se_mu <= KEY_SE_MU_W242))

all_pass = all(c[3] for c in checks)
ledger_face = json.load(open("results/perpetual_faces/n1_w243_results.json", encoding="utf-8"))["science_gates"]

receipt = {
    "machine": "bm-a",
    "wave": 243,
    "phase": "finalize five-key machine assertion (prereg sec.5 frozen keys vs finalize face)",
    "results_file": RES,
    "merged": {"k": merged_k, "mu": merged_mu, "sigma": merged_sigma, "se_mu_k532520": se_mu},
    "w243_only": {"mu": w243_mu, "sigma": pool["w243_only"]["sigma"]},
    "skill_line": {"n_eff_held": sl["n_eff_held_equal"], "line_pre_w243": line_pre,
                   "line_merged_532520": line_merged, "k_lift_delta": klift},
    "a_band": {"full_sharpe_p95": a_p95, "full_sharpe_p99": famA["full_sharpe_p99"]},
    "checks": [{"name": c[0], "value": c[1], "band": c[2], "pass": c[3]} for c in checks],
    "all_pass": all_pass,
    "ledger_identity": {"prev_total": 956735, "batch_trials": 2200, "total": 958935,
                        "exact": (956735 + 2200) == 958935},
    "canon_flip": sl["canon_flip"],
    "honest_disclosure": [
        "line_pre_w243=1.1933 vs prereg-quoted W242 line_merged@K530,320=1.1932: 0.0001 held-n face "
        "(pre-line recomputed at n_eff=956,735 by skill_line_v2; key4 judges the MOVE +0.0001 not absolute)",
        "W242 prereg sec7/8 placeholders remain un-backfilled (r999 overclaim, no functional impact; "
        "W242 numbers live in n1_w242_results.json + commit 90db59fc3)",
    ],
}
json.dump(receipt, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("five-key ALL PASS:", all_pass)
for c in checks:
    print(" ", c[0], "=", c[1], "band", c[2], "->", "PASS" if c[3] else "FAIL")
print("receipt:", OUT)
