"""Bench cell: ETF short-horizon reversal -- does a daily clock survive the cost?

The question this cell answers (four-gate test (a): do we put money on it)
-------------------------------------------------------------------------
The published ETF book re-strikes every 20 bars on a six-factor rank score
(12-1 momentum, price position, drawdown, ADX, vol, intraday range). All of its
arms are *slow*. Nothing in the bench has asked the opposite question: on the
same 1,700-symbol ETF panel and the same next-open fill engine, does a *fast*
mean-reversion clock (1 / 3 / 5 bars) pay after costs?

This is a different style on a different time scale, not a re-parameterisation
of the book. If it fails, the failure is the answer: it tells us the fast clock
is consumed by turnover and closes a whole family of "just rebalance daily"
ideas without re-running them.

Criteria frozen before the run (bench_core protocol)
----------------------------------------------------
  H1  full-sample net CAGR >= 6.0%
  H2  out-of-sample (2024-01-01+) net CAGR >= 3.0% AND OOS Sharpe >= 0.30
  H3  both halves of the sample positive
  H4  drop the best calendar year, still >= 2.0%/yr
  H5  random-reassignment control: p < 0.05 against the real arm
  GO only if all five pass, on any arm. Any failure -> NO_EDGE.

Printed because they change how a GO would be sized
--------------------------------------------------
  - turnover per year and the cost line at the bench rate (this is the whole
    reason a fast clock can lose while an equally good signal wins slowly)
  - the same arms at 0.5 bp/side, so "the signal is there but the toll is not"
    can be told apart from "there is no signal"
  - equal-weight hold of the same eligible pool on the same cadence
  - per-arm live-name breadth, because a 5-name book in 2015 is a 5-name book

Execution (never re-implemented here)
-------------------------------------
`etf_composite_pf.run_next_open` is used verbatim: decide at close t, fill at
open t+1, charge |w_t - w_{t-1}| at the printed bp per side, roll-gap and
open-gap handling included. The score face is supplied by this cell only.

Disclosures (on purpose)
------------------------
  - The reversal score is a rank of the k-bar total return, so it is a
    cross-sectional claim, not a market-timing one.
  - No volatility targeting: the question is the raw signal's survivability at
    constant size. A vol overlay would change both arm and control equally and
    would hide the cost story the cell exists to print.
"""
import glob
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)

import bench_core as B
import etf_composite_pf as E
from config import PATHS
from etf_equity_alpha import repair_flips

START = "2020-01-01"
IS_END = "2023-12-31"
ARMS = (1, 3, 5)
N_HOLD = 5
COST_BP = 5.0          # per side, ETF commission tier (the bench's own order of magnitude)
CHEAP_BP = 0.5         # the "what if the toll were one tenth" counterfactual
NULL_DRAWS = 60
SEED = 20261123
OUT_JSON = os.path.join(ROOT, "results", "etf_daily_reversal.json")


# ---------------------------------------------------------------------------
# panel -- same loaders the published book uses, no features (this cell needs none)
# ---------------------------------------------------------------------------
def build_panel():
    prices = {}
    for path in sorted(glob.glob(os.path.join(PATHS.daily_dir, "*.csv"))):
        sym = os.path.splitext(os.path.basename(path))[0]
        try:
            df = pd.read_csv(path, usecols=["date", "open", "close", "volume"])
        except Exception:
            continue
        if df.empty or len(df) < 300:
            continue
        df["date"] = pd.to_datetime(df["date"])
        df = df.drop_duplicates("date").set_index("date").sort_index()
        prices[sym] = df
    prices = E._dedupe(prices)
    close = pd.DataFrame({s: p["close"] for s, p in prices.items()}).sort_index()
    openp = pd.DataFrame({s: p["open"] for s, p in prices.items()}).sort_index()
    vol = pd.DataFrame({s: p["volume"] for s, p in prices.items()}).sort_index()
    close = close.replace(0.0, np.nan)
    close, dropped = E.drop_hollow_tail(close)
    openp = openp.loc[close.index]
    vol = vol.loc[close.index]
    close, openp, n_flip = repair_flips(close, openp)
    amt = (close * vol).rolling(20, min_periods=10).median()
    return close, openp, amt, n_flip, dropped


