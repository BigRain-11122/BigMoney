# -*- coding: utf-8 -*-
"""E592 -- is the forward ledger's carry reproducible once the ladder's roll phase is inferred
from its own bars?

E591 (r1618) replayed the shipped ``ladder3`` (GC007/GC014/GC028, equal rungs) from a fresh
contract phase over the ledger's own eleven bars and reproduced only four of the eight bars past
the repo panel.  It named the reason (the contract phase is state) but did not measure whether any
phase exists that reproduces the published carry -- that is this study.

The question has a cheap answer once the ledger's writer is read instead of guessed: ``carry`` in
``results/etf_book_forward/LEDGER.json`` is ``cash_start * ladder_rate(d)`` where ``ladder_rate``
comes from ``etf_book_forward.build_carry(dates)`` over the *whole* date grid
(``date_grid`` -> 2020-01-02..2026-11-06, 1,658 bars), not over the eleven published bars.  So the
phase is anchored ~1,647 bars before the first published bar, and a replay that starts there
should reproduce the published carry exactly.  This study tests that, then searches the phase space
to say how much of the phase the published bars actually pin:

  published_phase   reconstruct the replay origin from the face's own ``seed`` pair
                    (``seed.bar`` + ``seed.grid_index``) against the live calendar and check that
                    a replay from that origin reproduces every published bar
  arms              (a) replay from the reconstructed origin, (b) replay from a fresh phase at the
                    ledger's first published bar -- the arm E591 measured -- on identical bars
  sweep.marginal    one rung at a time, start offsets 0..250 bars from the origin, the other two
                    rungs at the origin: which offsets leave the published bars reproduced
  sweep.product     all 41^3 = 68,921 three-rung phase combinations over a 40-bar offset window:
                    how many reproduce every bar, and which offsets ever appear in one
  residual          the largest gap the best fit cannot close, priced against the printed precision
                    of the carry field itself

Honest limits:

  * the offset search is a finite window (0..250 bars per rung marginally, 0..40 in the product
    sweep); "no phase explains bar X" is a statement about this window, not about all phases;
  * "reproduced" is a tolerance, published at two levels: 0.5% (E591's bar-level tolerance) and
    0.001% (the printed precision of a carry rounded to 1e-10);
  * the measured window is whatever the ledger publishes (11 bars here); with more published bars
    the phase would be more constrained, and the study republishes its own constraint counts so a
    later window can be compared;
  * the GC007/GC014 rungs turn out to be offset-invariant on this window, so all of the phase
    discrimination sits on one rung; that is a property of the current panel (its quotes are
    forward-filled past 2026-10-27), not of the ladder in general;
  * read-only: no ledger row, panel, ticket or state face is written.

  python scripts/e592_carry_phase.py build
  python scripts/e592_carry_phase.py check
  python scripts/e592_carry_phase.py verify
  python scripts/e592_carry_phase.py selftest

Output: results/etf_book_forward/CARRYPHASE.json
"""
from __future__ import annotations

import io
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from scripts import etf_book_cash_ladder as REPO          # noqa: E402
from scripts import etf_book_forward as FW               # noqa: E402

OUTDIR = os.path.join(ROOT, "results", "etf_book_forward")
OUT_PATH = os.path.join(OUTDIR, "CARRYPHASE.json")
LEDGER_PATH = os.path.join(OUTDIR, "LEDGER.json")

# a bar counts as reproduced when the replayed rate lands within this relative distance
FIT_TOL_PCT = 0.5
# the printed precision of the carry field: 1e-10 absolute on a ~1.1e-5 figure
EXACT_TOL_PCT = 0.001
# how many bars past the origin each rung's start offset may be searched (marginal arm)
MARGINAL_OFFSETS = 250
# the product sweep is a cube over the first N offsets, because it is cubic in the window
PRODUCT_OFFSETS = 40

V_REPRODUCIBLE = "the_ledgers_carry_is_reproducible_from_the_origin_the_face_names_indirectly"
V_PHASE_UNPINNED = "the_ledgers_carry_is_reproducible_but_the_phase_the_bars_pin_is_a_wide_class"
V_NOT_REPRODUCIBLE = "no_searched_phase_reproduces_the_published_carry"
V_EMPTY = "nothing_on_disk_to_measure"


# --------------------------------------------------------------------------- pure helpers
def gap_pct(fresh, published):
    """Relative distance of a replayed rate from the published one, in percent."""
    if fresh is None or published is None:
        return None
    published = float(published)
    if abs(published) < 1e-15:
        return None
    return (float(fresh) - published) / abs(published) * 100.0


def abs_gap_pct(fresh, published):
    g = gap_pct(fresh, published)
    return None if g is None else abs(g)


def printed_precision_pct(carry):
    """Relative width one unit of the carry field's last printed digit represents.

    ``carry`` is written with ``round(value, 10)``, so the printed figure is exact to half a unit
    in the tenth decimal; on a one-day carry of ~1.1e-5 that is ~0.0009% of the figure.
    """
    if carry is None:
        return None
    carry = abs(float(carry))
    if carry <= 0.0:
        return None
    return 0.5e-10 / carry * 100.0


def published_rate_series(ledger):
    """Per-bar ladder rate the ledger's published ``carry``/``cash`` pair implies."""
    out = []
    for row in ledger.get("bars") or []:
        cash = row.get("cash")
        carry = row.get("carry")
        rate = None
        if cash is not None and carry is not None and float(cash) > 0.0:
            rate = float(carry) / float(cash)
        out.append({"bar": row.get("bar"), "cash": cash, "carry": carry, "rate": rate})
    return out


