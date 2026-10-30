"""E266 -- does the wide-end threshold screen hold on rows it was not fitted on?

E265 turned "do not borrow another window's wide end" into a per-row screen: a row's verdict flips
at the multiplier

    t = |b| / max(|lo|, |hi|)          (E264/E265 form)

so any donor whose p95 exceeds t is supposed to flip that row.  E264 ranked the 12 read rows that
way and found both rows E262 actually moved inside the top 3, with a third-closest row that did not
move.  The claim under test here is the screen itself, not the ranking: over the 48 ordered pairs
E262 already published (no new draws, no new panel), is "donor p95 > t" exactly the set of
(row, donor) pairs that moved a verdict?

Three readings are compared against the published moves:

  S1 single      donor_p95 > t                      -- the screen as written
  S2 guarded     donor_p95 > t and own_p95 < t       -- a donor can only break a row that its own
                                                       end had already rejected
  S3 bracket     min(donor, own) < t_side < max(...) -- S2 with the row's own SIDE in the threshold

S3 exists because the max(|lo|,|hi|) form is only the flip multiplier when the row sits outside on
the wider side of its band.  A row below a band whose lower end is the narrow one crosses at
|b|/|lo|, which is LARGER than |b|/max(|lo|,|hi|); the published form understates how close such a
row is to its band.  Whether any published row is of that shape is measured here, not assumed.
"""
from __future__ import print_function

import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e262_p95_transfer_across_windows as e262   # noqa: E402  (row/arm resolution, judge)

ROOT = e262.ROOT
OUTDIR = os.path.join(ROOT, "results", "state_tilt")

STUDY = "E266_wide_end_screen_holdout"
TITLE = "does the wide-end threshold screen hold on rows it was not fitted on?"
CUTOFF = "2026-10-29"
SRC = "BANDTRANSFER-%s.json" % CUTOFF
FACE = "BANDSCREEN-%s.json" % CUTOFF
LATEST = "bandscreen_latest.json"

TOL = 1e-12

NO_BILL = ("measurement only: E262's published pairs are re-read; no shuffle stream is drawn, no "
           "band is rebuilt, and no row verdict outside this face is touched")

VERDICT_VOCAB = (
    "screen_exact_with_both_ends_and_the_side",   # S3 reproduces every published move and no other
    "donor_above_the_row_is_not_a_screen",        # S1 flags rows its own end never rejected
    "screen_misses_moves",                        # S3/S2 loses a move the data does contain
    "screen_needs_the_side",                      # S2 is short where the row sits on the narrow end
    "screen_untested_no_moves",                   # no pair in the face moved anything
    "no_published_pair_carries_a_row",            # nothing to compare
)


def _p(name):
    return os.path.join(ROOT, "results", "state_tilt", name)


def load(name):
    with io.open(_p(name), encoding="utf-8") as fh:
        return json.load(fh)


# ------------------------------------------------------------------ thresholds
def t_max_end(b, lo, hi):
    """E264/E265: the flip multiplier read off the wider end of the band."""
    if b is None or lo is None or hi is None:
        return None
    span = max(abs(float(lo)), abs(float(hi)))
    if span <= 0:
        return None
    return abs(float(b)) / span


def row_side(b, lo, hi):
    """Which end of the band the row has to cross as the band shrinks."""
    if b is None or lo is None or hi is None:
        return None
    b = float(b)
    if b < 0 and float(lo) < 0:
        return "lo"
    if b > 0 and float(hi) > 0:
        return "hi"
    return None


def t_side(b, lo, hi):
    """The flip multiplier on the row's own side: |b| / |the end it sits beyond|.

    A row inside the band has no side, so the nearer end is used -- that is the crossing that a
    shrinking band reaches first, and t < 1 for such a row (it flips on the way down).
    """
    if b is None or lo is None or hi is None:
        return None
    b, lo, hi = float(b), float(lo), float(hi)
    if b < 0 and lo < 0:
        end = abs(lo)
    elif b > 0 and hi > 0:
        end = abs(hi)
    elif b < 0 and hi > 0:
        end = abs(hi)          # positive band with a negative coefficient: crosses hi-side scale
    elif b > 0 and lo < 0:
        end = abs(lo)
    else:
        end = max(abs(lo), abs(hi))
    if end <= 0:
        return None
    return abs(b) / end


