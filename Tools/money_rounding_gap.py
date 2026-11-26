"""r2126 (bm-c): why the width-ladder leg can never pass, and how wide the family is.

The smoke leg "the width ladder names why it cannot be quoted, and the buffer line
is tested on a point it never saw" fails every round with

    the published gap is not observed minus predicted

The face publishes three numbers rounded to 3 dp:

    observed_pp = 0.748, predicted_pp = 0.298, gap_pp = 0.449

and `scripts/etf_book_phase_atlas_arms.py` computes them as

    round(obs, 3), round(pred, 3), round(gap, 3)     where gap = obs - pred

i.e. the gap is rounded from the UNROUNDED difference, while the two ends are
rounded separately. Two 3-dp numbers cannot reproduce that to better than one
rounding step (5e-4 + 5e-4 = 1e-3), but the leg demands 1e-9:

    abs(round(obs - pred, 3) - gap_pp) > 1e-9  ->  red

So the leg is red by construction, on a face that is arithmetically honest. This
is the r1813 judgement again ("a frequency sum after rounding is not a
distribution -- the tolerance IS the rounding error"), and the r1789 judgement
about permanent red training readers to ignore red.

This probe is READ-ONLY. It answers three things and writes nothing outside its
own results file:

  1. the exact numbers and the exact 1e-3 step that makes the assertion
     unreachable, plus the counterfactual tolerance that would let it pass;
  2. whether the same shape exists anywhere else in results/ (a published
     "difference" next to the two ends it is a difference of);
  3. which repair is smaller: widen the leg's tolerance to the rounding step, or
     publish the unrounded ends on the face.

Usage: python Tools/money_rounding_gap.py
"""
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "money_rounding_gap_probe.json")

LEG_TOL = 1e-9          # what smoke_test.py demands today
HALF_STEP_3DP = 5e-4    # a 3-dp number is off by at most half a step
STEP_3DP = 1e-3         # two 3-dp numbers differ from their own difference by <= this


def _load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _flatten(obj, prefix=""):
    """Walk a face and return {dotted.key: float} for numeric leaves only."""
    out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.update(_flatten(v, "%s.%s" % (prefix, k) if prefix else str(k)))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out.update(_flatten(v, "%s[%d]" % (prefix, i)))
    elif isinstance(obj, (int, float)) and not isinstance(obj, bool):
        out[prefix] = float(obj)
    return out


def probe_the_leg():
    """Re-derive the leg's own assertion on the face it reads."""
    path = os.path.join(ROOT, "results", "etf_book_buffer_floor_readback.json")
    if not os.path.exists(path):
        return {"status": "FACE_MISSING", "path": path}
    d = _load(path)
    obs = d.get("observed_pp")
    pred = d.get("predicted_pp")
    gap = d.get("gap_pp")
    tol = d.get("tolerance_pp")
    if obs is None or pred is None or gap is None:
        return {"status": "PUBLISHED_TRIPLE_INCOMPLETE",
                "observed_pp": obs, "predicted_pp": pred, "gap_pp": gap}

    obs, pred, gap = float(obs), float(pred), float(gap)
    from_published = round(obs - pred, 3)          # what the leg computes
    deviation = abs(from_published - gap)          # what the leg reds on
    # A face that publishes the unrounded ends can be checked exactly; one that
    # publishes only 3-dp ends cannot. Neither state is a defect in the face.
    reachable_at_leg_tol = deviation <= LEG_TOL
    reachable_at_step = deviation <= STEP_3DP + 1e-12
    return {
        "status": "OK",
        "face": "results/etf_book_buffer_floor_readback.json",
        "verdict_on_face": d.get("verdict"),
        "observed_pp": obs,
        "predicted_pp": pred,
        "gap_pp": gap,
        "tolerance_pp": tol,
        "gap_rebuilt_from_published_ends": from_published,
        "deviation": deviation,
        "rounding_step_3dp": STEP_3DP,
        "half_step_3dp": HALF_STEP_3DP,
        "leg_tolerance": LEG_TOL,
        "passes_at_leg_tolerance": reachable_at_leg_tol,
        "passes_at_rounding_step": reachable_at_step,
        "diagnosis": ("the face rounds both ends and the difference separately; "
                      "two 3-dp ends reproduce that difference to at most one step, "
                      "so a 1e-9 assertion is unreachable on this shape"),
        "counterfactual_tolerance_that_passes": STEP_3DP,
    }


