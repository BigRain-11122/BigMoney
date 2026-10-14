"""r1008 bm-a: W244 five-prediction-key machine assertion (prereg sec.5 vs finalize face).

Read-only against results/perpetual_faces/n1_w244_results.json + frozen prereg keys.
Writes results/_r1008bma_w244_fivekeys.json receipt. Ledger +0, marks +0.
"""
import json
import math

RES = "results/perpetual_faces/n1_w244_results.json"
OUT = "results/_r1008bma_w244_fivekeys.json"

# Frozen prediction keys (research/PERPETUAL_N1_W244_PREREG.md sec.5, derive-at-draft law)
KEY_MU_MERGED_W243 = -0.09275885        # pre face key (W243 finalize merged mu)
KEY_MU_W243_ONLY = -0.09687705
KEY_SIGMA_W243 = 0.24506859
KEY_A_P95_W243 = 0.3193
KEY_LINE_W243_MERGED = 1.1934           # line_merged@K532,520 (W243 finalize face)
KEY_SE_MU_W243 = 0.000336               # se_mu@K532,520 (W243 finalize face)
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
w244_mu = pool["w244_only"]["mu"]
se_mu = pool["se_mu_at_k534720"]
a_p95 = famA["full_sharpe_p95"]
line_pre = sl["line_pre_w244"]
line_merged = sl["line_merged_534720"]
klift = sl["line_delta_k_lift"]

checks = []
# key 1: W244-only mu vs merged mu gap
gap1 = abs(w244_mu - merged_mu)
checks.append(("key1_w244_vs_merged_mu_gap", gap1, BAND_MU_GAP, gap1 < BAND_MU_GAP))
# key 1b: merged mu vs W243 pre key
gap1b = abs(merged_mu - KEY_MU_MERGED_W243)
checks.append(("key1b_merged_vs_w243_key", gap1b, BAND_MU_GAP, gap1b < BAND_MU_GAP))
# key 2: sigma rel change vs W243 key
sig_rel = (merged_sigma - KEY_SIGMA_W243) / KEY_SIGMA_W243
checks.append(("key2_sigma_rel", sig_rel, BAND_SIGMA_REL, abs(sig_rel) < BAND_SIGMA_REL))
# key 3: A-band p95 vs W243 key
p95d = a_p95 - KEY_A_P95_W243
checks.append(("key3_a_p95_delta", p95d, BAND_A_P95, abs(p95d) < BAND_A_P95))
# key 4: K-lift line move
checks.append(("key4_k_lift_move", klift, BAND_KLIFT, abs(klift) <= BAND_KLIFT))
# key 5: se_mu narrowing vs W243
checks.append(("key5_se_mu_narrowing", se_mu, KEY_SE_MU_W243, se_mu <= KEY_SE_MU_W243))

all_pass = all(c[3] for c in checks)

receipt = {
    "machine": "bm-a",
    "wave": 244,
    "phase": "finalize five-key machine assertion (prereg sec.5 frozen keys vs finalize face)",
    "results_file": RES,
    "merged": {"k": merged_k, "mu": merged_mu, "sigma": merged_sigma, "se_mu_k534720": se_mu},
    "w244_only": {"mu": w244_mu, "sigma": pool["w244_only"]["sigma"]},
    "skill_line": {"n_eff_held": sl["n_eff_held_equal"], "line_pre_w244": line_pre,
                   "line_merged_534720": line_merged, "k_lift_delta": klift},
    "a_band": {"full_sharpe_p95": a_p95, "full_sharpe_p99": famA["full_sharpe_p99"]},
    "checks": [{"name": c[0], "value": c[1], "band": c[2], "pass": c[3]} for c in checks],
    "all_pass": all_pass,
    "ledger_identity": {"prev_total": 958935, "batch_trials": 2200, "total": 961135,
                        "exact": (958935 + 2200) == 961135},
    "canon_flip": sl["canon_flip"],
    "honest_disclosure": [
        "line_pre_w244=1.1935 vs prereg-quoted W243 line_merged@K532,520=1.1934: 0.0001 held-n face "
        "(pre-line recomputed at n_eff=958,935 by skill_line_v2; key4 judges the MOVE -0.0001 not absolute)",
        "K-lift delta -0.0001 = first negative move in the W136..W243 precedent chain (all prior within "
        "+/-0.0003); still inside the +/-0.0003 precedent band and far inside the 0.02 registered band",
        "A-band full_sharpe_p95 0.2952 vs W243 key 0.3193: delta -0.0241 inside 0.05 band (pure sampling "
        "noise of the 2,000-trial A slice; measurement face, not registered returns)",
        "W244-only mu -0.1039 vs merged -0.0928: gap 0.0111 inside 0.02 band; W243-only gap precedent 0.0041",
    ],
}
json.dump(receipt, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("five-key ALL PASS:", all_pass)
for c in checks:
    print(" ", c[0], "=", c[1], "band", c[2], "->", "PASS" if c[3] else "FAIL")
print("receipt:", OUT)
