"""E267 -- how much margin must a donor clear before the flip is worth acting on?

E266's bracket screen is exact on the 36 published comparisons, but it is a knife edge: a donor
0.0001 above the row's own-side threshold counts exactly as much as one 0.3 above it.  Anyone
acting on the screen has to decide how much clearance to demand, and that cost is measurable on
the same comparisons without drawing anything new:

    margin = donor_p95 / t - 1        the clearance the donor has over the flip threshold t

sweeping b in "donor_p95 > t * (1 + b)" over four rules (with and without the own-side guard that
E266 found necessary, on both threshold forms) publishes the false-positive / missed-move curve.

The reading that matters is not where the curve is best but whether it ever separates: a buffer can
only help if every false positive clears its threshold by less than some real move does.  If the
closest non-move sits BELOW the closest move, no b exists that keeps the move and drops the
non-move, and the missing ingredient is the guard, not the margin.

The b grid is frozen as a coarse grid plus every observed margin as a breakpoint, so the published
curve is exact on the population rather than sampled -- the curve can only change where a margin
crosses the line, and those are exactly the breakpoints.
"""
from __future__ import print_function

import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e266_wide_end_screen_holdout as e266   # noqa: E402  (comparison set, both thresholds)

ROOT = e266.ROOT
OUTDIR = os.path.join(ROOT, "results", "state_tilt")

STUDY = "E267_screen_buffer_margin"
TITLE = "how much margin must a donor clear before the flip is worth acting on?"
CUTOFF = "2026-10-29"
SRC = "BANDTRANSFER-%s.json" % CUTOFF
FACE = "BANDMARGIN-%s.json" % CUTOFF
LATEST = "bandmargin_latest.json"

TOL = 1e-12

NO_BILL = ("measurement only: E262's published pairs are re-read through E266's comparison set; no "
           "shuffle stream is drawn, no band is rebuilt, and no row verdict outside this face moves")

# frozen coarse grid (the observed margins are appended as breakpoints at run time)
GRID = (0.0, 0.001, 0.005, 0.01, 0.02, 0.03, 0.045, 0.05, 0.06, 0.075, 0.1, 0.15, 0.2, 0.3,
        0.5, 1.0, 2.0, 2.5)

RULES = (
    # name, threshold field, needs the own-side guard
    ("single_maxend", "t_max_end", False),
    ("guarded_maxend", "t_max_end", True),
    ("single_side", "t_side", False),
    ("guarded_side", "t_side", True),
)

VERDICT_VOCAB = (
    "buffer_cannot_buy_precision_itself",   # no b separates; the guard does the work alone
    "buffer_separates_moves_from_false_positives",  # some b keeps every move and drops every fp
    "no_moves_to_protect",                  # nothing moved in the population
    "guard_alone_is_not_exact",             # the own-side guard has its own error, so it is not
                                            # simply "use the guard"
    "undefined_population",                 # nothing to compare
)


# ------------------------------------------------------------------ the buffer
def margin(donor_p95, t):
    """The clearance a donor has over the flip threshold: don p95 = t * (1 + margin)."""
    if donor_p95 is None or t is None:
        return None
    t = float(t)
    if t <= 0:
        return None
    return float(donor_p95) / t - 1.0


def buffer_pred(rule_threshold, needs_guard, rec, b):
    """Does a rule with clearance b flag this comparison?  Strictly above the buffered line."""
    donor = rec.get("donor_p95")
    t = rec.get(rule_threshold)
    own = rec.get("own_p95")
    if donor is None or t is None:
        return None
    t = float(t)
    if t <= 0:
        return None
    if not float(donor) > t * (1.0 + float(b)):
        return False
    if needs_guard:
        if own is None:
            return None
        # a donor can only move a row its own end had already rejected
        return bool(float(own) < t)
    return True


