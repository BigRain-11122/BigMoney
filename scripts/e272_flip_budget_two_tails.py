"""E272 -- is one tail closer to mattering than the other, on ONE ruler?

E269 published, per row, the multiplier at which that row's verdict flips and found the
nearest flip 13.5% outside the widest p05 swing its own group publishes.  That measures the
tight half's budget only.  E262's two wide moves say the wide half is at least sometimes
reachable, but nothing yet says how far the other eleven rows sit from it.

The flip multiplier is ONE number per row -- a judgement flips at m_flip whichever tail
supplies m -- so both tails can be placed on the same ruler.  What differs is how much room
the population offers at each tail:

    tight availability = the range of p05 across the windows sharing the row's (leg, base)
    wide  availability = the same range of p95

For each row and each tail: gap = how far m_flip sits outside that tail's published range
(0 = some published arm is at/past the flip), and the NORMALISED gap = gap / that tail's own
spread, i.e. "how many spreads of draw budget before this tail could move this row".  The
tail with the smaller normalised gap is the one a future draw budget should buy resolution
for.  Positive polarity matters and is published, not assumed: a flip above 1 needs a
LARGER multiplier (widening, the wide tail); a flip below 1 needs a smaller one (narrowing,
the tight tail).

Reads (published faces only): BANDWINDIST-2026-10-29.json (E259 arms),
BANDTRANSFER-2026-10-29.json (E262 rows + its moved set), BANDTIGHT-2026-10-29.json (E269's
per-row flip gaps).
Writes: results/state_tilt/BANDFLIPBUDGET-2026-10-29.json (+ bandflipbudget_latest.json).
No new draws, no engine, no admission: measurement only.
"""
from __future__ import print_function

import io
import json
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e262_p95_transfer_across_windows as e262   # noqa: E402  (arms, rows, judge)
import e269_tight_end_transfer as e269            # noqa: E402  (flip_multiplier -- one source)

ROOT = e262.ROOT
OUTDIR = e262.OUTDIR

STUDY = "E272_flip_budget_two_tails"
TITLE = "is one tail closer to mattering than the other, on one ruler?"
CUTOFF = "2026-10-29"
SRC_ARMS = e262.SRC_WIDTH
SRC_ROWS = e262.FACE
SRC_TIGHT = e269.FACE
FACE = "BANDFLIPBUDGET-%s.json" % CUTOFF
LATEST = "bandflipbudget_latest.json"

TOL = e262.TOL
LEGS = e262.LEGS
BASE_COUNTS = e262.BASE_COUNTS

judge = e262.judge
flip_multiplier = e269.flip_multiplier

TAILS = ("tight", "wide")
KEY_OF = {"tight": "p05", "wide": "p95"}

VERDICT_VOCAB = (
    "the_wide_tail_is_the_only_tail_that_can_reach_a_row",
    "the_tight_tail_is_the_only_tail_that_can_reach_a_row",
    "both_tails_reach_at_least_one_row",
    "neither_tail_is_reachable_at_published_spreads",
    "the_wide_tail_is_closer_on_a_normalised_ruler",
    "the_tight_tail_is_closer_on_a_normalised_ruler",
    "the_two_tails_are_equally_out_of_reach",
    "no_rows_measured",
)

NO_BILL = ("measurement only: E259's published p05/p95 arms, E262's published rows and E269's "
           "published flip gaps are re-read; no shuffle stream is drawn, no band is rebuilt, "
           "no engine runs. A flip that is or is not reachable here is a statement about the "
           "published numbers, not about the market.")


# ------------------------------------------------------------------ per-tail availability
def tail_range(arms, leg, base, key):
    """The multiplier range this tail actually offers inside one (leg, base count) group."""
    cells = sorted({c for (c, l, b) in (arms or {}) if l == leg and b == base})
    vals = {}
    for c in cells:
        rec = (arms or {}).get((c, leg, base)) or {}
        v = rec.get(key)
        if v is not None:
            vals[c] = v
    out = {"leg": leg, "base": base, "tail": key, "cells": cells,
           "n_cells": len(vals), "min": None, "max": None, "spread_pct": None,
           "argmin": [], "argmax": [], "reason": None}
    if not vals:
        out["reason"] = "no published %s for this (leg, base count)" % key
        return out
    lo_m, hi_m = min(vals.values()), max(vals.values())
    out["min"] = lo_m
    out["max"] = hi_m
    out["argmin"] = sorted(c for c, v in vals.items() if v == lo_m)
    out["argmax"] = sorted(c for c, v in vals.items() if v == hi_m)
    out["spread_pct"] = (hi_m / lo_m - 1.0) * 100.0 if lo_m else None
    return out


