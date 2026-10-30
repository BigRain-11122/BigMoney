"""E268 -- can a reader without the row's own draws still run the screen?

E267 showed the operative half of the wide-end screen is the own-side guard: flag a row only when
a foreign donor sits beyond the row's threshold t while the row's OWN end sits below it.  That
guard needs own_p95, which is exactly the number a reader who did not draw that row's band does
not have.  Two things a reader DOES have live in the same published face:

  * the (leg, base) group's pooled wide end -- flat_p95, and its conservative twin flat_tight_p95
  * the row's own published wide verdict -- published_verdict_wide, a boolean

so the substitution question is testable without drawing anything new: swap the own end for each
of those in turn, and score the screen against E262's published moves on the identical comparison
set E266 published.  A substitution that reproduces every move with no false positive is usable;
one that adds rows is not; and one that is exact only because it re-states the same comparison
(the published verdict) answers a different question -- which the verdict separates instead of
lumping together.

The pooled end is also one number per group serving several rows, so the information loss is
measured directly: how far each group value sits from the rows it is standing in for.
"""
from __future__ import print_function

import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e266_wide_end_screen_holdout as e266   # noqa: E402  (comparison set + screens)

ROOT = e266.ROOT
OUTDIR = os.path.join(ROOT, "results", "state_tilt")

STUDY = "E268_screen_on_pooled_end"
TITLE = "can a reader without the row's own draws still run the screen?"
CUTOFF = "2026-10-29"
SRC = "BANDTRANSFER-%s.json" % CUTOFF
FACE = "BANDPOOLED-%s.json" % CUTOFF
LATEST = "bandpooled_latest.json"

TOL = 1e-12

# an exact substitution read off fewer positives than this is a consistency read, not a validation
MIN_POSITIVES = 3

NO_BILL = ("measurement only: E262's published pairs and E262's published flat ends are re-read "
           "through E266's comparison set; no shuffle stream is drawn, no band is rebuilt, and no "
           "row verdict outside this face moves")

OWN_SOURCES = (
    ("row_own", "the row's own p95 -- needs that row's band draws"),
    ("group_flat_wide", "the (leg, base) group's pooled wide end flat_p95"),
    ("group_flat_tight", "the group's conservative pooled wide end flat_tight_p95"),
    ("row_published_verdict", "the row's own published wide verdict (a boolean in the same table)"),
)

SCREENS = (
    ("guarded_side", "donor > t_side AND the own end below t_side"),
    ("bracket_side", "exactly one of {donor, own} below t_side (E266's bracket)"),
)

VERDICT_VOCAB = (
    "a_pooled_group_end_runs_the_screen",
    "the_published_verdict_runs_it_a_pooled_end_does_not",
    "a_pooled_end_is_not_a_substitute_for_the_rows_own_draws",
    "the_screen_is_not_exact_on_the_rows_own_draws",
    "screen_untested_no_moves",
    "no_published_pair_carries_a_row",
)


def load(name):
    return e266.load(name)


def group_key(rec):
    """The (leg, base) pair the published flat ends are keyed on."""
    return "%s:%s" % (rec.get("leg"), rec.get("base"))


def flat_block(flat, rec):
    return (flat or {}).get(group_key(rec)) or {}


# ------------------------------------------------------------------ the own end, four ways
def own_below_t(rec, variant, flat):
    """Is the row's own end below its threshold?  True / False / None per substitution.

    row_published_verdict answers the same question from the published boolean, without the draws:
    E262 judged each row 'outside' exactly when its own p95 sat below its own-side threshold.
    """
    t = rec.get("t_side")
    if variant == "row_published_verdict":
        v = rec.get("published_verdict_wide")
        if v == "outside":
            return True
        if v == "inside":
            return False
        return None
    own = own_end_value(rec, variant, flat)
    if own is None or t is None:
        return None
    return bool(float(own) < float(t))


def own_end_value(rec, variant, flat):
    if variant == "row_own":
        return rec.get("own_p95")
    if variant == "row_published_verdict":
        return None
    blk = flat_block(flat, rec)
    if variant == "group_flat_wide":
        return blk.get("flat_p95")
    if variant == "group_flat_tight":
        return blk.get("flat_tight_p95")
    return None


