#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""zoo93_disposition_cgo_judge -- the takeable half of the CGO decile spread.

WHY THIS FILE EXISTS
--------------------
r1393 priced zoo #93 (Grinblatt-Han capital-gains overhang) as a supply berth and returned
ADMIT_TO_PREREG on a decile *spread*: low-CGO decile +0.2717 % per 20 bars, high-CGO decile
-0.5130 %, i.e. 65 % of the gross spread sits on the leg an A-share desk cannot hold, because a
single stock cannot be shorted here.  The probe said so itself ("a decile spread is a claim
about a portfolio nobody has to be able to hold") and stopped, because a supply berth buys a
frozen prereg, not a profit claim.

This script is that prereg's judge (research/CASE_PREREG_ZOO93_TAKEABLE.md, frozen before the
first run).  It asks the only question that can become money: is the *long-only* part of the
spread worth doing, after the cost of actually turning the book over?

  A1_decile   bottom 10 % of CGO, equal weight, 20-bar cohorts, next-open entry
  A2_n50      the 50 lowest-CGO names (a size a desk can hold)
  B_pool      every liquid candidate (the control: the pool itself)
  C_510300    buy and hold the index ETF over the same span
  B_high/B_low  aggregate overhang as an index-timing gate, both signs frozen up front

Construct, panel and cost constant are the probe's, imported -- never re-implemented.

Run:  python scripts/zoo93_disposition_cgo_judge.py run | selftest
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import zoo93_disposition_cgo_probe as P  # noqa: E402  (probe = construct of record)
from etf_composite_pf import MIN_AMT  # noqa: E402  (20e6: the number the book uses)

OUT = os.path.join(ROOT, "results", "supply_berth", "zoo93_disposition_cgo_judge.json")
ETF_510300 = os.path.join(ROOT, "data", "daily", "sh510300.csv")

CONFIG = {
    "rebal": 20,
    "decile": 0.10,
    "n50": 50,
    "cost_per_side": P.COST_PER_SIDE,
    "cost_multipliers": (1.0, 3.0),
    "phases": (0, 5, 10, 15),
    "min_pool": P.MIN_POOL,
    "liq_window": 20,
    "liq_min_amt": MIN_AMT,
    "agg_window": 252,
    "agg_tail": 0.10,
    "gate_pp": 1.00,          # pp/yr the arm must add, frozen
    "null_draws": 200,
}
BARS_PER_YEAR = 252.0


# --------------------------------------------------------------------------- helpers

def rolling_median(a: np.ndarray, window: int) -> np.ndarray:
    """Trailing median over `window` rows; rows < window-1 are NaN (a partial window is not the
    frozen construct).  Loop of small slices: the strided view would cost >1 GB here."""
    T, S = a.shape
    out = np.full((T, S), np.nan)
    for t in range(window - 1, T):
        blk = a[t - window + 1: t + 1, :]
        out[t, :] = np.nanmedian(blk, axis=0) if np.isfinite(blk).any() else np.nan
    return out


def equity_stats(net: np.ndarray, bars_per_step: int) -> dict:
    """CAGR / vol / Sharpe / maxdd on a sequence of per-cohort net returns."""
    if net.size == 0:
        return {"n": 0}
    eq = np.cumprod(1.0 + net)
    total_bars = net.size * bars_per_step
    years = total_bars / BARS_PER_YEAR
    cagr = float(eq[-1] ** (1.0 / years) - 1.0) if years > 0 and eq[-1] > 0 else float("nan")
    sd = float(np.std(net, ddof=1)) if net.size > 1 else float("nan")
    sharpe = float(np.mean(net) / sd * np.sqrt(BARS_PER_YEAR / bars_per_step)) if sd and sd > 0 else float("nan")
    peak = np.maximum.accumulate(np.concatenate([[1.0], eq]))
    mdd = float(np.min(np.concatenate([[1.0], eq]) / peak - 1.0))
    return {
        "n_cohorts": int(net.size),
        "bars": int(total_bars),
        "cagr": cagr,
        "vol_ann": float(sd * np.sqrt(BARS_PER_YEAR / bars_per_step)) if np.isfinite(sd) else None,
        "sharpe": sharpe,
        "maxdd": mdd,
        "best": float(np.max(net)),
        "worst": float(np.min(net)),
        "share_positive": float(np.mean(net > 0)),
    }


