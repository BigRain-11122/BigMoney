"""Does the composite edge exist BEFORE the ETF universe existed?

Every published number for this book lives in 2020-01..2026-10, and the panel that
produces it contains 1,608 ETFs whose eligible cross-section grows from single digits
(2013) to ~720 names (2026). Two things could therefore be making the book look good:
the six-factor composite, or a 700-name cross-section full of funds that only exist
because the industry grew. This script separates those by pricing the SAME engine on
the SAME file panel over a period the published work never looked at.

Design (2x3, no re-implementation -- every cell rides scripts/etf_composite_pf.py):

  U_pre  = ETFs whose first bar is <= 2019-12-31 (they existed before the boom)
  U_all  = every ETF in data/daily

  cell A  U_pre x 2015-01-01..2019-12-31   the honest pre-period test
  cell B  U_pre x 2020-01-01..             same universe, published period
  cell C  U_all x 2020-01-01..             the published headline (repro check)

A vs B is the period question on a fixed universe; B vs C is the universe question on
a fixed period. Reading only one of them is how "the edge is real" and "the cross-
section is the edge" both get published from the same numbers.

Execution/costs are the production card's: decision at close t, fill at open t+1,
10bp per side on the weight actually turned over, top-N equal weight every R bars,
20d median amount >= 20M CNY and >= 120 bars of history to be eligible.

Honest limits carried in the artifact: (a) dead funds are missing from the panel, so
U_pre is itself survival-filtered -- a pre-period that fails while filtered is a
stronger negative than the same number on a complete universe, but a pre-period that
passes is weaker evidence than it looks; (b) a delisted name's price is forward-filled
inside the engine, so it stands still at zero return rather than at its liquidation
value; (c) the number of eligible names per decision is published beside every cell --
a top-5 choice out of 7 names is not a cross-section, it is the universe.

Exploratory: no preregistration, no verdict, no ledger booking, no member file touched.

Usage (cwd = repo root):
    python -m scripts.etf_book_pre2020 run
    python -m scripts.etf_book_pre2020 selftest
"""

import json
import os
import sys

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from scripts import etf_composite_pf as F  # noqa: E402
from engine.factors import compute_all  # noqa: E402

OUT_PATH = os.path.join(_REPO_ROOT, "results", "etf_book_pre2020.json")

NEEDLE = pd.Timestamp("2020-01-01")   # "existed before the boom" boundary
PRE_START = "2015-01-01"              # first year with a usable cross-section
PRE_END = "2019-12-31"
POST_START = "2020-01-01"

COST = 0.0010                         # production card per side
GRID_N = (3, 5, 8)
GRID_R = (10, 20)
PRIMARY_N = 5
PRIMARY_R = 20
NULL_ITER = 200


def _p(*a):
    """Flush-on-print: a piped stdout is block-buffered and would look like a hang."""
    print(*a)
    sys.stdout.flush()


def universe_pre(close, asof=NEEDLE):
    """Columns whose first valid bar is on/before `asof` -- i.e. funds that existed."""
    first = close.apply(lambda s: s.first_valid_index())
    return [c for c in close.columns if first.get(c) is not None and first[c] <= asof]


def truncate(frames, start=None, end=None):
    """Date-slice a run of date-indexed frames (DataFrame or {name: DataFrame})."""
    out = []
    for f in frames:
        if isinstance(f, dict):
            f = {k: v for k, v in f.items()}
            for k, v in f.items():
                f[k] = _slice(v, start, end)
        else:
            f = _slice(f, start, end)
        out.append(f)
    return out


def _slice(df, start, end):
    if df is None:
        return None
    if not isinstance(df.index, pd.DatetimeIndex):
        # engine/factors.compute_all ships one empty non-date frame (amt_20, 0x0) --
        # it is not date-sliceable and build_score reindexes it to all-NaN anyway.
        return df
    x = df
    if start is not None:
        x = x.loc[x.index >= pd.Timestamp(start)]
    if end is not None:
        x = x.loc[x.index <= pd.Timestamp(end)]
    return x


