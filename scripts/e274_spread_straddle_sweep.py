"""E274 -- can a row's own numbers say, in advance, whether an axis will move it?

E271 answered the donor question case by case: the donor axis is decisive only on rows whose flip
multiplier sits inside the p95 spread their (leg, base) group actually offers.  That is a
predictive screen, not a case report -- but it was scored on one axis only, against the moved set
one face happened to publish.

This face turns the screen into a family-wide census.  For every measured row in the BAND* family
it publishes, per axis, the row's flip multiplier, the multiplier range that axis actually offers
and a straddle flag; then it scores the flag against the moved sets the faces THEMSELVES already
published.  Three axes are scored because three faces publish both halves:

  wide_donor   range = the (leg, base) group's p95 spread (BANDTRANSFER arms)
               moved = BANDDONORCHOICE.summary.moved_row_indices  (E271's donor sweep)
  tight_p05    range = the same group's p05 spread (BANDTRANSFER arms)
               moved = BANDTIGHT.summary.rows_could_move_within_observed_p05_range
  top_ladder   range = the row's own published [multiplier_min, multiplier_max] (BANDTOPFLIP)
               moved = BANDTOPFLIP.summary.flipped_ids

The question is a reader's question: with two published numbers (m_flip, the range) can a reader
decide "do not borrow" versus "do not borrow from this cell" without re-running any sweep?  Two
error modes are published separately, because they mean opposite things: a moved row the screen
never flagged (the screen is unsafe) and a flagged row that never moved (the screen is useless).

No draws, no panel, no engine call: every number here is a function of published faces.

Modes: run | verify | selftest
"""

from __future__ import print_function

import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e262_p95_transfer_across_windows as e262  # noqa: E402  (OUTDIR, LEGS, BASE_COUNTS)

OUTDIR = e262.OUTDIR
CUTOFF = "2026-10-29"
SRC_TRANSFER = "BANDTRANSFER-%s.json" % CUTOFF
SRC_TIGHT = "BANDTIGHT-%s.json" % CUTOFF
SRC_DONOR = "BANDDONORCHOICE-%s.json" % CUTOFF
SRC_TOP = "BANDTOPFLIP-%s.json" % CUTOFF
FACE = "BANDSTRADDLESWEEP-%s.json" % CUTOFF
LATEST = "bandstraddlesweep_latest.json"

# A straddle is only tested away from the edge: a row whose flip multiplier sits within this
# share of the range width from an end is called "near edge" and disclosed separately, never
# counted as decided (E268's distance law, applied to the range instead of to a comparison).
EDGE_BAND_PCT = 5.0


# ------------------------------------------------------------------ io
def load(name):
    with io.open(os.path.join(OUTDIR, name), encoding="utf-8") as fh:
        return json.load(fh)


# ------------------------------------------------------------------ mechanism
def flip_multiplier(b, lo, hi):
    """The multiplier at which this row's verdict flips (E269's rule, unchanged)."""
    if b is None or lo is None or hi is None:
        return None
    if b < 0 and lo:
        return b / lo
    if b > 0 and hi:
        return b / hi
    return None


def edge_distance_pct(m, lo, hi):
    """How far the flip sits from the nearer end of the offered range, in percent of its width."""
    if m is None or lo is None or hi is None:
        return None
    width = hi - lo
    if not width:
        return None
    return min(m - lo, hi - m) / width * 100.0


def straddle(m, lo, hi, edge_band_pct=EDGE_BAND_PCT):
    """inside / near_edge / outside / untested -- never a bare boolean."""
    if m is None or lo is None or hi is None:
        return "untested"
    if hi <= lo:
        # a single-point (or inverted) range offers no spread, so no flag can be tested on it
        return "untested"
    if lo <= m <= hi:
        d = edge_distance_pct(m, lo, hi)
        if d is not None and d < edge_band_pct:
            return "near_edge"
        return "inside"
    return "outside"


