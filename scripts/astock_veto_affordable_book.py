#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A-share residual veto -- the book a 1,000,000 account can actually buy.

Why this face exists
--------------------
r1955 priced the veto at 30/50/100 names and returned VETO_NOT_SEPARABLE_AT_WIDTH.
r1956 priced the capital line and returned BOOK_NOT_OPENABLE: the arm that pays
(+3.4pp/yr over the whole pool) is a 2,052-name equal-weight book that needs
89.2M to hold, and the book a 1,000,000 account can buy -- the 50 biggest names
-- pays -11.10%/yr.  Both faces therefore left the same sentence unfinished:
"then what can this account own?"

There is a third way between "fewer, bigger names" and "89M": at a fixed money
line, DROP the names whose one 100-share lot does not fit the slot budget and
keep the width.  At 1,000,000 over 400 names that budget is 2,500 yuan a name --
almost every A-share clears it, while the 50-name book was never the veto's
question.  This face measures whether that book pays, and whether the money is
the veto's or the filter's.

What it prints -- per capital level and width
---------------------------------------------
    A  top-N by market cap, whole eligible pool      (the parent's book, no filter)
    P  top-N by market cap, whole pool AND affordable (filter alone, no veto)
    V  top-N by market cap, veto pool AND affordable  (the book under test)
    R  mean of 20 seeded random draws from the veto pool AND affordable
                                                      (does the ranking matter?)
    S  top-N by ASCENDING residual, veto pool AND affordable
                                                      (spend the ranking on the
                                                       signal instead of on size)

plus, for each: net CAGR (2 x 8bp x turnover), median one-lot, median market
cap of the picks, share of the picks whose one lot exceeded the budget, and the
share of the eligible pool that is affordable at all.

S is honest about its own arrival: the first pass measured A/P/V/R only, and it
came back with every cap-ranked arm losing money while the random draw from the
same pool made +7.8%..+11.8%.  That is a statement about the sort rule, not
about the veto, so S was added to spend the ordering on the signal.  Its
criterion was frozen at the moment of addition and the primary verdict (V, below)
was not moved.

Criteria frozen before the first run (nothing below is tuned on the numbers)
---------------------------------------------------------------------------
  CAPITALS     1M / 3M / 5M -- the money line this company could actually put
               behind one book; r1956 showed 10M still does not open the FULL book.
  WIDTHS       50 / 100 / 200 / 400 -- 400 is TEST_WIDTH: the width where the
               parent's paired difference first cleared two standard errors.
  TEST_WIDTH   400 at 1,000,000.  The verdict is read there and nowhere else,
               so the answer cannot be the best-looking cell.
  T_MIN        2.0, the bar both parent faces used.
  CONTROL      A50@1M and A400@1M must reproduce the parent face's published
               arms (-11.10% and -10.47%, read out of its own JSON) within
               0.60pp; otherwise CONTROL_MISMATCH.
  RANDOM_DRAWS 20 per date, one generator, one seed -- the same construction as
               the parent's random arm.

verdicts
  AFFORDABLE_VETO_PAYS                  > 0, beats A and beats R by 2 se
  AFFORDABLE_BOOK_BEATS_THE_UNBUYABLE_ONLY   beats A, but random from the same
                                        affordable pool does just as well -- the
                                        money would be the filter, not the sort
  AFFORDABLE_BOOK_POSITIVE_NOT_SIGNIFICANT
  AFFORDABLE_BOOK_STILL_LOSES
  CONTROL_MISMATCH
filter side (printed beside the verdict, never folded into it):
  THE_FILTER_IS_ITS_OWN_BET            P-A clears T_MIN: affordability itself
                                       moves returns, so V's edge needs re-reading
  THE_FILTER_BUYS_SMALLER_NAMES_BUT_PAYS_NOTHING
                                       V picks are under half A's median cap and
                                       P-A is not significant
  THE_FILTER_IS_A_COST_NOT_A_BET       otherwise
signal-sort side (frozen when S was added):
  SIGNAL_SORT_BEATS_RANDOM             > 0 and beats R by 2 se
  SIGNAL_SORT_PAYS_BUT_RANDOM_MATCHES_IT
  SIGNAL_SORT_ALSO_LOSES
  NO_SIGNAL_ARM

usage: python scripts/astock_veto_affordable_book.py [run|check|selftest]
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
    compound,
    daily_returns,
    load_panel,
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
    _cagr,
    _nets,
    pick_liquid,
)
from astock_veto_open_capital import (  # noqa: E402
    LOT,
    med,
)

OUT = os.path.join(ROOT, "results", "astock_veto_affordable_book.json")
PARENT = os.path.join(ROOT, "results", "astock_veto_open_capital.json")

CAPITALS = (1000000, 3000000, 5000000)
WIDTHS = (50, 100, 200, 400)
PRIMARY_CAPITAL = 1000000
TEST_WIDTH = 400
T_MIN = 2.0
RANDOM_DRAWS = 20
SEED = 20261123
CONTROL_TOL = 0.0060

