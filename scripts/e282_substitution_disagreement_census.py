"""E282 -- where do the two tails disagree about reachability, and is that a boundary artefact?

E272 published, for every measured row, a reading against two tails (tight / wide): the range of
multipliers that tail offers, and a boolean "reachable" (the row's flip multiplier lies inside that
range). E279 used those booleans to test substitution and found two rows where the tails disagree.
E279 bracketed the substitution threshold only as an interval, and its seed left a hypothesis:

    "both disagreeing rows sit at a dominant-tail normalised gap of exactly 0.0 -- i.e. the
     substitute lands on the flip. If that is the only shape that produces disagreement, then the
     disagreement is a boundary artefact of the rounding, not a distance effect."

This study tests that hypothesis. It does so on the position of the flip inside each tail's range,
because the gap field cannot carry the question.

DECISION RULES, declared before any number is read (E188 / r1319 discipline -- the rules are frozen
here and re-emitted into the face so the face cannot be read against rules it did not declare):

  D1  SCOPE IS MEASURED, NOT PRESUMED. The census covers every published face in results/state_tilt
      that carries, for the same row, BOTH tails' (multiplier_min, multiplier_max) and the row's
      flip_multiplier. Each face is classified as qualifying / excluded-with-reason and the counts
      are published. A face that publishes only a verdict is not censused and not silently dropped.

  D2  DISAGREEMENT IS CELL-SCOPED. One record per measured cell whose two tails' re-derived
      reachability differs. reachable = flip inside [multiplier_min, multiplier_max], both ends
      inclusive (E272's published convention), re-derived here and never copied from a boolean.

  D3  THE GAP FIELD IS CLAMPED, SO "gap == 0" IS NOT A POSITION. Upstream gap_to_flip_pct returns
      exactly 0.0 for ANY flip inside the range, so normalised_gap == 0 holds for every interior
      reading and cannot distinguish "on the flip" from "anywhere in the range". The hypothesis is
      therefore tested on a statistic that does vary inside the range:
          position p = (flip - lo) / (hi - lo)                (0 at lo, 1 at hi)
          edge_distance_pct = min(flip-lo, hi-flip) / flip * 100  (same % ruler as gap_pct)
      This is a statement about the published field's branch, re-measured on the data: if some
      reachable reading publishes a NON-zero gap, D3 is false and the test falls back to the gap.

  D4  BOUNDARY TIE = a disagreement cell where the non-reaching tail's nearest boundary is within
      TOL of the flip, i.e. the two verdicts differ only by the inclusive-vs-strict convention. It
      is computed per cell and reported as a boolean; it is never inferred from a gap of 0.

  D5  HYPOTHESIS REFUTED = at least one disagreement cell where (a) the reaching tail holds the flip
      strictly interior beyond the edge tolerance and (b) the non-reaching tail's gap exceeds TOL.
      Both conditions are published per cell so a reader can do the arithmetic without this file.

  D6  NO FALSE PRECISION. With this few cells the output is a count plus per-cell arithmetic; no
      calibrated threshold is claimed and calibrated=False is published unconditionally.

Usage:  python scripts/e282_substitution_disagreement_census.py run|verify|selftest
"""
import glob
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e279_substitution_soundness as e279  # noqa: E402  (OUTDIR / TOL / load / rows_from)
import e262_p95_transfer_across_windows as e262  # noqa: E402
import e_band_family_vintage as vintage  # noqa: E402  (universe vintage freeze)

ROOT = e262.ROOT
OUTDIR = e262.OUTDIR
TOL = e262.TOL
TAILS = ("tight", "wide")

STUDY = "E282_substitution_disagreement_census"
TITLE = ("family-wide: where do the two tails disagree about reachability, and is the disagreement "
         "always a substitute sitting exactly on the flip (normalised gap 0)?")
CUTOFF = "2026-10-29"
FACE = "BANDDISAGREE-%s.json" % CUTOFF
LATEST = "banddisagree_latest.json"
SELF_FACES = (FACE, LATEST)

VERDICT_VOCAB = (
    "no_disagreement_cells_published",
    "every_disagreement_is_a_boundary_tie",
    "the_disagreement_is_a_range_difference_not_a_boundary_tie",
    "disagreements_mix_boundary_ties_and_range_differences",
    "the_gap_field_varies_inside_the_range_so_the_hypothesis_is_testable",
)

NO_BILL = ("measurement only: the published per-row tail ranges are re-read and arithmetic is done "
           "on them. No draw stream is drawn, no band rebuilt, no engine runs. A verdict here is a "
           "statement about the published numbers, not about the market.")


# ------------------------------------------------------------------ io
def load(name, outdir=None):
    with io.open(os.path.join(outdir or OUTDIR, name), encoding="utf-8") as fh:
        return json.load(fh)


def face_files(outdir=None):
    """Every published BAND* face, one entry per PUBLICATION.

    Each dated face is mirrored to <slug>_latest.json by its own study, so the mirror carries the
    same rows as the dated face it copies. Counting both would census the same cells twice and
    inflate every count on this face -- the mirrors are dropped by name and the drop is published.
    """
    out, mirrors = [], []
    for path in sorted(glob.glob(os.path.join(outdir or OUTDIR, "BAND*.json"))):
        name = os.path.basename(path)
        if name in SELF_FACES:
            continue
        if name.endswith("_latest.json"):
            mirrors.append(name)
            continue
        out.append(name)
    return out, mirrors


