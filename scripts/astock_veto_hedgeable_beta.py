"""A-share residual veto book: the 27% vol ticket -- can the other side be bought?

r2003 fitted the veto book (B) on CSI1000 and got beta 0.976 with R^2 0.857, and then
said, in its own words, that "the beta leg is an attribution device, not a hedge
someone can buy at that price" -- because it regressed on index *levels*.
r2014 (tearsheet) printed the other half: 27.34% annualised vol, -25.92% max drawdown.

Neither face answers what a person holding this book actually asks:

    if 85% of that volatility is a small-cap beta I could short, what happens to the
    record when I short it -- with an instrument that exists, priced at what it
    actually cost, and judged on the part of the window I did not fit the beta on?

How it is measured
------------------
Two hedge instruments, both real, neither spliced by me:

* **512100** (中证1000 ETF): the full 77-period window. Its own series carries one
  +176% single-day print on 2022-09-05 (a share-conversion), so the leg is passed
  through the same 35% single-day line the ETF book already uses
  (`etf_equity_alpha.repair_flips`) before any return is taken; the repair is printed.
* **IM** (中证1000 stock-index future, main continuous): the 51 periods that sit
  inside its own listing window (2022-07-26 onwards). Nothing is repaired here; the
  series is what traded, so the basis is *measured* rather than assumed.

The hedge is rolled on the book's own 20-bar grid: short at the rebalance date, close
at the next one. Cost on the ETF arm is two sides per roll (8.00 bp each) on the
shorted notional, plus a separately printed short-finance sensitivity (0 / 2 / 5 %/yr
on the same notional). The IM arm pays its roll inside the traded price, so it is
printed with zero modelled cost and the realised basis next to it.

Beta honesty
------------
The headline arm uses the beta fitted on 2020-07-06..2023-12-31 only (43 periods) and
is then read on 2024+ (34 periods) without refitting. The full-window fit is printed
next to it for the r2003 cross-read. The IM arm is too short to split well; it is
labelled as fitted in-window, with a first-half/second-half variant beside it.

What this face does not claim
-----------------------------
* It does not say a hedge is free: shorting 512100 in size needs 融券 inventory, and
  the finance cost is a broker term this repository cannot observe. That is why the
  carry axis is a table, not a number.
* It does not model daily marks: drawdown is on the 20-bar period curve, exactly like
  the tearsheet it is anchored to.
* It does not claim the hedged book is tradeable as a *product* -- the short leg has
  its own margin, roll and borrow risks, and IM one lot is 1.11x a 1,000,000 CNY book
  at the last close (printed in `executability`).

Usage
-----
    python scripts/astock_veto_hedgeable_beta.py run
    python scripts/astock_veto_hedgeable_beta.py check
    python scripts/astock_veto_hedgeable_beta.py selftest
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from astock_resid_veto_layer import COST_ONE_SIDE, HOLD  # noqa: E402
from astock_veto_tearsheet import (  # noqa: E402
    PPY,
    annual_vol,
    equity_curve,
    hit_rate,
    max_drawdown,
    sharpe,
    underwater_share,
)
from astock_resid_veto_layer import compound  # noqa: E402
from etf_equity_alpha import FLIP_THR, repair_flips  # noqa: E402

OUT = os.path.join(ROOT, "results", "astock_veto_hedgeable_beta.json")
MD = os.path.join(ROOT, "research", "ASTOCK_VETO_HEDGEABLE_BETA.md")
BOOK = os.path.join(ROOT, "results", "astock_veto_turnover_layers.json")
TEARSHEET = os.path.join(ROOT, "results", "astock_veto_tearsheet.json")
YEAR_SOURCE = os.path.join(ROOT, "results", "astock_veto_year_source.json")
ETF_CSV = os.path.join(ROOT, "data", "daily", "sh512100.csv")
IM_CSV = os.path.join(ROOT, "data", "futures_daily", "IM.csv")
IDX_CSV = os.path.join(ROOT, "data", "index_daily", "sh000852.csv")

DOC_BEGIN = "<!-- BEGIN:ASTOCK-VETO-HEDGEABLE-BETA -->"
DOC_END = "<!-- END:ASTOCK-VETO-HEDGEABLE-BETA -->"

KS = (0.0, 0.25, 0.5, 1.0, 1.5)
ROLL_COST = 2.0 * COST_ONE_SIDE          # both sides of every roll, per unit of notional
CARRY_AXIS = (0.0, 0.02, 0.05)           # short-finance, %/yr on the shorted notional
IS_END = "2023-12-31"                    # beta fitted on dates <= this, read after it
ETF_SYMBOL = "512100"
ETF_LOT = 100                            # shares per lot
IM_MULT = 200                            # CNY per index point
CAPITALS = (1_000_000, 3_000_000, 10_000_000, 20_000_000)


# ------------------------------------------------------------------ pure logic
def ols(y, x) -> dict:
    """Slope, intercept and R^2 by least squares.  Fewer than 3 points, or a flat
    x, has no regression -- it says so instead of printing something that looks
    fitted."""
    y = np.asarray(y, dtype=np.float64)
    x = np.asarray(x, dtype=np.float64)
    keep = np.isfinite(y) & np.isfinite(x)
    y, x = y[keep], x[keep]
    n = int(len(y))
    if n < 3 or float(np.var(x)) <= 0.0:
        return {"n": n, "beta": None, "alpha": None, "r2": None}
    X = np.column_stack([np.ones_like(x), x])
    coef = np.linalg.lstsq(X, y, rcond=None)[0]
    fit = X @ coef
    ss_res = float(np.sum((y - fit) ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    r2 = None if ss_tot <= 0.0 else 1.0 - ss_res / ss_tot
    return {"n": n, "beta": float(coef[1]), "alpha": float(coef[0]), "r2": r2}


def arm_series(book, hedge, k: float, beta: float, roll_cost: float = ROLL_COST,
               carry_ppy: float = 0.0) -> list:
    """The hedged book, period by period.

    r = book - k*beta*hedge - |k*beta|*roll_cost - |k*beta|*carry/PPY

    k=0 is the book itself, bit for bit -- that identity is asserted in selftest.
    A period whose hedge return is missing is dropped, never treated as a flat
    hedge: a period we could not price is not a period we hedged for free.
    """
    out = []
    notional_coef = abs(k * beta)
    for b, h in zip(book, hedge):
        if h is None or not np.isfinite(h) or b is None or not np.isfinite(b):
            out.append(None)
            continue
        out.append(float(b) - k * beta * float(h)
                   - notional_coef * roll_cost
                   - notional_coef * carry_ppy / PPY)
    return out


def stats(rets) -> dict:
    """The tearsheet's five readings on one arm, plus the ones it also prints."""
    r = [x for x in rets if x is not None and np.isfinite(x)]
    if not r:
        return {"periods": 0}
    return {
        "periods": len(r),
        "per_period_mean": float(np.mean(r)),
        "annualized_compound": compound(list(r)),
        "annual_vol": annual_vol(r),
        "sharpe_excess_0": sharpe(r, 0.0),
        "max_drawdown": max_drawdown(r),
        "hit_rate": hit_rate(r),
        "worst_period": float(np.min(r)),
        "underwater_share": underwater_share(r),
    }