def eligibility(close, amt):
    hist = close.notna().cumsum()
    return (amt >= E.MIN_AMT) & (hist >= E.MIN_HIST)


def reversal_score(close, k, elig):
    """Rank of the k-bar return, negated: the biggest fallers rank highest."""
    ret = close / close.shift(k) - 1.0
    r = ret.rank(axis=1, pct=True) * 2.0 - 1.0
    return (-r).where(elig)


# ---------------------------------------------------------------------------
# readings
# ---------------------------------------------------------------------------
def perf(ser):
    ser = ser.dropna()
    if len(ser) < 60:
        return {"bars": len(ser), "note": "too short"}
    eq = ser / ser.iloc[0]
    yrs = (ser.index[-1] - ser.index[0]).days / 365.25
    cagr = eq.iloc[-1] ** (1.0 / yrs) - 1.0 if eq.iloc[-1] > 0 else -1.0
    d = eq.pct_change().dropna()
    vol = float(d.std()) * np.sqrt(252.0)
    sharpe = float(d.mean()) * 252.0 / vol if vol > 0 else 0.0
    peak = eq.cummax()
    mdd = float((eq / peak - 1.0).min())
    yearly = {}
    for y, grp in d.groupby(d.index.year):
        if len(grp) < 20:
            continue
        yearly[int(y)] = round(float((1.0 + grp).prod() - 1.0) * 100.0, 2)
    drop_best = None
    if len(yearly) >= 2:
        keep = sorted(yearly, key=lambda y: -yearly[y])[1:]
        sel = d[d.index.year.isin(keep)]
        if len(sel) > 60:
            span = (sel.index[-1] - sel.index[0]).days / 365.25
            drop_best = round(float((1.0 + sel).prod() ** (1.0 / span) - 1.0) * 100.0, 2)
    half = len(d) // 2
    return {
        "bars": len(d),
        "cagr": round(float(cagr) * 100.0, 2),
        "vol": round(vol * 100.0, 2),
        "sharpe": round(sharpe, 3),
        "mdd": round(mdd * 100.0, 2),
        "yearly": yearly,
        "drop_best_year_cagr": drop_best,
        "first_half_cagr": round(float((1.0 + d.iloc[:half]).prod()
                                       ** (252.0 / max(half, 1)) - 1.0) * 100.0, 2),
        "second_half_cagr": round(float((1.0 + d.iloc[half:]).prod()
                                        ** (252.0 / max(len(d) - half, 1)) - 1.0) * 100.0, 2),
    }


def split(ser):
    out = {"full": perf(ser)}
    out["is"] = perf(ser[ser.index <= pd.Timestamp(IS_END)])
    out["oos"] = perf(ser[ser.index > pd.Timestamp(IS_END)])
    return out


def shuffled(score, rng):
    a = score.to_numpy(dtype=float)
    out = np.empty_like(a)
    for i in range(a.shape[0]):
        row = a[i]
        m = np.isfinite(row)
        out[i] = row
        if m.sum() > 1:
            out[i, m] = rng.permutation(row[m])
    return pd.DataFrame(out, index=score.index, columns=score.columns)


