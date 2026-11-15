#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""what a carry sleeve is worth in risk units, and whether the desk's own book wants it

WHY THIS FILE EXISTS
--------------------
r1697/r1698 priced the basis-and-roll book in rupees of carry per year (IC 8.6%,
IM 10.1%, IF unresolved, IH out) and printed a hit rate.  A carry number without a
risk number cannot be sized: 8.6% a year on notional means one thing if the spread
never draws down 3% and another if it draws down 25%, and the desk's own adopted
book is published in exactly the units this face was missing -- CAGR, vol, Sharpe,
max drawdown, worst year.  So the two could not be compared at all, and the only
question that allocates money ("the next yuan: the ETF book or the carry sleeve?")
had no face.

WHAT IT MEASURES
----------------
For each index future (the same roll book as idx_fut_real_nav: hold whichever
contract has the most open interest, switch at the same close, no mask):
  * the daily spread series (held contract return minus its index return);
  * its own risk: annualised vol, Sharpe, max drawdown, longest underwater run,
    worst calendar year;
  * the same series scaled to the desk's 8% volatility target, so it can be read
    against the adopted book's numbers instead of next to them;
  * the margin identity: one contract ties up margin, and a real book also needs
    cash to survive its own drawdown, so return on the capital actually committed
    is carry/(margin + |maxdd|), not carry/margin;
  * the blend grid: (1-lam)*book + lam*carry, re-scaled to one risk level, with the
    correlation of the two sleeves printed beside it -- a sleeve that earns but
    moves with the book does not diversify the book.

HONEST BY CONSTRUCTION
----------------------
  * the roll book and its daily returns are imported from idx_fut_real_nav, and the
    ETF book from the same modules etf_book_year_gate uses; nothing is re-implemented
    and nothing is transcribed from another receipt;
  * a drawdown that has not healed at the last bar is printed as "still under water
    for N bars", never as 0 (r1230 family: a censored duration is not a fast recovery);
  * margin is an ASSUMPTION with three values printed, not a measured broker number;
  * every reading here is in-sample and the page says so: this face decides whether a
    sleeve is worth pricing forward, not whether it will earn.