def gap_to_flip_pct(mf, lo_m, hi_m):
    """How far the flip sits outside a tail's published range, in percent of the flip.

    Same convention as E269's published gap_to_p05_range_pct (one formula, two faces):
    zero = the flip is reachable by a multiplier this group actually published.
    """
    if mf is None or lo_m is None or hi_m is None:
        return None
    if not lo_m or mf <= 0:
        return None
    if mf < lo_m:
        return (lo_m / mf - 1.0) * 100.0
    if mf > hi_m:
        return (1.0 - hi_m / mf) * 100.0
    return 0.0


def normalised_gap(gap_pct, spread_pct):
    """Gap expressed in the spreads that tail actually offers -- the one ruler."""
    if gap_pct is None:
        return None, "no gap to normalise"
    if spread_pct is None:
        return None, "no published spread at this tail"
    if spread_pct <= 0:
        return None, "this tail publishes a single multiplier (spread 0): nothing to normalise against"
    return gap_pct / spread_pct, None


def flip_direction(mf):
    """Which way a multiplier has to move before this row's verdict changes."""
    if mf is None:
        return None
    if abs(mf - 1.0) <= TOL:
        return "boundary"
    return "widening_reenters" if mf > 1.0 else "narrowing_escapes"


def tail_budget_dict(mf, tail_range_rec):
    """One row's reading against one tail."""
    lo_m, hi_m = tail_range_rec.get("min"), tail_range_rec.get("max")
    gap = gap_to_flip_pct(mf, lo_m, hi_m)
    norm, note = normalised_gap(gap, tail_range_rec.get("spread_pct"))
    reachable = (gap is not None and gap <= TOL)
    # an exact tie at the edge is INSIDE (e257.outside is strict), so "reachable" needs
    # a published multiplier strictly past the flip
    strict = bool(reachable and hi_m is not None and mf is not None and hi_m > mf + TOL)
    below = bool(reachable and lo_m is not None and mf is not None and lo_m < mf - TOL)
    return {
        "tail": tail_range_rec.get("tail"),
        "multiplier_min": lo_m,
        "multiplier_max": hi_m,
        "spread_pct": tail_range_rec.get("spread_pct"),
        "n_cells": tail_range_rec.get("n_cells"),
        "argmin": tail_range_rec.get("argmin"),
        "argmax": tail_range_rec.get("argmax"),
        "gap_pct": gap,
        "normalised_gap": norm,
        "normalised_note": note,
        "reachable": bool(reachable),
        "reachable_strict": strict,
        "reachable_from_below": below,
        "unavailable": tail_range_rec.get("reason"),
    }


def closer_tail(tight, wide):
    """Which tail's budget is closer, on the normalised ruler.  Never nets a tail away."""
    nt, nw = tight.get("normalised_gap"), wide.get("normalised_gap")
    if nt is None and nw is None:
        return None, ("neither tail is normalisable (%s / %s)"
                      % (tight.get("normalised_note"), wide.get("normalised_note")))
    if nt is None:
        return "wide", "only the wide tail has a measurable spread here"
    if nw is None:
        return "tight", "only the tight tail has a measurable spread here"
    if abs(nt - nw) <= TOL:
        return "tie", "both tails sit the same number of spreads away"
    return ("wide" if nw < nt else "tight"), None


def row_budget(records, arms, legs=LEGS, base_counts=BASE_COUNTS):
    """Per (leg, base count) block: every measured row read against both tails."""
    out = {}
    for leg in legs:
        for base in base_counts:
            key = "%s:%d" % (leg, base)
            rng = {t: tail_range(arms, leg, base, KEY_OF[t]) for t in TAILS}
            rows = [x for x in records
                    if x.get("status") == "measured"
                    and x.get("leg") == leg and x.get("base") == base]
            recs = []
            for x in rows:
                mf = flip_multiplier(x.get("b"), x.get("band_lo"), x.get("band_hi"))
                tb = tail_budget_dict(mf, dict(rng["tight"], tail="tight"))
                wb = tail_budget_dict(mf, dict(rng["wide"], tail="wide"))
                closer, why = closer_tail(tb, wb)
                recs.append({
                    "index": x.get("index"), "cell": x.get("cell"), "row": x.get("row"),
                    "leg": leg, "base": base, "b": x.get("b"),
                    "band_lo": x.get("band_lo"), "band_hi": x.get("band_hi"),
                    "own_p05": x.get("own_p05"), "own_p95": x.get("own_p95"),
                    "verdict_tight": x.get("verdict_tight"),
                    "verdict_wide": x.get("verdict_wide"),
                    "flip_multiplier": mf,
                    "flip_direction": flip_direction(mf),
                    "margin_wide_published": x.get("margin_wide"),
                    "tight": tb, "wide": wb,
                    "closer_tail": closer, "closer_note": why,
                })
            out[key] = {"leg": leg, "base": base, "n_rows": len(recs),
                        "tight_range": rng["tight"], "wide_range": rng["wide"],
                        "rows": recs}
    return out


