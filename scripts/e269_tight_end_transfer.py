"""E269 -- does the tight end of another window transfer as badly as its wide end?

E262/E264/E266/E267/E268 swept the WIDE end (p95) only: borrow another window's p95, judge a row
with it, count the verdicts that move.  Every published arm in E259 also carries a p05, and every
published row carries own_p05 and a verdict_tight, so the tight half of the same transfer question
has never been scored.  The asymmetry is not obvious a priori: the wide end decides rejections on
the side a row sits beyond, the tight end decides how much a row can be over-credited, and both are
drawn from the same shuffle stream but from opposite tails.

Test with the identical machinery and the identical population (the 48 ordered donor/recipient pairs
inside each (leg, base count), no new draws):

  1. does any window's p05 dominate every other window's p05?  "Use the tightest" is a safe single
     number only if one arm's p05 sits at or below every other arm's.
  2. judged with a donor's p05 instead of its own, does a row's tight verdict move -- and if so in
     which direction (a smaller multiplier narrows the band, so a donor p05 above the row's own
     invents rejections rather than losing them).
  3. what does one pooled p05 per (leg, base) do, i.e. the number 'use the tightest' actually
     adopts, and how does the tight move count compare with the wide one already published.

Reads: results/state_tilt/BANDWINDIST-2026-10-29.json (E259 arms) and BANDTRANSFER-2026-10-29.json
(E262 rows + wide-end result).  Writes: results/state_tilt/BANDTIGHT-2026-10-29.json.
No new shuffles, no engine, no admission: measurement only.
"""
from __future__ import print_function

import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e262_p95_transfer_across_windows as e262   # noqa: E402  (arms, rows, judge, direction)

ROOT = e262.ROOT
OUTDIR = e262.OUTDIR

STUDY = "E269_tight_end_transfer"
TITLE = "does the tight end of another window transfer as badly as its wide end?"
CUTOFF = "2026-10-29"
SRC_ARMS = e262.SRC_WIDTH
SRC_ROWS = e262.FACE
FACE = "BANDTIGHT-%s.json" % CUTOFF
LATEST = "bandtight_latest.json"

TOL = e262.TOL
LEGS = e262.LEGS
BASE_COUNTS = e262.BASE_COUNTS

NO_BILL = ("measurement only: E259's published intervals and E262's published rows are re-read; "
           "no shuffle stream is drawn, no band is rebuilt, no engine runs. A tight verdict that "
           "moves here is a statement about the published numbers, not about the market.")

VERDICT_VOCAB = (
    "the_tight_end_is_inert_on_this_population",
    "the_tight_end_transfers_without_moving_a_verdict",
    "the_tight_end_moves_as_the_wide_end_does",
    "the_tight_end_moves_where_the_wide_end_does_not",
    "no_transfer_possible",
    "no_tight_rows_measured",
)

judge = e262.judge
_dir = e262._dir


def flip_multiplier(b, lo, hi):
    """The multiplier at which this row's verdict flips -- ONE number per row.

    band = (lo*m, hi*m) and b sits on one side, so 'outside' reduces to m < m_flip on that side.
    Publishing m_flip is what turns 'no pair moved a verdict' from a tautology into a measurement:
    a window spread of a few percent cannot move a row whose flip sits far outside that spread.
    """
    if b is None or lo is None or hi is None:
        return None
    if b < 0 and lo:
        return b / lo
    if b > 0 and hi:
        return b / hi
    return None