# ------------------------------------------------------------------ group spreads
def group_ranges(arms, legs=None, base_counts=None):
    """{(leg, base): {"p05": (min,max,cells), "p95": (min,max,cells)}} from the arms block."""
    legs = legs or e262.LEGS
    base_counts = base_counts or e262.BASE_COUNTS
    out = {}
    for leg in legs:
        for base in base_counts:
            cells = [a for a in arms or []
                     if a.get("leg") == leg and a.get("base") == base and a.get("cell")]
            p05 = [(a["cell"], a.get("p05")) for a in cells if a.get("p05") is not None]
            p95 = [(a["cell"], a.get("p95")) for a in cells if a.get("p95") is not None]
            rec = {"cells": sorted(a["cell"] for a in cells)}
            if not rec["cells"]:
                continue
            for name, pairs in (("p05", p05), ("p95", p95)):
                if pairs:
                    lo = min(pairs, key=lambda p: p[1])
                    hi = max(pairs, key=lambda p: p[1])
                    rec[name] = {"min": lo[1], "max": hi[1], "min_cell": lo[0],
                                 "max_cell": hi[0], "n_cells": len(pairs)}
                else:
                    rec[name] = None
            out[(leg, base)] = rec
    return out


# ------------------------------------------------------------------ the three axes
def axis_wide(transfer, donor_face):
    rows = [r for r in (transfer or {}).get("rows") or [] if r.get("status") == "measured"]
    ranges = group_ranges((transfer or {}).get("arms"))
    published = set((((donor_face or {}).get("summary") or {}).get("moved_row_indices")) or [])
    out = []
    for r in rows:
        g = ranges.get((r.get("leg"), r.get("base"))) or {}
        rg = g.get("p95") or {}
        m = flip_multiplier(r.get("b"), r.get("band_lo"), r.get("band_hi"))
        out.append({
            "index": r.get("index"), "row": r.get("row"), "cell": r.get("cell"),
            "leg": r.get("leg"), "base": r.get("base"),
            "flip_multiplier": m,
            "range": [rg.get("min"), rg.get("max")],
            "range_source": "group p95 spread of the row's own (leg, base)",
            "straddle": straddle(m, rg.get("min"), rg.get("max")),
            "edge_distance_pct": edge_distance_pct(m, rg.get("min"), rg.get("max")),
        })
    return {"name": "wide_donor", "rows": out, "published_moved": sorted(published),
            "published_source": "BANDDONORCHOICE.summary.moved_row_indices"}


def axis_tight(transfer, tight_face):
    rows = [r for r in (transfer or {}).get("rows") or [] if r.get("status") == "measured"]
    ranges = group_ranges((transfer or {}).get("arms"))
    published = set((((tight_face or {}).get("summary") or {})
                     .get("rows_could_move_within_observed_p05_range")) or [])
    out = []
    for r in rows:
        g = ranges.get((r.get("leg"), r.get("base"))) or {}
        rg = g.get("p05") or {}
        m = flip_multiplier(r.get("b"), r.get("band_lo"), r.get("band_hi"))
        out.append({
            "index": r.get("index"), "row": r.get("row"), "cell": r.get("cell"),
            "leg": r.get("leg"), "base": r.get("base"),
            "flip_multiplier": m,
            "range": [rg.get("min"), rg.get("max")],
            "range_source": "group p05 spread of the row's own (leg, base)",
            "straddle": straddle(m, rg.get("min"), rg.get("max")),
            "edge_distance_pct": edge_distance_pct(m, rg.get("min"), rg.get("max")),
        })
    return {"name": "tight_p05", "rows": out, "published_moved": sorted(published),
            "published_source": "BANDTIGHT.summary.rows_could_move_within_observed_p05_range"}


def axis_top(top_face):
    rows = [r for r in (top_face or {}).get("rows") or [] if r.get("b") is not None]
    summary = (top_face or {}).get("summary") or {}
    # flipped_ids = rows that flip at EVERY measurement (rows_flip_every_measurement); depends_ids
    # = rows that flip at SOME measurement.  The straddle flag answers "can this row move at all",
    # so the matching published set is the SOME set.  Both are carried so the choice is auditable
    # -- picking the EVERY set here would report two real moves as screen misses.
    published = set(summary.get("depends_ids") or [])
    every = set(summary.get("flipped_ids") or [])
    out = []
    for r in rows:
        m = flip_multiplier(r.get("b"), r.get("band_lo"), r.get("band_hi"))
        lo, hi = r.get("multiplier_min"), r.get("multiplier_max")
        key = r.get("index")
        if key is None:
            # join key must match the published id format exactly: source/cell/row
            key = "%s/%s/%s" % (r.get("source"), r.get("cell"), r.get("row"))
        out.append({
            "index": key, "row": r.get("row"), "cell": r.get("cell"),
            "flip_multiplier": m,
            "range": [lo, hi],
            "range_source": "the row's own published multiplier ladder span (BANDTOPFLIP)",
            "straddle": straddle(m, lo, hi),
            "edge_distance_pct": edge_distance_pct(m, lo, hi),
            "flips_on_any_measurement": r.get("flips_on_any_measurement"),
        })
    return {"name": "top_ladder", "rows": out,
            "published_moved": sorted(str(x) for x in published),
            "published_moved_definition": "flips at SOME published rung/family combination",
            "published_moved_stricter_alternative": sorted(str(x) for x in every),
            "published_moved_stricter_definition": "flips at EVERY published measurement",
            "published_source": "BANDTOPFLIP.summary.depends_ids"}