# ------------------------------------------------------------------ the three screens
def s1_single(donor_p95, own_p95, t):
    if donor_p95 is None or t is None:
        return None
    return bool(donor_p95 > t)


def s2_guarded(donor_p95, own_p95, t):
    if donor_p95 is None or own_p95 is None or t is None:
        return None
    return bool(donor_p95 > t and own_p95 < t)


def s3_bracket(donor_p95, own_p95, t):
    if donor_p95 is None or own_p95 is None or t is None:
        return None
    lo_end, hi_end = min(donor_p95, own_p95), max(donor_p95, own_p95)
    return bool(lo_end < t < hi_end)


def direction_of(own_p95, donor_p95, t):
    """What a flip would mean: the row was rejected by its own end and is not by the donor, or v.v."""
    if own_p95 is None or donor_p95 is None or t is None:
        return None
    before = own_p95 < t      # outside at its own end
    after = donor_p95 < t
    if before == after:
        return None
    return "rejections_lost" if before else "rejections_invented"


# ------------------------------------------------------------------ reading the published face
def base_of(row):
    """The published draw count, whichever key the face carries (e262 rows have 'base', the
    E259-style source rows only carry 'band_draws')."""
    for key in ("base", "band_draws"):
        try:
            return int(float(row.get(key)))
        except (TypeError, ValueError):
            continue
    return None


def indexed_rows(face):
    out = []
    for i, r in enumerate((face or {}).get("rows") or []):
        rec = dict(r)
        rec["index"] = i
        out.append(rec)
    return out


def comparisons(face):
    """One record per (published pair, recipient row) -- the whole comparison set."""
    rows = indexed_rows(face)
    out, groups = [], []
    for arm in sorted((face or {}).get("transfer") or {}):
        blk = face["transfer"][arm] or {}
        leg, base = blk.get("leg"), blk.get("base")
        g = {"arm": arm, "leg": leg, "base": base, "pairs": 0, "pairs_with_rows": 0,
             "comparisons": 0, "moved": 0, "rows_moved": []}
        for pair in blk.get("pairs") or []:
            g["pairs"] += 1
            moved = [m for m in (pair.get("moved") or [])]
            moved_idx = {m.get("index") for m in moved}
            recips = [r for r in rows
                      if r.get("status") == "measured"
                      and r.get("cell") == pair.get("recipient")
                      and r.get("leg") == leg and base_of(r) == base]
            if recips:
                g["pairs_with_rows"] += 1
            g["moved"] += len(moved_idx)
            for m in moved:
                g["rows_moved"].append({"index": m.get("index"), "row": m.get("row"),
                                        "direction": m.get("direction")})
            for r in recips:
                b, lo, hi = r.get("b"), r.get("band_lo"), r.get("band_hi")
                tm, ts = t_max_end(b, lo, hi), t_side(b, lo, hi)
                own, donor = r.get("own_p95"), pair.get("donor_p95")
                out.append({
                    "arm": arm, "leg": leg, "base": base,
                    "donor": pair.get("donor"), "recipient": pair.get("recipient"),
                    "index": r.get("index"), "cell": r.get("cell"), "row": r.get("row"),
                    "b": b, "band_lo": lo, "band_hi": hi,
                    "side": row_side(b, lo, hi),
                    "t_max_end": tm, "t_side": ts, "thresholds_differ": (
                        None if (tm is None or ts is None) else bool(abs(tm - ts) > TOL)),
                    "own_p95": own, "donor_p95": donor,
                    "own_verdict": None if (own is None or ts is None) else
                    ("outside" if own < ts else "inside"),
                    "donor_verdict": None if (donor is None or ts is None) else
                    ("outside" if donor < ts else "inside"),
                    "predicted_single": s1_single(donor, own, tm),
                    "predicted_guarded": s2_guarded(donor, own, tm),
                    "predicted_bracket": s3_bracket(donor, own, ts),
                    "predicted_direction": direction_of(own, donor, ts),
                    "actual_moved": bool(r.get("index") in moved_idx),
                    "actual_direction": next((m.get("direction") for m in moved
                                              if m.get("index") == r.get("index")), None),
                })
                g["comparisons"] += 1
        groups.append(g)
    return out, groups