def confusion(records, rule_threshold, needs_guard, b):
    c = {"predicted": 0, "actual": 0, "tp": 0, "fp": 0, "fn": 0, "tn": 0, "undefined": 0}
    for r in records:
        pred, act = buffer_pred(rule_threshold, needs_guard, r, b), r.get("actual_moved")
        if pred is None:
            c["undefined"] += 1
            continue
        c["predicted"] += 1 if pred else 0
        c["actual"] += 1 if act else 0
        if pred and act:
            c["tp"] += 1
        elif pred and not act:
            c["fp"] += 1
        elif act and not pred:
            c["fn"] += 1
        else:
            c["tn"] += 1
    c["precision"] = (None if not c["predicted"]
                      else float(c["tp"]) / c["predicted"])
    c["recall"] = (None if not c["actual"] else float(c["tp"]) / c["actual"])
    c["exact"] = bool(c["fp"] == 0 and c["fn"] == 0 and c["undefined"] == 0 and c["predicted"] > 0)
    return c


def breakpoints(records):
    """Every clearance value the population actually carries, on either threshold form.

    Only non-negative clearances are swept: a buffer demands MORE clearance than the threshold,
    so a negative "buffer" (accepting a donor below the threshold) is a different rule, not a
    weaker setting of this one.
    """
    out = set(float(b) for b in GRID)
    for r in records:
        for field in ("t_max_end", "t_side"):
            m = margin(r.get("donor_p95"), r.get(field))
            if m is not None and m >= 0.0:
                out.add(round(m, 12))
    return sorted(out)


def curve(records, rule_threshold, needs_guard, bps):
    rows = []
    grid = set(float(b) for b in GRID)
    for b in bps:
        c = confusion(records, rule_threshold, needs_guard, b)
        c["b"] = b
        c["source"] = "grid" if round(b, 12) in grid else "breakpoint"
        rows.append(c)
    return rows


def curve_summary(rows):
    """Where the curve peaks, and what a buffer actually costs."""
    defined = [r for r in rows if r.get("precision") is not None]
    best = None
    for r in defined:
        if best is None or (r["precision"], r["tp"], -r["b"]) > (best["precision"], best["tp"],
                                                                -best["b"]):
            best = r
    exact = [r["b"] for r in rows if r.get("exact")]
    first_buffer = next((r for r in rows if r["b"] > 0), None)
    at_zero = next((r for r in rows if abs(r["b"]) <= TOL), None)
    no_move = next((r for r in rows if r["b"] > 0 and r["tp"] == 0), None)
    return {
        "at_zero": at_zero,
        "first_buffer": first_buffer,
        "best": best,
        "best_precision": None if best is None else best["precision"],
        "best_b": None if best is None else best["b"],
        "best_b_window": _best_window(defined, best),
        "exact_b": exact,
        "reaches_exact": bool(exact),
        "first_b_with_no_true_positive": None if no_move is None else no_move["b"],
    }


def _best_window(defined, best):
    """The b interval over which the maximal precision is attained (open/closed disclosed)."""
    if best is None:
        return None
    same = [r["b"] for r in defined if abs(r["precision"] - best["precision"]) <= TOL]
    if not same:
        return None
    lo, hi = min(same), max(same)
    return {"from": lo, "to": hi, "width": hi - lo,
            "note": "b is swept at observed clearance values, so this is the widest published "
                    "interval carrying the peak, not a confidence region"}


