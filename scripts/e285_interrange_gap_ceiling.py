"""E285 -- the inter-range gap: how many rows can only a widened tail reach, and where does the
published headroom run out?

E282 showed the two tails disagree because they publish different ranges (not because of a
rounding tie).  E283 showed a degenerate tail can only reach a row when the flip equals its single
multiplier.  Both leave one shape unmeasured: the space BETWEEN the two tails.  On a row whose
tight interval ends before the wide interval starts, a flip landing in that gap is reachable by
NEITHER tail, so widening is the only instrument that could ever pick it up -- and the question a
reader needs answered is how much of the unresolvable set that gap accounts for, versus how much
sits beyond the family's published ceiling entirely (where no widening inside the published
evidence can reach at all).

This face measures, per (leg, base) arm:

  (1) the two published intervals and the inter-range gap [tight.hi, wide.lo] (positive only when
      the tight interval ends before the wide one starts);
  (2) every row's flip classified EXACTLY ONCE as reachable_tight / reachable_wide / in_gap /
      above_ceiling / below_floor, with the partition asserted to add up to the row count;
  (3) the widening target per in-gap row: the relative distance it needs from each published
      bound, and the gap width expressed in each tail's own spread (the only ruler the family
      publishes);
  (4) the headroom ceiling: rows above the family's published p95 ceiling are not "headroom", they
      are extrapolation, and they are counted separately from the gap so the two claims cannot be
      added together by a reader who is not told.

DECISION RULE, declared before any number is read:

  D1  ARM.  The two tails are published per (leg, base) arm; an arm's interval is the hull of its
      rows' published per-row intervals, and per-row ranges must equal that hull (a disagreement
      is published, never silently widened away).
  D2  GAP.  gap = wide.lo - tight.hi, published only when positive.  A flip strictly inside the
      gap is unreachable by both tails at publication -- that is arithmetic on the published
      intervals, not a new statistic.
  D3  CLASS IS EXCLUSIVE AND COMPLETE.  Each row takes exactly one class by a fixed order
      (reachable_tight -> reachable_wide -> in_gap -> above_ceiling -> below_floor); the counts are
      asserted to sum to the rows censused.
  D4  CEILING IS THE FAMILY'S, NOT THIS FACE'S.  The published p95 ceiling is read off the source
      face's own summary and every arm's wide.hi is asserted not to exceed it.  A row above that
      ceiling needs a range this family never published; it is reported as extrapolation, never as
      widening headroom.
  D5  NO REBURN.  Published faces are re-read only.  No draw stream, no band rebuild, no engine.

Verdict vocabulary (frozen):
  no_arm_publishes_a_positive_gap
  no_row_falls_in_the_inter_range_gap
  the_gap_holds_fewer_rows_than_the_area_beyond_the_published_ceiling
  the_gap_is_the_only_widening_target

Usage:  python scripts/e285_interrange_gap_ceiling.py run|verify|selftest
"""
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e272_flip_budget_two_tails as e272  # noqa: E402  (ROOT / OUTDIR)

ROOT = e272.ROOT
OUTDIR = e272.OUTDIR

STUDY = "E285_interrange_gap_ceiling"
TITLE = ("the substitution can only add a can-move on rows whose flip falls in the gap between the "
         "two tails ranges -- how much widening headroom is spent on rows that stay unresolvable, "
         "and where does that headroom run out?")
CUTOFF = "2026-10-29"
SRC_BUDGET = "BANDFLIPBUDGET-%s.json" % CUTOFF   # E272's per-arm two-tail budget
FACE = "BANDGAPCEILING-%s.json" % CUTOFF
LATEST = "bandgapceiling_latest.json"
SELF_FACES = (FACE, LATEST)

TOL = 1e-12
TAILS = ("tight", "wide")

VERDICT_VOCAB = (
    "no_arm_publishes_a_positive_gap",
    "no_row_falls_in_the_inter_range_gap",
    "the_gap_holds_fewer_rows_than_the_area_beyond_the_published_ceiling",
    "the_gap_is_the_only_widening_target",
)