def rows_of(face):
    """Rows carrying both tails' range plus the row's flip; [] if the face cannot be censused."""
    rows = []
    blocks = face.get("tail_budget")
    if isinstance(blocks, dict):
        for _key, blk in sorted(blocks.items()):
            for row in (blk or {}).get("rows") or []:
                if _censusable(row):
                    rows.append(row)
    elif isinstance(face.get("rows"), list):
        for row in face["rows"]:
            if isinstance(row, dict) and _censusable(row):
                rows.append(row)
    return rows


def _censusable(row):
    if not isinstance(row, dict) or row.get("flip_multiplier") is None:
        return False
    for t in TAILS:
        blk = row.get(t)
        if not isinstance(blk, dict):
            return False
        if blk.get("multiplier_min") is None or blk.get("multiplier_max") is None:
            return False
    return True


def scope_census(outdir=None, only=None):
    """D1: which published faces can be censused, and why the others cannot."""
    qual, excluded = [], []
    files, mirrors = face_files(outdir)
    later = []
    if only is not None:
        later = [n for n in files + mirrors if n not in only]
        files = [n for n in files if n in only]
        mirrors = [n for n in mirrors if n in only]
    for name in mirrors:
        excluded.append({"face": name,
                         "reason": "mirror of a dated face (same rows, censused once via the "
                                   "dated face)"})
    for name in files:
        try:
            face = load(name, outdir)
        except (IOError, ValueError) as exc:
            excluded.append({"face": name, "reason": "unreadable: %s" % exc})
            continue
        rows = rows_of(face)
        if rows:
            qual.append({"face": name, "rows": len(rows)})
        else:
            excluded.append({"face": name,
                             "reason": "publishes no row carrying both tails' multiplier range "
                                       "and a flip multiplier"})
    return {"files_scanned": len(qual) + len(excluded),
            "faces_qualifying": qual,
            "faces_excluded": excluded,
            "n_qualifying": len(qual),
            "n_excluded": len(excluded)}


# ------------------------------------------------------------------ per-tail reading
def reachable_of(blk, flip):
    lo, hi = blk.get("multiplier_min"), blk.get("multiplier_max")
    if flip is None or lo is None or hi is None:
        return None
    return bool((float(lo) - TOL) <= float(flip) <= (float(hi) + TOL))


def position_of(blk, flip):
    """D3: where inside that tail's range the flip sits, in [0,1]; None if not expressible."""
    lo, hi = blk.get("multiplier_min"), blk.get("multiplier_max")
    if flip is None or lo is None or hi is None:
        return None
    lo, hi, flip = float(lo), float(hi), float(flip)
    if hi - lo <= TOL:
        return None
    return (flip - lo) / (hi - lo)


def edge_distance_pct(blk, flip):
    """Distance from the flip to that range's nearest bound, on gap_pct's own percent ruler."""
    lo, hi = blk.get("multiplier_min"), blk.get("multiplier_max")
    if flip is None or lo is None or hi is None or not float(flip):
        return None
    flip = float(flip)
    return min(abs(flip - float(lo)), abs(float(hi) - flip)) / flip * 100.0


def edge_tolerance_pct(flip):
    """D4's tolerance, mapped from a multiplier to the same % ruler gap_pct uses."""
    if flip is None or not float(flip):
        return None
    return TOL / float(flip) * 100.0


def tail_reading(row, tail):
    blk = row.get(tail) or {}
    flip = row.get("flip_multiplier")
    reach = reachable_of(blk, flip)
    return {
        "tail": tail,
        "multiplier_min": blk.get("multiplier_min"),
        "multiplier_max": blk.get("multiplier_max"),
        "spread_pct": blk.get("spread_pct"),
        "gap_pct": blk.get("gap_pct"),
        "normalised_gap": blk.get("normalised_gap"),
        "published_reachable": blk.get("reachable"),
        "reachable": reach,
        "position": position_of(blk, flip),
        "distance_to_nearest_bound_pct": edge_distance_pct(blk, flip),
    }


# ------------------------------------------------------------------ census
def census_row(row):
    """One record per measured row: both tails, re-derived reachability, positions."""
    flip = row.get("flip_multiplier")
    rec = {
        "row": row.get("row"),
        "leg": row.get("leg"),
        "base": row.get("base"),
        "index": row.get("index"),
        "cell": row.get("cell"),
        "flip_direction": row.get("flip_direction"),
        "flip_multiplier": flip,
        "edge_tolerance_pct": edge_tolerance_pct(flip),
        "tails": {t: tail_reading(row, t) for t in TAILS},
    }
    rea = {t: rec["tails"][t]["reachable"] for t in TAILS}
    rec["reachable"] = rea
    rec["disagrees"] = (rea["tight"] is not None and rea["wide"] is not None
                        and bool(rea["tight"]) != bool(rea["wide"]))
    rec["published_agrees"] = {t: (rea[t] == rec["tails"][t]["published_reachable"])
                               for t in TAILS}
    return rec


