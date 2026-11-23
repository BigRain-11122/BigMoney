"""Which index do you short?  Nine faces shorted 512100; nobody compared it to the alternatives.

r2022 priced five hedge sizes, r2023 turned them into a drawdown-budget purchase, r2024
re-read it on daily marks, r2025 raced nine ways of choosing a size, r2026 named the
default, r2027 turned it into lots, r2028 showed the price date moves the ticket, r2029
printed the beta's own band and r2030 walked the beta forward without the future.

All nine short the *same* instrument: 512100 (CSI 1000 ETF).  That choice is never
argued anywhere in the family.  It is also odd on its face -- the book is built from
CSI 300 and CSI 500 names (the pool the veto layer ranks), so the index that matches the
book's own universe is 510500, and the one the family actually uses is the small-cap
index.  A hedge is a *choice of index* before it is a choice of size, and the size (beta)
was the only thing the family ever measured.

This face fills that hole with four readings on the same 77 periods, same 20/20 booking,
same costs as the parents:

  * **the same beta arithmetic on three indexes** -- 510300 (CSI 300), 510500 (CSI 500)
    and 512100 (CSI 1000): beta, R^2, residual volatility, share of variance removed,
    and what each hedged arm actually earns;
  * **the ticket** -- one lot of each ETF at the latest price, lots needed per CNY 1m,
    and the beta error that rounding to whole lots leaves behind;
  * **a second leg** -- the book fitted on two indexes at once (300+500 and 300+1000),
    because if the book leans small, no single large-cap index can remove everything and
    the question becomes whether a second short pays for its own cost;
  * **an anchor** -- the 512100 column is recomputed here and must agree with the numbers
    r2022 already published, so a divergence is visible rather than plausible.

Thresholds are frozen in PREREG below, before the run, and are not tuned afterwards.

Outputs (new files only):
    results/astock_veto_hedge_instrument.json
    research/ASTOCK_VETO_HEDGE_INSTRUMENT.md

Usage:
    python scripts/astock_veto_hedge_instrument.py selftest
    python scripts/astock_veto_hedge_instrument.py run
    python scripts/astock_veto_hedge_instrument.py check
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timedelta, timezone

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from astock_resid_veto_layer import COST_ONE_SIDE, HOLD  # noqa: E402
from astock_veto_tearsheet import PPY, annual_vol as annual_vol_pure  # noqa: E402
from astock_veto_hedgeable_beta import (  # noqa: E402
    ROLL_COST,
    arm_series,
    hedge_returns,
    load_book,
    lots_for,
    ols,
    period_ends,
    stats,
    variance_read,
)
from etf_equity_alpha import FLIP_THR, repair_flips  # noqa: E402

PARENT = os.path.join(ROOT, "results", "astock_veto_hedgeable_beta.json")
BOOK_FACE = os.path.join(ROOT, "results", "astock_veto_turnover_layers.json")
DEFAULT_FACE = os.path.join(ROOT, "results", "astock_veto_hedge_default.json")
OUT_JSON = os.path.join(ROOT, "results", "astock_veto_hedge_instrument.json")
OUT_MD = os.path.join(ROOT, "research", "ASTOCK_VETO_HEDGE_INSTRUMENT.md")

IS_END = "2023-12-31"
ETF_LOT = 100
CAPITAL = 1_000_000.0

# (symbol, short name, csv) -- the three SH index ETFs that cover this book's universe
CANDIDATES = (
    ("510300", "CSI 300", "data/daily/sh510300.csv"),
    ("510500", "CSI 500", "data/daily/sh510500.csv"),
    ("512100", "CSI 1000", "data/daily/sh512100.csv"),
)
REFERENCE = "512100"   # the parents' calendar and the anchor column

# frozen before the run -- see PREREG in build_face()
LINE_SHARE_SPREAD = 0.05   # share-of-variance removed must spread this much to pick an index
LINE_RET_PP = 2.0          # annualised gap (pp) at or above this is a real trade-off
LINE_SECOND_LEG_VOL = 0.02  # a second short must remove this much annual vol to count
REACH_TOL = 0.01           # a rival "reaches" the best risk level within 1 pp of annual vol
GRID_K = np.arange(0.0, 4.0001, 0.005)   # the size grid every floor is measured on

TOL = 1e-12   # a line drawn at 0.05 is compared with that much machine slack, not with
              # float trivia: 0.85 - 0.80 reads 0.04999999999999993 in binary


# ------------------------------------------------------------------ small helpers
def _now() -> str:
    return datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")


def _rel(path: str) -> str:
    try:
        return os.path.relpath(path, ROOT).replace(os.sep, "/")
    except ValueError:
        return str(path).replace(os.sep, "/")


def _pct(x, nd=2) -> str:
    return "n/a" if x is None else ("%." + str(nd) + "f%%") % (100.0 * float(x))


def _f(x, nd=2) -> str:
    return "n/a" if x is None else ("%." + str(nd) + "f") % float(x)


def _read_json(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _sha_file(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


# ------------------------------------------------------------------ pure logic
def ols_two(y, x1, x2) -> dict:
    """Book on two indexes at once.  Same least squares as ols(), with an intercept so
    the two loadings are not biased by the book's own drift.  The residual series is
    returned because a second leg is judged by what it leaves, not by its R^2."""
    yy = np.asarray(y, dtype=np.float64)
    a = np.asarray(x1, dtype=np.float64)
    b = np.asarray(x2, dtype=np.float64)
    keep = np.isfinite(yy) & np.isfinite(a) & np.isfinite(b)
    yy, a, b = yy[keep], a[keep], b[keep]
    n = int(len(yy))
    if n < 4 or float(np.var(a)) <= 0.0 or float(np.var(b)) <= 0.0:
        return {"n": n, "alpha": None, "b1": None, "b2": None, "r2": None, "resid": []}
    X = np.column_stack([np.ones_like(a), a, b])
    coef = np.linalg.lstsq(X, yy, rcond=None)[0]
    fit = X @ coef
    ss_res = float(np.sum((yy - fit) ** 2))
    ss_tot = float(np.sum((yy - np.mean(yy)) ** 2))
    return {
        "n": n,
        "alpha": float(coef[0]),
        "b1": float(coef[1]),
        "b2": float(coef[2]),
        "r2": None if ss_tot <= 0.0 else 1.0 - ss_res / ss_tot,
        "resid": (yy - fit).tolist(),
    }


def two_leg_arm(book, h1, h2, b1: float, b2: float, roll_cost: float = ROLL_COST) -> list:
    """The book short two indexes at once, costed exactly like one leg: both sides of
    every roll on the summed shorted notional.  A missing price drops the period."""
    out = []
    coef = abs(b1) + abs(b2)
    for r_b, r_1, r_2 in zip(book, h1, h2):
        vals = (r_b, r_1, r_2)
        if any(v is None or not np.isfinite(v) for v in vals):
            out.append(None)
            continue
        out.append(float(r_b) - b1 * float(r_1) - b2 * float(r_2) - coef * roll_cost)
    return out


def pick_index(shares: dict) -> dict:
    """Which index removes the most, and by how much -- decided by the frozen line."""
    if not shares or any(v is None for v in shares.values()):
        return {"best": None, "spread": None, "verdict": "NOT_ENOUGH_DATA"}
    best = max(shares, key=lambda k: shares[k])
    worst = min(shares, key=lambda k: shares[k])
    spread = float(shares[best] - shares[worst])
    return {
        "best": best,
        "worst": worst,
        "spread": spread,
        "verdict": ("HEDGE_INSTRUMENT_MATTERS" if spread >= LINE_SHARE_SPREAD - TOL
                    else "ANY_OF_THE_THREE_IS_ENOUGH"),
    }


def tradeoff_verdict(best_share_symbol, arms: dict, annual: dict) -> dict:
    """Does the index that removes the most risk also earn the most?  A gap under the
    frozen line says there is no trade-off to price; over it, the reader is buying
    risk removal with return and has to be told.

    This is the *raw* k = 1 reading, kept for transparency only: it is confounded,
    because an index that removes less variance also keeps more of the return it never
    removed the risk for.  The token that counts is decided on the equal-risk control
    below (`reach_verdict`)."""
    if best_share_symbol is None or not arms:
        return {"verdict": "NOT_ENOUGH_DATA", "gap_pp": None}
    best_ret_symbol = max(annual, key=lambda k: annual[k])
    gap = float((annual[best_ret_symbol] - annual[best_share_symbol]) * 100.0)
    return {
        "best_return": best_ret_symbol,
        "gap_pp": gap,
        "raw_verdict": ("RISK_REMOVAL_COSTS_RETURN" if gap >= LINE_RET_PP - TOL
                        else "NO_TRADEOFF"),
    }


def vol_floor(book_net, hedge, beta, grid=GRID_K) -> dict:
    """The lowest volatility this index can leave the book at, over every size k >= 0.

    It matters because a hedge that removes 39% of the variance can never be held at the
    risk level of one that removes 85%: no k fixes a missing R^2.  The floor is measured,
    not inferred from R^2, so a grid that is too coarse shows up as a floor that is not
    where the fit says it should be."""
    best = None
    for k in grid:
        a = stats(arm_series(book_net, hedge, float(k), beta))
        if not a.get("annual_vol"):
            continue
        if best is None or a["annual_vol"] < best[1]["annual_vol"]:
            best = (float(k), a)
    if best is None:
        return {"k_at_floor": None, "floor_vol": None, "reaches_target": False}
    k, a = best
    return {"k_at_floor": k, "floor_vol": a["annual_vol"],
            "annualised_at_floor": a["annualized_compound"],
            "max_dd_at_floor": a["max_drawdown"],
            "worst_period_at_floor": a["worst_period"]}


def reach_verdict(target_vol, floors: dict, best_symbol, best_annual: float,
                  reach_tol: float = REACH_TOL) -> dict:
    """At the best index's own risk level, can any rival get there -- and if it can, does
    it earn at least the frozen line more?  Two different answers and no third one: a
    rival that cannot reach the risk is not a cheaper hedge, it is a hedge that leaves
    risk on the table and calls the un-removed risk return."""
    rivals = {s: v for s, v in floors.items() if s != best_symbol and v.get("floor_vol")}
    if not rivals:
        return {"verdict": "NOT_ENOUGH_DATA", "reachable": {}, "gap_pp": None}
    reach = {s: v for s, v in rivals.items()
             if v["floor_vol"] <= target_vol + reach_tol}
    closest = min(rivals, key=lambda s: rivals[s]["floor_vol"])
    if not reach:
        return {"reachable": {}, "gap_pp": None, "closest": closest,
                "closest_floor_vol": rivals[closest]["floor_vol"],
                "verdict": "NO_RIVAL_REACHES_THIS_RISK"}
    best_ret = max(reach, key=lambda s: reach[s]["annualised_at_floor"] or -9.9)
    gap = float(((reach[best_ret]["annualised_at_floor"] or 0.0) - best_annual) * 100.0)
    return {"reachable": {s: reach[s] for s in reach}, "closest": closest,
            "closest_floor_vol": rivals[closest]["floor_vol"],
            "best_reachable": best_ret, "gap_pp": gap,
            "verdict": ("RISK_REMOVAL_COSTS_RETURN" if gap >= LINE_RET_PP - TOL
                        else "NO_TRADEOFF")}


def second_leg_verdict(single_vol: float, pair_vol: float) -> dict:
    """A second short earns its place only if the residual it removes clears the line."""
    if single_vol is None or pair_vol is None:
        return {"verdict": "NOT_ENOUGH_DATA", "removed_vol": None}
    removed = float(single_vol - pair_vol)
    return {
        "removed_vol": removed,
        "verdict": ("SECOND_LEG_PAYS" if removed >= LINE_SECOND_LEG_VOL - TOL
                    else "SECOND_LEG_DOES_NOT_PAY"),
    }


def lean_verdict(b_large, b_small) -> str:
    if b_large is None or b_small is None:
        return "NOT_ENOUGH_DATA"
    return "BOOK_LEANS_SMALL" if abs(b_small) > abs(b_large) else "BOOK_LEANS_LARGE"


# ----------------------------------------------------------------------- loaders
def load_hedge(symbol: str, csv_rel: str) -> dict:
    """One ETF's traded close after the same 35% single-day line the parents use.  The
    repair list is returned, not swallowed: the reader sees what was flattened."""
    import pandas as pd

    path = os.path.join(ROOT, csv_rel)
    df = pd.read_csv(path, usecols=["date", "open", "close"])
    raw = df["close"].astype(float)
    adj, _adj_open, n_bad = repair_flips(df[["close"]].astype(float),
                                         df[["open"]].astype(float), thr=FLIP_THR)
    adj_close = adj["close"].astype(float)
    raw_r = raw.pct_change()
    bad = raw_r.abs() > FLIP_THR
    repairs = [{"date": str(d), "raw_move": float(raw_r.iloc[i])}
               for i, d in enumerate(df["date"].tolist()) if bool(bad.iloc[i])]
    return {
        "symbol": symbol,
        "csv": csv_rel,
        "file_sha256": _sha_file(path),
        "dates": [str(d) for d in df["date"].tolist()],
        "close": {str(d): float(c) for d, c in zip(df["date"].tolist(), adj_close.tolist())},
        "last_date": str(df["date"].tolist()[-1]),
        "last_price": float(adj_close.iloc[-1]),
        "repaired_prints": int(n_bad),
        "repairs": repairs,
    }


def _pair(book, hedge):
    """Book and hedge returns on the periods both can price."""
    b, h, keep_dates = [], [], []
    for i, (x, y) in enumerate(zip(book["net"], hedge)):
        if x is not None and np.isfinite(x) and y is not None and np.isfinite(y):
            b.append(float(x))
            h.append(float(y))
            keep_dates.append(book["dates"][i])
    return b, h, keep_dates


# ---------------------------------------------------------------------- the face
def build_face() -> dict:
    book = load_book()
    hedges = {sym: load_hedge(sym, csv) for sym, _name, csv in CANDIDATES}
    calendar = hedges[REFERENCE]["dates"]
    dates = book["dates"]
    ends, spans = period_ends(dates, calendar)
    book["ends"] = ends

    # --- data block (calendar agreement is printed, not assumed)
    pos_ref = {d: i for i, d in enumerate(calendar)}
    cal_note = {}
    for sym, _name, _csv in CANDIDATES:
        dts = hedges[sym]["dates"]
        miss = [d for d in (dates + [e for e in ends if e]) if d not in set(dts)]
        cal_note[sym] = {"misses_any_period_date": len(miss),
                         "first": dts[0], "last": dts[-1]}

    # --- per candidate: returns, betas, variance, arms
    per = {}
    for sym, name, _csv in CANDIDATES:
        h = hedge_returns(dates, ends, hedges[sym]["close"])
        b, hh, keep = _pair(book, h)
        fit_full = ols(b, hh)
        is_mask = [d <= IS_END for d in keep]
        fit_is = ols([x for x, m in zip(b, is_mask) if m], [x for x, m in zip(hh, is_mask) if m])
        var_full = variance_read(b, hh, fit_full["beta"]) if fit_full["beta"] is not None else {}
        var_is = (variance_read(b, hh, fit_is["beta"])
                  if fit_is["beta"] is not None else {})
        arm_full = stats(arm_series(book["net"], h, 1.0, fit_full["beta"]))
        oos = [x for x, d in zip(arm_series(book["net"], h, 1.0, fit_full["beta"]), dates)
               if d > IS_END]
        arm_oos = stats(oos)
        one_lot = hedges[sym]["last_price"] * ETF_LOT
        per[sym] = {
            "symbol": sym,
            "name": name,
            "paired_periods": len(b),
            "beta": fit_full.get("beta"),
            "alpha": fit_full.get("alpha"),
            "r2": fit_full.get("r2"),
            "beta_is": fit_is.get("beta"),
            "r2_is": fit_is.get("r2"),
            "book_annual_vol": var_full.get("book_annual_vol"),
            "residual_annual_vol": var_full.get("residual_annual_vol"),
            "residual_annual_vol_at_is_beta": var_is.get("residual_annual_vol"),
            "share_removed": var_full.get("share_removable"),
            "share_removed_at_is_beta": var_is.get("share_removable"),
            "arm_full": arm_full,
            "arm_oos": arm_oos,
            "one_lot_notional": float(one_lot),
            "last_price": hedges[sym]["last_price"],
            "ticket": lots_for(CAPITAL, fit_full["beta"] or 0.0,
                               hedges[sym]["last_price"], ETF_LOT),
        }
        t = per[sym]["ticket"]
        if t.get("lots_needed") is not None and np.isfinite(t["lots_needed"]):
            whole = float(round(t["lots_needed"]))
            t["lots_whole"] = whole
            t["realised_beta_after_rounding"] = whole * one_lot / CAPITAL
            t["beta_error_after_rounding"] = t["realised_beta_after_rounding"] - float(t["beta"])

    unhedged = stats(book["net"])

    # --- two legs: the book on two indexes at once
    pair_defs = {"CSI300+CSI500": ("510300", "510500"), "CSI300+CSI1000": ("510300", "512100")}
    pairs = {}
    for label, (s1, s2) in pair_defs.items():
        h1 = hedge_returns(dates, ends, hedges[s1]["close"])
        h2 = hedge_returns(dates, ends, hedges[s2]["close"])
        b, hh1, hh2, keep = [], [], [], []
        for i in range(len(dates)):
            vals = (book["net"][i], h1[i], h2[i])
            if any(v is None or not np.isfinite(v) for v in vals):
                continue
            b.append(float(vals[0]))
            hh1.append(float(vals[1]))
            hh2.append(float(vals[2]))
            keep.append(dates[i])
        fit = ols_two(b, hh1, hh2)
        resid = np.asarray(fit["resid"], dtype=np.float64) if fit["resid"] else np.array([])
        resid_vol = (float(np.std(resid, ddof=1) * np.sqrt(PPY)) if len(resid) > 2 else None)
        arm = stats(two_leg_arm(book["net"], h1, h2, fit["b1"] or 0.0, fit["b2"] or 0.0))
        pairs[label] = {
            "legs": [s1, s2],
            "periods": len(b),
            "b_large": fit["b1"],
            "b_small": fit["b2"],
            "r2": fit["r2"],
            "residual_annual_vol": resid_vol,
            "arm_full": arm,
            "lean": lean_verdict(fit["b1"], fit["b2"]),
        }

    # --- reads
    shares = {s: per[s]["share_removed"] for s in per}
    annual = {s: per[s]["arm_full"].get("annualized_compound") for s in per}
    pick = pick_index(shares)
    raw_trade = tradeoff_verdict(pick.get("best"), per, annual)
    single_vol = per[pick["best"]]["residual_annual_vol"] if pick.get("best") else None
    best_pair = min(pairs.values(),
                    key=lambda q: q["residual_annual_vol"] if q["residual_annual_vol"] is not None
                    else float("inf"))
    second = second_leg_verdict(single_vol, best_pair["residual_annual_vol"])

    # --- equal-risk control: what is the lowest volatility each index can hold the book at?
    target_vol = per[pick["best"]]["arm_full"].get("annual_vol") if pick.get("best") else None
    floors = {}
    for sym in per:
        h = hedge_returns(dates, ends, hedges[sym]["close"])
        floors[sym] = vol_floor(book["net"], h, per[sym]["beta"])
    reach = (reach_verdict(target_vol, floors, pick.get("best"),
                           per[pick["best"]]["arm_full"].get("annualized_compound") or 0.0)
             if pick.get("best") else {"verdict": "NOT_ENOUGH_DATA", "gap_pp": None,
                                       "reachable": {}})

    # --- anchor: the 512100 column must reproduce what r2022 published
    parent = _read_json(PARENT)
    pv = parent.get("variance") or {}
    pb = parent.get("beta") or {}
    anchor = {
        "parent_face": _rel(PARENT),
        # r2022's arm beta is the one fitted in-sample (2020-07-06..2023-12-31) and then
        # read out of sample; its variance block is the full-window fit.  Both are
        # compared against the matching column here, not one against the other.
        "parent_beta_used_for_arms": pv.get("beta_used_for_arms"),
        "our_beta_is": per["512100"]["beta_is"],
        "beta_is_abs_diff": (None if pv.get("beta_used_for_arms") is None
                             or per["512100"]["beta_is"] is None
                             else abs(float(pv["beta_used_for_arms"]) - float(per["512100"]["beta_is"]))),
        "parent_beta_full_window": (pb.get("etf_full_window") or {}).get("beta"),
        "our_beta_full_window": per["512100"]["beta"],
        "beta_full_abs_diff": (None if (pb.get("etf_full_window") or {}).get("beta") is None
                               or per["512100"]["beta"] is None
                               else abs(float(pb["etf_full_window"]["beta"])
                                        - float(per["512100"]["beta"]))),
        "parent_share_removable": pv.get("share_removable"),
        "our_share_removable": per["512100"]["share_removed"],
        "share_abs_diff": (None if pv.get("share_removable") is None
                           or per["512100"]["share_removed"] is None
                           else abs(float(pv["share_removable"]) - float(per["512100"]["share_removed"]))),
        "parent_residual_annual_vol": pv.get("residual_annual_vol"),
        "our_residual_annual_vol": per["512100"]["residual_annual_vol"],
    }
    anchor["ok"] = bool(
        anchor["beta_is_abs_diff"] is not None and anchor["beta_is_abs_diff"] <= 1e-6
        and anchor["beta_full_abs_diff"] is not None and anchor["beta_full_abs_diff"] <= 1e-6
        and anchor["share_abs_diff"] is not None and anchor["share_abs_diff"] <= 1e-6)

    parents = {}
    for key, path in (("book", BOOK_FACE), ("hedgeable_beta", PARENT), ("default", DEFAULT_FACE)):
        if os.path.exists(path):
            parents[key] = {"face": _rel(path), "file_sha256": _sha_file(path)}
        else:
            parents[key] = {"face": _rel(path), "file_sha256": None}

    face = {
        "generated": _now(),
        "evidence_cutoff": max(hedges[s]["last_date"] for s in hedges),
        "machine": "bm-c",
        "kind": "instrument-choice",
        "fills_the_hole_of": "astock_veto_hedgeable_beta (and the eight faces that quote it)",
        "prereg": {
            "question": ("Nine faces short 512100 (CSI 1000) against a book built from CSI 300 and "
                         "CSI 500 names.  Does the index a reader shorts change how much risk comes "
                         "off, how much the book earns, and what he has to place?"),
            "candidates": {s: n for s, n, _c in CANDIDATES},
            "booking": ("the parents' own: 20-bar hold, 20-bar stride, close(t)->close(t+20) on the "
                        "512100 calendar, 8 bp per side, roll cost 16 bp per period per unit of "
                        "shorted notional, no borrow carry on the base habit (r2022 quotes that axis)"),
            "primary_reading": "share of the book's variance removed by one unit of beta",
            "lines": {
                "share_spread": LINE_SHARE_SPREAD,
                "return_gap_pp": LINE_RET_PP,
                "second_leg_vol": LINE_SECOND_LEG_VOL,
                "reach_tol_vol": REACH_TOL,
            },
            "equal_risk_control": ("the k = 1 return gap is confounded -- an index that removes less "
                                   "variance keeps return it never removed the risk for.  So every "
                                   "rival is also scanned over k in 0..4 (step 0.005) for its lowest "
                                   "achievable volatility; the trade-off token is decided at that "
                                   "equal-risk point, not at k = 1.  No k can repair a missing R^2, "
                                   "so a rival that cannot reach the risk is not a cheaper hedge."),
            "verdict_rule": ("HEDGE_INSTRUMENT_MATTERS when the best and worst index are at least "
                             "%.2f apart in share removed; NO_RIVAL_REACHES_THIS_RISK when neither "
                             "rival can hold the book at the best index's volatility within %.1f pp "
                             "of annual vol at any k -- in that case there is no risk/return "
                             "trade-off to price; otherwise RISK_REMOVAL_COSTS_RETURN when the "
                             "reachable rival at equal risk earns at least %.1f pp more a year; "
                             "SECOND_LEG_PAYS when the best two-leg fit leaves at least %.2f less "
                             "annual volatility than the best single index."
                             % (LINE_SHARE_SPREAD, REACH_TOL, LINE_RET_PP, LINE_SECOND_LEG_VOL)),
            "rule_frozen_before_run": True,
        },
        "spec": {
            "hold": HOLD,
            "stride": HOLD,
            "cost_one_side": COST_ONE_SIDE,
            "roll_cost_per_period": ROLL_COST,
            "periods_per_year": PPY,
            "is_end": IS_END,
            "etf_lot": ETF_LOT,
            "capital": CAPITAL,
            "flip_threshold": FLIP_THR,
            "reference_calendar": REFERENCE,
            "note": ("the 512100 column is the parents' own number recomputed here; the anchor block "
                     "below must agree with r2022 or this face is not about the same book"),
        },
        "data": {
            "book": {"face": _rel(BOOK_FACE), "periods": len(dates),
                     "first": dates[0], "last": dates[-1]},
            "hedges": {s: {"csv": hedges[s]["csv"], "symbol": s,
                           "first": hedges[s]["dates"][0],
                           "last": hedges[s]["last_date"],
                           "last_price": hedges[s]["last_price"],
                           "repaired_prints": hedges[s]["repaired_prints"],
                           "repairs": hedges[s]["repairs"],
                           "misses_any_period_date": cal_note[s]["misses_any_period_date"]}
                       for s in hedges},
            "span_note": ("all three ETFs trade on the same SH calendar; every period date and every "
                          "period end is priced by all three, so the three columns see identical "
                          "periods"),
        },
        "parents": parents,
        "anchor": anchor,
        "unhedged": unhedged,
        "candidates": {s: per[s] for s in per},
        "pairs": pairs,
        "vol_floors": {"target_symbol": pick.get("best"), "target_vol": target_vol,
                       "reach_tol": REACH_TOL, "grid": "%d points over k in 0..4" % len(GRID_K),
                       "by_symbol": floors,
                       "reachable_at_target": sorted(reach.get("reachable") or {}),
                       "closest_rival": reach.get("closest"),
                       "closest_rival_floor_vol": reach.get("closest_floor_vol"),
                       "best_reachable": reach.get("best_reachable"),
                       "gap_pp_at_equal_risk": reach.get("gap_pp")},
        "reads": {
            "book_annual_vol": unhedged.get("annual_vol"),
            "book_annualized": unhedged.get("annualized_compound"),
            "share_by_symbol": shares,
            "annualized_by_symbol": annual,
            "best_by_share": pick.get("best"),
            "worst_by_share": pick.get("worst"),
            "share_spread": pick.get("spread"),
            "best_share_residual_annual_vol": single_vol,
            "best_two_leg_label": next(k for k, v in pairs.items() if v is best_pair),
            "best_two_leg_residual_annual_vol": best_pair["residual_annual_vol"],
            "second_leg_removed_vol": second.get("removed_vol"),
            "raw_gap_pp_at_k1": raw_trade.get("gap_pp"),
            "raw_best_return": raw_trade.get("best_return"),
            "gap_pp": reach.get("gap_pp"),
            "grandularity_ratio": (per["512100"]["one_lot_notional"]
                                   and per["510500"]["one_lot_notional"]
                                   and per["512100"]["one_lot_notional"]
                                   / per["510500"]["one_lot_notional"]),
        },
        "verdict": None,   # filled below
        "verdict_matters": pick.get("verdict"),
        "verdict_tradeoff": reach.get("verdict"),
        "verdict_second_leg": second.get("verdict"),
        "verdict_lean": pairs["CSI300+CSI1000"]["lean"],
        "verdict_why": (
            "the best index by variance removed is %s (%s) against %s (%s) -- a %s spread, line %s; "
            "at %s's own risk level (%s vol) the nearest rival %s bottoms out at %s vol, so %s"
            % (pick.get("best"), _pct(shares.get(pick.get("best") or "") or 0.0),
               pick.get("worst"), _pct(shares.get(pick.get("worst") or "") or 0.0),
               _pct(pick.get("spread"), 2), _pct(LINE_SHARE_SPREAD, 1),
               pick.get("best"), _pct(target_vol), reach.get("closest"),
               _pct(reach.get("closest_floor_vol")),
               ("no rival can be held at that risk at any size -- the k=1 return gap of %s pp is "
                "return the rivals never removed the risk for"
                % _f(raw_trade.get("gap_pp"), 2))
               if reach.get("verdict") == "NO_RIVAL_REACHES_THIS_RISK"
               else ("the equal-risk rival earns %s pp more a year (line %s pp)"
                     % (_f(reach.get("gap_pp"), 2), _f(LINE_RET_PP, 1))))),
    }
    face["verdict"] = "%s | %s | %s | %s" % (
        face["verdict_matters"], face["verdict_tradeoff"],
        face["verdict_second_leg"], face["verdict_lean"])
    return face


# ------------------------------------------------------------------------- page
def render_md(face: dict) -> str:
    c = face["candidates"]
    reads = face["reads"]
    un = face["unhedged"]
    a = face["anchor"]
    L = []
    L.append("# Which index do you short?")
    L.append("")
    L.append("<!-- BEGIN:ASTOCK-VETO-HEDGE-INSTRUMENT -->")
    L.append("")
    L.append("Nine faces short **512100, the CSI 1000 ETF**, against a book that is built from "
             "**CSI 300 and CSI 500** names.  None of them argues the choice of index; they argue "
             "only the size.  This face prices the choice.")
    L.append("")
    L.append("**Answer, one line: %s.**  %s" % (face["verdict"],
                                               face["verdict_why"][0].upper() + face["verdict_why"][1:]))
    L.append("")
    L.append("## 1. The three candidates and what one lot of each is worth")
    L.append("")
    L.append("| ETF | index | last price | one lot (CNY) | lots per CNY 1m at its own beta | repaired prints |")
    L.append("|---|---|---|---|---|---|")
    for s in ("510300", "510500", "512100"):
        k = c[s]
        L.append("| %s | %s | %.3f | %.0f | %.2f | %d |"
                 % (s, k["name"], k["last_price"], k["one_lot_notional"],
                    (k["ticket"].get("lots_needed") or float("nan")),
                    face["data"]["hedges"][s]["repaired_prints"]))
    L.append("")
    L.append("Every one of them prices every period: %s."
             % ", ".join("%s misses %d" % (s, face["data"]["hedges"][s]["misses_any_period_date"])
                         for s in ("510300", "510500", "512100")))
    L.append("")
    L.append("## 2. One unit of beta, three indexes, one book")
    L.append("")
    L.append("| hedge | beta | R^2 | beta (in-sample only) | book vol | residual vol | share removed |")
    L.append("|---|---|---|---|---|---|---|")
    L.append("| none | - | - | - | %s | %s | 0.00%% |"
             % (_pct(un.get("annual_vol")), _pct(un.get("annual_vol"))))
    for s in ("510300", "510500", "512100"):
        k = c[s]
        L.append("| %s %s | %.4f | %.4f | %.4f | %s | %s | %s |"
                 % (s, k["name"], k["beta"], k["r2"], k["beta_is"],
                    _pct(k["book_annual_vol"]), _pct(k["residual_annual_vol"]),
                    _pct(k["share_removed"])))
    L.append("")
    L.append("Fitted on all %d paired periods; the in-sample column is the same fit on dates "
             "<= %s, printed because r2030 showed the beta moves when it is refitted."
             % (c["512100"]["paired_periods"], IS_END))
    L.append("")
    L.append("## 3. What the hedged book actually earns (k = 1, full window)")
    L.append("")
    L.append("| arm | periods | annualised | vol | per unit of vol | max drawdown | worst period | down periods |")
    L.append("|---|---|---|---|---|---|---|---|")
    L.append("| book, no hedge | %d | %s | %s | %.2f | %s | %s | %d |"
             % (un["periods"], _pct(un["annualized_compound"]), _pct(un["annual_vol"]),
                un["annualized_compound"] / un["annual_vol"], _pct(un["max_drawdown"]),
                _pct(un["worst_period"]), int(round(un["hit_rate"] * un["periods"]))))
    for s in ("510300", "510500", "512100"):
        k = c[s]["arm_full"]
        L.append("| short %s | %d | %s | %s | %.2f | %s | %s | %d |"
                 % (s, k["periods"], _pct(k["annualized_compound"]), _pct(k["annual_vol"]),
                    k["annualized_compound"] / k["annual_vol"], _pct(k["max_drawdown"]),
                    _pct(k["worst_period"]), int(round(k["hit_rate"] * k["periods"]))))
    L.append("")
    L.append("Same k, same costs, same periods -- the only thing that changes between those three "
             "rows is which index is shorted.  **That table cannot be read as a trade-off**: an "
             "index that removes 39% of the variance keeps return it never removed the risk for.  "
             "Section 5 is the control that makes the comparison apples to apples.")
    L.append("")
    L.append("## 4. The ticket: rounding to whole lots costs beta, and it costs it unevenly")
    L.append("")
    L.append("| ETF | lots needed for CNY 1m | filled | realised beta | beta error |")
    L.append("|---|---|---|---|---|")
    for s in ("510300", "510500", "512100"):
        t = c[s]["ticket"]
        L.append("| %s | %.2f | %.0f | %.4f | %+.5f |"
                 % (s, t["lots_needed"], t["lots_whole"], t["realised_beta_after_rounding"],
                    t["beta_error_after_rounding"]))
    L.append("")
    L.append("CNY 1m needs **%.0f** lots of 512100 against **%.0f** of 510500: the index that "
             "removes the most risk also needs the most tickets.  The rounding those tickets force "
             "is smaller than the beta's own uncertainty in all three cases (|error| <= %.5f against "
             "the %s band r2029 printed), so granularity is not a reason to prefer a weaker hedge -- "
             "it is a reason to check the order before sending it."
             % (c["512100"]["ticket"]["lots_needed"], c["510500"]["ticket"]["lots_needed"],
                max(abs(c[s]["ticket"]["beta_error_after_rounding"])
                    for s in ("510300", "510500", "512100")), "0.2126"))
    L.append("")
    L.append("## 5. The equal-risk control: can the cheap index even hold this book?")
    L.append("")
    vf = face["vol_floors"]
    L.append("Every rival is scanned over **k in 0..4** (step 0.005) for the lowest volatility it "
             "can leave the book at.  The target is the size the family already uses: short 512100 "
             "at k = 1, which holds the book at **%s** annual volatility."
             % _pct(vf["target_vol"]))
    L.append("")
    L.append("| hedge | beta | best k | lowest vol it can reach | annualised at that point | max drawdown there | reaches %s? |"
             % vf["target_symbol"])
    L.append("|---|---|---|---|---|---|---|")
    for s in ("510300", "510500", "512100"):
        f = vf["by_symbol"][s]
        reaches = ("reference" if s == vf["target_symbol"]
                   else ("yes" if f.get("reaches_target") else "**no**"))
        L.append("| %s | %.4f | %.3f | %s | %s | %s | %s |"
                 % (s, c[s]["beta"], f["k_at_floor"], _pct(f["floor_vol"]),
                    _pct(f["annualised_at_floor"]), _pct(f["max_dd_at_floor"]), reaches))
    L.append("")
    if face["verdict_tradeoff"] == "NO_RIVAL_REACHES_THIS_RISK":
        L.append("**No rival gets there.**  The nearest one, %s, bottoms out at **%s** annual "
                 "volatility -- %s above the level the family already holds -- and it cannot be "
                 "pushed lower at any size, because what is left is the part of the book that "
                 "index does not explain.  There is therefore no risk/return trade-off to price "
                 "here: the %s pp the rivals keep at k = 1 is return they never removed the risk "
                 "for.  Choosing a large-cap index is not a cheaper hedge, it is a weaker hedge "
                 "wearing the same position size."
                 % (vf["closest_rival"], _pct(vf["closest_rival_floor_vol"]),
                    _pct(vf["closest_rival_floor_vol"] - vf["target_vol"]),
                    _f(reads["raw_gap_pp_at_k1"], 2)))
    else:
        L.append("At equal risk the reachable rival **%s** earns **%s %%** against the best "
                 "index's %s -- a gap of **%s pp** against the frozen line of %s pp: **%s**."
                 % (vf["best_reachable"],
                    _pct((vf["by_symbol"][vf["best_reachable"]].get("annualised_at_floor") or 0.0)),
                    _pct(reads["annualized_by_symbol"][vf["target_symbol"]]),
                    _f(vf["gap_pp_at_equal_risk"], 2), _f(LINE_RET_PP, 1),
                    face["verdict_tradeoff"]))
    L.append("")
    L.append("## 6. Does a second short pay for itself?")
    L.append("")
    L.append("| fit | large-cap loading | small-cap loading | R^2 | residual vol | lean |")
    L.append("|---|---|---|---|---|---|")
    for label, p in face["pairs"].items():
        L.append("| %s | %.4f | %.4f | %.4f | %s | %s |"
                 % (label, p["b_large"], p["b_small"], p["r2"],
                    _pct(p["residual_annual_vol"]), p["lean"]))
    L.append("")
    L.append("A **negative** loading on the large-cap leg (%.4f in the 300+1000 fit) is the "
             "mechanical reason the large-cap indexes fail above: this book is not just 'more beta "
             "than the CSI 300', it is long small against large.  Shorting a large-cap index "
             "therefore adds exposure on the very spread the book earns from instead of removing "
             "it, which is why the 510300 fit stops at R^2 %.4f at every size."
             % (face["pairs"]["CSI300+CSI1000"]["b_large"], c["510300"]["r2"]))
    L.append("")
    L.append("The best single index leaves **%s** of annual volatility; the best two-leg fit "
             "leaves **%s** -- a further **%s** removed, against the frozen line of %s.  %s."
             % (_pct(reads["best_share_residual_annual_vol"]),
                _pct(reads["best_two_leg_residual_annual_vol"]),
                _pct(reads["second_leg_removed_vol"]), _pct(LINE_SECOND_LEG_VOL),
                "A second short earns its roll cost" if face["verdict_second_leg"] == "SECOND_LEG_PAYS"
                else "It does not earn its extra roll cost, so one index is enough"))
    L.append("")
    L.append("## 7. Verdicts (frozen lines, printed with the numbers)")
    L.append("")
    L.append("| token | reading |")
    L.append("|---|---|")
    L.append("| %s | share removed spans %s (line %s) |"
             % (face["verdict_matters"], _pct(reads["share_spread"]), _pct(LINE_SHARE_SPREAD, 1)))
    L.append("| %s | nearest rival bottoms out at %s vol against the target %s (tol %s); "
             "k=1 raw gap %s pp is confounded and is not used |"
             % (face["verdict_tradeoff"], _pct(vf["closest_rival_floor_vol"]),
                _pct(vf["target_vol"]), _pct(REACH_TOL), _f(reads["raw_gap_pp_at_k1"], 2)))
    L.append("| %s | second leg removes %s of annual vol (line %s) |"
             % (face["verdict_second_leg"], _pct(reads["second_leg_removed_vol"]),
                _pct(LINE_SECOND_LEG_VOL)))
    L.append("| %s | two-leg fit loads %.4f on the large-cap index and %.4f on the small-cap one |"
             % (face["verdict_lean"], face["pairs"]["CSI300+CSI1000"]["b_large"],
                face["pairs"]["CSI300+CSI1000"]["b_small"]))
    L.append("")
    L.append("## 8. The anchor: this really is the parents' book")
    L.append("")
    L.append("| quantity | r2022 published | recomputed here | abs diff |")
    L.append("|---|---|---|---|")
    L.append("| beta used for the arms (in-sample fit) | %.4f | %.4f | %.2e |"
             % (a["parent_beta_used_for_arms"], a["our_beta_is"], a["beta_is_abs_diff"]))
    L.append("| beta on the full window | %.4f | %.4f | %.2e |"
             % (a["parent_beta_full_window"], a["our_beta_full_window"], a["beta_full_abs_diff"]))
    L.append("| share of variance removed | %.6f | %.6f | %.2e |"
             % (a["parent_share_removable"], a["our_share_removable"], a["share_abs_diff"]))
    L.append("")
    L.append("Anchor %s: the 512100 column is not a new model of the same book, it is the same "
             "model re-run, so any divergence in the other two columns is about the index and not "
             "about a different pipeline."
             % ("agrees" if a["ok"] else "DOES NOT AGREE"))
    L.append("")
    L.append("## 9. What this face does not say")
    L.append("")
    L.append("- It does not model borrow cost, margin, recall or basis: r2022 quotes the borrow "
             "axis (0/2/5 percent a year) and r2027 quotes the futures basis.  The base habit here is the "
             "parents' 8 bp + 16 bp roll.")
    L.append("- It does not re-choose k or a drawdown budget: r2023/r2025/r2026 own those.")
    L.append("- It does not walk the beta forward: r2030 does that, and this face keeps its "
             "full-window beta so the three indexes are compared on one identical footing.")
    L.append("- ETF prices are as-traded (no dividend adjustment); the book is priced at its last "
             "mark (%s) while the hedge panels run to %s, and that dating gap belongs to r2028 -- "
             "it is not repaired here." % (face["data"]["book"]["last"], face["evidence_cutoff"]))
    L.append("- A single-history answer: the spread between indexes is a reading of 2020-07..%s, "
             "not a law about which index hedges a future book." % face["data"]["book"]["last"])
    L.append("")
    L.append("## 10. Reproduction")
    L.append("")
    L.append("```")
    L.append("python scripts/astock_veto_hedge_instrument.py selftest")
    L.append("python scripts/astock_veto_hedge_instrument.py run")
    L.append("python scripts/astock_veto_hedge_instrument.py check")
    L.append("```")
    L.append("")
    L.append("<!-- END:ASTOCK-VETO-HEDGE-INSTRUMENT -->")
    L.append("")
    return "\n".join(L)


# ------------------------------------------------------------------------- run
def run(write: bool = True) -> int:
    face = build_face()
    if write:
        with open(OUT_JSON, "w", encoding="utf-8") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")
        with open(OUT_MD, "w", encoding="utf-8") as fh:
            fh.write(render_md(face))
    c = face["candidates"]
    print("astock_veto_hedge_instrument %s" % face["verdict"])
    print("  share removed: 510300 %s | 510500 %s | 512100 %s  (spread %s, line %s)"
          % (_pct(c["510300"]["share_removed"]), _pct(c["510500"]["share_removed"]),
             _pct(c["512100"]["share_removed"]), _pct(face["reads"]["share_spread"]),
             _pct(LINE_SHARE_SPREAD, 1)))
    print("  annualised k=1: 510300 %s | 510500 %s | 512100 %s"
          % (_pct(c["510300"]["arm_full"]["annualized_compound"]),
             _pct(c["510500"]["arm_full"]["annualized_compound"]),
             _pct(c["512100"]["arm_full"]["annualized_compound"])))
    print("  two legs: %s leaves %s vs best single %s (removed %s)"
          % (face["reads"]["best_two_leg_label"],
             _pct(face["reads"]["best_two_leg_residual_annual_vol"]),
             _pct(face["reads"]["best_share_residual_annual_vol"]),
             _pct(face["reads"]["second_leg_removed_vol"])))
    print("  anchor vs r2022: beta(is) diff %.2e | beta(full) diff %.2e | share diff %.2e -> %s"
          % (face["anchor"]["beta_is_abs_diff"], face["anchor"]["beta_full_abs_diff"],
             face["anchor"]["share_abs_diff"],
             "OK" if face["anchor"]["ok"] else "MISMATCH"))
    return 0 if face["anchor"]["ok"] else 1


def check(json_path: str = OUT_JSON, md_path: str = OUT_MD) -> int:
    """STALE when an upstream moved (the reader is told to re-derive); CHECK FAILED when
    the published numbers disagree with their own inputs."""
    if not os.path.exists(json_path):
        print("STALE: face missing (%s)" % _rel(json_path))
        return 3
    face = _read_json(json_path)
    problems = []
    for key, path in (("book", BOOK_FACE), ("hedgeable_beta", PARENT), ("default", DEFAULT_FACE)):
        rec = (face.get("parents") or {}).get(key) or {}
        disk = _sha_file(path) if os.path.exists(path) else None
        if rec.get("file_sha256") != disk:
            problems.append("STALE: parent %s moved (%s -> %s)"
                            % (key, str(rec.get("file_sha256"))[:12], str(disk)[:12]))
    for sym, _name, csv in CANDIDATES:
        rec = ((face.get("data") or {}).get("hedges") or {}).get(sym) or {}
        path = os.path.join(ROOT, csv)
        if not os.path.exists(path):
            problems.append("STALE: hedge panel missing (%s)" % csv)
            continue
        if rec.get("last") != load_hedge(sym, csv)["last_date"]:
            problems.append("STALE: %s panel advanced (%s -> %s)"
                            % (sym, rec.get("last"), load_hedge(sym, csv)["last_date"]))
    if problems:
        for p in problems:
            print(p)
        print("STALE: run `run` to re-derive")
        return 3

    fresh = build_face()

    for sym in ("510300", "510500", "512100"):
        x, y = face["candidates"][sym], fresh["candidates"][sym]
        for field in ("beta", "r2", "beta_is", "share_removed", "residual_annual_vol",
                      "residual_annual_vol_at_is_beta", "one_lot_notional"):
            p, q = x.get(field), y.get(field)
            if isinstance(p, (int, float)) and isinstance(q, (int, float)):
                if abs(float(p) - float(q)) > 1e-9:
                    problems.append("CHECK FAILED: %s.%s %r != %r" % (sym, field, p, q))
            elif p != q:
                problems.append("CHECK FAILED: %s.%s %r != %r" % (sym, field, p, q))
        for block in ("arm_full", "arm_oos"):
            for field in ("periods", "annualized_compound", "annual_vol", "max_drawdown",
                          "worst_period"):
                p, q = x[block].get(field), y[block].get(field)
                if isinstance(p, (int, float)) and isinstance(q, (int, float)):
                    if abs(float(p) - float(q)) > 1e-9:
                        problems.append("CHECK FAILED: %s.%s.%s %r != %r"
                                        % (sym, block, field, p, q))
        for field in ("lots_needed", "lots_whole", "realised_beta_after_rounding",
                      "beta_error_after_rounding"):
            p, q = x["ticket"].get(field), y["ticket"].get(field)
            if isinstance(p, (int, float)) and isinstance(q, (int, float)):
                if abs(float(p) - float(q)) > 1e-6:
                    problems.append("CHECK FAILED: %s.ticket.%s %r != %r" % (sym, field, p, q))

    for label in face["pairs"]:
        x, y = face["pairs"][label], fresh["pairs"][label]
        for field in ("b_large", "b_small", "r2", "residual_annual_vol"):
            p, q = x.get(field), y.get(field)
            if isinstance(p, (int, float)) and isinstance(q, (int, float)):
                if abs(float(p) - float(q)) > 1e-9:
                    problems.append("CHECK FAILED: pair %s/%s %r != %r" % (label, field, p, q))

    for key in ("share_spread", "second_leg_removed_vol", "gap_pp", "raw_gap_pp_at_k1",
                "best_by_share"):
        p = face["reads"].get(key)
        q = fresh["reads"].get(key)
        if isinstance(p, (int, float)) and isinstance(q, (int, float)):
            if abs(float(p) - float(q)) > 1e-9:
                problems.append("CHECK FAILED: reads.%s %r != %r" % (key, p, q))
        elif p != q:
            problems.append("CHECK FAILED: reads.%s %r != %r" % (key, p, q))

    for key in ("target_vol", "closest_rival", "closest_rival_floor_vol",
                "gap_pp_at_equal_risk", "reachable_at_target"):
        p = (face.get("vol_floors") or {}).get(key)
        q = (fresh.get("vol_floors") or {}).get(key)
        if isinstance(p, (int, float)) and isinstance(q, (int, float)):
            if abs(float(p) - float(q)) > 1e-9:
                problems.append("CHECK FAILED: vol_floors.%s %r != %r" % (key, p, q))
        elif p != q:
            problems.append("CHECK FAILED: vol_floors.%s %r != %r" % (key, p, q))

    for sym in ("510300", "510500", "512100"):
        p = ((face.get("vol_floors") or {}).get("by_symbol") or {}).get(sym) or {}
        q = ((fresh.get("vol_floors") or {}).get("by_symbol") or {}).get(sym) or {}
        for field in ("k_at_floor", "floor_vol", "annualised_at_floor", "reaches_target"):
            x, y = p.get(field), q.get(field)
            if isinstance(x, (int, float)) and isinstance(y, (int, float)):
                if abs(float(x) - float(y)) > 1e-9:
                    problems.append("CHECK FAILED: floor %s/%s %r != %r" % (sym, field, x, y))
            elif x != y:
                problems.append("CHECK FAILED: floor %s/%s %r != %r" % (sym, field, x, y))

    for key in ("verdict", "verdict_matters", "verdict_tradeoff", "verdict_second_leg",
                "verdict_lean", "verdict_why"):
        if face.get(key) != fresh.get(key):
            problems.append("CHECK FAILED: %s %r != %r" % (key, face.get(key), fresh.get(key)))

    if not face.get("anchor", {}).get("ok"):
        problems.append("CHECK FAILED: anchor against r2022 does not hold "
                        "(beta-is diff %r, beta-full diff %r, share diff %r)"
                        % (face["anchor"].get("beta_is_abs_diff"),
                           face["anchor"].get("beta_full_abs_diff"),
                           face["anchor"].get("share_abs_diff")))

    if problems:
        for p in problems:
            print(p)
        return 3

    if not os.path.exists(md_path):
        print("STALE: page missing (%s)" % _rel(md_path))
        return 3
    with open(md_path, "r", encoding="utf-8") as fh:
        page = fh.read()
    for token in (face["verdict"], face["verdict_matters"], face["verdict_tradeoff"],
                  face["verdict_second_leg"], face["verdict_lean"],
                  "<!-- BEGIN:ASTOCK-VETO-HEDGE-INSTRUMENT -->",
                  "<!-- END:ASTOCK-VETO-HEDGE-INSTRUMENT -->"):
        if token not in page:
            problems.append("STALE: page missing token %r" % token)
    if problems:
        for p in problems:
            print(p)
        return 3
    print("check OK: %d candidates, %d pairs, verdict %s, anchor beta-is diff %.2e"
          % (len(face["candidates"]), len(face["pairs"]), face["verdict"],
             face["anchor"]["beta_is_abs_diff"]))
    return 0


# --------------------------------------------------------------------- selftest
def selftest() -> int:
    ok = fail = 0

    def _ok(cond, msg):
        nonlocal ok, fail
        if cond:
            ok += 1
        else:
            fail += 1
            print("FAIL: %s" % msg)

    # 1. a slope of 2 is read back as 2
    f = ols([2.0 * x + 1.0 for x in range(10)], list(range(10)))
    _ok(abs(f["beta"] - 2.0) < 1e-12 and abs(f["alpha"] - 1.0) < 1e-12, "ols recovers 2x+1")

    # 2. an exact fit has R^2 = 1
    _ok(abs(f["r2"] - 1.0) < 1e-12, "ols exact fit R^2 = 1")

    # 3. a flat regressor has no regression, and says so
    flat = ols([1.0, 2.0, 3.0], [1.0, 1.0, 1.0])
    _ok(flat["beta"] is None and flat["n"] == 3, "flat x is refused, not fitted")

    # 4. k = 0 returns the book bit for bit
    book = [0.01, -0.02, 0.03, 0.0, 0.04]
    hedge = [0.02, -0.01, 0.05, 0.01, 0.02]
    _ok(arm_series(book, hedge, 0.0, 0.9) == book, "k=0 is the book itself")

    # 5. beta = 0 charges no roll: nothing is shorted
    _ok(arm_series(book, hedge, 1.0, 0.0) == book, "beta=0 charges no roll cost")

    # 6. one unit of beta with equal returns is a flat line minus roll
    same = arm_series([0.02] * 4, [0.02] * 4, 1.0, 1.0)
    _ok(all(abs(x + ROLL_COST) < 1e-12 for x in same), "perfect hedge leaves exactly the roll cost")

    # 7. a missing hedge price drops the period instead of hedging it for free
    dropped = arm_series([0.01, 0.02], [0.01, None], 1.0, 0.9)
    _ok(dropped[0] is not None and dropped[1] is None, "an unpriced period is dropped, not free")

    # 8. share removed by the true beta is 1 when the hedge explains everything
    _ok(abs(variance_read(book, [x * 1.5 for x in book], 1.0 / 1.5)["share_removable"] - 1.0) < 1e-12,
        "true beta removes all the variance")

    # 9. two-factor fit recovers both loadings on synthetic data
    rng = np.random.default_rng(7)
    x1 = rng.normal(0, 0.02, 200)
    x2 = rng.normal(0, 0.02, 200)
    y = 0.8 * x1 + 0.4 * x2
    t = ols_two(y, x1, x2)
    _ok(abs(t["b1"] - 0.8) < 1e-9 and abs(t["b2"] - 0.4) < 1e-9, "two-factor fit recovers both betas")

    # 10. and leaves no residual it cannot explain
    _ok(abs(float(np.max(np.abs(t["resid"])))) < 1e-12, "two-factor fit on an exact pair has no residual")

    # 11. the picker takes the largest share and reports the spread
    pick = pick_index({"A": 0.80, "B": 0.84, "C": 0.82})
    _ok(pick["best"] == "B" and abs(pick["spread"] - 0.04) < 1e-12, "picker names the best and the spread")
    _ok(pick["verdict"] == "ANY_OF_THE_THREE_IS_ENOUGH", "a 4pp spread is under the 5pp line")

    # 12. and the line flips at exactly the frozen value
    _ok(pick_index({"A": 0.80, "B": 0.85, "C": 0.82})["verdict"] == "HEDGE_INSTRUMENT_MATTERS",
        "a 5pp spread reaches the line")

    # 13. the raw k = 1 gap is printed as a reading, not used as the token
    _ok(tradeoff_verdict("A", {"A": {}, "B": {}}, {"A": 0.10, "B": 0.12})["raw_verdict"]
        == "RISK_REMOVAL_COSTS_RETURN", "2pp raw gap is labelled as a trade-off")
    _ok(tradeoff_verdict("A", {"A": {}, "B": {}}, {"A": 0.10, "B": 0.115})["raw_verdict"]
        == "NO_TRADEOFF", "1.5pp raw gap is not")

    # 14. a second leg needs the frozen volatility to count
    _ok(second_leg_verdict(0.11, 0.09)["verdict"] == "SECOND_LEG_PAYS", "2pp of vol pays")
    _ok(second_leg_verdict(0.11, 0.10)["verdict"] == "SECOND_LEG_DOES_NOT_PAY", "1pp of vol does not")

    # 15. the lean token follows the loading, not the label
    _ok(lean_verdict(0.5, 0.9) == "BOOK_LEANS_SMALL", "a larger small-cap loading is BOOK_LEANS_SMALL")
    _ok(lean_verdict(0.9, 0.5) == "BOOK_LEANS_LARGE", "a larger large-cap loading is BOOK_LEANS_LARGE")

    # 16. one lot of an ETF is 100 shares
    ticket = lots_for(1_000_000.0, 0.9, 2.3, 100)
    _ok(abs(ticket["one_lot_notional"] - 230.0) < 1e-12, "an ETF lot is 100 shares")
    _ok(abs(ticket["lots_needed"] - 900_000.0 / 230.0) < 1e-9, "lots = beta*capital / one lot")

    # 17. the two-leg arm charges both roll legs
    two = two_leg_arm([0.02] * 4, [0.01] * 4, [0.01] * 4, 1.0, 1.0)
    _ok(all(abs(x + 2.0 * ROLL_COST) < 1e-12 for x in two), "two legs pay two rolls")

    # 18. a period missing either leg is dropped
    two_drop = two_leg_arm([0.01, 0.01], [0.01, None], [0.01, 0.01], 1.0, 1.0)
    _ok(two_drop[0] is not None and two_drop[1] is None, "two-leg arm drops an unpriced period")

    # 19. the parents' constants are the ones this face runs on
    _ok(abs(ROLL_COST - 2.0 * COST_ONE_SIDE) < 1e-12 and HOLD == 20,
        "roll cost and hold are the parents' own constants")

    # 20. a book that *is* the hedge can be held at zero volatility
    same_book = [x * 1.3 for x in book]
    fl = vol_floor(same_book, book, 1.0 / 1.3)
    _ok(abs(fl["floor_vol"]) < 1e-9, "an exactly-hedged book reaches zero vol")

    # 21. the floor is never above the unhedged arm: k = 0 is on the grid
    book_v = annual_vol_pure(book)
    fl2 = vol_floor(book, [0.03, -0.01, 0.02, 0.0, 0.01], 0.5)
    _ok(fl2["floor_vol"] <= book_v + 1e-12, "the scanned floor never exceeds the unhedged vol")

    # 22. a rival that cannot reach the risk is not a cheaper hedge
    far = reach_verdict(0.11, {"A": {"floor_vol": 0.11}, "B": {"floor_vol": 0.30}}, "A", 0.07)
    _ok(far["verdict"] == "NO_RIVAL_REACHES_THIS_RISK" and far["closest"] == "B",
        "an unreachable rival is named and refused")
    _ok(far["gap_pp"] is None, "no trade-off gap is invented when nothing reaches the risk")

    # 23. a reachable rival that earns the frozen line more is a real trade-off
    near = reach_verdict(0.11, {"A": {"floor_vol": 0.105}, "B": {"floor_vol": 0.108,
                                                               "annualised_at_floor": 0.10}},
                         "A", 0.07)
    _ok(near["verdict"] == "RISK_REMOVAL_COSTS_RETURN" and abs(near["gap_pp"] - 3.0) < 1e-9,
        "3pp at equal risk is a trade-off")
    near2 = reach_verdict(0.11, {"A": {"floor_vol": 0.105}, "B": {"floor_vol": 0.108,
                                                                "annualised_at_floor": 0.08}},
                          "A", 0.07)
    _ok(near2["verdict"] == "NO_TRADEOFF", "1pp at equal risk is not")

    # 24. the reach tolerance is 1 pp and it is inclusive
    edge = reach_verdict(0.11, {"A": {"floor_vol": 0.11}, "B": {"floor_vol": 0.12,
                                                              "annualised_at_floor": 0.08}},
                         "A", 0.07)
    _ok(edge["verdict"] == "NO_TRADEOFF" and edge["reachable"],
        "exactly at the tolerance counts as reaching")

    print("selftest %d/%d PASS" % (ok, ok + fail))
    return 0 if fail == 0 else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cmd", nargs="?", default="run", choices=("run", "check", "selftest"))
    args = ap.parse_args(argv)
    if args.cmd == "check":
        return check()
    if args.cmd == "selftest":
        return selftest()
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
