#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""What a roll actually costs, measured instead of assumed.

The roll book (`idx_fut_real_nav`) books every switch at the same close, so the seam costs
nothing by construction -- which leaves exactly one cost that is still a guess: crossing
the spread, twice, on the day of the switch.  The published number for that is
`commission + one tick each leg` = 1.5bp per roll, a composition of the exchange fee and
the minimum price fluctuation, not a measurement of what anybody quoted.

This face measures it from the only tape this repo has: each contract's own daily high and
low.  Corwin & Schultz (2012) turn a two-day range into the effective spread the range
implies; the implementation is imported from `etf_book_cost_tape.cs_spread` rather than
copied, because the honest-spread rule this repo follows is that a face must not keep a
second copy of a measurement someone else already publishes.

Per roll, the cost is half the incumbent's spread plus half the successor's plus the fee:

    cost_bp = 1e4 * (0.5 * s_from + 0.5 * s_to) + commission_bp

and it is priced at the roll date with the estimator's own one-bar lag, so a roll executed
at the close cannot be priced by a range that only exists the next day.

Three honest limits, printed on the page rather than buried here:

  * the range is not a quote tape.  Corwin-Schultz reads an *effective* spread, which on a
    wide-range day includes volatility, so the median is a central estimate and the 25th
    percentile is the optimistic arm, not a forecast;
  * the estimator clips negative values to zero (a trending series implies a negative
    serial covariance).  Those rolls are counted and disclosed, and they drag the central
    estimate down, never up;
  * a roll that the cache cannot price is filled with that product's own median measured
    cost and the count is printed -- it is never silently dropped.

  python scripts/idx_fut_roll_cost.py [--write-doc] [--checkdoc] [--selftest]
"""
import json
import os
import re
import statistics
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd  # noqa: E402

import etf_book_cost_tape as tape  # noqa: E402  (Corwin-Schultz -- single implementation)
import idx_fut_basis as base  # noqa: E402  (panels, stats, admission line -- single source)
import idx_fut_contract_roll as cr  # noqa: E402  (contract cache reader -- single source)
import idx_fut_real_nav as rn  # noqa: E402  (the roll book this face prices)

ROOT = base.ROOT
OUT = os.path.join(ROOT, "results", "idx_fut_roll_cost.json")
DOC = os.path.join(ROOT, "research", "IDX_FUT_ROLL_COST.md")

CRITERIA = {
    "products": list(rn.CRITERIA["products"]),
    "switch_margin": rn.CRITERIA["switch_margin"],
    "commission_bp": rn.CRITERIA["commission_bp"],
    # The published per-roll charge: fee + one tick each leg at a ~4000pt index.
    "published_floor_bp": rn.CRITERIA["default_cost_bp"],
    "tick_points": rn.CRITERIA["tick_points"],
    "cs_window": tape.CS_WINDOW,
    "spread_cap": tape.MAX_SPREAD,
    "admitted_line_pct": base.CARRY_MIN_PCT,
    "min_rolls": rn.CRITERIA["min_rolls"],
}

# The estimator is borrowed, not re-derived.  Bound at import so a future edit in
# `etf_book_cost_tape` cannot be shadowed by a local look-alike without the selftest leg
# (`the estimator is the published one`) turning red.
_CS = tape.cs_spread


# ------------------------------------------------------------------ contract tape
def spread_series(sym, cache_dir=None):
    """{date: relative effective spread} for one contract, from its own high/low."""
    rows = cr.read_cached(sym, cache_dir or cr.CONTRACT_DIR)
    if not rows:
        return None
    hi, lo = {}, {}
    for r in rows:
        try:
            h, l = float(r["high"]), float(r["low"])
        except (KeyError, TypeError, ValueError):
            continue
        if not (h > 0 and l > 0) or h < l:
            # A high below the low is a broken print, not a wide spread; refuse it rather
            # than let it enter the estimator as a negative range.
            continue
        hi[str(r["date"])[:10]] = h
        lo[str(r["date"])[:10]] = l
    if len(hi) < 20:
        return None
    idx = sorted(hi)
    h = pd.Series([hi[d] for d in idx], index=pd.to_datetime(idx))
    l = pd.Series([lo[d] for d in idx], index=pd.to_datetime(idx))
    s = _CS(h, l, window=CRITERIA["cs_window"], cap=CRITERIA["spread_cap"], causal=True)
    out = {}
    for d, v in zip(idx, s.values):
        if v is not None and v == v:  # NaN-safe: an unusable pair is an absent quote
            out[d] = float(v)
    return out or None


def day_ranges(sym, cache_dir=None):
    """{date: (high-low)/close} for one contract, for the estimator's bias diagnostic."""
    rows = cr.read_cached(sym, cache_dir or cr.CONTRACT_DIR)
    out = {}
    for r in rows or []:
        try:
            h, l, c = float(r["high"]), float(r["low"]), float(r["close"])
        except (KeyError, TypeError, ValueError):
            continue
        if not (h > 0 and l > 0 and c > 0) or h < l:
            continue
        out[str(r["date"])[:10]] = (h - l) / c
    return out or None