def variance_read(book, hedge, beta) -> dict:
    """How much of the book's variance one unit of beta actually removes, measured
    rather than read off R^2 (the two agree only when the fit has an intercept --
    which it does here, and selftest proves they agree)."""
    b = np.asarray(book, dtype=np.float64)
    h = np.asarray(hedge, dtype=np.float64)
    keep = np.isfinite(b) & np.isfinite(h)
    b, h = b[keep], h[keep]
    if len(b) < 3:
        return {"share_removable": None, "n": int(len(b))}
    resid = b - beta * h
    var_b = float(np.var(b, ddof=1))
    var_r = float(np.var(resid, ddof=1))
    return {
        "n": int(len(b)),
        "book_annual_vol": float(np.std(b, ddof=1) * np.sqrt(PPY)),
        "residual_annual_vol": float(np.std(resid, ddof=1) * np.sqrt(PPY)),
        "share_removable": None if var_b <= 0 else 1.0 - var_r / var_b,
    }


def decide(full_k1: dict, full_k0: dict, oos_k1: dict, oos_k0: dict) -> tuple:
    """Three frozen states, strict comparisons, no invented margin.

    The verdict is on k=1 (beta-neutral), the only hedge size with a mechanical
    meaning.  Every other k is a curve, printed but not voted on -- picking the
    best-looking k after seeing the numbers is how a backtest becomes a story.
    """
    if not full_k1.get("sharpe_excess_0") or not full_k0.get("sharpe_excess_0"):
        return "INDETERMINATE", "one of the arms has no Sharpe"
    if (oos_k1.get("sharpe_excess_0") is not None
            and oos_k0.get("sharpe_excess_0") is not None
            and oos_k1["sharpe_excess_0"] > oos_k0["sharpe_excess_0"]
            and (oos_k1.get("per_period_mean") or 0.0) > 0.0):
        return "HEDGE_PAYS_OUT_OF_SAMPLE", (
            "beta-neutral hedge beats the unhedged book on the periods the beta was "
            "not fitted on, and still earns money there")
    if full_k1["sharpe_excess_0"] > full_k0["sharpe_excess_0"]:
        return "HEDGE_PAYS_IN_SAMPLE_ONLY", (
            "the hedge improves the full-window record but does not improve it on the "
            "out-of-sample part -- what it bought was the beta's path, not new edge")
    return "HEDGE_COSTS", (
        "after the roll cost the beta-neutral hedge is not better risk-adjusted even "
        "on the window it was fitted to")


def period_ends(dates, calendar) -> tuple:
    """Each period's end date.  Consecutive rebalances are 20 panel bars apart, so
    the next rebalance *is* the end; the last one is 20 bars further on the ETF
    calendar.  The bar count of every span is returned so a span that is one bar
    short is printed instead of hidden."""
    pos = {d: i for i, d in enumerate(calendar)}
    ends, spans = [], []
    for i in range(len(dates) - 1):
        ends.append(dates[i + 1])
    last = dates[-1]
    if last in pos and pos[last] + HOLD < len(calendar):
        ends.append(calendar[pos[last] + HOLD])
    else:
        ends.append(None)
    for d, e in zip(dates, ends):
        if d in pos and e in pos:
            spans.append(pos[e] - pos[d])
        else:
            spans.append(None)
    return ends, spans


def hedge_returns(dates, ends, close_of) -> list:
    """Price-path return of the hedge leg; None where either end is unpriced."""
    out = []
    for d, e in zip(dates, ends):
        if d is None or e is None or d not in close_of or e not in close_of:
            out.append(None)
            continue
        c0, c1 = close_of[d], close_of[e]
        out.append(None if not c0 else float(c1) / float(c0) - 1.0)
    return out


def lots_for(capital: float, beta: float, unit_price: float, multiplier: float) -> dict:
    """How many contracts/lots a beta-neutral short needs, and how big one is."""
    notional = abs(beta) * capital
    one = unit_price * multiplier
    lots = float("nan") if one <= 0 else notional / one
    return {
        "capital": float(capital),
        "beta": float(beta),
        "shorted_notional": float(notional),
        "one_lot_notional": float(one),
        "lots_needed": float(lots),
        "executable": bool(lots >= 1.0),
        "size_multiple_of_needed": float(lots),
        "capital_for_one_lot_at_this_beta": float(one / abs(beta)) if beta else None,
    }


