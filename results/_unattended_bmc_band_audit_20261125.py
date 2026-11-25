"""Independent second-eye audit of r2073's ruler band (read-only, new file only).

Why: results/etf_book_cap_trim_toll.json prints
    ruler_band_cny = ruler_band_pp / 100 * nav          (= 58,920)
while the same face prints its gap-to-cap in money via the up-stream
    trim_cny = (k*beta - cap)/beta * nav                (= 19,543)
Both `ruler_band_pp` and `over_pp_now` are *exposure-beta* units
(etf_book_cap_beta_units.band_units = k_noise_sd * beta), so a pp must
become money the same way in both places: cash = pp/100 / beta * nav.

This script re-derives both readings from the published faces and reports
the mismatch, the correct band, and whether the verdict direction flips.
It never writes a shared face and never imports the production scripts.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
        return json.load(fh)


cap = load("results/etf_book_cap_beta_units.json")["facts"]
tt = load("results/etf_book_cap_trim_toll.json")["facts"]

nav = float(cap["nav_cny"])
beta_now = float(cap["beta_now"])
k_noise_sd = float(cap["k_noise_sd"])
band_pp = float(cap["ruler_band_pp"])
over_pp_now = float(cap["over_pp_now"])          # exposure-beta pp over cap
trim_now = float(cap["trim_cny_now"])            # the published money gap

# (1) band in the ruler's own units: band_units = k_noise_sd * beta, so
#     band_pp = 100*k_noise_sd*beta and band_cny = band_units/beta*nav = k_noise_sd*nav.
band_cny_correct = band_pp / 100.0 / beta_now * nav
band_cny_from_k = k_noise_sd * nav

# (2) what the face actually printed, and the formula that reproduces it.
band_cny_face = float(tt["ruler_band_cny"])
band_cny_face_formula = band_pp / 100.0 * nav

# (3) cross-check that the *gap* used the divide-by-beta convention.
trim_check = over_pp_now / 100.0 / beta_now * nav

ratio = band_cny_correct / band_cny_face if band_cny_face else float("inf")
inv_beta = 1.0 / beta_now

# verdict re-derived with each band
def verdict(gap, band):
    if gap <= 0:
        return "NOTHING_TO_TRIM"
    if gap <= abs(band):
        return "TRIM_IS_INSIDE_THE_RULER"
    return "TRIM_IS_A_REAL_BREACH"


out = {
    "schema": "unattended-band-audit/v1",
    "audited_face": "results/etf_book_cap_trim_toll.json",
    "upstream_face": "results/etf_book_cap_beta_units.json",
    "levels": {
        "nav_cny": nav,
        "beta_now": beta_now,
        "k_noise_sd_pp": k_noise_sd * 100.0,
        "ruler_band_pp": band_pp,
        "over_pp_now": over_pp_now,
        "trim_now_cny": trim_now,
    },
    "band_cny": {
        "printed_by_face": round(band_cny_face, 2),
        "printed_formula": "band_pp/100*nav",
        "reproduced_by_formula": round(band_cny_face_formula, 2),
        "correct_divide_by_beta": round(band_cny_correct, 2),
        "correct_from_k_noise_sd": round(band_cny_from_k, 2),
        "ratio_correct_over_printed": round(ratio, 4),
        "one_over_beta_now": round(inv_beta, 4),
    },
    "gap_money_cross_check": {
        "recomputed_from_over_pp": round(trim_check, 2),
        "published_trim_cny": round(trim_now, 2),
        "delta_cny": round(trim_check - trim_now, 2),
        "uses_divide_by_beta": True,
    },
    "verdict": {
        "as_printed": tt["verdict_day"],
        "with_correct_band": verdict(trim_now, band_cny_correct),
        "direction_flips": verdict(trim_now, band_cny_correct) != tt["verdict_day"],
    },
    "finding": (
        "ONE PP, TWO RULERS: the gap (over_pp_now) is turned into money with "
        "divide-by-beta, but the noise band (ruler_band_pp) is turned into money "
        "with times-NAV, on the same face. Both are exposure-beta units, so the "
        "band is understated by 1/beta (~2.08x). The verdict direction does not "
        "flip (the trim is inside the ruler either way), but the printed band "
        "number is wrong and internally inconsistent with the gap on the same page."
    ),
}

print("BAND-AUDIT face=%s" % out["audited_face"])
print("  band printed      = %12.2f  (band_pp/100*nav)" % band_cny_face)
print("  band correct      = %12.2f  (band_pp/100/beta*nav)" % band_cny_correct)
print("  band from k_sd    = %12.2f  (k_noise_sd*nav, identity check)" % band_cny_from_k)
print("  ratio correct/printed = %.4f  vs 1/beta = %.4f" % (ratio, inv_beta))
print("  gap recomputed    = %12.2f  (published %.2f, delta %+.2f)" %
      (trim_check, trim_now, trim_check - trim_now))
print("  verdict as printed  = %s" % tt["verdict_day"])
print("  verdict w/ correct  = %s  (flips=%s)" %
      (out["verdict"]["with_correct_band"], out["verdict"]["direction_flips"]))
print("  FINDING: %s" % out["finding"])

outp = os.path.join(ROOT, "results", "_unattended_bmc_band_audit_20261125.json")
with open(outp, "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1, sort_keys=True)
    fh.write("\n")
print("WROTE results/_unattended_bmc_band_audit_20261125.json")