self   python scripts/idx_fut_carry_risk.py selftest
run    python scripts/idx_fut_carry_risk.py run [--write-doc]
check  python scripts/idx_fut_carry_risk.py check [--checkdoc]
"""
from __future__ import annotations

import argparse
import json
import math
import os
import statistics
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import idx_fut_basis as base            # noqa: E402  (index panel, TRADING_DAYS, single source)
import idx_fut_real_nav as rn          # noqa: E402  (roll book + daily returns, single source)
import etf_share_conversion as SCA     # noqa: E402  (share conversions vs quote flips)

OUT = os.path.join(ROOT, "results", "idx_fut_carry_risk.json")
DOC = os.path.join(ROOT, "research", "IDX_FUT_CARRY_RISK.md")
YEAR_GATE = os.path.join(ROOT, "results", "etf_book_year_gate", "YEAR-GATE.json")
# The dividend control arm lives on the basis face (C3). This file reads that published
# reading instead of re-deriving it: one dividend number, one producer.
BASIS_JSON = os.path.join(ROOT, "results", "idx_fut_basis.json")
# The two published roll rulers (threshold vs calendar) and the split that prices them.
# Read by this face so its own carry column travels with the size of that caliber.
ROLL_GAP = os.path.join(ROOT, "results", "idx_fut_roll_gap.json")
# Below this spread the caliber choice does not move the reading; above it the headline
# rides a choice. A display threshold, not a decision line.
CALIBER_SPREAD_PP = 1.0

CRITERIA = {
    "products": ["IC", "IF", "IM", "IH"],
    # the desk's own risk target: the adopted book is published at 8%/yr vol (nobond_vt08)
    "vol_target_pct": 8.0,
    "max_leverage": 5.0,
    # CFFEX exchange minimum margin, printed as an assumption with three values because
    # a broker adds its own and this host cannot measure that surcharge.
    "margin_assumptions": {"10pct": 0.10, "12pct": 0.12, "15pct": 0.15},
    # blend grid on the adopted book's daily returns
    "blend_lambdas": [0.0, 0.1, 0.2, 0.3],
    "blend_risk_pct": 10.0,
    "corr_diversifies_below": 0.5,
    "improve_sharpe_min": 0.02,
    "underwater_top_n": 3,
}


# ------------------------------------------------------------------ risk of a series
def equity(daily):
    """Level series from daily simple returns (start 1.0)."""
    lvl, acc = [1.0], 1.0
    for r in daily:
        acc *= 1.0 + r
        lvl.append(acc)
    return lvl


def underwater(levels):
    """(longest completed underwater run, bars still underwater at the last point).

    A run that has not healed by the last bar is returned separately and never counted
    as a completed one: the reader has to see "still waiting" as its own word.
    """
    peak_i, start, worst, open_run = 0, None, 0, 0
    for i, v in enumerate(levels):
        if v >= levels[peak_i]:
            if start is not None:
                worst = max(worst, i - start)
                start = None
            peak_i = i
        else:
            if start is None:
                start = i
            open_run = i - peak_i
    return worst, (open_run if start is not None else 0)


def risk_stats(daily, dates=None):
    """Vol / Sharpe / drawdown / underwater / worst year of a daily return series."""
    if len(daily) < 2:
        return {"n": len(daily), "insufficient": True}
    mean = statistics.fmean(daily)
    sd = statistics.stdev(daily)
    ann_mean = mean * base.TRADING_DAYS * 100.0
    ann_vol = sd * math.sqrt(base.TRADING_DAYS) * 100.0
    lvl = equity(daily)
    mdd = base.max_drawdown_pct(lvl)
    done, still = underwater(lvl)
    out = {
        "n": len(daily),
        "ann_mean_pct": round(ann_mean, 3),
        "ann_vol_pct": round(ann_vol, 3),
        "sharpe": round(ann_mean / ann_vol, 3) if ann_vol > 0 else None,
        "mdd_pct": round(mdd, 3),
        "underwater_max_bars": done,
        "underwater_open_bars": still,
        "hit_rate_pct": round(100.0 * sum(1 for v in daily if v > 0) / len(daily), 1),
        "ann_compound_pct": round(base.compound_pct(daily), 3),
    }
    if dates is not None and len(dates) == len(daily) + 1:
        out["by_year"] = year_returns(dates, daily)
        ys = out["by_year"]
        full = [v["compound_pct"] for v in ys.values()]
        out["worst_year_pct"] = round(min(full), 3) if full else None
        out["worst_year"] = min(ys, key=lambda y: ys[y]["compound_pct"]) if ys else None
    return out


def year_returns(dates, daily):
    """Compounded return per calendar year, with the bar count that produced it."""
    buckets = {}
    for k, r in enumerate(daily):
        buckets.setdefault(dates[k + 1][:4], []).append(r)
    return {y: {"days": len(v), "compound_pct": round(base.compound_pct(v), 3)}
            for y, v in sorted(buckets.items())}


def scale_to_vol(daily, target_pct, max_lev):
    """Lever the series to a volatility target (returns (series, leverage))."""
    if len(daily) < 2:
        return list(daily), 1.0
    sd = statistics.stdev(daily)
    vol = sd * math.sqrt(base.TRADING_DAYS) * 100.0
    lev = 1.0 if vol <= 0 else min(max_lev, target_pct / vol)
    return [r * lev for r in daily], round(lev, 4)


def margin_identity(ann_pct, mdd_pct, margin, stress_dd_pct=None):
    """Return on the capital a real book must keep behind one contract.

    margin alone is not the capital: a book that cannot fund its own drawdown is not
    holding the position, it is hoping.

    Two rulers, printed side by side because they answer different questions.  The
    sample ruler uses the drawdown this window produced; on a four-year futures series
    that number is small enough to make the capital look almost free, and it is a fact
    about the window, not about the contract.  The stress ruler uses the index's own
    worst drawdown over its whole history: the position is long the index, so that is
    the size of the hole it can be asked to fund no matter how kind the sample was.
    The buffer only grows (max of the two), never shrinks, so the stress column can
    never print a return higher than the sample column.
    """
    dd = abs(mdd_pct)
    cap = margin * 100.0 + dd            # both as percent of notional
    out = {
        "margin_assumed_pct": round(margin * 100.0, 2),
        "capital_pct_of_notional": round(cap, 3),
        "ann_on_capital_pct": round(ann_pct / cap * 100.0, 3) if cap > 0 else None,
        "dd_on_capital_pct": round(dd / cap * 100.0, 3) if cap > 0 else None,
        "dd_used_pct": round(dd, 3),
    }
    if stress_dd_pct is not None:
        sdd = max(dd, abs(float(stress_dd_pct)))
        scap = margin * 100.0 + sdd
        out["stress_dd_pct"] = round(sdd, 3)
        out["capital_stress_pct_of_notional"] = round(scap, 3)
        out["ann_on_capital_stress_pct"] = (
            round(ann_pct / scap * 100.0, 3) if scap > 0 else None)
        out["dd_on_capital_stress_pct"] = round(sdd / scap * 100.0, 3) if scap > 0 else None
        out["folded_to_sample_dd"] = bool(abs(sdd - dd) < 1e-9)
    return out


def corr(a, b):
    n = min(len(a), len(b))
    if n < 3:
        return None
    a, b = a[:n], b[:n]
    ma, mb = statistics.fmean(a), statistics.fmean(b)
    va = sum((x - ma) ** 2 for x in a)
    vb = sum((x - mb) ** 2 for x in b)
    if va <= 0 or vb <= 0:
        return None
    cov = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    return round(cov / math.sqrt(va * vb), 3)


# ------------------------------------------------------------------ the book under test
def adopted_book():
    """Daily returns of the desk's adopted book, rebuilt through the published engine.

    These are the same four calls etf_book_year_gate makes; the point of importing them
    rather than calling that script is that its receipt publishes the yearly face, not
    the daily series this face needs to correlate and blend.
    """
    import etf_composite_pf as E
    import etf_robust_pf as R
    import etf_equity_alpha as A

    close, openp, amt, feats = E.build_panel()
    close, openp, _n_flip = A.repair_flips(close, openp)
    cmap = A.load_class_map()
    cls = A.classify(close.columns, cmap, close)
    cols = [c for c in close.columns if cls[c] in ("equity", "commodity", "convertible")]
    sc = E.build_score(close[cols], amt[cols], feats)
    ser, turn = R.open_to_open_equity(close[cols], openp[cols], amt[cols], sc, 20, 5,
                                      0.0010, vol_target=CRITERIA["vol_target_pct"] / 100.0)
    lvl = [float(v) for v in ser.values]
    dates = [str(d)[:10] for d in ser.index]
    daily = [lvl[k] / lvl[k - 1] - 1.0 for k in range(1, len(lvl))]
    return {"book": "nobond_vt08_adopted", "dates": dates, "daily": daily,
            "turnover_side_pct": round(turn * 100.0, 2),
            "stats": risk_stats(daily, dates)}


def product_spread(prod, cache_dir=None):
    """The roll book's daily spread (held contract minus index) for one product."""
    code = base.PAIRS[prod][0]
    idx = base.load_index(code)
    panel = rn.contract_panel(prod, cache_dir)
    if not panel:
        return None
    first = min(min(v) for v in panel.values())
    last = max(max(v) for v in panel.values())
    days = sorted(d for d in idx if first <= d <= last)
    held, rolls = rn.active_path(days, panel)
    # the calendar of the returns comes back WITH them: rebuilding it here would be a
    # second implementation of the same drop rules, and a rebuilt one sits off by a day
    # the moment a contract or index day is skipped.
    cal_end, cal = [], [days[0]]
    rf, ri, forced = rn.book_returns(days, panel, held, idx, dates_out=cal_end)
    if len(rf) < CRITERIA.get("min_days", 400):
        return None
    spread = [a - b for a, b in zip(rf, ri)]
    cal.extend(cal_end)
    # What the same window paid for holding the MATCHING ETF instead: the spread above is
    # "long futures, short index", which needs a short leg this desk does not have; the
    # implementable form of the same idea is "own the future instead of the ETF", and that
    # is long index + carry, so it has to be priced against the ETF, not against zero.
    etf_ann, etf_flag = None, None
    try:
        etf_code = base.PAIRS[prod][2]
        holder = base.load_etf(etf_code) if etf_code else None
        if not etf_code:
            etf_flag = "no ETF mapped to this index in the panel, so there is nothing to price against"
        if holder:
            # A fund share conversion moves the price level by the same factor it divides
            # the share count, so that day carries no return and the leg is still readable.
            # Only an unexplained jump stays refused (etf_share_conversion, r1701).
            holder, conv_ev = SCA.adjusted_closes(etf_code)
            sub = [holder[d] for d in cal if d in holder]
            # the same trap the book's own panel carries: an unrepaired quote flip turns a
            # flat year into a hundred-percent one.  One >35% day and the ETF leg is a
            # reading we refuse to print rather than a gap we would report.
            jumps = sum(1 for k in range(1, len(sub))
                        if sub[k - 1] > 0 and (sub[k] / sub[k - 1] > 1.35
                                               or sub[k] / sub[k - 1] < 0.65))
            if jumps:
                etf_flag = "%d day(s) move more than 35%% in the ETF leg; gap not printed" % jumps
            elif len(sub) > 250 and sub[0] > 0:
                etf_ann = round(((sub[-1] / sub[0]) ** (base.TRADING_DAYS / (len(sub) - 1))
                                 - 1.0) * 100.0, 3)
                if conv_ev:
                    etf_flag = ("%d share conversion(s) removed (%s); level change is not a "
                                "return" % (len(conv_ev), ", ".join(
                                    "%s x%.3f" % (e["date"], e["ratio"]) for e in conv_ev)))
    except Exception:                                          # noqa: BLE001
        etf_ann = None
    return {"spread": spread, "dates": cal, "days": days, "rolls": len(rolls),
            "forced_api_days": forced, "index": code, "etf_ann_pct": etf_ann,
            "etf_flag": etf_flag,
            "futures_ann_pct": round(base.compound_pct(rf), 3),
            "index_ann_pct": round(base.compound_pct(ri), 3),
            # the hole this position can be asked to fund: the index's own worst
            # drawdown over its whole quoted history, not the kindest four years.
            "index_mdd_full_pct": round(
                base.max_drawdown_pct([idx[d] for d in sorted(idx)]), 3),
            "days_dropped": (len(days) - 1) - len(spread)}


def open_returns(dates, panel_ohlc, held):
    """Returns of the held contract between two OPENS, filled the day after the signal.

    Every reading this family published so far buys at a close: the roll book marks both
    legs at the same close, so the decision and the fill are the same instant and the
    seam costs zero by construction.  A desk cannot do that -- it decides after the
    close and fills the next session -- so the same book has to be re-run with the fill
    one session later, at that session's open.  The pairing is produced here (signal day
    -> fill day -> exit day) rather than rebuilt by a caller.
    """
    rf, ri = [], []
    for k in range(1, len(dates) - 1):
        d_dec, d_fill, d_exit = dates[k - 1], dates[k], dates[k + 1]
        sym = held.get(d_dec)
        row_a = panel_ohlc.get(sym, {}).get(d_fill) if sym else None
        row_b = panel_ohlc.get(sym, {}).get(d_exit) if sym else None
        if not (row_a and row_b and row_a["open"] > 0 and row_b["open"] > 0):
            continue
        rf.append(row_b["open"] / row_a["open"] - 1.0)
        ri.append(d_exit)
    return rf, ri


