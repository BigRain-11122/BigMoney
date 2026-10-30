#!/usr/bin/env python
"""E262 -- is the wide end of one window an upper bound for another?

E258 showed the draw multiplier's MEDIAN is not one object across windows; E259 measured the tails
and published a p05..p95 interval per (window, leg, base count). What a reader actually does with
those numbers is borrow one: judge a row with another window's wide end instead of its own. This
face measures that act directly, on E259's published intervals only -- no new draws.

Three questions, in order:
  1. does any window's p95 dominate every other window's p95 at the same (leg, base count)? A
     dominating arm is the only thing that makes "use the widest" a safe single number.
  2. if a row is judged with a donor's p95, does its verdict move? Moves are published with a
     direction: outside->inside loses a rejection, inside->outside invents one.
  3. what does one flat p95 per (leg, base) do -- the pooled maximum, i.e. the most permissive
     single number anyone would actually adopt?

The multiplier's denominator IS the base count (edge at top draws / edge at base draws), so a
transfer across base counts is a different quantity, not a different estimate of the same one. The
matrix is therefore published only within a (leg, base count); cross-base moves are disclosed as
the systematic offset they are and are never mixed into the matrix.

Reads: results/state_tilt/BANDWINDIST-2026-10-29.json (E259). Writes: BANDTRANSFER-2026-10-29.json.
No new shuffles, no engine, no admission: measurement only.
"""
from __future__ import annotations

import argparse
import io
import json
import os
import statistics
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e257_band_at_top_flips as e257  # noqa: E402
import e259_band_multiplier_distribution as e259  # noqa: E402

ROOT = e259.ROOT
OUTDIR = os.path.join(ROOT, "results", "state_tilt")

STUDY = "E262_p95_transfer_across_windows"
TITLE = "is the wide end of one window an upper bound for another?"
CUTOFF = "2026-10-29"
SRC_WIDTH = "BANDWINDIST-%s.json" % CUTOFF
FACE = "BANDTRANSFER-%s.json" % CUTOFF
LATEST = "bandtransfer_latest.json"

LEGS = ("self", "cross")
BASE_COUNTS = (60, 200)
TOL = 1e-12

# b_source is a name, and a name is not the leg it reads (E207/E208 family). These two sources name
# their leg explicitly; a residual carries no leg at all and is resolved by coefficient identity.
LEG_FROM_SOURCE = {"self_row.b_self": "self", "cross_row.b_cross": "cross"}

NO_BILL = ("measurement only: E259's published intervals are re-read; no shuffle stream is drawn, "
           "no engine runs, no admission or allocation decision is touched. A verdict that moves "
           "here is a statement about the published numbers, not about the market.")

VERDICT_VOCAB = (
    "a_foreign_wide_end_is_not_a_bound",
    "the_wide_end_transfers_without_moving_a_verdict",
    "no_transfer_possible",
    "no_windows_measured",
)


# ------------------------------------------------------------------ io
def _p(name):
    return os.path.join(OUTDIR, name)


def load(name):
    with io.open(_p(name), encoding="utf-8") as fh:
        return json.load(fh)


def _try_load(name):
    try:
        return load(name)
    except (FileNotFoundError, ValueError):
        return None


# ------------------------------------------------------------------ arms
def arms_from(face):
    """{(cell, leg, base): record} read off E259's interval table.

    The key carries the leg AND the base count. E258 stored its arms keyed by base count alone and
    a lookup by that coarse key silently returned the default (self) arm -- the pit r1286 recorded.
    """
    out = {}
    for r in ((face or {}).get("interval_spread") or {}).get("rows") or []:
        arm = str(r.get("arm") or "")
        if ":" not in arm:
            continue
        leg, base = arm.split(":", 1)
        try:
            base = int(base)
        except ValueError:
            continue
        iv = r.get("interval") or [None, None]
        out[(r.get("cell"), leg, base)] = {
            "cell": r.get("cell"), "leg": leg, "base": base,
            "p05": iv[0] if len(iv) > 0 else None,
            "p95": iv[1] if len(iv) > 1 else None,
            "median": r.get("median"),
            "width": r.get("width"),
            "e258_width": r.get("e258_width"),
            "ratio_vs_e258": r.get("ratio"),
        }
    return out


