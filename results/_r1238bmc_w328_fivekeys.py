# -*- coding: utf-8 -*-
"""r1238 bm-c: W328 five-prediction-key machine assertion (prereg sec.5 vs finalize face).

Read-only against results/perpetual_faces/n1_w328_results.json + the W327 product keys.
W328 prereg sec.5 froze its keys on W327 finalize actuals; keys are machine-read from
n1_w327_results.json here per the r587 never-transcribe law. Any prose literal that does
not reproduce the machine-read W327 actual is DISCLOSED in prereg_prose_deviations rather
than smoothed (r1190/r1191/r1203/r1208/r1210/r1236 precedent).
Writes results/_r1238bmc_w328_fivekeys.json receipt. Ledger +0, marks +0.
Clone lineage: _r1236bmc_w327_fivekeys.py (canon). All wave numerals written explicitly
(r1168/r1171/r1184/r1208 family).
"""
import io
import json

WAVE = 328
RES = "results/perpetual_faces/n1_w328_results.json"
PRIOR = "results/perpetual_faces/n1_w327_results.json"
PREREG = "research/PERPETUAL_N1_W328_PREREG.md"
OUT = "results/_r1238bmc_w328_fivekeys.json"

# Frozen prediction keys = W327 finalize actuals (cross-check anchors only; the
# assertion itself uses the live-read values)
KEY_MU_MERGED_W327 = -0.09287455291919924
KEY_SIGMA_W327 = 0.2452184696100091
KEY_A_P95_W327 = 0.2977
KEY_LINE_W327_MERGED = 1.2023
KEY_SE_MU_W327 = 0.00029
KEY_W327_ONLY_MU = -0.09439881818181818
KEY_KLIFT_W327 = 0.0
BAND_MU_GAP = 0.02
BAND_SIGMA_REL = 0.10
BAND_A_P95 = 0.05
BAND_KLIFT = 0.02
PRIOR_K = 717320
PRIOR_LEDGER = 1143741

w327 = json.load(open(PRIOR, encoding="utf-8"))
p1 = w327["null_pool_cumulative"]
s1 = w327["skill_line_v2_k_lift"]
f1 = w327["families"]["A_random_engine_exit"]
k_mu_merged = p1["merged"]["mu"]
k_sigma = p1["merged"]["sigma"]
k_a_p95 = f1["full_sharpe_p95"]
k_line_merged = s1["line_merged_717320"]
k_se_mu = p1["se_mu_at_k717320"]
k_prior_mu = p1["w327_only"]["mu"]
k_klift = s1["line_delta_k_lift"]
assert abs(k_mu_merged - KEY_MU_MERGED_W327) < 1e-9, (k_mu_merged, KEY_MU_MERGED_W327)
assert abs(k_sigma - KEY_SIGMA_W327) < 1e-9, (k_sigma, KEY_SIGMA_W327)
assert abs(k_a_p95 - KEY_A_P95_W327) < 1e-9, (k_a_p95, KEY_A_P95_W327)
assert abs(k_line_merged - KEY_LINE_W327_MERGED) < 1e-9, (k_line_merged, KEY_LINE_W327_MERGED)
assert abs(k_se_mu - KEY_SE_MU_W327) < 1e-9, (k_se_mu, KEY_SE_MU_W327)
assert abs(k_prior_mu - KEY_W327_ONLY_MU) < 1e-9, (k_prior_mu, KEY_W327_ONLY_MU)
assert abs(k_klift - KEY_KLIFT_W327) < 1e-9, (k_klift, KEY_KLIFT_W327)

d = json.load(open(RES, encoding="utf-8"))
pool = d["null_pool_cumulative"]
sl = d["skill_line_v2_k_lift"]
famA = d["families"]["A_random_engine_exit"]
merged_mu = pool["merged"]["mu"]
merged_sigma = pool["merged"]["sigma"]
merged_k = pool["merged"]["n_values"]
w_only_mu = pool["w328_only"]["mu"]
se_mu_key = "se_mu_at_k%d" % merged_k
se_mu = pool[se_mu_key]
a_p95 = famA["full_sharpe_p95"]
line_pre = sl["line_pre_w328"]
line_merged = sl["line_merged_%d" % merged_k]
klift = sl["line_delta_k_lift"]