def exec_vs_close(prod, sp, cache_dir=None):
    """The implementable version of the same book: decide at the close, fill at the next open.

    The published gap (futures minus the matching ETF) is a close-to-close number.  If it
    only exists because the book buys at the price it decides at, it is not a gap a desk
    can collect.  This runs both legs from the same opens, subtracts the roll cost the
    cost face already measured, and prints the close-to-close number beside it so a
    reader can see what the execution convention is worth.
    """
    panel_ohlc = rn.contract_panel_ohlc(prod, cache_dir)
    if not panel_ohlc:
        return {"status": "no_contract_book"}
    panel_proj = {sym: {d: (row["close"], row["hold"], row["volume"])
                        for d, row in series.items()}
                  for sym, series in panel_ohlc.items()}
    held, rolls = rn.active_path(sp["days"], panel_proj)
    rf, exits = open_returns(sp["dates"], panel_ohlc, held)
    if len(rf) < CRITERIA.get("min_days", 400):
        return {"status": "too_short", "days": len(rf)}

    etf_code = base.PAIRS[prod][2]
    etf_open, conv_open = (SCA.adjusted_field(etf_code, "open") if etf_code
                           else (None, []))
    etf_ann_open, etf_flag = None, None
    if not etf_code:
        etf_flag = "no ETF is mapped to this index, so there is no other leg to price"
    elif not etf_open:
        etf_flag = "the ETF panel has no opens on this host"
    else:
        sub = [etf_open[d] for d in exits if d in etf_open]
        if len(sub) <= 250:
            etf_flag = "only %d shared open-to-open days" % len(sub)
        elif sub[0] <= 0:
            etf_flag = "the ETF leg starts at a non-positive open"
        else:
            jumps = sum(1 for k in range(1, len(sub))
                        if sub[k] / sub[k - 1] > 1.35 or sub[k] / sub[k - 1] < 0.65)
            if jumps:
                etf_flag = ("%d day(s) move more than 35%% in the ETF leg at the open;"
                            " the gap is refused, not printed as zero" % jumps)
            else:
                etf_ann_open = round(((sub[-1] / sub[0]) ** (base.TRADING_DAYS / (len(sub) - 1))
                                     - 1.0) * 100.0, 3)
                if conv_open:
                    etf_flag = ("%d share conversion(s) removed at the open (%s); the level "
                                "change is not a return" % (len(conv_open), ", ".join(
                                    "%s x%.3f" % (e["date"], e.get("ratio", e.get("factor")))
                                    for e in conv_open)))

    fut_ann_open = round(base.compound_pct(rf), 3)
    gap_open = None if etf_ann_open is None else round(fut_ann_open - etf_ann_open, 3)
    gap_close = (None if (sp.get("futures_ann_pct") is None or sp.get("etf_ann_pct") is None)
                 else round(sp["futures_ann_pct"] - sp["etf_ann_pct"], 3))

    # The cost face prints a BAND, not a point: its estimator has no resolution below a
    # few dozen ticks, so a single "roll costs X" would be a choice dressed as a number.
    # Two drags are computed -- the exchange-file floor and the measured median -- and the
    # reader gets the gap under both ends.
    band = roll_cost_band(prod)
    years = len(rf) / base.TRADING_DAYS

    def drag(bp):
        return None if (bp is None or years <= 0) else round(len(rolls) * bp / 1e4 / years * 100.0, 3)

    drag_floor = drag(band.get("floor_bp") if band else None)
    drag_median = drag(band.get("median_bp") if band else None)
    gap_floor = None if (gap_open is None or drag_floor is None) else round(gap_open - drag_floor, 3)
    gap_median = None if (gap_open is None or drag_median is None) else round(gap_open - drag_median, 3)
    return {
        "status": "ok",
        "days": len(rf),
        "rolls": len(rolls),
        "roll_cost_bp": band,
        "roll_cost_drag_pp_per_year": {"file_floor": drag_floor, "measured_median": drag_median},
        "futures_open_open_ann_pct": fut_ann_open,
        "etf_open_open_ann_pct": etf_ann_open,
        "etf_flag": etf_flag,
        "gap_open_open_pp": gap_open,
        "gap_close_close_pp": gap_close,
        "gap_after_roll_cost_pp": {"file_floor": gap_floor, "measured_median": gap_median},
    }


def roll_cost_band(prod):
    """The measured cost of one roll for this product, as a band, from the cost face.

    Read, not recomputed: idx_fut_roll_cost owns that estimator and its caveats (no
    resolution below ~40 ticks, which is why IF stays unresolved there).  The floor is
    the exchange file; the median is what the amplitude reading returns, and the cost
    page itself says that reading is an upper region rather than a mid estimate.  If the
    face is missing, the numbers are absent and the caller prints "unknown", never zero.
    """
    path = os.path.join(ROOT, "results", "idx_fut_roll_cost.json")
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            face = json.load(f)
        row = face["products"][prod]
        med = (row.get("measured") or {}).get("median_bp")
        floor = row.get("published_floor_bp")
        if med is None and floor is None:
            return None
        return {"median_bp": med, "floor_bp": floor}
    except Exception:                                          # noqa: BLE001
        return None


def roll_caliber(prod, path=None):
    """What the same product's carry reads under each published roll ruler.

    Read, not recomputed: idx_fut_roll_gap owns both estimators and the split that
    prices them.  This face's own series performs every max-open-interest switch and
    drops no days, so neither ruler below is this face's treatment -- the column exists
    to show how far a carry headline moves when the roll-day rule changes, not to pick
    a favourite.  An unreadable face is UNKNOWN, never "the rulers agree".
    """
    p = path or ROLL_GAP
    if not p or not os.path.exists(p):
        return {"status": "unreadable"}
    try:
        with open(p, "r", encoding="utf-8") as f:
            face = json.load(f)
        pair = (((face.get("dilution") or {}).get("pairs") or {}).get(prod)) or {}
        pub = pair.get("published_ann_pct")
        cal = pair.get("calendar_ann_pct")
        spread = None if (pub is None or cal is None) else round(abs(cal - pub), 3)
        return {"status": "ok", "published_ann_pct": pub, "calendar_ann_pct": cal,
                "spread_pp": spread,
                "missed_roll_days": pair.get("missed_roll_days"),
                "deleted_real_days": pair.get("deleted_real_days"),
                "reading": pair.get("reading"),
                "face_verdict": (face.get("dilution") or {}).get("verdict")}
    except (OSError, ValueError, KeyError, TypeError):
        return {"status": "unreadable"}


def judge_product(prod, sp, book, cache_dir=None, caliber=None):
    r = risk_stats(sp["spread"], sp["dates"])
    scaled, lev = scale_to_vol(sp["spread"], CRITERIA["vol_target_pct"], CRITERIA["max_leverage"])
    r8 = risk_stats(scaled, sp["dates"])
    margins = {k: margin_identity(r["ann_compound_pct"], r["mdd_pct"], v,
                                  stress_dd_pct=sp.get("index_mdd_full_pct"))
               for k, v in CRITERIA["margin_assumptions"].items()}

    # align the two sleeves on shared dates before correlating or blending
    idx = {d: k for k, d in enumerate(sp["dates"][1:])}
    bidx = {d: k for k, d in enumerate(book["dates"][1:])}
    common = sorted(set(idx) & set(bidx))
    rs = [sp["spread"][idx[d]] for d in common]
    rb = [book["daily"][bidx[d]] for d in common]

    blends = []
    for lam in CRITERIA["blend_lambdas"]:
        raw = [(1.0 - lam) * b + lam * s for b, s in zip(rb, rs)]
        scaled_b, lev_b = scale_to_vol(raw, CRITERIA["blend_risk_pct"], 20.0)
        st = risk_stats(scaled_b)
        blends.append({"lambda": lam, "leverage": lev_b,
                       "ann_pct": st["ann_mean_pct"], "vol_pct": st["ann_vol_pct"],
                       "sharpe": st["sharpe"], "mdd_pct": st["mdd_pct"]})
    base_sharpe = next((b["sharpe"] for b in blends if b["lambda"] == 0.0), None)
    best = max((b for b in blends if b["sharpe"] is not None),
               key=lambda b: b["sharpe"], default=None)
    gain = None if (best is None or base_sharpe is None) else round(best["sharpe"] - base_sharpe, 3)

    c = corr(rb, rs)
    bstat = book["stats"]
    at_target_ann = r8.get("ann_compound_pct")
    verdict, why = derive_verdict(
        carry_ann=r.get("ann_compound_pct"), carry_ann8=at_target_ann,
        carry_mdd8=r8.get("mdd_pct"), book_cagr=bstat.get("ann_compound_pct"),
        book_mdd=bstat.get("mdd_pct"), corr=c, gain=gain,
        common_days=len(common))
    return {
        "product": prod, "index": sp["index"], "rolls": sp["rolls"],
        "days": len(sp["spread"]), "days_dropped": sp.get("days_dropped"),
        "span": {"first": sp["dates"][0], "last": sp["dates"][-1]},
        "risk": r,
        "execution": exec_vs_close(prod, sp, cache_dir),
        "at_vol_target": {"target_pct": CRITERIA["vol_target_pct"], "leverage": lev, **r8},
        "margin_identity": margins,
        "realizable": realizable_form(prod, sp, r, dividend_drift(prod)),
        "common_days_with_book": len(common),
        "corr_with_book": c,
        "blend": blends,
        "blend_best": best, "blend_gain_sharpe": gain,
        "roll_caliber": caliber if caliber is not None else {"status": "unreadable"},
        "verdict": verdict, "why": why,
    }