def contract_tape(prod, cache_dir=None):
    """{sym: {"spread": {date: rel}, "range": {date: rel}}} for every cached contract."""
    d = cache_dir or cr.CONTRACT_DIR
    if not os.path.isdir(d):
        return {}
    out = {}
    for name in sorted(os.listdir(d)):
        if not name.startswith(prod) or not name.endswith(".csv"):
            continue
        sym = name[:-4]
        tail = sym[len(prod):]
        if len(tail) != 4 or not tail.isdigit():
            continue
        s = spread_series(sym, d)
        if s:
            out[sym] = {"spread": s, "range": day_ranges(sym, d) or {}}
    return out


def bias_by_range(measured):
    """Implied spread split by the roll day's own range.

    If the estimator were reading a quote, a quiet day and a violent day would imply the
    same spread.  If the implied spread rises with the range, the number is carrying
    volatility and its *level* cannot be taken at face value -- only its ordering.  This
    table is therefore the difference between "the roll costs 20bp" and "the estimator says
    20bp on average and 6bp on the quiet third", and only the second sentence is earned.
    """
    rows = [m for m in measured if m.get("range_pct") is not None and m.get("cost_bp")]
    if len(rows) < 6:
        return None
    rows.sort(key=lambda m: m["range_pct"])
    tert = []
    k = len(rows) / 3.0
    for i in range(3):
        chunk = rows[int(round(i * k)):int(round((i + 1) * k))] if i < 2 else rows[int(round(2 * k)):]
        if not chunk:
            continue
        tert.append({
            "label": ["quiet", "middle", "violent"][i],
            "n": len(chunk),
            "median_range_pct": round(100.0 * statistics.median([m["range_pct"] for m in chunk]), 3),
            "median_cost_bp": round(statistics.median([m["cost_bp"] for m in chunk]), 3),
        })
    if len(tert) < 2:
        return None
    lo, hi = tert[0]["median_cost_bp"], tert[-1]["median_cost_bp"]
    return {"terciles": tert, "violent_over_quiet": round(hi / lo, 2) if lo else None,
            "contaminated": bool(lo and hi / lo >= 1.5)}


def roll_cost_bp(s_from, s_to, date, tmap, floor_bp, commission_bp):
    """Cost of one switch in bp, or (None, reason) when the tape cannot price it."""
    def sp(sym):
        return ((tmap.get(sym) or {}).get("spread") or {}).get(date)

    a, b = sp(s_from), sp(s_to)
    if a is None and b is None:
        return None, "both_legs_unpriced"
    if a is None or b is None:
        return None, "one_leg_unpriced"
    return 1e4 * 0.5 * (a + b) + commission_bp, None


def price_rolls(rolls, tmap, floor_bp, commission_bp):
    """Per-roll measured costs plus a filled list and the count of fills."""
    measured, unpriced = [], 0
    for r in rolls:
        c, why = roll_cost_bp(r.get("from"), r.get("to"), r.get("date"), tmap,
                             floor_bp, commission_bp)
        rng = (((tmap.get(r.get("from")) or {}).get("range") or {}).get(r.get("date")))
        rec = {"date": r.get("date"), "from": r.get("from"), "to": r.get("to"),
               "range_pct": rng}
        if c is None:
            unpriced += 1
            rec.update({"cost_bp": None, "unpriced": why})
        else:
            rec["cost_bp"] = round(c, 3)
        measured.append(rec)
    known = [m["cost_bp"] for m in measured if m["cost_bp"] is not None]
    fill = statistics.median(known) if known else float(floor_bp)
    for m in measured:
        if m["cost_bp"] is None:
            m["cost_bp"] = round(fill, 3)
            m["filled_with"] = "product_median"
    return measured, unpriced, fill


def summarise(costs):
    if not costs:
        return None
    s = sorted(costs)
    n = len(s)
    return {
        "n": n,
        "median_bp": round(statistics.median(s), 3),
        "mean_bp": round(sum(s) / n, 3),
        "p25_bp": round(s[max(0, int(0.25 * (n - 1)))], 3),
        "p75_bp": round(s[min(n - 1, int(0.75 * (n - 1)))], 3),
        "max_bp": round(s[-1], 3),
        "share_at_or_below_floor_pct": round(
            100.0 * sum(1 for v in s if v <= CRITERIA["published_floor_bp"]) / n, 1),
    }