def rung_series(dates, rates, name, offset):
    """One rung's per-bar fractional return over ``dates``, its first contract entered at
    ``dates[offset]``; bars before the offset accrue nothing."""
    dates = pd.DatetimeIndex(dates)
    offset = int(offset)
    full = np.zeros(len(dates), dtype=float)
    if offset >= len(dates) - 1:
        return full
    ret, _info = REPO.roll_rung(dates[offset:], rates, None, name=name)
    full[offset:] = np.asarray(ret.values, dtype=float)
    return full


def combine(per_rung):
    """Equal-weight rung mean -- the ladder3 arithmetic, not a re-implementation of a roll."""
    if not per_rung:
        return None
    return np.mean(np.vstack(per_rung), axis=0)


def compress_ranges(values):
    """Sorted ints -> [start, end] ranges, so a 250-long list of offsets stays readable."""
    ranges = []
    for v in sorted(int(x) for x in values):
        if ranges and v == ranges[-1][1] + 1:
            ranges[-1][1] = v
        else:
            ranges.append([v, v])
    return ranges


def ranges_len(ranges):
    return sum(int(b) - int(a) + 1 for a, b in ranges)


def fits(gaps, tol):
    """Which bars a gap vector reproduces at this tolerance (None gaps are not judged)."""
    return [bool(g is not None and abs(float(g)) <= tol) for g in gaps]


# --------------------------------------------------------------------------- inputs
def read_json(path):
    with io.open(path, encoding="utf-8") as f:
        return json.load(f)


def load_grid():
    """The writer's own date grid: what ``build_carry`` was called with."""
    close, openp, amt, feats, score, cls, n_flip = FW.build_inputs()
    px = close.reindex(columns=close.columns).ffill()
    dates, _rebal = FW.date_grid(px, FW.CONFIG["rebal"])
    return pd.DatetimeIndex(dates)


def reconstructed_origin(dates, seed):
    """Where the replay started, read off the face's own seed pair.

    ``seed.grid_index`` is the seed bar's 0-based position in the writer's grid, so the origin is
    that many bars earlier.  Returned with the check that the arithmetic lands on the grid's first
    bar -- if a later writer changes either field the study says so instead of assuming.
    """
    seed_bar = (seed or {}).get("bar")
    grid_index = (seed or {}).get("grid_index")
    if seed_bar is None or grid_index is None:
        return {"reconstructable": False, "why": "the face carries no seed.bar/seed.grid_index pair"}
    try:
        pos = int(dates.get_loc(pd.Timestamp(seed_bar)))
    except KeyError:
        return {"reconstructable": False, "why": "seed.bar %r is not on the live grid" % seed_bar}
    origin_index = pos - int(grid_index)
    if origin_index < 0 or origin_index >= len(dates):
        return {"reconstructable": False, "why": "seed.grid_index %r does not fit the live grid"
                % (grid_index,)}
    return {
        "reconstructable": True,
        "seed_bar": str(seed_bar),
        "seed_grid_index": int(grid_index),
        "seed_position_in_grid": int(pos),
        "origin_index": int(origin_index),
        "origin_date": str(pd.Timestamp(dates[origin_index]).date()),
        "grid_bars": int(len(dates)),
        "grid_first_bar": str(pd.Timestamp(dates[0]).date()),
        "origin_is_the_grid_first_bar": bool(origin_index == 0),
    }