# ---- prereg sec.5 prose literals: reproduce-or-disclose (no smoothing) ----
t = io.open(PREREG, encoding="utf-8").read().replace("\u2212", "-")
prose = [
    ("key1_merged_mu_w327", "-0.09287455", k_mu_merged, 1e-8),
    ("key1b_w327_only_mu", "-0.09439882", k_prior_mu, 1e-8),
    ("key2_sigma_w327", "0.24521847", k_sigma, 1e-8),
    ("key3_a_p95_w327", "0.2977", k_a_p95, 1e-9),
    ("key4_k_lift_w327", "+0.0000", k_klift, 1e-9),
    ("key5_w327_se_mu", "0.000290", k_se_mu, 1e-9),
    ("key4_line_merged_w327", "1.2023", k_line_merged, 1e-9),
]
deviations = []
for name, literal, actual, tol in prose:
    present = literal in t
    if present:
        got = float(literal.replace("+", ""))
        if abs(got - float(actual)) > tol:
            deviations.append({
                "key": name, "frozen_prose": literal, "machine_read_actual": actual,
                "note": ("sec.5 prose literal does not reproduce the W327 finalize actual; "
                         "the assertion runs on the machine-read actual (r587) and the "
                         "deviation is disclosed, not smoothed.")})
    else:
        deviations.append({
            "key": name, "frozen_prose": literal, "machine_read_actual": actual,
            "note": "sec.5 prose literal absent from the frozen prereg (absent, not smoothed)"})
held_literal = "1,143,741"
held_actual = sl["n_eff_held_equal"]
if held_literal not in t:
    deviations.append({
        "key": "n_eff_held_prose", "frozen_prose": held_literal,
        "machine_read_actual": held_actual,
        "note": ("sec.5 n_eff_held prose literal absent; finalize face holds the true "
                 "n_eff_held_equal -- disclosed, not smoothed")})
elif int(held_literal.replace(",", "")) != int(held_actual):
    # r1238: second live instance of the r1236 E96 class (present is not reproduction).
    # The W328 prereg carries the WAVE'S OWN ledger total (1,143,741) where the held n_eff
    # must be the PRIOR wave's total (1,141,541 = W326); the freeze window read the fresh
    # finalize number instead of the held number. Disclosed, never smoothed.
    deviations.append({
        "key": "n_eff_held_prose", "frozen_prose": held_literal,
        "machine_read_actual": held_actual,
        "note": ("sec.5 n_eff_held prose literal is the CURRENT wave's ledger total "
                 "(1,143,741) while the finalize face holds 1,141,541 (W326's total = the "
                 "n_eff this wave's line is held at); the freeze window transcribed the "
                 "prior wave's own finalize total into the held slot. Present-but-wrong is "
                 "a deviation, not a match (r1236 E96 class, second live instance).")})

checks = []
gap1 = abs(w_only_mu - merged_mu)
checks.append(("key1_w328_vs_merged_mu_gap", gap1, BAND_MU_GAP, gap1 < BAND_MU_GAP))
gap1b = abs(merged_mu - k_mu_merged)
checks.append(("key1b_merged_vs_w327_key", gap1b, BAND_MU_GAP, gap1b < BAND_MU_GAP))
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
    "wave": WAVE,
    "phase": "finalize five-key machine assertion (prereg sec.5 frozen keys vs finalize face)",
    "results_file": RES,
    "keys_anchor": ("W327 finalize actuals machine-read from n1_w327_results.json "
                    "(r587 law); W328 prereg sec.5 froze its keys on W327 actuals"),
    "prereg_prose_deviations": deviations,
    "merged": {"k": merged_k, "mu": merged_mu, "sigma": merged_sigma,
               se_mu_key: se_mu},
    "w328_only": {"mu": w_only_mu, "sigma": pool["w328_only"]["sigma"]},
    "skill_line": {"n_eff_held": held_actual, "line_pre_w328": line_pre,
                   "line_merged_%d" % merged_k: line_merged, "k_lift_delta": klift},
    "a_band": {"full_sharpe_p95": a_p95, "full_sharpe_p99": famA["full_sharpe_p99"]},
    "checks": [{"name": c[0], "value": c[1], "band": c[2], "pass": c[3]}
               for c in checks],
    "all_pass": all_pass,
    "ledger_identity": {"prev_total": ledger["prev_total"],
                        "batch_trials": ledger["batch_trials"],
                        "total": ledger["total"],
                        "exact": (ledger["prev_total"] + ledger["batch_trials"]) == ledger["total"]},
    "merged_k_identity": {"prev_k": PRIOR_K, "batch": 2200, "merged_k": merged_k,
                          "exact": (PRIOR_K + 2200) == merged_k},
    "keys_source": "W327 finalize actuals machine-read from n1_w327_results.json (r587 law)",
    "canon_flip": sl["canon_flip"],
}
json.dump(receipt, open(OUT, "w", encoding="utf-8", newline="\n"), indent=1,
          ensure_ascii=False)
print(json.dumps({"all_pass": all_pass,
                  "checks": [(c[0], round(c[1], 8) if isinstance(c[1], float) else c[1], c[3])
                             for c in checks],
                  "deviations": [x["key"] for x in deviations],
                  "merged_k": merged_k, "mu": merged_mu, "sigma": merged_sigma,
                  "se_mu": se_mu, "a_p95": a_p95,
                  "ledger": receipt["ledger_identity"],
                  "merged_k_identity": receipt["merged_k_identity"]}, indent=1))
raise SystemExit(0 if all_pass else 1)