#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""zoo85_salience_panic_probe -- supply berth probe (STOCK-domain cross-section).

WHY THIS FILE EXISTS
--------------------
The fill ladder has reported `compatible_ready=0 floor=3` for twenty-one rounds.
zoo #85 (`salience_panic`, Barberis-Shleifer 2012 salience theory / Cosemans-Frehen
2021) is registered since 2026-09-25 and has never been burned: the tree holds the
registry row and one judging digest, no probe.  It is the only registered stock-domain
behavioural factor that is *not* a reversal-from-some-price-pattern variant, and the
one question the berth asks is cheap enough to answer before anybody spends a frozen
prereg:

    do the names the crowd did NOT chase (low salience-weighted past return)
    beat the pool they were drawn from, after the cost of turning the book over,
    by more than a random equal-size draw from that same pool?

Everything here is a PROBE.  It burns no family, registers no seed, writes no ledger
row.  Its verdict is a *supply* verdict (`ADMIT_TO_PREREG` / `REFUSE_AS_CANDIDATE`),
never a research verdict.

CONSTRUCTION (frozen for this probe; changing any of it changes the family)
--------------------------------------------------------------------------
  r_i,t      close-to-close return of name i on bar t
  r_m,t      510300 close-to-close return -- the exchange-wide leg the registry calls
             中证全指; the ETF is the in-house priced proxy, disclosed not hidden
  salience   |r_i - r_m| / (|r_i| + |r_m| + 0.1)         (Cosemans-Frehen 2021)
  V_i,t      sum over the trailing W bars of salience * r_i
             = the return the name delivered WHILE it was grabbing attention
  factor     V, ranked ASCENDING: the bottom decile is the names the crowd did not chase
  cohorts    non-overlapping H-bar cohorts, four decision phases (0, 5, 10, 15)
  entry      next bar's open, exit H bars later's open (no same-bar trade anywhere)
  cost       COST_X1_RATE per side, two sides per cohort (sell the old book, buy the
             new one); x3 leg reported beside it
  control    the pool itself: every liquid candidate on that date, equal weight --
             the same denominator zoo #93 was measured against
  null       DRAW random equal-size draws from the SAME candidate pool; the statistic
             is portfolio minus pool, so the null is centred on zero by construction

The long side is the only side priced as a candidate: a single A-share cannot be
shorted, so a decile *spread* is a claim about a portfolio nobody can hold.

Run:  python scripts/zoo85_salience_panic_probe.py run | selftest
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

import zoo93_disposition_cgo_probe as Z  # noqa: E402  (panel reader of record)

OUT = os.path.join(ROOT, "results", "supply_berth", "zoo85_salience_panic_probe.json")
ETF_510300 = os.path.join(ROOT, "data", "daily", "sh510300.csv")

COST_PER_SIDE = Z.COST_PER_SIDE        # COST_X1_RATE, what the book cards pay
START = "2020-01-01"
WINDOW = 20                            # past return memory, frozen for this probe
HORIZONS = (20, 60)
PRIMARY_H = 20
DECILE = 0.10
LIQ_WINDOW = 20
LIQ_MIN_AMT = 2.0e7                    # the 20e6 liquidity gate the book uses
MIN_POOL = 100                         # a date needs this many ranked names to be read
DRAWS = 200
PHASES = (0, 5, 10, 15)
BARS_PER_YEAR = 252.0

# frozen verdict thresholds (echoed into every artifact)
GATE_PP = 1.0                          # pp/yr over the pool the arm must add
MAX_P = 0.05
REQUIRE_FOUR_OF_FOUR = True


# --------------------------------------------------------------------------- #
# construction
# --------------------------------------------------------------------------- #
def market_return(close: np.ndarray, etf: np.ndarray | None = None) -> np.ndarray:
    """Market leg in bars.  When an ETF series is supplied it is used as-is;
    otherwise the equal-weight pool return stands in (disclosed by the caller)."""
    if etf is not None:
        r = np.full(len(etf), np.nan)
        r[1:] = etf[1:] / etf[:-1] - 1.0
        return r
    rm = np.full_like(close, np.nan)
    rm[1:] = close[1:] / close[:-1] - 1.0
    return np.nanmean(rm, axis=1)