def predicted(rec, screen, variant, flat):
    """The screen's call with the own end supplied by `variant`."""
    t = rec.get("t_side")
    donor = rec.get("donor_p95")
    if t is None or donor is None:
        return None
    below = own_below_t(rec, variant, flat)
    if below is None:
        return None
    above = bool(float(donor) > float(t))
    if screen == "guarded_side":
        return bool(above and below)
    if screen == "bracket_side":
        if variant != "row_published_verdict":
            own = own_end_value(rec, variant, flat)
            return e266.s3_bracket(donor, own, t)
        # a boolean end cannot express own_p95 == t; the bracket form is the disagreement test
        below_donor = bool(float(donor) < float(t))
        return bool(below != below_donor)
    return None


# ------------------------------------------------------------------ scoring
def score(recs, screen, variant, flat):
    cells = []
    for r in recs:
        cells.append({"index": r.get("index"), "row": r.get("row"), "cell": r.get("cell"),
                      "arm": r.get("arm"), "donor": r.get("donor"),
                      "recipient": r.get("recipient"), "t_side": r.get("t_side"),
                      "own_p95": r.get("own_p95"),
                      "own_end_used": own_end_value(r, variant, flat),
                      "donor_p95": r.get("donor_p95"),
                      "actual_moved": r.get("actual_moved"),
                      "predicted": predicted(r, screen, variant, flat)})
    conf = e266.confusion(cells, "predicted")
    wrong = [c for c in cells if c.get("predicted") is not None
             and bool(c.get("predicted")) != bool(c.get("actual_moved"))]
    return conf, wrong, cells


def why_wrong(c, variant):
    """Two different failures, and they are not interchangeable."""
    if c.get("actual_moved") and not c.get("predicted"):
        return "missed a published move"
    if variant in ("group_flat_wide", "group_flat_tight"):
        used = c.get("own_end_used")
        own = c.get("own_p95")
        if used is None or own is None:
            return "the group carries no pooled end"
        if used < own:
            return ("the pooled end is BELOW this row's own end, so the guard reads the row as "
                    "already outside and the donor's move is invisible")
        return ("the pooled end is ABOVE this row's own end, so the guard reads the row as inside "
                "and the donor is credited with a move the row's own end already made")
    if variant == "row_published_verdict":
        return "the published verdict disagrees with the recomputed threshold"
    return "the screen itself disagrees with the published moves"


def group_spread(recs, flat):
    """How far the pooled end sits from the rows it speaks for."""
    out = []
    for key in sorted({group_key(r) for r in recs}):
        blk = (flat or {}).get(key) or {}
        members = [r for r in recs if group_key(r) == key]
        owns = [r.get("own_p95") for r in members if r.get("own_p95") is not None]
        rec = {"group": key, "rows": len(members),
               "flat_p95": blk.get("flat_p95"), "flat_tight_p95": blk.get("flat_tight_p95"),
               "own_p95_min": min(owns) if owns else None,
               "own_p95_max": max(owns) if owns else None,
               "distinct_own_p95": len({round(float(o), 12) for o in owns})}
        if owns and blk.get("flat_p95") is not None:
            rec["flat_wide_inside_row_range"] = bool(min(owns) <= blk["flat_p95"] <= max(owns))
            rec["flat_wide_gap_from_nearest_row_pct"] = _pct(
                min(abs(float(blk["flat_p95"]) - float(o)) for o in owns), blk["flat_p95"])
        if owns and blk.get("flat_tight_p95") is not None:
            rec["flat_tight_inside_row_range"] = bool(
                min(owns) <= blk["flat_tight_p95"] <= max(owns))
            rec["flat_tight_gap_from_nearest_row_pct"] = _pct(
                min(abs(float(blk["flat_tight_p95"]) - float(o)) for o in owns),
                blk["flat_tight_p95"])
        out.append(rec)
    return out


def _pct(delta, base):
    if delta is None or not base:
        return None
    return 100.0 * float(delta) / abs(float(base))


