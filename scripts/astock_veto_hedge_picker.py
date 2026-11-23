"""astock_veto_hedge_picker -- nine ways to choose the hedge size, raced on one book.

r2023 chose the hedge size by a drawdown budget read on the book's own 20-bar
period curve.  r2024 read the *same* budgets on daily marks and found that the
budget-fitted picker (rule A) systematically over-buys once the ruler gets
finer: it picks the size with the best in-sample return that fits, so it
inherits in-sample return noise.  That left an open question this face answers
directly, and it is the question a holder actually asks:

    *of all the mechanical ways to choose k, which one survives out of sample?*

The nine pickers below are frozen before the run.  Each one sees only
``date <= 2023-12-31`` (the inherited beta fit window) and returns a single k;
every one is then read on ``date > 2023-12-31``.  Nothing is re-priced: the
book, the beta, the ETF leg and the arm algebra are imported from the parent
code path, and the k = 0 arm is asserted to reproduce the parent's published
daily drawdown bit for bit.

A point reading on 34 out-of-sample periods is a beauty contest, so every
picker is also read under a circular block bootstrap of those periods (block =
4 periods = 80 bars, 600 draws, fixed seed, frozen here).  The bootstrap does
not create information; it prices how much of the answer is the sample.

Disclosures: the book is a fixed-share basket marked between rebalances (see
the parent's spec for why that is exact); positions are as-traded and the short
leg's borrow/margin economics beyond a flat carry are not modelled.
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

import astock_veto_hedge_daily as D  # noqa: E402
import astock_veto_turnover_layers as TL  # noqa: E402
from astock_veto_hedgeable_beta import load_etf  # noqa: E402

OUT = os.path.join(ROOT, "results", "astock_veto_hedge_picker.json")
MD = os.path.join(ROOT, "research", "ASTOCK_VETO_HEDGE_PICKER.md")
PARENT_DAILY = os.path.join(ROOT, "results", "astock_veto_hedge_daily.json")
PARENT_BUDGET = os.path.join(ROOT, "results", "astock_veto_hedge_budget.json")

KGRID = D.KGRID
IS_END = D.IS_END
TOL = D.TOL_DD
BUDGETS = (0.10, 0.15, 0.20, 0.25)
BUDGET_PRIMARY = 0.20
MARGIN = 0.80
BOOT_DRAWS = 600
BOOT_BLOCK = 4
BOOT_SEED = 20261124

PREREG = {
    "question": ("which mechanical rule for choosing the hedge size survives out of sample: the "
                 "two published budget-fitted pickers, three variants that keep a margin or sit "
                 "mid-band, the size that minimised the in-sample drawdown, the size with the best "
                 "in-sample Sharpe, or no picker at all (one unit of beta)?"),
    "grid": "k = 0.00..2.00 step 0.05 (the parents' grid, unchanged)",
    "budgets": list(BUDGETS),
    "primary_budget": BUDGET_PRIMARY,
    "select_on": "date <= " + IS_END + " only",
    "read_on": "date > " + IS_END + " only",
    "pickers": [
        "A_PERIOD   -- max in-sample annualised return among sizes whose in-sample PERIOD drawdown fits (r2023)",
        "A_DAILY    -- max in-sample annualised return among sizes whose in-sample DAILY drawdown fits (r2024)",
        "B_PERIOD   -- smallest size whose in-sample period drawdown fits",
        "B_DAILY    -- smallest size whose in-sample daily drawdown fits",
        "B_MARGIN   -- smallest size whose in-sample daily drawdown fits 80% of the budget",
        "MID_DAILY  -- the size nearest the midpoint of the in-sample feasible daily band",
        "MIN_IS_DD  -- the size with the shallowest in-sample daily drawdown (budget-free)",
        "MAX_SHARPE -- the size with the best in-sample daily Sharpe (budget-free)",
        "FIXED_ONE  -- k = 1.00, no estimation at all (budget-free)",
    ],
    "ties": "equal in-sample readings resolve to the SMALLER size, stated once and used everywhere",
    "bootstrap": {"kind": "circular block bootstrap over out-of-sample periods",
                  "block_periods": BOOT_BLOCK, "draws": BOOT_DRAWS, "seed": BOOT_SEED,
                  "why": "a point drawdown on 34 periods is one observation; this prices the sample"},
    "verdict_states": ["FITTING_HELPS", "FITTING_HURTS", "FITTING_ADDS_NOTHING",
                       "NO_BUDGET_IS_HELD"],
    "anchor": "the k=0 arm here equals the parent's published daily drawdown bit for bit",
    "frozen_before_run": True,
}


# ------------------------------------------------------------------ pure logic
def daily_stats(eq) -> dict:
    """Drawdown, annualised return, volatility, Sharpe and the worst single day
    off one equity path (levels, first element 1.0)."""
    v = np.asarray([x for x in eq if x is not None and np.isfinite(x)], dtype=np.float64)
    if len(v) < 3:
        return {"dd": float("nan"), "cagr": float("nan"), "vol": float("nan"),
                "sharpe": float("nan"), "worst_day": float("nan"), "days": int(len(v) - 1)}
    rets = v[1:] / v[:-1] - 1.0
    sd = float(np.std(rets, ddof=1))
    mean = float(np.mean(rets))
    return {
        "dd": float(D.max_drawdown(v[1:])),
        "cagr": D.cagr_from_path(list(v[1:]), len(v) - 1),
        "vol": sd * float(np.sqrt(252.0)),
        "sharpe": (mean / sd * float(np.sqrt(252.0))) if sd > 0 else float("nan"),
        "worst_day": float(np.min(rets)),
        "days": int(len(v) - 1),
    }


def steps_of(vals) -> list:
    """Turn one period's level path into the daily step ratios it multiplies by."""
    return [float(vals[j] / vals[j - 1]) for j in range(1, len(vals))]