def salience_weighted(close: np.ndarray, mkt: np.ndarray, w: int = WINDOW):
    """Trailing sum of salience * return.  A window must be COMPLETE: a name with
    fewer than w priced bars carries no factor (a partial window is a different
    construct, not a shorter one)."""
    T = close.shape[0]
    r = np.full_like(close, np.nan)
    r[1:] = close[1:] / close[:-1] - 1.0
    m = mkt.reshape(-1, 1)
    with np.errstate(invalid="ignore", divide="ignore"):
        sal = np.abs(r - m) / (np.abs(r) + np.abs(m) + 0.1)
    wr = sal * r
    ok = np.isfinite(wr)
    cw = np.cumsum(np.where(ok, wr, 0.0), axis=0)
    co = np.cumsum(ok.astype(np.int32), axis=0)
    F = np.full_like(close, np.nan)
    if T > w:
        tot = cw[w:] - cw[:-w]
        cnt = co[w:] - co[:-w]
        full = cnt == w
        blk = np.where(full, tot, np.nan)
        F[w:] = blk
    return F, r


def forward_matrix(open_: np.ndarray, h: int) -> np.ndarray:
    """fwd[t] = open[t+1+h] / open[t+1] - 1.  Entry is one bar after the decision,
    exit h bars after entry -- there is no same-bar fill anywhere."""
    T = open_.shape[0]
    F = np.full_like(open_, np.nan)
    n = T - h - 1
    if n > 0:
        F[:n] = open_[1 + h:1 + h + n] / open_[1:1 + n] - 1.0
    return F


def liquidity(amount: np.ndarray, w: int = LIQ_WINDOW) -> np.ndarray:
    """Trailing mean traded value; bars before a full window are not liquid."""
    A = np.where(np.isfinite(amount), amount, np.nan)
    T = A.shape[0]
    out = np.full_like(A, np.nan)
    if T >= w:
        cs = np.nancumsum(np.where(np.isfinite(A), A, 0.0), axis=0)
        cc = np.cumsum(np.isfinite(A).astype(np.int32), axis=0)
        tot = cs[w - 1:]
        cnt = cc[w - 1:]
        with np.errstate(invalid="ignore", divide="ignore"):
            out[w - 1:] = np.where(cnt >= w, tot / np.maximum(cnt, 1), np.nan)
    return out


def pool_reading(F: np.ndarray, fwd: np.ndarray, liq: np.ndarray, t: int,
                 min_pool: int = MIN_POOL, decile: float = DECILE):
    """One date's cross-section: the candidate pool, the bottom decile, the top decile."""
    row = F[t]
    cand = np.isfinite(row) & np.isfinite(fwd[t]) & (liq[t] >= LIQ_MIN_AMT)
    n = int(cand.sum())
    if n < min_pool:
        return None
    idx = np.flatnonzero(cand)
    order = idx[np.argsort(row[idx], kind="stable")]
    k = max(1, int(round(n * decile)))
    low = fwd[t, order[:k]]
    high = fwd[t, order[-k:]]
    pool = fwd[t, order]
    return {"n": n, "k": k, "low": low, "high": high, "pool": pool, "order": order}


def cohort_readings(F: np.ndarray, fwd: np.ndarray, liq: np.ndarray, h: int,
                    phase: int = 0, cost_mul: float = 1.0):
    """Non-overlapping cohorts from `phase`; returns the per-cohort excess series."""
    T = F.shape[0]
    lows, highs, pools, excess = [], [], [], []
    for t in range(phase, max(phase, T - h - 1), h):
        r = pool_reading(F, fwd, liq, t)
        if r is None:
            continue
        lo = float(np.mean(r["low"]))
        hi = float(np.mean(r["high"]))
        pl = float(np.mean(r["pool"]))
        lows.append(lo)
        highs.append(hi)
        pools.append(pl)
        excess.append(lo - pl - 2.0 * Z.COST_PER_SIDE * cost_mul)
    return {
        "n_cohorts": len(excess),
        "low_mean": float(np.mean(lows)) if lows else float("nan"),
        "high_mean": float(np.mean(highs)) if highs else float("nan"),
        "pool_mean": float(np.mean(pools)) if pools else float("nan"),
        "excess_series": excess,
    }


def annualise(per_cohort: float, h: int) -> float:
    return per_cohort * (BARS_PER_YEAR / float(h))