def per_year(net: np.ndarray, entry_years: list) -> dict:
    out: dict = {}
    for y in sorted(set(entry_years)):
        idx = [i for i, yy in enumerate(entry_years) if yy == y]
        if not idx:
            continue
        out[str(y)] = {
            "n": len(idx),
            "sum_net": float(np.sum(net[idx])),
            "share_positive": float(np.mean(net[idx] > 0)),
        }
    return out


def _weights(sel: np.ndarray, S: int) -> np.ndarray:
    w = np.zeros(S)
    if sel.size:
        w[sel] = 1.0 / sel.size
    return w


def _turnover_cost(w_new: np.ndarray, w_old: np.ndarray, cost: float) -> float:
    return float(np.sum(np.abs(w_new - w_old)) * cost)


# --------------------------------------------------------------------------- arms

def run_book(cgo, fwd, liq_ok, dates, grid: int, kind: str, cost_mult: float) -> dict:
    """One long-only arm on one decision grid.  `kind` in {decile, n50, pool}."""
    T, S = cgo.shape
    h = CONFIG["rebal"]
    cost = CONFIG["cost_per_side"] * cost_mult
    start = 0
    for t in range(T):
        if np.isfinite(cgo[t]).any():
            start = t + P.WINDOW - 1
            break
    rebs = [t for t in range(start + grid, T - h - 1, h)]
    w_old = np.zeros(S)
    nets, years, names, unused, traded = [], [], [], [], []
    for t in rebs:
        ok = np.isfinite(cgo[t]) & np.isfinite(fwd[t]) & liq_ok[t]
        idx = np.flatnonzero(ok)
        if idx.size < CONFIG["min_pool"]:
            unused.append(dates[t])
            continue
        vals = cgo[t, idx]
        if kind == "pool":
            sel = idx
        elif kind == "n50":
            sel = idx[np.argsort(vals, kind="stable")[: CONFIG["n50"]]]
        else:
            k = max(1, int(round(idx.size * CONFIG["decile"])))
            sel = idx[np.argsort(vals, kind="stable")[:k]]
        w_new = _weights(sel, S)
        c = _turnover_cost(w_new, w_old, cost)
        gross = float(np.mean(fwd[t, sel]))
        nets.append(gross - c)
        years.append(int(dates[t][:4]))
        names.append(int(sel.size))
        traded.append(dates[t])
        w_old = w_new
    net = np.array(nets, dtype=float)
    if net.size:
        net[-1] -= float(np.sum(w_old)) * cost          # no free exit
    stats = equity_stats(net, h)
    stats["first_date"] = traded[0] if traded else None
    stats["last_date"] = traded[-1] if traded else None
    stats["mean_names"] = float(np.mean(names)) if names else 0.0
    stats["dates_skipped"] = len(unused)
    stats["cost_mult"] = cost_mult
    stats["per_year"] = per_year(net, years)
    stats["_net"] = net
    stats["_years"] = years
    return stats


def load_bench() -> dict:
    """510300 from the repo's own daily panel (no second data source)."""
    d, o, c = [], [], []
    with open(ETF_510300, "r", encoding="utf-8") as fh:
        head = fh.readline()
        for line in fh:
            p = line.strip().split(",")
            if len(p) < 5:
                continue
            d.append(p[0])
            o.append(float(p[1]))
            c.append(float(p[4]))
    return {"date": np.array(d), "open": np.array(o), "close": np.array(c)}


def bench_window(bench: dict, first: str, last: str, cost_mult: float) -> dict:
    m = (bench["date"] >= first) & (bench["date"] <= last)
    o = bench["open"][m]
    c = bench["close"][m]
    if o.size < 3:
        return {"n": 0}
    r = c / o[0]
    cost = CONFIG["cost_per_side"] * cost_mult
    r[-1] *= (1.0 - cost)                               # exit charged, entry charged below
    eq = r * (1.0 - cost)
    years = (o.size) / BARS_PER_YEAR
    cagr = float(eq[-1] ** (1.0 / years) - 1.0)
    daily = np.diff(np.log(np.concatenate([[1.0], eq])))
    sd = float(np.std(daily, ddof=1))
    peak = np.maximum.accumulate(eq)
    return {
        "n_bars": int(o.size),
        "first": str(bench["date"][m][0]),
        "last": str(bench["date"][m][-1]),
        "cagr": cagr,
        "vol_ann": sd * np.sqrt(BARS_PER_YEAR),
        "sharpe": float(np.mean(daily) / sd * np.sqrt(BARS_PER_YEAR)) if sd > 0 else float("nan"),
        "maxdd": float(np.min(eq / peak - 1.0)),
    }