# ------------------------------------------------------------------ summary / verdict
def _all_rows(blocks):
    return [r for k in sorted(blocks) for r in blocks[k]["rows"]]


def summary_of(blocks, arms, records):
    rows = _all_rows(blocks)
    measured = [x for x in records if x.get("status") == "measured"]
    all_p05 = [v.get("p05") for v in (arms or {}).values() if v.get("p05") is not None]
    all_p95 = [v.get("p95") for v in (arms or {}).values() if v.get("p95") is not None]
    reach_tight = [r["index"] for r in rows if r["tight"]["reachable_strict"]]
    reach_wide = [r["index"] for r in rows if r["wide"]["reachable_strict"]]
    nt = [r["tight"]["normalised_gap"] for r in rows if r["tight"]["normalised_gap"] is not None]
    nw = [r["wide"]["normalised_gap"] for r in rows if r["wide"]["normalised_gap"] is not None]
    gaps_tight = [r["tight"]["gap_pct"] for r in rows if r["tight"]["gap_pct"] is not None]
    gaps_wide = [r["wide"]["gap_pct"] for r in rows if r["wide"]["gap_pct"] is not None]
    nearest = None
    for r in rows:
        for t in TAILS:
            g = r[t]["gap_pct"]
            if g is None:
                continue
            if nearest is None or g < nearest["gap_pct"]:
                nearest = {"index": r["index"], "tail": t, "gap_pct": g}
    return {
        "rows": len(records),
        "rows_measured": len(measured),
        "rows_unjudgeable": len(records) - len(measured),
        "rows_scored": len(rows),
        "rows_flip_needs_widening": sum(1 for r in rows if r["flip_direction"] == "widening_reenters"),
        "rows_flip_needs_narrowing": sum(1 for r in rows if r["flip_direction"] == "narrowing_escapes"),
        "rows_flip_on_the_boundary": sum(1 for r in rows if r["flip_direction"] == "boundary"),
        "rows_without_flip_multiplier": sum(1 for r in rows if r["flip_multiplier"] is None),
        "published_p05_floor": min(all_p05) if all_p05 else None,
        "published_p95_ceiling": max(all_p95) if all_p95 else None,
        "arms_where_p95_exceeds_p05": sum(1 for v in (arms or {}).values()
                                          if v.get("p95") is not None and v.get("p05") is not None
                                          and v["p95"] > v["p05"]),
        "arms_measured": len(arms or {}),
        "rows_flip_below_published_multiplier_floor": sum(
            1 for r in rows
            if r["flip_multiplier"] is not None and all_p05
            and r["flip_multiplier"] < min(all_p05) - TOL),
        "rows_reachable_tight": len(reach_tight),
        "rows_reachable_wide": len(reach_wide),
        "rows_reachable_either": len(set(reach_tight) | set(reach_wide)),
        "reachable_tight_indices": sorted(reach_tight),
        "reachable_wide_indices": sorted(reach_wide),
        "rows_wide_closer": sum(1 for r in rows if r["closer_tail"] == "wide"),
        "rows_tight_closer": sum(1 for r in rows if r["closer_tail"] == "tight"),
        "rows_closer_tie": sum(1 for r in rows if r["closer_tail"] == "tie"),
        "rows_closer_unmeasured": sum(1 for r in rows if r["closer_tail"] is None),
        "tight_normalised_gap_median": statistics.median(nt) if nt else None,
        "wide_normalised_gap_median": statistics.median(nw) if nw else None,
        "tight_gap_pct_median": statistics.median(gaps_tight) if gaps_tight else None,
        "wide_gap_pct_median": statistics.median(gaps_wide) if gaps_wide else None,
        "nearest_flip": nearest,
        "tight_tails_unmeasurable": sum(1 for r in rows if r["tight"]["normalised_gap"] is None),
        "wide_tails_unmeasurable": sum(1 for r in rows if r["wide"]["normalised_gap"] is None),
    }