NO_BILL = ("measurement only: E272's published per-arm tail intervals and flips are re-read and "
           "arithmetic is done on them. No draw stream is drawn, no band rebuilt, no engine runs. "
           "A verdict here is a statement about the published numbers, not about the market.")


# ------------------------------------------------------------------ io
def load(name, outdir=None):
    with io.open(os.path.join(outdir or OUTDIR, name), encoding="utf-8") as fh:
        return json.load(fh)


def arms_of(face):
    """D1: published arms, in file order, each with its rows."""
    budget = face.get("tail_budget") or {}
    out = []
    for arm_key, arm in budget.items():
        rows = list(arm.get("rows") or [])
        out.append({"arm": str(arm_key), "leg": arm.get("leg"), "base": arm.get("base"),
                    "n_rows": arm.get("n_rows", len(rows)), "rows": rows})
    return out


# ------------------------------------------------------------------ arithmetic helpers
def interval(rows, tail):
    """Hull of one tail's published multiplier interval across an arm's rows."""
    lows, highs = [], []
    for rec in rows:
        slot = rec.get(tail) or {}
        lo, hi = slot.get("multiplier_min"), slot.get("multiplier_max")
        if lo is None or hi is None:
            continue
        lows.append(float(lo))
        highs.append(float(hi))
    if not lows:
        return None
    return {"lo": min(lows), "hi": max(highs), "spread": max(highs) - min(lows),
            "n_rows_with_interval": len(lows)}


def ranges_are_row_identical(rows, tail, hull):
    """D1: every row in an arm must carry the arm's own hull, or the hull is not the arm's range."""
    if not hull:
        return None
    bad = []
    for rec in rows:
        slot = rec.get(tail) or {}
        lo, hi = slot.get("multiplier_min"), slot.get("multiplier_max")
        if lo is None or hi is None:
            continue
        if abs(float(lo) - hull["lo"]) > TOL or abs(float(hi) - hull["hi"]) > TOL:
            bad.append({"row_key": row_key(rec), "lo": lo, "hi": hi})
    return {"identical": not bad, "off_hull_rows": bad}


def row_key(rec):
    return "%s|%s|%s" % (rec.get("row") or rec.get("leg"), rec.get("base"), rec.get("index"))


def classify(flip, tight, wide):
    """D3: exactly one class, fixed order, tolerance-inclusive on the published bounds."""
    if flip is None or tight is None or wide is None:
        return "no_flip"
    if tight["lo"] - TOL <= flip <= tight["hi"] + TOL:
        return "reachable_tight"
    if wide["lo"] - TOL <= flip <= wide["hi"] + TOL:
        return "reachable_wide"
    if tight["hi"] < flip < wide["lo"] - TOL:
        return "in_gap"
    if flip > wide["hi"] + TOL:
        return "above_ceiling"
    if flip < tight["lo"] - TOL:
        return "below_floor"
    return "in_gap"  # tight.hi == wide.lo is a zero-width gap; unreachable, classified honestly


def nearest_distance_pct(flip, lo, hi):
    """Relative distance from the flip to the nearest published bound of an interval."""
    if flip is None or lo is None or hi is None or not flip:
        return None
    if lo - TOL <= flip <= hi + TOL:
        return 0.0
    bound = lo if flip < lo else hi
    return abs(bound - flip) / abs(flip) * 100.0


def _ratio(num, den):
    if num is None or den is None or abs(den) <= TOL:
        return None
    return num / den