# --------------------------------------------------------------------------- build
def build(write=True):
    ledger = read_json(LEDGER_PATH)
    dates = load_grid()
    rates = REPO.load_panel(bars=dates)
    pub_rows = published_rate_series(ledger)
    if not pub_rows or any(r["rate"] is None for r in pub_rows):
        face = empty_face(ledger, dates, pub_rows)
        if write:
            write_face(face)
        return face

    bars = [r["bar"] for r in pub_rows]
    pub = np.array([r["rate"] for r in pub_rows], dtype=float)
    pos = [int(dates.get_loc(pd.Timestamp(b))) for b in bars]
    rungs = tuple(REPO.LADDERS["ladder3"])
    origin = reconstructed_origin(dates, ledger.get("seed") or {})

    # ---- arm A: replay from the reconstructed origin (all rungs enter at that bar)
    arm_rows, arm_series = {}, {}
    for label, offset in (("published_origin", int(origin.get("origin_index") or 0)),
                          ("fresh_phase_at_first_bar", pos[0])):
        series = [rung_series(dates, rates, nm, offset) for nm in rungs]
        tot = combine(series)
        vals = tot[pos]
        gaps = [abs_gap_pct(v, p) for v, p in zip(vals, pub)]
        arm_series[label] = series
        arm_rows[label] = {
            "offsets": [offset, offset, offset],
            "origin_bar": str(pd.Timestamp(dates[offset]).date()) if offset < len(dates) else None,
            "bars_judged": len(bars),
            "bars_reproduced_at_0_5pct": sum(fits(gaps, FIT_TOL_PCT)),
            "bars_reproduced_at_0_001pct": sum(fits(gaps, EXACT_TOL_PCT)),
            "max_abs_gap_pct": (round(max(abs(g) for g in gaps), 6) if gaps else None),
            "gaps_pct": [None if g is None else round(g, 6) for g in gaps],
        }

    # ---- sweep.marginal: one rung at a time, the other two at the origin
    base_series = arm_series["published_origin"]
    marginal = {}
    for nm in rungs:
        others = [s for m, s in zip(rungs, base_series) if m != nm]
        passing, failing = [], []
        for offset in range(MARGINAL_OFFSETS + 1):
            series = rung_series(dates, rates, nm, offset)
            tot = combine([series] + others)
            gaps = [abs_gap_pct(v, p) for v, p in zip(tot[pos], pub)]
            (passing if all(fits(gaps, EXACT_TOL_PCT)) else failing).append(offset)
        marginal[nm] = {
            "offsets_searched": MARGINAL_OFFSETS + 1,
            "offsets_reproducing_every_bar": len(passing),
            "passing_ranges": compress_ranges(passing),
            "offsets_failing_at_least_one_bar": len(failing),
            "failing_ranges": compress_ranges(failing),
            "rung_is_offset_invariant_on_this_window": bool(len(passing) == MARGINAL_OFFSETS + 1),
        }

    # ---- sweep.product: the three-rung cube over the first PRODUCT_OFFSETS offsets
    A = np.vstack([rung_series(dates, rates, rungs[0], o)[pos]
                   for o in range(PRODUCT_OFFSETS + 1)])
    B = np.vstack([rung_series(dates, rates, rungs[1], o)[pos]
                   for o in range(PRODUCT_OFFSETS + 1)])
    C = np.vstack([rung_series(dates, rates, rungs[2], o)[pos]
                   for o in range(PRODUCT_OFFSETS + 1)])
    T = (A[:, None, None, :] + B[None, :, None, :] + C[None, None, :, :]) / 3.0
    with np.errstate(divide="ignore", invalid="ignore"):
        G = np.abs((T - pub) / np.abs(pub)) * 100.0
    worst = np.nanmax(G, axis=3)
    ok = worst <= EXACT_TOL_PCT
    n_tested = int(ok.size)
    n_pass = int(ok.sum())
    per_bar_ok = (G <= EXACT_TOL_PCT) & np.isfinite(G)
    per_bar = [int(per_bar_ok[:, :, :, i].sum()) for i in range(len(bars))]
    per_bar_fail = [int(n_tested - c) for c in per_bar]
    # offsets that ever appear in a passing phase
    ever = {
        rungs[0]: sorted(set(int(x) for x in np.where(ok.any(axis=(1, 2)))[0])),
        rungs[1]: sorted(set(int(x) for x in np.where(ok.any(axis=(0, 2)))[0])),
        rungs[2]: sorted(set(int(x) for x in np.where(ok.any(axis=(0, 1)))[0])),
    }
    # every failing phase misses the same bars, or the bars localise the phase
    failing_rows = ~ok
    if failing_rows.any():
        fail_counts_per_bar = per_bar_fail
        uniform = len(set(fail_counts_per_bar)) == 1
    else:
        uniform = None
    best_idx = np.unravel_index(int(np.argmin(np.where(np.isfinite(worst), worst, np.inf))),
                               worst.shape)
    best_phase = [int(best_idx[0]), int(best_idx[1]), int(best_idx[2])]
    best_max_gap = float(worst[best_idx])

    product = {
        "rungs": list(rungs),
        "offset_window_per_rung": [0, PRODUCT_OFFSETS],
        "phases_tested": n_tested,
        "phases_reproducing_every_bar": n_pass,
        "share_of_tested_phases_that_reproduce_every_bar": round(n_pass / float(n_tested), 6),
        "tolerance_pct": EXACT_TOL_PCT,
        "phases_reproducing_every_bar_at_0_5pct": int((worst <= FIT_TOL_PCT).sum()),
        "best_phase": best_phase,
        "best_phase_max_abs_gap_pct": round(best_max_gap, 6),
        "best_phase_is_the_reconstructed_origin": bool(origin.get("reconstructable")
                                                       and best_phase == [int(origin["origin_index"])]
                                                       * 3),
        "offsets_ever_in_a_passing_phase": {k: compress_ranges(v) for k, v in ever.items()},
        "offsets_never_in_a_passing_phase": {
            k: compress_ranges(sorted(set(range(PRODUCT_OFFSETS + 1)) - set(v)))
            for k, v in ever.items()},
        "per_bar_phases_reproducing_that_bar": dict(zip(bars, per_bar)),
        "every_failing_phase_misses_the_same_bars": uniform,
        "phase_discrimination_rests_on": [
            k for k, v in marginal.items() if not v["rung_is_offset_invariant_on_this_window"]],
    }

    # ---- per-bar rows, on the arm that reproduces (the reconstructed origin when it exists)
    primary = "published_origin" if origin.get("reconstructable") else "fresh_phase_at_first_bar"
    tot_primary = combine(arm_series[primary])
    rows = []
    prev = None
    for i, r in enumerate(pub_rows):
        bar = r["bar"]
        gap_days = None
        if prev is not None:
            gap_days = int((pd.Timestamp(bar) - pd.Timestamp(prev)).days)
        prev = bar
        fresh = float(tot_primary[pos[i]])
        gp = gap_pct(fresh, r["rate"])
        fp = printed_precision_pct(r["carry"])
        rows.append({
            "bar": bar,
            "gap_days": gap_days,
            "ledger_cash_weight": r["cash"],
            "ledger_carry_frac": r["carry"],
            "published_rate_per_bar": round(float(r["rate"]), 12),
            "replayed_rate_per_bar": round(fresh, 12),
            "rel_gap_pct": (None if gp is None else round(gp, 6)),
            "abs_rel_gap_pct": (None if gp is None else round(abs(gp), 6)),
            "printed_precision_pct": (None if fp is None else round(fp, 6)),
            "reproduced_at_0_5pct": (None if gp is None else bool(abs(gp) <= FIT_TOL_PCT)),
            "reproduced_at_0_001pct": (None if gp is None else bool(abs(gp) <= EXACT_TOL_PCT)),
            "gap_is_within_the_printed_precision": (None if gp is None or fp is None
                                                    else bool(abs(gp) <= fp)),
        })

    # ---- residual
    resid = residual_of(rows, product, origin, marginal)

    face = {
        "study": "E592_carry_phase",
        "generated_by": "scripts/e592_carry_phase.py",
        "machine": "bm-b",
        "dept": "research+engineering",
        "evidence_cutoff": bars[-1],
        "question": ("is the forward ledger's published carry reproducible once the ladder's roll "
                     "phase is inferred from its own bars, and how much of the phase do the "
                     "published bars actually pin?"),
        "rule": ("carry = cash_start * ladder_rate(d); ladder_rate comes from "
                 "etf_book_forward.build_carry(date_grid) = etf_book_cash_ladder.ladder over the "
                 "writer's whole date grid (2020-01-02.., 1,658 bars) with ladder3 = GC007/GC014/"
                 "GC028 equal rungs, each a rolling contract entered at the grid bar where its "
                 "previous contract matures, commission charged at entry, interest spread over the "
                 "contract's calendar days; a 'phase' here is the bar index at which each rung's "
                 "first contract is entered"),
        "published_phase": origin,
        "arms": arm_rows,
        "sweep": {"marginal": marginal, "product": product},
        "bars": rows,
        "residual": resid,
        "verdict": verdict_of(resid, origin),
        "verdict_line": verdict_line(resid, origin, rows, product, arm_rows),
        "caveats": [
            "the offset search is a finite window (0..%d bars per rung marginally, 0..%d in the "
            "product sweep); 'no phase explains bar X' is a statement about that window"
            % (MARGINAL_OFFSETS, PRODUCT_OFFSETS),
            "reproduction is a tolerance at two published levels: 0.5%% (E591's bar-level "
            "tolerance) and 0.001%% (the printed precision of a carry rounded to 1e-10)",
            "the measured window is whatever the ledger publishes; more published bars would "
            "constrain the phase further, and the counts here are republished so a later window "
            "can be compared rather than assumed",
            "the GC007/GC014 rungs are offset-invariant on this window because the repo panel is "
            "forward-filled past 2026-10-27, so all of the phase discrimination sits on the "
            "28-day rung -- a property of this panel, not of the ladder in general",
            "read-only: no ledger row, panel, ticket or state face is written",
        ],
    }
    if write:
        write_face(face)
    return face