# ------------------------------------------------------------------ scoring
def score_axis(axis):
    """Straddle flag versus the axis's own published moved set.  Four counts, never collapsed."""
    straddlers = [r["index"] for r in axis["rows"] if r["straddle"] in ("inside", "near_edge")]
    inside = [r["index"] for r in axis["rows"] if r["straddle"] == "inside"]
    near_edge = [r["index"] for r in axis["rows"] if r["straddle"] == "near_edge"]
    untested = [r["index"] for r in axis["rows"] if r["straddle"] == "untested"]
    moved = set(str(x) for x in axis["published_moved"])
    keys = {str(r["index"]): r for r in axis["rows"]}
    flagged = set(str(x) for x in straddlers)
    hit = sorted(moved & flagged)
    missed = sorted(moved - flagged)                      # screen unsafe: moved, never flagged
    unfired = sorted(flagged - moved)                     # screen useless: flagged, never moved
    decided = [r for r in axis["rows"] if r["straddle"] != "untested"]
    nearest_decision = None
    for r in decided:
        d = r.get("edge_distance_pct")
        if d is not None and r["straddle"] == "inside":
            nearest_decision = d if nearest_decision is None else min(nearest_decision, d)
    strict = set(str(x) for x in axis.get("published_moved_stricter_alternative") or [])
    return {
        "axis": axis["name"],
        "published_source": axis["published_source"],
        "published_moved_definition": axis.get("published_moved_definition"),
        "published_moved_stricter": sorted(strict),
        "moves_only_in_the_weaker_set": sorted(moved - strict),
        "rows": len(axis["rows"]),
        "rows_untested": untested,
        "straddlers": straddlers,
        "straddlers_inside": inside,
        "straddlers_near_edge": near_edge,
        "published_moved": sorted(moved),
        "n_published_moved": len(moved),
        "hit": hit,
        "missed_by_screen": missed,
        "flagged_never_moved": unfired,
        "precision": (len(hit) / float(len(flagged)) if flagged else None),
        "recall": (len(hit) / float(len(moved)) if moved else None),
        "exact": (not missed and not unfired),
        "nearest_inside_distance_pct": nearest_decision,
        "unresolved_indices": sorted(k for k in keys if str(k) in moved and k not in flagged),
    }


def summary_of(axes):
    scores = [score_axis(a) for a in axes]
    missed_any = sorted({x for s in scores for x in s["missed_by_screen"]})
    unfired_any = sorted({x for s in scores for x in s["flagged_never_moved"]})
    hits_any = sorted({x for s in scores for x in s["hit"]})
    return {
        "axes": [s["axis"] for s in scores],
        "rows_per_axis": {s["axis"]: s["rows"] for s in scores},
        "hits": hits_any,
        "missed_by_screen": missed_any,
        "flagged_never_moved": unfired_any,
        "exact_on_all_axes": not missed_any and not unfired_any,
        "axes_exact": [s["axis"] for s in scores if s["exact"]],
        "axes_inexact": [s["axis"] for s in scores if not s["exact"]],
        "n_moved_observations": sum(s["n_published_moved"] for s in scores),
        "underpowered": sum(s["n_published_moved"] for s in scores) < 3,
    }