def confusion(records, key):
    c = {"predicted": 0, "actual": 0, "tp": 0, "fp": 0, "fn": 0, "tn": 0, "undefined": 0}
    for r in records:
        pred, act = r.get(key), r.get("actual_moved")
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
    c["exact"] = bool(c["fp"] == 0 and c["fn"] == 0 and c["undefined"] == 0)
    return c


def counterexamples(records):
    """The rows the written screen flags but the data does not move (and any it misses)."""
    fp, fn = [], []
    for r in records:
        if r.get("predicted_single") and not r.get("actual_moved"):
            # two distinct reasons, and they are not interchangeable: a row already inside at its
            # own end cannot lose a rejection, while a row its own end rejects is only left alone
            # because the donor is not wide enough on the side the row actually sits.
            own = r.get("own_verdict")
            why = ("its own end had already rejected nothing (the row was inside)"
                   if own == "inside" else
                   "the donor is not wide enough on the row's own side (the max-end threshold "
                   "understates how close the row sits)")
            fp.append({"arm": r.get("arm"), "recipient": r.get("recipient"),
                       "donor": r.get("donor"), "index": r.get("index"), "row": r.get("row"),
                       "cell": r.get("cell"), "t_max_end": r.get("t_max_end"),
                       "t_side": r.get("t_side"),
                       "donor_p95": r.get("donor_p95"), "own_p95": r.get("own_p95"),
                       "own_verdict": own, "why": why})
        if r.get("actual_moved") and not r.get("predicted_bracket"):
            fn.append({"arm": r.get("arm"), "recipient": r.get("recipient"),
                       "donor": r.get("donor"), "index": r.get("index"), "row": r.get("row"),
                       "t_side": r.get("t_side"), "t_max_end": r.get("t_max_end"),
                       "donor_p95": r.get("donor_p95"), "own_p95": r.get("own_p95")})
    return fp, fn


def verdict_of(records, c_s1, c_s2, c_s3):
    if not records:
        return ("no_published_pair_carries_a_row",
                "none of the published ordered pairs carries a measured recipient row")
    if c_s3["actual"] == 0:
        return ("screen_untested_no_moves",
                "%d comparison(s) but not one published pair moves a verdict" % len(records))
    if c_s3["fn"]:
        return ("screen_misses_moves",
                "the bracket screen misses %d of the %d published move(s)"
                % (c_s3["fn"], c_s3["actual"]))
    if c_s2["fp"] and not c_s2["fn"]:
        return ("screen_needs_the_side",
                "the max-end threshold flags %d row(s) its own side does not reach" % c_s2["fp"])
    if c_s3["exact"] and not c_s1["exact"]:
        return ("donor_above_the_row_is_not_a_screen",
                "donor p95 above the threshold flags %d of %d comparisons while only %d move "
                "(precision %.3f); guarding on the row's own end removes every false positive but "
                "loses %d move because the max-end threshold understates a narrow-side row; the "
                "bracket on the row's own side reproduces the moved set exactly"
                % (c_s1["predicted"], len(records), c_s3["actual"],
                   (float(c_s1["tp"]) / c_s1["predicted"]) if c_s1["predicted"] else 0.0,
                   c_s2["fn"]))
    if c_s3["exact"]:
        return ("screen_exact_with_both_ends_and_the_side",
                "all %d published move(s) reproduced with %d false positive(s) on %d comparison(s)"
                % (c_s3["actual"], c_s3["fp"], len(records)))
    return ("screen_needs_the_side",
            "the max-end bracket disagrees with the published moves")