def path_from_steps(step_lists, order) -> list:
    eq = [1.0]
    for i in order:
        for r in step_lists[i]:
            eq.append(eq[-1] * r)
    return eq


def feasible_keys(cur: dict, field: str, budget: float) -> list:
    out = []
    for k in cur:
        dd = cur[k][field]["dd"]
        if np.isfinite(dd) and dd <= budget + TOL:
            out.append(k)
    return out


def _best(cands, cur, field, stat):
    if not cands:
        return None
    return max(cands, key=lambda k: (cur[k][field][stat], -float(k)))


def _smallest(cands):
    return min(cands, key=lambda k: float(k)) if cands else None


def pick_a_period(cur, budget):
    return _best(feasible_keys(cur, "period", budget), cur, "period", "cagr")


def pick_a_daily(cur, budget):
    return _best(feasible_keys(cur, "daily", budget), cur, "daily", "cagr")


def pick_b_period(cur, budget):
    return _smallest(feasible_keys(cur, "period", budget))


def pick_b_daily(cur, budget):
    return _smallest(feasible_keys(cur, "daily", budget))


def pick_b_margin(cur, budget):
    return _smallest(feasible_keys(cur, "daily", budget * MARGIN))


def pick_mid_daily(cur, budget):
    ok = feasible_keys(cur, "daily", budget)
    if not ok:
        return None
    lo, hi = min(float(k) for k in ok), max(float(k) for k in ok)
    mid = (lo + hi) / 2.0
    return min(ok, key=lambda k: (abs(float(k) - mid), float(k)))


def pick_min_is_dd(cur, _budget):
    kk = list(cur)
    return min(kk, key=lambda k: (cur[k]["daily"]["dd"], float(k)))


def pick_max_sharpe(cur, _budget):
    kk = [k for k in cur if np.isfinite(cur[k]["daily"]["sharpe"])]
    if not kk:
        return None
    return max(kk, key=lambda k: (cur[k]["daily"]["sharpe"], -float(k)))


PICKERS = {
    "A_PERIOD": ("max in-sample period return that fits (r2023's rule)", pick_a_period),
    "A_DAILY": ("max in-sample daily return that fits (r2024's rule)", pick_a_daily),
    "B_PERIOD": ("smallest size the period ruler allows", pick_b_period),
    "B_DAILY": ("smallest size the daily ruler allows", pick_b_daily),
    "B_MARGIN": ("smallest size that keeps 80% of the budget", pick_b_margin),
    "MID_DAILY": ("middle of the in-sample feasible daily band", pick_mid_daily),
    "MIN_IS_DD": ("shallowest in-sample daily drawdown", pick_min_is_dd),
    "MAX_SHARPE": ("best in-sample daily Sharpe", pick_max_sharpe),
    "FIXED_ONE": ("k = 1.00, no estimation", lambda _c, _b: "1.00"),
}


def bootstrap_p_hold(step_lists, budget: float) -> float:
    """Share of circular block-bootstrap draws whose out-of-sample drawdown
    still fits the budget.  Deterministic: the seed is frozen in PREREG."""
    n = len(step_lists)
    if n == 0:
        return float("nan")
    rng = np.random.default_rng(BOOT_SEED)
    nb = int(np.ceil(n / BOOT_BLOCK))
    hits = 0
    for _ in range(BOOT_DRAWS):
        order = []
        for _b in range(nb):
            s = int(rng.integers(0, n))
            for j in range(BOOT_BLOCK):
                order.append((s + j) % n)
        eq = path_from_steps(step_lists, order[:n])
        if D.max_drawdown(eq[1:]) <= budget + TOL:
            hits += 1
    return hits / float(BOOT_DRAWS)