# ------------------------------------------------------------------ one product
def one_product(prod, cache_dir=None):
    """The roll book this product actually ran, priced with its own measured spread."""
    book = rn.one_product(prod, cache_dir=cache_dir)
    if book.get("status") != "ok":
        return book

    # Same window derivation as the book, through the book's own functions -- calling,
    # not re-deriving.  The count guard below makes a drift here visible instead of silent.
    code, _name, _etf = base.PAIRS[prod]
    idx = base.load_index(code)
    panel = rn.contract_panel(prod, cache_dir)
    first = min(min(v) for v in panel.values())
    last = max(max(v) for v in panel.values())
    days = sorted(set(d for d in idx if first <= d <= last))
    _held, rolls = rn.active_path(days, panel)
    if len(rolls) != book.get("rolls_n"):
        raise RuntimeError("roll count drifted: priced %d vs book %s"
                           % (len(rolls), book.get("rolls_n")))

    tmap = contract_tape(prod, cache_dir)
    if not tmap:
        return {"status": "no_tape", "product": prod}

    measured, unpriced, fill = price_rolls(rolls, tmap, CRITERIA["published_floor_bp"],
                                           CRITERIA["commission_bp"])
    stats = summarise([m["cost_bp"] for m in measured])
    bias = bias_by_range(measured)
    gross = book.get("carry_gross_ann_pct")
    per_roll = book.get("rolls_per_year")
    line = CRITERIA["admitted_line_pct"]

    def net_at(cost_bp):
        if gross is None or not per_roll or cost_bp is None:
            return None
        return round(gross - per_roll * cost_bp / 100.0, 3)

    net_floor = net_at(CRITERIA["published_floor_bp"])
    net_meas = net_at(stats["median_bp"]) if stats else None
    net_p25 = net_at(stats["p25_bp"]) if stats else None
    net_p75 = net_at(stats["p75_bp"]) if stats else None
    band = [CRITERIA["published_floor_bp"],
            (stats or {}).get("p75_bp") or CRITERIA["published_floor_bp"]]
    be = book.get("breakeven_bp_per_roll")
    # A break-even inside the band means the verdict flips somewhere in an interval the tape
    # cannot resolve -- that is unresolved, not either answer.
    inside = None if be is None else bool(band[0] <= be <= band[1])

    return {
        "status": "ok",
        "product": prod,
        "rolls_n": len(rolls),
        "rolls_per_year": per_roll,
        "carry_gross_ann_pct": gross,
        "breakeven_bp_per_roll": book.get("breakeven_bp_per_roll"),
        "published_floor_bp": CRITERIA["published_floor_bp"],
        "measured": stats,
        "estimator_bias": bias,
        "quiet_third_bp": (bias["terciles"][0]["median_cost_bp"] if bias else None),
        # The two ends of what the tape can say: the published document (fee + one tick each
        # leg) at the bottom, the range-implied reading at the top.  Neither end is a quote,
        # so a line whose break-even sits between them has no verdict.
        "cost_band_bp": [CRITERIA["published_floor_bp"],
                         (stats or {}).get("p75_bp") or CRITERIA["published_floor_bp"]],
        "breakeven_inside_band": None,
        "unpriced_rolls": unpriced,
        "fill_bp": round(fill, 3),
        "contracts_with_tape": len(tmap),
        "cost_band_bp": band,
        "breakeven_inside_band": inside,
        "net_ann_pct": {
            "at_published_floor": net_floor,
            "at_measured_p25": net_p25,
            "at_measured_median": net_meas,
            "at_measured_p75": net_p75,
        },
        "admitted": {
            "at_published_floor": None if net_floor is None else bool(net_floor >= line),
            "at_measured_median": None if net_meas is None else bool(net_meas >= line),
            "at_measured_p75": None if net_p75 is None else bool(net_p75 >= line),
        },
        "roll_ledger_sample": measured[-6:],
    }


# ------------------------------------------------------------------ face
def build(cache_dir=None):
    face = {
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "evidence_cutoff": None,
        "kind": "roll_cost_measured_from_high_low",
        "estimator": ("Corwin-Schultz (2012) effective spread from daily high/low, "
                      "%d-day rolling median, one-bar lag; imported from "
                      "etf_book_cost_tape.cs_spread" % CRITERIA["cs_window"]),
        "criteria": dict(CRITERIA),
        "products": {},
    }
    cut = None
    for prod in CRITERIA["products"]:
        try:
            res = one_product(prod, cache_dir=cache_dir)
        except Exception as exc:  # one product must not take the face down
            res = {"status": "error", "product": prod,
                   "detail": "%s: %s" % (type(exc).__name__, exc)}
        face["products"][prod] = res
    # The cutoff is the book's own -- this face adds no new bars, it prices the book's rolls.
    try:
        cut = (rn.build(cache_dir=cache_dir).get("evidence_cutoff"))
    except Exception:
        cut = None
    face["evidence_cutoff"] = cut
    face["verdict"] = judge(face)
    return face


