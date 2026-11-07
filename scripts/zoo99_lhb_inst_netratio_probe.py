#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""zoo99_lhb_inst_netratio_probe -- does the institutional seat aggregate, now that it exists,
separate forward returns?

WHY THIS FILE EXISTS
--------------------
r1405 priced zoo #94 (LHB institutional timing) against `Money02/data/lhb/lhb_detail.parquet`,
found no seat column, and labelled the run `verdict_scope='frozen rule untested'` -- the frozen
numerator (institutional net buy) was not computable anywhere in the repo.  r1413 collected it
(`scripts/update_lhb_inst.py`: 58,636 rows, 5,154 codes, 2020-01-01..2026-11-06).  This script is
the pricing run that berth was waiting for.

FROZEN RULE (written before the first run; not edited after seeing readings)
---------------------------------------------------------------------------
score(stock, day)  = sum(机构买入净额) / sum(市场总成交额) over every LHB row for that
                     (stock, day).  Multi-day cumulative reasons are summed as the vendor
                     reports them -- both numerator and denominator are cumulative for those
                     rows, so the ratio stays a ratio; their share is disclosed, not hidden.
signal(t)          = mean of score over the trailing 20 bars (>= 1 observation).
eligibility(t)     = liquidity 20-bar median amount >= 2.0e7 CNY, forward leg finite,
                     >= MIN_NAMES names carrying a signal, AND the panel's own liq gate.
arm A (frozen)     = top decile by signal, equal weight, 20-bar cohorts, next-open entry.
arms B/C           = n50 by signal, and the pool of every eligible name (the control).
arm D              = bottom decile by signal (the sign check, not a candidate).
cost               = 13.041 bp/side x {1, 3}; phases {0, 5, 10, 15} trades per cohort.
null               = 200 draws picking k names UNIFORMLY from the eligible set of the same
                     decision date, i.e. "does the score beat an equal number of random names
                     from the same pool", which is the right null when coverage is partial.

DECISION (frozen): ADMIT_TO_PREREG iff
  C1  arm A net CAGR > pool control net CAGR at x1 cost
  C2  arm A net CAGR > pool control net CAGR at x3 cost
  C3  null p <= 0.05
  C4  arm A excess over the pool is positive in all four phases
Anything else = REFUSE_AS_CANDIDATE, naming the failing conditions.  ADMIT buys a frozen
prereg, not a profit claim.

Construct, cost constant and null machinery are imported from the zoo93 files of record --
never re-implemented.

Run:  python scripts/zoo99_lhb_inst_netratio_probe.py run | selftest
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

import zoo93_disposition_cgo_probe as P  # noqa: E402  (price panel of record)
import zoo93_disposition_cgo_judge as J  # noqa: E402  (stats / bench / null of record)
from etf_composite_pf import MIN_AMT  # noqa: E402

LHB_INST = os.path.join(ROOT, "data", "lhb_inst", "lhb_inst.parquet")
OUT = os.path.join(ROOT, "results", "supply_berth", "zoo99_lhb_inst_netratio_probe.json")

CONFIG = {
    "rebal": 20,
    "decile": 0.10,
    "n50": 50,
    "min_names": 20,
    "sig_window": 20,
    "cost_per_side": P.COST_PER_SIDE,
    "cost_multipliers": (1.0, 3.0),
    "phases": (0, 5, 10, 15),
    "liq_window": 20,
    "liq_min_amt": MIN_AMT,
    "null_draws": 200,
}
BARS_PER_YEAR = 252.0


# --------------------------------------------------------------------------- signal