def verdict_of(summary):
    if not summary.get("rows_measured"):
        return "no_rows_measured", "no measured row carries a coefficient and a band"
    rt, rw = summary.get("rows_reachable_tight") or 0, summary.get("rows_reachable_wide") or 0
    wide_c, tight_c = summary.get("rows_wide_closer") or 0, summary.get("rows_tight_closer") or 0
    tie = empty = "%d of %d scored row(s) put the wide tail closer on the normalised ruler, " \
                  "%d the tight tail, %d tie" % (wide_c, summary.get("rows_scored") or 0,
                                                 tight_c, summary.get("rows_closer_tie") or 0)
    reach = ("%d row(s) sit at a published multiplier past their flip: wide %r / tight %r"
             % (summary.get("rows_reachable_either") or 0,
                summary.get("reachable_wide_indices"), summary.get("reachable_tight_indices")))
    floor = ("every published p05 is >= %.4f while %d of %d flips need a multiplier LARGER "
             "than 1 (%s)"
             % (summary.get("published_p05_floor") or 0.0,
                summary.get("rows_flip_needs_widening") or 0,
                summary.get("rows_scored") or 0,
                "so a smaller multiplier cannot re-enter them" if
                (summary.get("rows_reachable_tight") or 0) == 0 else "tight side not excluded"))
    if rw > 0 and rt == 0:
        return ("the_wide_tail_is_the_only_tail_that_can_reach_a_row",
                "%s; %s; %s -- the tight end is inert here, but inert because the population "
                "never publishes a narrowing multiplier, not because the tight tail is safe"
                % (reach, floor, tie))
    if rt > 0 and rw == 0:
        return ("the_tight_tail_is_the_only_tail_that_can_reach_a_row",
                "%s; %s; %s" % (reach, floor, tie))
    if rt > 0 and rw > 0:
        return ("both_tails_reach_at_least_one_row", "%s; %s; %s" % (reach, floor, tie))
    # neither tail is reachable: the ruler still ranks them
    if wide_c > tight_c:
        return ("the_wide_tail_is_closer_on_a_normalised_ruler",
                "%s; %s; %s" % (reach, floor, tie))
    if tight_c > wide_c:
        return ("the_tight_tail_is_closer_on_a_normalised_ruler",
                "%s; %s; %s" % (reach, floor, tie))
    return ("the_two_tails_are_equally_out_of_reach", "%s; %s; %s" % (reach, floor, tie))


# ------------------------------------------------------------------ run
def _stamp():
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def run(save=True, outdir=None):
    outdir = outdir or OUTDIR
    arms = e262.arms_from(e262.load(SRC_ARMS))
    wide_face = e262.load(SRC_ROWS)
    # BANDTRANSFER publishes E262's ALREADY-RESOLVED row records, not raw source rows
    # (r1295 pit): read them verbatim instead of re-running row_records.
    records = [dict(r) for r in (wide_face.get("rows") or [])]
    blocks = row_budget(records, arms)
    summary = summary_of(blocks, arms, records)
    verdict, why = verdict_of(summary)
    summary["verdict"] = verdict
    summary["wide_face_verdict"] = wide_face.get("verdict")

    out = {
        "study": STUDY,
        "title": TITLE,
        "evidence_cutoff": CUTOFF,
        "generated": _stamp(),
        "no_bill": NO_BILL,
        "source_faces": [SRC_ARMS, SRC_ROWS, SRC_TIGHT],
        "frozen_spec": {
            "design": ("one flip multiplier per row (E269's flip_multiplier, imported not "
                       "re-implemented), then each tail's published multiplier range in the "
                       "row's own (leg, base count) placed on it"),
            "tight_availability": "the range of p05 across the windows sharing (leg, base)",
            "wide_availability": "the same range of p95",
            "gap_rule": ("gap = 0 when the flip sits inside the range, else the distance to the "
                         "nearer end as a percent of the flip (E269's published convention)"),
            "normalised_rule": ("normalised gap = gap_pct / that tail's own spread_pct -- the "
                               "number of spreads of draw budget before this tail could matter; "
                               "a tail publishing one multiplier has spread 0 and is reported "
                               "unmeasurable rather than infinite"),
            "reachable_rule": ("reachable_strict requires a published multiplier STRICTLY past the "
                               "flip, because e257.outside is strict: a multiplier exactly at the "
                               "flip leaves the row inside"),
            "polarity_rule": ("a flip above 1 needs a LARGER multiplier (widening, the wide tail); "
                              "below 1 needs a smaller one (narrowing, the tight tail); direction "
                              "is published per row, never assumed"),
            "match_rule": "a tail's range is only taken from windows sharing the row's (leg, base count)",
            "no_new_draws": "no shuffle stream is drawn; every number is a function of the faces",
            "tolerance": TOL,
        },
        "summary": summary,
        "tail_budget": blocks,
        "verdict": verdict,
        "verdict_reason": why,
    }
    if save:
        _write(out, outdir)
    return out


def _write(face, outdir, tag=""):
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    text = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
    path = os.path.join(outdir, "BANDFLIPBUDGET-%s%s.json" % (face.get("evidence_cutoff"), tag))
    for p in (path, os.path.join(outdir, LATEST)):
        with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text + "\n")
    return path