def equity_stats(series, h: int) -> dict:
    a = np.asarray(series, dtype=float)
    if a.size == 0:
        return {"n": 0}
    eq = np.cumprod(1.0 + a)
    years = a.size * h / BARS_PER_YEAR
    cagr = float(eq[-1] ** (1.0 / years) - 1.0) if years > 0 and eq[-1] > 0 else float("nan")
    sd = float(np.std(a, ddof=1)) if a.size > 1 else float("nan")
    sharpe = float(np.mean(a) / sd * np.sqrt(BARS_PER_YEAR / h)) if sd and sd > 0 else float("nan")
    peak = np.maximum.accumulate(np.concatenate([[1.0], eq]))
    dd = float((eq / peak[1:] - 1.0).min())
    return {"n": int(a.size), "cagr": cagr, "sharpe": sharpe, "maxdd": dd}


def null_p(F: np.ndarray, fwd: np.ndarray, liq: np.ndarray, h: int, phase: int,
           observed: float, draws: int = DRAWS, seed: int = 850085):
    """Random equal-size draws from the same pool.  The statistic is
    draw-minus-pool minus the same two-sided cost, so a draw of the whole pool
    returns exactly -2*cost, not zero: the null prices the same trade."""
    rng = np.random.default_rng(seed)
    T = F.shape[0]
    stats = []
    for t in range(phase, max(phase, T - h - 1), h):
        r = pool_reading(F, fwd, liq, t)
        if r is None:
            continue
        pool = r["pool"]
        k = r["k"]
        for _ in range(draws):
            pick = rng.choice(pool.size, size=k, replace=False)
            stats.append(float(np.mean(pool[pick])) - float(np.mean(pool))
                         - 2.0 * Z.COST_PER_SIDE)
    arr = np.asarray(stats, dtype=float)
    if arr.size == 0:
        return {"draws": 0, "p_two_sided": float("nan"), "mean": float("nan")}
    ge = int((np.abs(arr) >= abs(observed)).sum())
    return {
        "draws": int(arr.size),
        "per_cohort_draws": draws,
        "mean": float(arr.mean()),
        "sd": float(arr.std(ddof=1)) if arr.size > 1 else 0.0,
        "p_two_sided": float((ge + 1) / (arr.size + 1)),
        "p_floor": float(1.0 / (arr.size + 1)),
    }


def decide(overall: dict, phases: dict, null: dict) -> dict:
    conds = {
        "long_excess_over_gate": overall["x1_excess_pp"] > GATE_PP,
        "four_phases_positive": all(v["x1_excess_pp"] > 0 for v in phases.values())
                                if REQUIRE_FOUR_OF_FOUR else True,
        "beats_null": bool(np.isfinite(null["p_two_sided"]) and null["p_two_sided"] <= MAX_P),
        "survives_x3_cost": overall["x3_excess_pp"] > 0,
    }
    return {
        "verdict": "ADMIT_TO_PREREG" if all(conds.values()) else "REFUSE_AS_CANDIDATE",
        "conditions": conds,
        "thresholds": {"gate_pp": GATE_PP, "max_p": MAX_P,
                       "four_of_four": REQUIRE_FOUR_OF_FOUR},
        "note": "supply verdict only: it buys a frozen prereg and a judge, "
                "never a money claim",
    }