def p95_of(arms, cell, leg, base):
    rec = (arms or {}).get((cell, leg, base))
    return None if not rec else rec.get("p95")


# ------------------------------------------------------------------ which leg does a row read
def resolve_leg(row, cell_rows):
    """Which published arm is this row judged on? Never guess -- unresolvable says so."""
    src = row.get("b_source")
    if src in LEG_FROM_SOURCE:
        return LEG_FROM_SOURCE[src], "b_source names the leg"
    b = row.get("b")
    if b is None:
        return None, "row carries no coefficient"
    hits = [r.get("row") for r in (cell_rows or [])
            if r.get("row") in ("self", "cross")
            and r.get("b") is not None and abs(float(r["b"]) - float(b)) <= TOL]
    if len(hits) == 1:
        return hits[0], "coefficient identity"
    if len(hits) > 1:
        return None, "coefficient matches %d rows (%s): ambiguous" % (len(hits), ",".join(hits))
    return None, "coefficient matches no published row of this cell"


def judge(b, lo, hi, m):
    if b is None or lo is None or hi is None or m is None:
        return None
    return e257.outside(b, *e257.scale_band(lo, hi, m))


def _dir(before, after):
    if before is None or after is None or before == after:
        return None
    if before and not after:
        return "rejections_lost"
    return "rejections_invented"


# ------------------------------------------------------------------ rows
def row_records(face, arms):
    rows = (face or {}).get("rows") or []
    by_cell = {}
    for r in rows:
        by_cell.setdefault(r.get("cell"), []).append(r)
    out = []
    for i, r in enumerate(rows):
        rec = {"index": i, "cell": r.get("cell"), "row": r.get("row"), "b": r.get("b"),
               "band_lo": r.get("band_lo"), "band_hi": r.get("band_hi"),
               "published_outside": r.get("published_outside"),
               "published_verdict_wide": r.get("verdict_wide")}
        if r.get("b") is None or r.get("band_lo") is None or r.get("band_hi") is None:
            rec.update({"status": "unjudgeable", "reason": "row carries no coefficient or no band"})
            out.append(rec)
            continue
        try:
            base = int(float(r.get("band_draws")))
        except (TypeError, ValueError):
            rec.update({"status": "unjudgeable", "reason": "row carries no published draw count"})
            out.append(rec)
            continue
        rec["base"] = base
        leg, why = resolve_leg(r, by_cell.get(r.get("cell")))
        rec["leg_basis"] = why
        if leg is None:
            rec.update({"status": "leg_unresolved", "reason": why})
            out.append(rec)
            continue
        rec["leg"] = leg
        own = (arms or {}).get((rec["cell"], leg, base))
        if not own:
            rec.update({"status": "no_arm",
                        "reason": "no published %s:%d arm for this cell" % (leg, base)})
            out.append(rec)
            continue
        rec.update({
            "status": "measured",
            "own_p95": own.get("p95"),
            "own_p05": own.get("p05"),
            "verdict_wide": judge(rec["b"], rec["band_lo"], rec["band_hi"], own.get("p95")),
            "verdict_tight": judge(rec["b"], rec["band_lo"], rec["band_hi"], own.get("p05")),
            "margin_wide": (abs(rec["b"]) / max(abs(rec["band_lo"] * own["p95"]),
                                                abs(rec["band_hi"] * own["p95"]))
                            if own.get("p95") else None),
        })
        # the E259 face published its wide verdict on the self arm for every row; a row whose leg is
        # cross reads a different interval. Disclose the rows where the two readings differ instead
        # of silently overwriting one with the other.
        rec["e259_wide_verdict_reproduced"] = (
            None if r.get("verdict_wide") is None else
            (r.get("verdict_wide") == ("outside" if rec["verdict_wide"] else "inside")))
        out.append(rec)
    return out