def verdict_of(s):
    if s["exact_on_all_axes"]:
        if s["n_moved_observations"] == 0:
            return ("screen_is_vacuously_exact_no_axis_moves_anything",
                    "no published axis moves any row on this population, so the straddle flag is "
                    "exact and untested: nothing here can distinguish a screen from a constant")
        return ("two_published_numbers_predict_every_scored_axis",
                "on all %d scored axes the straddle flag reproduces the published moved set exactly "
                "(%d moved observations, %d hits, 0 missed, 0 flagged-but-inert); a reader can "
                "decide 'do not borrow from this cell' from m_flip and the offered range without "
                "re-running a sweep%s"
                % (len(s["axes"]), s["n_moved_observations"], len(s["hits"]),
                   "; the moved count is below the 3-positive floor, so this is untested at scale"
                   if s["underpowered"] else ""))
    if s["missed_by_screen"]:
        return ("the_screen_is_unsafe_on_some_axis",
                "%d published moved rows were never flagged (%s), so a reader following the two "
                "numbers would borrow from a cell that does move"
                % (len(s["missed_by_screen"]), ", ".join(str(x) for x in s["missed_by_screen"])))
    return ("the_screen_over_flags_on_some_axis",
            "%d rows are flagged as at risk but never moved (%s), so the two numbers alone do not "
            "separate a fragile cell from an inert one"
            % (len(s["flagged_never_moved"]), ", ".join(str(x) for x in s["flagged_never_moved"])))


# ------------------------------------------------------------------ run
def _stamp():
    import datetime
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z")


def run(save=True, outdir=None):
    transfer = load(SRC_TRANSFER)
    tight = load(SRC_TIGHT)
    donor = load(SRC_DONOR)
    top = load(SRC_TOP)
    axes = [axis_wide(transfer, donor), axis_tight(transfer, tight), axis_top(top)]
    scores = [score_axis(a) for a in axes]
    s = summary_of(axes)
    verdict, why = verdict_of(s)
    out = {
        "study": "e274_spread_straddle_sweep",
        "title": "can a row's own numbers say, in advance, whether an axis will move it?",
        "evidence_cutoff": CUTOFF,
        "generated": _stamp(),
        "source_faces": [SRC_TRANSFER, SRC_TIGHT, SRC_DONOR, SRC_TOP],
        "frozen_spec": {
            "design": ("for every measured BAND* row publish the flip multiplier, the multiplier "
                       "range the axis actually offers and a straddle flag; score the flag against "
                       "the moved set each face already published"),
            "no_new_draws": "no shuffle stream is drawn; every number is a function of published faces",
            "axis_selection": ("only axes that publish BOTH a range and a moved set are scored; an "
                               "axis with a moved set but no published range is disclosed, not guessed"),
            "error_modes": ("missed_by_screen (unsafe) and flagged_never_moved (useless) are "
                            "published separately; collapsing them would hide which way the screen "
                            "fails"),
            "edge_band": ("a flip within %.1f%% of the range width from an end is 'near_edge', "
                          "counted with the flag but disclosed apart from a decided 'inside'"
                          % EDGE_BAND_PCT),
        },
        "axes": {a["name"]: a for a in axes},
        "scores": scores,
        "summary": s,
        "verdict": verdict,
        "verdict_reason": why,
        "no_bill": "descriptive census over published faces; no trial, no ledger booking",
    }
    out["summary"]["verdict"] = verdict
    if save:
        _write(out, outdir)
    return out


def _write(face, outdir, tag=""):
    outdir = outdir or OUTDIR
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    text = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
    path = os.path.join(outdir, "BANDSTRADDLESWEEP-%s%s.json" % (face.get("evidence_cutoff"), tag))
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text + "\n")
    with io.open(os.path.join(outdir, LATEST), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text + "\n")
    return path


def verify(outdir=None, tag=""):
    outdir = outdir or OUTDIR
    path = os.path.join(outdir, "BANDSTRADDLESWEEP-%s%s.json" % (CUTOFF, tag))
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


def _axis(name, rows, moved):
    return {"name": name, "rows": rows, "published_moved": list(moved),
            "published_source": "fixture"}


def _row(index, m, lo, hi):
    return {"index": index, "row": "r%s" % index, "cell": "a", "flip_multiplier": m,
            "range": [lo, hi], "range_source": "fixture",
            "straddle": straddle(m, lo, hi), "edge_distance_pct": edge_distance_pct(m, lo, hi)}