def dividend_drift(prod, path=None):
    """ETF-accrues-dividend drift for one product, read from the basis face's C3 arm.

    The future tracks the PRICE index; the ETF holds the basket and is paid the cash
    dividend. So the gap column is gross of a structural drift that has nothing to do
    with the futures market. The basis face already measures that drift on this repo's
    own panel (C3 control arm) -- this reads its published reading rather than opening a
    second estimator. A missing face returns None, never 0: an unread control is not a
    measured zero.
    """
    p = path or BASIS_JSON
    try:
        with open(p, "r", encoding="utf-8") as fh:
            doc = json.load(fh)
    except (OSError, ValueError):
        return None
    for row in ((doc.get("verdict") or {}).get("carries") or []):
        if row.get("fut") == prod:
            d = row.get("drift_pct")
            return None if d is None else float(d)
    return None


def realizable_form(prod, sp, risk, drift=None):
    """The same carry, in the form this desk can actually hold.

    The daily spread is futures-minus-index: isolating it needs a short leg on the index,
    which this desk cannot borrow.  Holding the future INSTEAD of the ETF is the
    implementable version, and it is long the index too, so it can only be sold to a
    reader next to the ETF's own return over the same window.

    The gap is gross of the dividend control: the ETF is paid the basket's cash dividend
    and the price index the future tracks is not. Subtracting the basis face's measured
    drift is the net reading; when that control is unreadable the net column stays None
    and the page says so, because a reader who is handed the gross number alone will
    book a dividend as carry.
    """
    fut = sp.get("futures_ann_pct")
    etf = sp.get("etf_ann_pct")
    gap = None if (fut is None or etf is None) else round(fut - etf, 3)
    net = None if (gap is None or drift is None) else round(gap - drift, 3)
    return {
        "long_futures_ann_pct": fut,
        "etf_same_window_ann_pct": etf,
        "gap_pp": gap,
        "dividend_drift_pp": drift,
        "gap_net_of_dividend_pp": net,
        "dividend_source": ("results/idx_fut_basis.json verdict.carries[].drift_pct"
                            " (C3 control arm, this repo's own ETF/index panel)"),
        "etf_flag": sp.get("etf_flag"),
        "note": ("the spread is long-futures/short-index and needs a short leg this desk"
                 " does not have; owning the future instead of the ETF earns index+carry"
                 " and is priced against the ETF in the gap column, which is gross of the"
                 " dividend drift printed beside it"),
    }


def derive_verdict(carry_ann, carry_ann8, carry_mdd8, book_cagr, book_mdd, corr,
                   gain, common_days):
    """Mechanical: the sleeve has to earn at the desk's risk level AND not move with the book."""
    if common_days < 250:
        return "UNADJUDICABLE", "only %d shared days with the book" % common_days
    if carry_ann is None or carry_ann8 is None:
        return "UNADJUDICABLE", "carry series too short to measure"
    if carry_ann8 <= 0:
        return "REFUSE", "at the desk's risk level the sleeve earns nothing"
    if book_cagr is not None and carry_ann8 <= book_cagr:
        return ("REFUSE",
                "at %s%% vol the sleeve earns %.2f%% against the book's %.2f%%"
                % (CRITERIA["vol_target_pct"], carry_ann8, book_cagr))
    if corr is None or corr >= CRITERIA["corr_diversifies_below"]:
        return ("NO_GAIN",
                "earns %.2f%% at target risk but moves with the book (corr %s), so it"
                " does not change what the book earns per unit of risk"
                % (carry_ann8, corr))
    if gain is None or gain < CRITERIA["improve_sharpe_min"]:
        return ("NO_GAIN", "blending it into the book moves Sharpe by %s" % gain)
    return ("SLEEVE_CANDIDATE",
            "carry %.2f%% at target risk, corr %s, blend Sharpe %+.3f"
            % (carry_ann8, corr, gain))


# ------------------------------------------------------------------ face
def build(cache_dir=None, with_book=True):
    t0 = time.time()
    face = {
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "evidence_cutoff": None,
        "kind": "carry_sleeve_risk",
        "criteria": dict(CRITERIA),
        "book": None,
        "products": {},
        "verdict": {},
    }
    book = None
    if with_book:
        try:
            book = adopted_book()
        except Exception as exc:                                    # noqa: BLE001
            face["book"] = {"status": "unavailable",
                            "detail": "%s: %s" % (type(exc).__name__, exc)}
    if book is not None:
        face["book"] = {"book": book["book"],
                        "turnover_side_pct": book["turnover_side_pct"],
                        **book["stats"]}
        face["evidence_cutoff"] = book["dates"][-1]
    for prod in CRITERIA["products"]:
        try:
            sp = product_spread(prod, cache_dir)
        except Exception as exc:                                    # noqa: BLE001
            face["products"][prod] = {"status": "error",
                                      "detail": "%s: %s" % (type(exc).__name__, exc)}
            continue
        if sp is None:
            face["products"][prod] = {"status": "no_contract_book"}
            continue
        if book is None:
            face["products"][prod] = {"status": "no_book_to_compare"}
            continue
        row = judge_product(prod, sp, book, cache_dir, caliber=roll_caliber(prod))
        face["products"][prod] = row
        cut = row["span"]["last"]
        if face["evidence_cutoff"] is None or cut > face["evidence_cutoff"]:
            face["evidence_cutoff"] = cut
    face["verdict"] = judge(face)
    face["elapsed_sec"] = round(time.time() - t0, 1)
    return face


def judge(face):
    """One sentence per product, derived from its own row -- never typed."""
    rows = {}
    for prod, row in (face.get("products") or {}).items():
        if row.get("status"):
            rows[prod] = {"verdict": row["status"], "why": None}
        else:
            rows[prod] = {"verdict": row["verdict"], "why": row["why"],
                          "carry_at_target_pct": (row.get("at_vol_target") or {}).get(
                              "ann_compound_pct"),
                          "corr_with_book": row.get("corr_with_book"),
                          "blend_gain_sharpe": row.get("blend_gain_sharpe"),
                          "caliber_spread_pp": (row.get("roll_caliber") or {}).get(
                              "spread_pp")}
    cands = [p for p, v in rows.items() if v["verdict"] == "SLEEVE_CANDIDATE"]
    return {
        "rows": rows,
        "sleeve_candidates": sorted(cands),
        "any_candidate": bool(cands),
        "note": ("a candidate here is a sleeve worth pricing forward, not an adopted"
                 " position: the readings are in-sample and the margin is an assumption"),
    }


# ------------------------------------------------------------------ rendering
def _p(v, nd=2, dash="-"):
    return dash if v is None else ("%.*f" % (nd, v))


def _sgn(v, nd=2, dash="-"):
    """Signed percentage points.  A gap is only readable with its sign: +2.5 and -2.5
    are opposite decisions, and a formatter that drops the sign merges them."""
    return dash if v is None else ("%+.*f" % (nd, v))