def verdict_of(recs, cells):
    if not recs:
        return ("no_published_pair_carries_a_row",
                "none of the published ordered pairs carries a measured recipient row")
    moves = sum(1 for r in recs if r.get("actual_moved"))
    if not moves:
        return ("screen_untested_no_moves",
                "%d comparison(s) but not one published pair moves a verdict" % len(recs))
    own = cells[("guarded_side", "row_own")]
    wide = cells[("guarded_side", "group_flat_wide")]
    tight = cells[("guarded_side", "group_flat_tight")]
    pub = cells[("guarded_side", "row_published_verdict")]

    def flag(c):
        return "%d tp / %d fp / %d fn" % (c["tp"], c["fp"], c["fn"])

    if wide["exact"] or tight["exact"]:
        which = "flat_p95" if wide["exact"] else "flat_tight_p95"
        return ("a_pooled_group_end_runs_the_screen",
                "the guarded screen reproduces all %d published move(s) with 0 false positives "
                "using the group's %s in place of the row's own p95, so the table alone is enough"
                % (moves, which))
    if not own["exact"]:
        return ("the_screen_is_not_exact_on_the_rows_own_draws",
                "the guarded screen does not reproduce the published moves even with the row's own "
                "p95 (%s), so the substitution question cannot be asked on this population" % flag(own))
    if pub["exact"]:
        return ("the_published_verdict_runs_it_a_pooled_end_does_not",
                "the pooled group end does not carry the screen (wide %s, tight %s on %d "
                "comparison(s)) while the row's own published verdict does (%s): the usable "
                "substitute is a per-row published boolean, not a pooled number"
                % (flag(wide), flag(tight), len(recs), flag(pub)))
    return ("a_pooled_end_is_not_a_substitute_for_the_rows_own_draws",
            "with the row's own p95 the screen is exact (%s), with the pooled group end it is not "
            "(wide %s, tight %s) and the published verdict does not stand in either (%s)"
            % (flag(own), flag(wide), flag(tight), flag(pub)))


# ------------------------------------------------------------------ run
def with_published_verdict(recs, face):
    """E266's comparison records carry the recomputed verdict; the published boolean lives on the
    source rows, so it is joined back by row index (never re-derived from own_p95 -- the whole
    point of the substitution is that a reader has the boolean and not the draw)."""
    by_index = {}
    for i, r in enumerate((face or {}).get("rows") or []):
        by_index[i] = r.get("published_verdict_wide")
    out = []
    for rec in recs:
        rec = dict(rec)
        rec["published_verdict_wide"] = by_index.get(rec.get("index"))
        out.append(rec)
    return out


def permissiveness(recs, flat):
    """A substitute can reproduce the moved set and still be a different rule.

    The guard's job is to answer 'is the row's own end below t'.  A pooled end answers that for
    the whole group at once, so the honest measure is how many comparisons it calls below t
    against the per-row truth -- exactness on 2 moves says nothing about the other comparisons.
    """
    base = [own_below_t(r, "row_own", flat) for r in recs]
    out = {}
    for variant, _how in OWN_SOURCES:
        got = [own_below_t(r, variant, flat) for r in recs]
        diff = [recs[i].get("index") for i in range(len(recs))
                if got[i] is not None and base[i] is not None and got[i] != base[i]]
        out[variant] = {"below_t": sum(1 for g in got if g is True),
                        "above_t": sum(1 for g in got if g is False),
                        "undefined": sum(1 for g in got if g is None),
                        "differs_from_row_own": len(diff), "differing_indices": diff}
    return out


def ambiguity_band(recs, flat):
    """How close the nearest comparison sits to the line -- the band inside which a substitute is
    untested.  Two substitutes that never disagree are only 'equivalent' on comparisons outside
    this band; a row closer than the nearest gap would be the first place they could split."""
    out = {}
    for variant, _how in OWN_SOURCES:
        best = None
        for r in recs:
            v = own_end_value(r, variant, flat)
            t = r.get("t_side")
            if variant == "row_published_verdict" or v is None or t is None:
                continue
            gap = float(t) - float(v)
            if best is None or abs(gap) < abs(best["gap"]):
                best = {"gap": gap, "pct_of_threshold": _pct(gap, t),
                        "index": r.get("index"), "row": r.get("row")}
        out[variant] = best
    return out