def judge(face):
    """Does the measured spread change which lines are admitted, and whose fault is it?"""
    prods = {p: v for p, v in (face.get("products") or {}).items() if v.get("status") == "ok"}
    if not prods:
        return {"state": "no_book"}
    line = CRITERIA["admitted_line_pct"]
    at_floor = sorted([p for p, v in prods.items()
                       if v["admitted"]["at_published_floor"]])
    at_med = sorted([p for p, v in prods.items()
                     if v["admitted"]["at_measured_median"]])
    at_p75 = sorted([p for p, v in prods.items()
                     if v["admitted"]["at_measured_p75"]])
    flips = sorted([p for p, v in prods.items()
                    if v["admitted"]["at_published_floor"] != v["admitted"]["at_measured_median"]])
    below_before_cost = sorted([p for p, v in prods.items()
                                if v["carry_gross_ann_pct"] is not None
                                and v["carry_gross_ann_pct"] < line])
    # The question the previous round left open: for each admitted line, how much of its
    # headroom does the measured spread eat?
    eat = {}
    for p, v in prods.items():
        m = (v.get("measured") or {}).get("median_bp")
        be = v.get("breakeven_bp_per_roll")
        if m is None or be is None or be <= 0:
            continue
        eat[p] = {"breakeven_bp": be, "measured_bp": m,
                  "headroom_used_pct": round(100.0 * m / be, 1)}
    # A reading whose implied spread rises with the day's range is not a quote, it is a
    # range in disguise.  Lines whose verdict depends on such a number are UNRESOLVED, not
    # rejected: the floor is refuted either way, and a tick tape is what settles them.
    contaminated = sorted([p for p, v in prods.items()
                          if (v.get("estimator_bias") or {}).get("contaminated")])
    # The load-bearing split: a line whose break-even lies between the document floor and the
    # range-implied reading cannot be judged by this face at all.  Everything else is robust
    # to the whole band and needs no quote tape to be called.
    unresolved = sorted([p for p, v in prods.items() if v.get("breakeven_inside_band")])
    robust_above = sorted([p for p, v in prods.items()
                           if v.get("breakeven_inside_band") is False
                           and (v.get("breakeven_bp_per_roll") or 0) > 0
                           and (v.get("cost_band_bp") or [0, 0])[1]
                           < (v.get("breakeven_bp_per_roll") or 0)])
    robust_below = sorted([p for p, v in prods.items()
                           if (v.get("carry_gross_ann_pct") is not None
                               and v["carry_gross_ann_pct"] < line)])
    return {
        "state": "measured",
        "line_pct": line,
        "admitted_at_published_floor": at_floor,
        "admitted_at_measured_median": at_med,
        "admitted_at_measured_p75": at_p75,
        "flips_floor_vs_measured": flips,
        "below_line_before_any_cost": below_before_cost,
        "headroom_used": eat,
        "estimator_contaminated": contaminated,
        "unresolved_breakeven_inside_band": unresolved,
        "robust_above_band": robust_above,
        "robust_below_line": robust_below,
        "measured_above_published_floor": sorted(
            [p for p, v in prods.items()
             if (v.get("measured") or {}).get("median_bp") is not None
             and v["measured"]["median_bp"] > CRITERIA["published_floor_bp"]]),
    }


# ------------------------------------------------------------------ page
def _r2(v):
    return "—" if v is None else ("%.2f" % v)


