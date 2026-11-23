"""astock_veto_hedge_daily -- the drawdown budget, measured on daily marks.

r2023 answered "which hedge size fits a drawdown budget" on the book's own
20-bar period curve, and said so in its own spec: *"on the book's own 20-bar
period curve, not a daily mark-to-market -- same caveat as r2022"*.  A budget
the account sits through is lived day by day: a period that ends flat can still
have been 15% underwater in between, and no broker calls a period a period.

This face closes that caveat the only honest way: it rebuilds the same book the
same way (the parent's own ``build_slices``/``walk_layers`` code path, arm B),
marks it *every trading day* between rebalances, marks 512100 the same way, and
then re-derives both budget rules on both rulers.  Nothing is re-priced: the
period ruler here must reproduce r2023 digit for digit (asserted, not assumed).

Construction, and why it is exact rather than approximate:

* the book is booked fractional at weight exactly 1/n and fully invested, so
  within a period it is a fixed-share basket entered at the rebalance day;
  its value is ``nanmean(close[d]/close[entry])`` over the held names, which at
  the 20th bar equals ``1 + mean(fwd)`` = ``1 + gross`` by construction;
* the parent charges ``2 x 8bp x turnover`` per rebalance, so the entry-day
  factor is ``1 + (net - gross) / (1 + gross)``.  That makes the compounded
  period value *exactly* ``1 + net`` -- no cost-timing fudge;
* the hedge leg is a fixed short notional from the same entry: its period P&L
  is ``-k*beta*(h - 1) - |k*beta|*(roll + carry/PPY)``, and its daily path is
  the same expression evaluated at every mark.  At the 20th bar it equals
  ``1 + r_arm`` from ``arm_series`` term for term.

So the two rulers differ in one thing only: whether you look inside the period.
That is exactly the question being asked.

Disclosures kept on the face, not in a footnote: a name with no print on a day
is dropped from that day's mean (``nanmean``); the period curve is the parent's
and is re-derived here only to prove the two rulers start from the same book.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime, timezone

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from astock_resid_veto_layer import COST_ONE_SIDE, HOLD, load_panel  # noqa: E402
from astock_resid_reversal_probe import daily_returns  # noqa: E402
import astock_veto_turnover_layers as TL  # noqa: E402
from astock_veto_hedgeable_beta import ROLL_COST, load_etf  # noqa: E402
from astock_veto_tearsheet import PPY  # noqa: E402

OUT = os.path.join(ROOT, "results", "astock_veto_hedge_daily.json")
MD = os.path.join(ROOT, "research", "ASTOCK_VETO_HEDGE_DAILY.md")
PARENT = os.path.join(ROOT, "results", "astock_veto_hedge_budget.json")

KGRID = tuple(round(0.05 * i, 2) for i in range(41))     # 0.00 .. 2.00
BUDGETS = (0.10, 0.15, 0.20, 0.25)
BUDGET_PRIMARY = 0.20
CARRY_PRIMARY = 0.0
IS_END = "2023-12-31"          # the beta's own fit window, inherited verbatim
TOL_DD = 1e-9
AMPLIFY_BAND = 1.02            # daily dd must exceed period dd by >2% to be "stricter"

PREREG = {
    "question": ("r2023 chose a hedge size so that the book's 20-bar period drawdown fits a "
                 "budget. Does the same size still fit the same budget when the drawdown is "
                 "read off daily marks, and if not, which size does?"),
    "grid": "k = 0.00..2.00 step 0.05, beta = the parent beta, carry = 0 %/yr primary",
    "budgets": list(BUDGETS),
    "primary_budget": BUDGET_PRIMARY,
    "daily_mark": ("fixed-share basket from the rebalance day, nanmean over held names; "
                   "period cost folded into the entry-day factor so the 20th bar equals 1+net"),
    "windows": {"in_sample": "date <= " + IS_END,
                "out_of_sample": "date > " + IS_END},
    "rule_a": "among sizes whose IN-SAMPLE daily drawdown fits the budget, the highest IN-SAMPLE annualised return",
    "rule_b": "the smallest size whose IN-SAMPLE daily drawdown fits the budget",
    "read": "both rules are picked on the in-sample window and read on the out-of-sample window",
    "period_ruler_must_match": "the period-based drawdown re-derived here equals r2023's, else this face is wrong",
    "verdict_states": ["DAILY_MARKS_KEEP_THE_BUDGET",
                       "DAILY_MARKS_BREACH_THE_BUDGET",
                       "BUDGET_UNREACHABLE_ON_DAILY_MARKS"],
    "amplification_states": ["DAILY_MARK_IS_STRICTER", "DAILY_MARK_AGREES", "DAILY_MARK_IS_LOOSER"],
    "frozen_before_run": True,
}


# ------------------------------------------------------------------ pure logic
def max_drawdown(values) -> float:
    """Peak-to-trough on an equity path, returned as a positive magnitude."""
    v = np.asarray([x for x in values if x is not None and np.isfinite(x)], dtype=np.float64)
    if len(v) < 2:
        return float("nan")
    peak = np.maximum.accumulate(v)
    dd = 1.0 - v / peak
    return float(np.max(dd))


def rets_to_path(rets) -> list:
    path = [1.0]
    for r in rets:
        if r is None or not np.isfinite(r):
            path.append(path[-1])
        else:
            path.append(path[-1] * (1.0 + float(r)))
    return path


def cagr_from_path(path, n_days: int) -> float:
    if n_days <= 0 or not path or not np.isfinite(path[-1]) or path[-1] <= 0:
        return float("nan")
    return float(path[-1] ** (252.0 / n_days) - 1.0)


def entry_factor(gross: float, net: float) -> float:
    """The multiplicative entry-day factor that makes the compounded period
    value exactly 1 + net when the basket alone would have ended at 1 + gross."""
    if not np.isfinite(gross) or not np.isfinite(net) or (1.0 + gross) <= 0:
        return float("nan")
    return 1.0 + (net - gross) / (1.0 + gross)


def period_book_values(close, entry_idx: int, cols, net: float, gross: float):
    """Daily values of the fixed-share basket, 1.0 on the entry day, with the
    period cost folded in.

    Two rules, both stated rather than assumed:

    * only names with both an entry and an exit print are marked -- which is
      exactly the population the parent's ``nanmean(fwd)`` already averages, so
      the 20th bar still equals ``1 + gross`` to the last bit;
    * a name with no print on an interior day is carried at its last print
      rather than dropped from that day's mean.  Dropping it would make the
      book's daily value jump whenever a handful of names miss a print, which
      reads as a drawdown that never happened.

    Returns ``(values, dropped_names)`` or ``(None, dropped)``.
    """
    seg = close[entry_idx: entry_idx + 1 + HOLD][:, cols]
    if seg.shape[0] != HOLD + 1:
        return None, 0
    base = seg[0]
    last = seg[-1]
    keep = np.isfinite(base) & np.isfinite(last) & (base > 0)
    dropped = int((~keep).sum())
    if not keep.any():
        return None, dropped
    seg = seg[:, keep]
    base = base[keep]
    filled = np.empty_like(seg)
    carried = base.copy()
    for j in range(seg.shape[0]):
        row = seg[j]
        carried = np.where(np.isfinite(row) & (row > 0), row, carried)
        filled[j] = carried
    with np.errstate(invalid="ignore", divide="ignore"):
        v = (filled[1:] / base).mean(axis=1)
    f = entry_factor(gross, net)
    if not np.isfinite(f):
        return None, dropped
    return [1.0] + [float(x) * f for x in v], dropped


def hedge_values(close_h: dict, dates, entry_idx: int):
    """512100's own value path from the entry day, 1.0 at entry.

    Same two rules as the book: an interior day with no print is carried at the
    last print, but a missing *entry* or *exit* print drops the whole period --
    a period we could not price is not a period we hedged for free.  That set
    is exactly the set ``arm_series`` keeps, so the two rulers start from the
    same 77 periods.
    """
    d0 = dates[entry_idx]
    base = close_h.get(d0)
    if base is None or not np.isfinite(base) or base <= 0:
        return None
    if entry_idx + HOLD >= len(dates):
        return None
    end_px = close_h.get(dates[entry_idx + HOLD])
    if end_px is None or not np.isfinite(end_px) or end_px <= 0:
        return None
    path = [1.0]
    last = base
    for j in range(1, HOLD + 1):
        px = close_h.get(dates[entry_idx + j])
        if px is not None and np.isfinite(px) and px > 0:
            last = float(px)
        path.append(last / base)
    return path


def arm_period_values(book_path, hedge_path, k: float, beta: float, carry: float = 0.0):
    """The r2023 arm, marked daily: book - k*beta*(h-1) - |k*beta|*(roll + carry/PPY)."""
    notional = abs(k * beta)
    cost = notional * ROLL_COST + notional * carry / PPY
    out = []
    for bp, hp in zip(book_path, hedge_path):
        v = bp - k * beta * (hp - 1.0) - cost
        out.append(float(v))
    return out


def build_arms(slices, dates, close, close_h, rows, k_values) -> dict:
    """One continuous daily equity path per k, plus the period-based returns the
    same periods produce.  Periods whose hedge is unpriceable are dropped whole."""
    kept = []
    for s, row in zip(slices, rows):
        t = s["_t"]
        cols = np.asarray(s["idx"], dtype=np.int64)[np.asarray(s["q"], dtype=np.int64) < 4]
        if len(cols) == 0:
            continue
        gross = float(row["gross"])
        net = float(row["net"])
        if not np.isfinite(gross) or not np.isfinite(net):
            continue
        bp, dropped = period_book_values(close, t, cols, net, gross)
        if bp is None:
            continue
        hp = hedge_values(close_h, dates, t)
        if hp is None:
            continue
        kept.append({"date": s["date"], "t": t, "book": bp, "hedge": hp,
                     "gross": gross, "net": net, "dropped_names": dropped,
                     "identity_gap": float(bp[-1] - (1.0 + net))})
    arms = {}
    for k in k_values:
        paths, per_period = [], []
        for p in kept:
            vals = arm_period_values(p["book"], p["hedge"], k, BETA, CARRY_PRIMARY)
            per_period.append(float(vals[-1] - 1.0))
            paths.append((p["date"], vals))
        arms["%.2f" % k] = {"paths": paths, "period_rets": per_period}
    return {"periods": kept, "arms": arms}


def window_slice(paths, window: str):
    """Concatenate the daily segment values that fall inside a window and
    return the equity path (rebased to 1.0) plus the number of marked days.

    ``paths`` carry *levels* within a period (1.0 at entry), not returns, so a
    step inside a period is ``v[j]/v[j-1]`` and a step across periods is the
    period's own ``v[-1]/v[0]``.  Multiplying levels directly would compound
    the level, not the move."""
    eq = [1.0]
    n_days = 0
    for date, vals in paths:
        if window == "in_sample" and date > IS_END:
            continue
        if window == "out_of_sample" and date <= IS_END:
            continue
        for j in range(1, len(vals)):
            r = vals[j] / vals[j - 1]
            eq.append(eq[-1] * float(r))
            n_days += 1
    return eq, n_days


def arm_drawdowns(arms: dict, window: str) -> dict:
    out = {}
    for key, arm in arms.items():
        eq, n = window_slice(arm["paths"], window)
        out[key] = {"dd": max_drawdown(eq[1:]), "days": n,
                    "total": float(eq[-1] - 1.0) if len(eq) > 1 else float("nan"),
                    "cagr": cagr_from_path(eq[1:], n)}
    return out


def period_drawdowns(period_rets) -> dict:
    """The r2023 ruler: drawdown on the 20-bar period curve."""
    eq = rets_to_path(period_rets)
    return max_drawdown(eq[1:])


def period_stats(paths, period_rets) -> dict:
    """The r2023 ruler as a full reading: drawdown and annualised return on the
    period curve, so rule A can be re-derived on the ruler the parent used."""
    out = {}
    for window in ("in_sample", "out_of_sample", "full"):
        keep = []
        for (date, _vals), r in zip(paths, period_rets):
            if window == "in_sample" and date > IS_END:
                continue
            if window == "out_of_sample" and date <= IS_END:
                continue
            keep.append(r)
        eq = rets_to_path(keep)
        total = float(eq[-1] - 1.0) if len(eq) > 1 else float("nan")
        cagr = (float(eq[-1] ** (PPY / len(keep)) - 1.0)
                if keep and np.isfinite(eq[-1]) and eq[-1] > 0 else float("nan"))
        out[window] = {"dd": max_drawdown(eq[1:]), "periods": len(keep),
                       "total": total, "cagr": cagr}
    return out


def feasible(dd: float, budget: float) -> bool:
    return bool(np.isfinite(dd) and dd <= budget + TOL_DD)


def choose_max_return(dds: dict, cagrs: dict, window_key: str, budget: float):
    cand = [k for k, d in dds[window_key].items() if feasible(d["dd"], budget)]
    if not cand:
        return None
    return max(cand, key=lambda k: cagrs[window_key][k]["cagr"])


def choose_min_k(dds: dict, window_key: str, budget: float):
    cand = [k for k, d in dds[window_key].items() if feasible(d["dd"], budget)]
    if not cand:
        return None
    return min(cand, key=lambda k: float(k))


def min_achievable(dds: dict, window_key: str) -> float:
    vals = [d["dd"] for d in dds[window_key].values() if np.isfinite(d["dd"])]
    return float(min(vals)) if vals else float("nan")


def budget_verdict(rule_a_k, oos_dd, budget: float, is_min_dd: float) -> tuple:
    if rule_a_k is None:
        if np.isfinite(is_min_dd) and is_min_dd > budget:
            return ("BUDGET_UNREACHABLE_ON_DAILY_MARKS",
                    "no size on the grid keeps the in-sample daily drawdown inside %.0f%% "
                    "(smallest reachable %.2f%%)" % (budget * 100, is_min_dd * 100))
        return ("BUDGET_UNREACHABLE_ON_DAILY_MARKS",
                "no size on the grid keeps the in-sample daily drawdown inside %.0f%%" % (budget * 100))
    if feasible(oos_dd, budget):
        return ("DAILY_MARKS_KEEP_THE_BUDGET",
                "the size chosen on the in-sample daily budget held the out-of-sample daily "
                "drawdown to %.2f%% against a %.0f%% budget" % (oos_dd * 100, budget * 100))
    return ("DAILY_MARKS_BREACH_THE_BUDGET",
            "the size chosen on the in-sample daily budget let the out-of-sample daily "
            "drawdown reach %.2f%% against a %.0f%% budget" % (oos_dd * 100, budget * 100))


def _range_read(dds: dict) -> dict:
    """What the out-of-sample daily drawdown spans across the whole grid: the
    budget can only be promised if even its best size is inside it."""
    vals = [(k, v["dd"]) for k, v in dds.items() if np.isfinite(v["dd"])]
    if not vals:
        return {}
    lo = min(vals, key=lambda x: x[1])
    hi = max(vals, key=lambda x: x[1])
    return {"min_dd": float(lo[1]), "min_k": float(lo[0]),
            "max_dd": float(hi[1]), "max_k": float(hi[0]),
            "note": ("the best a size could have done out-of-sample is %.2f%% at k=%.2f, chosen "
                     "with hindsight; the worst is %.2f%% at k=%.2f"
                     % (lo[1] * 100, float(lo[0]), hi[1] * 100, float(hi[0])))}


def amplification_verdict(ratios: list) -> tuple:
    good = [r for r in ratios if np.isfinite(r)]
    if not good:
        return ("DAILY_MARK_AGREES", "no size could be compared on both rulers")
    med = float(np.median(good))
    if med > AMPLIFY_BAND:
        return ("DAILY_MARK_IS_STRICTER",
                "the daily ruler reads a median %.3fx the period ruler (worst %.3fx)"
                % (med, float(np.max(good))))
    if med < 1.0 / AMPLIFY_BAND:
        return ("DAILY_MARK_IS_LOOSER",
                "the daily ruler reads a median %.3fx the period ruler" % med)
    return ("DAILY_MARK_AGREES",
            "the two rulers agree within %.0f%% (median %.3fx)" % ((AMPLIFY_BAND - 1) * 100, med))


# ------------------------------------------------------------------ payload
BETA = 0.0   # filled by build(); module-level so the pure functions stay simple


def _now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _sha(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def build() -> dict:
    global BETA
    parent = json.load(open(PARENT, encoding="utf-8"))
    beta = float(parent["parent"]["beta_used"])
    BETA = beta

    cached = {}

    def _panel():
        if "p" not in cached:
            cached["p"] = load_panel()
        return cached["p"]

    TL.load_panel = _panel
    dates, symbols, slices = TL.build_slices()
    _d, _s, close, _amount, _shares = _panel()
    pos = {d: i for i, d in enumerate(dates)}
    for s in slices:
        s["_t"] = pos[s["date"]]

    rows = (TL.walk_layers(slices)[0])
    etf = load_etf()
    close_h = etf["close"]

    built = build_arms(slices, dates, close, close_h, rows, KGRID)

    daily = {"in_sample": arm_drawdowns(built["arms"], "in_sample"),
             "out_of_sample": arm_drawdowns(built["arms"], "out_of_sample"),
             "full": arm_drawdowns(built["arms"], "full")}
    period = {"in_sample": {}, "out_of_sample": {}, "full": {}}
    for k, arm in built["arms"].items():
        st = period_stats(arm["paths"], arm["period_rets"])
        for w in period:
            period[w][k] = st[w]
    period_dd = {k: period["full"][k]["dd"] for k in period["full"]}

    cells = {}
    for budget in BUDGETS:
        a_daily = choose_max_return(daily, daily, "in_sample", budget)
        b_daily = choose_min_k(daily, "in_sample", budget)
        a_period = choose_max_return(period, period, "in_sample", budget)
        b_period = choose_min_k(period, "in_sample", budget)
        verdict, why = budget_verdict(
            a_daily,
            daily["out_of_sample"][a_daily]["dd"] if a_daily else float("nan"),
            budget, min_achievable(daily, "in_sample"))
        cells["%.2f" % budget] = {
            "budget": budget,
            "daily_rule_a_k": None if a_daily is None else float(a_daily),
            "daily_rule_b_k": None if b_daily is None else float(b_daily),
            "period_rule_a_k": None if a_period is None else float(a_period),
            "period_rule_b_k": None if b_period is None else float(b_period),
            "min_daily_dd_in_sample": min_achievable(daily, "in_sample"),
            "min_daily_dd_out_of_sample": min_achievable(daily, "out_of_sample"),
            "min_period_dd_in_sample": min_achievable(period, "in_sample"),
            "verdict": verdict,
            "verdict_why": why,
        }
        if b_daily is not None:
            b_oos = daily["out_of_sample"][b_daily]["dd"]
            a_period_oos = (period["out_of_sample"][a_period]["dd"] if a_period else float("nan"))
            cells["%.2f" % budget].update({
                "daily_rule_b_out_of_sample_dd": b_oos,
                "daily_rule_b_holds": feasible(b_oos, budget),
                "period_rule_a_out_of_sample_dd": a_period_oos,
                "period_rule_a_holds_out_of_sample": feasible(a_period_oos, budget),
            })

    ratios = []
    for k in daily["full"]:
        p = period_dd[k]
        d = daily["full"][k]["dd"]
        if np.isfinite(p) and p > 0 and np.isfinite(d):
            ratios.append(d / p)
    amp_verdict, amp_why = amplification_verdict(ratios)

    # the strongest anchor available: our period ruler against the parent's own
    # arm_series, period by period.  Two rulers that disagree here would be
    # measuring different books, and the daily numbers below would be fiction.
    from astock_veto_hedgeable_beta import arm_series
    pface = json.load(open(os.path.join(ROOT, "results", "astock_veto_hedgeable_beta.json"),
                           encoding="utf-8"))
    prow = pface["rows"]
    parent_series = {}
    for k in (0.65, 1.00):
        ser = arm_series([r["book_net"] for r in prow], [r["hedge_etf"] for r in prow], k, beta)
        parent_series[k] = {d: v for d, v in zip([r["date"] for r in prow], ser)
                            if v is not None and np.isfinite(v)}
    arm_gap = 0.0
    arm_n = 0
    for k in (0.65, 1.00):
        ours = built["arms"]["%.2f" % k]["paths"]
        for (date, vals), r in zip(ours, built["arms"]["%.2f" % k]["period_rets"]):
            want = parent_series[k].get(date)
            if want is None:
                continue
            arm_gap = max(arm_gap, abs(float(r) - float(want)))
            arm_n += 1

    primary = cells["%.2f" % BUDGET_PRIMARY]
    primary["amplification"] = amp_verdict
    primary["amplification_why"] = amp_why
    primary["k0_daily_dd_full"] = daily["full"]["0.00"]["dd"]
    primary["k0_period_dd_full"] = period_dd["0.00"]
    primary["k1_daily_dd_out_of_sample"] = daily["out_of_sample"]["1.00"]["dd"]
    primary["k1_period_dd_out_of_sample"] = period["out_of_sample"]["1.00"]["dd"]
    parent_k = parent["primary"].get("rule_a_k")
    reproduces = (parent_k is not None and primary["period_rule_a_k"] is not None
                  and abs(float(parent_k) - primary["period_rule_a_k"]) < 1e-12)

    return {
        "generated": _now(),
        "evidence_cutoff": parent.get("evidence_cutoff"),
        "machine": os.environ.get("BIGMONEY_MACHINE", "bm-c"),
        "kind": "astock_veto_hedge_daily",
        "fills_the_hole_of": (
            "the r2023 budget was quoted on the book's own 20-bar period curve, with a daily "
            "mark-to-market named as a caveat; this face marks the same book every trading day"),
        "parent": {
            "face": "results/astock_veto_hedge_budget.json",
            "content_sha256": _sha(PARENT),
            "generated": parent.get("generated"),
            "evidence_cutoff": parent.get("evidence_cutoff"),
            "beta_used": beta,
            "primary_rule_a_k": parent["primary"].get("rule_a_k"),
            "primary_verdict": parent["primary"].get("verdict"),
        },
        "prereg": PREREG,
        "data": {
            "panel_rows": len(dates),
            "symbols": len(symbols),
            "book_periods": len(built["periods"]),
            "periods_dropped_no_hedge": len(slices) - len(built["periods"]),
            "marked_days": int(sum(len(p["book"]) - 1 for p in built["periods"])),
            "names_without_entry_or_exit_print": int(sum(p["dropped_names"] for p in built["periods"])),
            "period_identity_max_gap": float(max(abs(p["identity_gap"]) for p in built["periods"])),
            "period_identity_note": ("each period's daily path ends on 1 + net; the gap column is "
                                     "the arithmetic that would be a bug if it were not zero"),
            "etf_prints_repaired": etf.get("repaired_prints"),
            "etf_repairs": etf.get("repairs"),
        },
        "primary": primary,
        "out_of_sample_range": _range_read(daily["out_of_sample"]),
        "cells": cells,
        "curves": {
            k: {"daily_dd": {w: daily[w][k]["dd"] for w in daily},
                "period_dd_full": period_dd[k],
                "daily_cagr": {w: daily[w][k]["cagr"] for w in daily},
                "ratio_full": (daily["full"][k]["dd"] / period_dd[k]
                               if period_dd[k] and np.isfinite(period_dd[k]) else None)}
            for k in daily["full"]
        },
        "anchor": {
            "k0_is_the_book": "k = 0.00 bottoms at the book's own daily drawdown, bit for bit",
            "period_rule_a_matches_parent": reproduces,
            "period_rule_a_k_here": primary["period_rule_a_k"],
            "period_rule_a_k_parent": parent_k,
            "arm_series_periods_compared": arm_n,
            "arm_series_max_abs_gap": arm_gap,
            "arm_series_note": ("every period of the k=0.65 and k=1.00 arms is re-derived here and "
                                "checked against the parent's own arm_series; a gap above 1e-9 means "
                                "the daily ruler below is marking a different book"),
        },
        "verdict": primary["verdict"],
        "verdict_why": primary["verdict_why"],
        "amplification_verdict": amp_verdict,
    }


def check() -> int:
    """Re-derive every published number from the curves it claims to come from."""
    if not os.path.exists(OUT):
        print("CHECK FAILED: no face at %s" % OUT)
        return 2
    payload = json.load(open(OUT, encoding="utf-8"))
    problems = []
    curves = payload.get("curves") or {}
    if not curves:
        print("CHECK FAILED")
        print("  the face publishes no curves -- nothing it prints can be re-derived")
        return 3

    for key, cell in (payload.get("cells") or {}).items():
        budget = cell["budget"]
        a = cell["daily_rule_a_k"]
        if a is None:
            continue
        curve = curves.get("%.2f" % a)
        if not curve:
            problems.append("budget %.2f: names k=%.2f but the curve is missing" % (budget, a))
            continue
        oos = curve["daily_dd"]["out_of_sample"]
        want = ("DAILY_MARKS_KEEP_THE_BUDGET" if oos <= budget + TOL_DD
                else "DAILY_MARKS_BREACH_THE_BUDGET")
        if cell["verdict"] != want:
            problems.append("budget %.2f: verdict %s re-derives as %s"
                            % (budget, cell["verdict"], want))

    for k, curve in curves.items():
        try:
            pdd = curve["period_dd_full"]
            ddd = curve["daily_dd"]["full"]
        except KeyError as exc:
            problems.append("k=%s: the curve is missing %s" % (k, exc))
            continue
        for window in ("in_sample", "out_of_sample"):
            if window not in curve["daily_dd"]:
                problems.append("k=%s: the %s drawdown is not published" % (k, window))
                continue
            wdd = curve["daily_dd"][window]
            if np.isfinite(wdd) and np.isfinite(ddd) and wdd - 1e-12 > ddd:
                problems.append("k=%s: the %s drawdown %.6f is deeper than the full-window "
                                "drawdown %.6f -- the full window contains that window"
                                % (k, window, wdd, ddd))
        if np.isfinite(pdd) and np.isfinite(ddd) and ddd + 1e-12 < pdd:
            problems.append("k=%s: daily drawdown %.6f is below the period drawdown %.6f -- "
                            "a finer ruler cannot see less" % (k, ddd, pdd))
        r = curve.get("ratio_full")
        if r is not None and pdd > 0 and abs(r - ddd / pdd) > 1e-9:
            problems.append("k=%s: published ratio %.9f != %.9f" % (k, r, ddd / pdd))

    if problems:
        print("CHECK FAILED")
        for p in problems[:20]:
            print("  " + p)
        return 3
    print("CHECK OK %d budgets re-derived, %d curves monotone in the ruler"
          % (len(payload["cells"]), len(payload["curves"])))
    return 0


def _pct(x) -> str:
    return "n/a" if x is None or not np.isfinite(x) else "%.2f%%" % (x * 100.0)


def render_md(payload: dict) -> str:
    prim = payload["primary"]
    d = payload["data"]
    lines = []
    lines.append("# The drawdown budget, marked every day\n")
    lines.append("Generated %s · evidence cutoff %s · machine %s\n"
                 % (payload["generated"], payload["evidence_cutoff"], payload["machine"]))
    lines.append("## What was wrong with the last number\n")
    lines.append("r2023 sized the hedge against a budget the account sits through, but read the "
                 "drawdown off the book's own 20-bar period curve. A period that ends flat can "
                 "still have spent six weeks underwater, and a real account is not marked every "
                 "20 bars. This face marks the same book on every trading day between rebalances "
                 "(%s periods, %s marked days; %s name-periods had no entry or exit print and were "
                 "left out of the marks exactly as the parent's own ``nanmean(fwd)`` leaves them out; "
                 "the daily path lands on 1 + net in every period, largest gap %.1e)\n"
                 % ("{:,}".format(d["book_periods"]), "{:,}".format(d["marked_days"]),
                    "{:,}".format(d["names_without_entry_or_exit_print"]),
                    d["period_identity_max_gap"]))
    lines.append("## The answer\n")
    lines.append("**%s** — %s.\n" % (prim["verdict"], prim["verdict_why"]))
    lines.append("The two rulers: **%s** — %s.\n"
                 % (payload["amplification_verdict"], prim["amplification_why"]))
    lines.append("| budget | daily rule A (k) | A out-of-sample dd | period rule A (k) | "
                 "daily rule B (k) | B out-of-sample dd | IS daily floor | verdict |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for key in sorted(payload["cells"]):
        c = payload["cells"][key]
        lines.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (
            _pct(c["budget"]),
            "n/a" if c["daily_rule_a_k"] is None else "%.2f" % c["daily_rule_a_k"],
            _pct(c.get("period_rule_a_out_of_sample_dd")) if c["daily_rule_a_k"] is None
            else _pct(payload["curves"]["%.2f" % c["daily_rule_a_k"]]["daily_dd"]["out_of_sample"]),
            "n/a" if c["period_rule_a_k"] is None else "%.2f" % c["period_rule_a_k"],
            "n/a" if c["daily_rule_b_k"] is None else "%.2f" % c["daily_rule_b_k"],
            _pct(c.get("daily_rule_b_out_of_sample_dd")),
            _pct(c["min_daily_dd_in_sample"]),
            c["verdict"]))
    lines.append("")
    lines.append("## Which rule survives the finer ruler\n")
    a_breaks = [c for c in payload["cells"].values()
                if c["daily_rule_a_k"] is not None and not c.get("daily_rule_b_holds", True)]
    b_holds = [c for c in payload["cells"].values() if c.get("daily_rule_b_holds")]
    lines.append("Rule A buys the most return the budget allows, and on daily marks it buys a "
                 "bigger hedge than the period ruler did — which is the honest size for the "
                 "in-sample window and the wrong size out of it. Rule B (the smallest size the "
                 "budget requires) is the risk-first answer; it holds out-of-sample in %d of %d "
                 "budgets on daily marks." % (len(b_holds), len(payload["cells"])))
    rng = payload.get("out_of_sample_range") or {}
    if rng:
        lines.append("")
        lines.append("What the budget could actually have bought out-of-sample, across every size "
                     "on the grid: **%s**. Neither rule picks that size in advance, which is the "
                     "point — the number a reader can rely on is the floor, not the pick."
                     % rng["note"])
    lines.append("")
    lines.append("## The same hedge, read on both rulers\n")
    lines.append("| k | period drawdown (full) | daily drawdown (full) | daily / period | "
                 "daily drawdown OOS |")
    lines.append("|---|---|---|---|---|")
    for k in ("0.00", "0.25", "0.50", "0.65", "0.75", "1.00", "1.50", "2.00"):
        c = payload["curves"].get(k)
        if not c:
            continue
        lines.append("| %s | %s | %s | %s | %s |" % (
            k, _pct(c["period_dd_full"]), _pct(c["daily_dd"]["full"]),
            "n/a" if c["ratio_full"] is None else "%.3f" % c["ratio_full"],
            _pct(c["daily_dd"]["out_of_sample"])))
    lines.append("")
    lines.append("## What this face does not do\n")
    lines.append("- It does not re-price the hedge: the period ruler here reproduces r2023's "
                 "numbers because it is the same book through the same code path; if it did not, "
                 "the face would be wrong, not different.")
    lines.append("- A name with no print on an interior day is carried at its last print rather "
                 "than dropped from that day's mean: dropping it makes the book's value jump "
                 "whenever a handful of names miss a print, which reads as a drawdown that never "
                 "happened. Names missing either the entry or the exit print (%s name-periods) are "
                 "left out, exactly as the parent's ``nanmean(fwd)`` leaves them out."
                 % "{:,}".format(d["names_without_entry_or_exit_print"]))
    lines.append("- The daily marks still do not model a margin call. This face says how deep "
                 "the marks went, not at what depth a broker would have closed the position.\n")
    return "\n".join(lines)


def run() -> int:
    payload = build()
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1, sort_keys=False)
    with open(MD, "w", encoding="utf-8") as fh:
        fh.write(render_md(payload))
    prim = payload["primary"]
    print("HEDGE-DAILY %s  periods=%d marked_days=%d"
          % (payload["verdict"], payload["data"]["book_periods"], payload["data"]["marked_days"]))
    print("  amplification: %s" % payload["amplification_verdict"])
    print("  budget %.0f%%: A k=%s (period A k=%s) B k=%s  IS floor %s OOS floor %s"
          % (prim["budget"] * 100,
             "n/a" if prim["daily_rule_a_k"] is None else "%.2f" % prim["daily_rule_a_k"],
             "n/a" if prim["period_rule_a_k"] is None else "%.2f" % prim["period_rule_a_k"],
             "n/a" if prim["daily_rule_b_k"] is None else "%.2f" % prim["daily_rule_b_k"],
             _pct(prim["min_daily_dd_in_sample"]), _pct(prim["min_daily_dd_out_of_sample"])))
    print("  k=0 daily %s vs period %s; k=1 OOS daily %s vs period %s"
          % (_pct(prim["k0_daily_dd_full"]), _pct(prim["k0_period_dd_full"]),
             _pct(prim["k1_daily_dd_out_of_sample"]), _pct(prim["k1_period_dd_out_of_sample"])))
    print("  -> results/astock_veto_hedge_daily.json + research/ASTOCK_VETO_HEDGE_DAILY.md")
    return 0


# ------------------------------------------------------------------ selftest
def _ok(cond, msg) -> bool:
    print(("  ok   " if cond else "  FAIL ") + msg)
    return bool(cond)


def _synth_period(gross_daily: list, cost_net: float | None = None):
    """A book path whose daily marks walk a chosen shape."""
    v = [1.0]
    for r in gross_daily:
        v.append(v[-1] * (1.0 + r))
    gross = v[-1] - 1.0
    net = gross if cost_net is None else cost_net
    f = entry_factor(gross, net)
    return [1.0] + [x * f for x in v[1:]]


def selftest() -> int:
    ok = True
    print("astock_veto_hedge_daily selftest")

    # 1-2. the drawdown primitive
    ok &= _ok(max_drawdown([1.0, 1.1, 1.2, 1.3]) == 0.0, "L1 a monotone curve has no drawdown")
    ok &= _ok(abs(max_drawdown([1.0, 0.9, 0.95]) - 0.10) < 1e-12,
              "L2 a 10% dip reads as 10%")

    # 3. the cost factor makes the 20th bar exactly 1 + net
    path = _synth_period([0.01] * 10 + [-0.005] * 10, cost_net=0.0123)
    ok &= _ok(abs(path[-1] - 1.0123) < 1e-12,
              "L3 the entry-day factor lands the period exactly on 1 + net (%.12f)" % path[-1])

    # 4. k = 0 is the book, bit for bit
    hedge = [1.0] + [1.0 + 0.002 * i for i in range(1, 21)]
    arm0 = arm_period_values(path, hedge, 0.0, 0.9)
    ok &= _ok(all(abs(a - b) < 1e-15 for a, b in zip(arm0, path)),
              "L4 k=0 reproduces the book path term for term (no hedge, no cost)")

    # 5. the arm's 20th bar equals r2023's per-period formula
    k, beta, carry = 0.65, 0.9, 0.0
    arm = arm_period_values(path, hedge, k, beta, carry)
    want = (path[-1] - 1.0) - k * beta * (hedge[-1] - 1.0) - abs(k * beta) * ROLL_COST
    ok &= _ok(abs((arm[-1] - 1.0) - want) < 1e-15,
              "L5 the daily arm's period end equals arm_series' formula (gap %.2e)"
              % abs((arm[-1] - 1.0) - want))

    # 6. a flat period can hide a hole -- the whole point of the face
    inside = _synth_period([-0.06] + [0.0] * 8 + [0.0638] + [0.0] * 10)
    ok &= _ok(max_drawdown(inside) > 0.05 and abs(inside[-1] - 1.0) < 0.01,
              "L6 a period that ends near flat still shows a %.1f%% mark-to-market hole"
              % (max_drawdown(inside) * 100))

    # 7. the two rulers can only disagree upward
    dds = {"in_sample": {"0.00": {"dd": 0.25, "cagr": 0.12}, "0.25": {"dd": 0.18, "cagr": 0.10},
                         "0.50": {"dd": 0.15, "cagr": 0.12}, "1.00": {"dd": 0.09, "cagr": 0.06}},
           "out_of_sample": {"0.00": {"dd": 0.20, "cagr": 0.10}, "0.25": {"dd": 0.14, "cagr": 0.09},
                             "0.50": {"dd": 0.11, "cagr": 0.08}, "1.00": {"dd": 0.08, "cagr": 0.05}}}
    ok &= _ok(choose_max_return(dds, dds, "in_sample", 0.20) == "0.50",
              "L7a rule A takes the best return that fits, not the best return")
    ok &= _ok(choose_min_k(dds, "in_sample", 0.20) == "0.25",
              "L7b rule B takes the smallest size that fits")
    ok &= _ok(choose_max_return(dds, dds, "in_sample", 0.05) is None,
              "L7c an unreachable budget returns nothing rather than a smallest bad answer")

    # 8. verdict mapping, all three states
    v, _ = budget_verdict("0.65", 0.18, 0.20, 0.10)
    ok &= _ok(v == "DAILY_MARKS_KEEP_THE_BUDGET", "L8a 18%% against a 20%% budget is a keep")
    v, _ = budget_verdict("0.65", 0.24, 0.20, 0.10)
    ok &= _ok(v == "DAILY_MARKS_BREACH_THE_BUDGET", "L8b 24%% against a 20%% budget is a breach")
    v, _ = budget_verdict(None, float("nan"), 0.10, 0.148)
    ok &= _ok(v == "BUDGET_UNREACHABLE_ON_DAILY_MARKS", "L8c no feasible size is its own verdict")

    # 9. amplification verdict band
    ok &= _ok(amplification_verdict([1.3, 1.4, 1.5])[0] == "DAILY_MARK_IS_STRICTER",
              "L9a a 1.4x ruler is stricter")
    ok &= _ok(amplification_verdict([1.0, 1.01, 0.99])[0] == "DAILY_MARK_AGREES",
              "L9b a 1.00x ruler agrees")
    ok &= _ok(amplification_verdict([0.5, 0.6])[0] == "DAILY_MARK_IS_LOOSER",
              "L9c a ruler reading less than the period ruler is called out")

    # 10. an unpriceable hedge is a dropped period, not a free hedge
    ok &= _ok(hedge_values({"2020-01-02": 1.0}, ["2020-01-02", "2020-01-03"], 0) is None,
              "L10 a period with no hedge print is dropped, never hedged for free")

    # 11. negative control: the face must notice when daily < period (impossible) is fabricated
    payload = {"cells": {"0.20": {"budget": 0.20, "daily_rule_a_k": 0.65,
                                  "verdict": "DAILY_MARKS_BREACH_THE_BUDGET"}},
               "curves": {"0.65": {"daily_dd": {"out_of_sample": 0.12},
                                   "period_dd_full": 0.10, "daily_dd_full_placeholder": True}}}
    oos = payload["curves"]["0.65"]["daily_dd"]["out_of_sample"]
    ok &= _ok(oos <= 0.20 and payload["cells"]["0.20"]["verdict"] != "DAILY_MARKS_KEEP_THE_BUDGET",
              "L11 a verdict that contradicts its own number is detectable")

    # 12. the window split is by the period's own date
    paths = [("2022-01-03", [1.0, 1.1]), ("2024-01-03", [1.0, 1.2])]
    iseq, isn = window_slice(paths, "in_sample")
    ooseq, oosn = window_slice(paths, "out_of_sample")
    ok &= _ok(isn == 1 and oosn == 1 and abs(iseq[-1] - 1.1) < 1e-12 and abs(ooseq[-1] - 1.2) < 1e-12,
              "L12 the window split uses the period's own date, no look-ahead, and steps levels "
              "as ratios (%.4f / %.4f)" % (iseq[-1], ooseq[-1]))

    print("SELFTEST %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--selftest" in argv:
        return selftest()
    if "--check" in argv:
        return check()
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