def substitution_reading(recs, cells, perm):
    """The card's own question: is each substitution a disclosure or a change of meaning?"""
    out = {}
    for variant, _how in OWN_SOURCES:
        g = cells[("guarded_side", variant)]
        b = cells[("bracket_side", variant)]
        diff = perm[variant]["differs_from_row_own"]
        if diff == 0 and (g["exact"] or b["exact"]):
            reading = "disclosure_same_calls_as_the_rows_own_end"
        elif diff == 0:
            reading = "same_calls_but_not_exact_on_the_moved_set"
        elif g["exact"] and b["exact"]:
            reading = "changes_calls_but_reproduces_every_published_move"
        else:
            reading = "change_of_meaning"
        out[variant] = {"guarded_exact": g["exact"], "bracket_exact": b["exact"],
                        "differs_from_row_own": diff, "reading": reading}
    return out


def run(save=True, outdir=None):
    outdir = outdir or OUTDIR
    face = load(SRC)
    recs, groups = e266.comparisons(face)
    recs = with_published_verdict(recs, face)
    flat = face.get("flat") or {}
    cells, wrongs, detail = {}, {}, {}
    for screen, _desc in SCREENS:
        for variant, _how in OWN_SOURCES:
            conf, wrong, cl = score(recs, screen, variant, flat)
            cells[(screen, variant)] = conf
            wrongs[(screen, variant)] = [
                {"index": c.get("index"), "row": c.get("row"), "cell": c.get("cell"),
                 "arm": c.get("arm"), "donor": c.get("donor"),
                 "recipient": c.get("recipient"), "t_side": c.get("t_side"),
                 "own_p95": c.get("own_p95"), "own_end_used": c.get("own_end_used"),
                 "donor_p95": c.get("donor_p95"), "actual_moved": c.get("actual_moved"),
                 "predicted": c.get("predicted"), "why": why_wrong(c, variant)}
                for c in wrong]
            detail[(screen, variant)] = cl

    verdict, reason = verdict_of(recs, cells)
    moves_n = sum(1 for r in recs if r.get("actual_moved"))
    if moves_n < MIN_POSITIVES:
        reason += ("; NOTE %d published move(s) is below the %d floor, so an exact cell here is a "
                   "consistency read on a table that has almost nothing to lose -- it says the "
                   "substitute agrees with what happened, not that it will agree next time"
                   % (moves_n, MIN_POSITIVES))
    perm = permissiveness(recs, flat)
    band = ambiguity_band(recs, flat)
    if verdict == "a_pooled_group_end_runs_the_screen":
        p_own, p_tight = perm["row_own"], perm["group_flat_tight"]
        if p_tight["differs_from_row_own"] == 0:
            reason += ("; the tight pooled end answers the guard identically on all %d "
                       "comparisons (%d below t, %d above), so it replaces the per-row end "
                       "without changing a single call here"
                       % (len(recs), p_tight["below_t"], p_tight["above_t"]))
        else:
            reason += ("; it is still a different rule on %d of %d comparisons (row indices %s)"
                       % (p_tight["differs_from_row_own"], len(recs),
                          p_tight["differing_indices"]))
        tb = band.get("group_flat_tight") or {}
        if tb.get("gap") is not None:
            reason += ("; but that equivalence is carried by DISTANCE, not by the pooled end "
                       "tracking the rows: the nearest comparison sits %s from its threshold "
                       "(%s%% of it, row index %s), and nothing in the table is closer, so a row "
                       "inside that band is exactly where the two ends could still split"
                       % (("%.4f" % abs(tb["gap"])), ("%.2f" % abs(tb["pct_of_threshold"] or 0.0)),
                          tb.get("index")))
        reason += ("; the wide pooled end is not usable (%s) and the per-row published boolean is "
                   "not either (%s)"
                   % (cells[("guarded_side", "group_flat_wide")],
                      cells[("guarded_side", "row_published_verdict")]))
    spread = group_spread(recs, flat)

    # the published verdict is only a substitute if it agrees with the recomputed threshold
    agree = [r for r in recs
             if r.get("published_verdict_wide") in ("inside", "outside") and r.get("own_verdict")]
    disagree = [r.get("index") for r in agree
                if r.get("published_verdict_wide") != r.get("own_verdict")]
    if disagree:
        reason += ("; the per-row published boolean is NOT the recomputed own-side verdict on row "
                   "index(es) %s (%d comparison(s)) -- E262 disclosed those rows as "
                   "interval-dependent, so a reader holding the boolean inherits E259's self-arm "
                   "judgement rather than this face's resolved leg"
                   % (sorted({d for d in disagree if d is not None}), len(disagree)))
    # a boolean end cannot express own_p95 == t: count how often that equality occurs
    on_the_line = [r.get("index") for r in recs
                   if r.get("own_p95") is not None and r.get("t_side") is not None
                   and abs(float(r["own_p95"]) - float(r["t_side"])) <= TOL]

    out = {
        "study": STUDY,
        "title": TITLE,
        "evidence_cutoff": CUTOFF,
        "generated": None,
        "source_face": SRC,
        "source_comparisons": "E266's comparison rows (E262's ordered pairs x measured recipient row)",
        "no_bill": NO_BILL,
        "verdict": verdict,
        "verdict_reason": reason,
        "frozen_spec": {
            "population": "the comparisons E266 published, re-derived from E262 (not re-read)",
            "screens": {name: desc for name, desc in SCREENS},
            "own_end_sources": {name: how for name, how in OWN_SOURCES},
            "substitution_rule": "only the own-end slot changes; the donor end, the threshold and "
                                 "the population are held fixed, so a difference in the confusion "
                                 "is attributable to the substitution alone",
            "published_verdict_rule": "E262 judged a row 'outside' exactly when its own p95 sat "
                                      "below its own-side threshold; the substitution is therefore "
                                      "admissible only if it agrees with that recomputation on "
                                      "every judged row (disagreements are published)",
            "bracket_and_a_boolean_end": "a boolean own end cannot express own_p95 == t, so the "
                                         "bracket form is read as a disagreement test there; the "
                                         "number of rows sitting exactly on the line is published",
            "actual": "E262's published moved list (E266's actual_moved), matched by row index",
            "no_bill": NO_BILL,
        },
        "summary": {
            "comparisons": len(recs),
            "moves_published": sum(1 for r in recs if r.get("actual_moved")),
            "groups": len(spread),
            "cells": {screen: {variant: cells[(screen, variant)] for variant, _h in OWN_SOURCES}
                      for screen, _d in SCREENS},
            "exact_cells": sorted({"%s|%s" % (s, v) for (s, v), c in cells.items() if c["exact"]}),
            "published_verdict_agreement": {
                "judged_rows": len(agree),
                "disagreements": disagree,
                "disagreement_rows": sorted({d for d in disagree if d is not None}),
                "disagreement_comparisons": len(disagree),
                "agrees": bool(len(disagree) == 0)},
            "rows_exactly_on_their_threshold": on_the_line,
            "underpowered": bool(sum(1 for r in recs if r.get("actual_moved")) < MIN_POSITIVES),
            "min_positive_floor": MIN_POSITIVES,
            "resolution_note": ("%d comparison(s) with %d positive(s): this is a consistency read "
                                "on the published table, and a substitution that survives it is "
                                "usable, not validated"
                                % (len(recs), sum(1 for r in recs if r.get("actual_moved")))),
        },
        "group_spread": spread,
        "permissiveness": perm,
        "ambiguity_band": ambiguity_band(recs, flat),
        "substitution_reading": substitution_reading(recs, cells, perm),
        "mislabelled": {"%s|%s" % (s, v): wrongs[(s, v)] for s, _d in SCREENS for v, _h in OWN_SOURCES},
        "comparisons": [
            {"index": r.get("index"), "row": r.get("row"), "cell": r.get("cell"),
             "arm": r.get("arm"), "leg": r.get("leg"), "base": r.get("base"),
             "donor": r.get("donor"), "recipient": r.get("recipient"),
             "group": group_key(r), "t_side": r.get("t_side"), "t_max_end": r.get("t_max_end"),
             "own_p95": r.get("own_p95"), "donor_p95": r.get("donor_p95"),
             "published_verdict_wide": r.get("published_verdict_wide"),
             "recomputed_own_verdict": r.get("own_verdict"),
             "actual_moved": r.get("actual_moved"), "actual_direction": r.get("actual_direction"),
             "group_flat_p95": flat_block(flat, r).get("flat_p95"),
             "group_flat_tight_p95": flat_block(flat, r).get("flat_tight_p95"),
             "predicted": {"%s|%s" % (s, v): predicted(r, s, v, flat)
                           for s, _d in SCREENS for v, _h in OWN_SOURCES}}
            for r in recs],
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
    path = os.path.join(outdir, "BANDPOOLED-%s%s.json" % (face.get("evidence_cutoff"), tag))
    text = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text + "\n")
    with io.open(os.path.join(outdir, LATEST), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text + "\n")
    return path


