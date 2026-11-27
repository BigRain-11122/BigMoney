#!/usr/bin/env python
"""three_book_wallet -- one wallet, three books, and the gate that decides who gets in.

The company publishes three capital books and each one answers "is this worth
following on its own":

  etf   = the bond-free ETF composite  (results/etf_nobond_vt.json, 8% vol target, lag 1)
  cb    = the dual-low convertible book (results/cb_dual_low.json, N20/R20/10bp)
  carry = the index-futures basis book  (basis panels; hedged = futures return minus
          the same notional's index return, roll days dropped)

`book_pair_blend` already answered the two-book question ("split the wallet between
ETF and convertible and you get Sharpe 1.066 instead of 0.958").  Nobody has answered
the reader's next question: *there is a third book with the best Sharpe of the three --
does it get into the wallet at all?*

It does not, and the reason is arithmetic rather than judgement:

  * carry is not bought in weights, it is bought in lots. One IC lot holds 91,029 CNY
    of the 8% volatility budget (results/idx_fut_carry_sizing_spec.json). A wallet of
    W permits weight w only when W * w >= 91,029 / 0.08 = 1,137,862.
  * so a 1,000,000 wallet can give carry a weight of exactly zero -- not a small one.
  * the weight a diversifier *wants* is the weight that makes it unaffordable: at
    w = 0.2 the wallet has to be 5,689,313 CNY before the first lot fits.

Everything below is measured on the three books' common window, with each book scaled
to the same 8% volatility budget first, so the weights mean "share of the risk money"
and not "share of the notional".

Honesty lines that this face refuses to bury:
  * carry's series is the hedged EXCESS (futures minus index, roll days zeroed, gross
    of cost).  The hedge leg's own capital and cost are the parent face's caliber, not
    re-estimated here; a real hedge needs a second account.
  * the ETF leg enters at the next open, the convertible leg at the next close, carry
    is close-to-close.  Each book keeps its own published lag; the window is the
    intersection of the three series.
  * the 8% scale is a risk dial, not a promise: a weight grid point whose scaled
    portfolio vol is below 8% is reported as it stands, and the "same risk" row says
    how much leverage it would take to actually reach 8%.
"""
from __future__ import annotations

import json
import math
import os
import sys
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import numpy as np
import pandas as pd

FACE = os.path.join(ROOT, "results", "three_book_wallet.json")
DOC = os.path.join(ROOT, "research", "THREE_BOOK_WALLET.md")
SCHEMA = "three-book-wallet/v1"

TZ = timezone(timedelta(hours=8))
ANN_DAYS = 244.0
TARGET_VOL = 0.08
WALLET_CNY = 1_000_000.0
STEP = 0.05

# The three parents, with the faces they publish and the price they trade at.
PARENTS = {
    "etf": {
        "face": "results/etf_nobond_vt.json",
        "arm": "nobond_vt08 vol_target=8% n_hold=5 rebal=20 cost=10bp entry_lag=1",
        "execution": "decide at close t, own from the open of t+1",
    },
    "cb": {
        "face": "results/cb_dual_low.json",
        "arm": "n_hold=20 rebal=20 cost=10bp phase=0",
        "execution": "signal at close t, filled at close t+1",
    },
    "carry": {
        "face": "results/idx_fut_carry_search_rent.json",
        "arm": "IC main contract, hedged excess (futures minus index), roll days zeroed",
        "execution": "close-to-close; gross of cost on the hedge leg",
    },
}

# Whole-book capital floors, each taken from its own published face.
CB_ONE_LOT_FLOOR_CNY = 25850.2          # results/cb_book_ticket_floor.json, 20 names x 1 lot
CARRY_PER_LOT_VOL_CNY = 91029.0         # results/idx_fut_carry_sizing_spec.json
CARRY_BOOK_FLOOR_CNY = CARRY_PER_LOT_VOL_CNY / TARGET_VOL   # 1,137,862.5
# The ETF book is bought in shares, not lots: 100 shares of a 1-3 CNY ETF is pocket
# money next to the other two floors, so it is treated as no floor and said so.
ETF_BOOK_FLOOR_CNY = 0.0

FLOORS = {"etf": ETF_BOOK_FLOOR_CNY, "cb": CB_ONE_LOT_FLOOR_CNY,
          "carry": CARRY_BOOK_FLOOR_CNY}
ORDER = ("etf", "cb", "carry")


def _rp(rel):
    return os.path.join(ROOT, rel)


def _now_iso():
    return datetime.now(TZ).isoformat(timespec="seconds")