def inst_ratio_matrix(dates, symbols, path: str = LHB_INST) -> tuple:
    """(score matrix, coverage dict).  score[i, j] = institutional net-buy ratio of code j on day i."""
    import pandas as pd
    df = pd.read_parquet(path, columns=["代码", "上榜日期", "机构买入净额", "市场总成交额", "上榜原因"])
    df = df.dropna(subset=["代码", "上榜日期"])
    g = (df.groupby(["代码", "上榜日期"], as_index=False)
           .agg(net=("机构买入净额", "sum"), amt=("市场总成交额", "sum"),
                reasons=("上榜原因", "size")))
    g = g[(g["amt"] > 0) & np.isfinite(g["net"])]
    g["ratio"] = g["net"] / g["amt"]

    didx = {d: i for i, d in enumerate(dates)}
    sidx = {}
    for j, s in enumerate(symbols):
        sidx[s[2:] if s[:2] in ("sh", "sz", "bj") else s] = j

    T, S = len(dates), len(symbols)
    score = np.full((T, S), np.nan)
    rows = g["上榜日期"].map(didx)
    cols = g["代码"].map(sidx)
    ok = rows.notna() & cols.notna()
    score[rows[ok].to_numpy(dtype=np.int64), cols[ok].to_numpy(dtype=np.int64)] = \
        g.loc[ok, "ratio"].to_numpy(dtype=np.float64)

    multi = df["上榜原因"].astype(str).str.contains("累计")
    cov = {
        "lhb_rows": int(len(df)),
        "stock_days": int(len(g)),
        "codes_in_panel": int(ok.sum() and g.loc[ok, "代码"].nunique()),
        "codes_missing_from_price_panel": int(g.loc[~ok, "代码"].nunique()),
        "dates_inside_price_panel": int(g.loc[ok, "上榜日期"].nunique()),
        "cumulative_reason_row_share": float(multi.mean()),
        "mapped_cells": int(ok.sum()),
    }
    return score, cov


def trailing_mean(a: np.ndarray, window: int) -> np.ndarray:
    """Mean over the trailing `window` rows, ignoring NaN; rows with no observation stay NaN."""
    T, S = a.shape
    cs = np.nancumsum(a, axis=0)
    cnt = np.cumsum(np.isfinite(a), axis=0)
    out = np.full((T, S), np.nan)
    for t in range(T):
        lo = max(0, t - window + 1)
        s = cs[t] - (cs[lo - 1] if lo > 0 else np.zeros(S))
        c = cnt[t] - (cnt[lo - 1] if lo > 0 else np.zeros(S))
        out[t] = np.where(c > 0, s / np.maximum(c, 1), np.nan)
    return out


# --------------------------------------------------------------------------- arms

def run_cohorts(signal, fwd, liq_ok, dates, grid: int, kind: str, cost_mult: float,
                cfg: dict | None = None, rng: np.random.Generator | None = None) -> dict:
    """One long-only arm on one decision grid.  `kind` in {decile, n50, pool, bottom, random}."""
    cfg = cfg or CONFIG
    T, S = signal.shape
    h = cfg["rebal"]
    cost = cfg["cost_per_side"] * cost_mult
    rebs = [t for t in range(grid, T - h - 1, h)]
    w_old = np.zeros(S)
    nets, years, names, unused, traded = [], [], [], [], []
    for t in rebs:
        ok = np.isfinite(signal[t]) & np.isfinite(fwd[t]) & liq_ok[t]
        idx = np.flatnonzero(ok)
        if idx.size < cfg["min_names"]:
            unused.append(dates[t])
            continue
        vals = signal[t, idx]
        if kind == "pool":
            sel = idx
        elif kind == "n50":
            sel = idx[np.argsort(-vals, kind="stable")[: cfg["n50"]]]
        elif kind == "decile":
            k = max(1, int(round(idx.size * cfg["decile"])))
            sel = idx[np.argsort(-vals, kind="stable")[:k]]
        elif kind == "bottom":
            k = max(1, int(round(idx.size * cfg["decile"])))
            sel = idx[np.argsort(vals, kind="stable")[:k]]
        elif kind == "random":
            k = max(1, int(round(idx.size * cfg["decile"])))
            sel = rng.choice(idx, size=k, replace=False)
        else:
            raise ValueError("unknown kind %r" % kind)
        w_new = np.zeros(S)
        w_new[sel] = 1.0 / sel.size
        c = float(np.sum(np.abs(w_new - w_old)) * cost)
        nets.append(float(np.mean(fwd[t, sel])) - c)
        years.append(int(dates[t][:4]))
        names.append(int(sel.size))
        traded.append(dates[t])
        w_old = w_new
    net = np.array(nets, dtype=float)
    if net.size:
        net[-1] -= float(np.sum(w_old)) * cost
    stats = J.equity_stats(net, h)
    stats["first_date"] = traded[0] if traded else None
    stats["last_date"] = traded[-1] if traded else None
    stats["mean_names"] = float(np.mean(names)) if names else 0.0
    stats["dates_skipped"] = len(unused)
    stats["cost_mult"] = cost_mult
    stats["per_year"] = J.per_year(net, years)
    stats["_net"] = net
    stats["_years"] = years
    return stats