def sensitivity(records, arms, legs=LEGS, base_counts=BASE_COUNTS):
    """Could ANY observed p05 in the group have moved these rows?"""
    out = {}
    for leg in legs:
        for base in base_counts:
            vals = {c: p05_of(arms, c, leg, base) for c in cells_of(arms, leg, base)}
            vals = {c: v for c, v in vals.items() if v is not None}
            rows = [x for x in records if x.get("status") == "measured"
                    and x.get("leg") == leg and x.get("base") == base]
            if len(vals) < 2 or not rows:
                out["%s:%d" % (leg, base)] = {"leg": leg, "base": base, "rows": [],
                                              "reason": "no group spread or no measured row"}
                continue
            lo_m, hi_m = min(vals.values()), max(vals.values())
            recs, could = [], 0
            for x in rows:
                mf = flip_multiplier(x["b"], x["band_lo"], x["band_hi"])
                at_lo = judge(x["b"], x["band_lo"], x["band_hi"], lo_m)
                at_hi = judge(x["b"], x["band_lo"], x["band_hi"], hi_m)
                move = (at_lo != at_hi)
                could += 1 if move else 0
                gap = None
                if mf is not None:
                    # positive = how far OUTSIDE the group's published p05 range the flip sits,
                    # zero = the flip is reachable by a p05 that was actually published here
                    if mf < lo_m:
                        gap = (lo_m / mf - 1.0) * 100.0
                    elif mf > hi_m:
                        gap = (1.0 - hi_m / mf) * 100.0
                    else:
                        gap = 0.0
                recs.append({"index": x["index"], "row": x.get("row"), "b": x["b"],
                             "flip_multiplier": mf, "verdict_at_min_p05": at_lo,
                             "verdict_at_max_p05": at_hi, "could_move": move,
                             "gap_to_p05_range_pct": gap})
            out["%s:%d" % (leg, base)] = {
                "leg": leg, "base": base, "p05_min": lo_m, "p05_max": hi_m,
                "p05_spread_pct": (hi_m / lo_m - 1.0) * 100.0 if lo_m else None,
                "n_rows": len(rows), "n_could_move": could, "rows": recs, "reason": None,
            }
    return out


# ------------------------------------------------------------------ arms
def p05_of(arms, cell, leg, base):
    rec = (arms or {}).get((cell, leg, base))
    return None if not rec else rec.get("p05")


def cells_of(arms, leg, base):
    return sorted({c for (c, l, b) in (arms or {}) if l == leg and b == base})


# ------------------------------------------------------------------ transfer, tight side
def tight_transfer(records, arms, legs=LEGS, base_counts=BASE_COUNTS):
    """For every (leg, base) and every ordered (donor, recipient) pair: which tight verdicts move."""
    out = {}
    for leg in legs:
        for base in base_counts:
            cells = cells_of(arms, leg, base)
            if len(cells) < 2:
                out["%s:%d" % (leg, base)] = {
                    "leg": leg, "base": base, "cells": cells, "pairs": [],
                    "reason": "fewer than two published windows share this (leg, base count)",
                }
                continue
            pairs = []
            for donor in cells:
                for recip in cells:
                    if donor == recip:
                        continue
                    d_p05 = p05_of(arms, donor, leg, base)
                    r_p05 = p05_of(arms, recip, leg, base)
                    rrows = [x for x in records
                             if x.get("status") == "measured" and x.get("cell") == recip
                             and x.get("leg") == leg and x.get("base") == base]
                    moved = []
                    for x in rrows:
                        after = judge(x["b"], x["band_lo"], x["band_hi"], d_p05)
                        before = x.get("verdict_tight")
                        if after is None or before is None:
                            continue
                        if after != before:
                            moved.append({"index": x["index"], "row": x.get("row"),
                                          "b": x["b"], "own_p05": x.get("own_p05"),
                                          "donor_p05": d_p05,
                                          "before": "outside" if before else "inside",
                                          "after": "outside" if after else "inside",
                                          "direction": _dir(before, after)})
                    delta = (None if (d_p05 is None or not r_p05)
                             else (d_p05 / r_p05 - 1.0))
                    pairs.append({
                        "donor": donor, "recipient": recip,
                        "donor_p05": d_p05, "recipient_p05": r_p05,
                        "delta_pct": (None if delta is None else delta * 100.0),
                        "donor_tighter": None if delta is None else bool(delta < 0),
                        "n_rows": len(rrows), "n_moved": len(moved),
                        "moved": moved,
                    })
            out["%s:%d" % (leg, base)] = {"leg": leg, "base": base, "cells": cells,
                                          "pairs": pairs, "reason": None}
    return out