def eligibility_counts(close, amt, n_hold, rebal, start, end=None):
    """Eligible-name count on each decision date (the width of the cross-section).

    History is counted on the FULL frame and only the decision dates are bounded by the
    window: slicing the panel at `start` first would reset `notna().cumsum()` and make
    every name ineligible for its first 120 bars (the r1305 self-caught defect).
    """
    hist = close.notna().cumsum()
    elig = (amt >= F.MIN_AMT) & (hist >= F.MIN_HIST)
    if end is not None:
        elig = elig.loc[elig.index <= pd.Timestamp(end)]
    dates = [d for d in elig.index if d >= pd.Timestamp(start)]
    dec = dates[::rebal]
    counts = [int(elig.loc[d].sum()) for d in dec]
    if not counts:
        return {"decisions": 0, "median": 0, "min": 0, "max": 0,
                "thin_decisions": 0, "thin_rule": "< 2*n_hold names"}
    counts = np.array(counts)
    return {
        "decisions": len(counts),
        "median": int(np.median(counts)),
        "min": int(counts.min()),
        "max": int(counts.max()),
        "thin_decisions": int((counts < 2 * n_hold).sum()),
        "thin_rule": "fewer than 2*n_hold eligible names",
    }


def cell(close, openp, amt, feats, n_hold, rebal, start, end=None):
    """One priced cell: the book, its equal-weight control, and the cross-section width.

    Only the END is sliced out of the frames. The lower bound is passed to the engine as
    `start`, never applied to the panel, because eligibility carries a 120-bar history
    requirement -- cutting the panel at `start` would silently reset that counter and
    leave the book in cash for its first six months.
    """
    c, o, a, f = truncate([close, openp, amt, feats], None, end)
    ser, turnover, gapfill = F.run_next_open(
        c, o, a, f, rebal=rebal, n_hold=n_hold, cost=COST, start=start,
        min_amt=F.MIN_AMT, min_hist=F.MIN_HIST)
    m = F.metrics(ser, "book")
    # equal-weight control on the same eligible set: run_ew reads the module gate,
    # which is the same MIN_AMT/MIN_HIST this script holds constant -- one definition
    # of "eligible", never a copy.
    ew = F.run_ew(c, a, rebal, start=start)
    ew_m = F.metrics(ew, "ew")
    return {
        "book": m,
        "ew": ew_m,
        "excess_cagr_pp": round((m.get("cagr", 0.0) - ew_m.get("cagr", 0.0)) * 100, 2),
        "turnover_per_decision": round(turnover, 3),
        "open_gapfill": int(gapfill),
        "eligibility": eligibility_counts(close, amt, n_hold, rebal, start, end),
    }


def random_null(close, openp, amt, feats, n_hold, rebal, start, end=None,
                n_iter=NULL_ITER, seed=11):
    """Per-date random-score null: same engine, same eligibility, no factor information.

    A random score face is exactly a rank permutation of the composite in distribution,
    so this is the pick-randomly null without re-shuffling 1,700 rows x 200 rounds.
    """
    rng = np.random.default_rng(seed)
    c, o, a, f = truncate([close, openp, amt, feats], None, end)
    real_score = F.build_score(c, a, f)
    finite = np.isfinite(real_score.values)
    real_ser, _, _ = F.run_next_open(c, o, a, f, rebal=rebal, n_hold=n_hold,
                                     cost=COST, start=start, score=real_score)
    real_growth = F.metrics(real_ser, "book").get("cagr")
    if real_growth is None:
        return {"n_iter": 0, "p_value": None, "note": "real cell too short"}
    out = []
    for _ in range(n_iter):
        noise = pd.DataFrame(rng.random(real_score.shape),
                             index=real_score.index, columns=real_score.columns)
        noise = noise.where(finite)
        ser, _, _ = F.run_next_open(c, o, a, f, rebal=rebal, n_hold=n_hold,
                                    cost=COST, start=start, score=noise)
        g = F.metrics(ser, "null").get("cagr")
        out.append(np.nan if g is None else g)
    arr = np.array(out, dtype=float)
    arr = arr[np.isfinite(arr)]
    p = float((arr >= real_growth).mean()) if len(arr) else None
    return {
        "n_iter": int(len(arr)),
        "p_value": None if p is None else round(p, 3),
        "null_cagr_median": None if not len(arr) else round(float(np.median(arr)), 4),
        "null_cagr_p95": None if not len(arr) else round(float(np.percentile(arr, 95)), 4),
        "real_cagr": round(float(real_growth), 4),
    }