def run_gate(cgo, fwd_index, liq_ok, dates, grid: int, sign: str, cost_mult: float) -> dict:
    """Aggregate-overhang index gate.  `fwd_index[t]` = 510300 open[t+1] -> close[t+20]."""
    T = cgo.shape[0]
    h = CONFIG["rebal"]
    cost = CONFIG["cost_per_side"] * cost_mult
    w = CONFIG["agg_window"]
    agg = np.full(T, np.nan)
    for t in range(T):
        ok = np.isfinite(cgo[t]) & liq_ok[t]
        if ok.sum() >= CONFIG["min_pool"]:
            agg[t] = float(np.median(cgo[t, ok]))
    state = np.zeros(T, dtype=bool)                     # True = long the index
    for t in range(T):
        lo = max(0, t - w + 1)
        win = agg[lo: t + 1]
        win = win[np.isfinite(win)]
        if win.size < w // 2 or not np.isfinite(agg[t]):
            continue
        q = np.mean(win <= agg[t])
        if sign == "high":
            state[t] = q >= 1.0 - CONFIG["agg_tail"]
        else:
            state[t] = q <= CONFIG["agg_tail"]
    rebs = [t for t in range(grid, T - h - 1, h)]
    nets, years, prev, long_share = [], [], 0.0, []
    for t in rebs:
        if not np.isfinite(fwd_index[t]):
            continue
        want = 1.0 if state[t] else 0.0
        c = abs(want - prev) * cost
        nets.append(want * fwd_index[t] - c)
        years.append(int(dates[t][:4]))
        long_share.append(want)
        prev = want
    net = np.array(nets, dtype=float)
    if net.size:
        net[-1] -= prev * cost
    stats = equity_stats(net, h)
    stats["long_share"] = float(np.mean(long_share)) if long_share else 0.0
    stats["switches_per_year"] = float(
        np.sum(np.abs(np.diff(np.concatenate([[0.0], np.array(long_share)])))) / max(1e-9, net.size * h / BARS_PER_YEAR)
    ) if long_share else 0.0
    stats["cost_mult"] = cost_mult
    stats["per_year"] = per_year(net, years)
    stats["_net"] = net
    stats["_wants"] = np.array(long_share, dtype=float)
    stats["_returns"] = np.array([fwd_index[t] for t in rebs if np.isfinite(fwd_index[t])], dtype=float)
    stats["_cost"] = cost
    return stats


def circular_null(wants: np.ndarray, returns: np.ndarray, cost: float, draws: int, seed: int = 0) -> dict:
    """Rotate the rule's STATE against the realised returns -- never the realised net series
    against itself: a rotation is a permutation, so rolling the net series leaves its mean
    exactly invariant and any rule would score p = 1.000 (the identity trap)."""
    if wants.size < 4:
        return {"draws": 0}
    rng = np.random.default_rng(seed)

    def mean_net(w: np.ndarray) -> float:
        prev = np.concatenate([[0.0], w[:-1]])
        net = w * returns - np.abs(w - prev) * cost
        net[-1] -= w[-1] * cost                       # no free exit
        return float(np.mean(net))

    actual = mean_net(wants)
    n = wants.size
    sims = np.array([mean_net(np.roll(wants, int(rng.integers(1, n)))) for _ in range(draws)])
    return {
        "draws": int(draws),
        "actual_mean": actual,
        "mean_null": float(np.mean(sims)),
        "sd_null": float(np.std(sims, ddof=1)) if sims.size > 1 else None,
        "p_value": float((np.sum(sims >= actual) + 1) / (sims.size + 1)),
    }


# --------------------------------------------------------------------------- judgment