def scan_family():
    """Every face with a published 'difference' next to the two ends it comes from.

    Naming is not standardized, so we look for the two shapes that actually occur:
      <base>gap_pp / <base>delta_pp / <base>diff_pp beside <base>observed_pp + predicted_pp
      sibling pairs named *_a_pp / *_b_pp with *_gap_pp
    A hit is reported only when the difference can be rebuilt from published ends
    and the rebuild does NOT agree to 1e-9 -- i.e. the same trap.
    """
    hits = []
    pairs_checked = 0
    self_face = os.path.abspath(OUT)
    for p in sorted(glob.glob(os.path.join(ROOT, "results", "*.json"))):
        # r2126: this probe's own output lives in results/ and carries the exact
        # shape it hunts for, so an unexcluded scan counts itself as a second hit
        # and the number grows by one every run. A probe that reports a different
        # family size each time cannot be re-run to check anything.
        if os.path.abspath(p) == self_face:
            continue
        try:
            flat = _flatten(_load(p))
        except Exception:
            continue
        keys = set(flat)
        for k in sorted(keys):
            if not (k.endswith("gap_pp") or k.endswith("delta_pp") or k.endswith("diff_pp")):
                continue
            stem = k.rsplit(".", 1)
            prefix = (stem[0] + ".") if len(stem) == 2 else ""
            base = stem[-1][:-6] if stem[-1].endswith("gap_pp") else (
                stem[-1][:-8] if stem[-1].endswith("delta_pp") else stem[-1][:-7])
            candidates = [
                (prefix + base + "observed_pp", prefix + base + "predicted_pp"),
                (prefix + base + "a_pp", prefix + base + "b_pp"),
                (prefix + base + "high_pp", prefix + base + "low_pp"),
            ]
            ends = next(((a, b) for a, b in candidates if a in keys and b in keys), None)
            if not ends:
                continue
            pairs_checked += 1
            a, b = flat[ends[0]], flat[ends[1]]
            published = flat[k]
            rebuilt = round(a - b, 3) if (abs(a) < 1e4 and abs(b) < 1e4) else (a - b)
            dev = abs(rebuilt - published)
            if dev > LEG_TOL:
                hits.append({
                    "face": os.path.relpath(p, ROOT),
                    "difference_key": k,
                    "ends": [ends[0], ends[1]],
                    "ends_values": [a, b],
                    "published_difference": published,
                    "rebuilt_from_published_ends": rebuilt,
                    "deviation": dev,
                    "explained_by_rounding_step": dev <= STEP_3DP + 1e-12,
                })
    return {"pairs_checked": pairs_checked, "hits": hits}


def main():
    leg = probe_the_leg()
    fam = scan_family()
    unexplained = [h for h in fam["hits"] if not h["explained_by_rounding_step"]]

    if leg.get("status") != "OK":
        verdict = "FACE_UNREADABLE"
    elif leg["passes_at_leg_tolerance"]:
        verdict = "LEG_IS_REACHABLE"
    elif leg["passes_at_rounding_step"]:
        verdict = "LEG_UNREACHABLE_BY_ROUNDING_STEP"
    else:
        verdict = "FACE_AND_LEG_BOTH_OFF"

    out = {
        "schema": "r2126-buffer-gap-probe/1",
        "probe": "Tools/money_rounding_gap.py",
        "question": ("the width-ladder leg has been red every round on the buffer "
                     "read-back -- is the face wrong, or is the assertion wider "
                     "than the ruler it is applied to?"),
        "evidence_cutoff": _load(os.path.join(
            ROOT, "results", "etf_book_buffer_floor_readback.json")).get("evidence_cutoff")
        if leg.get("status") == "OK" else None,
        "verdict": verdict,
        "leg": leg,
        "family_scan": fam,
        "unexplained_hits": unexplained,
        "repair_options": [
            {"option": "widen the leg to the rounding step",
             "where": "smoke_test.py :: width ladder leg",
             "change": "1e-9 -> 2 * 5e-4 (the step two 3-dp ends can differ by)",
             "pro": "one constant; keeps the arithmetic contract testable",
             "con": "a face that stops rounding would lose exactness (nothing detects it)"},
            {"option": "publish the unrounded ends",
             "where": "scripts/etf_book_phase_atlas_arms.py :: readback_of",
             "change": "add observed_pp_raw / predicted_pp_raw / gap_pp_raw",
             "pro": "the difference becomes exactly rebuildable; the leg can stay at 1e-9",
             "con": "a second set of numbers on the face that must not be read as the headline"},
        ],
        "recommended": ("both, in this order: publish the raw ends so the arithmetic is "
                        "exactly checkable, then have the leg prefer raw when present and "
                        "fall back to the rounding step when it is not"),
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)

    print("verdict:", verdict)
    if leg.get("status") == "OK":
        print("  observed %.3f  predicted %.3f  published gap %.3f  rebuilt from ends %.3f"
              % (leg["observed_pp"], leg["predicted_pp"], leg["gap_pp"],
                 leg["gap_rebuilt_from_published_ends"]))
        print("  deviation %.6f  leg tolerance %.0e  rounding step %.0e"
              % (leg["deviation"], LEG_TOL, STEP_3DP))
        print("  passes at leg tolerance:", leg["passes_at_leg_tolerance"],
              "| at rounding step:", leg["passes_at_rounding_step"])
    print("  family: %d difference/ends pairs checked, %d hit the same shape, %d unexplained"
          % (fam["pairs_checked"], len(fam["hits"]), len(unexplained)))
    for h in fam["hits"]:
        print("   - %s :: %s dev=%.6f explained_by_step=%s"
              % (h["face"], h["difference_key"], h["deviation"],
                 h["explained_by_rounding_step"]))
    print("  wrote", os.path.relpath(OUT, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
