#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""zoo98_repo_rate_stress -- supply berth probe (funding-liquidity family).

WHY THIS FILE EXISTS
--------------------
The supply floor has read ready 0 < floor 3 for twelve rounds, and every berth
burned in that stretch asked a question about the *tape* (breadth, the forced
trade, momentum, the cost basis an owner sits on).  #98 asks about the money
that pays for the tape: the exchange repo rate.  When overnight funding gets
expensive, leveraged and margined positions get marked down for reasons that
have nothing to do with the assets themselves, and the folklore ("quarter-end
money is tight") is older than any of our panels.

    does a state gate built on GC001's own trailing percentile -- go to cash
    while funding is in its top decile, hold equity otherwise -- earn its
    turnover after cost, beyond a same-share phase null?

CONSTRUCTION (frozen; changing any of it changes the family)
------------------------------------------------------------
  rate panel  data/repo_daily/GC001.csv, column close (annualised %, the
              exchange's own close).  Rows outside the panel's own 0<close<200
              sanity band are dropped (the archive carries one 53.44% Spring
              Festival print; that is a real level, not an outlier to clip).
  level       pct_t = percentile rank of close_t inside the trailing W=252-bar
              window ENDING AT t (min_periods=W; no bar uses a later bar).
  state       tight when pct_t >= Q=0.90.  Rows that have neither a full
              window nor a rate quote are NaN = "no decision", never 0.
  confirm     the gate must read tight CONFIRM=2 consecutive bars before it
              acts (one bar of quarter-end noise is not a funding regime).
  allocation  tight -> 0% equity / 100% cash leg 511260; else 100% equity
              510300.  No partial sizing, no leverage.
  execution   decision on the close of bar t is held from bar t+1.
  benchmark   buy-and-hold the same equity leg over the same evaluated window.
  cost        turn * COST_X1_RATE where turn = 2*sum|dw| (both legs trade).
  null        circular phase rotation of the weight series, K=200 draws: it
              conserves the equity share and the persistence, so a rule that
              is simply out of the market a lot cannot win on share alone.

Everything here is a PROBE.  It burns no family, registers no seed, writes no
ledger row.  Its verdict is a *supply* verdict (ADMIT_TO_PREREG /
REFUSE_AS_CANDIDATE), never a research verdict.

HONEST LIMITS printed with the reading: GC001's close is quoted annualised and
is not the rate a particular position pays; the panel starts 2011 while the
equity leg starts 2020, so this probe only sees the recent shape of the cycle;
month-end clustering is a calendar property, and a cash leg that earns carry
means part of any excess is bond carry rather than timing.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from ce_transfer import COST_X1_RATE                      # noqa: E402
from live.paper import build_panels, load_core            # noqa: E402

# ---- frozen constants (echoed into every artifact) -------------------------
FAMILY = "zoo98_repo_rate_stress"
BATCH = "SUPPLY_BERTH_SLOT_14_CANDIDATE"
EQUITY = "510300"
CASH = "511260"
RATE_FILE = os.path.join(ROOT, "data", "repo_daily", "GC001.csv")
WINDOW = 252                    # one trading year of rate history
QUANTILE = 0.90                 # "top decile of funding stress"
CONFIRM = 2                     # consecutive tight bars before the gate acts
NULL_K = 200
NULL_SEED = 20981007
EVIDENCE_CUTOFF = "2026-11-06"
MIN_BARS = 750
ADMIT_MIN_EXCESS = 0.0
ADMIT_MAX_P = 0.05
ADMIT_DD_MUST_IMPROVE = True
ADMIT_MAX_TURNOVER_PER_YEAR = 24.0

RES_PATH = os.path.join(ROOT, "results", "supply_berth",
                        "zoo98_repo_rate_stress_probe.json")


def _now():
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


# ------------------------------------------------------------------- data
def load_rates(path: str = RATE_FILE) -> pd.Series:
    """GC001 close as an annualised-percent series indexed by bar date."""
    df = pd.read_csv(path)
    if "date" not in df.columns or "close" not in df.columns:
        raise SystemExit("rate panel missing date/close columns")
    df["date"] = pd.to_datetime(df["date"])
    r = pd.to_numeric(df["close"], errors="coerce")
    keep = r.notna() & (r > 0.0) & (r < 200.0)
    df, r = df[keep], r[keep]
    s = pd.Series(r.to_numpy(dtype=float), index=pd.DatetimeIndex(df["date"]))
    return s[~s.index.duplicated(keep="last")].sort_index()


# -------------------------------------------------------------- mechanics
def trailing_percentile(rate: pd.Series, window: int = WINDOW) -> pd.Series:
    """Percentile rank of each bar inside the window ending AT that bar.

    min_periods=window: a partial window is NaN ("no decision yet"), never a
    silently different statistic.
    """
    if len(rate) < window:
        return pd.Series(np.nan, index=rate.index)
    # rolling().rank() already reads each bar's rank INSIDE its own trailing
    # window (the bar is the newest member of that window).
    return rate.rolling(window, min_periods=window).rank(pct=True)


def tight_state(pct: pd.Series, q: float = QUANTILE) -> pd.Series:
    """Boolean-ish state: True = tight funding.  NaN stays NaN (no decision)."""
    out = pd.Series(np.nan, index=pct.index, dtype=float)
    ok = pct.notna()
    if ok.any():
        out.loc[ok] = (pct.loc[ok] >= q).astype(float)
    return out


def confirmed(state: pd.Series, n: int = CONFIRM) -> pd.Series:
    """Require `n` consecutive tight readings before the gate acts.

    A single True stays False until it has `n` in a row; a run that breaks
    resets.  NaN (no decision) breaks the run and stays NaN.
    """
    vals = state.to_numpy(dtype=float)
    out = np.full(len(vals), np.nan)
    run = 0
    for i, v in enumerate(vals):
        if not np.isfinite(v):
            run = 0
            continue
        if v >= 0.5:
            run += 1
        else:
            run = 0
        out[i] = 1.0 if run >= n else 0.0
    return pd.Series(out, index=state.index)


def weights_from_gate(gate_tight: pd.Series) -> pd.Series:
    """Tight -> 0% equity; loose -> 100%.  Decision on bar t held from t+1."""
    w = (1.0 - gate_tight.astype(float)).where(gate_tight.notna())
    return w.shift(1).fillna(0.0)


def evaluated_window(index: pd.DatetimeIndex, gate_tight: pd.Series) -> pd.DatetimeIndex:
    """Start at the first bar the gate could actually act on."""
    valid = gate_tight.dropna()
    if len(valid) == 0:
        return index[:0]
    pos = index.get_loc(valid.index[0])
    return index[pos + 1:]


def run_blend(ret_eq: pd.Series, ret_cash: pd.Series, w_eq: pd.Series,
              cost: float = COST_X1_RATE) -> dict:
    """Net return series of an equity/cash blend at weight w_eq."""
    w = w_eq.reindex(ret_eq.index).fillna(0.0)
    dw = w.diff().abs().fillna(w.abs())
    turn = 2.0 * dw                                  # both legs trade
    net = w * ret_eq + (1.0 - w) * ret_cash - turn * cost
    ann = 252.0
    n = int(len(net))
    sd = float(net.std(ddof=1)) if n > 1 else 0.0
    return {
        "bars": n,
        "equity_share": float(w.mean()),
        "switches": int((dw > 1e-12).sum()),
        "turnover_per_year": float(turn.sum() / max(n / ann, 1e-9)),
        "cost_drag_per_year": float(turn.sum() * cost / max(n / ann, 1e-9)),
        "cagr": float((1.0 + net).prod() ** (ann / n) - 1.0) if n > 0 else None,
        "sharpe": float(net.mean() / sd * np.sqrt(ann)) if sd > 0 else None,
        "maxdd": _maxdd(net),
        "net": net,
    }


def _maxdd(r: pd.Series) -> float:
    eq = (1.0 + r.fillna(0.0)).cumprod()
    return float((eq / eq.cummax() - 1.0).min())


def _buyhold_cagr(r: pd.Series) -> float:
    n = len(r)
    if n == 0:
        return 0.0
    return float((1.0 + r.fillna(0.0)).prod() ** (252.0 / n) - 1.0)


def per_year_excess(net: pd.Series, bh: pd.Series) -> dict:
    """Compounded net vs benchmark, one row per calendar year."""
    out = {}
    for y in sorted({d.year for d in net.index}):
        m = np.array([d.year == y for d in net.index])
        if m.sum() < 20:
            continue
        a = float((1.0 + net[m]).prod() - 1.0)
        b = float((1.0 + bh[m]).prod() - 1.0)
        out[str(y)] = {"net": a, "benchmark": b, "excess": a - b,
                       "bars": int(m.sum())}
    return out


def circular_null(ret_eq: pd.Series, ret_cash: pd.Series, w_eq: pd.Series,
                  observed: float, k: int = NULL_K, seed: int = NULL_SEED) -> dict:
    """Same equity share, same persistence, different phase."""
    w = w_eq.reindex(ret_eq.index).fillna(0.0).to_numpy(dtype=float)
    n = len(w)
    if n < 3:
        return {"k": 0, "p_two_sided": 1.0, "mean": 0.0, "sd": 0.0,
                "method": "not enough bars for a phase null"}
    rng = np.random.default_rng(seed)
    draws = []
    for _ in range(k):
        s = int(rng.integers(1, n - 1))
        draws.append(run_blend(ret_eq, ret_cash,
                               pd.Series(np.roll(w, s), index=ret_eq.index))
                     ["cagr"] - _buyhold_cagr(ret_eq))
    arr = np.array(draws, dtype=float)
    ge = int((np.abs(arr) >= abs(observed)).sum())
    return {
        "k": k,
        "seed": seed,
        "method": "circular phase rotation of the equity-weight series "
                  "(conserves equity share and persistence)",
        "mean": float(arr.mean()),
        "sd": float(arr.std(ddof=1)) if len(arr) > 1 else 0.0,
        "p_two_sided": float((ge + 1) / (k + 1)),
        "p_floor": float(1.0 / (k + 1)),
    }


def decide(summary: dict, null: dict) -> dict:
    """Frozen supply verdict; every condition is reported, not just the boolean."""
    conds = {
        "net_excess_positive": summary["excess_cagr_net"] > ADMIT_MIN_EXCESS,
        "beats_null": null["p_two_sided"] <= ADMIT_MAX_P,
        "drawdown_improves": (summary["maxdd_delta"] > 0
                              if ADMIT_DD_MUST_IMPROVE else True),
        "enough_bars": summary["bars"] >= MIN_BARS,
        "turnover_sane": summary["turnover_per_year"] <= ADMIT_MAX_TURNOVER_PER_YEAR,
    }
    return {
        "verdict": "ADMIT_TO_PREREG" if all(conds.values()) else "REFUSE_AS_CANDIDATE",
        "conditions": conds,
        "thresholds": {"min_excess": ADMIT_MIN_EXCESS, "max_p": ADMIT_MAX_P,
                       "dd_must_improve": ADMIT_DD_MUST_IMPROVE,
                       "min_bars": MIN_BARS,
                       "max_turnover_per_year": ADMIT_MAX_TURNOVER_PER_YEAR},
        "note": "supply verdict only: it decides whether this family earns a "
                "frozen prereg + judge, never what the judge will find",
    }


# ------------------------------------------------------------------- build
def build(prices: dict | None = None, rate: pd.Series | None = None,
          cutoff: str = EVIDENCE_CUTOFF) -> dict:
    prices = prices if prices is not None else load_core()
    rate = rate if rate is not None else load_rates()
    P = build_panels(prices)
    close = P["close"]
    # The evaluated window ends where BOTH panels have measured bars: the rate
    # archive lags the equity tape, and forward-filling a stale level across
    # the gap would read a funding state nobody measured.
    cut = min(pd.Timestamp(cutoff), pd.Timestamp(rate.index[-1]))
    if close.index[-1] > cut:
        close = close.loc[:cut]
    if EQUITY not in close.columns or CASH not in close.columns:
        raise SystemExit("missing leg: %s / %s" % (EQUITY, CASH))

    idx = close.index
    # The rate panel is the binding calendar: reindex onto the equity bars and
    # forward-fill a holiday gap (a holiday has no auction, not a new level).
    rate_on_idx = rate.reindex(rate.index.union(idx)).ffill().reindex(idx)
    pct = trailing_percentile(rate_on_idx)
    gate = confirmed(tight_state(pct))

    eq_p, cash_p = close[EQUITY], close[CASH]
    ret_eq, ret_cash = eq_p.pct_change(), cash_p.pct_change()

    w_all = weights_from_gate(gate)
    window = evaluated_window(idx, gate)
    if len(window) == 0:
        raise SystemExit("no evaluable window: the rate panel does not reach the equity bars")
    w = w_all.reindex(window)

    obs = run_blend(ret_eq.reindex(window), ret_cash.reindex(window), w)
    bh_ret = ret_eq.reindex(window)
    bh = {"cagr": _buyhold_cagr(bh_ret),
          "maxdd": _maxdd(bh_ret),
          "sharpe": (float(bh_ret.mean() / bh_ret.std(ddof=1) * np.sqrt(252))
                     if float(bh_ret.std(ddof=1)) > 0 else None)}
    cash_only = {"cagr": _buyhold_cagr(ret_cash.reindex(window)),
                 "maxdd": _maxdd(ret_cash.reindex(window))}

    tight_bars = int((gate.reindex(window).fillna(0.0) >= 0.5).sum())
    summary = {
        "bars": obs["bars"],
        "first_bar": str(window[0].date()),
        "last_bar": str(window[-1].date()),
        "rate_bars_in_window": int(rate_on_idx.reindex(window).notna().sum()),
        "tight_bars": tight_bars,
        "tight_share": float(tight_bars / max(len(window), 1)),
        "equity_share": obs["equity_share"],
        "switches": obs["switches"],
        "turnover_per_year": obs["turnover_per_year"],
        "cost_drag_per_year": obs["cost_drag_per_year"],
        "timing_cagr": obs["cagr"],
        "timing_sharpe": obs["sharpe"],
        "timing_maxdd": obs["maxdd"],
        "buyhold_cagr": bh["cagr"],
        "buyhold_sharpe": bh["sharpe"],
        "buyhold_maxdd": bh["maxdd"],
        "cash_only_cagr": cash_only["cagr"],
        "cash_only_maxdd": cash_only["maxdd"],
    }
    summary["excess_cagr_net"] = summary["timing_cagr"] - summary["buyhold_cagr"]
    summary["maxdd_delta"] = summary["timing_maxdd"] - summary["buyhold_maxdd"]

    null = circular_null(ret_eq.reindex(window), ret_cash.reindex(window), w,
                         summary["excess_cagr_net"])
    by_year = per_year_excess(obs["net"], bh_ret)
    verdict = decide(summary, null)

    return {
        "artifact": "zoo98_repo_rate_stress supply berth probe",
        "machine": os.environ.get("BM_MACHINE") or _machine(),
        "ts": _now(),
        "evidence_cutoff": cutoff,
        "batch": BATCH,
        "family": FAMILY,
        "construct": {
            "rate_panel": os.path.relpath(RATE_FILE, ROOT).replace(os.sep, "/"),
            "rate_column": "close (annualised %, GC001 exchange close)",
            "legs": {"equity": EQUITY, "cash": CASH},
            "window": WINDOW,
            "quantile": QUANTILE,
            "confirm_bars": CONFIRM,
            "state": "pct_rank(close_t within trailing %d bars) >= %.2f"
                     " for %d consecutive bars -> tight" % (WINDOW, QUANTILE, CONFIRM),
            "allocation": "tight -> 0%% equity, else 100%% equity (no partial sizing)",
            "execution": "decided on the close of bar t, held from bar t+1",
            "cost_per_side": COST_X1_RATE,
            "turnover_convention": "sum |dw| over both legs (a switch = 2.0)",
        },
        "panel": {"n_members": int(close.shape[1]),
                  "bars": int(close.shape[0]),
                  "first_bar": str(close.index[0].date()),
                  "last_bar": str(close.index[-1].date()),
                  "rate_first_bar": str(rate.index[0].date()),
                  "rate_last_bar": str(rate.index[-1].date())},
        "summary": summary,
        "null": null,
        "per_year": by_year,
        "verdict_block": verdict,
        "honest": [
            "probe only: one construct, one frozen parameter set, no grid -- a "
            "positive here buys a frozen prereg and a proper judge, not a claim "
            "that the gate makes money",
            "GC001's close is quoted annualised and is not the rate any "
            "particular position pays; a funding-stress level is a proxy for "
            "the price of leverage, not the price of our position",
            "the rate panel starts 2011 but the equity leg starts 2020, so the "
            "probe only ever sees the recent shape of the funding cycle",
            "the cash leg is an investable treasury ETF with its own positive "
            "return, so part of any excess is bond carry rather than timing",
            "the circular null conserves the equity share, so a rule that is "
            "simply out of the market most of the time cannot win on share alone",
            "the rate series is reindexed onto the equity calendar with a "
            "forward fill: a holiday carries the previous level, never a "
            "fabricated new one",
        ],
    }


def _machine() -> str:
    try:
        with open(os.path.join(ROOT, "fleet", "machine.json"),
                  encoding="utf-8") as fh:
            return json.load(fh).get("machine_id", "unknown")
    except Exception:
        return "unknown"


def run() -> int:
    out = build()
    os.makedirs(os.path.dirname(RES_PATH), exist_ok=True)
    with open(RES_PATH, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1, sort_keys=True)
    s, n, v = out["summary"], out["null"], out["verdict_block"]
    print("[zoo98] window %s..%s (%d bars) tight %d bars (%.1f%%)" % (
        s["first_bar"], s["last_bar"], s["bars"], s["tight_bars"],
        100.0 * s["tight_share"]))
    print("[zoo98] equity_share %.3f  switches %d  turnover %.2f/yr  "
          "cost_drag %.4f/yr" % (s["equity_share"], s["switches"],
                                 s["turnover_per_year"], s["cost_drag_per_year"]))
    print("[zoo98] gate %.4f vs buyhold %.4f  excess %+.4f | maxdd %.4f vs "
          "%.4f (delta %+.4f) | cash-only %.4f" % (
              s["timing_cagr"], s["buyhold_cagr"], s["excess_cagr_net"],
              s["timing_maxdd"], s["buyhold_maxdd"], s["maxdd_delta"],
              s["cash_only_cagr"]))
    print("[zoo98] null p=%.4f (mean %+.4f sd %.4f)" % (
        n["p_two_sided"], n["mean"], n["sd"]))
    print("[zoo98] VERDICT %s  conditions=%s" % (v["verdict"], v["conditions"]))
    print("[zoo98] receipt %s" % os.path.relpath(RES_PATH, ROOT))
    return 0


# ---------------------------------------------------------------- selftest
def selftest() -> int:
    ok, fail = 0, []

    def leg(name, fn):
        nonlocal ok
        try:
            fn()
        except AssertionError as e:
            fail.append("%s: %s" % (name, e))
        else:
            ok += 1

    def _idx(n, start="2021-01-01"):
        return pd.date_range(start, periods=n, freq="B")

    def l_percentile_is_backward_looking():
        idx = _idx(300)
        s = pd.Series(np.arange(300, dtype=float), index=idx)
        pct = trailing_percentile(s, window=20)
        assert pd.isna(pct.iloc[18]), "a partial window must be NaN"
        assert abs(float(pct.iloc[19]) - 1.0) < 1e-12, \
            "the newest bar of a rising series is the top of its own window"
        # Editing nothing after t must not change pct at t.
        s2 = s.copy()
        s2.iloc[200:] = -999.0
        assert abs(float(trailing_percentile(s2, 20).iloc[150])
                   - float(pct.iloc[150])) < 1e-12, \
            "a later bar must never change an earlier percentile"

    def l_percentile_constant_series():
        idx = _idx(60)
        s = pd.Series(1.0, index=idx)
        pct = trailing_percentile(s, window=20)
        # Ties share the window's average rank, not the top: 10.5/20 = 0.525.
        assert abs(float(pct.iloc[-1]) - 0.525) < 1e-12, \
            "a flat window's members tie at the average rank, got %r" % float(pct.iloc[-1])
        assert float(tight_state(pct, q=0.90).iloc[-1]) == 0.0, \
            "a flat rate must not read as funding stress"

    def l_tight_state_direction():
        pct = pd.Series([0.05, 0.50, 0.95], index=_idx(3))
        st = tight_state(pct, q=0.90)
        assert list(st.to_numpy()) == [0.0, 0.0, 1.0], \
            "only the top decile is tight, got %r" % list(st.to_numpy())

    def l_tight_state_keeps_nan():
        pct = pd.Series([np.nan, 0.99], index=_idx(2))
        st = tight_state(pct, q=0.90)
        assert pd.isna(st.iloc[0]), "no reading must stay no-decision"
        assert float(st.iloc[1]) == 1.0, "a reading still decides"

    def l_confirm_needs_consecutive():
        idx = _idx(8)
        st = pd.Series([0, 1, 0, 1, 1, 0, 1, 1], index=idx, dtype=float)
        c = confirmed(st, n=2)
        assert list(c.to_numpy()[:4]) == [0.0, 0.0, 0.0, 0.0], \
            "a lone reading must not act, got %r" % list(c.to_numpy()[:4])
        assert float(c.iloc[4]) == 1.0, "two in a row must act"
        assert float(c.iloc[5]) == 0.0, "a break resets the run"
        assert float(c.iloc[7]) == 1.0, "a new run must act again"

    def l_confirm_breaks_on_nan():
        idx = _idx(4)
        st = pd.Series([1.0, np.nan, 1.0, 1.0], index=idx)
        c = confirmed(st, n=2)
        assert pd.isna(c.iloc[1]), "no decision must stay no decision"
        assert float(c.iloc[2]) == 0.0, "a NaN must break the run, not continue it"
        assert float(c.iloc[3]) == 1.0, "two clean readings after the gap act"

    def l_gate_maps_to_cash():
        idx = _idx(5)
        gate = pd.Series([1.0, 0.0, 0.0, 1.0, 0.0], index=idx)
        w = weights_from_gate(gate)
        assert float(w.iloc[0]) == 0.0, "a decision cannot earn its own bar"
        assert float(w.iloc[1]) == 0.0, "tight on t-1 means cash on t"
        assert float(w.iloc[2]) == 1.0, "loose on t-1 means equity on t"
        assert float(w.iloc[4]) == 0.0, "tight on t-1 means cash on t"

    def l_cost_is_two_legs_per_switch():
        idx = _idx(50)
        r = pd.Series(0.0, index=idx)
        w = pd.Series(0.0, index=idx)
        w.iloc[10:] = 1.0
        out = run_blend(r, r, w, cost=0.001)
        assert out["switches"] == 1, "one switch expected, got %d" % out["switches"]
        assert abs(out["cost_drag_per_year"] - 2.0 * 0.001 * 252 / 50) < 1e-12, \
            "cost must charge both legs once"

    def l_always_loose_reproduces_buyhold():
        idx = _idx(400)
        rng = np.random.default_rng(3)
        r_eq = pd.Series(rng.normal(0.0003, 0.01, len(idx)), index=idx)
        out = run_blend(r_eq, pd.Series(0.0, index=idx),
                        pd.Series(1.0, index=idx), cost=0.0)
        assert abs(out["cagr"] - _buyhold_cagr(r_eq)) < 1e-12, \
            "always-in must reproduce buy-and-hold exactly"

    def l_fully_cash_earns_cash():
        idx = _idx(300)
        r_cash = pd.Series(0.0001, index=idx)
        out = run_blend(pd.Series(0.001, index=idx), r_cash,
                        pd.Series(0.0, index=idx), cost=0.0)
        assert abs(out["cagr"] - _buyhold_cagr(r_cash)) < 1e-12, \
            "a fully-cash book must earn exactly the cash leg"

    def l_null_does_not_flag_buy_and_hold():
        idx = _idx(600)
        rng = np.random.default_rng(5)
        r_eq = pd.Series(rng.normal(0.0003, 0.01, len(idx)), index=idx)
        w = pd.Series(1.0, index=idx)
        obs = run_blend(r_eq, pd.Series(0.0, index=idx), w, cost=0.0)["cagr"] \
            - _buyhold_cagr(r_eq)
        n = circular_null(r_eq, pd.Series(0.0, index=idx), w, obs, k=30)
        assert abs(obs) < 1e-12, "identity excess must be zero"
        assert n["p_two_sided"] > 0.05, "null must not flag an all-equity book"

    def l_null_flags_alignment():
        idx = _idx(600)
        rng = np.random.default_rng(9)
        r_eq = pd.Series(rng.normal(0.0, 0.008, len(idx)), index=idx)
        for lo, hi, mu in ((0, 120, 0.010), (120, 240, -0.010),
                           (240, 400, 0.012), (400, 500, -0.009),
                           (500, 600, 0.011)):
            r_eq.iloc[lo:hi] = r_eq.iloc[lo:hi] + mu
        w = (r_eq > 0).astype(float)
        obs = run_blend(r_eq, pd.Series(0.0, index=idx), w)["cagr"] \
            - _buyhold_cagr(r_eq)
        n = circular_null(r_eq, pd.Series(0.0, index=idx), w, obs, k=60)
        assert obs > 0, "a perfectly aligned rule must read positive, got %r" % obs
        assert n["p_two_sided"] <= 0.10, \
            "an aligned rule must be flagged by its own phase null, p=%r" % n["p_two_sided"]

    def l_verdict_names_failing_condition():
        s = {"excess_cagr_net": 0.02, "maxdd_delta": -0.05, "bars": 900,
             "turnover_per_year": 3.0}
        v = decide(s, {"p_two_sided": 0.01})
        assert v["verdict"] == "REFUSE_AS_CANDIDATE", "worse drawdown must refuse"
        assert v["conditions"]["drawdown_improves"] is False, "failing condition must be named"
        assert v["conditions"]["net_excess_positive"] is True, "passing conditions still reported"

    def l_verdict_refuses_expensive_rule():
        s = {"excess_cagr_net": 0.05, "maxdd_delta": 0.02, "bars": 900,
             "turnover_per_year": 30.0}
        v = decide(s, {"p_two_sided": 0.001})
        assert v["verdict"] == "REFUSE_AS_CANDIDATE", "turnover budget must bind"
        assert v["conditions"]["turnover_sane"] is False, "turnover condition must be named"

    def l_verdict_admits_clean_sweep():
        s = {"excess_cagr_net": 0.02, "maxdd_delta": 0.02, "bars": 900,
             "turnover_per_year": 3.0}
        v = decide(s, {"p_two_sided": 0.01})
        assert v["verdict"] == "ADMIT_TO_PREREG", "clean sweep must admit"

    def l_short_panel_refuses_on_bars():
        s = {"excess_cagr_net": 0.05, "maxdd_delta": 0.05, "bars": 200,
             "turnover_per_year": 2.0}
        v = decide(s, {"p_two_sided": 0.001})
        assert v["conditions"]["enough_bars"] is False, "a short window must be named"
        assert v["verdict"] == "REFUSE_AS_CANDIDATE", "short window must refuse"

    def l_rate_panel_band_is_enforced():
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "r.csv")
            with open(p, "w", encoding="utf-8") as fh:
                fh.write("date,open,high,low,close,volume\n")
                fh.write("2021-01-04,1,1,1,1.5,10\n")
                fh.write("2021-01-05,1,1,1,250.0,10\n")   # out of band
                fh.write("2021-01-06,1,1,1,0.0,10\n")     # out of band
                fh.write("2021-01-07,1,1,1,2.5,10\n")
            s = load_rates(p)
            assert len(s) == 2, "out-of-band rows must be dropped, got %d" % len(s)
            assert list(s.to_numpy()) == [1.5, 2.5], "kept levels must be verbatim"
            assert s.index[0] == pd.Timestamp("2021-01-04"), "index must be the bar date"

    def l_deterministic():
        idx = _idx(700)
        rng = np.random.default_rng(13)
        r_eq = pd.Series(rng.normal(0.0003, 0.01, len(idx)), index=idx)
        w = pd.Series((np.arange(len(idx)) % 30 < 5).astype(float), index=idx)
        a = run_blend(r_eq, pd.Series(0.0, index=idx), w)
        b = run_blend(r_eq, pd.Series(0.0, index=idx), w)
        assert json.dumps({k: v for k, v in a.items() if k != "net"}, sort_keys=True) == \
            json.dumps({k: v for k, v in b.items() if k != "net"}, sort_keys=True), \
            "identical input must give identical numbers"

    def l_per_year_covers_window():
        idx = _idx(600)
        net = pd.Series(0.0, index=idx)
        py = per_year_excess(net, net)
        assert sum(v["bars"] for v in py.values()) <= len(idx), "years cannot over-count bars"
        assert all(abs(v["excess"]) < 1e-15 for v in py.values()), "flat arms must show zero excess"

    def l_evaluated_window_starts_after_warmup():
        idx = _idx(400)
        gate = pd.Series(np.nan, index=idx)
        gate.iloc[260:] = 0.0
        win = evaluated_window(idx, gate)
        assert len(win) > 0, "a decided gate must give a window"
        assert win[0] > idx[260], "the window starts strictly after the first decision"

    for name, fn in [
        ("percentile is backward looking", l_percentile_is_backward_looking),
        ("flat window ranks at the top", l_percentile_constant_series),
        ("tight state follows the quantile", l_tight_state_direction),
        ("no reading stays no decision", l_tight_state_keeps_nan),
        ("confirmation needs consecutive bars", l_confirm_needs_consecutive),
        ("a NaN breaks the confirmation run", l_confirm_breaks_on_nan),
        ("tight gate maps to cash next bar", l_gate_maps_to_cash),
        ("a switch trades both legs", l_cost_is_two_legs_per_switch),
        ("always-loose reproduces buy-and-hold", l_always_loose_reproduces_buyhold),
        ("a fully-cash book earns the cash leg", l_fully_cash_earns_cash),
        ("null does not flag buy-and-hold", l_null_does_not_flag_buy_and_hold),
        ("null catches a perfectly aligned rule", l_null_flags_alignment),
        ("verdict names the failing condition", l_verdict_names_failing_condition),
        ("verdict refuses an expensive rule", l_verdict_refuses_expensive_rule),
        ("verdict admits a clean sweep", l_verdict_admits_clean_sweep),
        ("short window refuses on bars", l_short_panel_refuses_on_bars),
        ("rate band drops impossible levels", l_rate_panel_band_is_enforced),
        ("receipt is deterministic", l_deterministic),
        ("per-year rows cannot over-count", l_per_year_covers_window),
        ("window starts after warmup", l_evaluated_window_starts_after_warmup),
    ]:
        leg(name, fn)

    total = ok + len(fail)
    for f in fail:
        print("FAIL %s" % f)
    print("selftest: %d/%d PASS" % (ok, total))
    return 0 if not fail else 1


def main(argv) -> int:
    mode = (argv[1] if len(argv) > 1 else "run").lower().lstrip("-")
    if mode == "selftest":
        return selftest()
    if mode == "run":
        return run()
    print("usage: zoo98_repo_rate_stress_probe.py [run|selftest]", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))