def cross_checks(face, arms, wide_face, tight_face):
    """Re-derive the readings from the OTHER published faces -- verify, not self-agreement."""
    problems = []
    rows = _all_rows(face["tail_budget"])
    s = face["summary"]

    if len(rows) != (s.get("rows_measured") or 0):
        problems.append("scored %d row(s) against %s measured in the summary"
                        % (len(rows), s.get("rows_measured")))
    if (s.get("rows_measured") or 0) != ((wide_face.get("summary") or {}).get("rows_measured")):
        problems.append("measured-row count disagrees with BANDTRANSFER")

    # 1. the tails must be ordered, or 'wider end' is not a tail comparison at all
    bad_arms = [k for k, v in arms.items()
                if v.get("p05") is not None and v.get("p95") is not None and not v["p95"] > v["p05"]]
    if bad_arms:
        problems.append("arm(s) whose p95 does not exceed p05: %r" % (bad_arms[:3],))

    # 2. the tight reading must agree with E269's published per-row gap (one formula, two faces)
    published = {}
    for blk in (tight_face.get("sensitivity") or {}).values():
        for r in (blk.get("rows") or []):
            if r.get("gap_to_p05_range_pct") is not None:
                published[r.get("index")] = r["gap_to_p05_range_pct"]
    compared = 0
    for r in rows:
        got = r["tight"]["gap_pct"]
        want = published.get(r["index"])
        if want is None and got is None:
            continue
        if want is None or got is None:
            problems.append("row %s: tight gap published as %r but read as %r"
                            % (r["index"], want, got))
            continue
        compared += 1
        if abs(got - want) > 1e-9:
            problems.append("row %s: tight gap %r disagrees with E269's published %r"
                            % (r["index"], got, want))
    if compared < 6:
        problems.append("only %d row(s) could be compared with E269's published gaps" % compared)

    # 3. the reachable set must contain every row E262 actually moved (soundness, not equality:
    #    a zero gap is necessary for a move; it was also sufficient here and that is disclosed)
    moved = sorted({m.get("index")
                    for blk in (wide_face.get("transfer") or {}).values()
                    for p in (blk.get("pairs") or [])
                    for m in (p.get("moved") or []) if m.get("index") is not None})
    reach_wide = sorted(s.get("reachable_wide_indices") or [])
    missing = [i for i in moved if i not in reach_wide]
    if missing:
        problems.append("rows %r moved under E262 but are not marked wide-reachable here" % (missing,))
    if moved != reach_wide:
        # disclosed, not a failure: publish the difference as a summary field tripwire
        problems.append("wide-reachable set %r != E262's moved set %r (must be disclosed)"
                        % (reach_wide, moved))

    # 4. polarity: a flip above 1 must judge as OUTSIDE at m=1 and inside when widened past it
    for r in rows:
        mf = r["flip_multiplier"]
        if mf is None:
            continue
        if mf > 1.0 + TOL:
            if judge(r["b"], r["band_lo"], r["band_hi"], 1.0) is not True:
                problems.append("row %s: flip %.6f > 1 but the row is not outside at m=1"
                                % (r["index"], mf))
            if judge(r["b"], r["band_lo"], r["band_hi"], mf * 1.01) is not False:
                problems.append("row %s: widening past its flip does not bring it inside"
                                % (r["index"],))
        elif mf < 1.0 - TOL:
            if judge(r["b"], r["band_lo"], r["band_hi"], 1.0) is not False:
                problems.append("row %s: flip %.6f < 1 but the row is not inside at m=1"
                                % (r["index"], mf))

    # 5. the comparison must never point at a tail it did not measure
    for r in rows:
        c = r["closer_tail"]
        if c in TAILS and r[c]["normalised_gap"] is None:
            problems.append("row %s: closer_tail=%r but that tail is not normalisable"
                            % (r["index"], c))

    # 6. counts must sum to the population, not to some subset
    parts = ((s.get("rows_wide_closer") or 0) + (s.get("rows_tight_closer") or 0)
             + (s.get("rows_closer_tie") or 0) + (s.get("rows_closer_unmeasured") or 0))
    if parts != len(rows):
        problems.append("closer-tail counts sum to %d over %d scored row(s)" % (parts, len(rows)))
    return problems


def verify(outdir=None, tag=""):
    outdir = outdir or OUTDIR
    path = os.path.join(outdir, "BANDFLIPBUDGET-%s%s.json" % (CUTOFF, tag))
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
    if not problems:
        problems.extend(cross_checks(got, e262.arms_from(e262.load(SRC_ARMS)),
                                     e262.load(SRC_ROWS), e262.load(SRC_TIGHT)))
    return problems


# ------------------------------------------------------------------ selftest
def _leg(ok, name, detail=None):
    return {"leg": name, "ok": bool(ok), "detail": detail}


def _arm(p05, p95, cell, leg="self", base=60):
    return (cell, leg, base), {"cell": cell, "leg": leg, "base": base,
                               "p05": p05, "p95": p95}


def _arms(*specs):
    return dict(_arm(*s) for s in specs)