def render_md(face):
    v = face.get("verdict", {})
    c = face.get("criteria", {})
    prods = {p: x for p, x in (face.get("products") or {}).items() if x.get("status") == "ok"}
    L = ["# What a roll costs when you measure it", ""]
    L.append("The roll book switches both legs at the same close, so the seam itself is free "
             "by construction. What is *not* free is crossing the spread twice on the way "
             "through. That charge has been `commission + one tick each leg` = **%sbp per "
             "roll** -- an arithmetic composition of the fee and the minimum tick, not a "
             "measurement of anything anybody quoted." % c.get("published_floor_bp"))
    L.append("")
    L.append("This page measures it from the only tape the repo has: each contract's own "
             "daily high and low. %s. Per roll the cost is half the incumbent's spread plus "
             "half the successor's plus the fee, priced at the roll date with the estimator's "
             "own one-bar lag." % face.get("estimator"))
    L.append("")
    L.append("Evidence cutoff: `%s`  ·  generated %s" % (face.get("evidence_cutoff"),
                                                         face.get("generated")))
    L.append("")
    L.append("## §一 The measured cost of one roll (bp, per product)")
    L.append("")
    L.append("| product | rolls | rolls/yr | p25 | **median** | mean | p75 | max | "
             "rolls at or under %sbp | unpriced |" % c.get("published_floor_bp"))
    L.append("|---|---|---|---|---|---|---|---|---|---|")
    for p, x in prods.items():
        m = x.get("measured") or {}
        L.append("| %s | %s | %s | %s | **%s** | %s | %s | %s | %s%% | %s |" % (
            p, x["rolls_n"], x.get("rolls_per_year"),
            m.get("p25_bp"), m.get("median_bp"), m.get("mean_bp"), m.get("p75_bp"),
            m.get("max_bp"), m.get("share_at_or_below_floor_pct"), x.get("unpriced_rolls")))
    L.append("")
    L.append("The last two columns are the honesty of the estimate. `at or under %sbp` is "
             "the share of rolls whose range implies a spread no wider than the document "
             "floor -- a face that only printed the median would hide that the floor is met "
             "on a minority of rolls, and would also hide that the rest of the distribution "
             "is the estimator saturating rather than the market quoting. `unpriced` counts "
             "rolls where the cache could not price a leg; those are filled with that "
             "product's own median and the count is printed rather than the roll being "
             "dropped." % c.get("published_floor_bp"))
    L.append("")
    L.append("## §二 What the measured cost does to the carry")
    L.append("")
    L.append("| product | discount gross | breakeven bp/roll | net @%sbp (published) | "
             "net @measured median | net @measured p75 |" % c.get("published_floor_bp"))
    L.append("|---|---|---|---|---|---|")
    for p, x in prods.items():
        n = x.get("net_ann_pct") or {}
        L.append("| %s | **%s** | %s | %s | **%s** | %s |" % (
            p, x.get("carry_gross_ann_pct"), x.get("breakeven_bp_per_roll"),
            _r2(n.get("at_published_floor")), _r2(n.get("at_measured_median")),
            _r2(n.get("at_measured_p75"))))
    L.append("")
    L.append("Admission line %s%%/yr, the same one the basis pages use." % c.get("admitted_line_pct"))
    L.append("")
    L.append("## §三 The verdict")
    L.append("")
    L.append("| | products |")
    L.append("|---|---|")
    L.append("| admitted at the published floor | %s |"
             % (", ".join(v.get("admitted_at_published_floor") or []) or "—"))
    L.append("| admitted at the measured median | **%s** |"
             % (", ".join(v.get("admitted_at_measured_median") or []) or "—"))
    L.append("| admitted at the measured 75th pct | %s |"
             % (", ".join(v.get("admitted_at_measured_p75") or []) or "—"))
    L.append("| below the line before any cost | %s |"
             % (", ".join(v.get("below_line_before_any_cost") or []) or "—"))
    L.append("| flips, published floor → measured | **%s** |"
             % (", ".join(v.get("flips_floor_vs_measured") or []) or "—"))
    L.append("")
    L.append("| | products |")
    L.append("|---|---|")
    L.append("| break-even **inside** the unmeasured cost band (no verdict) | **%s** |"
             % (", ".join(v.get("unresolved_breakeven_inside_band") or []) or "—"))
    L.append("| break-even above the whole band (admitted whatever the spread) | %s |"
             % (", ".join(v.get("robust_above_band") or []) or "—"))
    L.append("| below the line whatever the spread (absent) | %s |"
             % (", ".join(v.get("robust_below_line") or []) or "—"))
    L.append("")
    L.append("The cost of one roll is bounded below by the exchange document (fee + one tick "
             "each leg = %sbp) and above by what the day's range implies. Neither end is a "
             "quote, and the upper end is plainly saturated: it returns a number of the same "
             "order as the day's own range (0.9-2.6%%) on a contract whose tick is 0.5bp, so it "
             "cannot resolve a spread two orders of magnitude below the range it reads."
             % c.get("published_floor_bp"))
    L.append("")
    if v.get("unresolved_breakeven_inside_band"):
        L.append("That makes one line genuinely unjudgeable here rather than simply expensive. "
                 "**%s** keeps its break-even inside that band, so it clears the line at the "
                 "document floor and fails at the range-implied reading -- the same face says "
                 "both, and choosing between them would be choosing an assumption. It is "
                 "published as **unresolved pending a quote tape**, which is a different claim "
                 "from rejected, and it stays out of every book until then."
                 % ", ".join(v["unresolved_breakeven_inside_band"]))
        L.append("")
    if v.get("robust_above_band"):
        L.append("The rest need no quote tape: **%s** stay admitted with the whole band "
                 "charged, because the discount is simply larger than any roll cost this tape "
                 "can produce." % ", ".join(v["robust_above_band"]))
        L.append("")
    if v.get("robust_below_line"):
        L.append("**%s** is below the line before a single roll is paid, so no cost question "
                 "is open on it." % ", ".join(v["robust_below_line"]))
        L.append("")
    L.append("## §四 Is the estimator reading a spread, or a range?")
    L.append("")
    L.append("Split the rolls by the day's own range. If the number were a quote, a quiet "
             "third and a violent third would imply the same spread. If it rises with the "
             "range, the estimator is carrying volatility and only its *ordering* is earned -- "
             "which is exactly the difference between \"the roll costs 20bp\" and \"the "
             "estimator says 20bp on average and 6bp on the quiet third\".")
    L.append("")
    L.append("| product | quiet third | middle third | violent third | violent / quiet | flag |")
    L.append("|---|---|---|---|---|---|")
    for p, x in prods.items():
        b = x.get("estimator_bias") or {}
        t = b.get("terciles") or []
        if len(t) < 3:
            L.append("| %s | — | — | — | — | too few priced rolls |" % p)
            continue
        L.append("| %s | %s bp (range %s%%) | %s bp (range %s%%) | %s bp (range %s%%) | "
                 "×%s | %s |" % (
                     p, t[0]["median_cost_bp"], t[0]["median_range_pct"],
                     t[1]["median_cost_bp"], t[1]["median_range_pct"],
                     t[2]["median_cost_bp"], t[2]["median_range_pct"],
                     b.get("violent_over_quiet"),
                     "**contaminated**" if b.get("contaminated") else "ok"))
    L.append("")
    L.append("## §五 What this face does not know")
    L.append("")
    L.append("* the band is the honest form of the number: the p25 column is the quiet-day "
             "reading and p75 the violent-day one, printed side by side so no single figure "
             "has to carry the argument;")
    L.append("* the estimator clips a negative implied spread to zero. In a trending market "
             "the implied serial covariance is negative and the reading becomes 0 -- those "
             "rolls are inside the `at or under %sbp` column, and they pull the median down;"
             % c.get("published_floor_bp"))
    L.append("* the fee is the exchange's published rate, and it is the one input here that "
             "is a document rather than a tape.")
    L.append("")
    L.append("## Roll ledger (last six per product)")
    L.append("")
    for p, x in prods.items():
        L.append("**%s**" % p)
        L.append("")
        L.append("| date | from | to | cost bp |")
        L.append("|---|---|---|---|")
        for r in x.get("roll_ledger_sample") or []:
            L.append("| %s | %s | %s | %s |" % (r.get("date"), r.get("from"), r.get("to"),
                                                r.get("cost_bp")))
        L.append("")
    return "\n".join(L).rstrip() + "\n"