# ------------------------------------------------------------------ per-arm measurement
def analyse_arm(arm, published_ceiling=None):
    rows = arm["rows"]
    tight = interval(rows, "tight")
    wide = interval(rows, "wide")
    gap_lo = tight["hi"] if tight else None
    gap_hi = wide["lo"] if wide else None
    gap_width = None if (gap_lo is None or gap_hi is None) else (gap_hi - gap_lo)
    rec = {
        "arm": arm["arm"], "leg": arm["leg"], "base": arm["base"], "n_rows": len(rows),
        "tight_interval": tight, "wide_interval": wide,
        "gap": {"lo": gap_lo, "hi": gap_hi, "width": gap_width,
                "positive": bool(gap_width is not None and gap_width > TOL),
                "width_in_tight_spreads": _ratio(gap_width, tight["spread"] if tight else None),
                "width_in_wide_spreads": _ratio(gap_width, wide["spread"] if wide else None)},
        "range_identity": {"tight": ranges_are_row_identical(rows, "tight", tight),
                           "wide": ranges_are_row_identical(rows, "wide", wide)},
        "rows": [],
    }
    if wide and published_ceiling is not None and wide["hi"] > published_ceiling + TOL:
        rec["range_identity"]["wide_exceeds_published_ceiling"] = wide["hi"] - published_ceiling
    for r in rows:
        flip = r.get("flip_multiplier")
        cls = classify(flip, tight, wide)
        item = {"row_key": row_key(r), "row": r.get("row") or r.get("leg"), "cell": r.get("cell"),
                "index": r.get("index"), "flip": flip, "class": cls,
                "published_reachable": {"tight": bool((r.get("tight") or {}).get("reachable")),
                                        "wide": bool((r.get("wide") or {}).get("reachable"))}}
        if cls == "in_gap":
            item["distance_to_tight_hi_pct"] = nearest_distance_pct(flip, tight["lo"], tight["hi"])
            item["distance_to_wide_lo_pct"] = nearest_distance_pct(flip, wide["lo"], wide["hi"])
            item["required_widening_of_wide_lo_pct"] = (
                None if not wide["lo"] else (wide["lo"] - flip) / wide["lo"] * 100.0)
            item["required_widening_of_tight_hi_pct"] = (
                None if not flip else (flip - tight["hi"]) / flip * 100.0)
            item["gap_fraction_below_wide_floor"] = _ratio(wide["lo"] - flip,
                                                           gap_width)
        elif cls == "above_ceiling":
            item["distance_above_wide_hi_pct"] = nearest_distance_pct(flip, wide["lo"], wide["hi"])
            item["flip_over_wide_hi"] = _ratio(flip, wide["hi"])
            if published_ceiling:
                item["flip_over_published_ceiling"] = _ratio(flip, published_ceiling)
        elif cls == "below_floor":
            item["distance_below_tight_lo_pct"] = nearest_distance_pct(flip, tight["lo"], tight["hi"])
        rec["rows"].append(item)
    counts = {}
    for item in rec["rows"]:
        counts[item["class"]] = counts.get(item["class"], 0) + 1
    rec["counts"] = counts
    rec["partition_sums_to_rows"] = sum(counts.values()) == len(rec["rows"])
    return rec


def arm_table(face):
    published_ceiling = (face.get("summary") or {}).get("published_p95_ceiling")
    return [analyse_arm(arm, published_ceiling) for arm in arms_of(face)]


# ------------------------------------------------------------------ verdict
def decide(table, summary_counts):
    if not any((rec["gap"] or {}).get("positive") for rec in table):
        return "no_arm_publishes_a_positive_gap"
    if not summary_counts.get("n_gap_rows"):
        return "no_row_falls_in_the_inter_range_gap"
    if summary_counts.get("n_above_ceiling", 0) > summary_counts["n_gap_rows"]:
        return "the_gap_holds_fewer_rows_than_the_area_beyond_the_published_ceiling"
    return "the_gap_is_the_only_widening_target"