def _row(index, b, lo, hi, leg="self", base=60, cell="a", p05=1.0, p95=2.0):
    return {"index": index, "row": "r%d" % index, "cell": cell, "leg": leg, "base": base,
            "status": "measured", "b": b, "band_lo": lo, "band_hi": hi,
            "own_p05": p05, "own_p95": p95,
            "verdict_tight": judge(b, lo, hi, p05), "verdict_wide": judge(b, lo, hi, p95)}


def selftest():
    legs = []

    # --- the gap ruler: inside is 0, outside is a percentage of the flip, no flip is no gap
    legs.append(_leg(gap_to_flip_pct(2.0, 1.0, 1.5) == 25.0,
                     "a flip above the range reports the distance to its max", str(gap_to_flip_pct(2.0, 1.0, 1.5))))
    legs.append(_leg(abs(gap_to_flip_pct(0.8, 1.0, 1.5) - 25.0) < 1e-12,
                     "a flip below the range reports the distance to its min",
                     str(gap_to_flip_pct(0.8, 1.0, 1.5))))
    legs.append(_leg(gap_to_flip_pct(1.2, 1.0, 1.5) == 0.0,
                     "a flip inside the range has zero gap"))
    legs.append(_leg(gap_to_flip_pct(None, 1.0, 1.5) is None
                     and gap_to_flip_pct(1.2, None, 1.5) is None,
                     "a missing flip or end has no gap"))
    legs.append(_leg(gap_to_flip_pct(1.2, 0.0, 1.5) is None,
                     "a zero min cannot be divided by"))

    # --- the normalised ruler: gap / that tail's own spread, and a zero spread is not infinite
    n, note = normalised_gap(5.0, 10.0)
    legs.append(_leg(abs(n - 0.5) < 1e-12, "a 5% gap on a 10% spread is half a spread", str(n)))
    n0, note0 = normalised_gap(5.0, 0.0)
    legs.append(_leg(n0 is None and note0 and "spread 0" in note0,
                     "a single-multiplier tail is unmeasurable, not infinite", str(note0)))
    legs.append(_leg(normalised_gap(None, 10.0)[0] is None, "no gap -> no normalised gap"))

    # --- polarity is published, and it decides which tail can possibly reach the row
    legs.append(_leg(flip_direction(2.33) == "widening_reenters", "a flip above 1 needs widening"))
    legs.append(_leg(flip_direction(0.63) == "narrowing_escapes", "a flip below 1 needs narrowing"))
    legs.append(_leg(flip_direction(1.0) == "boundary", "a flip at 1 is a boundary case"))
    legs.append(_leg(flip_direction(None) is None, "no flip -> no direction"))
    legs.append(_leg(judge(-0.5, -0.3, 0.3, 1.0) is True and judge(-0.4, -0.3, 0.3, 1.5) is False,
                     "the polarity claim matches the judge it is asserted against"))

    # --- tail availability is read per (leg, base count) and publishes its extremes
    arms = _arms((1.0, 1.6, "a"), (1.1, 2.0, "b"), (0.95, 1.9, "c"))
    tr = tail_range(arms, "self", 60, "p05")
    legs.append(_leg(abs(tr["min"] - 0.95) < 1e-12 and abs(tr["spread_pct"] - (1.1 / 0.95 - 1) * 100) < 1e-9,
                     "the tight range publishes min and spread", str(tr["spread_pct"])))
    legs.append(_leg(tr["argmin"] == ["c"] and tr["argmax"] == ["b"],
                     "argmin/argmax name the arms that hold the ends",
                     "%r/%r" % (tr["argmin"], tr["argmax"])))
    legs.append(_leg(tail_range(arms, "self", 60, "p95")["max"] == 2.0, "the wide range is a separate range"))
    legs.append(_leg(tail_range(arms, "self", 200, "p05")["reason"] is not None,
                     "a group with no published arm says why instead of reporting a range"))
    deg = tail_range(_arms((1.0, 1.5, "a"), (1.0, 1.7, "b")), "self", 60, "p05")
    legs.append(_leg(deg["spread_pct"] == 0.0 and deg["argmin"] == ["a", "b"],
                     "all-tied ends publish spread 0 and both arms (the cross:200 shape)"))
    mixed = _arms((1.0, 1.5, "a"), (None, 1.7, "b"))
    legs.append(_leg(tail_range(mixed, "self", 60, "p05")["n_cells"] == 1,
                     "an arm with no value at this tail is not counted as a cell"))

    # --- one row, both tails: the cheaper tail on the normalised ruler wins
    arms2 = _arms((1.00, 1.60, "a"), (1.10, 2.00, "b"))
    b = _row(0, -0.60, -0.30, 0.30, cell="a")            # flip = 0.60/0.30 = 2.0
    blk = row_budget([b], arms2)["self:60"]
    rec = blk["rows"][0]
    legs.append(_leg(abs(rec["flip_multiplier"] - 2.0) < 1e-12, "the row's flip is one number",
                     str(rec["flip_multiplier"])))
    legs.append(_leg(abs(rec["wide"]["gap_pct"] - 0.0) < 1e-12,
                     "a flip inside the wide range has zero wide gap", str(rec["wide"]["gap_pct"])))
    legs.append(_leg(rec["wide"]["reachable"] is True and rec["wide"]["reachable_strict"] is False,
                     "a flip sitting exactly on a published end is reachable but NOT strictly past it",
                     "%r/%r" % (rec["wide"]["reachable"], rec["wide"]["reachable_strict"])))
    legs.append(_leg(rec["tight"]["gap_pct"] > 0 and rec["tight"]["reachable"] is False,
                     "the same flip is out of reach of the tight tail", str(rec["tight"]["gap_pct"])))
    legs.append(_leg(rec["closer_tail"] == "wide", "the closer tail is the wide one here",
                     str(rec["closer_tail"])))
    legs.append(_leg(abs(rec["wide"]["normalised_gap"] - 0.0) < 1e-12
                     and rec["tight"]["normalised_gap"] > 0,
                     "normalised gaps are published per tail",
                     "%r/%r" % (rec["tight"]["normalised_gap"], rec["wide"]["normalised_gap"])))
    legs.append(_leg(sum(1 for t in TAILS if rec[t]["gap_pct"] is not None) == 2,
                     "both tails are scored for a normal row"))

    # --- base counts never mix, and a row is never scored against another base's range
    arms3 = _arms((1.0, 1.6, "a"), (1.1, 2.0, "b"), (1.0, 1.6, "a", "self", 200), (1.5, 3.0, "b", "self", 200))
    blk3 = row_budget([_row(0, -0.60, -0.30, 0.30, cell="a", base=200)], arms3)["self:200"]
    legs.append(_leg(abs(blk3["tight_range"]["min"] - 1.0) < 1e-12
                     and abs(blk3["tight_range"]["max"] - 1.5) < 1e-12,
                     "base 200 ranges come only from base 200 arms",
                     "%r..%r" % (blk3["tight_range"]["min"], blk3["tight_range"]["max"])))

    # --- an unjudgeable row is carried, never scored
    unj = {"index": 9, "status": "unjudgeable", "cell": "x", "leg": "self", "base": 60,
           "b": None, "band_lo": None, "band_hi": None}
    blk4 = row_budget([unj], arms2)["self:60"]
    legs.append(_leg(blk4["n_rows"] == 0, "an unjudgeable row is not scored", str(blk4["n_rows"])))

    # --- a row without a band is not silently dropped from the population count
    recs5 = [unj, b]
    s5 = summary_of(row_budget(recs5, arms2), arms2, recs5)
    legs.append(_leg(s5["rows"] == 2 and s5["rows_measured"] == 1 and s5["rows_unjudgeable"] == 1,
                     "the population keeps its unjudgeable rows",
                     "%r/%r/%r" % (s5["rows"], s5["rows_measured"], s5["rows_unjudgeable"])))

    # --- verdict: reachable-by-one-tail only, neither, and none at all
    v, _ = verdict_of({"rows_measured": 3, "rows_reachable_tight": 0, "rows_reachable_wide": 1,
                       "reachable_wide_indices": [1], "reachable_tight_indices": [],
                       "rows_scored": 3, "rows_wide_closer": 2, "rows_tight_closer": 1,
                       "rows_closer_tie": 0, "published_p05_floor": 1.0,
                       "rows_flip_needs_widening": 2})
    legs.append(_leg(v == "the_wide_tail_is_the_only_tail_that_can_reach_a_row",
                     "a reachable wide end and an inert tight end is the wide-only verdict", v))
    v, _ = verdict_of({"rows_measured": 3, "rows_reachable_tight": 1, "rows_reachable_wide": 0,
                       "reachable_wide_indices": [], "reachable_tight_indices": [2],
                       "rows_scored": 3, "rows_wide_closer": 1, "rows_tight_closer": 2,
                       "rows_closer_tie": 0, "published_p05_floor": 0.9,
                       "rows_flip_needs_widening": 1})
    legs.append(_leg(v == "the_tight_tail_is_the_only_tail_that_can_reach_a_row",
                     "the mirror case is not implied by the first", v))
    v, _ = verdict_of({"rows_measured": 3, "rows_reachable_tight": 1, "rows_reachable_wide": 1,
                       "reachable_wide_indices": [3], "reachable_tight_indices": [1],
                       "rows_scored": 3, "rows_wide_closer": 2, "rows_tight_closer": 1,
                       "rows_closer_tie": 0, "published_p05_floor": 0.9,
                       "rows_flip_needs_widening": 1})
    legs.append(_leg(v == "both_tails_reach_at_least_one_row", "both tails reaching is its own verdict", v))
    v, _ = verdict_of({"rows_measured": 2, "rows_reachable_tight": 0, "rows_reachable_wide": 0,
                       "rows_scored": 2, "rows_wide_closer": 1, "rows_tight_closer": 1,
                       "rows_closer_tie": 0, "published_p05_floor": 1.0,
                       "rows_flip_needs_widening": 0})
    legs.append(_leg(v == "the_two_tails_are_equally_out_of_reach",
                     "neither reachable and a tied ruler is published as a tie", v))
    v, _ = verdict_of({"rows_measured": 0})
    legs.append(_leg(v == "no_rows_measured", "an empty population is not a verdict about tails", v))

    # --- the closer-tail ruler never points at an unmeasured tail
    t = tail_budget_dict(2.0, {"tail": "tight", "min": 1.0, "max": 1.0, "spread_pct": 0.0,
                               "n_cells": 2, "argmin": ["a", "b"], "argmax": ["a", "b"]})
    w = tail_budget_dict(2.0, {"tail": "wide", "min": 1.5, "max": 2.2, "spread_pct": 46.6,
                               "n_cells": 2, "argmin": ["a"], "argmax": ["b"]})
    c, why = closer_tail(t, w)
    legs.append(_leg(c == "wide" and why and "only the wide" in why,
                     "an unmeasurable tail is named, not silently dropped", why))
    c2, why2 = closer_tail(t, dict(w, normalised_gap=None))
    legs.append(_leg(c2 is None and why2, "both unmeasurable -> no closer tail, with a reason"))
    c3, _ = closer_tail(dict(t, normalised_gap=1.0), dict(w, normalised_gap=1.0))
    legs.append(_leg(c3 == "tie", "equal normalised gaps are a tie, not a coin flip"))

    # --- the face's own vocabulary stays closed
    legs.append(_leg(len(set(VERDICT_VOCAB)) == len(VERDICT_VOCAB), "verdict vocabulary is unique"))
    live, _ = verdict_of({"rows_measured": 1, "rows_reachable_tight": 0, "rows_reachable_wide": 1,
                          "reachable_wide_indices": [0], "reachable_tight_indices": [],
                          "rows_scored": 1, "rows_wide_closer": 1, "rows_tight_closer": 0,
                          "rows_closer_tie": 0, "published_p05_floor": 1.0,
                          "rows_flip_needs_widening": 1})
    legs.append(_leg(live in VERDICT_VOCAB, "every emitted verdict is in the vocabulary", live))

    ok = all(l["ok"] for l in legs)
    print("selftest %d/%d %s" % (sum(1 for l in legs if l["ok"]), len(legs), "OK" if ok else "FAIL"))
    for l in legs:
        if not l["ok"]:
            print("  FAIL", l["leg"], l["detail"])
    return 0 if ok else 1