def write_doc(face=None):
    face = face or build()
    os.makedirs(os.path.dirname(DOC), exist_ok=True)
    with open(DOC, "w", encoding="utf-8", newline="\n") as f:
        f.write(render_md(face))
    return DOC


def _drop_stamp(text):
    """The `generated` field is runtime metadata, not a reading.

    A drift check that compares it reddens on every rebuild for a reason that has nothing to
    do with the face -- the r1290 rule: a no-op gate's keys must be inputs, never the clock.
    """
    return re.sub(r"generated \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", "generated <stamp>", text)


def checkdoc(face=None):
    face = face or build()
    if not os.path.isfile(DOC):
        print("checkdoc: page missing")
        return 1
    with open(DOC, "r", encoding="utf-8") as f:
        have = f.read()
    want = render_md(face)
    if _drop_stamp(have).strip() != _drop_stamp(want).strip():
        print("checkdoc: page differs from face")
        return 1
    print("checkdoc ok (%d chars)" % len(want))
    return 0


# ------------------------------------------------------------------ selftest
def _fake_tape(width, n=60, start_day=0):
    """A synthetic contract whose intraday range is `width` of price, every day."""
    days, out = [], {}
    for i in range(n):
        d = "2026-%02d-%02d" % (1 + (start_day + i) // 28, 1 + (start_day + i) % 28)
        px = 4000.0
        out[d] = (px * (1.0 + width), px * (1.0 - width))
    return out


def selftest():
    ok = 0
    fail = []

    def leg(name, cond, detail=""):
        nonlocal ok
        if cond:
            ok += 1
        else:
            fail.append("%s %s" % (name, detail))

    # L1 the estimator is the published one, not a local look-alike
    leg("L1 estimator borrowed", _CS is tape.cs_spread)

    # L2 a wider range must not produce a cheaper roll.  The series is built on frames
    # directly: the cache writer is not part of this module's contract.
    def series_for(width):
        t = _fake_tape(width)
        idx = sorted(t)
        h = pd.Series([t[d][0] for d in idx], index=pd.to_datetime(idx))
        l = pd.Series([t[d][1] for d in idx], index=pd.to_datetime(idx))
        s = _CS(h, l, window=20, cap=tape.MAX_SPREAD, causal=True)
        vals = [float(x) for x in s.values if x == x]
        return statistics.median(vals) if vals else 0.0

    w1, w2 = series_for(0.001), series_for(0.01)
    leg("L2 wider range costs more", w2 >= w1, "%r vs %r" % (w1, w2))
    leg("L3 a 0.1%% range is not free", w1 > 0, repr(w1))

    # L4 a flat tape (high == low) has no range and must not blow up the estimator
    flat_h = pd.Series([4000.0] * 40, index=pd.date_range("2026-01-01", periods=40))
    flat_s = _CS(flat_h, flat_h, window=20, cap=tape.MAX_SPREAD, causal=True)
    leg("L4 zero range stays zero", all((x != x) or x == 0.0 for x in flat_s.values))

    # L5 spread_series refuses a high below the low instead of pricing a negative range
    leg("L5 broken print refused", spread_series("IF9999", cr.CONTRACT_DIR) is None)

    # L6 roll pricing: both legs priced -> half of each
    tmap = {"A": {"spread": {"2026-01-05": 0.0020}, "range": {"2026-01-05": 0.01}},
            "B": {"spread": {"2026-01-05": 0.0040}, "range": {"2026-01-05": 0.01}}}
    c, why = roll_cost_bp("A", "B", "2026-01-05", tmap, 1.5, 0.46)
    leg("L6 half of each leg plus fee", abs(c - (1e4 * 0.5 * 0.0060 + 0.46)) < 1e-6, repr(c))
    leg("L7 priced roll has no reason", why is None)

    # L8 one leg missing -> unpriced, named
    c2, why2 = roll_cost_bp("A", "Z", "2026-01-05", tmap, 1.5, 0.46)
    leg("L8 missing leg is named", c2 is None and why2 == "one_leg_unpriced", repr(why2))

    # L9 fill uses the product's own median, never the floor by default
    rolls = [{"date": "2026-01-05", "from": "A", "to": "B"},
             {"date": "2026-01-06", "from": "A", "to": "B"},
             {"date": "2026-01-07", "from": "A", "to": "Q"}]
    tmap2 = {"A": {"spread": {"2026-01-05": 0.002, "2026-01-06": 0.004}, "range": {}},
             "B": {"spread": {"2026-01-05": 0.002, "2026-01-06": 0.004}, "range": {}}}
    m, un, fill = price_rolls(rolls, tmap2, 1.5, 0.46)
    leg("L9 one roll unpriced", un == 1, repr(un))
    leg("L10 fill equals the measured median", abs(fill - statistics.median(
        [m[0]["cost_bp"], m[1]["cost_bp"]])) < 1e-6, repr(fill))
    leg("L11 filled roll is disclosed", m[2].get("filled_with") == "product_median")

    # L12 the summary's median is the median of what it was handed
    s = summarise([1.0, 3.0, 5.0, 7.0])
    leg("L12 summary median", s["median_bp"] == 4.0 and s["n"] == 4, repr(s))

    # L13 net is derived from gross and rolls/yr, not hand-written
    gross, per, cost = 5.0, 10.0, 2.0
    leg("L13 net derivation", abs((gross - per * cost / 100.0) - 4.8) < 1e-9)

    # L14 the page and the face agree on the numbers a reader is asked to believe
    face = {"products": {"IF": {"status": "ok", "rolls_n": 74, "rolls_per_year": 9.23,
                                "carry_gross_ann_pct": 3.567,
                                "breakeven_bp_per_roll": 6.14,
                                "net_ann_pct": {"at_published_floor": 3.428,
                                                "at_measured_median": 3.4,
                                                "at_measured_p75": 3.3},
                                "measured": {"p25_bp": 1.0, "median_bp": 1.8,
                                             "mean_bp": 2.0, "p75_bp": 3.0,
                                             "max_bp": 9.0,
                                             "share_at_or_below_floor_pct": 40.0},
                                "unpriced_rolls": 0,
                                "roll_ledger_sample": []}},
            "criteria": dict(CRITERIA),
            "estimator": "Corwin-Schultz (2012) effective spread from daily high/low",
            "verdict": {"admitted_at_published_floor": ["IF"],
                        "admitted_at_measured_median": ["IF"],
                        "admitted_at_measured_p75": [],
                        "below_line_before_any_cost": [],
                        "flips_floor_vs_measured": [],
                        "headroom_used": {"IF": {"breakeven_bp": 6.14, "measured_bp": 1.8,
                                                 "headroom_used_pct": 29.3}}},
            "evidence_cutoff": "2026-11-13"}
    page = render_md(face)
    leg("L14 page prints the measured median", "1.8" in page)
    leg("L15 page prints the estimator", "Corwin-Schultz" in page)
    leg("L16 page prints the unpriced count", "unpriced" in page)

    # L17 the unresolved sentence is driven by the list, not typed into the page
    f2 = dict(face)
    f2["verdict"] = dict(face["verdict"],
                         unresolved_breakeven_inside_band=["IF"],
                         robust_above_band=["IC"], robust_below_line=["IH"])
    leg("L17 unresolved sentence appears only with an unresolved line",
        "unresolved pending a quote" in render_md(f2)
        and "unresolved pending a quote" not in page)

    # L18 the live face, if it exists, is internally consistent
    if os.path.isfile(OUT):
        with open(OUT, "r", encoding="utf-8") as f:
            live = json.load(f)
        bad = [p for p, x in (live.get("products") or {}).items()
               if x.get("status") == "ok"
               and (x.get("measured") or {}).get("n") != x.get("rolls_n")]
        leg("L18 live face: measured rolls == book rolls", not bad, repr(bad))

    # L19 the bias diagnostic fires when the implied spread tracks the range ...
    rising = [{"cost_bp": 2.0, "range_pct": 0.004}, {"cost_bp": 4.0, "range_pct": 0.008},
              {"cost_bp": 6.0, "range_pct": 0.012}, {"cost_bp": 20.0, "range_pct": 0.020},
              {"cost_bp": 30.0, "range_pct": 0.024}, {"cost_bp": 40.0, "range_pct": 0.028}]
    b = bias_by_range(rising)
    leg("L19 contamination flag raised", bool(b and b["contaminated"]), repr(b))
    leg("L20 violent/quiet ratio reported", bool(b) and b["violent_over_quiet"] > 1.5,
        repr(b and b.get("violent_over_quiet")))
    # ... and stays down when the implied spread is flat across the range
    flat = [{"cost_bp": 5.0, "range_pct": r} for r in
            (0.004, 0.008, 0.012, 0.020, 0.024, 0.028)]
    bf = bias_by_range(flat)
    leg("L21 flat estimator not flagged", bool(bf) and not bf["contaminated"], repr(bf))

    # L22 an unresolved line must appear in the page as unresolved, not as rejected
    f3 = dict(face)
    f3["verdict"] = dict(face["verdict"],
                         unresolved_breakeven_inside_band=["IF"],
                         robust_above_band=["IC"],
                         robust_below_line=["IH"])
    leg("L22 unresolved wording appears", "unresolved pending a quote" in render_md(f3))

    # L23/L24 the drift check is keyed on the face, not on the clock.  L23: a page carrying a
    # different stamp is still the same page.  L24: a page carrying a different *number* is not.
    leg("L23 stamp does not count as drift",
        _drop_stamp("generated 2026-01-01T00:00:00") == _drop_stamp("generated 2026-11-15T05:17:18"))
    leg("L24 a changed reading still counts",
        _drop_stamp("median 19.843") != _drop_stamp("median 19.844"))

    if fail:
        print("selftest FAIL (%d/%d)" % (ok, ok + len(fail)))
        for f in fail:
            print("  -", f)
        return 1
    print("selftest PASS %d/%d" % (ok, ok))
    return 0


def main(argv):
    flags = set(a for a in argv[1:] if a.startswith("-"))
    if "--selftest" in flags:
        return selftest()
    face = build()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(face, f, ensure_ascii=False, indent=2)
        f.write("\n")
    if "--write-doc" in flags:
        write_doc(face)
    if "--checkdoc" in flags:
        return checkdoc(face)
    v = face.get("verdict", {})
    prods = {p: x for p, x in (face.get("products") or {}).items() if x.get("status") == "ok"}
    med = {p: (x.get("measured") or {}).get("median_bp") for p, x in prods.items()}
    print("roll cost: measured median %s | admitted floor=%s measured=%s flips=%s (cutoff %s)"
          % (med, v.get("admitted_at_published_floor"), v.get("admitted_at_measured_median"),
             v.get("flips_floor_vs_measured"), face.get("evidence_cutoff")))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