def build(panel=None, etf_close=None) -> dict:
    if panel is None:
        panel = Z.load_panel(start=START)
    close = panel["close"]
    if etf_close is None:
        etf_close = _read_etf(ETF_510300, panel["dates"])
    mkt = market_return(close, etf_close)
    F, _ = salience_weighted(close, mkt, WINDOW)
    liq = liquidity(panel["amount"])

    out = {
        "artifact": "zoo85_salience_panic supply berth probe",
        "machine": os.environ.get("BM_MACHINE") or _machine(),
        "ts": _now(),
        "evidence_cutoff": _cutoff(panel),
        "family": "zoo85_salience_panic",
        "batch": "SUPPLY_BERTH_STOCK_FACTOR",
        "construct": {
            "salience": "|r_i - r_m| / (|r_i| + |r_m| + 0.1)",
            "factor": "trailing %d-bar sum of salience * r_i (complete windows only)" % WINDOW,
            "rank": "ascending; bottom decile = least-chased names",
            "market_leg": "510300 close-to-close" if etf_close is not None
                          else "equal-weight pool close-to-close (fallback)",
            "entry": "next bar open, exit h bars later open",
            "cost_per_side": Z.COST_PER_SIDE,
            "liq_gate": "trailing %d-bar mean amount >= %.0f" % (LIQ_WINDOW, LIQ_MIN_AMT),
        },
        "panel": {"n_symbols": int(close.shape[1]), "bars": int(close.shape[0]),
                  "first_bar": panel["dates"][0], "last_bar": panel["dates"][-1]},
        "horizons": {},
    }

    for h in HORIZONS:
        fwd = forward_matrix(panel["open"], h)
        per_phase = {}
        for ph in PHASES:
            rd = cohort_readings(F, fwd, liq, h, ph)
            if rd["n_cohorts"] == 0:
                per_phase["p%d" % ph] = {"n_cohorts": 0}
                continue
            xs = rd["excess_series"]
            per_phase["p%d" % ph] = {
                "n_cohorts": rd["n_cohorts"],
                "low_mean": rd["low_mean"],
                "high_mean": rd["high_mean"],
                "pool_mean": rd["pool_mean"],
                "spread_gross": rd["high_mean"] - rd["low_mean"],
                "x1_excess_pp": annualise(float(np.mean(xs)), h) * 100.0,
                "x1_equity": equity_stats([v + 2.0 * Z.COST_PER_SIDE for v in xs], h),
            }
        x1 = [v["x1_excess_pp"] for v in per_phase.values() if v.get("n_cohorts")]
        x3_rd = cohort_readings(F, fwd, liq, h, 0, cost_mul=3.0)
        x3_pp = (annualise(float(np.mean(x3_rd["excess_series"])), h) * 100.0
                 if x3_rd["n_cohorts"] else float("nan"))
        overall = {
            "x1_excess_pp": float(np.mean(x1)) if x1 else float("nan"),
            "x3_excess_pp": float(x3_pp),
            "phases_positive": int(sum(1 for v in x1 if v > 0)),
            "n_phases": len(x1),
        }
        block = {"phases": per_phase, "overall": overall}
        if h == PRIMARY_H:
            block["null"] = null_p(F, fwd, liq, h, 0, overall["x1_excess_pp"] / 100.0
                                   * (h / BARS_PER_YEAR))
            block["verdict_block"] = decide(overall, per_phase, block["null"])
        out["horizons"]["h%d" % h] = block

    out["honest"] = [
        "probe only: one window, one decile, no grid. A positive here buys a frozen "
        "prereg and a judge, not a claim that the factor pays.",
        "the pool control is the same denominator zoo #93 used; it is the honest "
        "comparison because the factor picks from that pool, not from the index",
        "the market leg is 510300, the in-house priced proxy for the registry's 中证全指; "
        "a different market leg changes the salience weights slightly, not the sign of "
        "the construct",
        "the short decile is reported for context and is NOT part of the verdict: a "
        "single A-share cannot be shorted here",
        "the panel is today's list applied to history (survivor caveat), unchanged from "
        "every other berth probe in this repo",
        "no look-ahead by construction: factor uses bars up to t, entry is t+1 open",
    ]
    return out


# --------------------------------------------------------------------------- #
# io
# --------------------------------------------------------------------------- #
def _read_etf(path: str, dates) -> np.ndarray | None:
    """510300 closes aligned to the panel's bar axis; None when the file is absent."""
    if not os.path.exists(path):
        return None
    import pandas as pd
    df = pd.read_csv(path)
    col = "date" if "date" in df.columns else df.columns[0]
    ccol = "close" if "close" in df.columns else df.columns[4]
    d = df[col].astype(str).str.slice(0, 10)
    c = pd.to_numeric(df[ccol], errors="coerce")
    ser = pd.Series(c.to_numpy(), index=d.to_numpy())
    ser = ser[~ser.index.duplicated(keep="last")]
    aligned = ser.reindex(dates)
    arr = aligned.to_numpy(dtype=float)
    if not np.isfinite(arr).any():
        return None
    return arr


def _cutoff(panel) -> str:
    return panel["dates"][-1]