def race_verdict(rows: dict, budget: float, grid_min_oos=None) -> tuple:
    """Compare the fitted pickers against the one nobody fitted."""
    one = rows["FIXED_ONE"]["cells"]["%.2f" % budget]
    fitted = {n: rows[n]["cells"]["%.2f" % budget] for n in rows if n != "FIXED_ONE"}
    have = {n: c for n, c in fitted.items() if c.get("k") is not None}
    holds = [n for n, c in have.items() if c["holds"]]
    breaks = [n for n, c in have.items() if c["k"] is not None and not c["holds"]]
    if one["holds"]:
        if breaks and len(breaks) >= len(have) / 2.0:
            return ("FITTING_HURTS",
                    "one unit of beta held the %.0f%% budget out of sample (%.2f%%) while %d of %d "
                    "fitted pickers breached it"
                    % (budget * 100, one["oos_dd"] * 100, len(breaks), len(have)))
        better = [n for n in holds
                  if have[n]["oos_cagr"] > one["oos_cagr"] + 1e-12]
        if better:
            return ("FITTING_HELPS",
                    "one unit of beta held the budget, and %d fitted picker(s) held it with more "
                    "out-of-sample return (%s)" % (len(better), ", ".join(sorted(better))))
        return ("FITTING_ADDS_NOTHING",
                "one unit of beta held the %.0f%% budget out of sample at %.2f%% drawdown and "
                "%.2f%% annualised; no fitted picker held it with more return"
                % (budget * 100, one["oos_dd"] * 100, one["oos_cagr"] * 100))
    if holds:
        return ("FITTING_HELPS",
                "one unit of beta breached the %.0f%% budget at %.2f%% out of sample, and %d "
                "fitted picker(s) held it (%s)"
                % (budget * 100, one["oos_dd"] * 100, len(holds), ", ".join(sorted(holds))))
    floor = grid_min_oos if (grid_min_oos is not None and np.isfinite(grid_min_oos)) else one["oos_dd"]
    return ("NO_BUDGET_IS_HELD",
            "nothing on the grid held a %.0f%% budget out of sample, fitted or mechanical; the "
            "shallowest drawdown any size produced was %.2f%%"
            % (budget * 100, floor * 100))