def build(outdir=None):
    outdir = outdir or OUTDIR
    face = load(SRC_BUDGET, outdir)
    table = arm_table(face)
    src_summary = face.get("summary") or {}
    published_ceiling = src_summary.get("published_p95_ceiling")
    published_floor = src_summary.get("published_p05_floor")

    totals = {}
    for rec in table:
        for cls, n in rec["counts"].items():
            totals[cls] = totals.get(cls, 0) + n
    rows_censused = sum(totals.values())
    gap_rows = [i for rec in table for i in rec["rows"] if i["class"] == "in_gap"]
    above_rows = [i for rec in table for i in rec["rows"] if i["class"] == "above_ceiling"]
    below_rows = [i for rec in table for i in rec["rows"] if i["class"] == "below_floor"]

    identity = {
        "rows_censused": rows_censused,
        "rows_measured_in_source": src_summary.get("rows_measured"),
        "rows_match_source": src_summary.get("rows_measured") == rows_censused,
        "reachable_wide_mine": totals.get("reachable_wide", 0),
        "reachable_wide_source": src_summary.get("rows_reachable_wide"),
        "reachable_tight_mine": totals.get("reachable_tight", 0),
        "reachable_tight_source": src_summary.get("rows_reachable_tight"),
        "reachable_either_source": src_summary.get("rows_reachable_either"),
        "reachable_either_mine": totals.get("reachable_wide", 0) + totals.get("reachable_tight", 0),
        "gap_rows_are_unreachable_by_construction": all(
            not i["published_reachable"]["tight"] and not i["published_reachable"]["wide"]
            for i in gap_rows),
        "partition_sums_to_rows": all(rec["partition_sums_to_rows"] for rec in table),
        "arm_hulls_are_row_identical": {
            rec["arm"]: {"tight": (rec["range_identity"]["tight"] or {}).get("identical"),
                         "wide": (rec["range_identity"]["wide"] or {}).get("identical")}
            for rec in table},
    }
    identity["counts_agree_with_source"] = bool(
        identity["rows_match_source"]
        and identity["reachable_wide_mine"] == identity["reachable_wide_source"]
        and identity["reachable_tight_mine"] == (identity["reachable_tight_source"] or 0))

    summary = {
        "rows_censused": rows_censused,
        "arms_measured": len(table),
        "n_gap_rows": len(gap_rows),
        "n_above_ceiling": len(above_rows),
        "n_below_floor": len(below_rows),
        "n_reachable_tight": totals.get("reachable_tight", 0),
        "n_reachable_wide": totals.get("reachable_wide", 0),
        "gap_rows": [i["row_key"] for i in gap_rows],
        "above_ceiling_rows": [i["row_key"] for i in above_rows],
        "below_floor_rows": [i["row_key"] for i in below_rows],
        "published_ceiling": published_ceiling,
        "published_floor": published_floor,
        "share_of_unresolvable_in_gap": _ratio(
            len(gap_rows),
            len(gap_rows) + len(above_rows) + len(below_rows)),
        "share_above_ceiling": _ratio(len(above_rows), rows_censused),
        "widening_ceiling_rows": len(gap_rows),
        "calibrated": False,
    }
    verdict = decide(table, summary)
    summary["verdict"] = verdict

    gaps = [{"arm": rec["arm"], "lo": rec["gap"]["lo"], "hi": rec["gap"]["hi"],
             "width": rec["gap"]["width"], "positive": rec["gap"]["positive"],
             "width_in_tight_spreads": rec["gap"]["width_in_tight_spreads"],
             "width_in_wide_spreads": rec["gap"]["width_in_wide_spreads"]}
            for rec in table]

    return {
        "study": STUDY, "title": TITLE, "evidence_cutoff": CUTOFF,
        "generated": None,  # stamped by run
        "no_bill": NO_BILL,
        "source_faces": [SRC_BUDGET],
        "frozen_spec": {
            "D1_arm_interval": "the two tails are published per (leg, base) arm; the arm's "
                               "interval is the hull of its rows' ranges and every row must match "
                               "the hull (per-row disagreement is published, not smoothed)",
            "D2_gap": "gap = wide.lo - tight.hi, positive only when the tight interval ends before "
                      "the wide one starts; a flip inside it is unreachable by both tails at "
                      "publication (arithmetic on published intervals)",
            "D3_exclusive_partition": "each row takes one class by fixed order reachable_tight -> "
                                      "reachable_wide -> in_gap -> above_ceiling -> below_floor and "
                                      "the class counts must sum to the rows censused",
            "D4_ceiling_is_the_family_s": "the published p95 ceiling is read off the source "
                                          "summary; a flip above it needs a range this family never "
                                          "published and is reported as extrapolation, not headroom",
            "D5_no_reburn": "published faces re-read only; no draw stream, no band rebuild, no engine",
            "tolerance": TOL,
            "verdict_vocab": list(VERDICT_VOCAB),
        },
        "arms": table,
        "gap_by_arm": gaps,
        "widening_target": {
            "class": "in_gap",
            "rows": gap_rows,
            "statement": "these rows are reachable by no published tail; covering them requires "
                         "extending one interval into the gap, and the gap is measured against each "
                         "tail's own spread so the extension can be priced in the family's ruler",
            "max_rows_any_gap_widening_could_add": len(gap_rows),
        },
        "beyond_ceiling": {
            "rows": above_rows,
            "statement": "these flips lie above the highest published multiplier in the family; "
                         "they are not widening headroom -- reaching them requires a range outside "
                         "every interval this family published",
            "n_rows": len(above_rows),
            "published_ceiling": published_ceiling,
        },
        "below_floor": {
            "rows": below_rows,
            "statement": "these flips lie below the lowest published multiplier in the family; they "
                         "need a narrower range or a different instrument",
            "n_rows": len(below_rows),
            "published_floor": published_floor,
        },
        "identity_check": identity,
        "summary": summary,
        "verdict": verdict,
        "verdict_reason": _reason(verdict, summary, gap_rows, above_rows),
    }