def judge(panel: dict, bench: dict, draws: int | None = None) -> dict:
    h = CONFIG["rebal"]
    cgo = P.cgo_matrix(panel["close"], panel["turn"], P.WINDOW)
    liq = rolling_median(panel["amount"], CONFIG["liq_window"])
    liq_ok = np.isfinite(liq) & (liq >= CONFIG["liq_min_amt"])
    fwd = P.forward_matrix(panel["open"], panel["close"], h)
    dates = panel["dates"]
    T = len(dates)

    # index forward leg on the panel's own date axis (no second calendar)
    bidx = {d: i for i, d in enumerate(bench["date"])}
    fwd_index = np.full(T, np.nan)
    for t in range(T - h - 1):
        i0 = bidx.get(dates[t + 1])
        i1 = bidx.get(dates[t + h])
        if i0 is None or i1 is None:
            continue
        o = bench["open"][i0]
        if o > 0:
            fwd_index[t] = bench["close"][i1] / o - 1.0

    arms: dict = {}
    raw: dict = {}
    for grid in CONFIG["phases"]:
        g = {}
        for kind in ("decile", "n50", "pool"):
            for cm in CONFIG["cost_multipliers"]:
                st = run_book(cgo, fwd, liq_ok, dates, grid, kind, cm)
                g[f"{kind}_x{int(cm)}"] = {k: v for k, v in st.items() if not k.startswith("_")}
                if cm == 1.0:
                    raw[f"grid{grid}_{kind}"] = st
        for sign in ("high", "low"):
            for cm in CONFIG["cost_multipliers"]:
                st = run_gate(cgo, fwd_index, liq_ok, dates, grid, sign, cm)
                g[f"gate_{sign}_x{int(cm)}"] = {k: v for k, v in st.items() if not k.startswith("_")}
                if cm == 1.0:
                    raw[f"grid{grid}_gate_{sign}"] = st
        arms[f"grid{grid}"] = g

    # benchmark over the span the primary grid actually traded (its own cohort dates)
    p0 = raw[f"grid{CONFIG['phases'][0]}_pool"]
    span_first = p0.get("first_date") or dates[0]
    span_last = p0.get("last_date") or dates[-1]
    if span_last in dates:                       # the last cohort holds h bars beyond its entry
        span_last = dates[min(len(dates) - 1, dates.index(span_last) + h)]
    bench_by_mult = {cm: bench_window(bench, span_first, span_last, cm) for cm in CONFIG["cost_multipliers"]}

    crit = evaluate(arms, raw, bench_by_mult)
    return {
        "artifact": "zoo93_disposition_cgo takeable judge",
        "family": "zoo93_disposition_cgo",
        "batch": "SUPPLY_BERTH_BEHAVIOURAL_FAMILY_JUDGE",
        "machine": "bm-c",
        "evidence_cutoff": panel["dates"][-1],
        "prereg": "research/CASE_PREREG_ZOO93_TAKEABLE.md",
        "config": {k: v for k, v in CONFIG.items() if k != "null_draws"},
        "panel": {
            "symbols": int(panel["close"].shape[1]),
            "bars": int(panel["close"].shape[0]),
            "first_date": panel["dates"][0],
            "last_date": panel["dates"][-1],
            "liquidity_gate": {"window": CONFIG["liq_window"], "min_median_amount_cny": CONFIG["liq_min_amt"]},
        },
        "benchmark": {"510300": bench_by_mult, "span": [span_first, span_last]},
        "arms": arms,
        "criteria": crit,
        "verdict_block": verdict(crit),
        "honest": [
            "the decile spread's short leg is not takeable in A-shares; this judge measures only what a long-only desk could hold",
            "the cost constant is the ETF book's 13.041 bp/side; A-share stock round trips are typically 25 bp+, hence the x3 ladder",
            "qfq prices near corporate actions distort price-versus-cost-basis for every holder at once",
            "a 10 % decile of ~4,800 names is not a portfolio; A2_n50 is the size a desk can hold and carries its own concentration risk",
            "the panel holds today's listed names (survivorship) and starts 2020-01, so nothing before 2020-04 is read",
        ],
    }


def _delta(arm: dict, ctrl: dict) -> float | None:
    a, b = arm.get("cagr"), ctrl.get("cagr")
    if a is None or b is None or not np.isfinite(a) or not np.isfinite(b):
        return None
    return float(a - b)