def tight_dominator(arms, leg, base):
    """'Use the tightest' is a safe single number only if one arm's p05 <= every other".

    The wide side asks for a maximum; the tight side asks for a minimum -- the two ends are
    dominated by opposite windows or by neither, and the direction is published, not assumed.
    """
    cells = cells_of(arms, leg, base)
    vals = {c: p05_of(arms, c, leg, base) for c in cells}
    if len(vals) < 2 or any(v is None for v in vals.values()):
        return {"cells": cells, "dominator": None, "max": None, "min": None,
                "spread_pct": None, "reason": "not enough measured arms to rank"}
    hi = max(vals.values())
    lo = min(vals.values())
    bottoms = [c for c, v in vals.items() if abs(v - lo) <= TOL]
    return {"cells": cells, "p05": vals,
            "dominator": bottoms[0] if len(bottoms) == 1 else None,
            "tied_at_min": bottoms if len(bottoms) > 1 else [],
            "max": hi, "min": lo,
            "spread_pct": (hi / lo - 1.0) * 100.0 if lo else None}


def tight_flat(records, arms, legs=LEGS, base_counts=BASE_COUNTS):
    """One number per (leg, base): the pooled MINIMUM p05 is what 'use the tightest' adopts."""
    out = {}
    for leg in legs:
        for base in base_counts:
            vals = {c: p05_of(arms, c, leg, base) for (c, l, b) in (arms or {})
                    if l == leg and b == base}
            vals = {c: v for c, v in vals.items() if v is not None}
            if len(vals) < 2:
                out["%s:%d" % (leg, base)] = {"leg": leg, "base": base,
                                             "reason": "fewer than two measured windows"}
                continue
            hi, lo = max(vals.values()), min(vals.values())
            hi_from = sorted([c for c, v in vals.items() if abs(v - hi) <= TOL])
            lo_from = sorted([c for c, v in vals.items() if abs(v - lo) <= TOL])
            rows = [x for x in records if x.get("status") == "measured"
                    and x.get("leg") == leg and x.get("base") == base]
            moved_lo, moved_hi = [], []
            for x in rows:
                for m, bucket in ((lo, moved_lo), (hi, moved_hi)):
                    after = judge(x["b"], x["band_lo"], x["band_hi"], m)
                    before = x.get("verdict_tight")
                    if after is None or before is None:
                        continue
                    if after != before:
                        bucket.append({"index": x["index"], "cell": x["cell"],
                                       "row": x.get("row"),
                                       "before": "outside" if before else "inside",
                                       "after": "outside" if after else "inside",
                                       "direction": _dir(before, after)})
            out["%s:%d" % (leg, base)] = {
                "leg": leg, "base": base,
                "flat_p05": lo, "flat_p05_from": lo_from,
                "flat_loose_p05": hi, "flat_loose_from": hi_from,
                "n_rows": len(rows),
                "n_moved_at_flat": len(moved_lo), "moved_at_flat": moved_lo,
                "n_moved_at_loose": len(moved_hi), "moved_at_loose": moved_hi,
            }
    return out


# ------------------------------------------------------------------ run
def _stamp():
    import datetime
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def _tally(transfer_block):
    pairs = 0
    moving = 0
    moved_rows = 0
    invented = 0
    lost = 0
    for key in sorted(transfer_block):
        blk = transfer_block[key]
        for p in blk.get("pairs") or []:
            pairs += 1
            if p["n_moved"]:
                moving += 1
                moved_rows += p["n_moved"]
                for m in p["moved"]:
                    if m["direction"] == "rejections_invented":
                        invented += 1
                    elif m["direction"] == "rejections_lost":
                        lost += 1
    return {"pairs": pairs, "pairs_moving_a_verdict": moving, "moved_row_readings": moved_rows,
            "rejections_invented": invented, "rejections_lost": lost}