def selftest():
    legs = []

    # --- flip multiplier, both signs (E269 rule must not drift) -------------------------
    legs.append(_leg(abs(flip_multiplier(-0.9, -0.3, 0.3) - 3.0) < 1e-12,
                     "negative side: m_flip = b/lo", flip_multiplier(-0.9, -0.3, 0.3)))
    legs.append(_leg(abs(flip_multiplier(0.9, -0.3, 0.3) - 3.0) < 1e-12,
                     "positive side: m_flip = b/hi", flip_multiplier(0.9, -0.3, 0.3)))
    legs.append(_leg(flip_multiplier(None, -0.3, 0.3) is None,
                     "no coefficient -> no flip multiplier, not zero"))

    # --- straddle is a four-way reading, never a bare boolean --------------------------
    legs.append(_leg(straddle(2.0, 1.0, 3.0) == "inside", "a flip mid-range is inside"))
    legs.append(_leg(straddle(0.5, 1.0, 3.0) == "outside", "a flip below the range is outside"))
    legs.append(_leg(straddle(None, 1.0, 3.0) == "untested", "no flip is untested, not outside"))
    # width 2.0, edge band 5% = 0.10 -> 2.98 sits 0.02 from the top end = 1% => near_edge
    legs.append(_leg(straddle(2.98, 1.0, 3.0) == "near_edge",
                     "a flip inside but within the edge band is near_edge", straddle(2.98, 1.0, 3.0)))
    legs.append(_leg(straddle(2.0, 3.0, 3.0) == "untested",
                     "a zero-width range cannot decide anything"))

    # --- group ranges come from the arms block, both ends ------------------------------
    arms = [{"cell": "a", "leg": "self", "base": 60, "p05": 1.0, "p95": 2.0},
            {"cell": "b", "leg": "self", "base": 60, "p05": 1.1, "p95": 2.5}]
    rg = group_ranges(arms)[("self", 60)]
    legs.append(_leg(rg["p95"]["min"] == 2.0 and rg["p95"]["max"] == 2.5,
                     "p95 range spans the cells", rg["p95"]))
    legs.append(_leg(rg["p05"]["max"] == 1.1, "p05 range spans the cells too", rg["p05"]))
    legs.append(_leg(rg["p95"]["max_cell"] == "b", "the widest cell is named, not just its value"))
    legs.append(_leg(group_ranges([]) == {}, "no arms -> no invented range"))

    # --- scoring: exact, unsafe, useless are three different readings ------------------
    exact = score_axis(_axis("x", [_row(0, 2.0, 1.0, 3.0), _row(1, 5.0, 1.0, 3.0)], ["0"]))
    legs.append(_leg(exact["exact"] and exact["precision"] == 1.0 and exact["recall"] == 1.0,
                     "an exact axis reads precision 1 and recall 1", exact))
    unsafe = score_axis(_axis("x", [_row(0, 5.0, 1.0, 3.0)], ["0"]))
    legs.append(_leg(unsafe["missed_by_screen"] == ["0"] and not unsafe["exact"],
                     "a moved row with no flag is published as missed", unsafe["missed_by_screen"]))
    useless = score_axis(_axis("x", [_row(0, 2.0, 1.0, 3.0)], []))
    legs.append(_leg(useless["flagged_never_moved"] == ["0"] and not useless["exact"],
                     "a flagged row that never moved is published as inert",
                     useless["flagged_never_moved"]))
    legs.append(_leg(useless["recall"] is None,
                     "recall over an empty moved set is None, not 1.0 (r1261 shape)"))

    # --- untested rows never count as decided -----------------------------------------
    unt = score_axis(_axis("x", [_row(0, None, 1.0, 3.0)], []))
    legs.append(_leg(unt["rows_untested"] == [0] and unt["straddlers"] == [],
                     "an untested row is disclosed and never flagged", unt["rows_untested"]))

    # --- verdict rule, all three faces --------------------------------------------------
    s_exact = summary_of([_axis("x", [_row(0, 2.0, 1.0, 3.0)], ["0"]),
                          _axis("y", [_row(0, 2.0, 1.0, 3.0)], ["0"]),
                          _axis("z", [_row(0, 2.0, 1.0, 3.0)], ["0"])])
    legs.append(_leg(verdict_of(s_exact)[0] == "two_published_numbers_predict_every_scored_axis",
                     "exact on every axis names the predictive reading"))
    legs.append(_leg(s_exact["underpowered"] is False,
                     "three moved observations clear the 3-positive floor",
                     s_exact["n_moved_observations"]))
    s_none = summary_of([_axis("x", [_row(0, 5.0, 1.0, 3.0)], [])])
    legs.append(_leg(verdict_of(s_none)[0] == "screen_is_vacuously_exact_no_axis_moves_anything",
                     "zero moves everywhere reads as vacuous, not as proof"))
    s_bad = summary_of([_axis("x", [_row(0, 5.0, 1.0, 3.0)], ["0"])])
    legs.append(_leg(verdict_of(s_bad)[0] == "the_screen_is_unsafe_on_some_axis",
                     "a missed move outranks an over-flag in the verdict"))

    # --- the published set must match what the flag answers ("can move", not "always moves") -
    axis_some = {"name": "top", "published_source": "fixture",
                 "rows": [_row("a", 2.0, 1.0, 3.0)],
                 "published_moved": ["a"], "published_moved_stricter_alternative": []}
    legs.append(_leg(score_axis(axis_some)["hit"] == ["a"],
                     "a straddler scored against the SOME set is a hit"))
    axis_every = dict(axis_some)
    axis_every["published_moved_stricter_alternative"] = []
    sc = score_axis(axis_every)
    legs.append(_leg(sc["moves_only_in_the_weaker_set"] == ["a"],
                     "a move visible only in the SOME set is disclosed as such", sc))
    axis_never = dict(axis_some)
    axis_never["published_moved"] = []
    legs.append(_leg(score_axis(axis_never)["flagged_never_moved"] == ["a"],
                     "and with no published move at all the same row reads as inert"))

    # --- live legs: the published faces exist and the wide axis is the E271 case -------
    faces_present = all(os.path.exists(os.path.join(OUTDIR, n)) for n in
                        (SRC_TRANSFER, SRC_TIGHT, SRC_DONOR, SRC_TOP))
    legs.append(_leg(faces_present, "all four source faces are on disk"))
    if faces_present:
        live = run(save=False)
        by = {s["axis"]: s for s in live["scores"]}
        wide = by["wide_donor"]
        legs.append(_leg(sorted(str(x) for x in wide["published_moved"])
                         == sorted(str(x) for x in wide["straddlers"]),
                         "live: the wide axis straddle set IS the published moved set",
                         (wide["straddlers"], wide["published_moved"])))
        legs.append(_leg(by["tight_p05"]["n_published_moved"] == 0,
                         "live: the tight axis publishes no moves", by["tight_p05"]["n_published_moved"]))
        legs.append(_leg(all(r["straddle"] in ("inside", "near_edge", "outside", "untested")
                             for a in live["axes"].values() for r in a["rows"]),
                         "live: every row carries one of the four readings"))
        legs.append(_leg(live["summary"]["exact_on_all_axes"] is True,
                         "live: the screen is exact on every scored axis",
                         (live["summary"]["missed_by_screen"],
                          live["summary"]["flagged_never_moved"])))

    ok = all(x["ok"] for x in legs)
    print("selftest %d/%d %s" % (sum(1 for x in legs if x["ok"]), len(legs),
                                 "PASS" if ok else "FAIL"))
    for x in legs:
        if not x["ok"]:
            print("  FAIL %s %s" % (x["leg"], x.get("detail")))
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
        print("  axes %s; moved observations %d; hits %d"
              % (",".join(s["axes"]), s["n_moved_observations"], len(s["hits"])))
        for sc in face["scores"]:
            print("  %-11s rows %2d  straddlers %-10s moved %-10s missed %-6s inert %s"
                  % (sc["axis"], sc["rows"], ",".join(str(x) for x in sc["straddlers"]) or "-",
                     ",".join(str(x) for x in sc["published_moved"]) or "-",
                     ",".join(str(x) for x in sc["missed_by_screen"]) or "-",
                     ",".join(str(x) for x in sc["flagged_never_moved"]) or "-"))
        return 0
    print("usage: e274_spread_straddle_sweep.py [run|verify|selftest]")
    return 2


if __name__ == "__main__":
    sys.exit(main())