def control():
    """Price the published arm through this script's own call path and assert it.

    A cell is only readable if the arm it is compared against is the arm that was
    published. results/etf_composite_pf_open.json (8bp/side, next open, N5/R20) is the
    control; the comparison is done at its own cost so the difference can only be the
    engine path or the data cutoff, never the fee.
    """
    pub_path = os.path.join(_REPO_ROOT, "results", "etf_composite_pf_open.json")
    with open(pub_path, "r", encoding="utf-8") as fh:
        pub = json.load(fh)
    want = next(r for r in pub["runs"] if r["label"] == "nextopen_rebal20_full")
    want_ew = next(r for r in pub["runs"] if r["label"] == "ew_universe_rebal20_full")

    close, openp, amt, feats = F.build_panel()
    c, o, a, f = close, openp, amt, feats          # lower bound stays in the engine
    ser, _, _ = F.run_next_open(c, o, a, f, rebal=20, n_hold=5, cost=pub["cost_per_side"],
                                start=POST_START, min_amt=pub["min_amt_cny"],
                                min_hist=F.MIN_HIST)
    got = F.metrics(ser, "control")
    ew = F.metrics(F.run_ew(c, a, 20, start=POST_START), "control_ew")
    out = {
        "published_file": os.path.relpath(pub_path, _REPO_ROOT),
        "published_cutoff": pub["evidence_cutoff"],
        "this_cutoff": str(close.index[-1].date()),
        "published_cagr": want["cagr"],
        "recomputed_cagr": got.get("cagr"),
        "delta_pp": round((got.get("cagr", 0) - want["cagr"]) * 100, 2),
        "published_ew_cagr": want_ew["cagr"],
        "recomputed_ew_cagr": ew.get("cagr"),
        "ew_delta_pp": round((ew.get("cagr", 0) - want_ew["cagr"]) * 100, 2),
        "note": "recomputed on a panel three trading days longer than the published one; "
                "the deltas are the cost of that extra data, not a code difference",
    }
    _p("control: published %.4f vs recomputed %.4f (delta %+.2fpp); EW %.4f vs %.4f (%+.2fpp)"
       % (want["cagr"], got.get("cagr"), out["delta_pp"], want_ew["cagr"],
          ew.get("cagr"), out["ew_delta_pp"]))
    if os.path.exists(OUT_PATH):
        with open(OUT_PATH, "r", encoding="utf-8") as fh:
            doc = json.load(fh)
        doc["control"] = out
        with open(OUT_PATH, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, ensure_ascii=False, indent=1)
        _p("control block written into %s" % os.path.relpath(OUT_PATH, _REPO_ROOT))
    return out


def run():
    t0 = pd.Timestamp.now()
    close, openp, amt, feats = F.build_panel()
    pre_cols = universe_pre(close)
    universes = {"U_pre": pre_cols, "U_all": list(close.columns)}
    print("panel %s  U_pre=%d  U_all=%d"
          % (close.shape, len(pre_cols), len(universes["U_all"])))

    cells_spec = [
        ("A_pre_universe_pre_period", "U_pre", PRE_START, PRE_END),
        ("B_pre_universe_post_period", "U_pre", POST_START, None),
        ("C_full_universe_post_period", "U_all", POST_START, None),
    ]
    grids = {}
    for label, uni, start, end in cells_spec:
        cols = universes[uni]
        sub = truncate([close[cols], openp[cols], amt[cols],
                        {k: v.reindex(columns=cols) for k, v in feats.items()
                         if hasattr(v, "columns")}], None, None)
        c, o, a, f = sub
        rows = {}
        for n_hold in GRID_N:
            for rebal in GRID_R:
                rows["N%d_R%d" % (n_hold, rebal)] = cell(c, o, a, f, n_hold, rebal, start, end)
                _p("%s N%d_R%d cagr=%s sr=%s ew=%s"
                   % (label, n_hold, rebal, rows["N%d_R%d" % (n_hold, rebal)]["book"].get("cagr"),
                      rows["N%d_R%d" % (n_hold, rebal)]["book"].get("sharpe"),
                      rows["N%d_R%d" % (n_hold, rebal)]["ew"].get("cagr")))
        primary = rows["N%d_R%d" % (PRIMARY_N, PRIMARY_R)]
        _p("%s: running the %d-iteration random-score null ..." % (label, NULL_ITER))
        primary["null"] = random_null(c, o, a, f, PRIMARY_N, PRIMARY_R, start, end)
        grids[label] = {
            "universe": uni,
            "universe_size": len(cols),
            "start": start,
            "end": end or str(close.index[-1].date()),
            "cells": rows,
        }
        print("%-30s %-6s %d cols  primary N%d/R%d: cagr=%s sr=%s dd=%s ew=%s null_p=%s"
              % (label, uni, len(cols), PRIMARY_N, PRIMARY_R,
                 primary["book"].get("cagr"), primary["book"].get("sharpe"),
                 primary["book"].get("maxdd"), primary["ew"].get("cagr"),
                 primary["null"].get("p_value")))

    out = {
        "generated": t0.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_sec": round((pd.Timestamp.now() - t0).total_seconds(), 1),
        "evidence_cutoff": str(close.index[-1].date()),
        "schema": "etf_book_pre2020/v1",
        "question": "does the six-factor composite pay on the ETFs that existed before "
                    "2020, over a period the published book never looked at?",
        "engine": "scripts/etf_composite_pf.run_next_open (no re-implementation)",
        "basis": "close decision -> next open fill, %dbp per side, top-N equal weight"
                 % int(COST * 1e4),
        "universe_rule": "first bar <= 2020-01-01; eligible when 20d median amount "
                         ">= %.0fM and >= %d bars of history"
                         % (F.MIN_AMT / 1e6, F.MIN_HIST),
        "grid": {"n_hold": list(GRID_N), "rebal_bars": list(GRID_R),
                 "primary": "N%d_R%d" % (PRIMARY_N, PRIMARY_R)},
        "cells": grids,
        "honest_limits": [
            "the panel holds no delisted funds, so U_pre is survival-filtered too",
            "a dead name's price is forward-filled by the engine (zero return, not NAV exit)",
            "eligibility counts are published per cell: top-5 out of 7 names is not a cross-section",
            "no preregistration and no ledger booking -- this is a measurement, not a verdict",
        ],
    }
    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print("wrote %s in %.0fs" % (os.path.relpath(OUT_PATH, _REPO_ROOT), out["elapsed_sec"]))
    return out