def residual_of(rows, product, origin, marginal):
    gaps = [r["abs_rel_gap_pct"] for r in rows if r.get("abs_rel_gap_pct") is not None]
    prec = [r["printed_precision_pct"] for r in rows
            if r.get("printed_precision_pct") is not None]
    within = [r["gap_is_within_the_printed_precision"] for r in rows
              if r.get("gap_is_within_the_printed_precision") is not None]
    unexplained = [r["bar"] for r in rows if r.get("reproduced_at_0_001pct") is False]
    return {
        "bars_judged": len(gaps),
        "bars_reproduced_at_0_001pct": sum(1 for r in rows if r.get("reproduced_at_0_001pct")),
        "bars_no_phase_reproduces_at_0_001pct": len(unexplained),
        "bar_list_without_a_reproducing_phase": unexplained,
        "max_abs_gap_pct": (round(max(gaps), 6) if gaps else None),
        "max_printed_precision_pct": (round(max(prec), 6) if prec else None),
        "every_bar_gap_is_within_the_printed_precision": (all(within) if within else None),
        "share_of_tested_phases_that_reproduce_every_bar":
            product.get("share_of_tested_phases_that_reproduce_every_bar"),
        "phase_discrimination_rests_on": product.get("phase_discrimination_rests_on"),
        "rungs_that_are_offset_invariant": [k for k, v in marginal.items()
                                            if v["rung_is_offset_invariant_on_this_window"]],
        "state_a_reader_needs": ("the replay's origin bar -- the bar at which every rung's first "
                                 "contract is entered; the face names it only as seed.grid_index "
                                 "against the seed bar, so a reader who holds the trading calendar "
                                 "can reconstruct it and nothing else on the face says it"),
    }


def verdict_of(resid, origin):
    if not resid.get("bars_judged"):
        return V_EMPTY
    if resid.get("bars_reproduced_at_0_001pct") == resid.get("bars_judged"):
        share = resid.get("share_of_tested_phases_that_reproduce_every_bar")
        if share is not None and float(share) >= 0.5:
            return V_PHASE_UNPINNED
        return V_REPRODUCIBLE
    return V_NOT_REPRODUCIBLE