# ------------------------------------------------------------------ CLI
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
        print("%s" % face["verdict"])
        print("  %s" % face["verdict_reason"])
        print("  rows %d measured / %d unjudgeable; flips need widening %d, narrowing %d"
              % (s["rows_measured"], s["rows_unjudgeable"],
                 s["rows_flip_needs_widening"], s["rows_flip_needs_narrowing"]))
        print("  reachable now: wide %r / tight %r" % (s["reachable_wide_indices"],
                                                       s["reachable_tight_indices"]))
        print("  normalised-gap medians: tight %s / wide %s"
              % (("%.2f" % s["tight_normalised_gap_median"])
                 if s["tight_normalised_gap_median"] is not None else "n/a",
                 ("%.2f" % s["wide_normalised_gap_median"])
                 if s["wide_normalised_gap_median"] is not None else "n/a"))
        for key in sorted(face["tail_budget"]):
            blk = face["tail_budget"][key]
            for r in blk["rows"]:
                print("  %-14s %-4s %-10s mf %6.3f %-17s tight %7.2f%% (%8s) wide %7.2f%% (%8s) -> %s"
                      % (r["cell"], r["leg"], str(r["row"])[:9], r["flip_multiplier"] or 0.0,
                         r["flip_direction"] or "-",
                         r["tight"]["gap_pct"] if r["tight"]["gap_pct"] is not None else -1,
                         ("%.2f" % r["tight"]["normalised_gap"])
                         if r["tight"]["normalised_gap"] is not None else "n/a",
                         r["wide"]["gap_pct"] if r["wide"]["gap_pct"] is not None else -1,
                         ("%.2f" % r["wide"]["normalised_gap"])
                         if r["wide"]["normalised_gap"] is not None else "n/a",
                         r["closer_tail"] or "-"))
        return 0
    print("usage: e272_flip_budget_two_tails.py [run|verify|selftest]")
    return 2


if __name__ == "__main__":
    sys.exit(main())