# ---------------------------------------------------------------- selftest

def _fixture(n_sym=60, n_bars=1300, seed=5, late_from=800):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2012-01-02", periods=n_bars)
    prices = {}
    for k in range(n_sym):
        start = 0 if k % 2 == 0 else late_from          # half the names list late
        n = n_bars - start
        drift = rng.normal(0.0004, 0.0004)
        ret = rng.normal(drift, 0.011, n)
        close = 2.0 * np.cumprod(1 + ret)
        op = close * (1 + rng.normal(0, 0.002, n))
        vol = np.full(n, 2.5e7)
        df = pd.DataFrame({"open": op, "close": close, "volume": vol}, index=idx[start:])
        df["high"] = np.maximum(df["open"], df["close"]) * 1.004
        df["low"] = np.minimum(df["open"], df["close"]) * 0.996
        df["amount"] = df["close"] * df["volume"]
        prices["s%02d" % k] = df
    close = pd.DataFrame({s: p["close"] for s, p in prices.items()}).sort_index()
    openp = pd.DataFrame({s: p["open"] for s, p in prices.items()}).sort_index()
    vol = pd.DataFrame({s: p["volume"] for s, p in prices.items()}).sort_index()
    feats = compute_all(prices, None)
    amt = (close * vol).rolling(20, min_periods=10).median()
    return close, openp, amt, feats