def evaluate(arms: dict, raw: dict, bench_by_mult: dict) -> dict:
    out: dict = {"long_only": {}, "gate": {}}
    for name in ("decile", "n50"):
        per_grid = {}
        for grid in CONFIG["phases"]:
            g = arms[f"grid{grid}"]
            d1 = _delta(g[f"{name}_x1"], g["pool_x1"])
            d3 = _delta(g[f"{name}_x3"], g["pool_x3"])
            per_grid[str(grid)] = {"excess_pp_x1": d1, "excess_pp_x3": d3}
        vals1 = [v["excess_pp_x1"] for v in per_grid.values() if v["excess_pp_x1"] is not None]
        vals3 = [v["excess_pp_x3"] for v in per_grid.values() if v["excess_pp_x3"] is not None]
        primary = per_grid[str(CONFIG["phases"][0])]
        out["long_only"][name] = {
            "per_grid": per_grid,
            "min_excess_x1": min(vals1) if vals1 else None,
            "median_excess_x1": float(np.median(vals1)) if vals1 else None,
            "grids_positive_x1": int(sum(1 for v in vals1 if v > 0)),
            "grids_positive_x3": int(sum(1 for v in vals3 if v > 0)),
            "passes": bool(
                primary["excess_pp_x1"] is not None
                and primary["excess_pp_x1"] / 100.0 >= CONFIG["gate_pp"] / 100.0
                and primary["excess_pp_x3"] is not None
                and primary["excess_pp_x3"] > 0
                and sum(1 for v in vals1 if v > 0) >= 3
            ),
        }
    for sign in ("high", "low"):
        bench = bench_by_mult[1.0]
        per_grid = {}
        for grid in CONFIG["phases"]:
            g = arms[f"grid{grid}"]
            per_grid[str(grid)] = {
                "excess_pp_x1": _delta(g[f"gate_{sign}_x1"], bench),
                "excess_pp_x3": _delta(g[f"gate_{sign}_x3"], bench_by_mult[3.0]),
            }
        primary_grid = CONFIG["phases"][0]
        g0 = raw[f"grid{primary_grid}_gate_{sign}"]
        null = circular_null(g0["_wants"], g0["_returns"], g0["_cost"], CONFIG["null_draws"])
        vals1 = [v["excess_pp_x1"] for v in per_grid.values() if v["excess_pp_x1"] is not None]
        vals3 = [v["excess_pp_x3"] for v in per_grid.values() if v["excess_pp_x3"] is not None]
        p = null.get("p_value")
        out["gate"][sign] = {
            "per_grid": per_grid,
            "null": null,
            "grids_positive_x1": int(sum(1 for v in vals1 if v > 0)),
            "grids_positive_x3": int(sum(1 for v in vals3 if v > 0)),
            "passes": bool(
                per_grid[str(primary_grid)]["excess_pp_x1"] is not None
                and per_grid[str(primary_grid)]["excess_pp_x1"] / 100.0 >= CONFIG["gate_pp"] / 100.0
                and (per_grid[str(primary_grid)]["excess_pp_x3"] or -1) > 0
                and p is not None and p < 0.05
                and sum(1 for v in vals1 if v > 0) >= 3
            ),
        }
    return out


def verdict(crit: dict) -> dict:
    ok_long = [n for n, v in crit["long_only"].items() if v["passes"]]
    ok_gate = [n for n, v in crit["gate"].items() if v["passes"]]
    reasons = []
    for n, v in crit["long_only"].items():
        if v["passes"]:
            continue
        if v["median_excess_x1"] is None:
            reasons.append(f"{n}: no readable excess")
            continue
        reasons.append(
            f"{n}: median excess {v['median_excess_x1']*100:+.2f}pp/yr over the pool "
            f"(positive on {v['grids_positive_x1']}/4 grids, x3-positive on {v['grids_positive_x3']}/4)"
        )
    for n, v in crit["gate"].items():
        if v["passes"]:
            continue
        p = (v["null"] or {}).get("p_value")
        reasons.append(
            f"gate_{n}: primary-grid excess "
            f"{(v['per_grid'][str(CONFIG['phases'][0])]['excess_pp_x1'] or float('nan'))*100:+.2f}pp/yr, "
            f"null p={p if p is not None else float('nan'):.3f}"
        )
    if ok_long or ok_gate:
        return {
            "verdict": "ADMIT_TO_CANDIDATE",
            "admitted": {"long_only": ok_long, "gate": ok_gate},
            "reason": "at least one takeable arm clears the frozen bar (>= +1.00 pp/yr at x1, >0 at x3, 3/4 grids)",
            "refused": reasons,
        }
    return {
        "verdict": "REFUSE_AS_CANDIDATE",
        "admitted": {"long_only": [], "gate": []},
        "reason": "no takeable arm clears the frozen bar; the spread's money is on the leg A-shares cannot hold",
        "refused": reasons,
    }


