#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A-share residual veto -- the capital line: how much money opens the book.

Why this face exists
--------------------
r1955 (scripts/astock_veto_holdable_width.py) priced the veto at 30/50/100
names and returned VETO_NOT_SEPARABLE_AT_WIDTH.  Two things came out of it at
once: the veto itself is still there (pure pool effect on random books
+0.24pp/20d, t=2.53), and the book a 1,000,000 account can actually buy
(top-50 by market cap) pays -16pp/yr versus a random 50 -- a size bet the
reader never asked for.  So the published +3.4pp/yr still has no owner: it
lives in a ~2,293-name book, and the one book this company can hold loses money.

That is exactly the hole r1780 closed on the futures side -- "a correct zero is
not a ticket": a rule that says "do not own the bad tail" must also say **how
much money opens the thing you should own**.  This face prices the money.

What it prints
--------------
Same panel, same rebalance dates (stride 20), same eligibility, same score and
same 2 x 8bp x turnover cost -- all imported from the two parent modules, never
re-declared.  Only the width (and therefore the money) changes:

    capital_min_lot        sum of one 100-share lot across the book
                           (the cheapest way to own every name once)
    capital_equal_all      N x the most expensive one-lot
                           (money at which equal weights give EVERY name a lot)
    capital_equal_typical  N x the median one-lot
    over_budget_share      share of the book whose one lot exceeds C/N

printed for both pools (A = whole eligible pool, B = veto pool q<4) at
50/100/200/400/800/1600 and FULL.

Criteria frozen before the first run (nothing here is tuned on the numbers)
--------------------------------------------------------------------------
  CAPITAL_LEVELS   1M / 3M / 5M / 10M -- the range this company could plausibly
                   put behind a single book.
  HOLDABLE_SHARE   2.0% -- a width counts as "holdable at C" when the median
                   share of names whose one lot exceeds C/N is at most one name
                   in fifty.  Above that, equal weights are a fiction.
  T_MIN            2.0, the same bar both parent faces used.
  CONTROL          FULL-width A/B must reproduce the parent's published
                   whole-pool arms (6.92% / 10.34%) within 0.60pp.  If they do
                   not, the ruler is wrong and this face says CONTROL_MISMATCH
                   instead of publishing a ladder.

verdicts
  CONTROL_MISMATCH              FULL arms do not reproduce the parent
  BOOK_OPENS_NEAR_THE_PAGE      whole-book equal-weight capital <= 3,000,000 --
                                the published +3.4pp is one top-up away
  BOOK_OPENS_WITH_MORE_CAPITAL  <= 10,000,000
  BOOK_NOT_OPENABLE             > 10,000,000 -- this account class cannot own it
  width side: VETO_PAYS_FROM_WIDTH_<n> / VETO_PAYS_ONLY_AT_FULL_BOOK /
              VETO_NEVER_SEPARABLE