def _verdict_of(summary, wide):
    if summary["tight_rows_measured"] == 0:
        return "no_tight_rows_measured", "no published row could be judged on the tight end"
    if summary["tight_pairs"] == 0:
        return "no_transfer_possible", "no (leg, base count) carries two windows to swap"
    tm = summary["tight_pairs_moving_a_verdict"]
    wm = summary["wide_pairs_moving_a_verdict"]
    if (tm == 0 and wm > 0 and summary.get("rows_could_move_within_observed_p05_range") == 0):
        return ("the_tight_end_is_inert_on_this_population",
                ("no pair moves AND no measured row could change verdict at any p05 actually "
                 "published for its group (nearest flip sits %.1f%% away from the widest observed "
                 "p05 swing): the tight end cannot transfer BADLY because it cannot move anything "
                 "here, while the wide end moves %d pair(s) -- the instruction is 'do not borrow "
                 "the wide end', and the tight half is untested rather than safe"
                 % (abs(summary.get("nearest_flip_gap_pct") or 0.0), wm)))
    if tm == 0 and wm > 0:
        return ("the_tight_end_transfers_without_moving_a_verdict",
                "the tight end moves nothing on %d pair(s) while the wide end moves %d: the "
                "instruction is 'do not borrow the wide end', not 'do not borrow'"
                % (summary["tight_pairs"], wm))
    if tm > 0 and wm == 0:
        return ("the_tight_end_moves_where_the_wide_end_does_not",
                "the tight end moves %d pair(s) while the wide end moved none: the wide end's "
                "clean transfer does not vouch for the tight end" % tm)
    if tm > max(wm, 0):
        return ("the_tight_end_moves_where_the_wide_end_does_not",
                "the tight end moves MORE pairs (%d) than the wide end (%d) on the same rows"
                % (tm, wm))
    return ("the_tight_end_moves_as_the_wide_end_does",
            "the tight end moves %d pair(s) against the wide end's %d: both ends are borrowable "
            "by the same standard" % (tm, wm))