def null_draws(signal, fwd, liq_ok, dates, grid: int, draws: int, seed: int = 11) -> dict:
    rng = np.random.default_rng(seed)
    obs = []
    for _ in range(draws):
        st = run_cohorts(signal, fwd, liq_ok, dates, grid, "random", 1.0, rng=rng)
        if st["n_cohorts"]:
            obs.append(float(np.mean(st["_net"])))
    return {"draws": len(obs), "mean": float(np.mean(obs)) if obs else None,
            "sd": float(np.std(obs, ddof=1)) if len(obs) > 1 else None,
            "_dist": obs}


def p_value(observed: float, dist: list) -> float:
    if not dist:
        return float("nan")
    return float((np.sum(np.asarray(dist) >= observed) + 1.0) / (len(dist) + 1.0))


# --------------------------------------------------------------------------- fakes

def _fake_score(cfg):
    """A signal that is persistent per NAME (that is what a cross-sectional rule can trade on)
    and only observed on a quarter of the cells."""
    rng = np.random.default_rng(3)
    T, S = cfg["T"], cfg["S"]
    alpha = rng.normal(0.0, 1.0, size=S)
    score = np.full((T, S), np.nan)
    live = rng.random((T, S)) < 0.25
    noisy = alpha[None, :] + rng.normal(0.0, 0.3, size=(T, S))
    score[live] = noisy[live]
    fwd = rng.normal(cfg["mu"], cfg["sd"], size=(T, S))
    liq_ok = np.ones((T, S), dtype=bool)
    dates = ["%04d-%02d-%02d" % (2020 + i // 336, (i // 28) % 12 + 1, i % 28 + 1) for i in range(T)]
    return score, fwd, liq_ok, dates, alpha


def _synthetic_cfg(T, S):
    cfg = dict(CONFIG)
    cfg.update({"T": T, "S": S, "rebal": 20, "min_names": 20, "decile": 0.10,
                "mu": 0.0, "sd": 0.05, "phases": (0,)})
    return cfg


# --------------------------------------------------------------------------- judge

def judge(panel: dict, score: np.ndarray, cov: dict, cfg: dict | None = None,
          draws: int | None = None) -> dict:
    cfg = cfg or CONFIG
    h = cfg["rebal"]
    dates = panel["dates"] if isinstance(panel, dict) and "dates" in panel else panel
    signal = trailing_mean(score, cfg["sig_window"])
    liq = J.rolling_median(panel["amount"], cfg["liq_window"])
    liq_ok = np.isfinite(liq) & (liq >= cfg["liq_min_amt"])
    fwd = P.forward_matrix(panel["open"], panel["close"], h)

    arms: dict = {}
    raw: dict = {}
    for grid in cfg["phases"]:
        g = {}
        for kind in ("decile", "n50", "pool", "bottom"):
            for cm in cfg["cost_multipliers"]:
                st = run_cohorts(signal, fwd, liq_ok, dates, grid, kind, cm, cfg=cfg)
                g["%s_x%d" % (kind, int(cm))] = {k: v for k, v in st.items() if not k.startswith("_")}
                if cm == 1.0:
                    raw["grid%d_%s" % (grid, kind)] = st
        arms["grid%d" % grid] = g

    nd = null_draws(signal, fwd, liq_ok, dates, cfg["phases"][0],
                    draws if draws is not None else cfg["null_draws"])
    obs_net = float(np.mean(raw["grid%d_decile" % cfg["phases"][0]]["_net"])) \
        if raw["grid%d_decile" % cfg["phases"][0]]["n_cohorts"] else float("nan")

    crit = evaluate(arms, raw, p_value(obs_net, nd.pop("_dist")), phases=cfg["phases"])
    return {
        "artifact": "zoo99_lhb_inst_netratio probe",
        "family": "zoo99_lhb_inst_netratio",
        "batch": "SUPPLY_BERTH_INSTITUTIONAL_SEAT_AGGREGATE",
        "machine": "bm-c",
        "evidence_cutoff": dates[-1],
        "panel": {
            "symbols": int(panel["close"].shape[1]),
            "bars": int(panel["close"].shape[0]),
            "first_date": dates[0],
            "last_date": dates[-1],
            "liquidity_gate": {"window": cfg["liq_window"], "min_median_amount_cny": cfg["liq_min_amt"]},
            "coverage": cov,
        },
        "config": {k: v for k, v in cfg.items() if k != "null_draws"},
        "arms": arms,
        "null": nd,
        "criteria": crit,
        "verdict": crit["verdict"],
    }


def evaluate(arms, raw, p, phases=None) -> dict:
    phases = tuple(phases if phases is not None else CONFIG["phases"])
    g0 = arms["grid%d" % phases[0]]
    base = g0["decile_x1"]["cagr"]
    pool1 = g0["pool_x1"]["cagr"]
    pool3 = g0["pool_x3"]["cagr"]
    dec3 = g0["decile_x3"]["cagr"]
    excess_by_phase = {}
    for grid in phases:
        a = arms["grid%d" % grid]["decile_x1"]["cagr"]
        b = arms["grid%d" % grid]["pool_x1"]["cagr"]
        excess_by_phase[str(grid)] = None if (a is None or b is None) else float(a - b)
        if a is None or b is None:
            excess_by_phase[str(grid)] = float("nan")
    c1 = bool(base is not None and pool1 is not None and base > pool1)
    c2 = bool(dec3 is not None and pool3 is not None and dec3 > pool3)
    c3 = bool(np.isfinite(p) and p <= 0.05)
    c4 = bool(all(np.isfinite(list(excess_by_phase.values()))) and
              all(v > 0 for v in excess_by_phase.values()))
    fails = [n for n, c in (("C1_beats_pool_x1", c1), ("C2_beats_pool_x3", c2),
                            ("C3_null_p<=0.05", c3), ("C4_all_phases_positive", c4)) if not c]
    return {
        "arm_A_decile_x1_cagr": base,
        "control_pool_x1_cagr": pool1,
        "arm_A_decile_x3_cagr": dec3,
        "control_pool_x3_cagr": pool3,
        "excess_by_phase": excess_by_phase,
        "null_p": None if not np.isfinite(p) else float(p),
        "C1": c1, "C2": c2, "C3": c3, "C4": c4,
        "failing": fails,
        "verdict": "ADMIT_TO_PREREG" if not fails else "REFUSE_AS_CANDIDATE",
    }


# --------------------------------------------------------------------------- selftest

def selftest() -> int:
    fails = []

    def chk(name, cond):
        print(("  ok   " if cond else "  FAIL ") + name)
        if not cond:
            fails.append(name)

    # trailing_mean: partial windows are means of what is there, empty windows stay NaN
    a = np.array([[1.0], [np.nan], [3.0], [np.nan], [np.nan]])
    tm = trailing_mean(a, 3)
    chk("trailing mean ignores missing rows", np.isclose(tm[2, 0], 2.0))
    chk("trailing mean of a single observation is that observation", np.isclose(tm[0, 0], 1.0))
    chk("a window with no observation stays NaN", np.isnan(trailing_mean(
        np.array([[1.0], [np.nan], [np.nan], [np.nan]]), 2)[3, 0]))

    # informative score -> the frozen rule clears; random score -> it does not
    for label, informative, want in (("injected", True, "ADMIT_TO_PREREG"),
                                     ("unrelated", False, "REFUSE_AS_CANDIDATE")):
        T, S = 320, 120
        cfg = _synthetic_cfg(T, S)
        score, fwd, liq_ok, dates, alpha = _fake_score(cfg)
        if informative:
            fwd = fwd + 0.0008 * alpha[None, :]
        panel = {"dates": dates, "amount": np.ones((T, S)) * 1e8,
                 "open": np.cumprod(1 + fwd, axis=0) * 10.0,
                 "close": np.cumprod(1 + fwd, axis=0) * 10.0}
        out = judge(panel, score, {"fake": True}, cfg=cfg, draws=40)
        chk("%s fixture lands on %s (got %s)" % (label, want, out["verdict"]),
            out["verdict"] == want)
        chk("%s fixture reports a p value in [0,1]" % label,
            out["criteria"]["null_p"] is not None and 0.0 <= out["criteria"]["null_p"] <= 1.0)

    # a signal that predicts the WRONG way must not be admitted by accident
    T, S = 320, 120
    cfg = _synthetic_cfg(T, S)
    score, fwd, liq_ok, dates, alpha = _fake_score(cfg)
    fwd = fwd - 0.0008 * alpha[None, :]
    panel = {"dates": dates, "amount": np.ones((T, S)) * 1e8,
             "open": np.cumprod(1 + fwd, axis=0) * 10.0,
             "close": np.cumprod(1 + fwd, axis=0) * 10.0}
    out = judge(panel, score, {"fake": True}, cfg=cfg, draws=40)
    chk("an inverted signal is refused", out["verdict"] == "REFUSE_AS_CANDIDATE")

    # p-value legs
    chk("p is small when the observation tops its null", p_value(1.0, [0.0] * 99) < 0.02)
    chk("p is large when the observation sits in the null's middle", p_value(0.0, [-1.0] * 50 + [1.0] * 50) > 0.4)
    chk("an empty null reports NaN, not 0", np.isnan(p_value(1.0, [])))

    # the ratio aggregation: multi-day cumulative rows are summed, not averaged
    import pandas as pd
    df = pd.DataFrame({"代码": ["600000"] * 2, "上榜日期": ["2020-01-02"] * 2,
                       "机构买入净额": [1.0e7, -4.0e6], "市场总成交额": [1.0e8, 2.0e8],
                       "上榜原因": ["同日", "连续三个交易日累计"]})
    g = (df.groupby(["代码", "上榜日期"], as_index=False)
           .agg(net=("机构买入净额", "sum"), amt=("市场总成交额", "sum")))
    chk("same stock-day rows sum into one ratio", np.isclose(g["net"].iloc[0], 6.0e6) and
        np.isclose(g["amt"].iloc[0], 3.0e8))

    print("selftest: %d checks, %d failed" % (12, len(fails)))
    return 0 if not fails else 1


# --------------------------------------------------------------------------- main

def _jsonable(o):
    if isinstance(o, dict):
        return {k: _jsonable(v) for k, v in o.items() if not k.startswith("_")}
    if isinstance(o, (list, tuple)):
        return [_jsonable(v) for v in o]
    if isinstance(o, (np.floating, float)):
        f = float(o)
        return None if not np.isfinite(f) else f
    if isinstance(o, (np.integer,)):
        return int(o)
    return o


def run(max_symbols: int | None = None) -> int:
    t0 = time.time()
    panel = P.load_panel(max_symbols=max_symbols)
    score, cov = inst_ratio_matrix(panel["dates"], panel["symbols"])
    out = judge(panel, score, cov)
    out["elapsed_sec"] = round(time.time() - t0, 1)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(_jsonable(out), fh, ensure_ascii=False, indent=1)
    c = out["criteria"]
    print("zoo99: %s  A_x1=%s pool_x1=%s A_x3=%s pool_x3=%s p=%s failed=%s"
          % (out["verdict"], _fmt(c["arm_A_decile_x1_cagr"]), _fmt(c["control_pool_x1_cagr"]),
             _fmt(c["arm_A_decile_x3_cagr"]), _fmt(c["control_pool_x3_cagr"]),
             _fmt(c["null_p"]), ",".join(c["failing"]) or "none"))
    print("zoo99: cohorts=%s coverage=%s elapsed=%.1fs"
          % (out["arms"]["grid0"]["decile_x1"]["n_cohorts"], cov["stock_days"], out["elapsed_sec"]))
    print("zoo99: wrote %s" % os.path.relpath(OUT, ROOT))
    return 0


def _fmt(v):
    return "n/a" if v is None else "%.2f%%" % (100.0 * v)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run")
    ap.add_argument("--max-symbols", type=int, default=None)
    a = ap.parse_args()
    if a.cmd == "selftest":
        return selftest()
    if a.cmd != "run":
        print(__doc__)
        return 2
    return run(max_symbols=a.max_symbols)


if __name__ == "__main__":
    sys.exit(main())