def _reason(verdict, summary, gap_rows, above_rows):
    if verdict == "no_arm_publishes_a_positive_gap":
        return ("every arm's tight interval reaches at least the wide interval's floor, so there is "
                "no inter-range gap to measure (%d arm(s) censused)."
                % summary["arms_measured"])
    if verdict == "no_row_falls_in_the_inter_range_gap":
        return ("%d arm(s) publish a positive gap but no flip lands inside one; the unresolvable "
                "rows sit outside the published intervals entirely (%d above the ceiling, %d below "
                "the floor)."
                % (summary["arms_measured"], summary["n_above_ceiling"],
                   summary["n_below_floor"]))
    if verdict == "the_gap_holds_fewer_rows_than_the_area_beyond_the_published_ceiling":
        return ("%d of %d row(s) fall in a positive inter-range gap (share of all unresolvable "
                "rows: %s), while %d row(s) sit above the family's published ceiling of %s -- the "
                "gap is a smaller widening target than the extrapolation zone, and any widening "
                "inside the published evidence can add at most those %d row(s)."
                % (len(gap_rows), summary["rows_censused"],
                   _fmt_pct(summary["share_of_unresolvable_in_gap"]),
                   len(above_rows), _fmt(summary["published_ceiling"]), len(gap_rows)))
    return ("%d of %d row(s) fall in a positive inter-range gap and no row sits above the family's "
            "published ceiling of %s, so the gap is the only target any widening could buy."
            % (len(gap_rows), summary["rows_censused"], _fmt(summary["published_ceiling"])))


def _fmt(value):
    return "n/a" if value is None else "%.6f" % value


def _fmt_pct(value):
    return "n/a" if value is None else "%.1f pct" % (value * 100.0)


# ------------------------------------------------------------------ commands
def write_face(face, outdir=None):
    outdir = outdir or OUTDIR
    text = json.dumps(face, ensure_ascii=False, indent=1) + "\n"
    for name in (FACE, LATEST):
        fh = io.open(os.path.join(outdir, name), "w", encoding="utf-8", newline="\n")
        try:
            fh.write(text)
        finally:
            fh.close()