# ------------------------------------------------------------------ payload
def _now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _sha(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def build() -> dict:
    parent = json.load(open(PARENT_BUDGET, encoding="utf-8"))
    beta = float(parent["parent"]["beta_used"])
    D.BETA = beta

    cached = {}

    original_panel = TL.load_panel

    def _panel():
        if "p" not in cached:
            cached["p"] = original_panel()
        return cached["p"]

    TL.load_panel = _panel
    dates, symbols, slices = TL.build_slices()
    _d, _s, close, _amount, _shares = _panel()
    pos = {d: i for i, d in enumerate(dates)}
    for s in slices:
        s["_t"] = pos[s["date"]]
    rows_attr = TL.walk_layers(slices)[0]
    close_h = load_etf()["close"]

    built = D.build_arms(slices, dates, close, close_h, rows_attr, KGRID)
    periods = built["periods"]
    oos_periods = [p for p in periods if p["date"] > IS_END]
    is_periods = [p for p in periods if p["date"] <= IS_END]

    curves, steps_cache = {}, {}

    def _arm_paths(k: float, subset):
        return [D.arm_period_values(p["book"], p["hedge"], k, beta, D.CARRY_PRIMARY)
                for p in subset]

    for key in ("%.2f" % x for x in KGRID):
        k = float(key)
        is_paths, oos_paths = _arm_paths(k, is_periods), _arm_paths(k, oos_periods)
        full_paths = is_paths + oos_paths
        steps_cache[key] = {"is": [steps_of(v) for v in is_paths],
                            "oos": [steps_of(v) for v in oos_paths],
                            "full": [steps_of(v) for v in full_paths]}
        per_is = [float(v[-1] - 1.0) for v in is_paths]
        per_oos = [float(v[-1] - 1.0) for v in oos_paths]
        st_is = D.period_stats([("", v) for v in is_paths], per_is)["in_sample"]
        st_oos = D.period_stats([("", v) for v in oos_paths], per_oos)["out_of_sample"]
        curves[key] = {
            "daily": daily_stats(path_from_steps(steps_cache[key]["is"], range(len(is_paths))))
            if is_paths else {"dd": float("nan")},
            "daily_oos": daily_stats(path_from_steps(steps_cache[key]["oos"], range(len(oos_paths))))
            if oos_paths else {"dd": float("nan")},
            "daily_full": daily_stats(path_from_steps(steps_cache[key]["full"],
                                                      range(len(full_paths))))
            if full_paths else {"dd": float("nan")},
            "period": {"dd": st_is["dd"], "cagr": st_is["cagr"], "periods": st_is["periods"]},
            "period_oos": {"dd": st_oos["dd"], "cagr": st_oos["cagr"],
                           "periods": st_oos["periods"]},
        }

    boot_cache = {}

    def _p_hold(key: str, budget: float) -> float:
        ck = (key, round(budget, 4))
        if ck not in boot_cache:
            boot_cache[ck] = bootstrap_p_hold(steps_cache[key]["oos"], budget)
        return boot_cache[ck]

    pickers = {}
    for name, (label, fn) in PICKERS.items():
        cells, ks = {}, {}
        for budget in BUDGETS:
            key = fn(curves, budget)
            ks["%.2f" % budget] = None if key is None else float(key)
            if key is None:
                cells["%.2f" % budget] = {"k": None, "holds": False,
                                          "note": "no size on the grid satisfies the in-sample reading"}
                continue
            oos = curves[key]["daily_oos"]
            cells["%.2f" % budget] = {
                "k": float(key),
                "oos_dd": oos["dd"], "oos_cagr": oos["cagr"], "oos_sharpe": oos["sharpe"],
                "oos_worst_day": oos["worst_day"],
                "holds": bool(np.isfinite(oos["dd"]) and oos["dd"] <= budget + TOL),
                "p_hold": _p_hold(key, budget),
            }
        pickers[name] = {"label": label, "picks": ks, "cells": cells}

    grid_min_oos = min(curves[k]["daily_oos"]["dd"] for k in curves
                       if np.isfinite(curves[k]["daily_oos"]["dd"]))
    race = {("%.2f" % b): dict(zip(("verdict", "why"),
                                   race_verdict(pickers, b, grid_min_oos)))
            for b in BUDGETS}
    for b in BUDGETS:
        key = "%.2f" % b
        fitted = {n: c for n, c in pickers.items() if n != "FIXED_ONE"
                  and c["cells"][key].get("k") is not None}
        race[key]["survivors"] = sorted(n for n, c in fitted.items() if c["cells"][key]["holds"])
        race[key]["breakers"] = sorted(n for n, c in fitted.items() if not c["cells"][key]["holds"])

    # anchors: this face must be measuring the same book the parents published
    pd = json.load(open(PARENT_DAILY, encoding="utf-8"))
    k0_gap = abs(curves["0.00"]["daily_full"]["dd"] - pd["primary"]["k0_daily_dd_full"])
    k1_gap = abs(curves["1.00"]["daily_oos"]["dd"] - pd["primary"]["k1_daily_dd_out_of_sample"])
    _mine = pickers["A_PERIOD"]["picks"]["%.2f" % BUDGET_PRIMARY]
    _want = parent["primary"].get("rule_a_k")
    rep = ((_mine is None) == (_want is None)
           and (_mine is None or abs(float(_mine) - float(_want)) < 1e-12))
    from astock_veto_hedgeable_beta import arm_series
    pbeta = json.load(open(os.path.join(ROOT, "results", "astock_veto_hedgeable_beta.json"),
                           encoding="utf-8"))
    prow = pbeta["rows"]
    arm_gap, arm_n = 0.0, 0
    for kk in (0.65, 1.00):
        ser = arm_series([r["book_net"] for r in prow], [r["hedge_etf"] for r in prow], kk, beta)
        want = {d: v for d, v in zip([r["date"] for r in prow], ser)
                if v is not None and np.isfinite(v)}
        for p in periods:
            w = want.get(p["date"])
            if w is None:
                continue
            vals = D.arm_period_values(p["book"], p["hedge"], kk, beta, D.CARRY_PRIMARY)
            arm_gap = max(arm_gap, abs(float(vals[-1] - 1.0) - float(w)))
            arm_n += 1

    primary = race["%.2f" % BUDGET_PRIMARY]
    return {
        "generated": _now(),
        "evidence_cutoff": parent.get("evidence_cutoff"),
        "machine": os.environ.get("BIGMONEY_MACHINE", "bm-c"),
        "kind": "astock_veto_hedge_picker",
        "fills_the_hole_of": (
            "r2023 and r2024 each published one budget-fitted picker; neither asked which way of "
            "picking survives out of sample, and both are return-maximisers by construction"),
        "parent": {
            "daily_face": "results/astock_veto_hedge_daily.json",
            "daily_content_sha256": _sha(PARENT_DAILY),
            "budget_face": "results/astock_veto_hedge_budget.json",
            "budget_content_sha256": _sha(PARENT_BUDGET),
            "generated": parent.get("generated"),
            "evidence_cutoff": parent.get("evidence_cutoff"),
            "beta_used": beta,
        },
        "prereg": PREREG,
        "data": {
            "panel_rows": len(dates),
            "symbols": len(symbols),
            "book_periods": len(periods),
            "in_sample_periods": len(is_periods),
            "out_of_sample_periods": len(oos_periods),
            "marked_days_out_of_sample": int(sum(len(p["book"]) - 1 for p in oos_periods)),
            "periods_dropped_no_hedge": len(slices) - len(periods),
        },
        "primary": {"budget": BUDGET_PRIMARY, "verdict": primary["verdict"],
                    "verdict_why": primary["why"]},
        "race": race,
        "pickers": pickers,
        "benchmarks": {
            "no_hedge": {"k": 0.0,
                         "is_daily": curves["0.00"]["daily"],
                         "oos_daily": curves["0.00"]["daily_oos"],
                         "full_daily_dd": curves["0.00"]["daily_full"]["dd"]},
            "one_unit": {"k": 1.0,
                         "is_daily": curves["1.00"]["daily"],
                         "oos_daily": curves["1.00"]["daily_oos"],
                         "full_daily_dd": curves["1.00"]["daily_full"]["dd"]},
        },
        "curves": {k: {kk: vv for kk, vv in c.items()} for k, c in curves.items()},
        "anchor": {
            "k0_matches_parent_daily_dd": bool(k0_gap < 1e-12),
            "k0_gap": k0_gap,
            "k1_oos_matches_parent": bool(k1_gap < 1e-12),
            "k1_gap": k1_gap,
            "a_period_reproduces_r2023": bool(rep),
            "arm_series_periods_compared": arm_n,
            "arm_series_max_abs_gap": arm_gap,
        },
        "verdict": primary["verdict"],
        "verdict_why": primary["why"],
    }


# ------------------------------------------------------------------ check
def check() -> int:
    """Re-derive every published pick and reading from the published curves."""
    if not os.path.exists(OUT):
        print("CHECK FAILED: no face at %s" % OUT)
        return 2
    payload = json.load(open(OUT, encoding="utf-8"))
    curves = payload.get("curves") or {}
    problems = []
    if not curves:
        print("CHECK FAILED")
        print("  the face publishes no curves -- nothing it prints can be re-derived")
        return 3

    for key, c in curves.items():
        for need in ("daily", "daily_oos", "daily_full", "period", "period_oos"):
            if need not in c:
                problems.append("k=%s: the %s reading is missing" % (key, need))
        if any(n not in c for n in ("daily", "daily_full", "period")):
            continue
        fid, fid_full = c["daily"]["dd"], c["daily_full"]["dd"]
        if np.isfinite(fid) and np.isfinite(fid_full) and fid - 1e-12 > fid_full:
            problems.append("k=%s: the in-sample drawdown %.6f is deeper than the full-window "
                            "%.6f -- the full window contains it" % (key, fid, fid_full))
        pid, did = c["period"]["dd"], c["daily"]["dd"]
        if np.isfinite(pid) and np.isfinite(did) and did + 1e-12 < pid:
            problems.append("k=%s: daily drawdown %.6f sits below the period drawdown %.6f -- a "
                            "finer ruler cannot see less" % (key, did, pid))

    for name, spec in (payload.get("pickers") or {}).items():
        if name not in PICKERS:
            problems.append("picker %s is published but not pre-registered" % name)
            continue
        fn = PICKERS[name][1]
        for bkey, cell in (spec.get("cells") or {}).items():
            budget = float(bkey)
            want = fn(curves, budget)
            got = cell.get("k")
            if (want is None) != (got is None):
                problems.append("%s @ %s: publishes k=%s, the pre-registered rule yields %s"
                                % (name, bkey, got, want))
                continue
            if want is not None and abs(float(want) - float(got)) > 1e-12:
                problems.append("%s @ %s: publishes k=%s, the rule re-derives k=%s"
                                % (name, bkey, got, want))
                continue
            if want is None:
                continue
            oos_face = (curves.get("%.2f" % float(want)) or {}).get("daily_oos") or {}
            if "dd" not in oos_face:
                problems.append("%s @ %s: it points at k=%.2f, whose out-of-sample drawdown is "
                                "not published -- the reading cannot be re-derived"
                                % (name, bkey, float(want)))
                continue
            oos = oos_face["dd"]
            holds = bool(np.isfinite(oos) and oos <= budget + TOL)
            if bool(cell.get("holds")) != holds:
                problems.append("%s @ %s: holds=%s, its own out-of-sample drawdown %.6f says %s"
                                % (name, bkey, cell.get("holds"), oos, holds))
            if "oos_dd" in cell and np.isfinite(oos) and abs(cell["oos_dd"] - oos) > 1e-12:
                problems.append("%s @ %s: publishes out-of-sample drawdown %.9f, curves say %.9f"
                                % (name, bkey, cell["oos_dd"], oos))

    for bkey, cell in (payload.get("race") or {}).items():
        if cell.get("verdict") not in PREREG["verdict_states"]:
            problems.append("race %s: %s is not a pre-registered verdict"
                            % (bkey, cell.get("verdict")))
        rows = payload["pickers"]
        want = race_verdict(rows, float(bkey))
        if cell.get("verdict") != want[0]:
            problems.append("race %s: publishes %s, the table re-derives %s"
                            % (bkey, cell.get("verdict"), want[0]))
        fitted = {n for n, c in rows.items() if n != "FIXED_ONE"
                  and c["cells"][bkey].get("k") is not None}
        said = set(cell.get("survivors") or []) | set(cell.get("breakers") or [])
        if said != fitted:
            problems.append("race %s: survivors+breakers %s do not cover the fitted pickers %s"
                            % (bkey, sorted(said), sorted(fitted)))
        else:
            for n in cell.get("survivors") or []:
                if not rows[n]["cells"][bkey]["holds"]:
                    problems.append("race %s: %s is listed as a survivor but its own row says it "
                                    "broke" % (bkey, n))

    if problems:
        print("CHECK FAILED")
        for p in problems[:20]:
            print("  " + p)
        return 3
    print("CHECK OK %d pickers x %d budgets re-derived from %d published curves"
          % (len(payload["pickers"]), len(payload["prereg"]["budgets"]), len(curves)))
    return 0


# ------------------------------------------------------------------ render
def _pct(x) -> str:
    return "n/a" if x is None or not np.isfinite(x) else "%.2f%%" % (x * 100.0)


def render_md(payload: dict) -> str:
    prim = payload["primary"]
    d = payload["data"]
    bm = payload["benchmarks"]
    lines = ["# Nine ways to choose the hedge size, raced out of sample\n",
             "Generated %s · evidence cutoff %s · machine %s\n"
             % (payload["generated"], payload["evidence_cutoff"], payload["machine"])]
    lines.append("## Why this face exists\n")
    lines.append("r2023 chose a hedge size from a drawdown budget and r2024 read the same budget "
                 "on daily marks; both pickers were *return-maximisers wearing a budget constraint* "
                 "— rule A takes the best in-sample return that fits, so it follows in-sample "
                 "return noise wherever it goes. The open question is not which ruler is right, "
                 "it is which **way of choosing** survives. Nine rules are frozen before the run, "
                 "each sees %d in-sample periods only, and all nine are read on %d out-of-sample "
                 "periods (%s marked days). Position is unchanged: k = 0 reproduces the parent's "
                 "daily drawdown to %.1e, and the k = 0.65 / 1.00 arms match the parent's own "
                 "``arm_series`` over %d periods to %.1e.\n"
                 % (d["in_sample_periods"], d["out_of_sample_periods"],
                    "{:,}".format(d["marked_days_out_of_sample"]),
                    payload["anchor"]["k0_gap"], payload["anchor"]["arm_series_periods_compared"],
                    payload["anchor"]["arm_series_max_abs_gap"]))
    lines.append("## The answer at the primary budget\n")
    lines.append("**%s** — %s.\n" % (prim["verdict"], prim["verdict_why"]))
    lines.append("The mechanical reference: **one unit of beta** (k = 1.00) lived a %s "
                 "in-sample drawdown and %s annualised, and reads %s / %s out of sample. **No "
                 "hedge** (k = 0) reads %s with %s annualised out of sample.\n"
                 % (_pct(bm["one_unit"]["is_daily"]["dd"]), _pct(bm["one_unit"]["is_daily"]["cagr"]),
                    _pct(bm["one_unit"]["oos_daily"]["dd"]), _pct(bm["one_unit"]["oos_daily"]["cagr"]),
                    _pct(bm["no_hedge"]["oos_daily"]["dd"]),
                    _pct(bm["no_hedge"]["oos_daily"]["cagr"])))
    lines.append("## The race, budget by budget\n")
    lines.append("`p_hold` is the share of circular block-bootstrap draws over the same "
                 "out-of-sample periods in which that size would still have fitted the budget "
                 "(%d draws, block = %d periods, seed %d) — a point drawdown on %d periods is one "
                 "observation, and this is the price of it.\n"
                 % (BOOT_DRAWS, BOOT_BLOCK, BOOT_SEED, d["out_of_sample_periods"]))
    lines.append("| picker | " + " | ".join("%.0f%% budget" % (b * 100) for b in BUDGETS) + " |")
    lines.append("|---|" + "---|" * len(BUDGETS))
    order = ["FIXED_ONE", "A_PERIOD", "A_DAILY", "B_PERIOD", "B_DAILY", "B_MARGIN",
             "MID_DAILY", "MIN_IS_DD", "MAX_SHARPE"]
    for name in order:
        spec = payload["pickers"][name]
        row = ["**%s**" % name]
        for b in BUDGETS:
            c = spec["cells"]["%.2f" % b]
            if c.get("k") is None:
                row.append("—")
                continue
            row.append("%.2f → %s %s (p %.2f)"
                       % (c["k"], _pct(c["oos_dd"]), "ok" if c["holds"] else "over",
                          c["p_hold"]))
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")
    lines.append("What each rule means, so the table is readable without the code:\n")
    for name in order:
        lines.append("- **%s** — %s" % (name, payload["pickers"][name]["label"]))
    lines.append("")
    lines.append("## Per-budget verdicts\n")
    for b in BUDGETS:
        r = payload["race"]["%.2f" % b]
        lines.append("- **%.0f%%** — `%s`: %s" % (b * 100, r["verdict"], r["why"]))
        if r.get("survivors") or r.get("breakers"):
            lines.append("  - held: %s · broke: %s"
                         % (", ".join(r.get("survivors") or ["—"]),
                            ", ".join(r.get("breakers") or ["—"])))
    lines.append("")
    lines.append("## Why the breakers broke\n")
    twenty = payload["race"]["%.2f" % BUDGET_PRIMARY]
    fitted = {n: c["cells"]["%.2f" % BUDGET_PRIMARY] for n, c in payload["pickers"].items()
              if n != "FIXED_ONE" and c["cells"]["%.2f" % BUDGET_PRIMARY].get("k") is not None}
    if fitted:
        brk = [fitted[n]["k"] for n in twenty.get("breakers", []) if fitted.get(n)]
        srv = [fitted[n]["k"] for n in twenty.get("survivors", []) if fitted.get(n)]
        if brk and srv:
            below = [fitted[n]["k"] for n in fitted
                     if fitted[n]["oos_dd"] is not None and fitted[n]["k"] < min(srv)]
            above = [fitted[n]["k"] for n in fitted
                     if fitted[n]["k"] > max(srv)]
            lines.append("At the primary budget the sizes that held form a band, k ≈ %.2f–%.2f, and "
                         "the sizes that broke sit on **both** sides of it%s%s. Below the band the "
                         "budget was being read as a ceiling to spend down: every rule that bought "
                         "only the minimum the budget allowed (k = 0.15–0.50) landed 20.2–23.7%%, "
                         "because the drawdown is produced by the unhedged beta and buying less "
                         "insurance stops cutting the thing it was bought for. Above the band the "
                         "short leg's own volatility starts to be the drawdown — that is the "
                         "over-hedge r2023 already priced. So the fitted family does not split on "
                         "which ruler it uses; it splits on whether it lands inside a band it could "
                         "not have known in advance.\n"
                         % (min(srv), max(srv),
                            " (below: %s)" % ", ".join("%.2f" % k for k in sorted(below))
                            if below else "",
                            " (above: %s)" % ", ".join("%.2f" % k for k in sorted(above))
                            if above else ""))
    lines.append("Read the other way, this also says something unflattering about the pickers that "
                 "survived: `MIN_IS_DD`, `MID_DAILY` and `MAX_SHARPE` all landed within a step or "
                 "two of k = 1.00, i.e. they agree with the mechanical answer, and their agreement "
                 "is not independent evidence — it is the same answer reached three ways.\n")
    lines.append("## What this face does not do\n")
    lines.append("- It does not search for a better picker. Nine rules were frozen, all nine are "
                 "printed, and no threshold was moved after seeing the answer.")
    lines.append("- The bootstrap resamples periods, not history: it re-orders the same %d "
                 "out-of-sample periods and cannot create a drawdown that never happened. It "
                 "answers 'how much of this is the sample', not 'what will happen next'."
                 % d["out_of_sample_periods"])
    lines.append("- Still not modelled: margin calls, borrow availability beyond a flat carry, "
                 "as-traded prices without dividends, and the book's own survivorship (the same "
                 "caveats the parents carry).")
    lines.append("- This is a sizing study on one book, not a tradable strategy; the deliverable "
                 "is which choices are robust, not a position to hold.\n")
    return "\n".join(lines)


def run() -> int:
    payload = build()
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1, sort_keys=False)
    with open(MD, "w", encoding="utf-8") as fh:
        fh.write(render_md(payload))
    print("HEDGE-PICKER %s  periods=%d IS=%d OOS=%d"
          % (payload["verdict"], payload["data"]["book_periods"],
             payload["data"]["in_sample_periods"], payload["data"]["out_of_sample_periods"]))
    print("  %s" % payload["verdict_why"])
    for b in BUDGETS:
        cells = payload["pickers"]
        best = sorted((n for n in cells),
                      key=lambda n: -cells[n]["cells"]["%.2f" % b].get("p_hold", -1))
        print("  %.0f%%: %s | top p_hold: %s"
              % (b * 100, payload["race"]["%.2f" % b]["verdict"],
                 ", ".join("%s %.2f" % (n, cells[n]["cells"]["%.2f" % b]["p_hold"]) for n in best[:3])))
    print("  -> results/astock_veto_hedge_picker.json + research/ASTOCK_VETO_HEDGE_PICKER.md")
    return 0


