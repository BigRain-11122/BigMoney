# -*- coding: utf-8 -*-
"""r1208 bm-c: W314 five-prediction-key machine assertion (prereg sec.5 vs finalize face).

Read-only against results/perpetual_faces/n1_w314_results.json + the W313 product keys.
The W314 prereg sec.5 froze its keys on W313 finalize actuals (live-chain-head basis);
keys are machine-read from n1_w313_results.json below per the r587 never-transcribe law.
Any prose literal that does not reproduce the machine-read W313 actual is DISCLOSED in
prereg_prose_deviations rather than smoothed (r1190/r1191/r1203 precedent).
Writes results/_r1208bmc_w314_fivekeys.json receipt. Ledger +0, marks +0.
Clone lineage: _r1206bmc_w313_fivekeys.py (canon).
"""
import io
import json

RES = "results/perpetual_faces/n1_w314_results.json"
PRIOR = "results/perpetual_faces/n1_w313_results.json"
PREREG = "research/PERPETUAL_N1_W314_PREREG.md"
OUT = "results/_r1208bmc_w314_fivekeys.json"

# Frozen prediction keys = W313 finalize actuals (machine-read below; constants are
# cross-check anchors only, the assertion itself uses the live-read values)
KEY_MU_MERGED_W313 = -0.09282770917089087
KEY_SIGMA_W313 = 0.24516098633452796
KEY_A_P95_W313 = 0.3071
KEY_LINE_W313_MERGED = 1.2008
BAND_MU_GAP = 0.02
BAND_SIGMA_REL = 0.10
BAND_A_P95 = 0.05
BAND_KLIFT = 0.02

w313 = json.load(open(PRIOR, encoding="utf-8"))
p1 = w313["null_pool_cumulative"]
s1 = w313["skill_line_v2_k_lift"]
f1 = w313["families"]["A_random_engine_exit"]
k_mu_merged = p1["merged"]["mu"]
k_sigma = p1["merged"]["sigma"]
k_a_p95 = f1["full_sharpe_p95"]
k_line_merged = s1["line_merged_686520"]
k_se_mu = p1["se_mu_at_k686520"]
k_prior_mu = p1["w313_only"]["mu"]
assert abs(k_mu_merged - KEY_MU_MERGED_W313) < 1e-12, (k_mu_merged, KEY_MU_MERGED_W313)
assert abs(k_sigma - KEY_SIGMA_W313) < 1e-12, (k_sigma, KEY_SIGMA_W313)
assert abs(k_a_p95 - KEY_A_P95_W313) < 1e-9, (k_a_p95, KEY_A_P95_W313)
assert abs(k_line_merged - KEY_LINE_W313_MERGED) < 1e-9, (k_line_merged, KEY_LINE_W313_MERGED)

d = json.load(open(RES, encoding="utf-8"))
pool = d["null_pool_cumulative"]
sl = d["skill_line_v2_k_lift"]
famA = d["families"]["A_random_engine_exit"]
merged_mu = pool["merged"]["mu"]
merged_sigma = pool["merged"]["sigma"]
merged_k = pool["merged"]["n_values"]
w314_mu = pool["w314_only"]["mu"]
se_mu = pool["se_mu_at_k688720"]
a_p95 = famA["full_sharpe_p95"]
line_pre = sl["line_pre_w314"]
line_merged = sl["line_merged_688720"]
klift = sl["line_delta_k_lift"]

# ---- prereg sec.5 prose literals: reproduce-or-disclose (no smoothing) ----
t = io.open(PREREG, encoding="utf-8").read().replace("\u2212", "-")
prose = [
    ("key1_merged_mu_w314", "-0.09282771", k_mu_merged, 1e-8),
    ("key1b_w314_only_mu", "-0.09864764", k_prior_mu, 1e-8),
    ("key2_sigma_w314", "0.24516099", k_sigma, 1e-8),
    ("key3_a_p95_w314", "0.3071", k_a_p95, 1e-9),
    ("key4_k_lift_w314", "+0.0000", klift, 1e-9),
    ("key5_w314_se_mu", "0.000296", k_se_mu, 1e-9),
]
deviations = []
for name, literal, actual, tol in prose:
    present = literal in t
    if present:
        got = float(literal.replace("+", ""))
        if abs(got - float(actual)) > tol:
            deviations.append({
                "key": name, "frozen_prose": literal, "machine_read_actual": actual,
                "note": ("sec.5 prose literal does not reproduce the W313 finalize actual; "
                         "the assertion runs on the machine-read actual (r587) and the "
                         "deviation is disclosed, not smoothed.")})
    else:
        deviations.append({
            "key": name, "frozen_prose": literal, "machine_read_actual": actual,
            "note": "sec.5 prose literal absent from the frozen prereg (absent, not smoothed)"})