# ------------------------------------------------------------------ separation
def separation(records):
    """Are the moves' clearances above every non-move's?  If not, no buffer can help."""
    tp = sorted(v for v in (margin(r.get("donor_p95"), r.get("t_side"))
                            for r in records if r.get("actual_moved")) if v is not None)
    fp = sorted(v for v in (margin(r.get("donor_p95"), r.get("t_side"))
                            for r in records if not r.get("actual_moved")
                            and buffer_pred("t_side", False, r, 0.0) is True) if v is not None)
    if not tp:
        return {"tp_margins_sorted": tp, "fp_margins_sorted": fp, "separable": None,
                "interleaved": None, "note": "no positive to place"}
    nearest_fp = fp[0] if fp else None
    nearest_tp = tp[0]
    # a buffer sets one clearance for the whole population, so it must clear every NON-MOVE and
    # stay under every MOVE: the binding constraint is the largest non-move, not the nearest one.
    largest_fp = fp[-1] if fp else None
    separable = None if largest_fp is None else bool(largest_fp < nearest_tp)
    return {
        "tp_margins_sorted": tp,
        "fp_margins_sorted": fp,
        "nearest_true_positive_margin": nearest_tp,
        "nearest_false_positive_margin": nearest_fp,
        "largest_true_positive_margin": tp[-1],
        "gap_positive_minus_false": (None if nearest_fp is None else nearest_tp - nearest_fp),
        "largest_false_positive_margin": largest_fp,
        "separable": separable,
        "interleaved": (None if separable is None else bool(not separable)),
        "separating_b_window": (None if not separable else {"from": largest_fp, "to": nearest_tp}),
        "buffer_that_clears_every_false_positive": largest_fp,
        "note": ("a buffer separates only if EVERY non-move clears its threshold by less than "
                 "EVERY move does; one non-move clearing by more than the closest move cannot be "
                 "filtered by margin at any cost the move survives"),
    }


def verdict_of(records, sums, sep, guard_ref):
    if not records:
        return ("undefined_population", "no comparison carries a measured recipient row")
    actual = sum(1 for r in records if r.get("actual_moved"))
    if not actual:
        return ("no_moves_to_protect",
                "%d comparison(s) but not one published pair moves a verdict" % len(records))
    if not (guard_ref.get("fp") == 0 and guard_ref.get("fn") == 0
            and guard_ref.get("predicted")):
        return ("guard_alone_is_not_exact",
                "the own-side guard alone gives tp/fp/fn %d/%d/%d -- neither the guard nor a "
                "buffer is sufficient"
                % (guard_ref.get("tp", 0), guard_ref.get("fp", 0), guard_ref.get("fn", 0)))
    if sums["single_side"]["reaches_exact"] or sums["single_maxend"]["reaches_exact"]:
        return ("buffer_separates_moves_from_false_positives",
                "some buffer keeps every move and drops every non-move")
    best = sums["single_side"]["best"]
    unbuffered = sums["single_side"]["at_zero"]
    reason = ("a buffer alone peaks at precision %.3f (tp %d of %d flagged) at b=%s, against %.3f "
              "unbuffered; the closest non-move clears its threshold by %s while the closest move "
              "clears it by %s, so no b keeps that move and drops that non-move"
              % (sums["single_side"]["best_precision"] or 0.0,
                 best["tp"] if best else 0, best["predicted"] if best else 0,
                 ("%.4f" % best["b"]) if best else "n/a",
                 (unbuffered["precision"] if unbuffered else 0.0) or 0.0,
                 ("%.4f" % sep["nearest_false_positive_margin"])
                 if sep.get("nearest_false_positive_margin") is not None else "n/a",
                 ("%.4f" % sep["nearest_true_positive_margin"])
                 if sep.get("nearest_true_positive_margin") is not None else "n/a"))
    if sep.get("largest_false_positive_margin") is not None:
        reason += ("; a non-move clears by up to %.2f%% of its threshold, so the buffer that would "
                   "clear every one of them costs every move"
                   % (100.0 * sep["largest_false_positive_margin"]))
    reason += "; the own-side guard reaches %d/%d with no buffer at all" % (
        guard_ref.get("tp", 0), guard_ref.get("predicted", 0))
    return ("buffer_cannot_buy_precision_itself", reason)


# ------------------------------------------------------------------ run
def load(name):
    return e266.load(name)