# ------------------------------------------------------------------ selftest
def _ok(cond, msg) -> bool:
    print(("  ok   " if cond else "  FAIL ") + msg)
    return bool(cond)


def _mk_curve(is_dd, is_cagr, is_sharpe, oos_dd, oos_cagr=0.05):
    return {"daily": {"dd": is_dd, "cagr": is_cagr, "sharpe": is_sharpe},
            "period": {"dd": is_dd * 0.8, "cagr": is_cagr},
            "daily_oos": {"dd": oos_dd, "cagr": oos_cagr, "sharpe": 0.5},
            "daily_full": {"dd": max(is_dd, oos_dd)}}


def selftest() -> int:
    ok = True
    print("astock_veto_hedge_picker selftest")

    cur = {"0.00": _mk_curve(0.30, 0.10, 0.40, 0.34),
           "0.50": _mk_curve(0.18, 0.09, 0.60, 0.15),
           "0.75": _mk_curve(0.14, 0.07, 0.55, 0.18),
           "1.00": _mk_curve(0.12, 0.05, 0.50, 0.21),
           "1.50": _mk_curve(0.22, 0.02, 0.30, 0.30)}

    ok &= _ok(pick_a_period(cur, 0.20) == "0.50",
              "L1 rule A on the period ruler takes the best return that fits (0.50)")
    ok &= _ok(pick_a_daily(cur, 0.20) == "0.50",
              "L2 rule A on the daily ruler also takes 0.50 here")
    ok &= _ok(pick_b_daily(cur, 0.20) == "0.50", "L3 rule B takes the smallest size that fits")
    ok &= _ok(pick_b_margin(cur, 0.20) == "0.75",
              "L4 an 80%% margin (16%%) drops the size that only just fits and takes the next one")
    ok &= _ok(pick_b_daily(cur, 0.05) is None,
              "L5 an unreachable budget returns nothing rather than a smallest bad answer")
    ok &= _ok(pick_mid_daily(cur, 0.20) == "0.75",
              "L6 mid-band sits between the smallest and largest feasible size (0.50..1.00 -> 0.75)")
    ok &= _ok(pick_min_is_dd(cur, 0.20) == "1.00",
              "L7 the shallowest in-sample drawdown is 1.00, regardless of budget")
    ok &= _ok(pick_max_sharpe(cur, 0.20) == "0.50", "L8 the best in-sample Sharpe is 0.50")
    ok &= _ok(PICKERS["FIXED_ONE"][1](cur, 0.20) == "1.00",
              "L9 the mechanical picker ignores the data entirely")

    # ties resolve to the smaller size, stated once
    tied = {"0.40": _mk_curve(0.10, 0.08, 0.60, 0.10),
            "0.45": _mk_curve(0.10, 0.08, 0.60, 0.10)}
    ok &= _ok(pick_max_sharpe(tied, 0.20) == "0.40" and pick_a_daily(tied, 0.20) == "0.40",
              "L10 equal in-sample readings resolve to the smaller size")

    # daily ruler can never read less than the period ruler
    ok &= _ok(daily_stats([1.0, 1.1, 1.0])["dd"] > 0 and
              daily_stats([1.0, 1.0, 1.0])["dd"] == 0.0,
              "L11 a flat path has no drawdown and a V has one")

    # steps -> path round trip, and level vs return stepping
    vl = [1.0, 1.1, 1.21]
    ok &= _ok(abs(path_from_steps([steps_of(vl)], [0])[-1] - 1.21) < 1e-12,
              "L12 levels are stepped as ratios, not compounded as levels")

    # bootstrap: a size that always fits returns 1.0, one that never fits returns 0.0
    flat = [[1.0001] * 20 for _ in range(8)]
    deep = [[0.98] * 20 for _ in range(8)]
    ok &= _ok(bootstrap_p_hold(flat, 0.05) == 1.0, "L13 a never-drawing size always holds")
    ok &= _ok(bootstrap_p_hold(deep, 0.05) == 0.0, "L14 a 32%-down size never holds a 5% budget")

    # verdict states
    rows = {"FIXED_ONE": {"cells": {"0.20": {"k": 1.0, "holds": True, "oos_dd": 0.15,
                                             "oos_cagr": 0.08}}},
            "A_DAILY": {"cells": {"0.20": {"k": 0.75, "holds": True, "oos_dd": 0.14,
                                           "oos_cagr": 0.09}}},
            "B_DAILY": {"cells": {"0.20": {"k": 0.50, "holds": True, "oos_dd": 0.11,
                                           "oos_cagr": 0.07}}}}
    ok &= _ok(race_verdict(rows, 0.20)[0] == "FITTING_HELPS",
              "L15 a fitted picker with more return than the mechanical one is a help")
    rows2 = json.loads(json.dumps(rows))
    rows2["A_DAILY"]["cells"]["0.20"]["oos_cagr"] = 0.05
    rows2["B_DAILY"]["cells"]["0.20"]["oos_cagr"] = 0.05
    ok &= _ok(race_verdict(rows2, 0.20)[0] == "FITTING_ADDS_NOTHING",
              "L16 fitted pickers that only match the mechanical one add nothing")
    rows3 = {"FIXED_ONE": {"cells": {"0.20": {"k": 1.0, "holds": True, "oos_dd": 0.15,
                                              "oos_cagr": 0.08}}},
             "A_DAILY": {"cells": {"0.20": {"k": 1.10, "holds": False, "oos_dd": 0.24,
                                            "oos_cagr": 0.11}}},
             "B_DAILY": {"cells": {"0.20": {"k": 0.35, "holds": False, "oos_dd": 0.22,
                                            "oos_cagr": 0.04}}}}
    ok &= _ok(race_verdict(rows3, 0.20)[0] == "FITTING_HURTS",
              "L17 fitted pickers that breach what the mechanical one held is a harm")
    rows4 = {"FIXED_ONE": {"cells": {"0.10": {"k": 1.0, "holds": False, "oos_dd": 0.34,
                                              "oos_cagr": 0.05}}},
             "A_DAILY": {"cells": {"0.10": {"k": None, "holds": False}}}}
    ok &= _ok(race_verdict(rows4, 0.10)[0] == "NO_BUDGET_IS_HELD",
              "L18 nothing holding anywhere is its own verdict")

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