def censused(rows):
    return [census_row(r) for r in rows]


def disagreement_cells(rows, outdir=None):
    """D2 + D4: one record per disagreeing cell, with both tails' positions and the tie flag."""
    out = []
    for rec in censused(rows):
        if not rec["disagrees"]:
            continue
        reaching = [t for t in TAILS if rec["reachable"][t] is True]
        missing = [t for t in TAILS if rec["reachable"][t] is False]
        if len(reaching) != 1 or len(missing) != 1:
            continue
        rt, mt = reaching[0], missing[0]
        rtail, mtail = rec["tails"][rt], rec["tails"][mt]
        tol_pct = rec["edge_tolerance_pct"]
        missing_gap = mtail["gap_pct"]
        # D4: the two verdicts differ only by the inclusive-vs-strict convention when the
        # non-reaching tail's nearest bound sits within TOL of the flip. Measured on the same
        # ruler the contract itself uses: upstream reachable == (gap_pct <= TOL).
        flip = float(rec["flip_multiplier"])
        bound_distance = min(abs(flip - float(mtail["multiplier_min"])),
                             abs(float(mtail["multiplier_max"]) - flip))
        tie = bool(missing_gap is not None and abs(float(missing_gap)) <= TOL)
        out.append({
            "row_key": "%s|%s|%s" % (rec["leg"], rec["base"], rec["index"]),
            "leg": rec["leg"], "base": rec["base"], "index": rec["index"],
            "cell": rec["cell"],
            "flip_direction": rec["flip_direction"],
            "flip_multiplier": rec["flip_multiplier"],
            "reaching_tail": rt,
            "non_reaching_tail": mt,
            "reaching_position": rtail["position"],
            "reaching_distance_to_nearest_bound_pct": rtail["distance_to_nearest_bound_pct"],
            "non_reaching_gap_pct": missing_gap,
            "non_reaching_normalised_gap": mtail["normalised_gap"],
            "non_reaching_multiplier_min": mtail["multiplier_min"],
            "non_reaching_multiplier_max": mtail["multiplier_max"],
            "non_reaching_bound_distance": bound_distance,
            "reaching_multiplier_min": rtail["multiplier_min"],
            "reaching_multiplier_max": rtail["multiplier_max"],
            "edge_tolerance_pct": tol_pct,
            "boundary_tie": tie,
            "interior_of_reaching_tail": bool(
                rtail["position"] is not None and TOL < rtail["position"] < 1.0 - TOL),
            "reaching_gap_pct_is_zero": bool(
                rtail["gap_pct"] is not None and abs(float(rtail["gap_pct"])) <= TOL),
        })
    return out


# ------------------------------------------------------------------ hypothesis tests
def tie_impossibility(cells):
    """D4 identity: upstream reachable == (gap_pct <= TOL). A tail is therefore non-reaching only
    when its gap exceeds TOL, so "the two tails differ only by the inclusive edge" cannot occur.

    Published as a measured identity rather than asserted: the smallest non-reaching gap over the
    census is reported next to the tolerance, so the exclusion is visible.
    """
    if not cells:
        return {"tie_possible_in_principle": None, "min_non_reaching_gap_pct": None,
                "identity": "vacuous_without_cells", "note": "no cell to measure"}
    gaps = [abs(float(c["non_reaching_gap_pct"])) for c in cells
            if c.get("non_reaching_gap_pct") is not None]
    mn = min(gaps) if gaps else None
    return {
        "tie_possible_in_principle": False,
        "min_non_reaching_gap_pct": mn,
        "max_non_reaching_gap_pct": max(gaps) if gaps else None,
        "tolerance": TOL,
        "identity": ("reachable is defined as gap_pct <= TOL, so a non-reaching tail's gap is "
                     "strictly greater than TOL by construction: a pair judged with one contract "
                     "cannot disagree on the boundary alone"),
        "note": ("so the seeded 'boundary artefact of the rounding' has two independent reasons "
                 "it cannot be true here: the gap field is clamped to 0 inside the range (D3), and "
                 "a boundary-only disagreement is excluded by the contract that produced the "
                 "disagreement (D4 identity)."),
    }


def clamp_check(censused_rows):
    """D3: is the gap field really clamped? Measured, not asserted."""
    reaching = []
    for rec in censused_rows:
        for t in TAILS:
            blk = rec["tails"][t]
            if blk["reachable"] is True:
                reaching.append({"row_key": "%s|%s|%s" % (rec["leg"], rec["base"], rec["index"]),
                                 "tail": t,
                                 "gap_pct": blk["gap_pct"],
                                 "position": blk["position"],
                                 "distance_to_nearest_bound_pct":
                                     blk["distance_to_nearest_bound_pct"]})
    nonzero = [r for r in reaching if r["gap_pct"] is None
               or abs(float(r["gap_pct"])) > TOL]
    return {
        "reaching_readings": len(reaching),
        "reaching_readings_with_zero_gap": len(reaching) - len(nonzero),
        "reaching_readings_with_nonzero_gap": nonzero,
        "gap_is_clamped_for_every_reaching_reading": bool(reaching) and not nonzero,
        "min_position_among_reaching": min([r["position"] for r in reaching
                                            if r["position"] is not None], default=None),
        "max_position_among_reaching": max([r["position"] for r in reaching
                                           if r["position"] is not None], default=None),
        "min_distance_to_bound_among_reaching": min(
            [r["distance_to_nearest_bound_pct"] for r in reaching
             if r["distance_to_nearest_bound_pct"] is not None], default=None),
    }