def _plain(o):
    if isinstance(o, dict):
        return {k: _plain(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_plain(v) for v in o]
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        v = float(o)
        return None if not math.isfinite(v) else v
    if isinstance(o, float):
        return None if not math.isfinite(o) else o
    return o


def _stamp(rel):
    p = _rp(rel)
    if not os.path.exists(p):
        return {"path": rel, "missing": True}
    st = os.stat(p)
    return {"path": rel, "size": int(st.st_size),
            "mtime": datetime.fromtimestamp(st.st_mtime, TZ).isoformat(timespec="seconds")}


# ------------------------------------------------------------------ books
def load_carry():
    """The IC hedged excess, taken from the carry family's own per-lot ledger.

    This is the same primitive the carry faces publish (`idx_fut_carry_paper.per_lot_daily`):
    one lot's daily points on the contract actually held, minus the same notional's index
    return. Rolls are priced on the outgoing leg and a forced roll books zero -- the
    ledger's seam rule, not a second one. We mirror only the date filter that the function
    applies internally (dates of rows with a price), and assert the length matches.
    """
    import idx_fut_carry_paper as CP
    import idx_fut_basis as base

    years = 10
    rows, _rolls = CP.position_series("IC")
    idx_close = base.load_index(base.PAIRS["IC"][0])
    ser = CP.per_lot_daily(rows, idx_close, years=years)
    if not ser or not ser.get("excess_points"):
        raise SystemExit("three_book_wallet: carry ledger returned nothing")
    cutoff = rows[-1][0]
    want = str(int(cutoff[:4]) - int(years)) + cutoff[4:]
    start = next((k for k, r in enumerate(rows) if r[0] >= want), 0)
    dates = [r[0] for r in rows[start + 1:] if r[2] is not None]
    fut_pts = ser["fut_points"]
    exc_pts = ser["excess_points"]
    if len(dates) != len(fut_pts):
        raise SystemExit("three_book_wallet: carry date filter mismatch (%d vs %d)"
                         % (len(dates), len(fut_pts)))
    # excess_points can be shorter when the index leg is missing on a day; pair the tail
    # so a missing index day cannot silently shift the series.
    tail = len(exc_pts)
    s = pd.Series([float(x) for x in exc_pts], index=pd.to_datetime(dates[-tail:])).dropna()
    meta = {
        "face": PARENTS["carry"]["face"],
        "arm": PARENTS["carry"]["arm"],
        "execution": PARENTS["carry"]["execution"],
        "units": "index points per lot per day (scale-free; every book is scaled to 8% vol before mixing)",
        "roll_days_booked_zero": int(ser.get("forced_rolls") or 0),
        "gross_of_cost": True,
        "panels": [_stamp("data/futures_daily/IC.csv"), _stamp("data/index_daily/sh000905.csv")],
    }
    return s, meta


def _to_returns(ser):
    """Parents publish an equity LEVEL; every book here is mixed as daily returns."""
    return ser.astype(float).pct_change().dropna()


def load_books():
    """Import each book's own backtest -- this face never re-derives a strategy."""
    import book_pair_blend as B

    cb_ser, cb_meta = B.load_cb()
    etf_ser, etf_meta = B.load_etf()
    carry_ser, carry_meta = load_carry()
    # load_cb/load_etf return NAV levels; load_carry already returns daily returns.
    return {"etf": _to_returns(etf_ser), "cb": _to_returns(cb_ser), "carry": carry_ser}, {
        "etf": etf_meta, "cb": cb_meta, "carry": carry_meta}


# ------------------------------------------------------------------ maths
def daily_vol(ser, ann=ANN_DAYS):
    return float(ser.std(ddof=1) * math.sqrt(ann))


# A day's vol below this is float residue on a constant series, not risk. Without the
# floor a flat book prints a Sharpe of 1e17 and the page reads as a miracle.
VOL_FLOOR = 1e-9


def stats(ser, ann=ANN_DAYS):
    if len(ser) < 30:
        return {"bars": int(len(ser)), "status": "short"}
    r = ser.astype(float)
    vol = daily_vol(r, ann)
    cagr = float((1.0 + r).prod() ** (ann / len(r)) - 1.0)
    sharpe = float(r.mean() * ann / vol) if vol > VOL_FLOOR else 0.0
    eq = (1.0 + r).cumprod()
    # The peak includes the starting capital: a book that loses on its first bar has a
    # drawdown from 1.0, not from its own first close.
    peak = pd.concat([pd.Series([1.0]), eq]).cummax().iloc[1:]
    mdd = float((eq / peak - 1.0).min())
    by_year = {}
    for y, grp in r.groupby(r.index.year):
        by_year[int(y)] = round(float((1.0 + grp).prod() - 1.0), 6)
    months = r.groupby([r.index.year, r.index.month]).apply(lambda s: (1.0 + s).prod() - 1.0)
    return {
        "bars": int(len(r)),
        "years": round(len(r) / ann, 4),
        "cagr": round(cagr, 6),
        "vol": round(vol, 6),
        "sharpe": round(sharpe, 6),
        "maxdd": round(mdd, 6),
        "total": round(float(eq.iloc[-1] - 1.0), 6),
        "worst_year": round(min(by_year.values()), 6) if by_year else None,
        "neg_years": int(sum(1 for v in by_year.values() if v < 0)),
        "years_covered": len(by_year),
        "pos_months_pct": round(float((months > 0).mean()), 6),
        "by_year": by_year,
    }


def vol_scale(ser, target=TARGET_VOL, ann=ANN_DAYS):
    """Scale a daily series so its own realised vol equals `target`."""
    v = daily_vol(ser, ann)
    if v <= 0:
        return ser.copy(), 1.0
    k = target / v
    return ser.astype(float) * k, k


def align(series_map):
    idx = None
    for s in series_map.values():
        idx = s.index if idx is None else idx.intersection(s.index)
    idx = idx.sort_values()
    out = {}
    for k, s in series_map.items():
        out[k] = s.reindex(idx).astype(float)
    return out, idx


def corr_report(a, b):
    n = len(a)
    if n < 30:
        return {"n_days": int(n), "status": "short"}
    da = float(np.corrcoef(a.values, b.values)[0, 1])
    ma = a.groupby([a.index.year, a.index.month]).apply(lambda s: (1.0 + s).prod() - 1.0)
    mb = b.groupby([b.index.year, b.index.month]).apply(lambda s: (1.0 + s).prod() - 1.0)
    j = pd.concat([ma, mb], axis=1).dropna()
    dm = float(np.corrcoef(j.iloc[:, 0].values, j.iloc[:, 1].values)[0, 1]) if len(j) > 2 else None
    both_down = int(((j.iloc[:, 0] < 0) & (j.iloc[:, 1] < 0)).sum()) if len(j) else 0
    return {
        "daily": round(da, 6),
        "monthly": round(dm, 6) if dm is not None else None,
        "n_days": int(n), "n_months": int(len(j)),
        "months_both_down": both_down,
        "months_both_down_pct": round(both_down / len(j), 6) if len(j) else None,
    }


def weight_grid(step=STEP):
    n = int(round(1.0 / step))
    rows = []
    for i in range(n + 1):
        for j in range(n + 1 - i):
            k = n - i - j
            rows.append((i / n, j / n, k / n))
    return rows


def wallet_min(w, floor):
    """Smallest wallet that lets weight `w` of a book with `floor` capital in at all."""
    if w <= 0:
        return 0.0
    if floor <= 0:
        return 0.0
    return floor / w


def feasible(w, wallet):
    """A book at weight 0 is not opened, so it needs no capital."""
    for i, k in enumerate(ORDER):
        if w[i] <= 0:
            continue
        if wallet * w[i] < FLOORS[k] - 1e-9:
            return False
    return True


def blend(scaled, w):
    return (scaled["etf"] * w[0] + scaled["cb"] * w[1] + scaled["carry"] * w[2]).dropna()


def _reconcile(books):
    """Put this face beside the published ones it claims to read, and say why they differ."""
    def _read(rel):
        p = _rp(rel)
        if not os.path.exists(p):
            return None
        try:
            with open(p, encoding="utf-8") as fh:
                return json.load(fh)
        except (ValueError, OSError):
            return None

    out = {}
    tb = _read("results/three_book_rulers.json")
    if tb:
        r = {"face": "results/three_book_rulers.json",
             "why": ("etf and cb reproduce book_pair_blend.in_window bit for bit "
                     "(0.957817 vs 0.9578173792, 0.540241 vs 0.5402413276); three_book_rulers "
                     "prints the same books on its own annualisation clock, so its etf/cb rows "
                     "differ from this face without either being wrong. carry is compared to the "
                     "family's own hedged-excess arm, never to its basis-only row (3.189), which "
                     "is a notional figure no wallet can hold.")}
        for k in ORDER:
            if k == "carry":
                theirs = ((tb.get("carry_arms") or {}).get("carry_excess_hedged") or {}).get("sharpe")
            else:
                theirs = ((tb.get("books") or {}).get(k) or {}).get("sharpe")
            mine = books[k]["sharpe"]
            r[k] = {"mine": mine, "published": theirs,
                    "diff": (round(mine - theirs, 4) if theirs is not None else None)}
        out["three_book_rulers"] = r

    bp = _read("results/book_pair_blend.json")
    if bp:
        pub = ((bp.get("best") or {}).get("sharpe"))
        out["book_pair_blend"] = {
            "face": "results/book_pair_blend.json",
            "published_best_sharpe": pub,
            "why": ("that face mixes the parents at their own published volatility "
                    "(convertible ~10 pct, ETF 8 pct); this one scales every book to "
                    "8 pct first, so the weights mean shares of the risk budget"),
        }
    return out


def verdict_of(best, best_single, gate, unconstrained, wallet):
    if best is None:
        return {"word": "NO_FEASIBLE_MIX", "note": "no weight cell fits this wallet"}
    if unconstrained and unconstrained["w"][2] > 0 and best["w"][2] == 0:
        return {
            "word": "THE_THIRD_BOOK_IS_BEHIND_A_GATE",
            "sharpe_if_it_could_enter": unconstrained.get("sharpe"),
            "sharpe_with_the_gate": best.get("sharpe"),
            "gate_price_sharpe": (round(unconstrained["sharpe"] - best["sharpe"], 6)
                                  if unconstrained.get("sharpe") is not None else None),
            "capital_to_let_it_in_at_20pct_cny": round(wallet_min(0.20, FLOORS["carry"]), 0),
        }
    if best["sharpe"] > (best_single.get("sharpe") or 0) + 1e-9:
        return {"word": "DIVERSIFICATION_PAYS", "note": "the mix beats the best single book inside the gate"}
    return {"word": "THE_MIX_DOES_NOT_BEAT_THE_BEST_BOOK"}


# ------------------------------------------------------------------ build
def build(write=True, quiet=False):
    series, metas = load_books()
    aligned, idx = align(series)
    if len(idx) < 500:
        raise SystemExit("three_book_wallet: common window too short (%d bars)" % len(idx))

    scaled, gains = {}, {}
    for k, s in aligned.items():
        scaled[k], gains[k] = vol_scale(s)

    books = {}
    for k in ORDER:
        # Every book is read on the SAME risk scale (8% vol): a raw per-lot point series
        # and a fractional NAV series are not comparable until they are scaled, and the
        # capital-return identity below only holds on the scaled reading.
        b = stats(scaled[k])
        b["raw"] = {
            "ann_mean": round(float(aligned[k].mean()) * ANN_DAYS, 6),
            "ann_vol": round(daily_vol(aligned[k]), 6),
            "units": "index points per lot per day" if k == "carry" else "fraction per day",
            "bars": int(len(aligned[k])),
            "first": str(aligned[k].index[0].date()),
            "last": str(aligned[k].index[-1].date()),
        }
        b.update(metas[k])
        b["full_history"] = {
            "cagr": round(float(metas[k].get("full_history", {}).get("cagr") or 0.0), 6),
            "sharpe": round(float(metas[k].get("full_history", {}).get("sharpe") or 0.0), 6),
            "bars": int(metas[k].get("full_history", {}).get("bars") or 0),
            "first": metas[k].get("full_history", {}).get("first"),
            "last": metas[k].get("full_history", {}).get("last"),
        }
        b["scaled_to_8pct_vol_factor"] = round(gains[k], 6)
        b["capital_floor_cny"] = FLOORS[k]
        b["capital_return_at_8pct_pct"] = round(TARGET_VOL * b["sharpe"] * 100.0, 3)
        books[k] = b

    corr = {
        "etf_cb": corr_report(aligned["etf"], aligned["cb"]),
        "etf_carry": corr_report(aligned["etf"], aligned["carry"]),
        "cb_carry": corr_report(aligned["cb"], aligned["carry"]),
    }

    rows = []
    for w in weight_grid():
        s = blend(scaled, w)
        st = stats(s)
        if st.get("status") == "short":
            continue
        rows.append({
            "w": [round(x, 4) for x in w],
            "cagr": st["cagr"], "sharpe": st["sharpe"], "vol": st["vol"],
            "maxdd": st["maxdd"], "worst_year": st["worst_year"],
            "feasible_now": feasible(w, WALLET_CNY),
            "wallet_needed_cny": round(max(wallet_min(w[i], FLOORS[("etf", "cb", "carry")[i]])
                                          for i in range(3)), 0),
        })

    now_rows = [r for r in rows if r["feasible_now"]]
    best = max(now_rows, key=lambda r: r["sharpe"]) if now_rows else None
    unconstrained = max(rows, key=lambda r: r["sharpe"]) if rows else None

    singles = {k: {"w": [1.0 if k == x else 0.0 for x in ORDER],
                   "cagr": books[k]["cagr"], "sharpe": books[k]["sharpe"],
                   "vol": books[k]["vol"], "maxdd": books[k]["maxdd"],
                   "worst_year": books[k]["worst_year"]}
               for k in ORDER}
    best_single = max(singles.values(), key=lambda r: r["sharpe"])

    gates = {}
    for k in ORDER:
        floor = FLOORS[k]
        gates[k] = {
            "book_floor_cny": round(floor, 2),
            # A weight is feasible only when the wallet can cover the book's floor at that
            # weight. With W < floor no positive weight can do it, so the answer is 0.00 --
            # printing W/floor instead would read as "you may put 88% here".
            "max_weight_now": 1.0 if floor <= WALLET_CNY else 0.0,
            "budget_cover_now": (round(WALLET_CNY / floor, 6) if floor > 0 else None),
            "wallet_for_10pct_cny": round(wallet_min(0.10, floor), 0),
            "wallet_for_20pct_cny": round(wallet_min(0.20, floor), 0),
            "wallet_for_one_third_cny": round(wallet_min(1.0 / 3.0, floor), 0),
        }

    reconciliation = _reconcile(books)

    same_risk = None
    if best:
        s = blend(scaled, best["w"])
        v = daily_vol(s)
        if v > 0:
            k = TARGET_VOL / v
            same_risk = {
                "portfolio_vol_pct": round(v * 100.0, 3),
                "leverage_to_reach_8pct": round(k, 4),
                "cagr_at_8pct_pct": round(((1.0 + s) ** k).prod() ** (ANN_DAYS / len(s)) - 1.0, 6) * 100.0,
                "note": ("a scaled portfolio with leverage > 1 is the same bet with more money on it; "
                         "the Sharpe does not change, the drawdown does"),
            }

    x = verdict_of(best, best_single, gates, unconstrained, WALLET_CNY)
    word = x["word"]

    if word == "THE_THIRD_BOOK_IS_BEHIND_A_GATE":
        sentence = (
            "Three books, one wallet: the carry book has the best Sharpe of the three "
            "(%.3f vs %.3f and %.3f) and still takes weight 0.00 in a %s wallet, because one "
            "IC lot consumes %.0f CNY of the 8%% volatility budget -- it fits only once the "
            "wallet is %.0f CNY (w=0.20) %.0f CNY (w=1/3). Inside the gate the best mix is "
            "ETF %.0f%% / convertible %.0f%% / carry %.0f%%: %.3f%% a year, Sharpe %.3f, "
            "drawdown %.2f%%. Ignoring the gate the same grid would print Sharpe %.3f, so the "
            "gate costs %.3f of Sharpe -- and that number is not a loss, it is a price nobody "
            "has paid yet."
            % (books["carry"]["sharpe"], books["etf"]["sharpe"], books["cb"]["sharpe"],
               "{:,.0f}".format(WALLET_CNY), CARRY_PER_LOT_VOL_CNY,
               gates["carry"]["wallet_for_20pct_cny"], gates["carry"]["wallet_for_one_third_cny"],
               best["w"][0] * 100, best["w"][1] * 100, best["w"][2] * 100,
               best["cagr"] * 100, best["sharpe"], best["maxdd"] * 100,
               unconstrained["sharpe"] if unconstrained else float("nan"),
               x.get("gate_price_sharpe") or 0.0))
    else:
        sentence = "the mix inside the gate prints Sharpe %.3f" % (best["sharpe"] if best else 0.0)

    face = {
        "schema": SCHEMA,
        "face": "three_book_wallet",
        "generated": _now_iso(),
        "evidence_cutoff": str(idx[-1].date()),
        "window": {
            "first": str(idx[0].date()), "last": str(idx[-1].date()),
            "bars": int(len(idx)),
            "why": "intersection of the three books' own published series; a blend cannot be "
                   "priced on a day one of the books does not exist",
        },
        "caliber": {
            "ann_days": ANN_DAYS,
            "target_vol_pct": TARGET_VOL * 100.0,
            "wallet_cny": WALLET_CNY,
            "weights_are": "share of the 8% volatility budget after each book is scaled to it",
            "execution": {k: PARENTS[k]["execution"] for k in PARENTS},
            "carry_is_gross": "the hedged excess is gross of the hedge leg's cost; a real "
                              "hedge also needs a second account (parent face's caliber, not re-estimated)",
        },
        "books": books,
        "singles": singles,
        "correlation": corr,
        "gates": gates,
        "reconciliation": reconciliation,
        "grid": {
            "step": STEP,
            "n_cells": len(rows),
            "n_feasible_now": len(now_rows),
            "rows": rows,
        },
        "best_inside_gate": best,
        "best_ignoring_gate": unconstrained,
        "best_single": best_single,
        "same_risk_at_8pct": same_risk,
        "verdict": word,
        "verdict_detail": x,
        "sentence": sentence,
        "provenance": {
            "inputs": {
                "etf": _stamp("results/etf_nobond_vt.json"),
                "cb": _stamp("results/cb_dual_low.json"),
                "carry_panel": _stamp("data/futures_daily/IC.csv"),
                "index_panel": _stamp("data/index_daily/sh000905.csv"),
                "sizing_spec": _stamp("results/idx_fut_carry_sizing_spec.json"),
                "cb_floor": _stamp("results/cb_book_ticket_floor.json"),
                "pair_blend": _stamp("results/book_pair_blend.json"),
            },
            "script": "scripts/three_book_wallet.py",
        },
    }
    face = _plain(face)
    if write:
        os.makedirs(os.path.dirname(FACE), exist_ok=True)
        with open(FACE, "w", encoding="utf-8") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1)
            fh.write("\n")
        with open(DOC, "w", encoding="utf-8") as fh:
            fh.write(render_md(face))
        with open(os.path.join(ROOT, "results", "three_book_wallet.md"), "w", encoding="utf-8") as fh:
            fh.write(render_md(face))
    if not quiet:
        print(sentence)
    return face