def run(save=True, outdir=None):
    outdir = outdir or OUTDIR
    recs, groups = e266.comparisons(load(SRC))
    bps = breakpoints(recs)
    curves, sums = {}, {}
    for name, field, guard in RULES:
        rows = curve(recs, field, guard, bps)
        curves[name] = rows
        sums[name] = curve_summary(rows)
    sep = separation(recs)
    guard_ref = confusion(recs, "t_side", True, 0.0)
    verdict, reason = verdict_of(recs, sums, sep, guard_ref)
    moved = [r for r in recs if r.get("actual_moved")]

    out = {
        "study": STUDY,
        "title": TITLE,
        "evidence_cutoff": CUTOFF,
        "generated": None,
        "source_face": SRC,
        "source_comparisons": "E266's 36 comparison rows (E262's 48 pairs x measured rows)",
        "no_bill": NO_BILL,
        "verdict": verdict,
        "verdict_reason": reason,
        "frozen_spec": {
            "population": "the 36 comparisons E266 published (re-derived from E262, not re-read)",
            "margin": "donor_p95 / t - 1  -- the clearance the donor has over threshold t",
            "buffer_rule": "flag iff donor_p95 > t * (1 + b); equality is NOT clearance (strict >)",
            "thresholds": {"t_side": "|b| / |the band end on the row's own side|",
                           "t_max_end": "|b| / max(|lo|,|hi|)  (E264/E265 form)"},
            "rules": {name: {"threshold": field, "own_side_guard": guard}
                      for name, field, guard in RULES},
            "b_grid": {"fixed": list(GRID),
                       "breakpoints": "every non-negative clearance value on either threshold form",
                       "b_domain": "b >= 0 only: a buffer demands more clearance than the "
                                   "threshold, so accepting a donor below the threshold is a "
                                   "different rule, not a weaker setting of this one",
                       "why": "the curve can only change where a margin crosses the line, so the "
                              "breakpoints make the published curve exact on this population"},
            "actual": "E262's published moved list (E266's actual_moved), matched by row index",
            "no_bill": NO_BILL,
        },
        "summary": {
            "comparisons": len(recs),
            "moves_published": len(moved),
            "breakpoints": len(bps),
            "rules": {name: {"at_zero": sums[name]["at_zero"],
                             "first_buffer": sums[name]["first_buffer"],
                             "best_precision": sums[name]["best_precision"],
                             "best_b": sums[name]["best_b"],
                             "best_b_window": sums[name]["best_b_window"],
                             "reaches_exact": sums[name]["reaches_exact"],
                             "exact_b": sums[name]["exact_b"],
                             "first_b_with_no_true_positive":
                                 sums[name]["first_b_with_no_true_positive"]}
                      for name, _f, _g in RULES},
            "guard_only": guard_ref,
            "separation": sep,
            "moves_detail": [{"index": r.get("index"), "cell": r.get("cell"), "row": r.get("row"),
                       "arm": r.get("arm"), "donor": r.get("donor"),
                       "recipient": r.get("recipient"),
                       "margin_over_side_threshold": margin(r.get("donor_p95"), r.get("t_side")),
                       "margin_over_max_end_threshold":
                           margin(r.get("donor_p95"), r.get("t_max_end"))}
                      for r in moved],
            "resolution_note": ("%d comparison(s) with %d positive(s): the curve is a consistency "
                                "read on published pairs, not a validated operating point"
                                % (len(recs), len(moved))),
        },
        "curves": curves,
        "comparison_margins": [
            {"index": r.get("index"), "cell": r.get("cell"), "row": r.get("row"),
             "arm": r.get("arm"), "donor": r.get("donor"), "recipient": r.get("recipient"),
             "side": r.get("side"), "actual_moved": r.get("actual_moved"),
             "own_verdict": r.get("own_verdict"),
             "t_side": r.get("t_side"), "t_max_end": r.get("t_max_end"),
             "donor_p95": r.get("donor_p95"), "own_p95": r.get("own_p95"),
             "margin_over_side_threshold": margin(r.get("donor_p95"), r.get("t_side")),
             "margin_over_max_end_threshold": margin(r.get("donor_p95"), r.get("t_max_end"))}
            for r in sorted(recs, key=lambda r: (margin(r.get("donor_p95"), r.get("t_side"))
                                                 if r.get("t_side") else -9.9))],
        "groups": groups,
    }
    out["generated"] = _stamp()
    if save:
        _write(out, outdir)
    return out