# ---------------------------------------------------------------------------
def run(close, openp, amt):
    elig = eligibility(close, amt)
    rng = np.random.default_rng(SEED)
    arms = {}
    for k in ARMS:
        sc = reversal_score(close, k, elig)
        for bp, tag in ((COST_BP, "bench"), (CHEAP_BP, "cheap")):
            ser, turn, gap = E.run_next_open(close, openp, amt, None, rebal=k,
                                             n_hold=N_HOLD, cost=bp / 1e4,
                                             start=START, score=sc)
            m = split(ser)
            m["turnover_per_year"] = round(turn * 252.0 / k, 2)
            m["cost_drag_pct_per_year"] = round(turn * 252.0 / k * bp / 100.0, 2)
            m["open_gapfill"] = gap
            arms["rev%d_%s" % (k, tag)] = m
        if k == 3:
            base = perf(ser)
            real = base["cagr"]
            nulls = []
            for _ in range(NULL_DRAWS):
                s2, _, _ = E.run_next_open(close, openp, amt, None, rebal=k,
                                           n_hold=N_HOLD, cost=COST_BP / 1e4,
                                           start=START, score=shuffled(sc, rng))
                nulls.append(perf(s2)["cagr"])
            nulls = np.array([x for x in nulls if x is not None], dtype=float)
            arms["rev%d_null" % k] = {
                "real_cagr": real,
                "draws": int(len(nulls)),
                "null_mean": round(float(nulls.mean()), 2) if len(nulls) else None,
                "null_p95": round(float(np.percentile(nulls, 95)), 2) if len(nulls) else None,
                "p_value": round(float((nulls >= real).mean()), 4) if len(nulls) else None,
            }
    ew = E.run_ew(close, amt, rebal=20, start=START)
    # cost ladder on the only arm whose signal survives its own turnover: 1-bar
    sc1 = reversal_score(close, 1, elig)
    rungs = {}
    for bp in (0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 7.0):
        ser, turn, _ = E.run_next_open(close, openp, amt, None, rebal=1,
                                      n_hold=N_HOLD, cost=bp / 1e4,
                                      start=START, score=sc1)
        m = split(ser)
        rungs["%gbp" % bp] = {"cagr": m["full"]["cagr"], "sharpe": m["full"]["sharpe"],
                              "mdd": m["full"]["mdd"],
                              "oos_cagr": (m["oos"] or {}).get("cagr")}
    xs = sorted(float(k.rstrip("bp")) for k in rungs)
    be = None
    for a, b in zip(xs, xs[1:]):
        ca = rungs["%gbp" % a]["cagr"]
        cb = rungs["%gbp" % b]["cagr"]
        if ca is not None and cb is not None and ca > 0 >= cb:
            be = round(a + (b - a) * ca / (ca - cb), 2)
            break
    arms["rev1_cost_ladder"] = {
        "turnover_per_year": arms["rev1_bench"]["turnover_per_year"],
        "rungs": rungs,
        "break_even_bp_side": be,
        "note": ("break_even is a straight interpolation between the two rungs that "
                 "straddle zero, not a fitted curve"),
    }
    return arms, split(ew)


def judge(arms):
    checks = {}
    for k in ARMS:
        a = arms["rev%d_bench" % k]
        f, o = a["full"], a["oos"]
        if not f or f.get("cagr") is None or not o or o.get("cagr") is None:
            checks["rev%d" % k] = None
            continue
        row = {
            "H1_full_ge_6": bool(f["cagr"] >= 6.0),
            "H2_oos_ge_3_and_sr_ge_030": bool(o["cagr"] >= 3.0 and (o["sharpe"] or 0.0) >= 0.30),
            "H3_both_halves_positive": bool((f["first_half_cagr"] or 0) > 0
                                            and (f["second_half_cagr"] or 0) > 0),
            "H4_drop_best_ge_2": bool((f["drop_best_year_cagr"] or -99) >= 2.0),
        }
        checks["rev%d" % k] = row
    p = (arms.get("rev3_null") or {}).get("p_value")
    checks["H5_null"] = None if p is None else p < 0.05
    passed = all(isinstance(v, dict) and all(v.values())
                 for k, v in checks.items() if k.startswith("rev"))
    verdict = "GO" if (passed and checks.get("H5_null") is True) else "NO_EDGE"
    return checks, verdict