usage: python scripts/astock_veto_open_capital.py [run|check|selftest]
"""

import argparse
import json
import os
import sys
from datetime import datetime

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from astock_resid_reversal_probe import (  # noqa: E402
    COST_ONE_SIDE,
    FIRST_DATE,
    HOLD,
    LOOKBACK_BETA,
    MIN_AMOUNT_20D,
    MIN_BARS,
    load_panel,
    daily_returns,
    market_return,
)
from astock_resid_veto_layer import (  # noqa: E402
    _paired,
    _turnover,
    panel_frontier,
    score_slice,
    staleness,
)
from astock_veto_holdable_width import (  # noqa: E402
    _nets,
    _cagr,
)

OUT = os.path.join(ROOT, "results", "astock_veto_open_capital.json")
PANEL_PER = os.path.join(ROOT, "data", "astock_daily", "per")

LADDER = (50, 100, 200, 400, 800, 1600)
CAPITAL_LEVELS = (1000000, 3000000, 5000000, 10000000)
HOLDABLE_SHARE = 0.02
T_MIN = 2.0
LOT = 100

# the parent face's published whole-pool readings; the control leg replays them
PARENT_WHOLE_POOL_CAGR = 0.0692
PARENT_VETO_CAGR = 0.1034
CONTROL_TOL = 0.0060


# --------------------------------------------------------------- pure arithmetic
def lot_capital(prices, names, levels=CAPITAL_LEVELS, lot=LOT):
    """Money required to hold `names` equal-weighted slots of this book.

    Three different questions, three different answers -- kept separate on
    purpose (r1813: weight is not an order):
      capital_min_lot        own every name once, unequal share counts
      capital_equal_all      equal weights, and even the priciest name gets a lot
      capital_equal_typical  N x the median lot -- the typical requirement
    """
    p = np.asarray(prices, dtype=float)
    p = p[np.isfinite(p) & (p > 0)]
    if len(p) == 0:
        return None
    lots = p * float(lot)
    slots = float(max(int(names), 1))
    return {
        "names": int(names),
        "capital_min_lot": float(np.sum(lots)),
        "capital_equal_all": float(len(p) * np.max(lots)),
        "capital_equal_typical": float(len(p) * np.median(lots)),
        "max_one_lot": float(np.max(lots)),
        "median_one_lot": float(np.median(lots)),
        "over_budget_share": {str(int(c)): float(np.mean(lots > c / slots))
                              for c in levels},
    }


def med(values):
    v = [float(x) for x in values if x is not None and np.isfinite(float(x))]
    if not v:
        return None
    return float(np.median(v))


def pick_size(pool_key, n):
    """Indices of the n largest names -- the same rule as the parent face."""
    if n >= len(pool_key):
        return np.arange(len(pool_key))
    return np.argsort(-pool_key, kind="mergesort")[:n]


def ladder_pick(over_share_by_width, levels=CAPITAL_LEVELS, holdable=HOLDABLE_SHARE):
    """Widest width that is holdable at each capital level.

    `over_share_by_width` maps width-label -> {capital -> median share}.  Widths
    are read in the order they were priced (ascending); the answer is the last
    one still under the bar, so a capital level that cannot even hold the
    narrowest step returns None instead of silently falling back to it.
    """
    out = {}
    labels = [k for k in over_share_by_width]
    for c in levels:
        best = None
        for label in labels:
            share = (over_share_by_width.get(label) or {}).get(str(int(c)))
            if share is None:
                continue
            if share <= holdable:
                best = label
            else:
                break
        out[str(int(c))] = best
    return out


def verdict_capital(cap_equal_all):
    if cap_equal_all is None:
        return "NO_BOOK"
    if cap_equal_all <= 3000000:
        return "BOOK_OPENS_NEAR_THE_PAGE"
    if cap_equal_all <= 10000000:
        return "BOOK_OPENS_WITH_MORE_CAPITAL"
    return "BOOK_NOT_OPENABLE"


def verdict_width(paired, widths=LADDER):
    """Smallest width whose B-A clears T_MIN, else only-at-full, else never."""
    for n in widths:
        p = (paired.get(str(n)) or {}).get("B%d_vs_A%d" % (n, n)) or {}
        if p.get("mean") is not None and p.get("t") is not None:
            if p["mean"] > 0 and p["t"] >= T_MIN:
                return "VETO_PAYS_FROM_WIDTH_%d" % n
    full = (paired.get("FULL") or {}).get("BFULL_vs_AFULL") or {}
    if full.get("mean") is not None and full.get("t") is not None:
        if full["mean"] > 0 and full["t"] >= T_MIN:
            return "VETO_PAYS_ONLY_AT_FULL_BOOK"
    return "VETO_NEVER_SEPARABLE"


# ------------------------------------------------------------------- the run
def run(dates, symbols, close, amount, shares, stride=HOLD, widths=LADDER,
        levels=CAPITAL_LEVELS):
    rets = daily_returns(close)
    mkt = market_return(rets)

    start = 0
    while start < len(dates) and dates[start] < FIRST_DATE:
        start += 1
    start = max(start, LOOKBACK_BETA)

    prev = {}
    rows = []
    t = start
    while t + HOLD < len(dates):
        idx, resid, q, fwd = score_slice(t, close, amount, shares, rets, mkt)
        if resid is None:
            t += stride
            continue
        with np.errstate(invalid="ignore"):
            size = close[t][idx] * shares[t][idx]
        pools = {"A": np.ones(len(idx), dtype=bool), "B": (q < 4)}
        row = {"date": dates[t], "n_pool": int(len(idx)),
               "n_veto_pool": int(np.sum(pools["B"]))}
        for tag, mask in pools.items():
            pool_pos = np.nonzero(mask)[0]
            steps = [(n, "%s%d" % (tag, n)) for n in widths] + [(None, "%sFULL" % tag)]
            for n, key in steps:
                if n is None:
                    pos = pool_pos
                elif len(pool_pos) < n:
                    row[key] = {"gross": None, "net": None, "turnover": None,
                                "size": int(len(pool_pos)), "capital": None}
                    continue
                else:
                    pos = pool_pos[pick_size(size[mask], n)]
                cur = set(idx[pos].tolist())
                gross = float(np.mean(fwd[pos]))
                turb = _turnover(cur, prev.get(key))
                prev[key] = cur
                row[key] = {
                    "gross": gross,
                    "net": gross - 2.0 * COST_ONE_SIDE * turb,
                    "turnover": turb,
                    "size": int(len(pos)),
                    "capital": lot_capital(close[t][idx[pos]], len(pos), levels),
                }
        rows.append(row)
        t += stride
    return rows


def paired_widths(rows, widths=LADDER):
    out = {}
    for n in widths:
        a, b = "A%d" % n, "B%d" % n
        aa, bb = _nets(rows, a), _nets(rows, b)
        mask = np.isfinite(aa) & np.isfinite(bb)
        if int(np.sum(mask)) < 3:
            out[str(n)] = {"%s_vs_%s" % (b, a): {"n": int(np.sum(mask)), "mean": None,
                                                 "se": None, "t": None}}
            continue
        out[str(n)] = {"%s_vs_%s" % (b, a): _paired(
            [{"date": "x", "L": {"net": float(d)}, "M": {"net": 0.0}}
             for d in (bb[mask] - aa[mask]).tolist()], "L", "M")}
    aa, bb = _nets(rows, "AFULL"), _nets(rows, "BFULL")
    mask = np.isfinite(aa) & np.isfinite(bb)
    out["FULL"] = {"BFULL_vs_AFULL": _paired(
        [{"date": "x", "L": {"net": float(d)}, "M": {"net": 0.0}}
         for d in (bb[mask] - aa[mask]).tolist()], "L", "M") if int(np.sum(mask)) >= 3
        else {"n": int(np.sum(mask)), "mean": None, "se": None, "t": None}}
    return out


def capital_table(rows, widths=LADDER, levels=CAPITAL_LEVELS):
    """Median money line per width for both pools, plus the return of the arm."""
    table = {}
    labels = ["%d" % n for n in widths] + ["FULL"]
    for tag in ("A", "B"):
        for label in labels:
            key = "%s%s" % (tag, label)
            caps = [(r.get(key) or {}).get("capital") for r in rows]
            caps = [c for c in caps if c]
            if not caps:
                table[key] = None
                continue
            table[key] = {
                "width": int(caps[0]["names"]),
                "cagr_net": _cagr(rows, key),
                "capital_min_lot": med([c["capital_min_lot"] for c in caps]),
                "capital_equal_all": med([c["capital_equal_all"] for c in caps]),
                "capital_equal_typical": med([c["capital_equal_typical"] for c in caps]),
                "max_one_lot": med([c["max_one_lot"] for c in caps]),
                "median_one_lot": med([c["median_one_lot"] for c in caps]),
                "over_budget_share": {str(int(c)): med([cc["over_budget_share"][str(int(c))]
                                                        for cc in caps])
                                      for c in levels},
                "mean_turnover": float(np.nanmean([
                    (r.get(key) or {}).get("turnover") for r in rows
                    if (r.get(key) or {}).get("turnover") is not None] or [float("nan")])),
            }
    return table


def cmd_check():
    if not os.path.exists(OUT):
        print("STALE face missing: %s" % os.path.relpath(OUT, ROOT))
        return 3
    with open(OUT, encoding="utf-8") as fh:
        face = json.load(fh)
    frontier, sampled = panel_frontier()
    state, msg = staleness(face, frontier)
    if state == "stale":
        print("STALE %s (sample %d files)" % (msg, sampled))
        return 3
    if state == "inconsistent":
        print("CHECK FAILED %s (sample %d files)" % (msg, sampled))
        return 1

    # external question: the headline money line must still equal the series it
    # was summarised from, and the verdict must still be what its own numbers say
    problems = []
    series = face.get("full_book_capital") or {}
    for tag in ("A", "B"):
        s = (series.get(tag) or {}).get("capital_equal_all") or []
        printed = (((face.get("capital") or {}).get("%sFULL" % tag) or {})
                   .get("capital_equal_all"))
        if not s or printed is None:
            problems.append("%sFULL: series or printed value missing" % tag)
            continue
        recomputed = med(s)
        if recomputed is None or abs(recomputed - printed) > 1e-6 * max(1.0, abs(printed)):
            problems.append("%sFULL capital_equal_all printed %.2f != series median %s"
                            % (tag, printed, recomputed))
    want_cap = verdict_capital((face.get("capital") or {}).get("BFULL", {}).get("capital_equal_all"))
    if face.get("verdict_capital") != want_cap:
        problems.append("verdict_capital printed %s but re-derives %s"
                        % (face.get("verdict_capital"), want_cap))
    want_width = verdict_width(face.get("paired") or {})
    if face.get("verdict_width") != want_width:
        problems.append("verdict_width printed %s but re-derives %s"
                        % (face.get("verdict_width"), want_width))
    if face.get("verdict") == "CONTROL_MISMATCH":
        problems.append("FULL arms do not reproduce the parent face (control leg red)")
    if problems:
        for p in problems:
            print("CHECK FAILED %s" % p)
        return 1
    print("OK %s (sample %d files)" % (msg, sampled))
    return 0


# ------------------------------------------------------------------- selftest
def selftest():
    fails = []

    def check(name, cond, detail=""):
        if not cond:
            fails.append("%s %s" % (name, detail))

    # L1 capital arithmetic on a hand book: prices 10/20/30, three names
    c = lot_capital([10.0, 20.0, 30.0], 3, levels=(1000, 10000))
    check("L1a", abs(c["capital_min_lot"] - 6000.0) < 1e-9, c["capital_min_lot"])
    check("L1b", abs(c["capital_equal_all"] - 9000.0) < 1e-9, c["capital_equal_all"])
    check("L1c", abs(c["capital_equal_typical"] - 6000.0) < 1e-9, c["capital_equal_typical"])
    check("L1d", abs(c["over_budget_share"]["1000"] - 1.0) < 1e-12,
          c["over_budget_share"])  # 1000/3 = 333 per slot, no lot fits
    check("L1e", abs(c["over_budget_share"]["10000"] - 0.0) < 1e-12,
          c["over_budget_share"])  # 10000/3 = 3333 per slot, all lots fit

    # L2 non-finite prices are dropped, not counted as free names
    c2 = lot_capital([10.0, float("nan"), 0.0, 20.0], 2, levels=(1000, 10000))
    check("L2", c2["names"] == 2 and abs(c2["capital_min_lot"] - 3000.0) < 1e-9, c2)
    check("L2b", lot_capital([], 0) is None)

    # L3 ladder picker: widest step still under the bar, and a capital level
    # that cannot hold even the first step returns None rather than step 1
    shares = {
        "50": {"1000000": 0.01, "3000000": 0.0},
        "100": {"1000000": 0.03, "3000000": 0.01},
        "200": {"1000000": 0.09, "3000000": 0.02},
    }
    picked = ladder_pick(shares, levels=(1000000, 3000000), holdable=0.02)
    check("L3a", picked["1000000"] == "50", picked)
    check("L3b", picked["3000000"] == "200", picked)  # 200 is exactly at 0.02 -> holdable
    check("L3c",
          ladder_pick({"50": {"1000000": 0.5}}, levels=(1000000,), holdable=0.02)["1000000"] is None)
    # L4 exactly-at-the-bar counts as holdable (<= not <)
    picked4 = ladder_pick({"50": {"1000000": 0.02}}, levels=(1000000,), holdable=0.02)
    check("L4", picked4["1000000"] == "50", picked4)

    # L5 verdict mapping by capital
    check("L5a", verdict_capital(2999999) == "BOOK_OPENS_NEAR_THE_PAGE")
    check("L5b", verdict_capital(3000000) == "BOOK_OPENS_NEAR_THE_PAGE")
    check("L5c", verdict_capital(3000001) == "BOOK_OPENS_WITH_MORE_CAPITAL")
    check("L5d", verdict_capital(10000001) == "BOOK_NOT_OPENABLE")
    check("L5e", verdict_capital(None) == "NO_BOOK")

    # L6 verdict mapping by width, all three branches
    def pw(mean, t):
        return {"mean": mean, "t": t}

    check("L6a", verdict_width({"50": {"B50_vs_A50": pw(0.001, 2.5)}})
          == "VETO_PAYS_FROM_WIDTH_50")
    check("L6b", verdict_width({"50": {"B50_vs_A50": pw(0.001, 1.0)},
                               "FULL": {"BFULL_vs_AFULL": pw(0.002, 3.0)}})
          == "VETO_PAYS_ONLY_AT_FULL_BOOK")
    check("L6c", verdict_width({"50": {"B50_vs_A50": pw(-0.001, 3.0)},
                                "FULL": {"BFULL_vs_AFULL": pw(0.002, 1.0)}})
          == "VETO_NEVER_SEPARABLE")

    # L7 full-width selection is the identity: no name is dropped, none added
    key = np.array([5.0, 1.0, 9.0, 3.0])
    check("L7", len(pick_size(key, 4)) == 4 and set(pick_size(key, 4).tolist()) == {0, 1, 2, 3})
    check("L7b", pick_size(key, 2).tolist() == [2, 0])  # top-two by size, stable

    # L8 turnover bookkeeping is the parent's: same book -> 0, first book -> 1
    check("L8a", _turnover({1, 2}, None) == 1.0)
    check("L8b", _turnover({1, 2}, {1, 2}) == 0.0)
    check("L8c", abs(_turnover({2, 3}, {1, 2}) - 0.5) < 1e-12)

    # L9 the control constants are the parent's published pair, not our own
    check("L9", abs(PARENT_WHOLE_POOL_CAGR - 0.0692) < 1e-12
          and abs(PARENT_VETO_CAGR - 0.1034) < 1e-12)

    # L10 check() shouts STALE on a face that records a bar the panel has passed
    global OUT
    keep = OUT
    tmp = os.path.join(ROOT, "results", "_selftest_open_capital_face.json")
    try:
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump({"evidence_cutoff": "1990-01-02",
                       "panel": {"last": "1990-01-02"}}, fh)
        OUT = tmp
        import io as _io
        import contextlib as _ctx
        buf = _io.StringIO()
        with _ctx.redirect_stdout(buf):
            rc = cmd_check()
        check("L10", rc == 3 and "STALE" in buf.getvalue(), (rc, buf.getvalue()[:80]))
    finally:
        OUT = keep
        try:
            os.remove(tmp)
        except OSError:
            pass

    # L11 check() must not pass a face whose printed money line left its series
    frontier, _sampled = panel_frontier()
    keep = OUT
    tmp2 = os.path.join(ROOT, "results", "_selftest_open_capital_face2.json")
    try:
        face = {"evidence_cutoff": frontier, "panel": {"last": frontier},
                "full_book_capital": {"A": {"capital_equal_all": [100.0, 100.0]},
                                      "B": {"capital_equal_all": [200.0, 200.0]}},
                "capital": {"AFULL": {"capital_equal_all": 100.0},
                            "BFULL": {"capital_equal_all": 250.0}},
                "verdict_capital": verdict_capital(250.0),
                "verdict_width": "VETO_NEVER_SEPARABLE", "paired": {}, "verdict": "x"}
        with open(tmp2, "w", encoding="utf-8") as fh:
            json.dump(face, fh)
        OUT = tmp2
        import io as _io
        import contextlib as _ctx
        buf = _io.StringIO()
        with _ctx.redirect_stdout(buf):
            rc = cmd_check()
        text = buf.getvalue()
        check("L11", rc == 1 and "BFULL capital_equal_all" in text, (rc, text[:120]))
    finally:
        OUT = keep
        try:
            os.remove(tmp2)
        except OSError:
            pass

    if fails:
        for f in fails:
            print("FAIL %s" % f)
        print("selftest FAILED %d/%d" % (len(fails), 11))
        return 1
    print("selftest PASS 11/11")
    return 0


# ---------------------------------------------------------------------- main
def _machine():
    try:
        with open(os.path.join(ROOT, "fleet", "machine.json"), encoding="utf-8") as fh:
            return json.load(fh).get("machine_id", "unknown")
    except (OSError, ValueError):
        return "unknown"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "check", "selftest"])
    ap.add_argument("--stride", type=int, default=HOLD)
    args = ap.parse_args(argv)
    if args.cmd == "selftest":
        return selftest()
    if args.cmd == "check":
        return cmd_check()

    dates, symbols, close, amount, shares = load_panel()
    rows = run(dates, symbols, close, amount, shares, stride=args.stride)
    if not rows:
        print("no rebalance rows")
        return 2

    paired = paired_widths(rows)
    table = capital_table(rows)
    vw = verdict_width(paired)
    a_full = table["AFULL"]["cagr_net"]
    b_full = table["BFULL"]["cagr_net"]
    control = {
        "parent_whole_pool_cagr": PARENT_WHOLE_POOL_CAGR,
        "parent_veto_cagr": PARENT_VETO_CAGR,
        "replay_whole_pool_cagr": a_full,
        "replay_veto_cagr": b_full,
        "tol": CONTROL_TOL,
        "pass": (a_full is not None and b_full is not None
                 and abs(a_full - PARENT_WHOLE_POOL_CAGR) <= CONTROL_TOL
                 and abs(b_full - PARENT_VETO_CAGR) <= CONTROL_TOL),
    }
    vc = verdict_capital(table["BFULL"]["capital_equal_all"])
    v = "CONTROL_MISMATCH" if not control["pass"] else vc

    over = {}
    for label in ["%d" % n for n in LADDER] + ["FULL"]:
        over[label] = (table["B%s" % label] or {}).get("over_budget_share") or {}
    ladder = ladder_pick(over)

    payload = {
        "generated": datetime.now().astimezone().isoformat(timespec="seconds"),
        "evidence_cutoff": dates[-1],
        "machine": _machine(),
        "kind": "astock_veto_open_capital",
        "fills_the_hole_of": "results/astock_veto_holdable_width.json (prices the width, not the money)",
        "prereg": None,
        "adoption": None,
        "spec": {"hold": HOLD, "stride": args.stride, "lookback_beta": LOOKBACK_BETA,
                 "min_amount_20d": MIN_AMOUNT_20D, "min_bars": MIN_BARS,
                 "cost_one_side": COST_ONE_SIDE, "lot": LOT,
                 "ladder": list(LADDER) + ["FULL"],
                 "capital_levels": list(CAPITAL_LEVELS),
                 "holdable_share": HOLDABLE_SHARE, "t_min": T_MIN,
                 "selection": "top-N by market cap (close x outstanding shares), identical rule both pools",
                 "capital_kinds": {
                     "capital_min_lot": "sum of one 100-share lot over the book (unequal share counts)",
                     "capital_equal_all": "N x most expensive one lot (equal weights, every name gets a lot)",
                     "capital_equal_typical": "N x median one lot"},
                 "arms": {"A": "whole eligible pool", "B": "pool minus top 20% residual"}},
        "panel": {"dates": len(dates), "symbols": len(symbols),
                  "first": dates[0], "last": dates[-1]},
        "rebalances": len(rows),
        "capital": table,
        "paired": paired,
        "control": control,
        "ladder_holdable_width": ladder,
        "full_book_capital": {
            "A": {"dates": [r["date"] for r in rows],
                  "capital_equal_all": [(r["AFULL"]["capital"] or {}).get("capital_equal_all")
                                        for r in rows],
                  "capital_min_lot": [(r["AFULL"]["capital"] or {}).get("capital_min_lot")
                                      for r in rows]},
            "B": {"dates": [r["date"] for r in rows],
                  "capital_equal_all": [(r["BFULL"]["capital"] or {}).get("capital_equal_all")
                                        for r in rows],
                  "capital_min_lot": [(r["BFULL"]["capital"] or {}).get("capital_min_lot")
                                      for r in rows]},
        },
        "verdict_capital": vc,
        "verdict_width": vw,
        "verdict": v,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)

    print("rebalances %d  cutoff %s  panel %d symbols"
          % (len(rows), payload["evidence_cutoff"], len(symbols)))
    print("  control A %.2f%% (parent %.2f%%)  B %.2f%% (parent %.2f%%)  -> %s"
          % (100.0 * (a_full or 0), 100.0 * PARENT_WHOLE_POOL_CAGR,
             100.0 * (b_full or 0), 100.0 * PARENT_VETO_CAGR,
             "PASS" if control["pass"] else "MISMATCH"))
    print("  %-5s %8s %8s %10s %14s %14s %14s"
          % ("width", "A cagr", "B cagr", "B-A t", "min_lot", "equal_all", "equal_typ"))
    for label in ["%d" % n for n in LADDER] + ["FULL"]:
        a, b = table["A%s" % label], table["B%s" % label]
        p = (paired.get(label) or {}).get("B%s_vs_A%s" % (label, label)) or {}
        print("  %-5s %7s %7s %10s %14s %14s %14s"
              % (label,
                 ("%.2f%%" % (100.0 * a["cagr_net"])) if a["cagr_net"] is not None else "n/a",
                 ("%.2f%%" % (100.0 * b["cagr_net"])) if b["cagr_net"] is not None else "n/a",
                 ("%+.2f" % p["t"]) if p.get("t") is not None else "n/a",
                 ("%.2fM" % (b["capital_min_lot"] / 1e6)) if b["capital_min_lot"] else "n/a",
                 ("%.2fM" % (b["capital_equal_all"] / 1e6)) if b["capital_equal_all"] else "n/a",
                 ("%.2fM" % (b["capital_equal_typical"] / 1e6)) if b["capital_equal_typical"] else "n/a"))
    for c in CAPITAL_LEVELS:
        print("  at %d: widest holdable width = %s"
              % (c, ladder.get(str(int(c)))))
    print("verdict capital=%s width=%s -> %s" % (vc, vw, os.path.relpath(OUT, ROOT)))
    return 0 if v != "CONTROL_MISMATCH" else 2


if __name__ == "__main__":
    sys.exit(main())