def run(save=True, outdir=None):
    outdir = outdir or OUTDIR
    arms = e262.arms_from(e262.load(SRC_ARMS))
    wide_face = e262.load(SRC_ROWS)
    # BANDTRANSFER publishes E262's ALREADY-RESOLVED row records (index/leg/base/own_p05/verdicts),
    # not the raw source rows: re-running e262.row_records on them looks for band_draws, misses it
    # and marks all 16 unjudgeable (r1295 pit). Read the published records verbatim.
    records = [dict(r) for r in (wide_face.get("rows") or [])]
    tt = tight_transfer(records, arms)
    tf = tight_flat(records, arms)
    tally = _tally(tt)
    wide_summary = wide_face.get("summary") or {}
    measured = [r for r in records if r.get("status") == "measured"]
    tight_measured = [r for r in measured if r.get("verdict_tight") is not None]
    dom_tight = {"%s:%d" % (l, b): tight_dominator(arms, l, b) for l in LEGS for b in BASE_COUNTS}
    spreads = [v["spread_pct"] for v in dom_tight.values() if v.get("spread_pct") is not None]
    sens = sensitivity(records, arms)
    could_move = sum(v.get("n_could_move") or 0 for v in sens.values())
    gaps = [r["gap_to_p05_range_pct"] for v in sens.values() for r in (v.get("rows") or [])
            if r.get("gap_to_p05_range_pct") is not None]

    summary = {
        "rows": len(records),
        "rows_measured": len(measured),
        "tight_rows_measured": len(tight_measured),
        "tight_rows_outside": sum(1 for r in tight_measured if r.get("verdict_tight") is True),
        "tight_rows_inside": sum(1 for r in tight_measured if r.get("verdict_tight") is False),
        "wide_rows_outside": sum(1 for r in measured if r.get("verdict_wide") is True),
        "tight_pairs": tally["pairs"],
        "tight_pairs_moving_a_verdict": tally["pairs_moving_a_verdict"],
        "tight_moved_row_readings": tally["moved_row_readings"],
        "tight_rejections_invented": tally["rejections_invented"],
        "tight_rejections_lost": tally["rejections_lost"],
        "wide_pairs": wide_summary.get("pairs"),
        "wide_pairs_moving_a_verdict": wide_summary.get("pairs_moving_a_verdict"),
        "wide_rejections_invented": wide_summary.get("rejections_invented"),
        "wide_rejections_lost": wide_summary.get("rejections_lost"),
        "p05_spread_pct_max": max(spreads) if spreads else None,
        "dominators_tight": {k: v.get("dominator") for k, v in dom_tight.items()},
        "dominators_wide": wide_face.get("dominator") or {},
        "flat_moved_at_flat": sum(x.get("n_moved_at_flat") or 0 for x in tf.values()),
        "flat_moved_at_loose": sum(x.get("n_moved_at_loose") or 0 for x in tf.values()),
        "rows_could_move_within_observed_p05_range": could_move,
        "rows_insensitive_to_observed_p05_range": max(len(tight_measured) - could_move, 0),
        "nearest_flip_gap_pct": min(gaps) if gaps else None,
        "tight_end_inert": bool(tally["pairs_moving_a_verdict"] == 0 and could_move == 0),
        "resolution_note": ("%d measured row(s), of which %d could change verdict at some p05 "
                            "actually published for their group: a zero here is a measurement of "
                            "insensitivity, not an untested screen"
                            % (len(tight_measured), could_move)),
    }
    verdict, why = _verdict_of(summary, wide_summary)
    summary["verdict"] = verdict

    out = {
        "study": STUDY,
        "title": TITLE,
        "evidence_cutoff": CUTOFF,
        "generated": _stamp(),
        "no_bill": NO_BILL,
        "source_faces": [SRC_ARMS, SRC_ROWS],
        "frozen_spec": {
            "design": ("read E259's published p05..p95 interval per (window, leg, base count) and "
                       "judge each published row with a donor window's TIGHT end instead of its "
                       "own -- the mirror of E262, on the same rows"),
            "judge_rule": ("verdict = outside(b, band*m) with m the borrowed p05; a smaller "
                           "multiplier NARROWS the band, so a donor p05 above the row's own "
                           "INVENTS a rejection rather than losing one -- direction is published"),
            "dominator_rule": ("'use the tightest' is a safe single number only when one arm's "
                               "p05 is <= every other arm's p05 in the same (leg, base)"),
            "flat_rule": ("one number per (leg, base) = the pooled MINIMUM p05, which is what "
                          "'use the tightest' actually adopts; the pooled maximum is published "
                          "beside it as the loose alternative"),
            "match_rule": ("a transfer is published only within one (leg, base count); the "
                           "multiplier's denominator is the base count itself"),
            "no_new_draws": "no shuffle stream is drawn; every number is a function of the two faces",
            "tolerance": TOL,
            "verdict_rule": ("the tight end 'transfers' only if no pair moves a verdict; a moved "
                             "verdict is published with its direction, never netted out"),
        },
        "summary": summary,
        "dominator_tight": dom_tight,
        "flat_tight": tf,
        "sensitivity": sens,
        "transfer_tight": tt,
        "rows": [
            {"index": r.get("index"), "cell": r.get("cell"), "row": r.get("row"),
             "leg": r.get("leg"), "base": r.get("base"), "b": r.get("b"),
             "band_lo": r.get("band_lo"), "band_hi": r.get("band_hi"),
             "own_p05": r.get("own_p05"), "own_p95": r.get("own_p95"),
             "verdict_tight": r.get("verdict_tight"), "verdict_wide": r.get("verdict_wide"),
             "status": r.get("status")}
            for r in records],
        "verdict": verdict,
        "verdict_reason": why,
    }
    if save:
        _write(out, outdir)
    return out


def _write(face, outdir, tag=""):
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    path = os.path.join(outdir, "BANDTIGHT-%s%s.json" % (face.get("evidence_cutoff"), tag))
    text = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text + "\n")
    with io.open(os.path.join(outdir, LATEST), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text + "\n")
    return path


def verify(outdir=None, tag=""):
    outdir = outdir or OUTDIR
    path = os.path.join(outdir, "BANDTIGHT-%s%s.json" % (CUTOFF, tag))
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