def _stamp():
    import datetime
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def _write(face, outdir, tag=""):
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "BANDMARGIN-%s%s.json" % (face.get("evidence_cutoff"), tag))
    text = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text + "\n")
    with io.open(os.path.join(outdir, LATEST), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text + "\n")
    return path


def verify(outdir=None, tag=""):
    outdir = outdir or OUTDIR
    path = os.path.join(outdir, "BANDMARGIN-%s%s.json" % (CUTOFF, tag))
    if not os.path.exists(path):
        return ["no published face at %s" % path]
    with io.open(path, encoding="utf-8") as fh:
        got = json.load(fh)
    fresh = run(save=False)
    problems = []
    for key in sorted(set(got) | set(fresh)):
        if key == "generated":
            continue
        if got.get(key) != fresh.get(key):
            problems.append("%s does not re-derive" % key)
    return problems


# ------------------------------------------------------------------ selftest
def _leg(ok, name, detail=None):
    return {"leg": name, "ok": bool(ok), "detail": detail}


def _rec(donor, t_side, own, moved, t_max_end=None, index=0):
    return {"donor_p95": donor, "t_side": t_side, "t_max_end": t_side if t_max_end is None
            else t_max_end, "own_p95": own, "actual_moved": moved, "index": index}


def selftest():
    legs = []

    # --- the clearance, and what "clearing it" means
    legs.append(_leg(abs(margin(2.2, 2.0) - 0.1) <= TOL, "margin = donor/t - 1", margin(2.2, 2.0)))
    legs.append(_leg(margin(2.0, 2.0) == 0.0, "a donor exactly on the threshold has zero margin"))
    legs.append(_leg(margin(2.0, None) is None and margin(None, 2.0) is None,
                     "an absent donor or threshold has no margin"))
    legs.append(_leg(margin(2.0, 0.0) is None, "a zero threshold has no margin (not infinity)"))
    r = _rec(2.2, 2.0, 1.5, True)
    legs.append(_leg(buffer_pred("t_side", False, r, 0.0) is True, "b=0 flags a donor above t"))
    legs.append(_leg(buffer_pred("t_side", False, r, 0.1) is False,
                     "a donor sitting exactly at t*(1+b) is NOT clearance (strict >)"))
    legs.append(_leg(buffer_pred("t_side", False, r, 0.09) is True,
                     "a hair under the buffered line still flags"))
    legs.append(_leg(buffer_pred("t_side", False, _rec(2.0, 2.0, 1.5, True), 0.0) is False,
                     "a donor exactly on t with b=0 does not flag"))

    # --- raising b can only remove predictions: the curve is a ladder, not a random walk
    recs = [_rec(2.30, 2.0, 1.5, True, index=0),      # margin 0.150 move
            _rec(2.05, 2.0, 1.5, False, index=1),     # margin 0.025 non-move
            _rec(2.60, 2.0, 2.2, False, index=2)]     # margin 0.300 non-move, own end already cleared
    picked = [confusion(recs, "t_side", False, b)["predicted"]
              for b in (0.0, 0.02, 0.03, 0.14, 0.16)]
    legs.append(_leg(picked == [3, 3, 2, 2, 1],
                     "predictions are non-increasing in b and drop at the observed margins", picked))
    legs.append(_leg(confusion(recs, "t_side", False, 0.31)["fp"] == 0,
                     "a buffer above every non-move margin clears the false positives"))
    legs.append(_leg(confusion(recs, "t_side", False, 0.31)["tp"] == 0,
                     "and it clears the move too -- precision is undefined, not perfect",
                     confusion(recs, "t_side", False, 0.31)))

    # --- precision is NOT monotone in b even though the prediction count is
    ladder = [{"b": 0.0, "predicted": 3, "tp": 1, "fp": 2, "precision": 1 / 3.0},
              {"b": 0.05, "predicted": 2, "tp": 1, "fp": 1, "precision": 0.5},
              {"b": 0.2, "predicted": 1, "tp": 0, "fp": 1, "precision": 0.0}]
    legs.append(_leg(ladder[0]["precision"] < ladder[1]["precision"]
                     and ladder[1]["precision"] > ladder[2]["precision"],
                     "precision can rise then fall as the ladder climbs (it has a peak, not a "
                     "monotone trend)"))
    legs.append(_leg(confusion(recs, "t_side", False, 0.0)["recall"] == 1.0,
                     "recall is 1 only while every move is still flagged",
                     confusion(recs, "t_side", False, 0.0)["recall"]))
    legs.append(_leg(confusion(recs, "t_side", False, 0.16)["recall"] < 1.0,
                     "a buffer inside the move's margin already loses recall"))
    empty = confusion([], "t_side", False, 0.0)
    legs.append(_leg(empty["precision"] is None and empty["recall"] is None,
                     "an empty population has undefined precision (not 0.0)", empty))
    legs.append(_leg(empty["exact"] is False, "an empty population is never exact"))

    # --- the guard is not a buffer: it keys on the row's own end, at any b
    legs.append(_leg(buffer_pred("t_side", True, _rec(2.60, 2.0, 2.2, False), 0.0) is False,
                     "the guard drops a donor far above t when the row's own end is above t"))
    legs.append(_leg(buffer_pred("t_side", True, _rec(2.10, 2.0, 1.5, True), 0.0) is True,
                     "the guard keeps a donor just above t when its own end is below t"))
    legs.append(_leg(buffer_pred("t_side", True, _rec(2.60, 2.0, 2.0, False), 0.0) is False,
                     "own_p95 == t is not a rejection the donor can take away (strict <)"))

    # --- the breakpoint grid carries every observed margin, so the curve is exact
    bps = breakpoints(recs)
    legs.append(_leg(all(any(abs(b - m) <= TOL for b in bps)
                         for m in [0.150, 0.025, 0.300]),
                     "every observed margin is a breakpoint", bps))
    legs.append(_leg(bps == sorted(bps) and len(bps) == len(set(bps)),
                     "breakpoints are sorted and unique"))
    zero_bp = [b for b in bps if abs(b) <= TOL]
    legs.append(_leg(len(zero_bp) >= 1, "b=0 is in the grid (the unbuffered reading is published)"))
    neg = breakpoints([_rec(1.5, 2.0, 1.5, False)])          # clearance -0.25
    legs.append(_leg(all(b >= 0 for b in neg),
                     "a negative clearance is not swept (a buffer cannot be negative)", neg))

    # --- separation: one non-move clearing more than a move means no buffer can help
    interleaved = [_rec(2.05, 2.0, 1.5, True, index=0),    # margin 0.025 move
                   _rec(2.60, 2.0, 2.2, False, index=1)]   # margin 0.300 non-move, own end above t
    sep_i = separation(interleaved)
    legs.append(_leg(sep_i["interleaved"] is True and sep_i["separable"] is False,
                     "a non-move clearing more than the closest move is not separable", sep_i))
    separated = [_rec(2.30, 2.0, 1.5, True, index=0),      # margin 0.150 move
                 _rec(2.05, 2.0, 1.5, False, index=1)]     # margin 0.025 non-move
    sep_s = separation(separated)
    legs.append(_leg(sep_s["separable"] is True,
                     "a non-move below every move is separable", sep_s))
    legs.append(_leg(abs(sep_s["gap_positive_minus_false"] - 0.125) < 1e-9,
                     "the gap is the closest move margin minus the nearest non-move margin",
                     sep_s["gap_positive_minus_false"]))
    legs.append(_leg(abs(sep_s["largest_false_positive_margin"] - 0.025) < 1e-9,
                     "separability binds on the LARGEST non-move, not the nearest one",
                     sep_s["largest_false_positive_margin"]))
    seps = curve(separated, "t_side", False, breakpoints(separated))
    sums_s = curve_summary(seps)
    legs.append(_leg(sums_s["reaches_exact"] is True,
                     "a separated population is reachable by some buffer", sums_s["exact_b"]))
    legs.append(_leg(all(b > 0.025 - TOL for b in sums_s["exact_b"]),
                     "and every exact b clears the non-move's 0.025", sums_s["exact_b"]))
    cur_i = curve(interleaved, "t_side", False, breakpoints(interleaved))
    sums_i = curve_summary(cur_i)
    legs.append(_leg(sums_i["reaches_exact"] is False,
                     "a non-separable population is reachable by NO buffer", sums_i["exact_b"]))
    legs.append(_leg(sums_i["best_precision"] == 0.5 and abs(sums_i["best_b"]) <= TOL,
                     "its best reading is the unbuffered one at precision 0.5 (half the flags are "
                     "the non-move)", [sums_i["best_precision"], sums_i["best_b"]]))
    legs.append(_leg(abs(sums_i["first_b_with_no_true_positive"] - 0.025) <= TOL,
                     "the move dies exactly at its own margin, not above it (strict >)",
                     sums_i["first_b_with_no_true_positive"]))

    # --- verdict totality
    v, _ = verdict_of([], {}, {}, {})
    legs.append(_leg(v == "undefined_population", "an empty population is its own verdict", v))
    nomove = [_rec(2.3, 2.0, 1.5, False)]
    v, _ = verdict_of(nomove, {}, {}, confusion(nomove, "t_side", True, 0.0))
    legs.append(_leg(v == "no_moves_to_protect", "zero positives is not a buffer result", v))
    sums_empty = {k: curve_summary(curve(interleaved, *r, breakpoints(interleaved)))
                  for k, r in (("single_side", ("t_side", False)),
                               ("single_maxend", ("t_max_end", False)))}
    guard_bad = {"tp": 1, "fp": 1, "fn": 0, "predicted": 2}
    v, _ = verdict_of(interleaved, sums_empty, sep_i, guard_bad)
    legs.append(_leg(v == "guard_alone_is_not_exact",
                     "a guard with its own false positive outranks the buffer reading", v))
    guard_ok = confusion(interleaved, "t_side", True, 0.0)
    v, _ = verdict_of(interleaved, sums_empty, sep_i, guard_ok)
    legs.append(_leg(v == "buffer_cannot_buy_precision_itself",
                     "when the guard is exact and no b is, the buffer cannot buy precision", v))

    ok = all(l["ok"] for l in legs)
    print("selftest %d/%d %s" % (sum(1 for l in legs if l["ok"]), len(legs), "OK" if ok else "FAIL"))
    for l in legs:
        if not l["ok"]:
            print("  FAIL", l["leg"], l["detail"])
    return 0 if ok else 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "run"
    if cmd == "selftest":
        return selftest()
    if cmd == "verify":
        problems = verify()
        if problems:
            print("verify %d problem(s)" % len(problems))
            for p in problems:
                print("  -", p)
            return 1
        print("verify 0 problems")
        return 0
    if cmd == "run":
        face = run()
        s = face["summary"]
        print("%s: %s" % (face["verdict"], face["verdict_reason"]))
        for name, _f, _g in RULES:
            r = s["rules"][name]
            print("  %-15s b=0 tp/fp %d/%d p=%s | best p=%s at b=%s | exact b=%s"
                  % (name, r["at_zero"]["tp"], r["at_zero"]["fp"],
                     ("%.3f" % r["at_zero"]["precision"]) if r["at_zero"]["precision"] is not None
                     else "n/a",
                     ("%.3f" % r["best_precision"]) if r["best_precision"] is not None else "n/a",
                     ("%.4f" % r["best_b"]) if r["best_b"] is not None else "n/a",
                     r["exact_b"] if r["exact_b"] else "none"))
        sep = s["separation"]
        print("  nearest non-move margin %s vs nearest move %s (gap %s), interleaved=%s"
              % (sep["nearest_false_positive_margin"], sep["nearest_true_positive_margin"],
                 sep["gap_positive_minus_false"], sep["interleaved"]))
        return 0
    print("usage: e267_screen_buffer_margin.py [run|verify|selftest]")
    return 2


if __name__ == "__main__":
    sys.exit(main())