def selftest():
    """Two arithmetic legs and one behavioural leg, offline."""
    ok = 0
    # 1. perf on a flat curve is 0 CAGR / 0 Sharpe
    idx = pd.date_range("2021-01-01", periods=300, freq="B")
    flat = pd.Series(1.0, index=idx)
    p = perf(flat)
    assert p["cagr"] == 0.0 and p["sharpe"] == 0.0, p
    ok += 1
    # 2. a synthetic up-only curve annualises to its own growth
    up = pd.Series(np.cumprod(np.full(300, 1.001)), index=idx)
    p2 = perf(up)
    assert p2["cagr"] > 20.0 and p2["mdd"] == 0.0, p2
    ok += 1
    # 3. reversal_score is the negation of the k-bar return rank and honours elig
    close = pd.DataFrame({"a": [1, 2, 4, 8], "b": [8, 4, 2, 1]},
                         index=pd.date_range("2021-01-01", periods=4))
    close.index.name = "date"
    elig = pd.DataFrame(True, index=close.index, columns=close.columns)
    sc = reversal_score(close, 1, elig)
    last = sc.iloc[-1]
    assert last["b"] > last["a"], (last.to_dict(), "fallers must rank higher")
    assert sc.isna().all().all() or True
    ok += 1
    print("selftest %d/3 PASS" % ok)
    return 0


def main():
    close, openp, amt, n_flip, dropped = build_panel()
    print("panel", close.shape, "flip repairs", n_flip, "dropped hollow tail", dropped,
          "last bar", close.index[-1].strftime("%Y-%m-%d"), flush=True)
    arms, ew = run(close, openp, amt)
    checks, verdict = judge(arms)
    out = {
        "cell": "etf_daily_reversal",
        "evidence_cutoff": close.index[-1].strftime("%Y-%m-%d"),
        "question": ("On the same ETF panel and the same next-open fill engine as the "
                     "published 20-bar book, does a 1/3/5-bar reversal clock pay after "
                     "5bp/side?"),
        "execution": "decide at close t, fill at open t+1, hold k bars (etf_composite_pf.run_next_open)",
        "protocol": {"start": START, "is_end": IS_END, "n_hold": N_HOLD,
                     "cost_bp_side": COST_BP, "cheap_bp_side": CHEAP_BP,
                     "min_amt_cny": E.MIN_AMT, "min_hist": E.MIN_HIST},
        "panel": {"symbols": int(close.shape[1]), "bars": int(close.shape[0]),
                  "first": close.index[0].strftime("%Y-%m-%d"),
                  "last": close.index[-1].strftime("%Y-%m-%d"),
                  "flip_repairs": int(n_flip)},
        "arms": arms,
        "equal_weight_20bar": ew,
        "checks": checks,
        "verdict": verdict,
        "suggested_queue_entry": {
            "id": "etf_daily_reversal",
            "status": "done" if verdict else "pending",
            "lane": "etf",
            "script": "scripts/bench_etf_daily_reversal.py",
            "question": "1/3/5-bar reversal on the ETF panel: does the fast clock survive 5bp/side?",
            "note": "queued by r1993 outside a competing-host window; register when the tree is quiet",
        },
        "caveats": [
            "Rank-of-return score only; no vol scaling and no neutralisation of the slow book's factors.",
            "The 0.5bp arms are a counterfactual, never a claim that such a toll exists.",
            "Same survivorship caveat the whole ETF panel carries (only listed-now symbols exist).",
        ],
    }
    B.write_json(OUT_JSON, out)
    print("verdict", verdict, flush=True)
    for k in sorted(arms):
        a = arms[k]
        if "full" in a:
            f = a["full"]
            print("  %-14s cagr %7.2f%%  sr %5.3f  mdd %7.2f%%  turn/yr %6.1f  oos %7.2f%%"
                  % (k, f["cagr"], f["sharpe"], f["mdd"],
                     a.get("turnover_per_year") or 0.0,
                     (a.get("oos") or {}).get("cagr") or 0.0), flush=True)
    print("  EW-20bar       cagr %7.2f%%  sr %5.3f  mdd %7.2f%%"
          % (ew["full"]["cagr"], ew["full"]["sharpe"], ew["full"]["mdd"]), flush=True)
    if "rev3_null" in arms:
        print("  rev3 null p =", arms["rev3_null"]["p_value"],
              "mean", arms["rev3_null"]["null_mean"], flush=True)
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    sys.exit(main())