def caliber_block(face):
    """The caliber the carry column rides on, one row per product.

    Two published rulers count different days as roll days, and the annualised carry
    moves by several points between them.  This prints three numbers side by side -- this
    face's own reading, the threshold ruler, the calendar ruler -- plus the size of the
    disagreement, so no single figure is read as a measurement.  Every number is read off
    the roll-mask face; nothing is recomputed and nothing is borrowed across a missing
    side (an unread ruler is "unknown", never "they agree").
    """
    rows = face.get("products") or {}
    out = ["## the caliber the carry column rides on", ""]
    out.append("Which days count as roll days moves the annualised carry by more than this"
               " sleeve's whole margin over the book, so the column above travels with both"
               " rulers the roll-mask face publishes for the same products"
               " (`results/idx_fut_roll_gap.json`, read, not recomputed). This face's own"
               " series performs every max-open-interest switch and drops no days, so"
               " neither ruler below is this face's own treatment.")
    out.append("")
    out.append("| product | this face carry %/yr | threshold ruler %/yr | calendar ruler %/yr"
               " | rulers disagree by pp | roll days the threshold ruler misses |")
    out.append("|---|---|---|---|---|---|")
    bullets = []
    for prod in CRITERIA["products"]:
        row = rows.get(prod) or {}
        cal = row.get("roll_caliber") or {}
        own = None if row.get("status") else (row.get("risk") or {}).get("ann_compound_pct")
        pub = cal.get("published_ann_pct")
        knd = cal.get("calendar_ann_pct")
        spr = cal.get("spread_pp")
        miss = cal.get("missed_roll_days")
        out.append("| %s | %s | %s | %s | %s | %s |"
                   % (prod, _p(own), _p(pub), _p(knd),
                      ("%.2f" % spr if spr is not None else "?"),
                      miss if miss is not None else "?"))
        if cal.get("status") != "ok":
            bullets.append("- **%s**: the roll-mask face is unreadable on this host, so the"
                           " caliber is unknown here -- an unread ruler is not 'the rulers"
                           " agree'." % prod)
        elif spr is None:
            bullets.append("- **%s**: one of the two rulers has no reading on this window, so"
                           " the spread is unknown rather than zero." % prod)
        elif spr >= CALIBER_SPREAD_PP:
            bullets.append("- **%s**: the two published rulers disagree by %.2f pp on the same"
                           " window; a single carry figure inside that band is a caliber"
                           " choice, not a measurement." % (prod, spr))
        else:
            bullets.append("- **%s**: the two published rulers agree to within %.2f pp here,"
                           " so the caliber does not move this product's reading."
                           % (prod, spr))
    out.append("")
    out.extend(bullets)
    out.append("")
    return out