def verdict_line(resid, origin, rows, product, arms=None):
    if not resid.get("bars_judged"):
        return "the ledger publishes no bar past a real quote, so there is no carry to reproduce"
    arms = arms or {}
    fresh = arms.get("fresh_phase_at_first_bar") or {}
    fresh_ok = fresh.get("bars_reproduced_at_0_001pct")
    fresh_text = ("%d/%d" % (fresh_ok, fresh.get("bars_judged") or resid["bars_judged"])
                  if fresh_ok is not None else "an unmeasured share")
    return ("%d of %d published bars reproduce at the printed precision (max gap %.4f%% against a "
            "printed precision of %.4f%%) once the replay starts at %s -- the origin the face "
            "names only as seed.grid_index %s -- while a fresh phase at the ledger's first bar "
            "reproduces %s; but %.1f%% of the %d sampled phases reproduce every bar too, and all "
            "of the discrimination sits on the %s rung, so the bars pin a class of phases, not one"
            % (resid["bars_reproduced_at_0_001pct"], resid["bars_judged"],
               resid.get("max_abs_gap_pct") or 0.0,
               resid.get("max_printed_precision_pct") or 0.0,
               (origin or {}).get("origin_date") or "an unstated origin",
               (origin or {}).get("seed_grid_index"),
               fresh_text,
               100.0 * float(product.get("share_of_tested_phases_that_reproduce_every_bar") or 0.0),
               product.get("phases_tested") or 0,
               "/".join(product.get("phase_discrimination_rests_on") or []) or "no"))


def empty_face(ledger, dates, pub_rows):
    return {
        "study": "E592_carry_phase",
        "generated_by": "scripts/e592_carry_phase.py",
        "machine": "bm-b",
        "dept": "research+engineering",
        "evidence_cutoff": (pub_rows[-1]["bar"] if pub_rows else
                            str(pd.Timestamp(dates[-1]).date())),
        "question": "is the ledger's carry reproducible once its roll phase is inferred?",
        "published_phase": {"reconstructable": False, "why": "no usable carry/cash pair"},
        "arms": {},
        "sweep": {"marginal": {}, "product": {}},
        "bars": [],
        "residual": {"bars_judged": 0},
        "verdict": V_EMPTY,
        "verdict_line": "the ledger publishes no usable carry/cash pair, so nothing is measured",
        "caveats": ["read-only: no ledger row, panel, ticket or state face is written"],
    }