# ------------------------------------------------------------------ transfer matrix
def transfer(records, arms, legs=LEGS, base_counts=BASE_COUNTS):
    """For every (leg, base) and every ordered (donor, recipient) pair, what moves."""
    out = {}
    for leg in legs:
        for base in base_counts:
            cells = sorted({c for (c, l, b) in (arms or {}) if l == leg and b == base})
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
                    d_p95 = p95_of(arms, donor, leg, base)
                    r_p95 = p95_of(arms, recip, leg, base)
                    rrows = [x for x in records
                             if x.get("status") == "measured" and x.get("cell") == recip
                             and x.get("leg") == leg and x.get("base") == base]
                    moved = []
                    for x in rrows:
                        after = judge(x["b"], x["band_lo"], x["band_hi"], d_p95)
                        before = x["verdict_wide"]
                        if after is None or before is None:
                            continue
                        if after != before:
                            moved.append({"index": x["index"], "row": x.get("row"),
                                          "b": x["b"], "before": "outside" if before else "inside",
                                          "after": "outside" if after else "inside",
                                          "direction": _dir(before, after)})
                    delta = (None if (d_p95 is None or not r_p95)
                             else (d_p95 / r_p95 - 1.0))
                    pairs.append({
                        "donor": donor, "recipient": recip,
                        "donor_p95": d_p95, "recipient_p95": r_p95,
                        "delta_pct": (None if delta is None else delta * 100.0),
                        "donor_wider": None if delta is None else bool(delta > 0),
                        "n_rows": len(rrows), "n_moved": len(moved),
                        "moved": moved,
                    })
            out["%s:%d" % (leg, base)] = {"leg": leg, "base": base, "cells": cells,
                                          "pairs": pairs, "reason": None}
    return out


def dominator(arms, leg, base):
    """The only arm that makes 'use the widest' a safe number: one whose p95 >= every other."""
    cells = sorted({c for (c, l, b) in (arms or {}) if l == leg and b == base})
    vals = {c: p95_of(arms, c, leg, base) for c in cells}
    if len(vals) < 2 or any(v is None for v in vals.values()):
        return {"cells": cells, "dominator": None, "max": None, "min": None,
                "spread_pct": None, "reason": "not enough measured arms to rank"}
    hi = max(vals.values())
    lo = min(vals.values())
    tops = [c for c, v in vals.items() if abs(v - hi) <= TOL]
    return {"cells": cells, "p95": vals,
            "dominator": tops[0] if len(tops) == 1 else None,
            "tied_at_max": tops if len(tops) > 1 else [],
            "max": hi, "min": lo,
            "spread_pct": (hi / lo - 1.0) * 100.0 if lo else None}