def render_md(face):
    L = []
    L.append("# index-futures carry: what it is worth in risk units")
    L.append("")
    L.append("Generated %s · evidence cutoff %s · `scripts/idx_fut_carry_risk.py`"
             % (face.get("generated"), face.get("evidence_cutoff")))
    L.append("")
    L.append("The roll book (hold the deepest-open-interest contract, switch at the same"
             " close) is the one `idx_fut_real_nav` publishes in rupees of carry per year."
             " This page asks the only question that allocates money: at the desk's own 8%"
             " volatility target, does that carry buy anything the adopted book does not"
             " already buy, and does it move with it?")
    L.append("")
    bk = face.get("book") or {}
    if bk.get("status"):
        L.append("**The adopted book could not be rebuilt this run** (`%s`) -- every"
                 " comparison below is unavailable, not zero." % bk.get("status"))
        L.append("")
    else:
        L.append("## the book it is compared against")
        L.append("")
        L.append("- %s: %s%% a year compounded, vol %s%%, Sharpe %s, max drawdown %s%%,"
                 " worst year %s%%, underwater run up to %s bars"
                 % (bk.get("book"), _p(bk.get("ann_compound_pct"), 2),
                    _p(bk.get("ann_vol_pct")), _p(bk.get("sharpe"), 3),
                    _p(bk.get("mdd_pct")), _p(bk.get("worst_year_pct")),
                    bk.get("underwater_max_bars")))
        if bk.get("underwater_open_bars"):
            L.append("- the last drawdown **has not healed**: still under water for"
                     " %s bars at the last bar (a censored duration is not a fast recovery)"
                     % bk.get("underwater_open_bars"))
        L.append("")
    L.append("## each product, in its own risk units")
    L.append("")
    L.append("| product | years | carry %/yr | vol % | Sharpe | max DD % | underwater bars"
             " (still open) | worst year % |")
    L.append("|---|---|---|---|---|---|---|---|")
    for prod in CRITERIA["products"]:
        row = (face.get("products") or {}).get(prod) or {}
        if row.get("status") or not row.get("risk"):
            L.append("| %s | - | - | - | - | - | - | - |" % prod)
            continue
        r = row["risk"]
        yrs = round(row["days"] / base.TRADING_DAYS, 2)
        L.append("| %s | %s | %s | %s | %s | %s | %s (%s) | %s |"
                 % (prod, yrs, _p(r.get("ann_compound_pct")), _p(r.get("ann_vol_pct")),
                    _p(r.get("sharpe"), 3), _p(r.get("mdd_pct")),
                    r.get("underwater_max_bars"), r.get("underwater_open_bars", 0),
                    _p(r.get("worst_year_pct"))))
    L.extend(caliber_block(face))
    L.append("## at the desk's 8% volatility target")
    L.append("")
    L.append("| product | leverage to 8% vol | carry %/yr | max DD % | corr with the book |"
             " best blend lam | blend Sharpe gain | verdict |")
    L.append("|---|---|---|---|---|---|---|---|")
    for prod in CRITERIA["products"]:
        row = (face.get("products") or {}).get(prod) or {}
        if not row or row.get("status") or not row.get("at_vol_target"):
            L.append("| %s | - | - | - | - | - | - | %s |"
                     % (prod, row.get("status") or "absent"))
            continue
        a8 = row["at_vol_target"]
        best = row.get("blend_best") or {}
        L.append("| %s | x%s | %s | %s | %s | %s | %s | %s |"
                 % (prod, _p(a8.get("leverage"), 2), _p(a8.get("ann_compound_pct")),
                    _p(a8.get("mdd_pct")), _p(row.get("corr_with_book"), 3),
                    _p(best.get("lambda"), 2),
                    ("%+.3f" % row["blend_gain_sharpe"]
                     if row.get("blend_gain_sharpe") is not None else "-"),
                    row["verdict"]))
    L.append("")
    for prod in CRITERIA["products"]:
        row = (face.get("products") or {}).get(prod) or {}
        if row.get("why"):
            L.append("- **%s**: %s" % (prod, row["why"]))
    L.append("")
    L.append("## the form this desk can actually hold")
    L.append("")
    L.append("The daily spread above is futures minus index: it is the *excess* return, and"
             " isolating it needs a short leg on the index, which this desk cannot borrow."
             " The implementable version of the same idea is owning the future **instead of**"
             " the matching ETF -- that is long the index too -- so the column that matters"
             " is the gap against the ETF itself over the same window.")
    L.append("")
    L.append("| product | long the future %/yr | the matching ETF %/yr | gap pp |"
             " dividend drift pp | gap net of dividend pp |")
    L.append("|---|---|---|---|---|---|")
    for prod in CRITERIA["products"]:
        row = (face.get("products") or {}).get(prod) or {}
        rz = row.get("realizable")
        if not rz:
            L.append("| %s | - | - | - | - | - |" % prod)
            continue
        L.append("| %s | %s | %s | %s | %s | %s |"
                 % (prod, _p(rz.get("long_futures_ann_pct")),
                    _p(rz.get("etf_same_window_ann_pct")),
                    ("%+.2f" % rz["gap_pp"] if rz.get("gap_pp") is not None else "-"),
                    _p(rz.get("dividend_drift_pp")),
                    ("%+.2f" % rz["gap_net_of_dividend_pp"]
                     if rz.get("gap_net_of_dividend_pp") is not None else "-")))
    L.append("")
    L.append("The gap column is GROSS of a structural drift that is not a futures market"
             " reading: the ETF is paid the basket's cash dividend and the price index the"
             " future tracks is not. The drift column is the basis face's own C3 control"
             " arm (results/idx_fut_basis.json), measured on this repo's panel -- it is not"
             " a dividend announcement. Where that control could not be read the net"
             " column is blank, not equal to the gross one.")
    flags = [(p, (face["products"][p].get("realizable") or {}).get("etf_flag"))
             for p in CRITERIA["products"]
             if (face.get("products") or {}).get(p, {}).get("realizable", {}).get("etf_flag")]
    for p, why in flags:
        rz = ((face.get("products") or {}).get(p) or {}).get("realizable") or {}
        priced = rz.get("gap_pp") is not None
        L.append("- **%s leg %s**: %s%s" % (
            p, "priced, level change disclosed" if priced else "not priced", why,
            "" if priced else " -- an unread leg is printed as a refusal, not as a zero gap"))
    L.append("")
    L.append("## the same book filled at the next open")
    L.append("")
    L.append("Every number above buys at the close it decides at. A desk decides after the"
             " close and fills the next session, so the book is re-run with the fill one"
             " session later at that session's open (both legs, rolls included), and the"
             " roll cost the cost face measured is subtracted. If the gap against the ETF"
             " only exists at closes, it is not a gap anyone can collect.")
    L.append("")
    L.append("| product | futures open→open %/yr | ETF open→open %/yr | gap pp | gap at closes pp |"
             " gap after cost (file floor) pp | gap after cost (measured median) pp |")
    L.append("|---|---|---|---|---|---|---|")
    for prod in CRITERIA["products"]:
        row = (face.get("products") or {}).get(prod) or {}
        ex = row.get("execution") or {}
        if ex.get("status") != "ok":
            L.append("| %s | - | - | - | - | - | %s |"
                     % (prod, ex.get("status", "not built")))
            continue
        after = ex.get("gap_after_roll_cost_pp") or {}
        L.append("| %s | %s | %s | %s | %s | %s | %s |"
                 % (prod, _p(ex.get("futures_open_open_ann_pct")),
                    _p(ex.get("etf_open_open_ann_pct")),
                    _sgn(ex.get("gap_open_open_pp")), _sgn(ex.get("gap_close_close_pp")),
                    _sgn(after.get("file_floor")), _sgn(after.get("measured_median"))))
    for prod in CRITERIA["products"]:
        ex = ((face.get("products") or {}).get(prod) or {}).get("execution") or {}
        if ex.get("status") != "ok":
            continue
        after = ex.get("gap_after_roll_cost_pp") or {}
        floor, med = after.get("file_floor"), after.get("measured_median")
        at_close = ex.get("gap_close_close_pp")
        drags = ex.get("roll_cost_drag_pp_per_year") or {}
        if ex.get("gap_open_open_pp") is None:
            # Two different absences live here and they call for opposite actions: the
            # other leg cannot be priced (quote problem) versus the cost is unknown
            # (face missing).  Printing one word for both is the r1159 family.
            L.append("- **%s**: no open-to-open gap is printed because the other leg could not"
                     " be priced (%s); that is a missing price, not a zero gap"
                     % (prod, ex.get("etf_flag") or "unstated"))
        elif floor is None or med is None:
            L.append("- **%s**: the roll cost for this product is unknown on this host, so the"
                     " gap after execution is not printed (an absent number is not zero)" % prod)
        elif floor > 0 and med > 0:
            L.append("- **%s**: holds at both ends of the cost band: %+.2f pp/yr at the exchange"
                     " file, %+.2f pp/yr at the measured median (%d rolls, drag %s / %s pp/yr)"
                     % (prod, floor, med, ex["rolls"], _p(drags.get("file_floor")),
                        _p(drags.get("measured_median"))))
        elif floor > 0:
            L.append("- **%s**: only at the exchange file (%+.2f pp/yr); at the measured median"
                     " the gap is %+.2f pp/yr, so this stays undecided on a quote tape rather"
                     " than admitted" % (prod, floor, med))
        else:
            L.append("- **%s**: does not survive the fill convention and the roll cost: %+.2f"
                     " pp/yr at the file floor against %s pp at closes -- the published gap is"
                     " partly the convention, not the carry" % (prod, floor, _sgn(at_close)))
    refused = [(p, ((face.get("products") or {}).get(p) or {}).get("execution") or {})
               for p in CRITERIA["products"]]
    for p, ex in refused:
        if ex.get("status") == "ok" and ex.get("etf_flag"):
            # A removed share conversion is a disclosure on a leg that IS priced; only a
            # leg whose flag left it unpriced belongs in "not priced" (r1159 family).
            priced = ex.get("gap_open_open_pp") is not None
            L.append("- **%s leg %s**: %s" % (
                p, "priced, with the level change disclosed" if priced else "not priced at the open",
                ex["etf_flag"]))
    L.append("")
    L.append("## what one contract actually ties up (margin is an assumption)")
    L.append("")
    L.append("Margin is not the capital: a book that cannot fund its own drawdown is not"
             " holding the position. Capital = margin + |max drawdown|, so the return on it"
             " is carry/(margin+DD) and the drawdown is DD/(margin+DD) of everything you put in.")
    L.append("")
    L.append("| product | margin 10% | margin 12% | margin 15% |")
    L.append("|---|---|---|---|")
    for prod in CRITERIA["products"]:
        row = (face.get("products") or {}).get(prod) or {}
        m = row.get("margin_identity")
        if not m:
            L.append("| %s | - | - | - |" % prod)
            continue
        cells = []
        for key in ("10pct", "12pct", "15pct"):
            v = m.get(key) or {}
            cells.append("%s%% on capital, DD %s%%"
                         % (_p(v.get("ann_on_capital_pct")), _p(v.get("dd_on_capital_pct"))))
        L.append("| %s | %s | %s | %s |" % (prod, cells[0], cells[1], cells[2]))
    L.append("")
    L.append("### the same carry sized against the index's worst drawdown")
    L.append("")
    L.append("The table above buffers the margin with the drawdown this window produced."
             " That buffer is a property of the sample, not of the contract: the position"
             " is long the index, so the hole it can be asked to fund is the index's own"
             " worst drawdown over its full quoted history. Same carry, same margin, only"
             " the buffer changes -- and the buffer is the whole difference between a"
             " capital number you can finance and one you cannot.")
    L.append("")
    L.append("| product | index worst DD % | margin 10% | margin 12% | margin 15% |")
    L.append("|---|---|---|---|---|")
    for prod in CRITERIA["products"]:
        row = (face.get("products") or {}).get(prod) or {}
        m = row.get("margin_identity") or {}
        mid = m.get("12pct") or {}
        sdd = mid.get("stress_dd_pct")
        if sdd is None:
            L.append("| %s | - | - | - | - |" % prod)
            continue
        cells = []
        for key in ("10pct", "12pct", "15pct"):
            v = m.get(key) or {}
            cells.append("%s%% on capital, DD %s%%"
                         % (_p(v.get("ann_on_capital_stress_pct")),
                            _p(v.get("dd_on_capital_stress_pct"))))
        L.append("| %s | %s | %s | %s | %s |"
                 % (prod, _p(sdd), cells[0], cells[1], cells[2]))
    stress_vals = []
    for prod in CRITERIA["products"]:
        mid = ((((face.get("products") or {}).get(prod) or {}).get("margin_identity")
                or {}).get("12pct") or {})
        if mid.get("stress_dd_pct") is not None:
            stress_vals.append(mid["stress_dd_pct"])
    if len(stress_vals) > 1:
        L.append("")
        L.append("The four holes sit within %s pp of each other (%s to %s): these indices"
                 " fell in the same crisis, so the buffer is one market-wide number, not"
                 " four independent ones -- holding several products does not shrink it."
                 % (_p(max(stress_vals) - min(stress_vals)), _p(min(stress_vals)),
                    _p(max(stress_vals))))
    L.append("")
    L.append("## blend grid")
    L.append("")
    L.append("(1-lam) x adopted book + lam x carry, rescaled to one 10% risk level so the"
             " columns are comparable: leverage is doing the risk normalisation, not the book.")
    L.append("")
    for prod in CRITERIA["products"]:
        row = (face.get("products") or {}).get(prod) or {}
        if row.get("status"):
            continue
        L.append("**%s**" % prod)
        L.append("")
        L.append("| lam | leverage | ann % | vol % | Sharpe | max DD % |")
        L.append("|---|---|---|---|---|---|")
        for b in row.get("blend") or []:
            L.append("| %s | x%s | %s | %s | %s | %s |"
                     % (_p(b.get("lambda"), 2), _p(b.get("leverage"), 2),
                        _p(b.get("ann_pct")), _p(b.get("vol_pct")),
                        _p(b.get("sharpe"), 3), _p(b.get("mdd_pct"))))
        L.append("")
    L.append("## honest limits")
    L.append("")
    L.append("- every reading is in-sample; this page says whether the sleeve is worth"
             " pricing forward, not whether it will earn.")
    L.append("- the carry series is futures-minus-index on the quote source's closes, with"
             " the roll performed at one close; a broker's fill and the margin surcharge are"
             " not in it.")
    L.append("- correlation is measured on shared calendar days only; a product whose"
             " contract history is short is judged on fewer days, printed per row.")
    L.append("- a sleeve candidate here is a candidate for the **hedged** sleeve. Without the"
             " short leg the same carry is only available bundled with index risk, which is"
             " what the two-column gap above prices.")
    L.append("- the sleeve candidate test uses the book's own realised vol, so a change in"
             " the book's risk engine moves this verdict without touching the carry.")
    L.append("")
    return "\n".join(L) + "\n"


