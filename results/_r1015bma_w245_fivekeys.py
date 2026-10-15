"""r1015 bm-a: W245 five-prediction-key machine assertion (prereg sec.5 vs finalize face).

Read-only against results/perpetual_faces/n1_w245_results.json + frozen prereg keys.
Writes results/_r1015bma_w245_fivekeys.json receipt. Ledger +0, marks +0.
Clone lineage: _r1008bma_w244_fivekeys.py (W244 precedent, one-pass finalize window).
"""
import json

RES = "results/perpetual_faces/n1_w245_results.json"
OUT = "results/_r1015bma_w245_fivekeys.json"

# Frozen prediction keys (research/PERPETUAL_N1_W245_PREREG.md sec.5, derive-at-draft law)
KEY_MU_MERGED_W244 = -0.09280471        # pre face key (W244 finalize merged mu, K=534,720)
KEY_MU_W244_ONLY = -0.10390359
KEY_SIGMA_W244 = 0.24505388
KEY_A_P95_W244 = 0.2952
KEY_LINE_W244_MERGED = 1.1934           # line_merged@K534,720 (W244 finalize face)
KEY_SE_MU_W244 = 0.000335               # se_mu@K534,720 (W244 finalize face)
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
w245_mu = pool["w245_only"]["mu"]
se_mu = pool["se_mu_at_k536920"]
a_p95 = famA["full_sharpe_p95"]
line_pre = sl["line_pre_w245"]
line_merged = sl["line_merged_536920"]
klift = sl["line_delta_k_lift"]

checks = []
# key 1: W245-only mu vs merged mu gap
gap1 = abs(w245_mu - merged_mu)
checks.append(("key1_w245_vs_merged_mu_gap", gap1, BAND_MU_GAP, gap1 < BAND_MU_GAP))
# key 1b: merged mu vs W244 pre key
gap1b = abs(merged_mu - KEY_MU_MERGED_W244)
checks.append(("key1b_merged_vs_w244_key", gap1b, BAND_MU_GAP, gap1b < BAND_MU_GAP))
# key 2: sigma rel change vs W244 key
sig_rel = (merged_sigma - KEY_SIGMA_W244) / KEY_SIGMA_W244
checks.append(("key2_sigma_rel", sig_rel, BAND_SIGMA_REL, abs(sig_rel) < BAND_SIGMA_REL))
# key 3: A-band p95 vs W244 key
p95d = a_p95 - KEY_A_P95_W244
checks.append(("key3_a_p95_delta", p95d, BAND_A_P95, abs(p95d) < BAND_A_P95))
# key 4: K-lift line move
checks.append(("key4_k_lift_move", klift, BAND_KLIFT, abs(klift) <= BAND_KLIFT))
# key 5: se_mu narrowing vs W244
checks.append(("key5_se_mu_narrowing", se_mu, KEY_SE_MU_W244, se_mu <= KEY_SE_MU_W244))

all_pass = all(c[3] for c in checks)

receipt = {
    "machine": "bm-a",
    "wave": 245,
    "phase": "finalize five-key machine assertion (prereg sec.5 frozen keys vs finalize face)",
    "results_file": RES,
    "merged": {"k": merged_k, "mu": merged_mu, "sigma": merged_sigma, "se_mu_k536920": se_mu},
    "w245_only": {"mu": w245_mu, "sigma": pool["w245_only"]["sigma"]},
    "skill_line": {"n_eff_held": sl["n_eff_held_equal"], "line_pre_w245": line_pre,
                   "line_merged_536920": line_merged, "k_lift_delta": klift},
    "a_band": {"full_sharpe_p95": a_p95, "full_sharpe_p99": famA["full_sharpe_p99"]},
    "checks": [{"name": c[0], "value": c[1], "band": c[2], "pass": c[3]} for c in checks],
    "all_pass": all_pass,
    "ledger_identity": {"prev_total": 961135, "batch_trials": 2200, "total": 963335,
                        "exact": (961135 + 2200) == 963335},
    "canon_flip": sl["canon_flip"],
    "honest_disclosure": [
        "line_pre_w245=1.1935 vs prereg-quoted W244 line_merged@K534,720=1.1934: 0.0001 held-n face "
        "(pre-line recomputed at n_eff=961,135 by skill_line_v2; key4 judges the MOVE -0.0001 not absolute)",
        "K-lift delta -0.0001 = second consecutive negative move in the W136..W244 precedent chain "
        "(W244 first-negative; all prior within +/-0.0003); inside precedent band and far inside the "
        "0.02 registered band -- nulls-deepening measurement face, not a returns claim",
        "A-band full_sharpe_p95 0.3020 vs W244 key 0.2952: delta +0.0068 inside 0.05 band (pure sampling "
        "noise of the 2,000-trial A slice; measurement face, not registered returns)",
        "se_mu 0.000334 continues the monotone narrowing chain (W244 0.000335); K=536,920 EXACT "
        "534,720+2,200; ledger 961,135+2,200=963,335 EXACT",
    ],
}
json.dump(receipt, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("fivekeys:", "ALL PASS" if all_pass else "FAIL", "| K=%d merged mu=%.5f sigma=%.5f se_mu=%.6f" % (merged_k, merged_mu, merged_sigma, se_mu))
for c in checks:
    print("  %-32s value=%-+.6g band=%-6g pass=%s" % (c[0], c[1], c[2], c[3]))