def _machine() -> str:
    try:
        with open(os.path.join(ROOT, "fleet", "machine.json"), encoding="utf-8") as fh:
            return json.load(fh).get("machine_id", "unknown")
    except Exception:
        return "unknown"


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def run() -> int:
    out = build()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1, sort_keys=True)
    p = out["panel"]
    print("[zoo85] panel %d symbols x %d bars (%s..%s)" % (
        p["n_symbols"], p["bars"], p["first_bar"], p["last_bar"]))
    for name, blk in sorted(out["horizons"].items()):
        o = blk["overall"]
        print("[zoo85] %s x1 %+0.2f pp/yr (x3 %+0.2f) phases+ %d/%d" % (
            name, o["x1_excess_pp"], o["x3_excess_pp"],
            o["phases_positive"], o["n_phases"]))
        if "null" in blk:
            print("[zoo85]   null p=%.4f (draws %d)  verdict %s conds=%s" % (
                blk["null"]["p_two_sided"], blk["null"]["draws"],
                blk["verdict_block"]["verdict"], blk["verdict_block"]["conditions"]))
    print("[zoo85] receipt %s" % os.path.relpath(OUT, ROOT))
    return 0


# --------------------------------------------------------------------------- #
# selftest
# --------------------------------------------------------------------------- #
def _synth(nT=420, nS=140, seed=11, inject=False):
    """Hermetic panel.  `inject` gives the LOW half a persistent negative-salience
    drift: those names rise on quiet bars and fall on loud ones, so the
    salience-weighted sum sorts them apart from the high half."""
    rng = np.random.default_rng(seed)
    close = np.cumprod(1.0 + rng.normal(0.0, 0.01, size=(nT, nS)), axis=0) * 10.0
    if inject:
        loud = np.zeros(nT, dtype=bool)
        loud[::10] = True
        for j in range(nS):
            if j < nS // 2:
                # the crowd's dumping ground: loud crashes on noisy bars, quiet drift up
                drift = np.where(loud, -0.05, 0.008)
            else:
                # the crowd's darling: loud spikes, quiet bleed
                drift = np.where(loud, 0.05, -0.008)
            close[:, j] = 10.0 * np.cumprod(1.0 + drift)
    open_ = close * 1.0
    amount = np.full_like(close, 5.0e7)
    return {
        "dates": ["d%04d" % i for i in range(nT)],
        "symbols": ["s%03d" % j for j in range(nS)],
        "open": open_,
        "close": close,
        "turn": np.full_like(close, 1.0),
        "volume": np.full_like(close, 1.0e6),
        "amount": amount,
    }


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

    def l_market_shape():
        p = _synth(30, 5)
        m = market_return(p["close"])
        assert m.shape == (30,), m.shape
        assert np.isnan(m[0]) and np.isfinite(m[-1])

    def l_factor_needs_full_window():
        p = _synth(40, 6)
        F, _ = salience_weighted(p["close"], market_return(p["close"]), 10)
        assert np.isnan(F[:10]).all(), "bars before a complete window must stay NaN"
        assert np.isfinite(F[10]).any(), "a complete window must produce a factor"

    def l_forward_no_same_bar():
        p = _synth(30, 4)
        fwd = forward_matrix(p["open"], 5)
        assert np.isnan(fwd[-6:]).all(), "the last h+1 bars cannot have a forward return"
        manual = p["open"][6, 0] / p["open"][1, 0] - 1.0
        assert abs(fwd[0, 0] - manual) < 1e-12, (fwd[0, 0], manual)

    def l_liquidity_gate():
        p = _synth(60, 5)
        a = p["amount"].copy()
        a[:, 0] = 1.0e5
        liq = liquidity(a, 20)
        assert np.isnan(liq[:19]).all(), "a partial window is not liquid"
        assert liq[19, 0] < LIQ_MIN_AMT and liq[19, 1] >= LIQ_MIN_AMT

    def l_pool_reading_orders_ascending():
        p = _synth(40, 200)
        F, _ = salience_weighted(p["close"], market_return(p["close"]), 5)
        fwd = forward_matrix(p["open"], 2)
        liq = liquidity(p["amount"], 5)
        r = pool_reading(F, fwd, liq, 30, min_pool=50, decile=0.1)
        assert r is not None, "a 200-name panel must be readable"
        vals = F[30, r["order"]]
        assert np.all(np.diff(vals) >= -1e-15), "the order must be ascending by factor"
        assert r["k"] == 20, r["k"]

    def l_cost_is_charged_twice():
        p = _synth(60, 200)
        F, _ = salience_weighted(p["close"], market_return(p["close"]), 5)
        fwd = forward_matrix(p["open"], 5)
        liq = liquidity(p["amount"], 5)
        a = cohort_readings(F, fwd, liq, 5, 0, cost_mul=1.0)
        b = cohort_readings(F, fwd, liq, 5, 0, cost_mul=3.0)
        assert a["n_cohorts"] > 0 and a["n_cohorts"] == b["n_cohorts"]
        d = (np.mean(a["excess_series"]) - np.mean(b["excess_series"]))
        assert abs(d - 4.0 * Z.COST_PER_SIDE) < 1e-12, d

    def l_injected_signal_is_read():
        p = _synth(420, 160, seed=3, inject=True)
        F, _ = salience_weighted(p["close"], market_return(p["close"]), 20)
        fwd = forward_matrix(p["open"], 20)
        liq = liquidity(p["amount"], 20)
        rd = cohort_readings(F, fwd, liq, 20, 0, cost_mul=0.0)
        assert rd["n_cohorts"] > 0
        # low-salience half drifts up on quiet bars: its forward return must exceed
        # the high half, and the pool must sit between them
        assert rd["low_mean"] > rd["high_mean"], (rd["low_mean"], rd["high_mean"])
        assert min(rd["low_mean"], rd["high_mean"]) <= rd["pool_mean"] <= max(
            rd["low_mean"], rd["high_mean"]), rd["pool_mean"]

    def l_null_is_centred_on_the_cost():
        p = _synth(120, 200)
        F, _ = salience_weighted(p["close"], market_return(p["close"]), 5)
        fwd = forward_matrix(p["open"], 5)
        liq = liquidity(p["amount"], 5)
        nl = null_p(F, fwd, liq, 5, 0, 0.0, draws=5)
        assert nl["draws"] > 0
        exp = -2.0 * Z.COST_PER_SIDE
        # sampling error of a 20-of-200 draw is real; the centre must still be the cost
        assert abs(nl["mean"] - exp) < 2e-3, (nl["mean"], exp)

    def l_min_pool_refuses():
        p = _synth(40, 40)
        F, _ = salience_weighted(p["close"], market_return(p["close"]), 5)
        fwd = forward_matrix(p["open"], 2)
        liq = liquidity(p["amount"], 5)
        assert pool_reading(F, fwd, liq, 30, min_pool=100) is None

    def l_equity_stats_censor_free():
        st = equity_stats([0.01, -0.005, 0.002], 20)
        assert st["n"] == 3 and st["maxdd"] <= 0.0
        assert equity_stats([], 20)["n"] == 0

    def l_verdict_refuses_on_empty():
        blk = decide({"x1_excess_pp": float("nan"), "x3_excess_pp": float("nan")},
                     {}, {"p_two_sided": float("nan")})
        assert blk["verdict"] == "REFUSE_AS_CANDIDATE", blk["verdict"]
        assert blk["conditions"]["beats_null"] is False

    def l_determinism():
        p = _synth(200, 120, seed=5)
        F1, _ = salience_weighted(p["close"], market_return(p["close"]), 10)
        F2, _ = salience_weighted(p["close"], market_return(p["close"]), 10)
        assert np.array_equal(np.nan_to_num(F1, nan=-9.0), np.nan_to_num(F2, nan=-9.0))

    leg("market return shape", l_market_shape)
    leg("factor requires a complete window", l_factor_needs_full_window)
    leg("forward matrix has no same-bar entry", l_forward_no_same_bar)
    leg("liquidity gate needs a full window", l_liquidity_gate)
    leg("pool reading orders ascending", l_pool_reading_orders_ascending)
    leg("two sides of cost are charged", l_cost_is_charged_twice)
    leg("injected salience signal is read", l_injected_signal_is_read)
    leg("null is centred on the cost", l_null_is_centred_on_the_cost)
    leg("min pool refuses a thin date", l_min_pool_refuses)
    leg("equity stats on a short series", l_equity_stats_censor_free)
    leg("verdict refuses when nothing measured", l_verdict_refuses_on_empty)
    leg("determinism", l_determinism)

    for f in fail:
        print("[FAIL] %s" % f)
    print("selftest %d/%d PASS" % (ok, ok + len(fail)))
    return 0 if not fail else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run", choices=("run", "selftest"))
    ap.add_argument("--selftest", action="store_true",
                    help="same as the `selftest` subcommand (suite contract)")
    ap.add_argument("--max-symbols", type=int, default=0)
    args = ap.parse_args()
    if args.selftest or args.cmd == "selftest":
        return selftest()
    return run()


if __name__ == "__main__":
    raise SystemExit(main())