def flat_read(records, arms, legs=LEGS, base_counts=BASE_COUNTS):
    """One number per (leg, base): the pooled maximum, which is what 'use the widest' adopts."""
    out = {}
    for leg in legs:
        for base in base_counts:
            vals = {c: p95_of(arms, c, leg, base) for (c, l, b) in (arms or {})
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
            moved_hi, moved_lo = [], []
            for x in rows:
                for name, m, bucket in (("wide", hi, moved_hi), ("tight", lo, moved_lo)):
                    after = judge(x["b"], x["band_lo"], x["band_hi"], m)
                    if after is None or x["verdict_wide"] is None:
                        continue
                    if after != x["verdict_wide"]:
                        bucket.append({"index": x["index"], "cell": x["cell"], "row": x.get("row"),
                                       "before": "outside" if x["verdict_wide"] else "inside",
                                       "after": "outside" if after else "inside",
                                       "direction": _dir(x["verdict_wide"], after)})
            out["%s:%d" % (leg, base)] = {
                "leg": leg, "base": base,
                "flat_p95": hi, "flat_p95_from": hi_from,
                "flat_tight_p95": lo, "flat_tight_from": lo_from,
                "n_rows": len(rows),
                "n_moved_at_flat": len(moved_hi), "moved_at_flat": moved_hi,
                "n_moved_at_flat_tight": len(moved_lo), "moved_at_flat_tight": moved_lo,
            }
    return out


def cross_base_offset(arms, legs=LEGS, base_counts=BASE_COUNTS):
    """Disclosure only: a multiplier at base 60 is not an estimate of one at base 200."""
    out = {}
    for leg in legs:
        if len(base_counts) < 2:
            continue
        lo_b, hi_b = min(base_counts), max(base_counts)
        a = [p95_of(arms, c, leg, lo_b) for (c, l, b) in (arms or {}) if l == leg and b == lo_b]
        z = [p95_of(arms, c, leg, hi_b) for (c, l, b) in (arms or {}) if l == leg and b == hi_b]
        a = [v for v in a if v is not None]
        z = [v for v in z if v is not None]
        if not a or not z:
            continue
        out[leg] = {"base_small": lo_b, "base_large": hi_b,
                    "p95_median_small": statistics.median(a),
                    "p95_median_large": statistics.median(z),
                    "ratio_median": (statistics.median(a) / statistics.median(z)),
                    "note": ("the same leg's wide end is systematically larger at the smaller base "
                             "count, because the base edge it divides by is taken lower on the "
                             "curve; these two are not estimates of one quantity")}
    return out


# ------------------------------------------------------------------ verdict
def verdict_of(records, trans, flat, dom):
    measured = [x for x in records if x.get("status") == "measured"]
    if not (trans or any((v or {}).get("pairs") for v in (trans or {}).values())):
        return "no_windows_measured", "E259's %s is absent; no arm can be transferred" % SRC_WIDTH
    pairs = [p for v in trans.values() for p in (v.get("pairs") or [])]
    if not pairs:
        return ("no_transfer_possible",
                "no two windows share a (leg, base count) pair with a published interval")
    moved = [p for p in pairs if p["n_moved"]]
    lost = sum(len([m for m in p["moved"] if m["direction"] == "rejections_lost"])
               for p in moved)
    invented = sum(len([m for m in p["moved"] if m["direction"] == "rejections_invented"])
                   for p in moved)
    doms = {k: v.get("dominator") for k, v in (dom or {}).items() if v.get("cells")}
    if moved:
        why = ("%d of %d ordered (donor, recipient) pairs move at least one row's wide-end verdict "
               "(%d rejection(s) lost, %d invented); no single window dominates at every (leg, base "
               "count) (%s). Borrowing another window's wide end is therefore a different claim, "
               "not a conservative one"
               % (len(moved), len(pairs), lost, invented,
                  ", ".join("%s=%s" % (k, v or "-") for k, v in sorted(doms.items()))))
        return "a_foreign_wide_end_is_not_a_bound", why
    why = ("none of the %d ordered pairs moves a row's verdict (%d row(s) judged across %d arms)"
           % (len(pairs), len(measured), len({(x["cell"], x["leg"], x["base"])
                                              for x in measured})))
    spread = [v.get("spread_pct") for v in (dom or {}).values() if v.get("spread_pct") is not None]
    if spread:
        why += ("; the arms' wide ends still differ by up to %.1f%%, so the intervals are not one "
                "object even though these rows cannot tell them apart" % max(spread))
    return "the_wide_end_transfers_without_moving_a_verdict", why


# ------------------------------------------------------------------ run
def run(save=True, outdir=None):
    outdir = outdir or OUTDIR
    face = _try_load(SRC_WIDTH)
    if face is None:
        out = {"study": STUDY, "title": TITLE, "evidence_cutoff": CUTOFF,
               "generated": datetime.now().isoformat(timespec="seconds"),
               "verdict": "no_windows_measured",
               "verdict_reason": "E259's %s is absent" % SRC_WIDTH,
               "arms": [], "rows": [], "transfer": {}, "flat": {}, "dominator": {},
               "source_faces": ["results/state_tilt/%s" % SRC_WIDTH], "no_bill": NO_BILL}
        out["summary"] = _summary(out)
        if save:
            _write(out, outdir)
        return out

    arms = arms_from(face)
    records = row_records(face, arms)
    trans = transfer(records, arms)
    flat = flat_read(records, arms)
    dom = {"%s:%d" % (leg, base): dominator(arms, leg, base)
           for leg in LEGS for base in BASE_COUNTS}
    offset = cross_base_offset(arms)
    v, why = verdict_of(records, trans, flat, dom)

    out = {
        "study": STUDY,
        "title": TITLE,
        "evidence_cutoff": face.get("evidence_cutoff") or CUTOFF,
        "generated": datetime.now().isoformat(timespec="seconds"),
        "frozen_spec": {
            "design": ("read E259's published p05..p95 interval per (window, leg, base count) and "
                       "judge each published row with a donor window's wide end instead of its own"),
            "no_new_draws": ("no shuffle stream is drawn; every number here is a function of "
                             "results/state_tilt/%s" % SRC_WIDTH),
            "leg_rule": ("a row is judged on the leg its own coefficient identifies: b_source names "
                         "it where it says self_row.b_self / cross_row.b_cross; a residual carries "
                         "no leg and is resolved by coefficient identity against that cell's "
                         "published rows; a row matching both or neither is published unresolved "
                         "and never guessed"),
            "match_rule": ("a transfer is published only within one (leg, base count): the "
                           "multiplier divides the edge at the top draw count by the edge at the "
                           "row's own base count, so two base counts are different quantities"),
            "judge_rule": ("verdict = outside((b), scale_band(lo, hi, m)) with m the borrowed p95; "
                           "a move is published with its direction -- outside->inside loses a "
                           "rejection, inside->outside invents one"),
            "flat_rule": ("one number per (leg, base) = the pooled maximum p95 across windows, which "
                          "is what 'use the widest' actually adopts; the pooled minimum is published "
                          "beside it as the tight alternative"),
            "tolerance": TOL,
            "verdict_rule": ("'not a bound' requires a moved row, not a wide spread: spread without a "
                             "moved verdict is published as such"),
        },
        "source_faces": ["results/state_tilt/%s" % SRC_WIDTH],
        "windows_measured": sorted({c for (c, _l, _b) in arms}),
        "arms": sorted(arms.values(), key=lambda a: (a["cell"], a["leg"], a["base"])),
        "rows": records,
        "transfer": trans,
        "flat": flat,
        "dominator": dom,
        "cross_base_offset": offset,
        "rejudge_note": {
            "rows_where_e259_wide_verdict_differs": [
                {"index": r["index"], "cell": r["cell"], "row": r.get("row"),
                 "leg_used": r.get("leg"), "e259_published": r.get("published_verdict_wide"),
                 "resolved_leg": "outside" if r.get("verdict_wide") else "inside"}
                for r in records
                if r.get("status") == "measured" and r.get("e259_wide_verdict_reproduced") is False],
            "note": ("E259's row table judged every row on the self arm; a row whose coefficient is "
                     "the cross coefficient reads the cross interval. The list is disclosure, not a "
                     "correction of the record -- the E259 face keeps its published numbers"),
        },
        "verdict": v,
        "verdict_reason": why,
        "no_bill": NO_BILL,
    }
    out["summary"] = _summary(out)
    if save:
        _write(out, outdir)
    return out


def _summary(face):
    records = face.get("rows") or []
    measured = [x for x in records if x.get("status") == "measured"]
    pairs = [p for v in (face.get("transfer") or {}).values() for p in (v.get("pairs") or [])]
    flats = {k: v for k, v in (face.get("flat") or {}).items() if v.get("flat_p95") is not None}
    return {
        "windows": len(face.get("windows_measured") or []),
        "arms": len(face.get("arms") or []),
        "rows": len(records),
        "rows_measured": len(measured),
        "rows_leg_unresolved": sum(1 for x in records if x.get("status") == "leg_unresolved"),
        "rows_no_arm": sum(1 for x in records if x.get("status") == "no_arm"),
        "rows_unjudgeable": sum(1 for x in records if x.get("status") == "unjudgeable"),
        "pairs": len(pairs),
        "pairs_moving_a_verdict": sum(1 for p in pairs if p.get("n_moved")),
        "verdicts_moved": sum(p.get("n_moved") or 0 for p in pairs),
        "rejections_lost": sum(len([m for m in p["moved"]
                                    if m["direction"] == "rejections_lost"]) for p in pairs),
        "rejections_invented": sum(len([m for m in p["moved"]
                                        if m["direction"] == "rejections_invented"]) for p in pairs),
        "flat_moved_at_flat": sum(v.get("n_moved_at_flat") or 0 for v in flats.values()),
        "flat_moved_at_flat_tight": sum(v.get("n_moved_at_flat_tight") or 0 for v in flats.values()),
        "dominators": {k: v.get("dominator") for k, v in (face.get("dominator") or {}).items()},
        "p95_spread_pct_max": max([v.get("spread_pct") for v in (face.get("dominator") or {}).values()
                                   if v.get("spread_pct") is not None] or [None]),
        "e259_wide_verdict_differs": len(((face.get("rejudge_note") or {})
                                          .get("rows_where_e259_wide_verdict_differs") or [])),
        "verdict": face.get("verdict"),
    }


def _write(face, outdir, tag=""):
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "BANDTRANSFER-%s%s.json" % (face.get("evidence_cutoff"), tag))
    text = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text + "\n")
    with io.open(os.path.join(outdir, LATEST), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text + "\n")
    return path