def write_doc(face):
    with open(DOC, "w", encoding="utf-8", newline="\n") as f:
        f.write(render_md(face))
    return DOC


def checkdoc(face=None):
    if face is None:
        # "page == face" means the page matches the face that was PUBLISHED. Rebuilding
        # one here stamps a new `generated` and the comparison can never pass, which is a
        # red leg nobody can act on.
        try:
            with open(OUT, "r", encoding="utf-8") as _f:
                face = json.load(_f)
        except (OSError, ValueError):
            face = build(with_book=False)
    if not os.path.isfile(DOC):
        print("checkdoc: page missing")
        return 1
    with open(DOC, "r", encoding="utf-8") as f:
        have = f.read()
    want = render_md(face)
    if have.strip() != want.strip():
        print("checkdoc: page != face (%d vs %d chars)" % (len(have), len(want)))
        return 1
    print("checkdoc: rc0 page==face (%d chars)" % len(want))
    return 0


# ------------------------------------------------------------------ selftest
def selftest():
    legs = []

    def leg(name, ok, detail=""):
        legs.append((name, bool(ok), detail))

    # a constant positive spread: no vol, no drawdown, leverage capped
    flat = [0.001] * 250
    r = risk_stats(flat, ["d%03d" % i for i in range(251)])
    leg("a constant spread has zero vol and no drawdown",
        r["ann_vol_pct"] == 0.0 and r["mdd_pct"] == 0.0, str(r["ann_vol_pct"]))

    # a drawdown that never heals must be reported as open, not as zero
    dd = [-0.01] * 50 + [0.0001] * 50
    lvl = equity(dd)
    done, still = underwater(lvl)
    leg("an unhealed drawdown is open, not completed", done == 0 and still > 0,
        "done=%s still=%s" % (done, still))

    # a full drawdown and recovery is a completed run
    cyc = [-0.01] * 20 + [0.012] * 20
    done2, still2 = underwater(equity(cyc))
    leg("a healed drawdown is completed and not open", done2 > 0 and still2 == 0,
        "done=%s still=%s" % (done2, still2))

    # scaling to a vol target must actually hit it (within the cap)
    noisy = [0.002, -0.001, 0.003, -0.002] * 100
    sc, lev = scale_to_vol(noisy, 8.0, 10.0)
    v_before = risk_stats(noisy)["ann_vol_pct"]
    v_after = risk_stats(sc)["ann_vol_pct"]
    capped = lev >= 10.0 - 1e-9
    leg("scaling to 8% vol lands on 8% +/- 0.05pp unless the cap binds",
        abs(v_after - 8.0) < 0.05 or capped,
        "lev=%s before=%s after=%s" % (lev, v_before, v_after))

    # the leverage cap binds instead of inventing a huge position
    tiny = [0.0001, -0.0001] * 100
    _sc2, lev2 = scale_to_vol(tiny, 8.0, 3.0)
    leg("the leverage cap binds", lev2 <= 3.0, str(lev2))

    # margin identity: capital includes the drawdown, so return on capital < return/margin
    m = margin_identity(8.0, -20.0, 0.12)
    leg("capital = margin + |drawdown|", abs(m["capital_pct_of_notional"] - 32.0) < 1e-6,
        str(m["capital_pct_of_notional"]))
    leg("return on capital is diluted by the buffer",
        m["ann_on_capital_pct"] < 8.0 / 12.0 * 100, str(m["ann_on_capital_pct"]))

    # the stress ruler: a bigger buffer can only lower the return, never raise it
    ms = margin_identity(10.0, -5.0, 0.12, stress_dd_pct=-45.0)
    leg("stress buffer folds to the index's worst hole",
        abs(ms["capital_stress_pct_of_notional"] - 57.0) < 1e-6,
        str(ms["capital_stress_pct_of_notional"]))
    leg("stress lowers the return on capital",
        ms["ann_on_capital_stress_pct"] < ms["ann_on_capital_pct"],
        "%s < %s" % (ms["ann_on_capital_stress_pct"], ms["ann_on_capital_pct"]))
    leg("a sample already worse than the index keeps its own buffer",
        margin_identity(10.0, -60.0, 0.12, stress_dd_pct=-45.0)["stress_dd_pct"] == 60.0,
        str(margin_identity(10.0, -60.0, 0.12, stress_dd_pct=-45.0)["stress_dd_pct"]))
    leg("no stress input prints no stress column",
        "ann_on_capital_stress_pct" not in m, str(m.get("stress_dd_pct")))

    # correlation of a series with itself is 1, and with its negation is -1
    a = [0.1, -0.2, 0.3, -0.1, 0.05]
    leg("corr(x,x)=1", abs((corr(a, a) or 0) - 1.0) < 1e-9, str(corr(a, a)))
    leg("corr(x,-x)=-1", abs((corr(a, [-v for v in a]) or 0) + 1.0) < 1e-9,
        str(corr(a, [-v for v in a])))

    # verdicts are mechanical
    v1 = derive_verdict(8.0, 9.0, -5.0, 11.5, -12.5, 0.1, 0.10, 1000)
    leg("carry below the book at equal risk is refused", v1[0] == "REFUSE", v1[0])
    v2 = derive_verdict(8.0, 14.0, -5.0, 11.5, -12.5, 0.9, 0.30, 1000)
    leg("carry that moves with the book is no gain", v2[0] == "NO_GAIN", v2[0])
    v3 = derive_verdict(8.0, 14.0, -8.0, 11.5, -12.5, 0.1, 0.30, 1000)
    leg("carry that earns and diversifies is a candidate", v3[0] == "SLEEVE_CANDIDATE", v3[0])
    v4 = derive_verdict(8.0, 14.0, -8.0, 11.5, -12.5, 0.1, 0.30, 10)
    leg("too few shared days is unadjudicable", v4[0] == "UNADJUDICABLE", v4[0])

    # year buckets never annualise a partial year into a full one silently
    dates = ["2024-12-%02d" % d for d in range(1, 11)] + ["2025-01-%02d" % d for d in range(1, 11)]
    yr = year_returns(dates, [0.01] * 19)
    leg("partial years are printed with their own bar count",
        yr["2024"]["days"] == 9 and yr["2025"]["days"] == 10, str({y: v["days"] for y, v in yr.items()}))

    # the fill is the session AFTER the signal: a book that decides at the close cannot
    # transact at it, and a test that pairs decision and fill on the same day would pass
    # on an implementation that quietly buys at yesterday's price.
    oh = {"A": {"d1": {"open": 100.0, "close": 100.0, "hold": 1.0, "volume": 1.0},
                "d2": {"open": 110.0, "close": 111.0, "hold": 1.0, "volume": 1.0},
                "d3": {"open": 121.0, "close": 122.0, "hold": 1.0, "volume": 1.0},
                "d0": {"open": 50.0, "close": 99.0, "hold": 1.0, "volume": 1.0}}}
    ro, _ex = open_returns(["d0", "d1", "d2", "d3"], oh, {"d0": "A", "d1": "A", "d2": "A"})
    leg("open-to-open returns pair signal day with the NEXT session's open",
        len(ro) == 2 and abs(ro[0] - 0.10) < 1e-9 and abs(ro[1] - 0.10) < 1e-9, str(ro))
    leg("the fill day is not the signal day (50 -> 110 would be the wrong pairing)",
        abs(ro[0] - 1.2) > 1e-6, str(ro[0] if ro else None))

    # a gap keeps its sign when it is printed
    leg("a gap prints its sign", _sgn(-2.5) == "-2.50" and _sgn(2.5) == "+2.50", _sgn(-2.5))

    # the gap is gross of a dividend drift that belongs to the ETF, not to the futures
    rz = realizable_form("X", {"futures_ann_pct": 9.0, "etf_ann_pct": 1.0}, None, 2.5)
    leg("the net gap subtracts the dividend control from the gross gap",
        rz["gap_pp"] == 8.0 and rz["gap_net_of_dividend_pp"] == 5.5,
        "%s / %s" % (rz["gap_pp"], rz["gap_net_of_dividend_pp"]))
    rz0 = realizable_form("X", {"futures_ann_pct": 9.0, "etf_ann_pct": 1.0}, None, None)
    leg("an unread dividend control leaves the net gap blank, never equal to the gross one",
        rz0["gap_pp"] == 8.0 and rz0["gap_net_of_dividend_pp"] is None,
        str(rz0["gap_net_of_dividend_pp"]))
    leg("an unreadable basis face is not a measured zero drift",
        dividend_drift("IC", path=os.path.join(ROOT, "results", "__no_such_face__.json")) is None,
        str(dividend_drift("IC", path=os.path.join(ROOT, "results", "__no_such_face__.json"))))

    # the rendered page must carry the verdict words, not just the numbers
    fake = {"generated": "x", "evidence_cutoff": "2026-11-13", "criteria": CRITERIA,
            "book": {"status": "unavailable"}, "products": {}, "verdict": {}}
    page = render_md(fake)
    leg("the page prints the execution convention beside the close-to-close gap",
        "fill" in page and "gap after cost (measured median)" in page,
        "gap after cost (measured median)" if "gap after cost (measured median)" in page else page[:60])
    leg("the page names the missing book instead of printing zeros",
        "could not be rebuilt" in page, page.splitlines()[6][:60] if len(page.splitlines()) > 6 else "")

    # --- the caliber the carry column rides on (r1712) -------------------------------
    # A face whose two roll rulers disagree by 6.91 pp must print that spread and call the
    # single figure a choice; a face where they agree must NOT claim a choice exists.
    def _cal_rows(spread, pub=2.881, knd=9.793, missed=105, status="ok"):
        return {"IC": {"risk": {"ann_compound_pct": 12.041},
                       "roll_caliber": {"status": status, "published_ann_pct": pub,
                                        "calendar_ann_pct": knd, "spread_pp": spread,
                                        "missed_roll_days": missed}}}

    wide = "\n".join(caliber_block({"products": _cal_rows(6.912)}))
    leg("C1 the two rulers and their spread are printed off the face, not typed",
        "2.88" in wide and "9.79" in wide and "6.91" in wide and "105" in wide,
        wide.splitlines()[6][:80] if len(wide.splitlines()) > 6 else "")

    leg("C2 a wide spread is called a caliber choice, not a measurement",
        "caliber choice, not a measurement" in wide and "agree to within" not in wide,
        wide.splitlines()[-2][:70])

    narrow = "\n".join(caliber_block({"products": _cal_rows(0.24, pub=9.60, knd=9.84)}))
    leg("C3 rulers that agree must not be sold as a choice (flip side of C2)",
        "agree to within 0.24 pp" in narrow and "caliber choice" not in narrow,
        narrow.splitlines()[-2][:70])

    moved = "\n".join(caliber_block({"products": _cal_rows(6.912, pub=2.881, knd=14.00)}))
    leg("C4 a moved ruler moves the block (no stale sentence survives)",
        moved != wide and "14.00" in moved, "" if moved != wide else "identical output")

    unknown = "\n".join(caliber_block({"products": _cal_rows(None, status="unreadable")}))
    leg("C5 an unreadable ruler is unknown, never 'the rulers agree' or a zero spread",
        "unknown here" in unknown and "agree to within" not in unknown
        and "| ? |" in unknown, unknown.splitlines()[-2][:70])

    half = "\n".join(caliber_block({"products": _cal_rows(None, knd=None)}))
    leg("C6 a missing side keeps the spread unknown instead of borrowing the other",
        "spread is unknown rather than zero" in half and "| ? |" in half,
        half.splitlines()[-2][:70])

    absent = "\n".join(caliber_block({"products": {}}))
    leg("C7 a product with no row still gets a row and a stated unknown",
        absent.count("| ? |") == len(CRITERIA["products"]) and "unreadable" in absent,
        str(absent.count("| ? |")))

    own_is_not_the_ruler = "\n".join(caliber_block({"products": _cal_rows(6.912)}))
    leg("C8 the face's own carry and both rulers are three separate numbers",
        "12.04" in own_is_not_the_ruler and "this face" in own_is_not_the_ruler
        and "neither ruler below is this face's own treatment" in own_is_not_the_ruler,
        "")

    bad = sum(1 for _n, ok, _d in legs if not ok)
    for n, ok, d in legs:
        print("[%s] %s%s" % ("PASS" if ok else "FAIL", n, (" | " + d) if d else ""))
    print("selftest %d/%d" % (len(legs) - bad, len(legs)))
    return 0 if bad == 0 else 1