# ------------------------------------------------------------------ run
def run(save=True, outdir=None):
    outdir = outdir or OUTDIR
    face_src = load(SRC)
    recs, groups = comparisons(face_src)
    c_s1 = confusion(recs, "predicted_single")
    c_s2 = confusion(recs, "predicted_guarded")
    c_s3 = confusion(recs, "predicted_bracket")
    fp, fn = counterexamples(recs)
    verdict, reason = verdict_of(recs, c_s1, c_s2, c_s3)
    differing = [r for r in recs if r.get("thresholds_differ")]
    moved = [r for r in recs if r.get("actual_moved")]

    out = {
        "study": STUDY,
        "title": TITLE,
        "evidence_cutoff": CUTOFF,
        "generated": None,
        "source_face": SRC,
        "no_bill": NO_BILL,
        "verdict": verdict,
        "verdict_reason": reason,
        "frozen_spec": {
            "population": "E262's 48 ordered (donor, recipient) pairs, re-read -- no new draws",
            "unit": "one comparison = one published pair x one measured recipient row",
            "t_max_end": "|b| / max(|lo|,|hi|)  (E264/E265 form)",
            "t_side": "|b| / |the band end on the row's own side| (inside rows: the nearer end)",
            "S1_single": "donor_p95 > t_max_end",
            "S2_guarded": "donor_p95 > t_max_end and own_p95 < t_max_end",
            "S3_bracket": "min(donor_p95, own_p95) < t_side < max(donor_p95, own_p95)",
            "actual": "E262's published moved list, matched by row index",
            "flip_rule": "outside at m <=> |b| > max(|lo|*m, |hi|*m) on the row's own side "
                         "(e262.judge: literal band test, sign aware)",
            "no_bill": NO_BILL,
        },
        "summary": {
            "pairs": sum(g["pairs"] for g in groups),
            "pairs_with_rows": sum(g["pairs_with_rows"] for g in groups),
            "comparisons": len(recs),
            "comparisons_undefined": c_s3["undefined"],
            "moves_published": c_s3["actual"],
            "rows_moved": [{"index": r.get("index"), "cell": r.get("cell"), "row": r.get("row"),
                            "arm": r.get("arm"), "donor": r.get("donor"),
                            "recipient": r.get("recipient"),
                            "direction": r.get("actual_direction"),
                            "t_side": r.get("t_side"), "t_max_end": r.get("t_max_end"),
                            "donor_p95": r.get("donor_p95"), "own_p95": r.get("own_p95")}
                           for r in moved],
            "rows_where_the_two_thresholds_differ": len(differing),
            "S1_single": c_s1,
            "S2_guarded": c_s2,
            "S3_bracket": c_s3,
            "S1_precision": (None if not c_s1["predicted"]
                             else float(c_s1["tp"]) / c_s1["predicted"]),
            "S3_exact": c_s3["exact"],
            "resolution_note": ("%d comparison(s) with %d positive(s): exactness here is a "
                                "consistency check on the published pairs, not a validated screen"
                                % (len(recs), c_s3["actual"])),
        },
        "thresholds_that_differ": [
            {"index": r.get("index"), "cell": r.get("cell"), "row": r.get("row"),
             "arm": r.get("arm"), "side": r.get("side"),
             "t_max_end": r.get("t_max_end"), "t_side": r.get("t_side"),
             "donor_p95": r.get("donor_p95"), "own_p95": r.get("own_p95"),
             "actual_moved": r.get("actual_moved"),
             "bracket_under_t_max_end": s3_bracket(r.get("donor_p95"), r.get("own_p95"),
                                                   r.get("t_max_end"))}
            for r in differing],
        "counterexamples_of_the_written_screen": fp,
        "moves_the_bracket_screen_misses": fn,
        "groups": groups,
        "comparison_rows": recs,
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
    path = os.path.join(outdir, "BANDSCREEN-%s%s.json" % (face.get("evidence_cutoff"), tag))
    text = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text + "\n")
    with io.open(os.path.join(outdir, LATEST), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text + "\n")
    return path


def verify(outdir=None, tag=""):
    """Re-derive and report every field that does not come back (generated stamp excepted)."""
    outdir = outdir or OUTDIR
    path = os.path.join(outdir, "BANDSCREEN-%s%s.json" % (CUTOFF, tag))
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


def _pair(donor, recipient, donor_p95, rows):
    return {"donor": donor, "recipient": recipient, "donor_p95": donor_p95,
            "recipient_p95": None, "moved": rows}