def verify(outdir=None, tag=""):
    """Re-derive the published face and report every field that does not come back."""
    outdir = outdir or OUTDIR
    path = os.path.join(outdir, "BANDTRANSFER-%s%s.json" % (CUTOFF, tag))
    if not os.path.exists(path):
        return ["no published face at %s" % path]
    with io.open(path, encoding="utf-8") as fh:
        got = json.load(fh)
    fresh = run(save=False)
    problems = []
    for key in ("verdict", "verdict_reason", "summary", "frozen_spec", "transfer", "flat",
                "dominator", "arms", "rows", "cross_base_offset", "rejudge_note"):
        if got.get(key) != fresh.get(key):
            problems.append("%s does not re-derive" % key)
    if got.get("evidence_cutoff") != fresh.get("evidence_cutoff"):
        problems.append("evidence_cutoff does not re-derive")
    return problems


# ------------------------------------------------------------------ selftest
def _leg(ok, name, detail=None):
    return {"leg": name, "ok": bool(ok), "detail": detail}


def _arm(cell, leg, base, p05=1.0, p95=2.0):
    return {"cell": cell, "leg": leg, "base": base, "p05": p05, "p95": p95, "median": 1.5,
            "width": p95 - p05, "e258_width": 0.4, "ratio_vs_e258": 2.0}