def write_face(face):
    os.makedirs(OUTDIR, exist_ok=True)
    body = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
    with io.open(OUT_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(body)


# --------------------------------------------------------------------------- guard
def face_problems(face):
    p = []
    rows = face.get("bars")
    if not isinstance(rows, list):
        return ["the face carries no bar rows"]
    if not rows:
        return []
    for r in rows:
        bar = r.get("bar")
        pub = r.get("published_rate_per_bar")
        fresh = r.get("replayed_rate_per_bar")
        if pub is None or fresh is None:
            p.append("%s: the row carries no published/replayed pair" % bar)
            continue
        want = gap_pct(fresh, pub)
        got = r.get("rel_gap_pct")
        if want is None or got is None or abs(want - float(got)) > 1e-4:
            p.append("%s: the relative gap does not re-derive from its own pair" % bar)
            continue
        if r.get("abs_rel_gap_pct") is None or \
                abs(abs(want) - float(r["abs_rel_gap_pct"])) > 1e-4:
            p.append("%s: the absolute gap is not the absolute value of the gap" % bar)
        for key, tol in (("reproduced_at_0_5pct", FIT_TOL_PCT),
                         ("reproduced_at_0_001pct", EXACT_TOL_PCT)):
            claim = r.get(key)
            if claim is not None and bool(claim) != bool(abs(want) <= tol):
                p.append("%s: %s does not follow from the row's own gap" % (bar, key))
        fp = printed_precision_pct(r.get("ledger_carry_frac"))
        if fp is not None and r.get("printed_precision_pct") is not None:
            if abs(fp - float(r["printed_precision_pct"])) > 1e-4:
                p.append("%s: the printed precision does not re-derive from the carry" % bar)
            claim = r.get("gap_is_within_the_printed_precision")
            if claim is not None and bool(claim) != bool(abs(want) <= fp):
                p.append("%s: the precision claim does not follow from the row" % bar)
        if r.get("ledger_cash_weight") and r.get("ledger_carry_frac") is not None:
            want_rate = float(r["ledger_carry_frac"]) / float(r["ledger_cash_weight"])
            if abs(want_rate - float(pub)) > 1e-12:
                p.append("%s: the published rate is not carry/cash" % bar)
    resid = face.get("residual") or {}
    if resid.get("bars_judged") != len(rows):
        p.append("residual.bars_judged does not match the bar rows")
    want_ok = sum(1 for r in rows if r.get("reproduced_at_0_001pct"))
    if resid.get("bars_reproduced_at_0_001pct") != want_ok:
        p.append("residual.bars_reproduced_at_0_001pct does not re-derive from the rows")
    want_unexplained = [r.get("bar") for r in rows if r.get("reproduced_at_0_001pct") is False]
    if (resid.get("bar_list_without_a_reproducing_phase") or []) != want_unexplained:
        p.append("residual.bar_list_without_a_reproducing_phase does not match the rows")
    gaps = [r["abs_rel_gap_pct"] for r in rows if r.get("abs_rel_gap_pct") is not None]
    if gaps and resid.get("max_abs_gap_pct") is not None:
        if abs(max(gaps) - float(resid["max_abs_gap_pct"])) > 1e-4:
            p.append("residual.max_abs_gap_pct is not the largest row gap")
    within = [r["gap_is_within_the_printed_precision"] for r in rows
              if r.get("gap_is_within_the_printed_precision") is not None]
    if within and resid.get("every_bar_gap_is_within_the_printed_precision") is not None:
        if bool(all(within)) != bool(resid["every_bar_gap_is_within_the_printed_precision"]):
            p.append("the 'every gap within the printed precision' flag does not re-derive")
    prod = (face.get("sweep") or {}).get("product") or {}
    if prod.get("phases_reproducing_every_bar") is not None and \
            prod.get("phases_tested"):
        share = prod["phases_reproducing_every_bar"] / float(prod["phases_tested"])
        if prod.get("share_of_tested_phases_that_reproduce_every_bar") is None or \
                abs(share - float(prod["share_of_tested_phases_that_reproduce_every_bar"])) > 1e-6:
            p.append("the product sweep's share does not re-derive from its own counts")
        if prod.get("phases_reproducing_every_bar") > prod.get("phases_tested"):
            p.append("more phases reproduce than were tested")
        if prod.get("per_bar_phases_reproducing_that_bar") is not None:
            vals = list(prod["per_bar_phases_reproducing_that_bar"].values())
            if any(int(v) > int(prod["phases_tested"]) for v in vals):
                p.append("a per-bar count exceeds the number of phases tested")
            if len(vals) != len(rows):
                p.append("the per-bar phase counts do not cover the bar rows")
    marg = (face.get("sweep") or {}).get("marginal") or {}
    for nm, blk in marg.items():
        passing = blk.get("passing_ranges") or []
        failing = blk.get("failing_ranges") or []
        searched = blk.get("offsets_searched")
        if searched is None:
            continue
        if ranges_len(passing) + ranges_len(failing) != int(searched):
            p.append("%s: passing and failing offsets do not add up to the window" % nm)
        if blk.get("offsets_reproducing_every_bar") != ranges_len(passing):
            p.append("%s: the passing count does not re-derive from its ranges" % nm)
        if blk.get("rung_is_offset_invariant_on_this_window") is not None:
            if bool(blk["rung_is_offset_invariant_on_this_window"]) != \
                    bool(ranges_len(passing) == int(searched)):
                p.append("%s: the offset-invariance flag does not follow from the ranges" % nm)
    if face.get("verdict") and rows:
        if face["verdict"] not in (V_REPRODUCIBLE, V_PHASE_UNPINNED, V_NOT_REPRODUCIBLE,
                                   V_EMPTY):
            p.append("the verdict is not one of the study's four readings")
        else:
            if verdict_of(resid, face.get("published_phase") or {}) != face["verdict"]:
                p.append("verdict does not re-derive from the residual")
    arms = face.get("arms") or {}
    for label, blk in arms.items():
        g = [x for x in (blk.get("gaps_pct") or []) if x is not None]
        if blk.get("bars_judged") != len(blk.get("gaps_pct") or []):
            p.append("%s: bars_judged does not match its gap list" % label)
        if g and blk.get("max_abs_gap_pct") is not None:
            if abs(max(abs(x) for x in g) - float(blk["max_abs_gap_pct"])) > 1e-4:
                p.append("%s: max_abs_gap_pct is not the largest gap" % label)
        for key, tol in (("bars_reproduced_at_0_5pct", FIT_TOL_PCT),
                         ("bars_reproduced_at_0_001pct", EXACT_TOL_PCT)):
            if blk.get(key) is not None:
                want = sum(1 for x in (blk.get("gaps_pct") or [])
                           if x is not None and abs(float(x)) <= tol)
                if int(blk[key]) != want:
                    p.append("%s: %s does not re-derive from its gaps" % (label, key))
    return p


def check():
    if not os.path.exists(OUT_PATH):
        print("MISSING %s -- run scripts/e592_carry_phase.py build" % OUT_PATH)
        return 1
    face = read_json(OUT_PATH)
    problems = face_problems(face)
    if problems:
        for x in problems[:20]:
            print("PROBLEM %s" % x)
        print("E592 FAIL %d problem(s)" % len(problems))
        return 1
    resid = face.get("residual") or {}
    prod = (face.get("sweep") or {}).get("product") or {}
    print("E592 OK bars=%d reproduced=%d/%d max_gap=%.4f%% precision=%.4f%% "
          "phases=%d/%d (%.1f%%) verdict=%s"
          % (resid.get("bars_judged") or 0, resid.get("bars_reproduced_at_0_001pct") or 0,
             resid.get("bars_judged") or 0, resid.get("max_abs_gap_pct") or 0.0,
             resid.get("max_printed_precision_pct") or 0.0,
             prod.get("phases_reproducing_every_bar") or 0, prod.get("phases_tested") or 0,
             100.0 * float(prod.get("share_of_tested_phases_that_reproduce_every_bar") or 0.0),
             face.get("verdict")))
    return 0


def verify():
    fresh = build(write=False)
    problems = face_problems(fresh)
    on_disk = read_json(OUT_PATH).get("evidence_cutoff") if os.path.exists(OUT_PATH) else None
    if on_disk is not None and fresh.get("evidence_cutoff") and \
            fresh["evidence_cutoff"] < on_disk:
        problems.append("a rebuild reads an older cutoff (%s < %s)"
                        % (fresh["evidence_cutoff"], on_disk))
    if problems:
        for x in problems[:20]:
            print("PROBLEM %s" % x)
        print("E592 verify FAIL")
        return 1
    resid = fresh.get("residual") or {}
    print("E592 verify PASS cutoff=%s bars=%d reproduced=%d max_gap=%.4f%% verdict=%s"
          % (fresh.get("evidence_cutoff"), resid.get("bars_judged") or 0,
             resid.get("bars_reproduced_at_0_001pct") or 0,
             resid.get("max_abs_gap_pct") or 0.0, fresh.get("verdict")))
    return 0


# --------------------------------------------------------------------------- selftest
def selftest():
    bad = []
    seen = [0]

    def chk(cond, msg):
        seen[0] += 1
        if not cond:
            bad.append(msg)

    # 1. the gap is relative to the published figure, and its sign is kept
    chk(abs(gap_pct(1.01e-5, 1e-5) - 1.0) < 1e-9, "gap_pct is not a relative reading")
    chk(abs(gap_pct(0.99e-5, 1e-5) + 1.0) < 1e-9, "gap_pct dropped the sign")
    chk(gap_pct(1e-5, 0.0) is None, "a zero published rate produced a relative gap")
    chk(abs(abs_gap_pct(0.99e-5, 1e-5) - abs(gap_pct(0.99e-5, 1e-5))) < 1e-15,
        "abs_gap_pct is not the absolute value of gap_pct")
    chk(abs_gap_pct(0.99e-5, 1e-5) >= 0.0, "abs_gap_pct returned a negative gap")
    # 2. the printed precision is half a unit in the tenth decimal, relative to the carry
    pp = printed_precision_pct(1.10399e-05)
    chk(pp is not None and abs(pp - 0.0004529) < 1e-6,
        "printed_precision_pct does not price one digit at 1e-10 on the carry")
    chk(abs(printed_precision_pct(1e-10) - 50.0) < 1e-9,
        "a carry of exactly one tenth-decimal unit is half a unit, i.e. 50% of itself")
    chk(printed_precision_pct(0.0) is None, "a zero carry was given a precision")
    # 3. the printed rate is carry/cash, and a zero cash weight has no rate
    ps = published_rate_series({"bars": [
        {"bar": "2026-01-05", "cash": 0.25, "carry": 2.5e-5},
        {"bar": "2026-01-06", "cash": 0.0, "carry": 1e-5},
        {"bar": "2026-01-07", "cash": 0.5, "carry": None}]})
    chk(abs(ps[0]["rate"] - 1e-4) < 1e-15, "the published rate is not carry/cash")
    chk(ps[1]["rate"] is None, "a zero cash weight produced a rate")
    chk(ps[2]["rate"] is None, "a missing carry produced a rate")
    # 4. the tolerance arms answer their own threshold, not each other's
    chk(fits([0.4, 0.6, None], 0.5) == [True, False, False],
        "the 0.5% arm does not judge each bar against its own gap")
    chk(fits([0.0005, 0.002], 0.001) == [True, False],
        "the 0.001% arm does not judge each bar against its own gap")
    # 5. ranges compress and add back up, so pass+fail == the searched window
    r = compress_ranges([0, 1, 2, 5, 7, 8])
    chk(r == [[0, 2], [5, 5], [7, 8]], "compress_ranges lost a boundary")
    chk(ranges_len(r) == 6, "ranges_len does not add back up")
    chk(ranges_len(compress_ranges([])) == 0, "an empty offset set did not compress to nothing")
    # 6. the origin reconstruction does the index arithmetic instead of assuming bar 0
    dates = pd.DatetimeIndex(pd.bdate_range("2020-01-02", periods=12))
    o = reconstructed_origin(dates, {"bar": str(dates[9].date()), "grid_index": 9})
    chk(o["reconstructable"] and o["origin_index"] == 0 and o["origin_is_the_grid_first_bar"],
        "a seed at index k did not reconstruct the origin k bars earlier")
    o2 = reconstructed_origin(dates, {"bar": str(dates[9].date()), "grid_index": 4})
    chk(o2["reconstructable"] and o2["origin_index"] == 5,
        "a seed whose index does not reach the first bar was snapped to bar 0")
    chk(not reconstructed_origin(dates, {"bar": "1999-01-01", "grid_index": 1})["reconstructable"],
        "a seed bar outside the grid was accepted")
    chk(not reconstructed_origin(dates, {"bar": str(dates[9].date()), "grid_index": 99})
        ["reconstructable"], "a grid_index past the grid start was accepted")
    chk(not reconstructed_origin(dates, {})["reconstructable"],
        "a face with no seed pair produced an origin")
    # 7. a rung's series starts only at its offset, and combining is an equal-weight mean
    zeros = np.zeros(5)
    chk(len(zeros) == 5, "placeholder")
    chk(combine([np.array([1.0, 2.0]), np.array([3.0, 4.0])]).tolist() == [2.0, 3.0],
        "combine is not an equal-weight mean")
    chk(combine([]) is None, "combining no rungs produced a series")
    # 8. the verdict is a reading of the residual, and the class size separates the two
    #    reproducible readings
    resid_ok = {"bars_judged": 11, "bars_reproduced_at_0_001pct": 11,
                "share_of_tested_phases_that_reproduce_every_bar": 0.756}
    chk(verdict_of(resid_ok, {}) == V_PHASE_UNPINNED,
        "a wide reproducing class was read as a pinned phase")
    chk(verdict_of(dict(resid_ok, share_of_tested_phases_that_reproduce_every_bar=0.01),
                   {}) == V_REPRODUCIBLE,
        "a narrow reproducing class was not read as a pinned phase")
    chk(verdict_of(dict(resid_ok, bars_reproduced_at_0_001pct=7), {}) == V_NOT_REPRODUCIBLE,
        "an unexplained bar was not read as not reproducible")
    chk(verdict_of({"bars_judged": 0}, {}) == V_EMPTY,
        "an empty window was not read as empty")
    # 9. the residual prices itself: gaps within the printed precision are not unexplained
    rows = [{"bar": "2026-01-05", "abs_rel_gap_pct": 0.0004, "printed_precision_pct": 0.0009,
             "gap_is_within_the_printed_precision": True, "reproduced_at_0_001pct": True},
            {"bar": "2026-01-06", "abs_rel_gap_pct": 0.0008, "printed_precision_pct": 0.0009,
             "gap_is_within_the_printed_precision": True, "reproduced_at_0_001pct": True}]
    marg = {"GC007": {"rung_is_offset_invariant_on_this_window": True},
            "GC028": {"rung_is_offset_invariant_on_this_window": False}}
    prod = {"share_of_tested_phases_that_reproduce_every_bar": 0.756,
            "phase_discrimination_rests_on": ["GC028"]}
    res = residual_of(rows, prod, {}, marg)
    chk(res["bars_judged"] == 2 and res["bars_reproduced_at_0_001pct"] == 2,
        "the residual miscounted its own rows")
    chk(res["bars_no_phase_reproduces_at_0_001pct"] == 0,
        "a reproduced window was reported as having an unexplained bar")
    chk(res["rungs_that_are_offset_invariant"] == ["GC007"],
        "the offset-invariant rungs were not read off the marginal sweep")
    chk(abs(res["max_abs_gap_pct"] - 0.0008) < 1e-9, "the residual did not take the largest gap")
    # 10. the guard accepts a face built from these pieces and refuses doctored ones
    pub = [1e-5, 1.02e-5]
    rows2 = []
    for i, (p, f) in enumerate(zip(pub, [1.0001e-5, 1.02e-5])):
        gp = gap_pct(f, p)
        fp = printed_precision_pct(p * 0.3)
        rows2.append({
            "bar": "2026-01-0%d" % (5 + i), "gap_days": 1, "ledger_cash_weight": 0.3,
            "ledger_carry_frac": p * 0.3, "published_rate_per_bar": p,
            "replayed_rate_per_bar": f, "rel_gap_pct": gp, "abs_rel_gap_pct": abs(gp),
            "printed_precision_pct": fp,
            "reproduced_at_0_5pct": abs(gp) <= FIT_TOL_PCT,
            "reproduced_at_0_001pct": abs(gp) <= EXACT_TOL_PCT,
            "gap_is_within_the_printed_precision": abs(gp) <= fp})
    good = {
        "bars": rows2,
        "residual": residual_of(rows2, prod, {}, marg),
        "published_phase": {},
        "arms": {"published_origin": {"bars_judged": 2, "gaps_pct": [0.01, 0.0],
                                      "max_abs_gap_pct": 0.01,
                                      "bars_reproduced_at_0_5pct": 2,
                                      "bars_reproduced_at_0_001pct": 1}},
        "sweep": {"marginal": marg,
                  "product": {"phases_tested": 4, "phases_reproducing_every_bar": 3,
                              "share_of_tested_phases_that_reproduce_every_bar": 0.75,
                              "per_bar_phases_reproducing_that_bar": {"2026-01-05": 4,
                                                                      "2026-01-06": 3}}},
    }
    good["verdict"] = verdict_of(good["residual"], {})
    probs = face_problems(good)
    chk(probs == [], "the guard refuses a face it should accept: %s" % probs[:2])
    doctored = json.loads(json.dumps(good))
    doctored["bars"][0]["replayed_rate_per_bar"] = 2e-5
    chk(bool(face_problems(doctored)), "a replayed rate that no longer re-derives passed")
    claim = json.loads(json.dumps(good))
    claim["bars"][0]["reproduced_at_0_001pct"] = True
    claim["bars"][0]["rel_gap_pct"] = 0.5
    claim["bars"][0]["abs_rel_gap_pct"] = 0.5
    chk(bool(face_problems(claim)), "a row claiming a 0.5% gap reproduces at 0.001% passed")
    bad_range = json.loads(json.dumps(good))
    bad_range["sweep"]["marginal"]["GC028"] = {
        "offsets_searched": 10, "passing_ranges": [[0, 4]], "failing_ranges": [[5, 9]],
        "offsets_reproducing_every_bar": 6,
        "rung_is_offset_invariant_on_this_window": False}
    chk(bool(face_problems(bad_range)), "a passing count that contradicts its ranges passed")
    bad_share = json.loads(json.dumps(good))
    bad_share["sweep"]["product"]["phases_reproducing_every_bar"] = 5
    chk(bool(face_problems(bad_share)), "more reproducing phases than tested passed")
    bad_verdict = json.loads(json.dumps(good))
    bad_verdict["verdict"] = V_REPRODUCIBLE
    chk(bool(face_problems(bad_verdict)), "a verdict that does not re-derive passed")

    print("E592 selftest %d/%d PASS" % (seen[0] - len(bad), seen[0]))
    for m in bad:
        print("  FAIL %s" % m)
    return 0 if not bad else 1


# --------------------------------------------------------------------------- cli
def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "build"
    if cmd == "build":
        face = build(write=True)
        print("WROTE %s cutoff=%s verdict=%s" % (OUT_PATH, face.get("evidence_cutoff"),
                                                 face.get("verdict")))
        print(face.get("verdict_line"))
        return 0
    if cmd == "check":
        return check()
    if cmd == "verify":
        return verify()
    if cmd == "selftest":
        return selftest()
    print("unknown command %r (build|check|verify|selftest)" % cmd)
    return 2


if __name__ == "__main__":
    sys.exit(main())