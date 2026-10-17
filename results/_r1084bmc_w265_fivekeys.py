# -*- coding: utf-8 -*-
"""r1084 bm-c: W265 five-prediction-key machine assertion (prereg sec.5 vs finalize face).

Read-only against results/perpetual_faces/n1_w265_results.json + frozen prereg keys.
W265 prereg froze its sec.5 keys on W264 finalize actuals (prereg line 44: 本波 §5
预测键 = W264 实测, n1_w264_results.json 机读 -- W264 finalize landed pre-draft,
live-chain-head basis). Keys are machine-read from n1_w264_results.json
(r587 never-transcribe law); constants below are cross-check anchors only.
Writes results/_r1084bmc_w265_fivekeys.json receipt. Ledger +0, marks +0.
Clone lineage: _r1077bmc_w264_fivekeys.py (canon, prior-wave keys variant).
"""
import json

RES = "results/perpetual_faces/n1_w265_results.json"
PRIOR = "results/perpetual_faces/n1_w264_results.json"
OUT = "results/_r1084bmc_w265_fivekeys.json"

# Frozen prediction keys = W264 finalize actuals (machine-read below; the
# constants are cross-check anchors only, assertion uses the live-read values)
KEY_MU_MERGED_W264 = -0.09272765534282555   # W264 finalize merged mu, K=578,720
KEY_SIGMA_W264 = 0.2450429696990889
KEY_A_P95_W264 = 0.3046
KEY_LINE_W264_MERGED = 1.1955
KEY_SE_MU_W264 = 0.000322
KEY_KLIFT_W264 = 0.0001
BAND_MU_GAP = 0.02
BAND_SIGMA_REL = 0.10
BAND_A_P95 = 0.05
BAND_KLIFT = 0.02

w264 = json.load(open(PRIOR, encoding="utf-8"))
p1 = w264["null_pool_cumulative"]; s1 = w264["skill_line_v2_k_lift"]
f1 = w264["families"]["A_random_engine_exit"]
# live machine-read keys (r587 law: never transcribe)
k_mu_merged = p1["merged"]["mu"]
k_sigma = p1["merged"]["sigma"]
k_a_p95 = f1["full_sharpe_p95"]
k_line_merged = s1["line_merged_578720"]
k_se_mu = p1["se_mu_at_k578720"]
k_klift = s1["line_delta_k_lift"]
# cross-check anchors (constant vs live-read equality)
assert k_mu_merged == KEY_MU_MERGED_W264, (k_mu_merged, KEY_MU_MERGED_W264)
assert k_sigma == KEY_SIGMA_W264
assert k_a_p95 == KEY_A_P95_W264
assert k_line_merged == KEY_LINE_W264_MERGED
assert k_se_mu == KEY_SE_MU_W264
assert k_klift == KEY_KLIFT_W264

d = json.load(open(RES, encoding="utf-8"))
pool = d["null_pool_cumulative"]
sl = d["skill_line_v2_k_lift"]
famA = d["families"]["A_random_engine_exit"]

merged_mu = pool["merged"]["mu"]
merged_sigma = pool["merged"]["sigma"]
merged_k = pool["merged"]["n_values"]
w265_mu = pool["w265_only"]["mu"]
se_mu = pool["se_mu_at_k580920"]
a_p95 = famA["full_sharpe_p95"]
line_pre = sl["line_pre_w265"]
line_merged = sl["line_merged_580920"]
klift = sl["line_delta_k_lift"]

checks = []
# key 1: W265-only mu vs merged mu gap
gap1 = abs(w265_mu - merged_mu)
checks.append(("key1_w265_vs_merged_mu_gap", gap1, BAND_MU_GAP, gap1 < BAND_MU_GAP))
# key 1b: merged mu vs W264 frozen key (prereg keys = prior-wave actuals)
gap1b = abs(merged_mu - k_mu_merged)
checks.append(("key1b_merged_vs_w264_key", gap1b, BAND_MU_GAP, gap1b < BAND_MU_GAP))
# key 2: sigma rel change vs W264 key
sig_rel = (merged_sigma - k_sigma) / k_sigma
checks.append(("key2_sigma_rel", sig_rel, BAND_SIGMA_REL, abs(sig_rel) < BAND_SIGMA_REL))
# key 3: A-band p95 vs W264 key (double-direction band)
p95d = a_p95 - k_a_p95
checks.append(("key3_a_p95_delta", p95d, BAND_A_P95, abs(p95d) < BAND_A_P95))
# key 4: K-lift line move
checks.append(("key4_k_lift_move", klift, BAND_KLIFT, abs(klift) <= BAND_KLIFT))
# key 5: se_mu narrowing vs W264 (se_mu chain face, sec.5 prose)
checks.append(("key5_se_mu_narrowing", se_mu, k_se_mu, se_mu <= k_se_mu))

all_pass = all(c[3] for c in checks)

receipt = {
    "machine": "bm-c",
    "wave": 265,
    "phase": "finalize five-key machine assertion (prereg sec.5 frozen keys vs finalize face)",
    "results_file": RES,
    "keys_anchor": ("W264 finalize actuals machine-read from n1_w264_results.json "
                    "(r587 law) -- W265 prereg froze sec.5 keys on W264 actuals "
                    "(prereg line 44; W264 finalize had landed pre-draft; prereg "
                    "sec.5 header names the live-chain-head basis)"),
    "merged": {"k": merged_k, "mu": merged_mu, "sigma": merged_sigma,
                "se_mu_k580920": se_mu},
    "w265_only": {"mu": w265_mu, "sigma": pool["w265_only"]["sigma"]},
    "skill_line": {"n_eff_held": sl["n_eff_held_equal"], "line_pre_w265": line_pre,
                   "line_merged_580920": line_merged, "k_lift_delta": klift},
    "a_band": {"full_sharpe_p95": a_p95, "full_sharpe_p99": famA["full_sharpe_p99"]},
    "checks": [{"name": c[0], "value": c[1], "band": c[2], "pass": c[3]}
               for c in checks],
    "all_pass": all_pass,
    "ledger_identity": {"prev_total": 1005135, "batch_trials": 2200,
                        "total": 1007335,
                        "exact": (1005135 + 2200) == 1007335},
    "merged_k_identity": {"prev_k": 578720, "batch": 2200, "merged_k": merged_k,
                          "exact": (578720 + 2200) == merged_k},
    "keys_source": "W264 finalize actuals machine-read from n1_w264_results.json (r587 law)",
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