def _row(cell, row, b, lo, hi, base=60, src="self_row.b_self"):
    return {"cell": cell, "row": row, "b": b, "band_lo": lo, "band_hi": hi,
            "band_draws": base, "b_source": src, "published_outside": True,
            "verdict_wide": "outside"}


def selftest():
    legs = []

    # --- the arm key carries leg and base, not base alone (the r1286 coarse-key pit)
    face = {"interval_spread": {"rows": [
        {"cell": "A", "arm": "self:60", "interval": [1.0, 1.5], "median": 1.2, "width": 0.5},
        {"cell": "A", "arm": "cross:60", "interval": [1.0, 2.5], "median": 1.4, "width": 1.5},
        {"cell": "A", "arm": "self:200", "interval": [1.0, 1.1], "median": 1.05, "width": 0.1},
    ]}}
    arms = arms_from(face)
    legs.append(_leg(len(arms) == 3, "three published arms read as three keys", len(arms)))
    legs.append(_leg(arms[("A", "cross", 60)]["p95"] == 2.5,
                     "a lookup by leg returns that leg's arm, not the default one"))
    legs.append(_leg(p95_of(arms, "A", "self", 200) == 1.1,
                     "a lookup by base count returns that base count's arm"))
    legs.append(_leg(p95_of(arms, "A", "self", 60) != p95_of(arms, "A", "cross", 60),
                     "the two legs at one base count are two different numbers"))
    legs.append(_leg(p95_of(arms, "B", "self", 60) is None,
                     "an unpublished cell has no arm and reads None, not zero"))

    # --- a name is not the leg it reads
    legs.append(_leg(resolve_leg({"b": 1.0, "b_source": "self_row.b_self"}, [])[0] == "self",
                     "b_source self_row.b_self resolves to the self leg"))
    legs.append(_leg(resolve_leg({"b": 1.0, "b_source": "cross_row.b_cross"}, [])[0] == "cross",
                     "b_source cross_row.b_cross resolves to the cross leg"))
    cell_rows = [{"row": "self", "b": -0.30}, {"row": "cross", "b": -0.833}]
    got, why = resolve_leg({"b": -0.833, "b_source": "star_residual.b1"}, cell_rows)
    legs.append(_leg(got == "cross", "a residual with no leg is resolved by coefficient identity",
                     why))
    got, why = resolve_leg({"b": -0.99, "b_source": "star_residual.b1"}, cell_rows)
    legs.append(_leg(got is None and "no published row" in why,
                     "a coefficient that matches nothing is published unresolved, not guessed", why))
    got, why = resolve_leg({"b": -1.0, "b_source": "star_residual.b1"},
                           [{"row": "self", "b": -1.0}, {"row": "cross", "b": -1.0}])
    legs.append(_leg(got is None and "ambiguous" in why,
                     "a coefficient matching both legs is ambiguous and never guessed", why))
    legs.append(_leg(resolve_leg({"b": None}, [])[0] is None,
                     "a row with no coefficient has no leg"))

    # --- judging and direction
    legs.append(_leg(judge(-0.9, -0.3, 0.3, 5.0) is False,
                     "a coefficient of 0.9 inside a band scaled by 5 is inside"))
    legs.append(_leg(judge(-0.9, -0.3, 0.3, 1.0) is True,
                     "the same row at the unscaled band is outside"))
    legs.append(_leg(judge(None, -0.3, 0.3, 1.0) is None,
                     "no coefficient means no verdict, not 'inside'"))
    legs.append(_leg(judge(-0.9, None, 0.3, 1.0) is None, "no band means no verdict"))
    legs.append(_leg(_dir(True, False) == "rejections_lost",
                     "outside->inside is a lost rejection"))
    legs.append(_leg(_dir(False, True) == "rejections_invented",
                     "inside->outside is an invented rejection"))
    legs.append(_leg(_dir(True, True) is None and _dir(False, False) is None,
                     "an unchanged verdict has no direction"))

    # --- the matrix never crosses a leg or a base count
    arms2 = {("A", "self", 60): _arm("A", "self", 60, p95=2.0),
             ("B", "self", 60): _arm("B", "self", 60, p95=3.0),
             ("A", "cross", 60): _arm("A", "cross", 60, p95=9.0),
             ("A", "self", 200): _arm("A", "self", 200, p95=9.0),
             ("B", "self", 200): _arm("B", "self", 200, p95=1.0)}
    recs = row_records({"rows": [_row("A", "self", -0.7, -0.3, 0.3, base=60)]}, arms2)
    legs.append(_leg(recs[0]["status"] == "measured", "a resolvable row is measured",
                     recs[0].get("reason")))
    legs.append(_leg(recs[0]["own_p95"] == 2.0,
                     "the row is judged on its own arm's p95, not another cell's"))
    tr = transfer(recs, arms2)
    pairs = tr["self:60"]["pairs"]
    to_a = [p for p in pairs if p["recipient"] == "A"]
    legs.append(_leg(len(pairs) == 2 and len(to_a) == 1 and to_a[0]["donor"] == "B",
                     "only the cell sharing leg AND base count is a donor", len(pairs)))
    legs.append(_leg(to_a[0]["donor_p95"] == 3.0,
                     "the donor contributes its own p95, not the cross or 200 arm"))
    legs.append(_leg(len(to_a[0]["moved"]) == 1
                     and to_a[0]["moved"][0]["direction"] == "rejections_lost",
                     "a wider donor loses a rejection on a row that sat just outside"))
    legs.append(_leg(tr["cross:60"]["cells"] == ["A"] and not tr["cross:60"]["pairs"],
                     "a (leg, base) with one window publishes no pair and says why"))
    legs.append(_leg(tr["self:200"]["cells"] == ["A", "B"]
                     and len(tr["self:200"]["pairs"]) == 2,
                     "the same two cells at another base count form their own pairs"))

    # --- a row whose own arm is missing is not counted as moved
    recs2 = row_records({"rows": [_row("Z", "self", -0.9, -0.3, 0.3, base=60)]}, arms2)
    legs.append(_leg(recs2[0]["status"] == "no_arm",
                     "a row whose cell publishes no arm at its base count says so"))
    tr2 = transfer(recs2, arms2)
    legs.append(_leg(all(p["n_moved"] == 0 for p in tr2["self:60"]["pairs"]),
                     "a row without an own arm cannot be moved by anyone"))

    # --- a row whose band is missing is unjudgeable and never guessed
    recs3 = row_records({"rows": [_row("A", "self", -0.5, None, 0.3, base=60)]}, arms2)
    legs.append(_leg(recs3[0]["status"] == "unjudgeable",
                     "a row without a band is unjudgeable"))
    legs.append(_leg(recs3[0]["verdict_wide"] if "verdict_wide" in recs3[0] else None is None,
                     "an unjudgeable row publishes no verdict"))

    # --- dominator and flat read
    dom = dominator(arms2, "self", 60)
    legs.append(_leg(dom["dominator"] == "B", "B's 3.0 dominates A's 2.0 at self:60", dom))
    legs.append(_leg(abs(dom["spread_pct"] - 50.0) < 1e-9,
                     "spread is published as a percentage of the lower end"))
    arms3 = dict(arms2)
    arms3[("B", "self", 60)] = _arm("B", "self", 60, p95=2.0)
    dom3 = dominator(arms3, "self", 60)
    legs.append(_leg(dom3["dominator"] is None
                     and sorted(dom3["tied_at_max"]) == ["A", "B"],
                     "a tie at the maximum publishes both cells instead of picking one", dom3))
    flat = flat_read(recs, arms2)
    legs.append(_leg(flat["self:60"]["flat_p95"] == 3.0
                     and flat["self:60"]["flat_p95_from"] == ["B"],
                     "the flat read adopts the pooled maximum and names its source"))
    legs.append(_leg(flat["self:60"]["flat_tight_p95"] == 2.0,
                     "the tight alternative is the pooled minimum"))
    legs.append(_leg(flat["self:60"]["n_moved_at_flat"] == 1,
                     "the flat maximum moves the row that its own arm kept out"))

    # --- verdict is driven by moved rows, not by spread (name-is-semantics guard)
    v, why = verdict_of(recs, tr, flat, {"self:60": dom})
    legs.append(_leg(v == "a_foreign_wide_end_is_not_a_bound",
                     "a moved row makes the foreign wide end not a bound", why))
    # same recs, but the donor interval equals the recipient's: nothing moves
    arms4 = {("A", "self", 60): _arm("A", "self", 60, p95=2.0),
             ("B", "self", 60): _arm("B", "self", 60, p95=2.0)}
    tr4 = transfer(recs, arms4)
    flat4 = flat_read(recs, arms4)
    v4, why4 = verdict_of(recs, tr4, flat4, {"self:60": dominator(arms4, "self", 60)})
    legs.append(_leg(v4 == "the_wide_end_transfers_without_moving_a_verdict",
                     "identical intervals move nothing and the verdict says so", why4))
    v5, why5 = verdict_of([], {}, {}, {})
    legs.append(_leg(v5 == "no_windows_measured",
                     "no face means no windows measured", why5))

    # --- cross-base offsets are disclosed, never mixed into the matrix
    off = cross_base_offset(arms2)
    legs.append(_leg(abs(off["self"]["ratio_median"] - 0.5) < 1e-9,
                     "the disclosure compares the two base counts without judging them", off["self"]))
    legs.append(_leg("self" in off and "cross" not in off,
                     "a leg with only one base count publishes no offset"))

    # --- determinism and the published numbers re-derive
    a = run(save=False)
    b = run(save=False)
    legs.append(_leg(a.get("verdict") == b.get("verdict")
                     and a.get("summary") == b.get("summary")
                     and a.get("transfer") == b.get("transfer"),
                     "two runs of the same face publish the same numbers",
                     a.get("verdict")))
    legs.append(_leg(a.get("source_faces") == ["results/state_tilt/%s" % SRC_WIDTH],
                     "the face reads E259 only -- no second source is mixed in"))
    legs.append(_leg(len(a.get("arms") or []) == 16,
                     "the published face carries all 16 windows x legs x base counts",
                     len(a.get("arms") or [])))

    ok = all(x["ok"] for x in legs)
    return {"ok": ok, "legs": legs, "passed": sum(1 for x in legs if x["ok"]),
            "total": len(legs)}


# ------------------------------------------------------------------ main
def main(argv=None):
    ap = argparse.ArgumentParser(description=STUDY)
    ap.add_argument("cmd", nargs="?", default="run",
                    choices=("run", "verify", "selftest", "show"))
    args = ap.parse_args(argv)
    if args.cmd == "selftest":
        res = selftest()
        for x in res["legs"]:
            print(("PASS " if x["ok"] else "FAIL ") + x["leg"])
        print("%d/%d" % (res["passed"], res["total"]))
        return 0 if res["ok"] else 1
    if args.cmd == "verify":
        probs = verify()
        for p in probs:
            print("PROBLEM " + p)
        print("%d problem(s)" % len(probs))
        return 0 if not probs else 1
    face = run()
    if args.cmd == "show":
        print(json.dumps(face.get("summary"), ensure_ascii=False, indent=1))
        print(face.get("verdict"), "--", face.get("verdict_reason"))
    return 0


if __name__ == "__main__":
    sys.exit(main())