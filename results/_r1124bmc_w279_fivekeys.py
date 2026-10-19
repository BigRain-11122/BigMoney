# -*- coding: utf-8 -*-
"""r1124 bm-c: W279 five-prediction-key machine assertion (prereg sec.5 vs finalize face).

Read-only against results/perpetual_faces/n1_w279_results.json + frozen prereg keys.
W279 prereg froze its sec.5 keys on W278 finalize actuals (live-chain-head basis;
keys machine-read from n1_w278_results.json, r587 never-transcribe law --
constants below are cross-check anchors only, live-extracted from the W278
finalize product this window: mu -0.09278576 / sigma 0.24505494 / a_p95 0.2844 /
line_merged 1.1969 / se_mu 0.000314 / k_lift -0.0002 -- FULL-PRECISION machine-read
per the r1093 fivekeys anchor-precision pit entry, prereg sec.5 8-decimal prose
faces are narrative-only).
Writes results/_r1124bmc_w279_fivekeys.json receipt. Ledger +0, marks +0.
Clone lineage: _r1118bmc_w278_fivekeys.py (canon, prior-wave keys variant).
"""
import json

RES = "results/perpetual_faces/n1_w279_results.json"
PRIOR = "results/perpetual_faces/n1_w278_results.json"
OUT = "results/_r1124bmc_w279_fivekeys.json"

# Frozen prediction keys = W278 finalize actuals (machine-read below; the
# constants are cross-check anchors only, assertion uses the live-read values;
# full-precision anchors machine-read from the W278 finalize product this
# window -- the prereg sec.5 quotes 8-decimal rounded faces, live-read governs
# r587 / r1093 anchor-precision pit law)
KEY_MU_MERGED_W278 = -0.09278575748129675   # W278 finalize merged mu, K=609,520
KEY_SIGMA_W278 = 0.24505493584785207
KEY_A_P95_W278 = 0.2844
KEY_LINE_W278_MERGED = 1.1969
KEY_SE_MU_W278 = 0.000314
KEY_KLIFT_W278 = -0.0002
BAND_MU_GAP = 0.02
BAND_SIGMA_REL = 0.10
BAND_A_P95 = 0.05
BAND_KLIFT = 0.02

w278 = json.load(open(PRIOR, encoding="utf-8"))
p1 = w278["null_pool_cumulative"]; s1 = w278["skill_line_v2_k_lift"]
f1 = w278["families"]["A_random_engine_exit"]
# live machine-read keys (r587 law: never transcribe)
k_mu_merged = p1["merged"]["mu"]
k_sigma = p1["merged"]["sigma"]
k_a_p95 = f1["full_sharpe_p95"]
k_line_merged = s1["line_merged_609520"]
k_se_mu = p1["se_mu_at_k609520"]
k_klift = s1["line_delta_k_lift"]
# cross-check anchors (constant vs live-read equality)
assert abs(k_mu_merged - KEY_MU_MERGED_W278) < 1e-9, (k_mu_merged, KEY_MU_MERGED_W278)
assert abs(k_sigma - KEY_SIGMA_W278) < 1e-9, (k_sigma, KEY_SIGMA_W278)
assert abs(k_a_p95 - KEY_A_P95_W278) < 1e-9, (k_a_p95, KEY_A_P95_W278)
assert abs(k_line_merged - KEY_LINE_W278_MERGED) < 1e-9, (k_line_merged, KEY_LINE_W278_MERGED)
assert abs(k_se_mu - KEY_SE_MU_W278) < 1e-9, (k_se_mu, KEY_SE_MU_W278)
assert abs(k_klift - KEY_KLIFT_W278) < 1e-9, (k_klift, KEY_KLIFT_W278)

d = json.load(open(RES, encoding="utf-8"))
pool = d["null_pool_cumulative"]
sl = d["skill_line_v2_k_lift"]
famA = d["families"]["A_random_engine_exit"]

merged_mu = pool["merged"]["mu"]
merged_sigma = pool["merged"]["sigma"]
merged_k = pool["merged"]["n_values"]
w279_mu = pool["w279_only"]["mu"]
se_mu = pool["se_mu_at_k611720"]
a_p95 = famA["full_sharpe_p95"]
line_pre = sl["line_pre_w279"]
line_merged = sl["line_merged_611720"]
klift = sl["line_delta_k_lift"]

checks = []
# key 1: W279-only mu vs merged mu gap
gap1 = abs(w279_mu - merged_mu)
checks.append(("key1_w279_vs_merged_mu_gap", gap1, BAND_MU_GAP, gap1 < BAND_MU_GAP))
# key 1b: merged mu vs W278 frozen key (prereg keys = prior-wave actuals)
gap1b = abs(merged_mu - k_mu_merged)
checks.append(("key1b_merged_vs_w278_key", gap1b, BAND_MU_GAP, gap1b < BAND_MU_GAP))
# key 2: sigma rel change vs W278 key
sig_rel = (merged_sigma - k_sigma) / k_sigma
checks.append(("key2_sigma_rel", sig_rel, BAND_SIGMA_REL, abs(sig_rel) < BAND_SIGMA_REL))
# key 3: A-band p95 vs W278 key (double-direction band)
p95d = a_p95 - k_a_p95
checks.append(("key3_a_p95_delta", p95d, BAND_A_P95, abs(p95d) < BAND_A_P95))
# key 4: K-lift line move
checks.append(("key4_k_lift_move", klift, BAND_KLIFT, abs(klift) <= BAND_KLIFT))
# key 5: se_mu narrowing vs W278 (se_mu chain face, sec.5 prose)
checks.append(("key5_se_mu_narrowing", se_mu, k_se_mu, se_mu <= k_se_mu))

all_pass = all(c[3] for c in checks)

receipt = {
    "machine": "bm-c",
    "wave": 279,
    "phase": "finalize five-key machine assertion (prereg sec.5 frozen keys vs finalize face)",
    "results_file": RES,
    "keys_anchor": ("W278 finalize actuals machine-read from n1_w278_results.json "
                    "(r587 law) -- W279 prereg froze sec.5 keys on W278 actuals "
                    "(live-chain-head basis; W278 finalize landed pre-draft r1122)"),
    "merged": {"k": merged_k, "mu": merged_mu, "sigma": merged_sigma,
                "se_mu_k611720": se_mu},
    "w279_only": {"mu": w279_mu, "sigma": pool["w279_only"]["sigma"]},
    "skill_line": {"n_eff_held": sl["n_eff_held_equal"], "line_pre_w279": line_pre,
                   "line_merged_611720": line_merged, "k_lift_delta": klift},
    "a_band": {"full_sharpe_p95": a_p95, "full_sharpe_p99": famA["full_sharpe_p99"]},
    "checks": [{"name": c[0], "value": c[1], "band": c[2], "pass": c[3]}
               for c in checks],
    "all_pass": all_pass,
    "ledger_identity": {"prev_total": 1035935, "batch_trials": 2200,
                        "total": 1038135,
                        "exact": (1035935 + 2200) == 1038135},
    "merged_k_identity": {"prev_k": 609520, "batch": 2200, "merged_k": merged_k,
                          "exact": (609520 + 2200) == merged_k},
    "keys_source": "W278 finalize actuals machine-read from n1_w278_results.json (r587 law)",
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