# ------------------------------------------------------------------ check
def check():
    if not os.path.isfile(OUT):
        print("check: receipt missing")
        return 1
    with open(OUT, "r", encoding="utf-8") as f:
        face = json.load(f)
    errs = []
    rows = (face.get("verdict") or {}).get("rows") or {}
    for prod, row in (face.get("products") or {}).items():
        if row.get("status"):
            continue
        r = row["risk"]
        # re-derive the two things a reader would act on
        if r.get("ann_vol_pct") is not None and r.get("sharpe") is not None and r["ann_vol_pct"] > 0:
            if abs(r["sharpe"] - r["ann_mean_pct"] / r["ann_vol_pct"]) > 1e-3:
                errs.append("%s: sharpe does not equal mean/vol" % prod)
        said = (rows.get(prod) or {}).get("verdict")
        if said != row.get("verdict"):
            errs.append("%s: verdict row disagrees with product row" % prod)
        if row.get("mdd_pct", 0) > 0:
            errs.append("%s: drawdown is positive" % prod)
        if row.get("days_dropped"):
            errs.append("%s: %s days dropped between contract and index"
                        % (prod, row["days_dropped"]))
    cands = sorted([p for p, r in (rows or {}).items() if r.get("verdict") == "SLEEVE_CANDIDATE"])
    if cands != (face.get("verdict") or {}).get("sleeve_candidates"):
        errs.append("candidate list not re-derived from rows")
    if errs:
        print("CHECK_FAIL: " + "; ".join(errs))
        return 1
    print("CHECK_OK: %d products re-derived, candidates=%s" % (len(rows), cands))
    return 0


# ------------------------------------------------------------------ main
def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run",
                    choices=["run", "selftest", "check", "render"])
    ap.add_argument("--write-doc", action="store_true")
    ap.add_argument("--checkdoc", action="store_true")
    ap.add_argument("--cache-dir", default=None)
    ap.add_argument("--no-book", action="store_true",
                    help="skip rebuilding the adopted book (fast, comparisons unavailable)")
    args = ap.parse_args(argv)

    if args.cmd == "selftest":
        return selftest()
    if args.cmd == "check":
        return check()
    if args.cmd == "render":
        with open(OUT, "r", encoding="utf-8") as f:
            face = json.load(f)
        if args.checkdoc:
            return checkdoc(face)
        print(render_md(face))
        return 0

    face = build(cache_dir=args.cache_dir, with_book=not args.no_book)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(face, f, ensure_ascii=False, indent=1, sort_keys=False)
        f.write("\n")
    if args.write_doc:
        write_doc(face)
    print("carry risk: cutoff=%s elapsed=%.1fs candidates=%s"
          % (face.get("evidence_cutoff"), face.get("elapsed_sec") or 0.0,
             (face.get("verdict") or {}).get("sleeve_candidates")))
    for prod, row in (face.get("products") or {}).items():
        if row.get("status"):
            print("  %s: %s" % (prod, row["status"]))
            continue
        a8 = row["at_vol_target"]
        print("  %s: carry %s%%/yr vol %s%% mdd %s%% | @8%%vol x%s -> %s%% (mdd %s%%)"
              " corr %s | %s"
              % (prod, _p(row["risk"].get("ann_compound_pct")),
                 _p(row["risk"].get("ann_vol_pct")), _p(row["risk"].get("mdd_pct")),
                 _p(a8.get("leverage"), 2), _p(a8.get("ann_compound_pct")),
                 _p(a8.get("mdd_pct")), _p(row.get("corr_with_book"), 3), row["verdict"]))
    if args.checkdoc:
        return checkdoc(face)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