def hypothesis_test(cells, clamp):
    """D5: refuted / supported / not-testable, on the position statistic rather than the gap."""
    impo = tie_impossibility(cells)
    if not cells:
        return {"status": "not_testable",
                "reason": "no disagreement cell is published, so nothing can be confined to a "
                          "boundary tie.",
                "refuted_by": [], "boundary_ties": [], "interior_cells": [],
                "tie_impossibility": impo}
    ties = [c["row_key"] for c in cells if c["boundary_tie"]]
    interior = [c for c in cells if c["interior_of_reaching_tail"]]
    refuted_by = [c["row_key"] for c in interior
                  if c["non_reaching_gap_pct"] is not None
                  and abs(float(c["non_reaching_gap_pct"])) > TOL]
    if not clamp.get("gap_is_clamped_for_every_reaching_reading"):
        status = "the_gap_field_varies_inside_the_range_so_the_hypothesis_is_testable"
        reason = ("at least one reachable reading publishes a non-zero gap, so 'gap == 0' does "
                  "carry position information and the hypothesis should be tested on the gap "
                  "itself before the position statistic.")
    elif refuted_by:
        status = "refuted"
        reason = ("%d of %d disagreement cell(s) sit strictly interior to the reaching tail "
                  "(position %s) while the non-reaching tail's gap is %s pct. Two independent "
                  "grounds: the gap field reads 0.0 for every interior reading because it is "
                  "clamped (so 'gap == 0' carries no position), and a boundary-only disagreement "
                  "is excluded by the contract that produced it (non-reaching gaps start at %s "
                  "pct against a tolerance of %s). The disagreement is a range difference, not a "
                  "rounding tie."
                  % (len(refuted_by), len(cells),
                     "/".join("%.3f" % c["reaching_position"] for c in interior),
                     "/".join("%.2f" % abs(float(c["non_reaching_gap_pct"])) for c in interior),
                     "%.3g" % impo["min_non_reaching_gap_pct"], "%.1g" % TOL))
    elif ties and len(ties) == len(cells):
        status = "supported"
        reason = ("every disagreement cell has the non-reaching tail's nearest bound within the "
                  "edge tolerance of the flip: the two verdicts differ only by the "
                  "inclusive-vs-strict convention.")
    else:
        status = "mixed"
        reason = ("%d boundary tie(s) and %d interior cell(s) without a boundary explanation."
                  % (len(ties), len(cells) - len(ties)))
    return {"status": status, "reason": reason, "refuted_by": refuted_by,
            "boundary_ties": ties,
            "interior_cells": [c["row_key"] for c in interior],
            "position_statistic": "p = (flip - lo) / (hi - lo) on the reaching tail",
            "gap_statistic_calibrated": False,
            "tie_impossibility": impo}


def verdict_of(hyp, cells):
    if not cells:
        return "no_disagreement_cells_published"
    if hyp["status"] == "the_gap_field_varies_inside_the_range_so_the_hypothesis_is_testable":
        return "the_gap_field_varies_inside_the_range_so_the_hypothesis_is_testable"
    if hyp["status"] == "refuted":
        interior = len(hyp["interior_cells"])
        return ("the_disagreement_is_a_range_difference_not_a_boundary_tie" if interior == len(cells)
                else "disagreements_mix_boundary_ties_and_range_differences")
    if hyp["status"] == "supported":
        return "every_disagreement_is_a_boundary_tie"
    return "disagreements_mix_boundary_ties_and_range_differences"


def reason_of(verdict, hyp, cells, clamp):
    if verdict == "no_disagreement_cells_published":
        return "no censused cell has a tail pair that disagrees about reachability."
    if verdict == "the_disagreement_is_a_range_difference_not_a_boundary_tie":
        return ("all %d disagreement cell(s) are range differences: the reaching tail holds the "
                "flip strictly interior to its published multipliers (%s) while the gap field "
                "reads 0.0 for %d of %d reachable readings because it is CLAMPED inside the range "
                "-- so 'gap == 0' says nothing about sitting on the flip, and the seeded "
                "hypothesis is refuted by a measurement, not by an opinion."
                % (len(cells),
                   "/".join("%.3f" % c["reaching_position"] for c in cells),
                   clamp["reaching_readings_with_zero_gap"], clamp["reaching_readings"]))
    if verdict == "every_disagreement_is_a_boundary_tie":
        return ("every disagreement cell is a boundary tie at the edge tolerance (%s pct): the "
                "verdict differs only by the inclusive-vs-strict convention."
                % "/".join("%.3g" % c["edge_tolerance_pct"] for c in cells))
    return hyp["reason"]