# --------------------------------------------------------------------------- selftest

def _synth(nT=400, nS=120, seed=7):
    rng = np.random.default_rng(seed)
    dates = [f"2021-{1 + i // 21:02d}-{1 + i % 21:02d}" for i in range(nT)]
    dates = sorted(set(dates))
    nT = len(dates)
    ret = rng.normal(0.0, 0.02, size=(nT, nS))
    close = 10.0 * np.cumprod(1.0 + ret, axis=0)
    open_ = np.vstack([close[0], close[:-1] * (1.0 + rng.normal(0, 0.002, size=(nT - 1, nS)))])
    turn = rng.uniform(0.005, 0.03, size=(nT, nS))
    amount = np.full((nT, nS), 5e7)
    return {"dates": dates, "symbols": [f"s{j}" for j in range(nS)], "open": open_,
            "close": close, "turn": turn, "volume": np.full((nT, nS), 1e7),
            "amount": amount}


def _synth_signal(nT=400, nS=120, seed=11):
    """Panel where the mechanism the judge exists to see is actually present: prices follow a
    mean-reverting level (OU), so a name whose turnover-weighted cost basis sits far below its
    price (high CGO) is a name that has run up and drifts back down.  Constant per-name drift
    cannot express this -- it makes CGO and forward return the same variable."""
    p = _synth(nT, nS, seed)
    rng = np.random.default_rng(seed)
    phi = 0.97
    x = np.zeros((nT, nS))
    eps = rng.normal(0.0, 0.02, size=(nT, nS))
    for t in range(1, nT):
        x[t] = phi * x[t - 1] + eps[t]
    close = 10.0 * np.exp(x)
    p["close"] = close
    p["open"] = np.vstack([close[0], close[:-1]])
    return p