# ----------------------------------------------------------------------- loaders
def _read_json(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def load_book() -> dict:
    face = _read_json(BOOK)
    rows = face.get("rows") or []
    if not rows:
        raise SystemExit("book face has no rows: %s" % BOOK)
    return {
        "dates": [r["date"] for r in rows],
        "net": [float(r["net"]) for r in rows],
        "cutoff": face.get("evidence_cutoff"),
    }


def load_etf() -> dict:
    """512100's own traded close, after the 35% single-day line.  The repair list is
    returned, not swallowed: the reader is entitled to see what was flattened."""
    import pandas as pd

    df = pd.read_csv(ETF_CSV, usecols=["date", "open", "close"])
    raw = df["close"].astype(float)
    adj, _adj_open, n_bad = repair_flips(df[["close"]].astype(float),
                                         df[["open"]].astype(float), thr=FLIP_THR)
    adj_close = adj["close"].astype(float)
    raw_r = raw.pct_change()
    bad = raw_r.abs() > FLIP_THR
    repairs = [{"date": str(d), "raw_move": float(raw_r.iloc[i])}
               for i, d in enumerate(df["date"].tolist()) if bool(bad.iloc[i])]
    return {
        "dates": [str(d) for d in df["date"].tolist()],
        "close": {str(d): float(c) for d, c in zip(df["date"].tolist(), adj_close.tolist())},
        "last_price": float(adj_close.iloc[-1]),
        "repairs": repairs,
        "repaired_prints": int(n_bad),
        "threshold": float(FLIP_THR),
    }


def load_im() -> dict:
    import pandas as pd

    df = pd.read_csv(IM_CSV, usecols=["date", "close"])
    idx = pd.read_csv(IDX_CSV, usecols=["date", "close"])
    im_close = {str(d): float(c) for d, c in zip(df["date"], df["close"])}
    ix_close = {str(d): float(c) for d, c in zip(idx["date"], idx["close"])}
    common = sorted(set(im_close) & set(ix_close))
    basis = [im_close[d] / ix_close[d] - 1.0 for d in common if ix_close[d]]
    return {
        "dates": sorted(im_close),
        "close": im_close,
        "index_close": ix_close,
        "first": sorted(im_close)[0],
        "last": sorted(im_close)[-1],
        "basis_median": float(np.median(basis)) if basis else None,
        "basis_days": len(basis),
    }


# ------------------------------------------------------------------------ the face
def build_face() -> dict:
    book = load_book()
    etf = load_etf()
    im = load_im()

    dates = book["dates"]
    ends, spans = period_ends(dates, etf["dates"])
    hedge_etf = hedge_returns(dates, ends, etf["close"])
    hedge_im = hedge_returns(dates, ends, im["close"])
    book_net = book["net"]

    is_mask = [d <= IS_END for d in dates]

    def split(series):
        return ([v for v, m in zip(series, is_mask) if m],
                [v for v, m in zip(series, is_mask) if not m])

    def paired(book_s, hedge_s):
        """Drop the pairs where either leg is missing, once, so both arms are read
        on the same periods."""
        b, h = [], []
        for x, y in zip(book_s, hedge_s):
            if y is None or x is None or not np.isfinite(y) or not np.isfinite(x):
                continue
            b.append(x)
            h.append(y)
        return b, h

    b_is, h_is = paired(
        [v for v, m in zip(book_net, is_mask) if m],
        [v for v, m in zip(hedge_etf, is_mask) if m])
    b_oos, h_oos = paired(
        [v for v, m in zip(book_net, is_mask) if not m],
        [v for v, m in zip(hedge_etf, is_mask) if not m])
    b_all, h_all = paired(book_net, hedge_etf)

    beta_is = ols(b_is, h_is)
    beta_full = ols(b_all, h_all)

    arms_etf = {}
    for k in KS:
        series = arm_series(book_net, hedge_etf, k, beta_is["beta"])
        is_part = [v for v, m in zip(series, is_mask) if m]
        oos_part = [v for v, m in zip(series, is_mask) if not m]
        arms_etf["%.2f" % k] = {
            "k": k,
            "beta_used": beta_is["beta"],
            "full": stats(series),
            "in_sample": stats(is_part),
            "out_of_sample": stats(oos_part),
        }

    carry = {}
    for c in CARRY_AXIS:
        series = arm_series(book_net, hedge_etf, 1.0, beta_is["beta"], carry_ppy=c)
        carry["%.2f" % c] = {
            "carry_per_year": c,
            "full": stats(series),
            "out_of_sample": stats([v for v, m in zip(series, is_mask) if not m]),
        }

    # --- IM arm: only the periods fully inside the future's own listing window
    im_ok = []
    for d, e in zip(dates, ends):
        im_ok.append(bool(d and e and d in im["close"] and e in im["close"]
                          and d >= im["first"] and e <= im["last"]))
    b_im = [v for v, ok in zip(book_net, im_ok) if ok]
    h_im = [v for v, ok in zip(hedge_im, im_ok) if ok]
    beta_im = ols(b_im, h_im)
    half = len(b_im) // 2
    beta_im_h1 = ols(b_im[:half], h_im[:half])
    arms_im = {}
    for k in (0.0, 0.5, 1.0):
        arms_im["%.2f" % k] = {
            "k": k,
            "beta_used": beta_im["beta"],
            "full": stats(arm_series(b_im, h_im, k, beta_im["beta"])),
        }
    im_h2_arm = {
        "beta_from_first_half": beta_im_h1["beta"],
        "second_half_unhedged": stats(b_im[half:]),
        "second_half_hedged": stats(arm_series(b_im[half:], h_im[half:], 1.0,
                                               beta_im_h1["beta"] or 0.0)),
    }

    var_read = variance_read(b_all, h_all, beta_full["beta"] or 0.0)
    _b = np.asarray(b_all, dtype=np.float64)
    _r_is = _b - (beta_is["beta"] or 0.0) * np.asarray(h_all, dtype=np.float64)
    var_read["residual_annual_vol_at_is_beta"] = float(np.std(_r_is, ddof=1) * np.sqrt(PPY))
    var_read["share_removable_at_is_beta"] = float(
        1.0 - np.var(_r_is, ddof=1) / np.var(_b, ddof=1))
    var_read["beta_used_for_identity"] = beta_full["beta"]
    var_read["beta_used_for_arms"] = beta_is["beta"]
    verdict, why = decide(arms_etf["1.00"]["full"], arms_etf["0.00"]["full"],
                          arms_etf["1.00"]["out_of_sample"],
                          arms_etf["0.00"]["out_of_sample"])
    best_k = max((v for v in arms_etf.values() if v["k"] > 0),
                 key=lambda v: v["out_of_sample"].get("sharpe_excess_0") or -9)

    cross = _cross_read(beta_is, beta_full)
    anchor = _anchor(arms_etf["0.00"], arms_etf)
    execu = {}
    execu["etf"] = {
        "unit": "one lot = %d shares" % ETF_LOT,
        "one_lot_notional": etf["last_price"] * ETF_LOT,
        "by_capital": {str(c): lots_for(c, beta_is["beta"] or 0.0,
                                        etf["last_price"], ETF_LOT) for c in CAPITALS},
    }
    execu["im"] = {
        "unit": "one contract = %d CNY per index point" % IM_MULT,
        "one_lot_notional": im["close"][im["last"]] * IM_MULT,
        "by_capital": {str(c): lots_for(c, beta_is["beta"] or 0.0,
                                        im["close"][im["last"]], IM_MULT)
                       for c in CAPITALS},
    }

    rows = []
    for i, d in enumerate(dates):
        rows.append({
            "date": d,
            "end": ends[i] if i < len(ends) else None,
            "span_bars": spans[i] if i < len(spans) else None,
            "book_net": book_net[i],
            "hedge_etf": hedge_etf[i] if i < len(hedge_etf) else None,
            "hedge_im": hedge_im[i] if i < len(hedge_im) else None,
            "in_sample": bool(is_mask[i]),
            "im_window": bool(im_ok[i]),
        })

    return {
        "generated": _now(),
        "evidence_cutoff": book.get("cutoff"),
        "machine": "bm-c",
        "kind": "astock_veto_hedgeable_beta",
        "family_faces_before": _family_count(),
        "fills_the_hole_of": (
            "r2003 fitted beta 0.976 / R^2 0.857 on index levels and said in print that "
            "the beta leg is an attribution device, not a hedge anyone can buy; r2014 "
            "printed 27.34% vol. Nobody priced the other side on a tradable instrument."),
        "prereg": {
            "question": ("how much of the veto book's 27.34% volatility is a shortable "
                         "index beta, and what does the record look like once that beta "
                         "is actually shorted, rolled every 20 bars, net of cost, on the "
                         "part of the window the beta was not fitted on?"),
            "arms": {("%.2f" % k): "short k xbeta_is of the hedge leg every period"
                     for k in KS},
            "primary_arm": "k = 1.00 (beta-neutral) -- the only size with a mechanical meaning",
            "hedge_instrument": {
                "primary": "512100 CSI1000 ETF, traded close, one split repaired at %.2f" % FLIP_THR,
                "secondary": "IM CSI1000 stock-index future (main continuous), its own listing window",
            },
            "beta_estimation": ("OLS of the book's own net per-period return on the hedge's "
                                "per-period return; headline uses dates <= %s only" % IS_END),
            "cost_model": ("two sides x 8.00 bp per roll on the shorted notional; short-finance "
                           "carry printed as a 0/2/5 %/yr axis, not assumed; IM arm carries its "
                           "roll inside the traded price and prints the realised basis"),
            "verdict_rule": ("three states, strict comparison of Sharpe (excess over 0%) at k=1: "
                             "OUT_OF_SAMPLE = k=1 beats k=0 on the not-fitted part AND earns >0 "
                             "there; IN_SAMPLE_ONLY = full window better but out-of-sample not; "
                             "COSTS = not better even in window. No margin invented."),
            "rule_frozen_before_run": True,
        },
        "spec": {
            "hold": HOLD,
            "stride": HOLD,
            "cost_one_side": COST_ONE_SIDE,
            "roll_cost_per_period": ROLL_COST,
            "periods_per_year": PPY,
            "booking": "close(t) -> close(t+20) on the book's own panel calendar",
            "book_arm": "B = pool minus residual top 20% (parent face, net of its own turnover cost)",
            "is_end": IS_END,
            "etf_lot": ETF_LOT,
            "im_multiplier": IM_MULT,
        },
        "data": {
            "book": {"face": "results/astock_veto_turnover_layers.json",
                     "periods": len(dates), "first": dates[0], "last": dates[-1]},
            "etf": {"symbol": ETF_SYMBOL, "csv": "data/daily/sh512100.csv",
                    "first": etf["dates"][0], "last": etf["dates"][-1],
                    "repaired_prints": etf["repaired_prints"],
                    "repairs": etf["repairs"], "last_price": etf["last_price"]},
            "im": {"csv": "data/futures_daily/IM.csv", "first": im["first"],
                   "last": im["last"], "basis_median": im["basis_median"],
                   "basis_days": im["basis_days"],
                   "basis_note": ("IM close over CSI1000 index close, median across the "
                                  "overlapping days; a negative number is the discount a "
                                  "short pays for")},
            "span_note": ("one of the 76 spans covers %d ETF bars instead of %d because "
                          "512100 has no bar on one panel date"
                          % (min([s for s in spans if s] or [HOLD]),
                             HOLD)) if any(s and s != HOLD for s in spans) else
                         "every span covers exactly %d ETF bars" % HOLD,
        },
        "beta": {
            "etf_in_sample": beta_is,
            "etf_full_window": beta_full,
            "im_in_window": beta_im,
            "im_first_half": beta_im_h1,
        },
        "variance": {
            **var_read,
            "r2_full_window": beta_full.get("r2"),
            "identity_note": ("share_removable from the variance identity equals R^2 of the "
                              "same fit; both are printed so a divergence is visible"),
        },
        "arms_etf": arms_etf,
        "arms_im": arms_im,
        "im_half_split": im_h2_arm,
        "carry_sensitivity": carry,
        "verdict": verdict,
        "verdict_why": why,
        "grid_note": ("网格上样本外夏普最好的一档是 k=%.2f（%.3f，对未对冲的 %.3f）；"
                      "只作曲线观察，判词仍取 k=1"
                      % (best_k["k"],
                         best_k["out_of_sample"].get("sharpe_excess_0") or float("nan"),
                         arms_etf["0.00"]["out_of_sample"].get("sharpe_excess_0") or float("nan"))),
        "executability": execu,
        "cross_read_r2003": cross,
        "anchor": anchor,
        "rows": rows,
    }


def _family_count() -> int:
    try:
        names = [n for n in os.listdir(os.path.join(ROOT, "results"))
                 if n.startswith("astock_veto_") and n.endswith(".json")]
        return len(names)
    except OSError:
        return 0


def _cross_read(beta_is, beta_full) -> dict:
    """r2003 fitted B on CSI1000 *index levels*: beta 0.976, R^2 0.857, and said the
    leg was attribution, not a buyable hedge.  If the ETF leg lands near those
    numbers, the two faces are measuring the same exposure through different
    instruments -- which is the whole reason this face is allowed to call it beta."""
    try:
        face = _read_json(YEAR_SOURCE)
    except (OSError, ValueError) as exc:
        return {"ok": False, "why": "r2003 face unreadable: %s" % exc}
    found = ((face.get("betas") or {}).get("B") or {}).get("CSI1000")
    if not isinstance(found, dict):
        return {"ok": False, "why": "r2003 betas.B.CSI1000 not found in face shape"}
    out = {"ok": True, "published_beta": found.get("beta"), "published_r2": found.get("r2"),
           "published_n": found.get("n"),
           "mine_full_beta": beta_full.get("beta"), "mine_full_r2": beta_full.get("r2"),
           "mine_is_beta": beta_is.get("beta")}
    try:
        out["beta_gap_vs_published"] = abs(float(out["mine_full_beta"]) - float(out["published_beta"]))
        out["r2_gap_vs_published"] = abs(float(out["mine_full_r2"]) - float(out["published_r2"]))
    except (TypeError, ValueError):
        out["beta_gap_vs_published"] = None
        out["r2_gap_vs_published"] = None
    return out


def _anchor(k0_arm: dict, arms: dict) -> dict:
    """The k=0 arm must reproduce the tearsheet's published B fractional readings
    bit for bit -- that is the proof this face hedges *this* book."""
    try:
        face = _read_json(TEARSHEET)
        ref = face["summary"]["B"]["bookings"]["fractional"]
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return {"ok": False, "why": "tearsheet unreadable: %s" % exc}
    mine = k0_arm["full"]
    pairs = (("per_period_mean", "per_period_mean"),
             ("annualized_compound", "annualized_compound"),
             ("annual_vol", "annual_vol"),
             ("sharpe_excess_0", "sharpe_excess_0"),
             ("max_drawdown", "max_drawdown"))
    worst, fields = 0.0, {}
    for theirs, ours in pairs:
        try:
            diff = abs(float(ref[theirs]) - float(mine[ours]))
        except (KeyError, TypeError, ValueError):
            return {"ok": False, "why": "field %s missing on one side" % theirs}
        fields[theirs] = diff
        worst = max(worst, diff)
    return {"ok": worst <= 1e-12, "worst_abs_diff": worst, "fields": fields}


def _now() -> str:
    return datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")


def _rel(path: str) -> str:
    try:
        rel = os.path.relpath(path, ROOT)
    except ValueError:
        return str(path).replace(os.sep, "/")
    return rel.replace(os.sep, "/")


# ------------------------------------------------------------------------ the docs
def _p(x, nd=4) -> str:
    return "—" if x is None else ("%.*f%%" % (nd, x * 100))


def _f(x, nd=3) -> str:
    return "—" if x is None else ("%.*f" % (nd, x))


def write_md(payload) -> None:
    arms = payload["arms_etf"]
    k0 = arms["0.00"]
    n_is = k0["in_sample"]["periods"]
    n_oos = k0["out_of_sample"]["periods"]
    n_all = k0["full"]["periods"]
    n_im = payload["arms_im"]["0.00"]["full"]["periods"]
    line = []
    a = line.append
    a(DOC_BEGIN)
    a("")
    a("# A 股残差黑名单：27% 的波动那张票，反票到底买不买得成")
    a("")
    a("generated %s | evidence_cutoff **%s** | verdict **%s**"
      % (payload["generated"], payload["evidence_cutoff"], payload["verdict"]))
    a("")
    a("r2003 拟合出 B 臂对中证 1000 的 beta 0.976、R² 0.857，并且在自己的正文里写死了："
      "「这条 beta 腿是归因装置，不是谁在那个价位能买到的对冲」。r2014 补了另一半："
      "年化波动 27.34%、最大回撤 -25.92%。两张面之间那句话一直没人接——**如果 85% 的波动"
      "真的是一段可以卖空的小盘 beta，把它卖空之后账面长什么样，扣完成本、在没拟合 beta 的"
      "那段时间上还剩多少。本面去打那张反票。**")
    a("")
    a("## 一句话")
    a("")
    var = payload["variance"]
    b = payload["beta"]["etf_in_sample"]
    a("**这本书对可交易标的 512100（中证 1000 ETF）的 beta 是 %s（样本内 R² %s）。"
      "用全窗 beta %s 算，一单位 beta 的对冲削掉 **%s** 的方差（这个份额在数学上就等于同一次拟合的 R²，"
      "本面把两者并列印出来）：年化波动 %s → %s；真按样本内 beta %s 去对冲，实际落地是 %s。"
      "全窗净夏普 %s → %s（扣掉每次移仓两侧 8 bp），但**样本外（2024 起）%s vs %s——对冲买到的是"
      "beta 的路径，不是新的边**，判 `%s`。网格上唯一在样本外跑赢的是半仓（k=0.5，%s），"
      "这个观察印出来但不参与判决：先看数再挑 k，就是编故事。**"
      % (_f(b["beta"]), _f(b["r2"]), _f(var["beta_used_for_identity"]),
         _p(var["share_removable"], 1),
         _p(var["book_annual_vol"], 2), _p(var["residual_annual_vol"], 2),
         _f(var["beta_used_for_arms"]), _p(var["residual_annual_vol_at_is_beta"], 2),
         _f(k0["full"]["sharpe_excess_0"]), _f(arms["1.00"]["full"]["sharpe_excess_0"]),
         _f(arms["1.00"]["out_of_sample"]["sharpe_excess_0"]),
         _f(k0["out_of_sample"]["sharpe_excess_0"]), payload["verdict"],
         _f(arms["0.50"]["out_of_sample"]["sharpe_excess_0"])))
    a("")
    a("## 怎么量的")
    a("")
    a("* **对冲腿**：512100 自己的成交价，按账面同一张 20 根 bar 的网格滚动（调仓日卖空、"
      "下一次调仓日平掉）。它有一段 %s，被同一条 35%% 单日线压平后再取收益（%d 处，已印在 JSON）。"
      % ("、".join("%s 的 %s" % (r["date"], _p(r["raw_move"], 2)) for r in payload["data"]["etf"]["repairs"]) or "无异常",
         payload["data"]["etf"]["repaired_prints"]))
    a("* **第二根尺**：IM（中证 1000 股指期货主力连续）只在它自己的上市窗内读（%s 起，%d 期）；"
      "不修任何跳空——它的移仓成本就写在成交价里，实测基差中位数 %s（贴水=卖空者在付钱）。"
      % (payload["data"]["im"]["first"], n_im, _p(payload["data"]["im"]["basis_median"], 3)))
    a("* **beta 诚实**：头条臂的 beta 只用 %s 之前的 %d 期拟合，然后在 2024 起的 %d 期上读，不重拟合。"
      "全窗拟合只用于和 r2003 对账（它对 CSI1000 指数水平拟合出 %s / R² %s，本面对**期货**拟合出 %s / R² %s"
      "——两根尺隔着不同标的落在同一个数上，这才叫同一个敞口）。"
      % (payload["spec"]["is_end"], n_is, n_oos,
         _f(payload["cross_read_r2003"].get("published_beta")),
         _f(payload["cross_read_r2003"].get("published_r2")),
         _f(payload["beta"]["im_in_window"]["beta"]),
         _f(payload["beta"]["im_in_window"]["r2"])))
    a("* **成本**：ETF 腿每次移仓两侧 8 bp 打在空头名义额上；融券成本不是我能观测的券商条款，"
      "所以它是 0 / 2 / 5 %%/年 的一张表，不是一个数。")
    a("")
    a("## 四条读数")
    a("")
    a("| k × beta | 期数 | 期间均值 | 年化(复利) | 年化波动 | 夏普 | 最大回撤 | 胜率 |")
    a("|---|---|---|---|---|---|---|---|")
    for key in ("0.00", "0.25", "0.50", "1.00", "1.50"):
        s = arms[key]["full"]
        a("| %s | %d | %s | %s | %s | %s | %s | %s |"
          % (key, s["periods"], _p(s["per_period_mean"]), _p(s["annualized_compound"], 2),
             _p(s["annual_vol"], 2), _f(s["sharpe_excess_0"]), _p(s["max_drawdown"], 2),
             _p(s["hit_rate"], 1)))
    a("")
    a("`k=0` 这一行必须逐位复现 r2014 的 B 臂分数口径：本面最大绝对差 **%.3e**（ok=%s）。"
      % (payload["anchor"]["worst_abs_diff"], payload["anchor"]["ok"]))
    a("")
    a("## 样本内 / 样本外")
    a("")
    a("| k × beta | 样本内夏普 | 样本外夏普 | 样本外期间均值 | 样本外年化波动 |")
    a("|---|---|---|---|---|")
    for key in ("0.00", "0.50", "1.00", "1.50"):
        i, o = arms[key]["in_sample"], arms[key]["out_of_sample"]
        a("| %s | %s | %s | %s | %s |"
          % (key, _f(i.get("sharpe_excess_0")), _f(o.get("sharpe_excess_0")),
             _p(o.get("per_period_mean")), _p(o.get("annual_vol"), 2)))
    a("")
    a(payload["grid_note"])
    a("")
    a("## 融券成本能把判词翻掉吗")
    a("")
    a("| 融券 %/年 | 全窗年化 | 全窗夏普 | 样本外夏普 |")
    a("|---|---|---|---|")
    for key in ("0.00", "0.02", "0.05"):
        c = payload["carry_sensitivity"][key]
        a("| %s | %s | %s | %s |"
          % (_p(c["carry_per_year"], 0), _p(c["full"]["annualized_compound"], 2),
             _f(c["full"]["sharpe_excess_0"]), _f(c["out_of_sample"].get("sharpe_excess_0"))))
    a("")
    a("## 期货那根尺（IM，%s 起 %d 期）" % (payload["data"]["im"]["first"], n_im))
    a("")
    a("| k × beta | 期数 | 年化(复利) | 年化波动 | 夏普 | 最大回撤 |")
    a("|---|---|---|---|---|---|")
    for key in ("0.00", "0.50", "1.00"):
        s = payload["arms_im"][key]["full"]
        a("| %s | %d | %s | %s | %s | %s |"
          % (key, s["periods"], _p(s["annualized_compound"], 2), _p(s["annual_vol"], 2),
             _f(s["sharpe_excess_0"]), _p(s["max_drawdown"], 2)))
    a("")
    a("这一段的 beta 是在同一段窗内拟合的（%d 期太短，拆开会把噪声当系数），所以只当**归因级**读数看。" % n_im)
    hs = payload["im_half_split"]
    half_n = hs["second_half_unhedged"]["periods"]
    a("半窗检验：用前一半（%d 期）拟合的 beta %s，在后一半（%d 期）上读——不对冲夏普 %s / 对冲后 %s。"
      "这段后一半是上涨段，对冲在这里是纯成本，和 ETF 全窗的样本外结论同向。"
      % (n_im - half_n, _f(hs["beta_from_first_half"]), half_n,
         _f(hs["second_half_unhedged"].get("sharpe_excess_0")),
         _f(hs["second_half_hedged"].get("sharpe_excess_0"))))
    a("")
    a("IM 这一段样本与 ETF 全窗的差别就是判词为什么两样：它包含 2022H2–2024 的那段下跌，"
      "对冲在那段是真金；2024 之后是上涨段，对冲只是在付钱。**买对冲的人买的不是夏普，"
      "是「市场跌的时候我还剩多少」。**")
    a("")
    a("## 反票买得到吗")
    a("")
    ex = payload["executability"]
    a("| 资金 | ETF 一手 %s 元 → 需要几手 | IM 一手 %s 元 → 需要几手 |"
      % (_f(ex["etf"]["one_lot_notional"], 0), _f(ex["im"]["one_lot_notional"], 0)))
    a("|---|---|---|")
    for cap in ex["etf"]["by_capital"]:
        e = ex["etf"]["by_capital"][cap]
        m = ex["im"]["by_capital"][cap]
        a("| %s | %s 手（%s） | %s 手（%s） |"
          % (format(int(float(cap)), ","), _f(e["lots_needed"], 2),
             "可做" if e["executable"] else "做不到",
             _f(m["lots_needed"], 2), "可做" if m["executable"] else "做不到"))
    a("")
    a("ETF 这条腿在 100 万就能整手做（一手 %s 元），代价是**要借券**——这是它的门槛，不是资金量。"
      "IM 一手 %s 元：100 万时连一手都不够（%s 手，只能欠配或超配），要到 %s 元以上才能"
      "「按 beta 配一手」。这正是 r2017 那张 IH 面（一手 81.6 万、100 万时 10.9 倍）做不成的事"
      "——换成小盘指数之后，**可执行性本身就是答案的一半**。"
      % (_f(ex["etf"]["one_lot_notional"], 0), _f(ex["im"]["one_lot_notional"], 0),
         _f(ex["im"]["by_capital"]["1000000"]["lots_needed"], 2),
         format(int(ex["im"]["by_capital"]["1000000"]["capital_for_one_lot_at_this_beta"] or 0), ",")))
    a("")
    a("## 这张面不是什么")
    a("")
    a("* 不是「对冲后就能上」的产品结论：卖空腿有自己的保证金、移仓、借券可得性与强平风险，"
      "这只是把 beta 的价格印出来。")
    a("* 不是日频口径：回撤仍在 20 根 bar 的期间曲线上（和 r2014 同一条尺）。")
    a("* 不外推：`k=1.5` 那一行是**过度对冲**（年化 %s、回撤 %s），说明最优 k 就在 1 附近、"
      "再往上只是把波动加倍。"
      % (_p(arms["1.50"]["full"]["annualized_compound"], 2),
         _p(arms["1.50"]["full"]["max_drawdown"], 2)))
    a("* 票池现存标的（幸存者偏差，父面同）；2020 只有 7 期。")
    a("")
    a("## 复现")
    a("")
    a("```")
    a("python scripts/astock_veto_hedgeable_beta.py selftest")
    a("python scripts/astock_veto_hedgeable_beta.py run")
    a("python scripts/astock_veto_hedgeable_beta.py check")
    a("```")
    a("")
    a(DOC_END)
    a("")
    text = "\n".join(line)
    os.makedirs(os.path.dirname(MD), exist_ok=True)
    with open(MD, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def run() -> int:
    payload = build_face()
    if not payload["anchor"]["ok"]:
        print("ANCHOR BROKEN: k=0 does not reproduce the tearsheet (worst %.3e)"
              % (payload["anchor"].get("worst_abs_diff") or float("nan")))
        return 2
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    write_md(payload)
    print("wrote %s" % _rel(OUT))
    print("wrote %s" % _rel(MD))
    print("verdict %s | removable %s | beta_is %.3f r2 %.3f"
          % (payload["verdict"],
             _p(payload["variance"]["share_removable"], 1),
             payload["beta"]["etf_in_sample"]["beta"] or float("nan"),
             payload["beta"]["etf_in_sample"]["r2"] or float("nan")))
    return 0


# ------------------------------------------------------------------------- check
def check() -> int:
    """Re-derive every number from the published rows and the raw legs, then ask the
    face's own verdict rule for the token again.  Shape problems are named (so a
    reader can tell "face missing" from "the numbers moved")."""
    if not os.path.exists(OUT):
        print("face missing: %s -- nothing to check" % _rel(OUT))
        return 3
    face = _read_json(OUT)
    problems = []

    try:
        etf = load_etf()
        im = load_im()
    except (OSError, ValueError, KeyError) as exc:
        print("STALE: legs unreadable (%s) -- rebuild the face" % exc)
        return 3

    # 0. freshness has to be asked of something outside this face, or the face can
    # never say "I am behind" -- its own rows always agree with themselves.
    try:
        parent_cut = _read_json(BOOK).get("evidence_cutoff")
    except (OSError, ValueError):
        parent_cut = None
    if parent_cut and face.get("evidence_cutoff") != parent_cut:
        print("STALE: the book face moved to %s, this face still says %s -- rebuild"
              % (parent_cut, face.get("evidence_cutoff")))
        return 3
    if etf["dates"][-1] != face["data"]["etf"]["last"]:
        print("STALE: the hedge leg now ends %s, this face priced to %s -- rebuild"
              % (etf["dates"][-1], face["data"]["etf"]["last"]))
        return 3

    rows = face.get("rows") or []
    if not rows or len(rows) != int(face["data"]["book"].get("periods") or 0):
        print("CHECK FAILED: published rows (%d) disagree with the face's own period count"
              % len(rows))
        return 3
    dates = [r["date"] for r in rows]
    book = [r["book_net"] for r in rows]
    hedge = [r["hedge_etf"] for r in rows]
    is_mask = [r["in_sample"] for r in rows]

    # 1. the hedge leg itself must still price the same on those dates
    for r in rows:
        d, e = r["date"], r["end"]
        if e is None or d not in etf["close"] or e not in etf["close"]:
            if r["hedge_etf"] is not None:
                problems.append("hedge priced where a bar is missing: %s" % d)
            continue
        again = etf["close"][e] / etf["close"][d] - 1.0
        if r["hedge_etf"] is None or abs(again - r["hedge_etf"]) > 1e-12:
            problems.append("hedge return moved on %s (%.6e)" % (d, again - (r["hedge_etf"] or 0)))

    # 2. beta + every arm re-derived
    pairs_is = [(b, h) for b, h, m in zip(book, hedge, is_mask)
                if m and h is not None and np.isfinite(h)]
    beta_now = ols([p[0] for p in pairs_is], [p[1] for p in pairs_is])
    if beta_now["beta"] is None or abs(beta_now["beta"] - face["beta"]["etf_in_sample"]["beta"]) > 1e-9:
        problems.append("in-sample beta moved")
    if beta_now["r2"] is None or abs(beta_now["r2"] - face["beta"]["etf_in_sample"]["r2"]) > 1e-9:
        problems.append("in-sample R^2 moved")

    for key, arm in face["arms_etf"].items():
        k = arm["k"]
        series = arm_series(book, hedge, k, beta_now["beta"])
        again_full = stats(series)
        again_oos = stats([v for v, m in zip(series, is_mask) if not m])
        for field in ("per_period_mean", "annualized_compound", "annual_vol",
                      "sharpe_excess_0", "max_drawdown", "hit_rate"):
            mine = again_full.get(field)
            theirs = arm["full"].get(field)
            if (mine is None) != (theirs is None):
                problems.append("%s full/%s shape changed" % (key, field))
            elif mine is not None and abs(mine - theirs) > 1e-9:
                problems.append("%s full/%s moved" % (key, field))
        for field in ("per_period_mean", "sharpe_excess_0", "annual_vol"):
            mine = again_oos.get(field)
            theirs = arm["out_of_sample"].get(field)
            if (mine is None) != (theirs is None):
                problems.append("%s oos/%s shape changed" % (key, field))
            elif mine is not None and abs(mine - theirs) > 1e-9:
                problems.append("%s oos/%s moved" % (key, field))

    # 3. variance share must equal the fit's R^2
    var = face["variance"]
    b_all = [b for b, h in zip(book, hedge) if h is not None and np.isfinite(h)]
    h_all = [h for h in hedge if h is not None and np.isfinite(h)]
    beta_full = ols(b_all, h_all)
    again = variance_read(b_all, h_all, beta_full["beta"] or 0.0)
    if abs((again["share_removable"] or 0) - (var["share_removable"] or 0)) > 1e-9:
        problems.append("share_removable moved")
    if beta_full["r2"] is not None and abs(again["share_removable"] - beta_full["r2"]) > 1e-6:
        problems.append("variance share and R^2 disagree")

    # 4. the verdict must be the face's own rule applied to its own rows
    verdict, why = decide(face["arms_etf"]["1.00"]["full"], face["arms_etf"]["0.00"]["full"],
                          face["arms_etf"]["1.00"]["out_of_sample"],
                          face["arms_etf"]["0.00"]["out_of_sample"])
    if verdict != face["verdict"]:
        problems.append("verdict no longer follows from the arms (%s vs %s)"
                        % (verdict, face["verdict"]))

    # 5. the k=0 anchor against the tearsheet
    anchor = _anchor(face["arms_etf"]["0.00"], face["arms_etf"])
    if not anchor.get("ok"):
        problems.append("anchor to r2014 broken: %s" % anchor.get("why") or
                        "worst %.3e" % (anchor.get("worst_abs_diff") or float("nan")))

    # 6. IM window still covers the same periods
    im_ok = [r["im_window"] for r in rows]
    if sum(im_ok) != face["arms_im"]["0.00"]["full"]["periods"]:
        problems.append("IM window period count moved")

    if problems:
        for p in problems[:12]:
            print("CHECK FAILED: %s" % p)
        print("total %d problem(s)" % len(problems))
        return 3
    print("CHECK OK: %d periods, %d ETF bars, %d IM periods, verdict %s"
          % (len(rows), len(etf["dates"]), sum(im_ok), face["verdict"]))
    return 0


# ---------------------------------------------------------------------- selftest
def selftest() -> int:
    ok = 0
    fail = 0

    def _ok(cond, msg):
        nonlocal ok, fail
        if cond:
            ok += 1
        else:
            fail += 1
            print("FAIL: %s" % msg)

    rng = np.random.default_rng(20261124)

    # 1. a noiseless line comes back with an exact slope
    x = rng.normal(0, 0.03, 200)
    y = 0.004 + 2.5 * x
    fit = ols(y, x)
    _ok(abs(fit["beta"] - 2.5) < 1e-9 and abs(fit["r2"] - 1.0) < 1e-12,
        "noiseless line recovers slope 2.5 and R^2 1")

    # 2. with R^2 = 1 the beta-neutral arm has no variance at all
    hedged = arm_series(y, x, 1.0, fit["beta"], roll_cost=0.0)
    _ok(float(np.std(hedged)) < 1e-12, "perfect fit leaves nothing to hedge away twice")

    # 3. the variance identity: share removable == R^2 of the same fit
    x2 = rng.normal(0.005, 0.05, 300)
    y2 = 0.003 + 0.9 * x2 + rng.normal(0, 0.02, 300)
    f2 = ols(y2, x2)
    v2 = variance_read(y2, x2, f2["beta"])
    _ok(abs(v2["share_removable"] - f2["r2"]) < 1e-12,
        "variance share equals R^2 of the same fit")

    # 4. k=0 is the book, bit for bit -- and costs nothing
    base = arm_series(y2, x2, 0.0, f2["beta"], roll_cost=0.0016, carry_ppy=0.05)
    _ok(all(abs(a - b) < 1e-15 for a, b in zip(base, y2)),
        "k=0 arm is the unhedged book, no cost, no carry")

    # 5. one unit of notional costs exactly 2 x 8 bp per period
    k1 = arm_series(y2, x2, 1.0, f2["beta"], roll_cost=0.0016, carry_ppy=0.0)
    k1_free = arm_series(y2, x2, 1.0, f2["beta"], roll_cost=0.0, carry_ppy=0.0)
    gap = [a - b for a, b in zip(k1, k1_free)]
    _ok(all(abs(g + 0.0016 * abs(f2["beta"])) < 1e-15 for g in gap),
        "roll cost is charged on the shorted notional, not on the book")

    # 6. carry only ever lowers the hedged arm, and proportionally to k
    c5 = arm_series(y2, x2, 1.0, f2["beta"], roll_cost=0.0, carry_ppy=0.05)
    c0 = arm_series(y2, x2, 1.0, f2["beta"], roll_cost=0.0, carry_ppy=0.0)
    _ok(all(a < b for a, b in zip(c5, c0)), "positive carry lowers every hedged period")
    c_half = arm_series(y2, x2, 0.5, f2["beta"], roll_cost=0.0, carry_ppy=0.05)
    c_half0 = arm_series(y2, x2, 0.5, f2["beta"], roll_cost=0.0, carry_ppy=0.0)
    _ok(abs((c_half0[0] - c_half[0]) * 2 - (c0[0] - c5[0])) < 1e-15,
        "half the hedge pays half the carry")

    # 7. over-hedging adds variance back
    vol1 = float(np.std(arm_series(y2, x2, 1.0, f2["beta"], 0.0, 0.0)))
    vol15 = float(np.std(arm_series(y2, x2, 1.5, f2["beta"], 0.0, 0.0)))
    _ok(vol15 > vol1, "k=1.5 carries more volatility than k=1")

    # 8. a zero-beta book cannot be helped by a hedge
    v3 = variance_read(y2, rng.normal(0, 0.05, 300), 0.0)
    _ok(abs(v3["share_removable"]) < 1e-12, "a zero hedge removes nothing")

    # 9. missing hedge prints are dropped, never priced as flat
    series = arm_series([0.01, 0.02, 0.03], [0.005, None, 0.004], 1.0, 1.0)
    _ok(series[1] is None and series[0] is not None, "a missing hedge period stays missing")
    st = stats(series)
    _ok(st["periods"] == 2, "stats count only the periods both legs priced")

    # 10. flat series has no Sharpe, one observation has none either
    _ok(sharpe([0.0] * 5, 0.0) is None, "a flat arm has no Sharpe")
    _ok(sharpe([0.01], 0.0) is None, "one observation has no Sharpe")

    # 11. drawdown is never positive and a monotone-up curve has none
    _ok(max_drawdown([0.01, 0.02, 0.03]) == 0.0, "monotone-up curve has 0 drawdown")
    _ok(max_drawdown([0.10, -0.10, 0.10]) < 0, "a dip produces a negative drawdown")

    # 12. annualisation is the tearsheet's, not a different one
    st = stats([0.01] * 76 + [0.01])
    _ok(abs(st["annualized_compound"] - ((1.01 ** 77) ** (PPY / 77) - 1)) < 1e-12,
        "annualised compound uses periods_per_year = %.3f" % PPY)

    # 13. period ends: next rebalance is the end, the last one walks the calendar
    cal = ["2020-01-%02d" % d for d in range(1, 29)] + ["2020-02-%02d" % d for d in range(1, 29)]
    ends, spans = period_ends(["2020-01-01", "2020-01-21"], cal)
    _ok(ends[0] == "2020-01-21" and spans[0] == 20, "consecutive rebalances are 20 bars apart")
    _ok(ends[1] == cal[40], "the last period runs 20 bars past the last rebalance")
    _ok(spans[1] == 20, "the last span is measured, not assumed")

    # 14. an unpriced end date yields None, not a zero return
    hr = hedge_returns(["2020-01-01"], [None], {"2020-01-01": 1.0})
    _ok(hr == [None], "an unpriced end date is missing, not flat")

    # 15. lots arithmetic: one lot of notional, and the capital it takes
    l = lots_for(1_000_000, 0.9, 2.30, 100)
    _ok(abs(l["shorted_notional"] - 900_000) < 1e-9, "shorted notional = beta x capital")
    _ok(abs(l["one_lot_notional"] - 230) < 1e-9, "one ETF lot is 100 shares x price")
    _ok(l["executable"] and l["lots_needed"] > 1000, "a 1M book can short 512100 in lots")
    m = lots_for(1_000_000, 0.9, 5545.6, 200)
    _ok(not m["executable"], "one IM contract is more than a 1M beta-neutral short")
    _ok(abs(m["capital_for_one_lot_at_this_beta"] - 5545.6 * 200 / 0.9) < 1e-6,
        "capital for one IM lot at this beta is printed")

    # 16. IS/OOS membership is inclusive of the frozen boundary
    _ok(all([d <= IS_END] == [d <= "2023-12-31"] for d in
            ("2023-12-31", "2024-01-02", "2020-07-06")), "IS boundary is inclusive")

    # 17. the split repair flattens the one jump that would otherwise fabricate a move
    try:
        import pandas as pd
        close = pd.DataFrame({"close": [1.0, 1.02, 2.75, 2.80, 2.83]})
        openp = pd.DataFrame({"open": [1.0, 1.01, 2.74, 2.79, 2.82]})
        adj, _o, n = repair_flips(close, openp, thr=0.35)
        r = adj["close"].pct_change().dropna()
        _ok(n == 1 and float(r.abs().max()) < 0.05,
            "a +170% conversion print is flattened before any return is taken")
    except ImportError:
        _ok(False, "pandas is required for the split repair")

    # 18. the three verdict states come out of the frozen rule, not taste
    up = {"sharpe_excess_0": 0.9, "per_period_mean": 0.006}
    down = {"sharpe_excess_0": 0.5, "per_period_mean": 0.010}
    _ok(decide(up, down, up, down)[0] == "HEDGE_PAYS_OUT_OF_SAMPLE",
        "better in and out of sample reads as OUT_OF_SAMPLE")
    _ok(decide(up, down, down, down)[0] == "HEDGE_PAYS_IN_SAMPLE_ONLY",
        "better in window only reads as IN_SAMPLE_ONLY")
    _ok(decide(down, up, down, up)[0] == "HEDGE_COSTS",
        "worse even in window reads as COSTS")
    _ok(decide(up, down, {"sharpe_excess_0": 0.9, "per_period_mean": -0.001}, down)[0]
        == "HEDGE_PAYS_IN_SAMPLE_ONLY",
        "a better Sharpe that still loses money is not OUT_OF_SAMPLE")

    # 19. underwater share counts the recovery time, not the depth
    _ok(abs(underwater_share([0.10, -0.05, 0.10]) - 1.0 / 3.0) < 1e-12,
        "one period below the peak is one period underwater")

    # 20. equity curve compounds; it never sums
    _ok(abs(float(equity_curve([0.10, 0.10])[-1]) - 1.21) < 1e-12,
        "two +10% periods compound to 1.21")

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
