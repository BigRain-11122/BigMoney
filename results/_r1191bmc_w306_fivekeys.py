# -*- coding: utf-8 -*-
"""r1191 bm-c: W306 five-prediction-key machine assertion (prereg sec.5 vs finalize face).

Read-only against results/perpetual_faces/n1_w306_results.json + W305 product keys.
W306 prereg sec.5 froze its keys on W305 finalize actuals (live-chain-head basis);
keys are machine-read from n1_w305_results.json below per the r587 never-transcribe law.
One prose-anchor deviation is disclosed rather than smoothed: sec.5 key 4 plants the
n_eff_held_equal literal as 1,093,141 (the W304 value) while W305 reads 1,095,341.
The assertion runs against the machine-read actuals; the prose literal is disclosed.
Writes results/_r1191bmc_w306_fivekeys.json receipt. Ledger +0, marks +0.
Clone lineage: _r1190bmc_w305_fivekeys.py (canon).
"""
import json

RES = "results/perpetual_faces/n1_w306_results.json"
PRIOR = "results/perpetual_faces/n1_w305_results.json"
OUT = "results/_r1191bmc_w306_fivekeys.json"

# Frozen prediction keys = W305 finalize actuals (machine-read below; constants
# are cross-check anchors only, assertion uses the live-read values)
KEY_MU_MERGED_W305 = -0.09285818378879389
KEY_SIGMA_W305 = 0.2451369647572941
KEY_A_P95_W305 = 0.3009
KEY_LINE_W305_MERGED = 1.1999
KEY_SE_MU_W305 = 0.0003
KEY_N_EFF_PROSE_W305 = 1093141
BAND_MU_GAP = 0.02
BAND_SIGMA_REL = 0.10
BAND_A_P95 = 0.05
BAND_KLIFT = 0.02

w305 = json.load(open(PRIOR, encoding="utf-8"))
p1 = w305["null_pool_cumulative"]
s1 = w305["skill_line_v2_k_lift"]
f1 = w305["families"]["A_random_engine_exit"]
k_mu_merged = p1["merged"]["mu"]
k_sigma = p1["merged"]["sigma"]
k_a_p95 = f1["full_sharpe_p95"]
k_line_merged = s1["line_merged_668920"]
k_se_mu = p1["se_mu_at_k668920"]
assert abs(k_mu_merged - KEY_MU_MERGED_W305) < 1e-12, (k_mu_merged, KEY_MU_MERGED_W305)
assert abs(k_sigma - KEY_SIGMA_W305) < 1e-12, (k_sigma, KEY_SIGMA_W305)
assert abs(k_a_p95 - KEY_A_P95_W305) < 1e-9, (k_a_p95, KEY_A_P95_W305)
assert abs(k_line_merged - KEY_LINE_W305_MERGED) < 1e-9, (k_line_merged, KEY_LINE_W305_MERGED)
assert abs(k_se_mu - KEY_SE_MU_W305) < 1e-12, (k_se_mu, KEY_SE_MU_W305)

d = json.load(open(RES, encoding="utf-8"))
pool = d["null_pool_cumulative"]
sl = d["skill_line_v2_k_lift"]
famA = d["families"]["A_random_engine_exit"]

merged_mu = pool["merged"]["mu"]
merged_sigma = pool["merged"]["sigma"]
merged_k = pool["merged"]["n_values"]
w306_mu = pool["w306_only"]["mu"]
se_mu = pool["se_mu_at_k671120"]
a_p95 = famA["full_sharpe_p95"]
line_pre = sl["line_pre_w306"]
line_merged = sl["line_merged_671120"]
klift = sl["line_delta_k_lift"]

checks = []
gap1 = abs(w306_mu - merged_mu)
checks.append(("key1_w306_vs_merged_mu_gap", gap1, BAND_MU_GAP, gap1 < BAND_MU_GAP))
gap1b = abs(merged_mu - k_mu_merged)
checks.append(("key1b_merged_vs_w305_key", gap1b, BAND_MU_GAP, gap1b < BAND_MU_GAP))
sig_rel = (merged_sigma - k_sigma) / k_sigma
checks.append(("key2_sigma_rel", sig_rel, BAND_SIGMA_REL, abs(sig_rel) < BAND_SIGMA_REL))
p95d = a_p95 - k_a_p95
checks.append(("key3_a_p95_delta_actual_anchor", p95d, BAND_A_P95, abs(p95d) < BAND_A_P95))
checks.append(("key4_k_lift_move", klift, BAND_KLIFT, abs(klift) <= BAND_KLIFT))
checks.append(("key5_se_mu_narrowing", se_mu, k_se_mu, se_mu <= k_se_mu))

all_pass = all(c[3] for c in checks)

ledger = d["science_gates"]["ledger"]
receipt = {
    "machine": "bm-c",
    "wave": 306,
    "phase": "finalize five-key machine assertion (prereg sec.5 frozen keys vs finalize face)",
    "results_file": RES,
    "keys_anchor": ("W305 finalize actuals machine-read from n1_w305_results.json "
                    "(r587 law); W306 prereg sec.5 froze its keys on W305 actuals"),
    "prereg_prose_deviations": [
        {"key": "key4_n_eff_held_equal", "frozen_prose": KEY_N_EFF_PROSE_W305,
         "machine_read_w305": s1["n_eff_held_equal"],
         "note": "prose plants the W304 n_eff literal (1,093,141); W305 actual reads "
                 "1,095,341. Disclosed, not smoothed; the K-lift band is unaffected "
                 "(n_eff is the held-equal carrier, recomputed live every wave)."},
    ],
    "merged": {"k": merged_k, "mu": merged_mu, "sigma": merged_sigma,
               "se_mu_k671120": se_mu},
    "w306_only": {"mu": w306_mu, "sigma": pool["w306_only"]["sigma"]},
    "skill_line": {"n_eff_held": sl["n_eff_held_equal"], "line_pre_w306": line_pre,
                   "line_merged_671120": line_merged, "k_lift_delta": klift},
    "a_band": {"full_sharpe_p95": a_p95, "full_sharpe_p99": famA["full_sharpe_p99"]},
    "checks": [{"name": c[0], "value": c[1], "band": c[2], "pass": c[3]}
               for c in checks],
    "all_pass": all_pass,
    "ledger_identity": {"prev_total": ledger["prev_total"],
                        "batch_trials": ledger["batch_trials"],
                        "total": ledger["total"],
                        "exact": (ledger["prev_total"] + ledger["batch_trials"]) == ledger["total"]},
    "merged_k_identity": {"prev_k": 668920, "batch": 2200, "merged_k": merged_k,
                          "exact": (668920 + 2200) == merged_k},
    "keys_source": "W305 finalize actuals machine-read from n1_w305_results.json (r587 law)",
    "canon_flip": sl["canon_flip"],
}
json.dump(receipt, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(json.dumps({"all_pass": all_pass,
                  "checks": [(c[0], round(c[1], 7) if isinstance(c[1], float) else c[1], c[3])
                             for c in checks],
                  "merged_k": merged_k, "mu": merged_mu, "sigma": merged_sigma,
                  "se_mu": se_mu, "a_p95": a_p95,
                  "ledger": receipt["ledger_identity"],
                  "merged_k_identity": receipt["merged_k_identity"]}, indent=1))
raise SystemExit(0 if all_pass else 1)