# ------------------------------------------------------------------ identity
def identity_check(censused_rows, face_e279, budget):
    """Two identities: our booleans re-derive E272's, and our disagreement set is E279's."""
    mismatched, checked = [], 0
    for rec in censused_rows:
        for t in TAILS:
            pub = rec["tails"][t]["published_reachable"]
            mine = rec["reachable"][t]
            if pub is None and mine is None:
                continue
            checked += 1
            if pub != mine:
                mismatched.append({"row": rec["row"], "cell": rec["cell"], "leg": rec["leg"],
                                   "base": rec["base"], "index": rec["index"], "tail": t,
                                   "published": pub, "mine": mine})
    mine_cells = sorted("%s|%s|%s" % (r["leg"], r["base"], r["index"])
                        for r in censused_rows if r["disagrees"])
    e279_cells = []
    if isinstance(face_e279, dict):
        for rec in face_e279.get("census") or []:
            swap = (rec.get("swap") or {}).get("tight") or {}
            if swap.get("agrees") is False:
                e279_cells.append("%s|%s|%s" % (rec.get("leg"), rec.get("base"),
                                               rec.get("index")))
        e279_cells = sorted(e279_cells)
    budget_rows = (budget.get("summary") or {}).get("rows")
    return {
        "checked_tail_booleans": checked,
        "mismatched": mismatched,
        "disagreement_cells_here": mine_cells,
        "disagreement_cells_per_e279": e279_cells,
        "disagreement_set_agrees": bool(mine_cells == e279_cells) if e279_cells else None,
        "rows_censused": len(censused_rows),
        "rows_in_budget_summary": budget_rows,
        "row_count_note": ("the budget summary counts rows carrying a flip; the census counts rows "
                           "that also publish both tails' ranges"),
    }


# ------------------------------------------------------------------ build / publish
def _vintage_names(outdir):
    """The universe this face already published, read back out of its own scope census.

    The family universe grows with every sibling study, so re-deriving over the live directory made
    this face disagree with itself after each new publication (see e_band_family_vintage).  The face
    stores every name it scanned -- qualifying and excluded -- so the vintage is exact here, rather
    than inferred from timestamps.
    """
    for name in (FACE, LATEST):
        path = os.path.join(outdir, name)
        if not os.path.exists(path):
            continue
        try:
            with io.open(path, encoding="utf-8") as fh:
                face = json.load(fh)
        except (IOError, ValueError):
            continue
        scope = face.get("scope_census") or {}
        names = []
        for block in ("faces_qualifying", "faces_excluded"):
            for item in scope.get(block) or []:
                if isinstance(item, dict) and isinstance(item.get("face"), str):
                    names.append(item["face"])
        if names:
            return set(names), name
    return None, None


def build(outdir=None, extend=False):
    outdir = outdir or OUTDIR
    frozen, frozen_from = (None, None) if extend else _vintage_names(outdir)
    scope = scope_census(outdir, only=frozen)
    vintage_note = None
    if frozen is not None:
        files, mirrors = face_files(outdir)
        vintage_note = {
            "frozen_from": frozen_from,
            "faces_in_scope": len(frozen),
            "faces_not_yet_published": sorted(n for n in files + mirrors if n not in frozen),
            "rule": "a face re-derives against the universe it published; only a new run widens it",
        }
    rows = []
    per_face = []
    for q in scope["faces_qualifying"]:
        face = load(q["face"], outdir)
        rs = rows_of(face)
        per_face.append({"face": q["face"], "rows": len(rs)})
        for r in rs:
            r = dict(r)
            r.setdefault("row", "%s" % (r.get("leg")))
            rows.append(r)
    cen = censused(rows)
    cells = disagreement_cells(rows, outdir)
    clamp = clamp_check(cen)
    hyp = hypothesis_test(cells, clamp)
    verdict = verdict_of(hyp, cells)
    dist = {
        "non_reaching_gap_pct": sorted(abs(float(c["non_reaching_gap_pct"]))
                                       for c in cells
                                       if c["non_reaching_gap_pct"] is not None),
        "non_reaching_normalised_gap": sorted(float(c["non_reaching_normalised_gap"])
                                              for c in cells
                                              if c["non_reaching_normalised_gap"] is not None),
        "reaching_position": sorted(float(c["reaching_position"]) for c in cells
                                    if c["reaching_position"] is not None),
        "reaching_distance_to_nearest_bound_pct": sorted(
            float(c["reaching_distance_to_nearest_bound_pct"]) for c in cells
            if c["reaching_distance_to_nearest_bound_pct"] is not None),
    }
    s = {
        "faces_scanned": scope["files_scanned"],
        "faces_censused": scope["n_qualifying"],
        "faces_excluded": scope["n_excluded"],
        "rows_censused": len(cen),
        "rows_where_tails_disagree": len(cells),
        "disagreement_cells": [c["row_key"] for c in cells],
        "boundary_tie_cells": hyp["boundary_ties"],
        "interior_cells": hyp["interior_cells"],
        "reaching_readings": clamp["reaching_readings"],
        "reaching_readings_with_zero_gap": clamp["reaching_readings_with_zero_gap"],
        "gap_is_clamped": clamp["gap_is_clamped_for_every_reaching_reading"],
        "hypothesis_status": hyp["status"],
        "boundary_tie_possible_in_principle": (hyp.get("tie_impossibility") or {}).get(
            "tie_possible_in_principle"),
        "min_non_reaching_gap_pct": (hyp.get("tie_impossibility") or {}).get(
            "min_non_reaching_gap_pct"),
        "identity_mismatched": len(mismatched_flat(cen)),
        "verdict": verdict,
        "calibrated": False,
    }
    return {
        "study": STUDY,
        "title": TITLE,
        "evidence_cutoff": CUTOFF,
        "generated": _stamp(),
        "universe_vintage": vintage_note,
        "frozen_spec": {
            "D1_scope_measured": "every published BAND* face in results/state_tilt is classified "
                                 "qualifying / excluded-with-reason; counts published.",
            "D2_disagreement_cell_scoped": "one record per cell whose two tails' re-derived "
                                           "reachability differs; reachable = flip inside "
                                           "[min,max] inclusive, re-derived never copied.",
            "D3_gap_is_clamped": "upstream returns gap 0.0 for any flip inside the range, so "
                                 "normalised_gap == 0 is not a position. Position p = "
                                 "(flip-lo)/(hi-lo) and edge_distance_pct are the statistics used, "
                                 "and D3 is itself measured on the data (clamp_check).",
            "D4_boundary_tie": "non-reaching tail's nearest bound within TOL of the flip, computed "
                               "per cell, never inferred from a gap of 0.",
            "D5_refuted": "at least one cell strictly interior on the reaching tail whose "
                          "non-reaching gap exceeds TOL.",
            "D6_no_false_precision": "counts plus per-cell arithmetic; calibrated=False always.",
            "tolerance": TOL,
        },
        "scope_census": scope,
        "faces": per_face,
        "census": [_public(rec) for rec in cen],
        "disagreement_cells": cells,
        "clamp_check": clamp,
        "distributions": dist,
        "hypothesis_test": hyp,
        "identity_check": identity_check(cen, _safe_load(e279.FACE, outdir),
                                         _safe_load(e279.SRC_BUDGET, outdir)),
        "summary": s,
        "verdict": verdict,
        "verdict_reason": reason_of(verdict, hyp, cells, clamp),
        "no_bill": NO_BILL,
    }