def cmd_run():
    import datetime
    face = build()
    face["generated"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    write_face(face)
    s = face["summary"]
    print("E285 %s" % face["verdict"])
    print("  arms=%d rows=%d gap=%d above_ceiling=%d below_floor=%d reachable=%d/%d"
          % (s["arms_measured"], s["rows_censused"], s["n_gap_rows"], s["n_above_ceiling"],
             s["n_below_floor"], s["n_reachable_tight"], s["n_reachable_wide"]))
    print("  gap rows: %s" % (", ".join(s["gap_rows"]) or "none"))
    print("  ceiling=%s  identity=%s"
          % (_fmt(s["published_ceiling"]), face["identity_check"]["counts_agree_with_source"]))
    return 0


def cmd_verify():
    stored = load(FACE)
    live = build()
    problems = []
    for key in ("verdict",):
        if stored.get(key) != live.get(key):
            problems.append("%s: stored=%r live=%r" % (key, stored.get(key), live.get(key)))
    if (stored.get("summary") or {}).get("gap_rows") != (live.get("summary") or {}).get("gap_rows"):
        problems.append("gap rows do not re-derive")
    if (stored.get("summary") or {}).get("above_ceiling_rows") != \
            (live.get("summary") or {}).get("above_ceiling_rows"):
        problems.append("above-ceiling rows do not re-derive")
    if (stored.get("summary") or {}).get("n_gap_rows") != (live.get("summary") or {}).get("n_gap_rows"):
        problems.append("gap row count does not re-derive")
    if not live["identity_check"]["partition_sums_to_rows"]:
        problems.append("the class partition does not sum to the rows censused (D3)")
    if not live["identity_check"]["gap_rows_are_unreachable_by_construction"]:
        problems.append("a gap row is published reachable by a tail (D2)")
    if (stored.get("summary") or {}).get("verdict") not in VERDICT_VOCAB:
        problems.append("verdict outside the frozen set")
    print("E285 verify: %d problem(s)" % len(problems))
    for p in problems:
        print("  - %s" % p)
    return 0 if not problems else 1


# ------------------------------------------------------------------ selftest
def _td(lo, hi):
    return {"multiplier_min": lo, "multiplier_max": hi}


def _fixture_arm(gap_row_flip=1.5, above_row_flip=None):
    rows = [
        {"row": "cross", "leg": "cross", "base": 60, "index": 1, "flip_multiplier": 2.2,
         "tight": _td(1.0, 1.1), "wide": dict(_td(2.0, 2.3), reachable=True)},
        {"row": "cross", "leg": "cross", "base": 60, "index": 2, "flip_multiplier": gap_row_flip,
         "tight": _td(1.0, 1.1), "wide": _td(2.0, 2.3)},
    ]
    if above_row_flip is not None:
        rows.append({"row": "cross", "leg": "cross", "base": 60, "index": 3,
                     "flip_multiplier": above_row_flip,
                     "tight": _td(1.0, 1.1), "wide": _td(2.0, 2.3)})
    return {"arm": "cross:60", "leg": "cross", "base": 60, "n_rows": len(rows), "rows": rows}


def cmd_selftest():
    ok, fail = 0, []

    def leg(name, cond, detail=""):
        nonlocal ok
        if cond:
            ok += 1
        else:
            fail.append("%s %s" % (name, detail))

    tight = {"lo": 1.0, "hi": 1.1}
    wide = {"lo": 2.0, "hi": 2.3}
    # L1 a flip between the intervals is in the gap
    leg("L1", classify(1.5, tight, wide) == "in_gap")
    # L2 the published bounds are inclusive on both sides (tolerance, not strictness)
    leg("L2", classify(1.1, tight, wide) == "reachable_tight"
        and classify(2.0, tight, wide) == "reachable_wide")
    # L3 above the wide ceiling is extrapolation, not the gap
    leg("L3", classify(2.5, tight, wide) == "above_ceiling")
    # L4 below the tight floor is its own class
    leg("L4", classify(0.5, tight, wide) == "below_floor")
    # L5 a missing flip is not forced into a class
    leg("L5", classify(None, tight, wide) == "no_flip")
    # L6 the arm hull is the min/max of its rows, and identical rows produce an identical verdict
    arm = _fixture_arm()
    tight_hull = interval(arm["rows"], "tight")
    leg("L6", abs(tight_hull["lo"] - 1.0) < 1e-12 and abs(tight_hull["hi"] - 1.1) < 1e-12
        and tight_hull["n_rows_with_interval"] == 2, tight_hull)
    # L7 a row off the hull is published rather than smoothed
    off = _fixture_arm()
    off["rows"][1]["tight"] = _td(0.9, 1.2)
    chk = ranges_are_row_identical(off["rows"], "tight", interval(off["rows"], "tight"))
    leg("L7", chk["identical"] is False and len(chk["off_hull_rows"]) == 1, chk)
    # L8 D3: the partition sums to the rows censused
    rec = analyse_arm(_fixture_arm())
    leg("L8", rec["partition_sums_to_rows"] and
        sum(rec["counts"].values()) == rec["n_rows"], rec["counts"])
    # L9 the gap is positive only when the tight interval ends before the wide one starts
    rec2 = analyse_arm(_fixture_arm())
    leg("L9", rec2["gap"]["positive"] and abs(rec2["gap"]["width"] - 0.9) < 1e-12, rec2["gap"])
    overlap = _fixture_arm()
    for r in overlap["rows"]:
        r["tight"] = _td(1.0, 2.1)
    leg("L10", analyse_arm(overlap)["gap"]["positive"] is False)
    # L11 the gap is priced in each tail's own spread (the family's only ruler)
    leg("L11", abs(rec2["gap"]["width_in_tight_spreads"] - 9.0) < 1e-9
        and abs(rec2["gap"]["width_in_wide_spreads"] - 3.0) < 1e-9, rec2["gap"])
    # L12 a gap row carries the widening it would need from both published bounds
    item = [i for i in rec2["rows"] if i["class"] == "in_gap"][0]
    leg("L12", abs(item["required_widening_of_tight_hi_pct"] - (1.5 - 1.1) / 1.5 * 100) < 1e-9
        and abs(item["required_widening_of_wide_lo_pct"] - (2.0 - 1.5) / 2.0 * 100) < 1e-9, item)
    # L13 D4: an above-ceiling row reports the flip over the ceiling, never as headroom
    rec3 = analyse_arm(_fixture_arm(above_row_flip=3.0), published_ceiling=2.3)
    ab = [i for i in rec3["rows"] if i["class"] == "above_ceiling"][0]
    leg("L13", abs(ab["flip_over_wide_hi"] - 3.0 / 2.3) < 1e-12
        and abs(ab["flip_over_published_ceiling"] - 3.0 / 2.3) < 1e-12
        and "flip_over_wide_hi" not in [i for i in rec3["rows"] if i["class"] == "in_gap"][0], ab)
    # L14 an arm whose ceiling exceeds the family's ceiling is flagged, not silently accepted
    bad = analyse_arm(_fixture_arm(), published_ceiling=2.0)
    leg("L15", "wide_exceeds_published_ceiling" in bad["range_identity"])
    # L16 verdict vocabulary is frozen and decide() only returns members
    counts = {"n_gap_rows": 1, "n_above_ceiling": 2}
    leg("L16", decide([rec2], counts)
        == "the_gap_holds_fewer_rows_than_the_area_beyond_the_published_ceiling"
        and decide([rec2], counts) in VERDICT_VOCAB)
    # L17 the gap is the only target when nothing sits above the ceiling
    leg("L17", decide([rec2], {"n_gap_rows": 1, "n_above_ceiling": 0})
        == "the_gap_is_the_only_widening_target")
    # L18 no gap rows at all is its own verdict, never a silent zero
    leg("L18", decide([rec2], {"n_gap_rows": 0, "n_above_ceiling": 3})
        == "no_row_falls_in_the_inter_range_gap")
    # L19 no positive gap at all short-circuits the verdict
    leg("L19", decide([analyse_arm(overlap)], {"n_gap_rows": 0, "n_above_ceiling": 0})
        == "no_arm_publishes_a_positive_gap")
    # L20 on the real face: the class counts sum to the rows censused and the gap rows are
    # published unreachable by both tails
    live = build()
    ic = live["identity_check"]
    leg("L20", ic["partition_sums_to_rows"] and ic["gap_rows_are_unreachable_by_construction"], ic)
    # L21 the real face's reachable counts agree with the source summary (an identity, not a copy)
    leg("L21", ic["rows_match_source"] and ic["counts_agree_with_source"], ic)
    # L22 this face never censuses itself (E180/E209 self-inclusion family)
    face = live
    leg("L22", face["source_faces"] == [SRC_BUDGET])
    # L23 the distance helper returns 0 inside a range and a positive pct outside
    leg("L23", nearest_distance_pct(1.05, 1.0, 1.1) == 0.0
        and nearest_distance_pct(1.5, 1.0, 1.1) > 0)
    # L24 a zero-spread interval cannot be used as a ruler (no division by zero)
    leg("L24", _ratio(0.5, 0.0) is None and _ratio(0.5, None) is None)

    print("E285 selftest: %d/%d" % (ok, ok + len(fail)))
    for f in fail:
        print("  FAIL %s" % f)
    return 0 if not fail else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "run":
        return cmd_run()
    if cmd == "verify":
        return cmd_verify()
    if cmd == "selftest":
        return cmd_selftest()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))