def _row(cell, row, b, lo, hi, base=60, leg="self", own_p95=2.0, published="inside"):
    return {"cell": cell, "row": row, "b": b, "band_lo": lo, "band_hi": hi, "band_draws": base,
            "leg": leg, "own_p95": own_p95, "verdict_wide": published, "status": "measured"}


def _face(rows, transfer):
    return {"rows": rows, "transfer": transfer}


def selftest():
    legs = []

    # --- the two thresholds, and where they disagree
    legs.append(_leg(abs(t_max_end(-0.7, -0.3, 0.2) - 0.7 / 0.3) <= TOL,
                     "t_max_end = |b| / max(|lo|,|hi|)", t_max_end(-0.7, -0.3, 0.2)))
    legs.append(_leg(abs(t_side(-0.7, -0.3, 0.2) - 0.7 / 0.3) <= TOL,
                     "on the wider side the two thresholds agree", t_side(-0.7, -0.3, 0.2)))
    ts, tm = t_side(-0.8, -0.30, 0.38), t_max_end(-0.8, -0.30, 0.38)
    legs.append(_leg(ts > tm + 0.1,
                     "a row outside on the NARROW side crosses later than the max-end form says",
                     [ts, tm]))
    legs.append(_leg(abs(t_side(0.8, -0.38, 0.30) - 0.8 / 0.30) <= TOL,
                     "the mirror row (positive, narrow hi) reads its own end"))
    legs.append(_leg(abs(t_side(-0.1, -0.30, 0.38) - 0.1 / 0.30) <= TOL,
                     "an inside row reads the nearer end (t < 1, it flips on the way down)",
                     t_side(-0.1, -0.30, 0.38)))
    legs.append(_leg(t_side(None, 1, 1) is None and t_max_end(-1, 0, 0) is None,
                     "no coefficient or a zero-width band has no threshold"))
    legs.append(_leg(row_side(-0.8, -0.3, 0.2) == "lo" and row_side(0.8, -0.3, 0.2) == "hi",
                     "the side is the end the row sits beyond"))
    legs.append(_leg(row_side(-0.8, 0.1, 0.2) is None,
                     "a row below a positive-only band has no side of its own (disclosed)"))

    # --- S1 is what the card wrote, and it flags a row whose own end never rejected it
    t = t_max_end(-0.8, -0.30, 0.38)                 # 2.099
    legs.append(_leg(s1_single(2.18, 2.17, 2.099) is True,
                     "S1 flags the row on a donor barely wider than its own end"))
    legs.append(_leg(s2_guarded(2.18, 2.17, 2.099) is False,
                     "S2 does not: its own end had already rejected it (own_p95 > t)"))
    legs.append(_leg(s3_bracket(2.18, 2.17, 2.099) is False,
                     "S3 agrees with S2 on the max-end threshold"))

    # --- the max-end bracket is the one that gets a narrow-side row wrong
    ts = t_side(-0.8, -0.30, 0.38)                   # 2.667
    tm = t_max_end(-0.8, -0.30, 0.38)                # 2.105
    legs.append(_leg(s3_bracket(1.99, 2.17, ts) is False,
                     "S3 on the row's own side says no flip: its own end still rejects the row",
                     ts))
    legs.append(_leg(s3_bracket(1.99, 2.17, tm) is True,
                     "the same comparison under t_max_end is a false positive (the narrow-side row)",
                     tm))
    legs.append(_leg(s3_bracket(2.0, 2.0, 2.0) is False,
                     "a donor equal to the row's own end moves nothing"))
    legs.append(_leg(direction_of(1.99, 2.17, 2.10) == "rejections_lost",
                     "a wider donor takes the rejection away"))
    legs.append(_leg(direction_of(2.17, 1.99, 2.10) == "rejections_invented",
                     "a narrower donor invents one"))

    # --- confusion counting is a 2x2, and undefined predictions are counted not absorbed
    recs = [{"predicted_bracket": True, "actual_moved": True},
            {"predicted_bracket": True, "actual_moved": False},
            {"predicted_bracket": False, "actual_moved": True},
            {"predicted_bracket": False, "actual_moved": False},
            {"predicted_bracket": None, "actual_moved": False}]
    c = confusion(recs, "predicted_bracket")
    legs.append(_leg((c["tp"], c["fp"], c["fn"], c["tn"], c["undefined"]) == (1, 1, 1, 1, 1),
                     "the confusion counts all five classes", [c["tp"], c["fp"], c["fn"],
                                                               c["tn"], c["undefined"]]))
    legs.append(_leg(c["exact"] is False, "an undefined prediction means not exact"))

    # --- the pipeline on a two-pair fake face: one honest move, one S1 false positive
    fake = _face(
        rows=[_row("A", "self", -0.8, -0.30, 0.38, own_p95=1.50, published="outside"),
              _row("B", "self", -0.8, -0.30, 0.38, own_p95=2.30, published="outside")],
        transfer={"self:60": {"leg": "self", "base": 60, "cells": ["A", "B"], "reason": None,
                              "pairs": [_pair("B", "A", 2.80, [{"index": 0, "row": "self",
                                                                "direction": "rejections_lost"}]),
                                        _pair("A", "B", 2.20, [])]}})
    recs, groups = comparisons(fake)
    legs.append(_leg(len(recs) == 2 and groups[0]["pairs"] == 2,
                     "one comparison per (pair, recipient row), pairs counted separately",
                     [len(recs), groups[0]["pairs"]]))
    legs.append(_leg(recs[0]["actual_moved"] is True and recs[0]["predicted_bracket"] is True,
                     "the honest move is predicted by the bracket screen",
                     [recs[0]["actual_moved"], recs[0]["predicted_bracket"]]))
    legs.append(_leg(recs[1]["predicted_single"] is True and recs[1]["actual_moved"] is False,
                     "S1 flags a row that does not move (the false-positive class)",
                     [recs[1]["predicted_single"], recs[1]["actual_moved"]]))
    fp_rows, fn_rows = counterexamples(recs)
    legs.append(_leg(len(fp_rows) >= 1 and len(fn_rows) == 0,
                     "counterexamples are listed, not summed away", [len(fp_rows), len(fn_rows)]))
    v, _ = verdict_of(recs, confusion(recs, "predicted_single"), confusion(recs, "predicted_guarded"),
                      confusion(recs, "predicted_bracket"))
    legs.append(_leg(v == "donor_above_the_row_is_not_a_screen",
                     "the fake face reaches the S1-is-not-a-screen verdict", v))

    # --- verdict totality: no rows, no moves, and a miss each have their own answer
    v, _ = verdict_of([], confusion([], "predicted_bracket"), None, None)
    legs.append(_leg(v == "no_published_pair_carries_a_row", "an empty set is its own verdict", v))
    nomove = [{"predicted_bracket": False, "actual_moved": False}]
    v, _ = verdict_of(nomove, confusion(nomove, "predicted_single"),
                      confusion(nomove, "predicted_guarded"),
                      confusion(nomove, "predicted_bracket"))
    legs.append(_leg(v == "screen_untested_no_moves", "zero positives is not exactness", v))
    miss = [{"predicted_bracket": False, "actual_moved": True}]
    v, _ = verdict_of(miss, confusion(miss, "predicted_single"), confusion(miss, "predicted_guarded"),
                      confusion(miss, "predicted_bracket"))
    legs.append(_leg(v == "screen_misses_moves", "a missed move outranks every other reading", v))

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
        print("%s: %s" % (face["verdict"], face["verdict_reason"]))
        m = face["summary"]
        print("pairs %d (%d carry rows) | comparisons %d | moves %d | S1 tp/fp/fn %d/%d/%d | "
              "S3 tp/fp/fn %d/%d/%d | thresholds differ on %d row(s)" % (
                  m["pairs"], m["pairs_with_rows"], m["comparisons"], m["moves_published"],
                  m["S1_single"]["tp"], m["S1_single"]["fp"], m["S1_single"]["fn"],
                  m["S3_bracket"]["tp"], m["S3_bracket"]["fp"], m["S3_bracket"]["fn"],
                  m["rows_where_the_two_thresholds_differ"]))
        return 0
    print("usage: e266_wide_end_screen_holdout.py [run|verify|selftest]")
    return 2


if __name__ == "__main__":
    sys.exit(main())