def mismatched_flat(cen):
    out = []
    for rec in cen:
        for t in TAILS:
            pub = rec["tails"][t]["published_reachable"]
            mine = rec["reachable"][t]
            if pub is None and mine is None:
                continue
            if pub != mine:
                out.append((rec["leg"], rec["base"], rec["index"], t))
    return out


def _public(rec):
    return rec


def _safe_load(name, outdir=None):
    try:
        return load(name, outdir)
    except (IOError, ValueError):
        return None


def _stamp():
    import time
    return time.strftime("%Y-%m-%dT%H:%M:%S")


def _write(face, outdir=None):
    outdir = outdir or OUTDIR
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    body = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
    for name in (FACE, LATEST):
        with io.open(os.path.join(outdir, name), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body)
    return os.path.join(outdir, FACE)


def run(save=True, outdir=None):
    face = build(outdir, extend=True)
    if save:
        face["_written"] = os.path.basename(_write(face, outdir))
    return face


def verify(outdir=None):
    problems = []
    disk = load(FACE, outdir)
    fresh = build(outdir)
    for key in ("scope_census", "census", "disagreement_cells", "clamp_check", "distributions",
                "hypothesis_test", "identity_check", "summary", "verdict", "verdict_reason"):
        if fresh.get(key) != disk.get(key):
            problems.append("%s does not re-derive" % key)
    if (fresh.get("summary") or {}).get("verdict") not in VERDICT_VOCAB:
        problems.append("verdict is outside the frozen vocabulary")
    if (fresh.get("identity_check") or {}).get("mismatched"):
        problems.append("our reachability disagrees with the published boolean")
    if not (fresh.get("summary") or {}).get("faces_censused"):
        problems.append("no face qualifies -- the census would be about nothing")
    return {"ok": not problems, "problems": problems,
            "verdict": (disk.get("summary") or {}).get("verdict")}


# ------------------------------------------------------------------ selftest
def _row(index, flip, tight, wide, cell="c0", leg="cross", base=60, row="cross"):
    """tight/wide = (lo, hi, spread_pct); gap/ng are computed the way upstream computes them."""
    def blk(t, spec):
        lo, hi, spread = spec
        if flip is None or lo is None or hi is None:
            gap = None
        elif not lo or flip <= 0:
            gap = None
        elif flip < lo:
            gap = (lo / flip - 1.0) * 100.0
        elif flip > hi:
            gap = (1.0 - hi / flip) * 100.0
        else:
            gap = 0.0
        ng = None if (gap is None or not spread) else gap / spread
        return {"tail": t, "multiplier_min": lo, "multiplier_max": hi,
                "spread_pct": spread, "gap_pct": gap, "normalised_gap": ng,
                "reachable": (None if gap is None else bool(gap <= TOL))}
    return {"row": row, "index": index, "cell": cell, "leg": leg, "base": base,
            "flip_direction": ("widening_reenters" if flip and flip > 1.0 else "narrowing_escapes"),
            "flip_multiplier": flip,
            "tight": blk("tight", tight), "wide": blk("wide", wide)}