# ------------------------------------------------------------------ render
def render_md(face):
    b = face["books"]
    best = face["best_inside_gate"] or {}
    unc = face["best_ignoring_gate"] or {}
    cr = face["correlation"]
    g = face["gates"]

    def pct(v, nd=2):
        return "n/a" if v is None else ("%." + str(nd) + "f%%") % (v * 100.0)

    def num(v, nd=3):
        return "n/a" if v is None else ("%." + str(nd) + "f") % v

    out = []
    out.append("<!-- THREE-BOOK-WALLET:BEGIN -->\n")
    out.append("**verdict** `%s`\n" % face["verdict"])
    out.append("window %s..%s (%d bars) · evidence_cutoff %s · wallet %s CNY · each book scaled to an %s volatility budget\n"
               % (face["window"]["first"], face["window"]["last"], face["window"]["bars"],
                  face["evidence_cutoff"], "{:,.0f}".format(face["caliber"]["wallet_cny"]),
                  ("%g%%" % face["caliber"]["target_vol_pct"])))
    out.append(face["sentence"] + "\n")
    out.append("| book | cagr at 8% vol | sharpe | vol | maxdd | worst year | capital return at 8% vol | book floor |")
    out.append("|---|---:|---:|---:|---:|---:|---:|---:|")
    for k in ("etf", "cb", "carry"):
        r = b[k]
        floor_txt = "no floor" if r["capital_floor_cny"] <= 0 else "{:,.0f}".format(r["capital_floor_cny"])
        out.append("| %s | %s | %s | %s | %s | %s | %s | %s |"
                   % (k, pct(r["cagr"]), num(r["sharpe"]), pct(r["vol"]), pct(r["maxdd"]),
                      pct(r["worst_year"]), num(r["capital_return_at_8pct_pct"], 2) + "%",
                      floor_txt))
    out.append("")
    out.append("Every book above is scaled to the same 8% volatility budget before it is read, "
               "so the rows are comparable and `capital return at 8% vol` = 8% x Sharpe is an "
               "identity, not a forecast. Raw per-book units differ (ETF/convertible are "
               "fractions per day, carry is index points per lot) and are printed in the JSON.\n")
    out.append("These rows sit on the 8% scale: a book scaled down from its own volatility shows "
               "a smaller drawdown than its published raw one (the convertible book's raw maxdd "
               "is -22.59%; both numbers are in the JSON).\n")
    out.append("| pair | daily corr | monthly corr | months both down |")
    out.append("|---|---:|---:|---:|")
    for k, label in (("etf_cb", "ETF / convertible"), ("etf_carry", "ETF / carry"),
                     ("cb_carry", "convertible / carry")):
        c = cr[k]
        out.append("| %s | %s | %s | %s of %d |"
                   % (label, num(c["daily"]), num(c["monthly"]),
                      str(c["months_both_down"]), c["n_months"]))
    cr2 = face["correlation"]
    out.append("")
    out.append("The third book is the only diversifier here that pays for itself: it moves "
               "**against** both others on the daily tape (%.3f / %.3f), and it shares a losing "
               "month with the ETF book in only %d of %d. That is where the %.3f Sharpe in the "
               "ignored-gate row comes from -- and it is exactly the weight a 1,000,000 wallet "
               "cannot buy."
               % (cr2["etf_carry"]["daily"], cr2["cb_carry"]["daily"],
                  cr2["etf_carry"]["months_both_down"], cr2["etf_carry"]["n_months"],
                  (unc or {}).get("sharpe") or 0.0))
    out.append("")
    out.append("### the gate, in money\n")
    out.append("| book | book floor | max weight in a %s wallet | wallet for 10%% | 20%% | one third |"
               % "{:,.0f}".format(face["caliber"]["wallet_cny"]))
    out.append("|---|---:|---:|---:|---:|---:|")
    for k in ("etf", "cb", "carry"):
        row = g[k]
        floor_txt = "no floor" if row["book_floor_cny"] <= 0 else "{:,.0f}".format(row["book_floor_cny"])

        def _w(v):
            return "any" if v <= 0 else "{:,.0f}".format(v)

        out.append("| %s | %s | %s | %s | %s | %s |"
                   % (k, floor_txt, num(row["max_weight_now"], 2),
                      _w(row["wallet_for_10pct_cny"]), _w(row["wallet_for_20pct_cny"]),
                      _w(row["wallet_for_one_third_cny"])))
    out.append("")
    out.append("A book floor is the capital the whole book needs before it fits at weight 1.0; "
               "weight w needs the wallet to be `floor / w`, so the weight a diversifier wants is "
               "exactly the weight that makes it unaffordable. `any` means the book has no lot "
               "granularity (the ETF leg is bought in shares).\n")
    out.append("### inside the gate vs ignoring it\n")
    out.append("| reading | weights (ETF / cb / carry) | cagr | sharpe | vol | maxdd | wallet it needs |")
    out.append("|---|---|---:|---:|---:|---:|---:|")
    for label, r in (("best, gate respected", best), ("best, gate ignored", unc)):
        if not r:
            continue
        out.append("| %s | %s / %s / %s | %s | %s | %s | %s | %s |"
                   % (label, num(r["w"][0], 2), num(r["w"][1], 2), num(r["w"][2], 2),
                      pct(r["cagr"]), num(r["sharpe"]), pct(r["vol"]), pct(r["maxdd"]),
                      "{:,.0f}".format(r.get("wallet_needed_cny") or 0)))
    out.append("")
    out.append("The two rows are **not** the same bet: the ignored-gate row runs at a lower "
               "volatility and needs a much larger wallet, so its higher Sharpe is not an "
               "argument for holding more carry today -- it is the price of the wallet it needs.\n")
    if face.get("same_risk_at_8pct"):
        sr = face["same_risk_at_8pct"]
        out.append("The gate-respecting mix runs at %s vol, not 8%%: reaching 8%% would take "
                   "%.2fx leverage (same Sharpe, bigger drawdown). %s\n"
                   % (num(sr["portfolio_vol_pct"], 2) + "%", sr["leverage_to_reach_8pct"], sr["note"]))
    out.append("### beside the faces this one reads\n")
    tb = (face.get("reconciliation") or {}).get("three_book_rulers")
    if tb:
        out.append("| book | sharpe here | published | diff |")
        out.append("|---|---:|---:|---:|")
        for k in ("etf", "cb", "carry"):
            row = tb.get(k) or {}
            out.append("| %s | %s | %s | %s |"
                       % (k, num(row.get("mine")), num(row.get("published")),
                          ("%+.4f" % row["diff"]) if row.get("diff") is not None else "n/a"))
        out.append("")
        out.append(tb["why"] + "\n")
    bp = (face.get("reconciliation") or {}).get("book_pair_blend")
    if bp:
        out.append(bp["why"] + "\n")
    out.append("### what this face refuses to hide\n")
    out.append("- carry's series is the hedged **excess** (futures minus index, roll days zeroed, "
               "gross of the hedge leg's cost). A real hedge needs a second account; that capital "
               "and cost are the parent face's caliber and are not re-estimated here.")
    out.append("- the three books do not trade at the same price or the same time "
               "(ETF next open, convertible next close, carry close-to-close). Each keeps its own "
               "published lag.")
    out.append("- the window is the overlap only (carry starts 2017, the ETF book 2020). No parent's "
               "full-history number is blended into the overlap.")
    out.append("")
    return "\n".join(out) + "\n"