# the parent face's published arms, re-read (not re-typed) where the file exists
PARENT_A50_CAGR = -0.111013
PARENT_A400_CAGR = -0.104660


# ------------------------------------------------------------------ pure rules
def feasible_mask(price, budget, lot=LOT):
    """A name is buyable when one 100-share lot fits the slot budget.

    Exactly at the budget counts as buyable: the slot pays for the lot and keeps
    nothing, which is still a fill (r1813: weight is not an order).
    """
    p = np.asarray(price, dtype=float)
    with np.errstate(invalid="ignore"):
        return np.isfinite(p) & (p > 0) & (p * float(lot) <= float(budget))


def thin_pool(n_avail, n):
    """Too few affordable names to call this a book of width n.

    Half the width is the floor: a 400-name book drawn from 210 names is a
    210-name book wearing a 400-name label, and its turnover cost is priced on
    the label.  Below three names there is no cross-section at all.
    """
    return int(n_avail) < max(3, int(n) // 2)


def verdict_book(cagr, t_vs_a, t_vs_r, t_min=T_MIN):
    if cagr is None:
        return "NO_BOOK"
    if cagr <= 0:
        return "AFFORDABLE_BOOK_STILL_LOSES"
    if t_vs_a is None or t_vs_a < t_min:
        return "AFFORDABLE_BOOK_POSITIVE_NOT_SIGNIFICANT"
    if t_vs_r is None or t_vs_r < t_min:
        return "AFFORDABLE_BOOK_BEATS_THE_UNBUYABLE_ONLY"
    return "AFFORDABLE_VETO_PAYS"


def filter_diagnostic(t_p_vs_a, size_ratio, t_min=T_MIN):
    if t_p_vs_a is not None and t_p_vs_a >= t_min:
        return "THE_FILTER_IS_ITS_OWN_BET"
    if size_ratio is not None and size_ratio < 0.5:
        return "THE_FILTER_BUYS_SMALLER_NAMES_BUT_PAYS_NOTHING"
    return "THE_FILTER_IS_A_COST_NOT_A_BET"


def signal_sort_diagnostic(cagr_s, t_s_vs_r, t_min=T_MIN):
    """The signal-sorted book, judged against the random draw -- the same two
    gates r1865 used, because "beats nothing" and "beats random" are different
    sentences."""
    if cagr_s is None:
        return "NO_SIGNAL_ARM"
    if cagr_s <= 0:
        return "SIGNAL_SORT_ALSO_LOSES"
    if t_s_vs_r is not None and t_s_vs_r <= -t_min:
        return "SIGNAL_SORT_WORSE_THAN_RANDOM"
    if t_s_vs_r is None or t_s_vs_r < t_min:
        return "SIGNAL_SORT_PAYS_BUT_RANDOM_MATCHES_IT"
    return "SIGNAL_SORT_BEATS_RANDOM"


def key_of(tag, n, capital):
    return "%s%d@%d" % (tag, n, int(capital))


# ------------------------------------------------------------------- the run
def run(dates, symbols, close, amount, shares, capitals=CAPITALS, widths=WIDTHS,
        stride=HOLD, draws=RANDOM_DRAWS):
    """One pass, every capital level: score_slice is capital-independent, and
    paying for it three times is how a face stops being run (r1850 family)."""
    rets = daily_returns(close)
    mkt = market_return(rets)

    start = 0
    while start < len(dates) and dates[start] < FIRST_DATE:
        start += 1
    start = max(start, LOOKBACK_BETA)

    rng = np.random.default_rng(SEED)
    prev = {}
    rows = []
    t = start
    while t + HOLD < len(dates):
        idx, resid, q, fwd = score_slice(t, close, amount, shares, rets, mkt)
        if resid is None:
            t += stride
            continue
        price = np.asarray(close[t][idx], dtype=float)
        with np.errstate(invalid="ignore"):
            mcap = price * shares[t][idx]
        veto = q < 4
        row = {"date": dates[t], "n_eligible": int(len(idx)), "n_veto": int(np.sum(veto)),
               "median_one_lot_pool": float(np.nanmedian(price * LOT)),
               "median_mcap_pool": float(np.nanmedian(mcap)),
               "median_mcap_veto": float(np.nanmedian(mcap[veto])) if np.any(veto) else None}
        for capital in capitals:
            for n in widths:
                budget = float(capital) / float(n)
                feas = feasible_mask(price, budget)
                row["pool@%d@%d" % (int(capital), n)] = {
                    "budget": budget,
                    "feasible_share": float(np.mean(feas)),
                    "feasible_veto_share": float(np.mean(feas & veto)),
                }
                pools = {"A": np.ones(len(idx), dtype=bool), "P": feas, "V": feas & veto}
                for tag, mask in pools.items():
                    k = key_of(tag, n, capital)
                    pos_pool = np.nonzero(mask)[0]
                    if thin_pool(len(pos_pool), n):
                        row[k] = {"thin": True, "size": int(len(pos_pool))}
                        continue
                    take = min(n, len(pos_pool))
                    pick = pos_pool[pick_liquid(mcap[mask], pos_pool, take)]
                    cur = set(idx[pick].tolist())
                    gross = float(np.mean(fwd[pick]))
                    turb = _turnover(cur, prev.get(k))
                    prev[k] = cur
                    one_lot = price[pick] * LOT
                    row[k] = {
                        "gross": gross,
                        "net": gross - 2.0 * COST_ONE_SIDE * turb,
                        "turnover": turb,
                        "size": int(take),
                        "thin": False,
                        "median_one_lot": float(np.median(one_lot)),
                        "median_mcap": float(np.median(mcap[pick])),
                        "over_budget": float(np.mean(one_lot > budget + 1e-9)),
                    }
                # the ranking control: same affordable veto pool, random picks
                k = key_of("R", n, capital)
                pos_pool = np.nonzero(feas & veto)[0]
                if thin_pool(len(pos_pool), n):
                    row[k] = {"thin": True, "size": int(len(pos_pool))}
                    continue
                take = min(n, len(pos_pool))
                grosses, nets, turbs = [], [], []
                for d in range(draws):
                    pick = np.sort(rng.choice(pos_pool, size=take, replace=False))
                    dk = "%s#%d" % (k, d)
                    cur = set(idx[pick].tolist())
                    turb = _turnover(cur, prev.get(dk))
                    prev[dk] = cur
                    g = float(np.mean(fwd[pick]))
                    grosses.append(g)
                    turbs.append(turb)
                    nets.append(g - 2.0 * COST_ONE_SIDE * turb)
                row[k] = {"gross": float(np.mean(grosses)), "net": float(np.mean(nets)),
                          "turnover": float(np.mean(turbs)), "size": int(take),
                          "thin": False, "median_one_lot": None, "median_mcap": None,
                          "over_budget": None}
                # kept so the reader can see how far ONE draw lands from the mean
                row["%s_draws" % k] = list(nets)
                # the signal sort: same affordable veto pool, cheapest residual first
                # (residual reversal means the most oversold names are the picks)
                k = key_of("S", n, capital)
                if thin_pool(len(pos_pool), n):
                    row[k] = {"thin": True, "size": int(len(pos_pool))}
                    continue
                take = min(n, len(pos_pool))
                pick = pos_pool[np.argsort(resid[pos_pool], kind="mergesort")[:take]]
                cur = set(idx[pick].tolist())
                gross = float(np.mean(fwd[pick]))
                turb = _turnover(cur, prev.get(k))
                prev[k] = cur
                one_lot = price[pick] * LOT
                row[k] = {
                    "gross": gross,
                    "net": gross - 2.0 * COST_ONE_SIDE * turb,
                    "turnover": turb,
                    "size": int(take),
                    "thin": False,
                    "median_one_lot": float(np.median(one_lot)),
                    "median_mcap": float(np.median(mcap[pick])),
                    "over_budget": float(np.mean(one_lot > budget + 1e-9)),
                }
        rows.append(row)
        t += stride
    return rows


# ------------------------------------------------------------------ summaries
def _num(v):
    """A missing value is NaN; a zero is a zero (0.0 turnover is not missing)."""
    return float(v) if v is not None else float("nan")


def summarize(rows, capital, n, tag):
    k = key_of(tag, n, capital)
    diag = [r.get("pool@%d@%d" % (int(capital), n)) or {} for r in rows]
    return {
        "arm": tag,
        "width_target": int(n),
        "capital_cny": int(capital),
        "slot_budget_cny": float(capital) / float(n),
        "cagr_net": _cagr(rows, k),
        "mean_turnover": float(np.nanmean([_num((r.get(k) or {}).get("turnover"))
                                           for r in rows])),
        "median_size": med([(r.get(k) or {}).get("size") for r in rows]),
        "median_one_lot": med([(r.get(k) or {}).get("median_one_lot") for r in rows]),
        "median_mcap": med([(r.get(k) or {}).get("median_mcap") for r in rows]),
        "mean_over_budget": float(np.nanmean([_num((r.get(k) or {}).get("over_budget"))
                                              for r in rows])),
        "thin_rounds": int(sum(1 for r in rows if (r.get(k) or {}).get("thin"))),
        "feasible_share": float(np.nanmean([_num(d.get("feasible_share")) for d in diag])),
        "feasible_veto_share": float(np.nanmean([_num(d.get("feasible_veto_share"))
                                                 for d in diag])),
    }


def paired_t(rows, capital, n, arm, base):
    return _paired(rows, key_of(arm, n, capital), key_of(base, n, capital))


def pool_diagnostics(rows):
    """The size question, asked on the pools rather than on the picks.

    A random draw from a pool has that pool's size distribution, so the honest
    answer to "is the random book a small-cap bet?" is the pool's own median
    market cap next to the cap-sorted book's.  Printed, never scored.
    """
    return {
        "median_mcap_whole_pool": med([r.get("median_mcap_pool") for r in rows]),
        "median_mcap_veto_pool": med([r.get("median_mcap_veto") for r in rows]),
        "median_one_lot_whole_pool": med([r.get("median_one_lot_pool") for r in rows]),
        "median_n_eligible": med([r.get("n_eligible") for r in rows]),
        "median_n_veto": med([r.get("n_veto") for r in rows]),
    }


def draw_cagrs(rows, capital, n, draws=RANDOM_DRAWS):
    """CAGR of each single random draw, not the mean of draws.

    The mean of 20 draws is the pool's expected return; the book a reader would
    own is ONE draw.  Printing only the mean sells a precision no account has.
    """
    k = "%s_draws" % key_of("R", n, capital)
    series = [[] for _ in range(draws)]
    for r in rows:
        d = r.get(k)
        if not d:
            continue
        for i in range(min(draws, len(d))):
            series[i].append(float(d[i]))
    out = [compound(s) for s in series if len(s) >= 3]
    out = [v for v in out if v is not None]
    if not out:
        return {"draws": 0}
    return {"draws": len(out), "min": float(np.min(out)),
            "median": float(np.median(out)), "max": float(np.max(out))}


def table_all(rows, capitals=CAPITALS, widths=WIDTHS):
    out = {}
    for capital in capitals:
        out[str(int(capital))] = {}
        for n in widths:
            out[str(int(capital))][str(n)] = {
                tag: summarize(rows, capital, n, tag) for tag in ("A", "P", "V", "R", "S")}
    return out


def paired_all(rows, capitals=CAPITALS, widths=WIDTHS):
    out = {}
    for capital in capitals:
        out[str(int(capital))] = {}
        for n in widths:
            out[str(int(capital))][str(n)] = {
                "V_vs_A": paired_t(rows, capital, n, "V", "A"),
                "V_vs_P": paired_t(rows, capital, n, "V", "P"),
                "V_vs_R": paired_t(rows, capital, n, "V", "R"),
                "P_vs_A": paired_t(rows, capital, n, "P", "A"),
                "S_vs_R": paired_t(rows, capital, n, "S", "R"),
                "S_vs_A": paired_t(rows, capital, n, "S", "A"),
            }
    return out


def primary_block(table, paired):
    cell = table[str(int(PRIMARY_CAPITAL))][str(TEST_WIDTH)]
    pair = paired[str(int(PRIMARY_CAPITAL))][str(TEST_WIDTH)]
    v, a, s = cell["V"], cell["A"], cell["S"]
    size_ratio = None
    if v.get("median_mcap") and a.get("median_mcap"):
        size_ratio = float(v["median_mcap"]) / float(a["median_mcap"])
    t_a = (pair["V_vs_A"] or {}).get("t")
    t_r = (pair["V_vs_R"] or {}).get("t")
    t_p = (pair["P_vs_A"] or {}).get("t")
    t_s_r = (pair["S_vs_R"] or {}).get("t")
    return {
        "capital_cny": int(PRIMARY_CAPITAL),
        "width": int(TEST_WIDTH),
        "arm_used": "V",
        "cagr_net": v.get("cagr_net"),
        "t_vs_A": t_a,
        "t_vs_R": t_r,
        "t_vs_P": (pair["V_vs_P"] or {}).get("t"),
        "t_filter_vs_A": t_p,
        "size_ratio_V_over_A": size_ratio,
        "feasible_share": v.get("feasible_share"),
        "median_size": v.get("median_size"),
        "verdict": verdict_book(v.get("cagr_net"), t_a, t_r),
        "filter_diagnostic": filter_diagnostic(t_p, size_ratio),
        "signal": {
            "arm": "S",
            "cagr_net": s.get("cagr_net"),
            "t_vs_R": t_s_r,
            "t_vs_A": (pair["S_vs_A"] or {}).get("t"),
            "mean_turnover": s.get("mean_turnover"),
            "median_mcap": s.get("median_mcap"),
            "diagnostic": signal_sort_diagnostic(s.get("cagr_net"), t_s_r),
        },
    }


# --------------------------------------------------------------------- check
def _control(face_table):
    a50 = (((face_table or {}).get(str(int(PRIMARY_CAPITAL)), {})
            .get("50", {}).get("A")) or {}).get("cagr_net")
    a400 = (((face_table or {}).get(str(int(PRIMARY_CAPITAL)), {})
             .get("400", {}).get("A")) or {}).get("cagr_net")
    ok = (a50 is not None and a400 is not None
          and abs(a50 - PARENT_A50_CAGR) <= CONTROL_TOL
          and abs(a400 - PARENT_A400_CAGR) <= CONTROL_TOL)
    return {"parent_a50": PARENT_A50_CAGR, "parent_a400": PARENT_A400_CAGR,
            "replay_a50": a50, "replay_a400": a400, "tol": CONTROL_TOL, "pass": bool(ok)}


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

    problems = []

    # 1. every printed arm CAGR must still be the compound of its own series;
    #    the series is stored for the primary width only, so that is what is asked
    series = face.get("series") or {}
    cell = (((face.get("table") or {}).get(str(int(PRIMARY_CAPITAL)), {})
             .get(str(TEST_WIDTH))) or {})
    for tag in ("A", "P", "V", "R", "S"):
        nets = series.get(tag)
        printed = (cell.get(tag) or {}).get("cagr_net")
        if not nets:
            problems.append("%s%d series missing" % (tag, TEST_WIDTH))
            continue
        if printed is None:
            problems.append("%s%d printed CAGR missing" % (tag, TEST_WIDTH))
            continue
        recomputed = compound([float(v) for v in nets if v is not None])
        if recomputed is None or abs(recomputed - printed) > 1e-9 * max(1.0, abs(printed)):
            problems.append("%s%d printed CAGR %.6f != series compound %s"
                            % (tag, TEST_WIDTH, printed, recomputed))

    # 2. the verdict must be what its own printed numbers say
    prim = face.get("primary") or {}
    want_v = verdict_book(prim.get("cagr_net"), prim.get("t_vs_A"), prim.get("t_vs_R"))
    if prim.get("verdict") != want_v:
        problems.append("primary verdict printed %s but re-derives %s"
                        % (prim.get("verdict"), want_v))
    want_f = filter_diagnostic(prim.get("t_filter_vs_A"), prim.get("size_ratio_V_over_A"))
    if prim.get("filter_diagnostic") != want_f:
        problems.append("filter diagnostic printed %s but re-derives %s"
                        % (prim.get("filter_diagnostic"), want_f))
    sig = prim.get("signal") or {}
    want_s = signal_sort_diagnostic(sig.get("cagr_net"), sig.get("t_vs_R"))
    if sig.get("diagnostic") != want_s:
        problems.append("signal diagnostic printed %s but re-derives %s"
                        % (sig.get("diagnostic"), want_s))

    # 3. the control leg must still be green against the parent's published arms
    ctl = face.get("control") or {}
    recomputed_ctl = _control(face.get("table"))
    if not recomputed_ctl["pass"]:
        problems.append("control leg red: replay A50=%s A400=%s vs parent %s/%s (tol %.4f)"
                        % (recomputed_ctl["replay_a50"], recomputed_ctl["replay_a400"],
                           recomputed_ctl["parent_a50"], recomputed_ctl["parent_a400"],
                           recomputed_ctl["tol"]))
    if bool(ctl.get("pass")) != bool(recomputed_ctl["pass"]):
        problems.append("control.pass printed %s but re-derives %s"
                        % (ctl.get("pass"), recomputed_ctl["pass"]))

    if problems:
        for p in problems:
            print("CHECK FAILED %s" % p)
        return 1
    print("OK %s (sample %d files)" % (msg, sampled))
    return 0


# ------------------------------------------------------------------ selftest
def selftest():
    fails = []
    total = [0]

    def check(name, cond, detail=""):
        total[0] += 1
        if not cond:
            fails.append("%s %s" % (name, detail))

    # L1 the affordability rule, including the exact-boundary fill
    m = feasible_mask([10.0, 200.0, 200.01, float("nan"), 0.0], 20000.0)
    check("L1", m.tolist() == [True, True, False, False, False], m.tolist())
    check("L1b", bool(feasible_mask([200.0], 20000.0)[0]),
          "one lot exactly at the budget is a fill")

    # L2 budget arithmetic is capital / width, per name
    check("L2", abs(1000000.0 / 400.0 - 2500.0) < 1e-12)

    # L3 thin-pool floor: half the width, never below three
    check("L3a", thin_pool(20, 50) is True)
    check("L3b", thin_pool(25, 50) is False)
    check("L3c", thin_pool(2, 5) is True)
    check("L3d", thin_pool(3, 5) is False)

    # L4 the four verdict branches are all reachable, and NO_BOOK for no arm
    check("L4a", verdict_book(-0.01, 3.0, 3.0) == "AFFORDABLE_BOOK_STILL_LOSES")
    check("L4b", verdict_book(0.02, 1.0, 1.0) == "AFFORDABLE_BOOK_POSITIVE_NOT_SIGNIFICANT")
    check("L4c", verdict_book(0.02, 2.5, 0.5) == "AFFORDABLE_BOOK_BEATS_THE_UNBUYABLE_ONLY")
    check("L4d", verdict_book(0.02, 2.5, 2.5) == "AFFORDABLE_VETO_PAYS")
    check("L4e", verdict_book(None, 3.0, 3.0) == "NO_BOOK")
    check("L4f", verdict_book(0.02, None, 3.0) == "AFFORDABLE_BOOK_POSITIVE_NOT_SIGNIFICANT")

    # L5 the filter diagnostic is a separate judgement from the verdict
    check("L5a", filter_diagnostic(2.4, 0.9) == "THE_FILTER_IS_ITS_OWN_BET")
    check("L5b", filter_diagnostic(0.4, 0.2) == "THE_FILTER_BUYS_SMALLER_NAMES_BUT_PAYS_NOTHING")
    check("L5c", filter_diagnostic(0.4, 0.8) == "THE_FILTER_IS_A_COST_NOT_A_BET")
    check("L5d", filter_diagnostic(None, None) == "THE_FILTER_IS_A_COST_NOT_A_BET")

    # L5e the signal-sort diagnostic is its own judgement, also all four states
    check("L5e1", signal_sort_diagnostic(None, None) == "NO_SIGNAL_ARM")
    check("L5e2", signal_sort_diagnostic(-0.02, 3.0) == "SIGNAL_SORT_ALSO_LOSES")
    check("L5e3", signal_sort_diagnostic(0.05, 0.9) == "SIGNAL_SORT_PAYS_BUT_RANDOM_MATCHES_IT")
    check("L5e4", signal_sort_diagnostic(0.05, 2.1) == "SIGNAL_SORT_BEATS_RANDOM")
    check("L5e5", signal_sort_diagnostic(0.05, -2.4) == "SIGNAL_SORT_WORSE_THAN_RANDOM")
    check("L5e6", signal_sort_diagnostic(0.05, -1.6) == "SIGNAL_SORT_PAYS_BUT_RANDOM_MATCHES_IT")

    # L6 zero-drift: a book with no change and a first book
    check("L6a", _turnover({1, 2}, None) == 1.0)
    check("L6b", _turnover({1, 2}, {1, 2}) == 0.0)

    # L7 the selection rule is the parent's, with the filter as the only change
    cap = np.array([5.0, 1.0, 9.0, 3.0])
    check("L7a", pick_liquid(cap, np.arange(4), 2).tolist() == [2, 0])
    check("L7b", len(pick_liquid(cap, np.arange(4), 9)) == 4)

    # L8 the random arm is seeded: same seed -> same picks
    a = np.random.default_rng(SEED).choice(np.arange(50), size=10, replace=False)
    b = np.random.default_rng(SEED).choice(np.arange(50), size=10, replace=False)
    check("L8", a.tolist() == b.tolist())

    # L9 the control constants are the parent's published arms, and the parent
    #    file (when present) still says the same thing
    check("L9a", abs(PARENT_A50_CAGR - (-0.111013)) < 1e-12
          and abs(PARENT_A400_CAGR - (-0.104660)) < 1e-12)
    note9 = "parent face absent"
    if os.path.exists(PARENT):
        try:
            with open(PARENT, encoding="utf-8") as fh:
                pf = json.load(fh)
            pa50 = ((pf.get("capital") or {}).get("A50") or {}).get("cagr_net")
            pa400 = ((pf.get("capital") or {}).get("A400") or {}).get("cagr_net")
            check("L9b", pa50 is not None and abs(pa50 - PARENT_A50_CAGR) <= CONTROL_TOL,
                  (pa50, PARENT_A50_CAGR))
            check("L9c", pa400 is not None and abs(pa400 - PARENT_A400_CAGR) <= CONTROL_TOL,
                  (pa400, PARENT_A400_CAGR))
            note9 = "parent face agrees"
        except (OSError, ValueError) as exc:  # pragma: no cover - corrupt file
            check("L9b", False, str(exc))

    # L10 check() shouts STALE on a face that records a bar the panel has passed
    global OUT
    keep = OUT
    tmp = os.path.join(ROOT, "results", "_selftest_affordable_face.json")
    try:
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump({"evidence_cutoff": "1990-01-02",
                       "panel": {"last": "1990-01-02"}}, fh)
        OUT = tmp
        import contextlib as _ctx
        import io as _io
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

    # L11 check() must not pass a face whose printed CAGR left its own series
    frontier, _sampled = panel_frontier()
    keep = OUT
    tmp2 = os.path.join(ROOT, "results", "_selftest_affordable_face2.json")
    try:
        good_nets = [0.001, 0.002, -0.001, 0.0]
        cell = {tag: {"cagr_net": compound(good_nets)} for tag in ("A", "P", "V", "R", "S")}
        cell["V"]["cagr_net"] = float(cell["V"]["cagr_net"]) + 0.01  # the lie
        face = {
            "evidence_cutoff": frontier, "panel": {"last": frontier},
            "table": {str(int(PRIMARY_CAPITAL)): {str(TEST_WIDTH): cell}},
            "series": {tag: good_nets for tag in ("A", "P", "V", "R", "S")},
            "primary": {"cagr_net": 0.02, "t_vs_A": 2.5, "t_vs_R": 2.5,
                        "t_filter_vs_A": 0.1, "size_ratio_V_over_A": 0.9,
                        "verdict": "AFFORDABLE_VETO_PAYS",
                        "filter_diagnostic": "THE_FILTER_IS_A_COST_NOT_A_BET"},
            "control": {"pass": True},
        }
        with open(tmp2, "w", encoding="utf-8") as fh:
            json.dump(face, fh)
        OUT = tmp2
        import contextlib as _ctx
        import io as _io
        buf = _io.StringIO()
        with _ctx.redirect_stdout(buf):
            rc = cmd_check()
        text = buf.getvalue()
        check("L11", rc == 1 and "V400 printed CAGR" in text, (rc, text[:140]))

        # L12 the same face with the honest CAGR must pass on these two legs
        cell["V"]["cagr_net"] = compound(good_nets)
        face["control"] = _control(face["table"])
        with open(tmp2, "w", encoding="utf-8") as fh:
            json.dump(face, fh)
        buf = _io.StringIO()
        with _ctx.redirect_stdout(buf):
            rc2 = cmd_check()
        text2 = buf.getvalue()
        check("L12", "V400 printed CAGR" not in text2,
              "an honest series must not be named as the defect: %s" % text2[:160])

        # L13 a printed verdict that its own numbers no longer support
        face["primary"]["verdict"] = "AFFORDABLE_BOOK_POSITIVE_NOT_SIGNIFICANT"
        with open(tmp2, "w", encoding="utf-8") as fh:
            json.dump(face, fh)
        buf = _io.StringIO()
        with _ctx.redirect_stdout(buf):
            rc3 = cmd_check()
        text3 = buf.getvalue()
        check("L13", rc3 == 1 and "verdict printed" in text3, (rc3, text3[:140]))

        # L14 ... and a signal diagnostic that its own numbers no longer support
        face["primary"]["verdict"] = "AFFORDABLE_VETO_PAYS"
        face["primary"]["signal"] = {"cagr_net": 0.05, "t_vs_R": 2.5,
                                     "diagnostic": "SIGNAL_SORT_ALSO_LOSES"}
        with open(tmp2, "w", encoding="utf-8") as fh:
            json.dump(face, fh)
        buf = _io.StringIO()
        with _ctx.redirect_stdout(buf):
            rc4 = cmd_check()
        text4 = buf.getvalue()
        check("L14", rc4 == 1 and "signal diagnostic" in text4, (rc4, text4[:140]))
    finally:
        OUT = keep
        try:
            os.remove(tmp2)
        except OSError:
            pass

    # L15 the per-draw dispersion is a distribution, not a second mean:
    #     min <= median <= max, and a flat draw set collapses to one value
    kk = "%s_draws" % key_of("R", 400, PRIMARY_CAPITAL)
    fake = [{kk: [0.01] * RANDOM_DRAWS} for _ in range(5)]
    d = draw_cagrs(fake, PRIMARY_CAPITAL, 400)
    check("L15a", d.get("draws") == RANDOM_DRAWS, d)
    check("L15b", abs(d["max"] - d["min"]) < 1e-12, d)
    fake2 = [{kk: [(0.01 + 0.001 * i) for i in range(RANDOM_DRAWS)]} for _ in range(5)]
    d2 = draw_cagrs(fake2, PRIMARY_CAPITAL, 400)
    check("L15c", d2["min"] <= d2["median"] <= d2["max"] and d2["max"] > d2["min"], d2)

    if fails:
        for f in fails:
            print("FAIL %s" % f)
        print("selftest FAILED %d/%d" % (len(fails), total[0]))
        return 1
    print("selftest PASS %d/%d (%s)" % (total[0], total[0], note9))
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

    table = table_all(rows)
    paired = paired_all(rows)
    prim = primary_block(table, paired)
    control = _control(table)
    verdict = "CONTROL_MISMATCH" if not control["pass"] else prim["verdict"]

    series = {tag: [float(v) if np.isfinite(v) else None
                    for v in _nets(rows, key_of(tag, TEST_WIDTH, PRIMARY_CAPITAL)).tolist()]
              for tag in ("A", "P", "V", "R", "S")}

    payload = {
        "generated": datetime.now().astimezone().isoformat(timespec="seconds"),
        "evidence_cutoff": dates[-1],
        "machine": _machine(),
        "kind": "astock_veto_affordable_book",
        "fills_the_hole_of": "results/astock_veto_open_capital.json (prices the money, "
                             "not the book that money can buy)",
        "prereg": None,
        "adoption": None,
        "spec": {
            "hold": HOLD, "stride": args.stride, "lookback_beta": LOOKBACK_BETA,
            "min_amount_20d": MIN_AMOUNT_20D, "min_bars": MIN_BARS,
            "cost_one_side": COST_ONE_SIDE, "lot": LOT,
            "capitals": list(CAPITALS), "widths": list(WIDTHS),
            "primary_capital": int(PRIMARY_CAPITAL), "test_width": int(TEST_WIDTH),
            "t_min": T_MIN, "random_draws": RANDOM_DRAWS, "seed": SEED,
            "selection": "top-N by market cap (close x outstanding shares), identical "
                         "rule in every arm; the filter is the only difference",
            "arms": {
                "A": "whole eligible pool, no affordability filter (the parent's book)",
                "P": "whole pool restricted to names whose one lot fits capital/N",
                "V": "veto pool (drop top 20% residual) restricted the same way",
                "R": "20 seeded random draws from the affordable veto pool",
                "S": "top-N by ascending residual inside the affordable veto pool "
                     "(added after the first pass: every cap-ranked arm lost money "
                     "while the random draw from the same pool did not)"},
            "thin_pool_floor": "fewer than max(3, N//2) affordable names = thin, not a book",
        },
        "panel": {"dates": len(dates), "symbols": len(symbols),
                  "first": dates[0], "last": dates[-1]},
        "rebalances": len(rows),
        "table": table,
        "paired": paired,
        "pools": pool_diagnostics(rows),
        "random_draw_spread": draw_cagrs(rows, PRIMARY_CAPITAL, TEST_WIDTH),
        "primary": prim,
        "series": series,
        "series_width": int(TEST_WIDTH),
        "control": control,
        "verdict": verdict,
        "verdict_filter": prim["filter_diagnostic"],
        "verdict_signal": prim["signal"]["diagnostic"],
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)

    print("rebalances %d  cutoff %s  panel %d symbols"
          % (len(rows), payload["evidence_cutoff"], len(symbols)))
    print("  control A50 %.2f%% (parent %.2f%%)  A400 %.2f%% (parent %.2f%%) -> %s"
          % (100.0 * (control["replay_a50"] or 0), 100.0 * PARENT_A50_CAGR,
             100.0 * (control["replay_a400"] or 0), 100.0 * PARENT_A400_CAGR,
             "PASS" if control["pass"] else "MISMATCH"))
    for capital in CAPITALS:
        print("  capital %d" % capital)
        print("    %-4s %6s %8s %8s %8s %8s %8s %8s %8s %8s"
              % ("N", "feas%", "A cagr", "P cagr", "V cagr", "R cagr", "S cagr",
                 "V-A t", "V-R t", "S-R t"))
        for n in WIDTHS:
            cell = table[str(int(capital))][str(n)]
            pair = paired[str(int(capital))][str(n)]

            def pct(x):
                return ("%.2f%%" % (100.0 * x)) if x is not None else "n/a"

            def tt(x):
                return ("%+.2f" % x) if x is not None else "n/a"

            print("    %-4d %6.1f %8s %8s %8s %8s %8s %8s %8s %8s"
                  % (n, 100.0 * (cell["A"].get("feasible_share") or 0),
                     pct(cell["A"]["cagr_net"]), pct(cell["P"]["cagr_net"]),
                     pct(cell["V"]["cagr_net"]), pct(cell["R"]["cagr_net"]),
                     pct(cell["S"]["cagr_net"]),
                     tt((pair["V_vs_A"] or {}).get("t")),
                     tt((pair["V_vs_R"] or {}).get("t")),
                     tt((pair["S_vs_R"] or {}).get("t"))))
    sig = prim["signal"]
    print("primary (%d @ N=%d): V %.2f%%  t(V-A) %s  t(V-R) %s  filter t %s  size x%s"
          % (PRIMARY_CAPITAL, TEST_WIDTH,
             100.0 * (prim["cagr_net"] or 0),
             ("%.2f" % prim["t_vs_A"]) if prim["t_vs_A"] is not None else "n/a",
             ("%.2f" % prim["t_vs_R"]) if prim["t_vs_R"] is not None else "n/a",
             ("%.2f" % prim["t_filter_vs_A"]) if prim["t_filter_vs_A"] is not None else "n/a",
             ("%.2f" % prim["size_ratio_V_over_A"])
             if prim["size_ratio_V_over_A"] is not None else "n/a"))
    print("  signal sort S %.2f%%  t(S-R) %s  turnover %.3f -> %s"
          % (100.0 * (sig["cagr_net"] or 0),
             ("%.2f" % sig["t_vs_R"]) if sig["t_vs_R"] is not None else "n/a",
             sig["mean_turnover"] or 0.0, sig["diagnostic"]))
    pools = pool_diagnostics(rows)
    print("  pools: whole pool median cap %.2fbn CNY, one lot %.0f; veto pool median cap "
          "%.2fbn (%s names)" % ((pools["median_mcap_whole_pool"] or 0) / 1e9,
                                 pools["median_one_lot_whole_pool"] or 0,
                                 (pools["median_mcap_veto_pool"] or 0) / 1e9,
                                 pools["median_n_veto"]))
    spread = payload["random_draw_spread"]
    if spread.get("draws"):
        print("  one random draw out of 20, primary cell: %.2f%% .. %.2f%% (median %.2f%%)"
              % (100.0 * spread["min"], 100.0 * spread["max"], 100.0 * spread["median"]))
    print("verdict %s | filter %s -> %s"
          % (verdict, prim["filter_diagnostic"], os.path.relpath(OUT, ROOT)))
    return 0 if verdict != "CONTROL_MISMATCH" else 2


if __name__ == "__main__":
    sys.exit(main())