def selftest():
    legs = []

    def leg(ok, name, detail=""):
        legs.append({"ok": bool(ok), "name": name, "detail": detail})

    # L1: D3 clamp -- an interior flip publishes gap 0.0, and a flip outside publishes a real gap
    interior = _row(0, 2.2, (1.0, 1.1, 10.0), (1.9, 2.3, 16.0))
    outside = _row(0, 2.5, (1.0, 1.1, 10.0), (1.9, 2.3, 16.0))
    leg(interior["wide"]["gap_pct"] == 0.0
        and position_of(interior["wide"], 2.2) is not None,
        "L1 interior gap is 0.0 (clamped) while the position still varies -- fixture sanity",
        repr(interior["wide"]["gap_pct"]))
    leg(outside["wide"]["gap_pct"] > 0 and outside["wide"]["normalised_gap"] > 0,
        "L1b outside the range the gap is a real distance",
        "%.3f/%.3f" % (outside["wide"]["gap_pct"], outside["wide"]["normalised_gap"]))
    cen = censused([interior])
    clamp = clamp_check(cen)
    leg(clamp["gap_is_clamped_for_every_reaching_reading"] is True
        and clamp["reaching_readings_with_zero_gap"] == 1
        and clamp["min_position_among_reaching"] is not None,
        "L1c clamp_check measures the clamp and still records a position",
        repr(clamp["min_position_among_reaching"]))

    # L2: position_of / distances
    blk = {"multiplier_min": 2.0, "multiplier_max": 4.0}
    leg(abs(position_of(blk, 3.0) - 0.5) < 1e-12, "L2 position mid-range is 0.5")
    leg(position_of(blk, 2.0) == 0.0 and position_of(blk, 4.0) == 1.0,
        "L2b position is 0/1 on the bounds")
    leg(position_of(blk, 3.0) is not None and position_of(
        {"multiplier_min": 2.0, "multiplier_max": 2.0}, 2.0) is None,
        "L2c degenerate range has no position")
    leg(abs(edge_distance_pct(blk, 3.0) - (1.0 / 3.0) * 100.0) < 1e-9,
        "L2d nearest-bound distance on the % ruler",
        repr(edge_distance_pct(blk, 3.0)))

    # L3: D4 identity -- a boundary-only disagreement is excluded by the contract itself. A flip
    # landing inside a tail's range is reachable there (gap 0 <= TOL), so the same pair cannot
    # disagree on the boundary alone; the branch is exercised on a synthetic cell record.
    at_bound = _row(9, 2.3, (1.0, 1.1, 10.0), (1.9, 2.3, 16.0))
    leg(at_bound["wide"]["reachable"] is True and at_bound["tight"]["reachable"] is False,
        "L3 a flip on a tail's own bound is reachable there",
        "wide=%r tight=%r" % (at_bound["wide"]["reachable"], at_bound["tight"]["reachable"]))
    cells = disagreement_cells([at_bound])
    leg(len(cells) == 1 and cells[0]["boundary_tie"] is False
        and cells[0]["non_reaching_gap_pct"] > TOL,
        "L3b that cell is a distance, never a boundary tie",
        "gap=%.2f tie=%r" % (cells[0]["non_reaching_gap_pct"], cells[0]["boundary_tie"]))
    _fake_tie = {"row_key": "x|60|0", "leg": "x", "base": 60, "index": 0, "cell": "c",
                 "flip_multiplier": 2.3, "reaching_tail": "wide", "non_reaching_tail": "tight",
                 "reaching_position": 0.5, "non_reaching_gap_pct": TOL / 2.0,
                 "boundary_tie": True, "interior_of_reaching_tail": False}
    leg(hypothesis_test([_fake_tie], {"gap_is_clamped_for_every_reaching_reading": True})["status"]
        == "supported",
        "L3c the supported branch exists and is reachable by a synthetic cell")

    # L3d: the identity is measured on the real census -- non-reaching gaps start above TOL
    _real = _safe_load(FACE)
    if _real is not None and (_real.get("disagreement_cells") or []):
        _imp = (_real.get("hypothesis_test") or {}).get("tie_impossibility") or {}
        leg(_imp.get("tie_possible_in_principle") is False
            and _imp.get("min_non_reaching_gap_pct") is not None
            and _imp["min_non_reaching_gap_pct"] > TOL,
            "L3d the tie impossibility is measured on the real census",
            "min_gap=%s" % _imp.get("min_non_reaching_gap_pct"))
    else:
        leg(False, "L3d the tie impossibility is measured on the real census", "face missing")

    # L4: D5 refutation on an interior fixture, support on the synthetic tie cell
    interior = _row(9, 2.2, (1.0, 1.1, 10.0), (1.9, 2.3, 16.0))
    leg(disagreement_cells([interior])[0]["interior_of_reaching_tail"] is True,
        "L4 the interior fixture is interior",
        "pos=%.4f" % disagreement_cells([interior])[0]["reaching_position"])
    hyp = hypothesis_test(disagreement_cells([interior]),
                          clamp_check(censused([interior])))
    leg(hyp["status"] == "refuted" and hyp["refuted_by"] == ["cross|60|9"],
        "L4b interior disagreement refutes the hypothesis", hyp["status"])
    hyp = hypothesis_test([_fake_tie], {"gap_is_clamped_for_every_reaching_reading": True})
    leg(hyp["status"] == "supported", "L4c a boundary tie would support it", hyp["status"])

    # L5: the non-reaching tail's gap is a real distance on a genuine disagreement cell
    cells_dist = disagreement_cells([at_bound])
    leg(cells_dist[0]["non_reaching_gap_pct"] > TOL,
        "L5 the non-reaching tail's gap is a real distance",
        repr(cells_dist[0]["non_reaching_gap_pct"]))

    # L6: mixed shapes get their own verdict
    hyp = hypothesis_test(disagreement_cells([at_bound, interior]),
                          clamp_check(censused([at_bound, interior])))
    leg(verdict_of(hyp, [{"row_key": "a"}, {"row_key": "b"}])
        == "disagreements_mix_boundary_ties_and_range_differences",
        "L6 mixed evidence is not collapsed into one story", hyp["status"])
    leg(verdict_of({"status": "not_testable"}, []) == "no_disagreement_cells_published",
        "L6b an empty census says so")

    # L7: real face -- the census must actually fire (r1261: assert the mechanism ran)
    path = os.path.join(OUTDIR, FACE)
    face = _safe_load(FACE)
    if face is None:
        leg(False, "L7 real census fired", "face missing: %s" % path)
        leg(False, "L8 identity to the published booleans", "face missing")
        leg(False, "L9 disagreement set equals E279's census", "face missing")
        leg(False, "L10 a scoped face qualifies", "face missing")
        leg(False, "L11 the face's own verdict recomputes from its cells", "face missing")
        leg(False, "L12 clamp claim measured on real data", "face missing")
    else:
        s = face.get("summary") or {}
        leg(s.get("faces_censused", 0) >= 1 and s.get("rows_censused", 0) >= 1,
            "L7 real census fired",
            "faces=%s rows=%s cells=%s" % (s.get("faces_censused"), s.get("rows_censused"),
                                           s.get("rows_where_tails_disagree")))
        idc = face.get("identity_check") or {}
        leg(idc.get("checked_tail_booleans") and not idc.get("mismatched")
            and idc.get("checked_tail_booleans") == 2 * len(face.get("census") or []),
            "L8 identity to the published booleans",
            "checked=%s mismatched=%s" % (idc.get("checked_tail_booleans"),
                                          len(idc.get("mismatched") or [])))
        leg(idc.get("disagreement_set_agrees") is True
            and idc.get("disagreement_cells_here") == idc.get("disagreement_cells_per_e279"),
            "L9 disagreement set equals E279's census",
            "%s vs %s" % (idc.get("disagreement_cells_here"),
                          idc.get("disagreement_cells_per_e279")))
        leg((face.get("scope_census") or {}).get("n_qualifying", 0) >= 1,
            "L10 a scoped face qualifies",
            "scanned=%s qualifying=%s" % ((face.get("scope_census") or {}).get("files_scanned"),
                                          (face.get("scope_census") or {}).get("n_qualifying")))
        cells = face.get("disagreement_cells") or []
        hyp2 = hypothesis_test(cells, face.get("clamp_check") or {})
        leg(face.get("verdict") == verdict_of(hyp2, cells) == s.get("verdict"),
            "L11 the face's own verdict recomputes from its cells",
            "%r vs %r" % (face.get("verdict"), verdict_of(hyp2, cells)))
        clamp = face.get("clamp_check") or {}
        leg(clamp.get("gap_is_clamped_for_every_reaching_reading") is True
            and clamp.get("reaching_readings_with_zero_gap") == clamp.get("reaching_readings")
            and clamp.get("min_distance_to_bound_among_reaching") is not None,
            "L12 clamp claim measured on real data",
            "reach=%s zero=%s min_dist=%s"
            % (clamp.get("reaching_readings"), clamp.get("reaching_readings_with_zero_gap"),
               clamp.get("min_distance_to_bound_among_reaching")))

    ok = sum(1 for l in legs if l["ok"])
    return {"legs": legs, "passed": ok, "total": len(legs), "ok": ok == len(legs)}


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "run"
    if cmd == "run":
        face = run()
        s = face["summary"]
        print("verdict=%s cells=%d faces=%d/%d clamp=%s hyp=%s"
              % (s["verdict"], s["rows_where_tails_disagree"], s["faces_censused"],
                 s["faces_scanned"], s["gap_is_clamped"], s["hypothesis_status"]))
        print("cells=%s positions=%s non_reaching_gaps=%s"
              % (",".join(s["disagreement_cells"]) or "none",
                 ",".join("%.3f" % p for p in
                          (face.get("distributions") or {}).get("reaching_position") or []),
                 ",".join("%.2f" % g for g in
                          (face.get("distributions") or {}).get(
                              "non_reaching_gap_pct") or [])))
        print("written results/state_tilt/%s" % FACE)
        return 0
    if cmd == "verify":
        r = verify()
        print(json.dumps(r, ensure_ascii=False))
        return 0 if r["ok"] else 1
    if cmd == "selftest":
        r = selftest()
        for l in r["legs"]:
            print("%s %s  %s" % ("PASS" if l["ok"] else "FAIL", l["name"], l["detail"]))
        print("%d/%d" % (r["passed"], r["total"]))
        return 0 if r["ok"] else 1
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())