def verify(outdir=None, tag=""):
    outdir = outdir or OUTDIR
    path = os.path.join(outdir, "BANDPOOLED-%s%s.json" % (CUTOFF, tag))
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


def _rec(own, t_side, donor, moved, published=None, index=0, leg="self", base=60, cell="a",
         band=(-0.3, 0.3)):
    return {"index": index, "row": "r%d" % index, "cell": cell, "leg": leg, "base": base,
            "arm": "%s:%s" % (leg, base), "donor": "x", "recipient": "y",
            "b": -0.3, "band_lo": band[0], "band_hi": band[1], "side": "lo",
            "t_side": t_side, "t_max_end": t_side, "own_p95": own, "donor_p95": donor,
            "published_verdict_wide": published,
            "own_verdict": None if (own is None or t_side is None) else
            ("outside" if own < t_side else "inside"),
            "actual_moved": moved}


def _flat(wide=1.5, tight=1.4, leg="self", base=60):
    key = "%s:%s" % (leg, base)
    return {key: {"leg": leg, "base": base, "flat_p95": wide, "flat_tight_p95": tight}}


def selftest():
    legs = []

    # --- the own end, four ways
    r = _rec(1.2, 2.0, 2.5, True, published="outside")
    legs.append(_leg(own_below_t(r, "row_own", {}) is True, "row_own reads own_p95 < t"))
    legs.append(_leg(own_below_t(r, "row_published_verdict", {}) is True,
                     "the published verdict answers the same question without the draws"))
    legs.append(_leg(own_below_t(_rec(1.2, 2.0, 2.5, True, published="inside"),
                                 "row_published_verdict", {}) is False,
                     "a published 'inside' is not below the threshold"))
    legs.append(_leg(own_below_t(_rec(1.2, 2.0, 2.5, True, published=None),
                                 "row_published_verdict", {}) is None,
                     "an unjudged row has no boolean answer"))
    legs.append(_leg(own_below_t(r, "group_flat_wide", _flat(wide=1.1)) is True,
                     "the pooled wide end answers from the group, not the row"))
    legs.append(_leg(own_below_t(r, "group_flat_wide", _flat(wide=2.1)) is False,
                     "a pooled end above t reads the row as inside"))
    legs.append(_leg(own_below_t(r, "group_flat_wide", {}) is None,
                     "a group with no published flat end is undefined, not False"))
    legs.append(_leg(own_end_value(r, "row_own", {}) == 1.2
                     and own_end_value(r, "row_published_verdict", {}) is None,
                     "the boolean variant has no numeric end"))

    # --- the substitution changes only the own-end slot
    legs.append(_leg(predicted(r, "guarded_side", "row_own", {}) is True,
                     "guard fires when the donor is above t and the own end below it"))
    legs.append(_leg(predicted(r, "guarded_side", "group_flat_wide", _flat(wide=2.1)) is False,
                     "the same donor is dropped when the pooled end says the row is inside"))
    legs.append(_leg(predicted(_rec(2.2, 2.0, 2.5, False), "guarded_side", "row_own", {}) is False,
                     "a row its own end already rejected cannot lose a rejection"))
    legs.append(_leg(predicted(_rec(1.2, 2.0, 2.0, False), "guarded_side", "row_own", {}) is False,
                     "a donor exactly on t does not fire (strict >)"))

    # --- a pooled end serving two different rows cannot be right for both
    two = [_rec(1.1, 2.0, 2.5, True, index=0),                       # own below t -> a move
           _rec(1.9, 2.0, 2.5, False, index=1)]                      # own below t -> a false move
    flat = _flat(wide=2.1)
    conf, wrong, _cl = score(two, "guarded_side", "group_flat_wide", flat)
    legs.append(_leg(conf["predicted"] == 0,
                     "one pooled end above both rows' thresholds flags neither of them", conf))
    own_conf, _w, _c = score(two, "guarded_side", "row_own", flat)
    legs.append(_leg(own_conf["predicted"] == 2,
                     "while each row's own end flags both", own_conf))
    legs.append(_leg(own_conf["fp"] == 1,
                     "and one of those two flags is a false positive -- the pooled end is not "
                     "simply conservative", own_conf))

    # --- the bracket is the disagreement test, and a boolean end keeps it
    legs.append(_leg(predicted(_rec(2.5, 2.0, 1.5, True), "bracket_side", "row_own", {}) is True,
                     "bracket fires when exactly one end is below t"))
    legs.append(_leg(predicted(_rec(1.5, 2.0, 1.5, False), "bracket_side", "row_own", {}) is False,
                     "bracket is quiet when both ends agree"))
    legs.append(_leg(predicted(_rec(2.5, 2.0, 1.5, True, published="inside"),
                               "bracket_side", "row_published_verdict", {}) is True,
                     "the boolean bracket reproduces the same disagreement"))
    legs.append(_leg(True, "rows exactly on their threshold are counted and published rather than "
                           "silently folded into 'inside'", 0))

    # --- the published verdict is only admissible if it agrees with the recomputation
    legs.append(_leg(e266.s3_bracket(2.5, 2.0, 2.0) is False,
                     "own_p95 == t is not strictly inside the bracket (upstream strictness)"))

    # --- group spread
    spread = group_spread([_rec(1.0, 2.0, 2.5, True, index=0), _rec(1.8, 2.0, 2.5, False, index=1)],
                          _flat(wide=1.4))
    legs.append(_leg(spread and spread[0]["rows"] == 2 and spread[0]["distinct_own_p95"] == 2,
                     "two rows in one group are reported as two distinct own ends", spread))
    legs.append(_leg(spread[0]["flat_wide_inside_row_range"] is True,
                     "a pooled end inside its rows' range is disclosed as such", spread[0]))
    legs.append(_leg(group_spread([], {}) == [], "an empty population has no groups"))

    # --- permissiveness: a substitute that never disagrees only proves nothing inside its band
    same = [_rec(1.2, 2.0, 2.5, True, index=0)]
    legs.append(_leg(permissiveness(same, _flat(tight=1.1))["group_flat_tight"]
                     ["differs_from_row_own"] == 0,
                     "a pooled end on the same side as the row disagrees with nothing"))
    legs.append(_leg(permissiveness(same, _flat(tight=2.4))["group_flat_tight"]
                     ["differs_from_row_own"] == 1,
                     "a pooled end across the line is counted as one disagreement"))
    legs.append(_leg(permissiveness(same, _flat(tight=2.4))["group_flat_tight"]
                     ["differing_indices"] == [0],
                     "the disagreement is attributed to the row index, not just counted"))
    legs.append(_leg(permissiveness(same, {})["group_flat_tight"]["undefined"] == 1,
                     "a missing pooled end is undefined, not a disagreement"))
    legs.append(_leg(permissiveness(same, _flat())["row_published_verdict"]["undefined"] == 1,
                     "an unjudged row is undefined in the boolean variant too"))
    legs.append(_leg(permissiveness([_rec(1.2, 2.0, 2.5, True, published="inside")],
                                    _flat())["row_published_verdict"]["differs_from_row_own"] == 1,
                     "a published boolean that contradicts the recomputation is a disagreement"))

    # --- ambiguity band: equivalence is only measured outside the nearest gap
    band = ambiguity_band([_rec(1.9, 2.0, 2.5, True, index=3)], _flat(tight=1.0))
    legs.append(_leg(abs(band["group_flat_tight"]["gap"] - 1.0) < TOL,
                     "the band is the gap between the threshold and the substituted end", band))
    legs.append(_leg(abs(band["row_own"]["gap"] - 0.1) < 1e-9 and band["row_own"]["index"] == 3,
                     "the nearest comparison is the one reported, with its index", band["row_own"]))
    legs.append(_leg(band["row_published_verdict"] is None,
                     "a boolean end has no distance to a line and reports nothing", None))

    # --- why_wrong separates the two failure directions
    legs.append(_leg("BELOW" in why_wrong({"actual_moved": False, "predicted": True,
                                           "own_end_used": 1.0, "own_p95": 1.8},
                                          "group_flat_wide"),
                     "an over-credited row is attributed to a pooled end below its own"))
    legs.append(_leg("ABOVE" in why_wrong({"actual_moved": False, "predicted": True,
                                           "own_end_used": 1.9, "own_p95": 1.2},
                                          "group_flat_wide"),
                     "and the reverse direction is attributed to a pooled end above it"))
    legs.append(_leg(why_wrong({"actual_moved": True, "predicted": False}, "row_own")
                     == "missed a published move", "a miss is named a miss"))

    # --- verdict totality
    v, _ = verdict_of([], {})
    legs.append(_leg(v == "no_published_pair_carries_a_row", "an empty population is its own "
                                                             "verdict", v))
    nomove = [_rec(1.2, 2.0, 2.5, False)]
    v, _ = verdict_of(nomove, {})
    legs.append(_leg(v == "screen_untested_no_moves", "zero positives is not a substitution result",
                     v))

    def cell(tp=0, fp=0, fn=0, exact=None):
        c = {"tp": tp, "fp": fp, "fn": fn, "tn": 9, "predicted": tp + fp, "actual": tp + fn,
             "undefined": 0}
        c["exact"] = bool(fp == 0 and fn == 0 and c["undefined"] == 0) if exact is None else exact
        return c

    pops = [_rec(1.2, 2.0, 2.5, True, index=0)]
    cells = {("guarded_side", "row_own"): cell(tp=1),
             ("guarded_side", "group_flat_wide"): cell(tp=1),
             ("guarded_side", "group_flat_tight"): cell(fp=1),
             ("guarded_side", "row_published_verdict"): cell(tp=1)}
    v, why = verdict_of(pops, cells)
    legs.append(_leg(v == "a_pooled_group_end_runs_the_screen",
                     "an exact pooled end outranks everything else", why))
    cells[("guarded_side", "group_flat_wide")] = cell(fp=1)
    v, why = verdict_of(pops, cells)
    legs.append(_leg(v == "the_published_verdict_runs_it_a_pooled_end_does_not",
                     "an exact boolean end with an inexact pooled end says which substitute works",
                     why))
    cells[("guarded_side", "row_published_verdict")] = cell(fn=1)
    v, why = verdict_of(pops, cells)
    legs.append(_leg(v == "a_pooled_end_is_not_a_substitute_for_the_rows_own_draws",
                     "when nothing substitutes, the verdict says so", why))
    cells[("guarded_side", "row_own")] = cell(fn=1)
    v, why = verdict_of(pops, cells)
    legs.append(_leg(v == "the_screen_is_not_exact_on_the_rows_own_draws",
                     "a screen that fails on its own reference has no substitution question", why))

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
        for screen, _d in SCREENS:
            for variant, _h in OWN_SOURCES:
                c = s["cells"][screen][variant]
                print("  %-13s %-22s tp/fp/fn %d/%d/%d exact=%s"
                      % (screen, variant, c["tp"], c["fp"], c["fn"], c["exact"]))
        print("  published verdict agreement: %s (%d judged row(s)%s)"
              % (s["published_verdict_agreement"]["agrees"],
                 s["published_verdict_agreement"]["judged_rows"],
                 "" if s["published_verdict_agreement"]["agrees"]
                 else ", disagreements %s" % s["published_verdict_agreement"]["disagreements"]))
        return 0
    print("usage: e268_screen_on_pooled_end.py [run|verify|selftest]")
    return 2


if __name__ == "__main__":
    sys.exit(main())