assert "1,112,941" in t, 'n_eff held-equal prose literal missing'

checks = []
gap1 = abs(w314_mu - merged_mu)
checks.append(("key1_w314_vs_merged_mu_gap", gap1, BAND_MU_GAP, gap1 < BAND_MU_GAP))
gap1b = abs(merged_mu - k_mu_merged)
checks.append(("key1b_merged_vs_w313_key", gap1b, BAND_MU_GAP, gap1b < BAND_MU_GAP))
sig_rel = (merged_sigma - k_sigma) / k_sigma
checks.append(("key2_sigma_rel", sig_rel, BAND_SIGMA_REL, abs(sig_rel) < BAND_SIGMA_REL))
p95d = a_p95 - k_a_p95
checks.append(("key3_a_p95_delta_actual_anchor", p95d, BAND_A_P95, abs(p95d) < BAND_A_P95))
checks.append(("key4_k_lift_move", klift, BAND_KLIFT, abs(klift) <= BAND_KLIFT))
checks.append(("key5_se_mu_narrowing", se_mu, k_se_mu, se_mu <= k_se_mu))

all_pass = all(c[3] for c in checks)

ledger = d["science_gates"]["ledger"]
# five-key receipt shape: checks are OBJECTS (name/value/band/pass) -- consumers index
# by key name, never by tuple position (r1181 sister pitfall).
receipt = {
    "machine": "bm-c",
    "wave": 314,
    "phase": "finalize five-key machine assertion (prereg sec.5 frozen keys vs finalize face)",
    "results_file": RES,
    "keys_anchor": ("W313 finalize actuals machine-read from n1_w313_results.json "
                    "(r587 law); W314 prereg sec.5 froze its keys on W313 actuals"),
    "prereg_prose_deviations": deviations,
    "merged": {"k": merged_k, "mu": merged_mu, "sigma": merged_sigma,
               "se_mu_k688720": se_mu},
    "w314_only": {"mu": w314_mu, "sigma": pool["w314_only"]["sigma"]},
    "skill_line": {"n_eff_held": sl["n_eff_held_equal"], "line_pre_w314": line_pre,
                   "line_merged_688720": line_merged, "k_lift_delta": klift},
    "a_band": {"full_sharpe_p95": a_p95, "full_sharpe_p99": famA["full_sharpe_p99"]},
    "checks": [{"name": c[0], "value": c[1], "band": c[2], "pass": c[3]}
               for c in checks],
    "all_pass": all_pass,
    "ledger_identity": {"prev_total": ledger["prev_total"],
                        "batch_trials": ledger["batch_trials"],
                        "total": ledger["total"],
                        "exact": (ledger["prev_total"] + ledger["batch_trials"]) == ledger["total"]},
    "merged_k_identity": {"prev_k": 686520, "batch": 2200, "merged_k": merged_k,
                          "exact": (686520 + 2200) == merged_k},
    "keys_source": "W313 finalize actuals machine-read from n1_w313_results.json (r587 law)",
    "canon_flip": sl["canon_flip"],
}
json.dump(receipt, open(OUT, "w", encoding="utf-8", newline="\n"), indent=1,
          ensure_ascii=False)
print(json.dumps({"all_pass": all_pass,
                  "checks": [(c[0], round(c[1], 8) if isinstance(c[1], float) else c[1], c[3])
                             for c in checks],
                  "deviations": deviations,
                  "merged_k": merged_k, "mu": merged_mu, "sigma": merged_sigma,
                  "se_mu": se_mu, "a_p95": a_p95,
                  "ledger": receipt["ledger_identity"],
                  "merged_k_identity": receipt["merged_k_identity"]}, indent=1))
raise SystemExit(0 if all_pass else 1)