def selftest() -> int:
    ok = True

    def chk(name, cond, extra=""):
        nonlocal ok
        print(f"[{'PASS' if cond else 'FAIL'}] {name}" + (f" | {extra}" if extra else ""))
        ok = ok and bool(cond)

    rng = np.random.default_rng(3)
    rm = rolling_median(rng.normal(size=(40, 5)), 20)
    chk("rolling_median leaves a partial window NaN", np.isnan(rm[:19]).all())
    series = np.arange(1.0, 41.0)[:, None] * np.ones((1, 2))
    chk("rolling_median is the trailing median",
        abs(rolling_median(series, 20)[39, 0] - np.median(np.arange(21.0, 41.0))) < 1e-12)

    a = np.array([0.01, -0.02, 0.03, 0.0])
    st = equity_stats(a, 20)
    chk("equity_stats reproduces a hand CAGR",
        abs(st["cagr"] - (np.prod(1 + a) ** (252 / 80) - 1)) < 1e-12)
    chk("equity_stats maxdd is not zero on a losing series", st["maxdd"] < 0)

    w = _weights(np.array([3, 4]), 5)
    chk("equal weights sum to one", abs(w.sum() - 1.0) < 1e-12)
    chk("full replacement is charged two sides",
        abs(_turnover_cost(np.array([0, 0, 1.0]), np.array([1.0, 0, 0]), 0.001) - 0.002) < 1e-12)

    # a panel with no signal must not manufacture excess
    flat = _synth()
    cgo = P.cgo_matrix(flat["close"], flat["turn"], P.WINDOW)
    fwd = P.forward_matrix(flat["open"], flat["close"], CONFIG["rebal"])
    liq_ok = np.isfinite(flat["amount"])
    d1 = run_book(cgo, fwd, liq_ok, flat["dates"], 0, "decile", 1.0)["cagr"]
    pl = run_book(cgo, fwd, liq_ok, flat["dates"], 0, "pool", 1.0)["cagr"]
    chk("no-signal panel: decile does not beat the pool by the frozen bar",
        (d1 - pl) < CONFIG["gate_pp"] / 100.0, f"delta={d1-pl:+.4f}")

    # deterministic: two runs identical
    r1 = run_book(cgo, fwd, liq_ok, flat["dates"], 0, "n50", 1.0)["cagr"]
    r2 = run_book(cgo, fwd, liq_ok, flat["dates"], 0, "n50", 1.0)["cagr"]
    chk("the arm is deterministic", r1 == r2)

    # the n50 book holds exactly the requested size when the pool is big enough
    st = run_book(cgo, fwd, liq_ok, flat["dates"], 0, "n50", 1.0)
    chk("n50 holds 50 names", abs(st["mean_names"] - 50) < 1e-9, f"names={st['mean_names']}")

    # an injected edge must be found (a judge that cannot see a planted signal judges nothing)
    sig = _synth_signal()
    cgo_s = P.cgo_matrix(sig["close"], sig["turn"], P.WINDOW)
    fwd_s = P.forward_matrix(sig["open"], sig["close"], CONFIG["rebal"])
    e_dec = run_book(cgo_s, fwd_s, liq_ok, sig["dates"], 0, "decile", 1.0)["cagr"]
    e_pool = run_book(cgo_s, fwd_s, liq_ok, sig["dates"], 0, "pool", 1.0)["cagr"]
    chk("planted edge: decile beats the pool", e_dec > e_pool, f"{e_dec:+.4f} vs {e_pool:+.4f}")

    # null: rotating a realised NET series cannot move its mean (a permutation is not a test),
    # while rotating the STATE against the returns can -- and a state that is anti-correlated
    # with the returns must be rejected against its own rotations.
    nul = circular_null(np.array([1.0, 0.0] * 20), np.array([0.01, 0.01] * 20), 0.0, 50)
    chk("state-vs-return null rejects a rule whose long bars earn nothing",
        nul["p_value"] > 0.5, f"p={nul['p_value']:.3f}")
    good = np.zeros(40)
    rets = np.concatenate([np.full(20, 0.01), np.full(20, -0.005)])
    good[:20] = 1.0
    nul2 = circular_null(good, rets, 0.0, 99)
    chk("state-vs-return null accepts a state aligned with the up bars",
        nul2["p_value"] < 0.1, f"p={nul2['p_value']:.3f}")

    # verdict vocabulary is closed
    v = verdict({"long_only": {"decile": {"passes": False, "median_excess_x1": 0.001, "grids_positive_x1": 2, "grids_positive_x3": 1}},
                 "gate": {}})
    chk("a failing arm reads REFUSE_AS_CANDIDATE", v["verdict"] == "REFUSE_AS_CANDIDATE")
    v2 = verdict({"long_only": {"decile": {"passes": True, "median_excess_x1": 0.02, "grids_positive_x1": 4, "grids_positive_x3": 4}},
                  "gate": {}})
    chk("a passing arm reads ADMIT_TO_CANDIDATE", v2["verdict"] == "ADMIT_TO_CANDIDATE")

    print(f"selftest {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


def _jsonable(o):
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    raise TypeError(f"Object of type {type(o).__name__} is not JSON serializable")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", nargs="?", default="run", choices=["run", "selftest"])
    args = ap.parse_args()
    if args.mode == "selftest":
        return selftest()
    t0 = time.time()
    panel = P.load_panel()
    bench = load_bench()
    res = judge(panel, bench)
    res["elapsed_sec"] = round(time.time() - t0, 1)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(res, fh, ensure_ascii=False, indent=1, default=_jsonable)
    vb = res["verdict_block"]
    print(json.dumps({"verdict": vb["verdict"], "admitted": vb["admitted"],
                      "refused": vb["refused"]}, ensure_ascii=False, indent=1))
    print(f"elapsed {res['elapsed_sec']}s -> {os.path.relpath(OUT, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())