def selftest():
    ok, fail = 0, 0

    def chk(name, cond, detail=""):
        nonlocal ok, fail
        if cond:
            ok += 1
            print("[PASS] %s | %s" % (name, detail))
        else:
            fail += 1
            print("[FAIL] %s | %s" % (name, detail))

    close, openp, amt, feats = _fixture()
    needle = close.index[700]
    pre = universe_pre(close, asof=needle)

    # L1 universe mask really binds
    chk("selftest: universe mask binds", 0 < len(pre) < len(close.columns),
        "U_pre=%d of %d" % (len(pre), len(close.columns)))
    chk("selftest: mask keeps the early names",
        all(close[s].first_valid_index() <= needle for s in pre),
        "max first bar %s" % max(close[s].first_valid_index() for s in pre).date())

    start = str(close.index[400].date())
    c, o, a, f = truncate([close, openp, amt, feats], start, None)

    # L2 the run actually trades (r1261: an equivalence check on a book that never
    #    trades passes trivially -- assert the mechanism fired before reading numbers)
    ser, turn, _ = F.run_next_open(c, o, a, f, rebal=20, n_hold=5, cost=COST, start=start)
    chk("selftest: run is active", turn > 0 and len(ser) > 100,
        "turnover=%.3f bars=%d" % (turn, len(ser)))

    # L3 cost monotonicity through this call path
    free, _, _ = F.run_next_open(c, o, a, f, rebal=20, n_hold=5, cost=0.0, start=start)
    pricey, _, _ = F.run_next_open(c, o, a, f, rebal=20, n_hold=5, cost=0.005, start=start)
    g_free = F.metrics(free, "f").get("cagr")
    g_pricey = F.metrics(pricey, "p").get("cagr")
    chk("selftest: cost is charged monotonically", g_free > g_pricey,
        "cagr 0bp=%.4f 50bp=%.4f" % (g_free, g_pricey))

    # L4 window bounds are respected on both ends
    ser2, _, _ = F.run_next_open(c, o, a, f, rebal=20, n_hold=5, cost=COST, start=start,
                                 score=F.build_score(c, a, f))
    chk("selftest: window start respected",
        ser2.index[0] >= pd.Timestamp(start), "first=%s" % ser2.index[0].date())
    c_end, o_end, a_end, f_end = truncate(
        [close, openp, amt, feats], str(close.index[600].date()),
        str(close.index[900].date()))
    ser3, _, _ = F.run_next_open(c_end, o_end, a_end, f_end, rebal=20, n_hold=5,
                                 cost=COST, start=str(close.index[600].date()))
    chk("selftest: window end respected", ser3.index[-1] <= close.index[900],
        "last=%s bound=%s" % (ser3.index[-1].date(), close.index[900].date()))

    # L5 eligibility counts see the thin cross-section rather than hiding it
    thin = eligibility_counts(close, amt, 5, 20, str(close.index[700].date()), None)
    chk("selftest: thin cross-section is counted", thin["decisions"] > 0,
        "median=%(median)d thin=%(thin_decisions)d/%(decisions)d" % thin)

    # L6b slicing the panel at `start` must NOT reset the eligibility history counter
    #     (the r1305 self-caught defect: a truncated panel left the book in cash for
    #     its first 120 bars, so every book cell under-read against its control)
    full_score = F.build_score(close, amt, feats)
    cut_c, cut_o, cut_a, cut_f = truncate([close, openp, amt, feats], start, None)
    cut_score = F.build_score(cut_c, cut_a, cut_f)
    first_live = [d for d in full_score.index if d >= pd.Timestamp(start)][60]
    n_full = int(full_score.loc[first_live].notna().sum())
    n_cut = int(cut_score.loc[first_live].notna().sum()) if first_live in cut_score.index else -1
    chk("selftest: window start does not reset the history counter",
        n_full > 0 and n_cut == 0,
        "eligible at %s: full-panel=%d truncated-panel=%d (truncation must lose them all)"
        % (first_live.date(), n_full, n_cut))

    # L6 metrics renormalises a sub-window (a slice starting at 2.0 must not be read
    #    as if it started at 1.0 -- the r1262 CAGR artefact)
    s = pd.Series(2.0 * 1.10 ** (np.arange(253) / 252.0),
                  index=pd.bdate_range("2020-01-01", periods=253))
    m = F.metrics(s, "x")
    chk("selftest: sub-window CAGR is renormalised",
        abs(m.get("cagr", 0) - 0.1) < 0.005 and m.get("start_level") == 2.0,
        "cagr=%s start_level=%s (a last_level-1 read would print 1.20)"
        % (m.get("cagr"), m.get("start_level")))

    # L7 the EW control is a real book, not an empty series
    one = cell(close, openp, amt, feats, 5, 20, start, None)
    chk("selftest: EW control is active",
        one["ew"].get("bars", 0) > 100 and one["ew"].get("vol", 0) > 0,
        "ew bars=%s vol=%s" % (one["ew"].get("bars"), one["ew"].get("vol")))

    # L8 the null destroys the signal it is supposed to destroy
    null = random_null(close, openp, amt, feats, 5, 20, start, None, n_iter=12, seed=3)
    chk("selftest: null returns a usable p-value",
        null["p_value"] is not None and 0.0 <= null["p_value"] <= 1.0,
        "p=%s n=%d" % (null["p_value"], null["n_iter"]))

    print("\nselftest: %d/%d PASS, %d FAIL" % (ok, ok + fail, fail))
    return 0 if fail == 0 else 1


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "selftest":
        return selftest()
    if cmd == "control":
        control()
        return 0
    run()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))