def _arm(p05, p95, cell, leg="self", base=60):
    return (cell, leg, base), {"cell": cell, "leg": leg, "base": base,
                               "p05": p05, "p95": p95}


def _arms(*specs):
    return dict(_arm(*s) for s in specs)


def _row(index, b, lo, hi, leg="self", base=60, cell="a", p05=1.0):
    verdict_tight = judge(b, lo, hi, p05)
    return {"index": index, "row": "r%d" % index, "cell": cell, "leg": leg, "base": base,
            "status": "measured", "b": b, "band_lo": lo, "band_hi": hi,
            "own_p05": p05, "own_p95": 2.0,
            "verdict_tight": verdict_tight, "verdict_wide": judge(b, lo, hi, 2.0)}


def selftest():
    legs = []

    # --- direction: a smaller multiplier narrows the band, so a donor above own invents
    r = _row(0, -1.0, -0.3, 0.3, p05=1.0)          # band (*1.0) = [-0.3, 0.3]; b=-1 outside
    legs.append(_leg(r["verdict_tight"] is True, "own p05=1 leaves b=-1 outside its band"))
    legs.append(_leg(judge(r["b"], r["band_lo"], r["band_hi"], 4.0) is False,
                     "a WIDER multiplier brings b inside (band grows)"))
    legs.append(_leg(judge(0.2, -0.3, 0.3, 1.0) is False
                     and judge(0.2, -0.3, 0.3, 0.5) is True,
                     "a SMALLER multiplier pushes a borderline b outside"))

    # --- pairwise transfer counts a move with its direction
    arms = _arms((1.0, 2.0, "a", "self", 60), (2.0, 2.0, "b", "self", 60))
    rows = [_row(0, -0.5, -0.3, 0.3, cell="a", p05=1.0)]     # own: outside; donor p05=2 -> inside
    tt = tight_transfer(rows, arms)
    blk = tt["self:60"]
    legs.append(_leg(len(blk["pairs"]) == 2, "two ordered pairs from two windows",
                     str(len(blk["pairs"]))))
    donor_b = [p for p in blk["pairs"] if p["donor"] == "b"][0]
    legs.append(_leg(donor_b["n_moved"] == 1, "the donor p05 moves the row",
                     str(donor_b["n_moved"])))
    legs.append(_leg(donor_b["moved"][0]["direction"] == "rejections_lost",
                     "a larger donor p05 widens the band and LOSES a rejection",
                     donor_b["moved"][0]["direction"]))
    donor_a = [p for p in blk["pairs"] if p["donor"] == "a"][0]
    legs.append(_leg(donor_a["n_moved"] == 0, "a recipient judged on its own end cannot move"))
    legs.append(_leg(donor_b["donor_tighter"] is False, "a donor with a larger p05 is not tighter"))

    # --- a single window cannot transfer
    one = tight_transfer(rows, _arms((1.0, 2.0, "a", "self", 60)))
    legs.append(_leg(one["self:60"]["pairs"] == [] and one["self:60"].get("reason"),
                     "one window carries no pair and says why"))

    # --- base counts never mix
    arms2 = _arms((1.0, 2.0, "a", "self", 60), (2.0, 2.0, "b", "self", 200))
    tt2 = tight_transfer([_row(0, -0.5, -0.3, 0.3, cell="a", p05=1.0)], arms2)
    legs.append(_leg(tt2["self:60"]["pairs"] == [] and tt2["self:200"]["pairs"] == [],
                     "two windows at DIFFERENT base counts are never paired"))

    # --- dominator asks for a minimum on the tight side
    arms3 = _arms((1.0, 2.0, "a", "self", 60), (2.0, 2.0, "b", "self", 60))
    d = tight_dominator(arms3, "self", 60)
    legs.append(_leg(d["dominator"] == "a", "'use the tightest' is the arm with the SMALLEST p05",
                     str(d.get("dominator"))))
    legs.append(_leg(abs(d["spread_pct"] - 100.0) < 1e-9, "spread is published as a percentage"))
    legs.append(_leg(d["tied_at_min"] == [], "a strict minimum has no tie"))
    d_tie = tight_dominator(_arms((1.0, 2.0, "a", "self", 60), (1.0, 2.0, "b", "self", 60)),
                            "self", 60)
    legs.append(_leg(d_tie["dominator"] is None and d_tie["tied_at_min"] == ["a", "b"],
                     "a tie publishes both arms and no dominator"))
    legs.append(_leg(tight_dominator(_arms((1.0, 2.0, "a", "self", 60)), "self", 60)
                     ["dominator"] is None,
                     "one arm cannot dominate itself into a safe single number"))

    # --- flat tight adopts the MINIMUM, and discloses its twin
    arms4 = _arms((1.0, 2.0, "a", "self", 60), (2.0, 2.0, "b", "self", 60))
    rows4 = [_row(0, -0.5, -0.3, 0.3, cell="a", p05=1.0)]
    f = tight_flat(rows4, arms4)["self:60"]
    legs.append(_leg(abs(f["flat_p05"] - 1.0) < 1e-12 and f["flat_p05_from"] == ["a"],
                     "'use the tightest' adopts the pooled minimum, not the maximum",
                     str(f.get("flat_p05"))))
    legs.append(_leg(abs(f["flat_loose_p05"] - 2.0) < 1e-12, "the loose twin is published beside it"))
    legs.append(_leg(f["n_moved_at_flat"] == 0, "adopting the row's own p05 moves nothing"))
    legs.append(_leg(f["n_moved_at_loose"] == 1, "the loose twin moves the row"))

    # --- verdict: nothing moves on the tight side -> 'do not borrow the wide end'
    s0 = {"tight_rows_measured": 4, "tight_pairs": 8, "tight_pairs_moving_a_verdict": 0,
          "wide_pairs_moving_a_verdict": 2}
    v, _why = _verdict_of(s0, {})
    legs.append(_leg(v == "the_tight_end_transfers_without_moving_a_verdict",
                     "zero tight moves against nonzero wide moves is the asymmetry verdict", v))
    s1 = dict(s0, tight_pairs_moving_a_verdict=3)
    v, _why = _verdict_of(s1, {})
    legs.append(_leg(v == "the_tight_end_moves_where_the_wide_end_does_not",
                     "tight moves outnumber wide moves -> the wide clean transfer does not vouch", v))
    s2 = dict(s0, tight_pairs_moving_a_verdict=2)
    v, _why = _verdict_of(s2, {})
    legs.append(_leg(v == "the_tight_end_moves_as_the_wide_end_does",
                     "equal move counts -> both ends judged by one standard", v))
    s3 = dict(s0, tight_rows_measured=0)
    v, _why = _verdict_of(s3, {})
    legs.append(_leg(v == "no_tight_rows_measured", "no judgeable row is its own verdict", v))
    s4 = {"tight_rows_measured": 3, "tight_pairs": 0, "tight_pairs_moving_a_verdict": 0,
          "wide_pairs_moving_a_verdict": 0}
    v, _why = _verdict_of(s4, {})
    legs.append(_leg(v == "no_transfer_possible", "no pair at all is not a clean transfer", v))

    # --- tally keeps invented and lost apart
    tt3 = {"x": {"pairs": [{"n_moved": 1, "moved": [{"direction": "rejections_invented"}]},
                           {"n_moved": 0, "moved": []}]}}
    t = _tally(tt3)
    legs.append(_leg(t["pairs"] == 2 and t["pairs_moving_a_verdict"] == 1
                     and t["rejections_invented"] == 1 and t["rejections_lost"] == 0,
                     "the tally separates invented from lost rejections", str(t)))

    # --- the flip multiplier: 'outside' is exactly m < m_flip on the side b sits on
    mf = flip_multiplier(-0.5, -0.3, 0.3)
    legs.append(_leg(abs(mf - (0.5 / 0.3)) < 1e-12, "a negative b flips against the lo edge", str(mf)))
    legs.append(_leg(judge(-0.5, -0.3, 0.3, mf * 0.99) is True
                     and judge(-0.5, -0.3, 0.3, mf * 1.01) is False,
                     "just below m_flip is outside, just above is inside"))
    mf_pos = flip_multiplier(0.15, -0.3, 0.3)
    legs.append(_leg(abs(mf_pos - 0.5) < 1e-12, "a positive b flips against the hi edge", str(mf_pos)))
    legs.append(_leg(flip_multiplier(None, -0.3, 0.3) is None
                     and flip_multiplier(0.1, -0.3, None) is None,
                     "a missing row or edge has no flip multiplier"))

    # --- sensitivity: could ANY observed p05 have moved the row?
    arms5 = _arms((1.0, 2.0, "a", "self", 60), (1.6, 2.0, "b", "self", 60))
    near = _row(0, -0.45, -0.3, 0.3, cell="a", p05=1.0)     # m_flip = 0.45/0.3 = 1.5 (in range)
    far = _row(1, -3.0, -0.3, 0.3, cell="a", p05=1.0)       # m_flip = 10 (far above the range)
    s = sensitivity([near, far], arms5)["self:60"]
    legs.append(_leg(s["n_could_move"] == 1, "only the row whose flip sits inside the range moves",
                     str(s["n_could_move"])))
    legs.append(_leg(abs(s["p05_spread_pct"] - 60.0) < 1e-9, "the group's p05 spread is published",
                     str(s.get("p05_spread_pct"))))
    far_rec = [r for r in s["rows"] if r["index"] == 1][0]
    legs.append(_leg(far_rec["could_move"] is False and far_rec["gap_to_p05_range_pct"] > 0,
                     "a far row publishes a POSITIVE gap, i.e. how far outside the range it sits",
                     str(far_rec["gap_to_p05_range_pct"])))
    legs.append(_leg(sensitivity([], arms5)["self:60"].get("reason"),
                     "no measured row is disclosed, not silently zero"))

    # --- an inert population is a different verdict from a clean transfer
    s_inert = {"tight_rows_measured": 12, "tight_pairs": 48, "tight_pairs_moving_a_verdict": 0,
               "wide_pairs_moving_a_verdict": 2, "rows_could_move_within_observed_p05_range": 0,
               "nearest_flip_gap_pct": 43.5}
    v, _why = _verdict_of(s_inert, {})
    legs.append(_leg(v == "the_tight_end_is_inert_on_this_population",
                     "zero moves with zero could-move rows is inertness, not a clean transfer", v))
    s_live = dict(s_inert, rows_could_move_within_observed_p05_range=3)
    v, _why = _verdict_of(s_live, {})
    legs.append(_leg(v == "the_tight_end_transfers_without_moving_a_verdict",
                     "rows that COULD have moved and did not is the transfer verdict", v))

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
        print("  rows measured %d (tight outside %d / inside %d)"
              % (s["tight_rows_measured"], s["tight_rows_outside"], s["tight_rows_inside"]))
        print("  tight: %d pairs, %d moving, %d invented / %d lost"
              % (s["tight_pairs"], s["tight_pairs_moving_a_verdict"],
                 s["tight_rejections_invented"], s["tight_rejections_lost"]))
        print("  wide : %s pairs, %s moving, %s invented / %s lost"
              % (s["wide_pairs"], s["wide_pairs_moving_a_verdict"],
                 s["wide_rejections_invented"], s["wide_rejections_lost"]))
        print("  flat tight moved %d (loose twin %d)"
              % (s["flat_moved_at_flat"], s["flat_moved_at_loose"]))
        for key in sorted(face["flat_tight"]):
            blk = face["flat_tight"][key]
            if blk.get("reason"):
                print("  %-11s %s" % (key, blk["reason"]))
                continue
            print("  %-11s flat_p05 %.4f from %-12s moved %d/%d"
                  % (key, blk["flat_p05"], ",".join(blk["flat_p05_from"]),
                     blk["n_moved_at_flat"], blk["n_rows"]))
        return 0
    print("usage: e269_tight_end_transfer.py [run|verify|selftest]")
    return 2


if __name__ == "__main__":
    sys.exit(main())