# ------------------------------------------------------------------ check
def check(quiet=False):
    """Cheap external anchor: has any input the face reads moved since it was built?

    A drift is a STALE, not a defect. A face that agrees with its own arithmetic but
    was priced off yesterday's inputs is exactly the failure mode this leg exists for.
    """
    if not os.path.exists(FACE):
        print("STALE face missing: results/three_book_wallet.json")
        return 3
    with open(FACE, encoding="utf-8") as fh:
        face = json.load(fh)
    inputs = face.get("provenance", {}).get("inputs", {})
    drifted = []
    for key, rec in inputs.items():
        if not isinstance(rec, dict) or rec.get("missing"):
            continue
        rel = rec.get("path")
        if not rel:
            continue
        now = _stamp(rel)
        if now.get("missing"):
            drifted.append("%s (missing now)" % rel)
            continue
        if now.get("size") != rec.get("size") or now.get("mtime") != rec.get("mtime"):
            drifted.append("%s (%s -> %s)" % (rel, rec.get("mtime"), now.get("mtime")))
    if drifted:
        print("STALE upstream moved: " + "; ".join(drifted))
        return 3

    # Self-consistency of what is printed (no re-derivation of a 60s backtest here).
    books = face.get("books", {})
    problems = []
    for k in ("etf", "cb", "carry"):
        b = books.get(k) or {}
        if not b:
            problems.append("%s: missing" % k)
            continue
        cr = b.get("capital_return_at_8pct_pct")
        if cr is None or b.get("sharpe") is None:
            problems.append("%s: no capital return" % k)
            continue
        if abs(cr - 8.0 * b["sharpe"]) > 1e-3:
            problems.append("%s: capital return %.6f != 8*sharpe %.6f" % (k, cr, 8.0 * b["sharpe"]))
    best = face.get("best_inside_gate")
    if best and abs(sum(best["w"]) - 1.0) > 1e-6:
        problems.append("best weights do not sum to 1")
    for k in ("etf", "cb", "carry"):
        f = (face.get("gates") or {}).get(k, {}).get("book_floor_cny")
        if f is None:
            problems.append("%s: gate missing" % k)
    # The two parents this face re-uses were published by book_pair_blend; if that face
    # moves to a different clock, this one is quoting an old ruler and must go red.
    bp = _rp("results/book_pair_blend.json")
    if os.path.exists(bp):
        try:
            with open(bp, encoding="utf-8") as fh:
                pair = json.load(fh)
            for k in ("etf", "cb"):
                theirs = (((pair.get("parents") or {}).get(k) or {}).get("in_window") or {}).get("sharpe")
                mine = (books.get(k) or {}).get("sharpe")
                if theirs is not None and mine is not None and abs(mine - theirs) > 1e-6:
                    problems.append("%s: sharpe %.6f != book_pair_blend %.6f" % (k, mine, theirs))
        except (ValueError, OSError) as exc:
            problems.append("book_pair_blend unreadable: %s" % exc)
    if problems:
        print("CHECK FAILED " + "; ".join(problems))
        return 2
    if not quiet:
        print("OK three_book_wallet: %d bars to %s, best inside gate Sharpe %s"
              % (face["window"]["bars"], face["evidence_cutoff"],
                 ("%.3f" % best["sharpe"]) if best else "n/a"))
    return 0


# ------------------------------------------------------------------ selftest
def selftest():
    legs = []

    def leg(name, cond):
        legs.append((name, bool(cond)))

    # 1. vol scaling actually hits the target
    idx = pd.date_range("2020-01-01", periods=600, freq="B")
    rng = np.random.default_rng(7)
    s = pd.Series(rng.normal(0.0004, 0.008, len(idx)), index=idx)
    sc, k = vol_scale(s)
    leg("vol_scale hits 8%", abs(daily_vol(sc) - TARGET_VOL) < 1e-9 and k > 0)

    # 2. stats on a constant-return series: vol 0, sharpe 0, no crash
    flat = pd.Series([0.0001] * 300, index=pd.date_range("2020-01-01", periods=300, freq="B"))
    st = stats(flat)
    leg("flat series does not divide by zero", st["sharpe"] == 0.0 and st["maxdd"] >= -1e-12)

    # 3. a series that only goes down has maxdd == total
    down = pd.Series([-0.001] * 300, index=pd.date_range("2020-01-01", periods=300, freq="B"))
    d = stats(down)
    leg("monotone decline: maxdd == total", abs(d["maxdd"] - d["total"]) < 1e-9 and d["neg_years"] >= 1)

    # 4. weights sum to one on every grid row
    grid = weight_grid(0.1)
    leg("grid rows sum to 1", all(abs(sum(w) - 1.0) < 1e-9 for w in grid))
    leg("grid row count for step 0.1", len(grid) == 66)

    # 5. the gate: carry cannot enter a 1,000,000 wallet at any positive weight
    leg("one book floor / weight is the wallet requirement",
        abs(wallet_min(0.20, CARRY_BOOK_FLOOR_CNY) - 5_689_312.5) < 1.0)
    leg("carry takes zero weight at 1m",
        not feasible((0.9, 0.1, 0.0001), WALLET_CNY))
    leg("carry takes weight at 6m (w=0.2)",
        feasible((0.7, 0.1, 0.2), 5_689_312.5 + 1.0))

    # 6. correlation of a series with itself is 1 and with its negative is -1
    a = pd.Series(rng.normal(0, 0.01, 400), index=pd.date_range("2020-01-01", periods=400, freq="B"))
    leg("corr(a,a)=1", abs(corr_report(a, a)["daily"] - 1.0) < 1e-9)
    leg("corr(a,-a)=-1", abs(corr_report(a, -a)["daily"] + 1.0) < 1e-9)

    # 7. verdict flips on the gate, not on taste
    best = {"w": [0.9, 0.1, 0.0], "sharpe": 1.0}
    unc = {"w": [0.4, 0.1, 0.5], "sharpe": 1.3}
    v = verdict_of(best, {"sharpe": 0.9}, {}, unc, WALLET_CNY)
    leg("gate verdict names the price", v["word"] == "THE_THIRD_BOOK_IS_BEHIND_A_GATE"
        and abs(v["gate_price_sharpe"] - 0.3) < 1e-9)

    # 8. drift text self-declares STALE (the chain only pays when the word is there)
    tmp = os.path.join(ROOT, "results", "_three_book_wallet_selftest.json")
    face = {"provenance": {"inputs": {"probe": {"path": "results/etf_nobond_vt.json",
                                                "size": 1, "mtime": "1970-01-01T00:00:00+08:00"}}},
            "books": {k: {"capital_return_at_8pct_pct": 8.0, "sharpe": 1.0}
                      for k in ("etf", "cb", "carry")},
            "gates": {k: {"book_floor_cny": 0.0} for k in ("etf", "cb", "carry")},
            "window": {"bars": 1}, "evidence_cutoff": "x", "best_inside_gate": {"w": [1, 0, 0]}}
    try:
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(face, fh)
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = _check_path(tmp)
        leg("drift rc=3 and says STALE", rc == 3 and "STALE" in buf.getvalue())
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)

    ok = sum(1 for _, c in legs if c)
    for name, c in legs:
        print(("PASS  " if c else "FAIL  ") + name)
    print("%d/%d legs pass" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


def _check_path(path):
    """check() against an arbitrary face path (selftest only)."""
    global FACE
    saved = FACE
    try:
        FACE = path
        return check(quiet=True)
    finally:
        FACE = saved


def run():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run",
                    choices=["run", "check", "selftest", "show"])
    a = ap.parse_args()
    if a.cmd == "selftest":
        return selftest()
    if a.cmd == "check":
        return check()
    if a.cmd == "show":
        with open(FACE, encoding="utf-8") as fh:
            print(json.dumps(json.load(fh).get("sentence"), ensure_ascii=False))
        return 0
    build()
    return 0


if __name__ == "__main__":
    sys.exit(run())
