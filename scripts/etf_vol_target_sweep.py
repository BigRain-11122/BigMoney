"""ETF book -- is the volatility-target setting a plateau or a spike?

The production card's headline (debt removed, top-N composite, 20-bar cadence, 10bp per
side, 8% vol target on a 60-day realised-vol estimate) carries two numbers that were
never swept: the TARGET (8%) and the WINDOW (60 bars). Everything else about the
configuration has a grid behind it (holdings x cadence x cost, r1260-r1262; capacity and
breadth, r1263; carry, r1268). A single choice on two axes is exactly the kind of knob
that reads as "tuned" even when it is not, and cannot be defended without the surface.

So this script prices the surface: window x target, at the production configuration and
at the 5-name variant, plus the un-targeted book as the reference each cell de-levers
from. The question it answers is narrow and honest:

  * does 8% / 60d sit in the middle of a flat region (the setting is not load-bearing),
  * or is it a local spike (the setting IS the result, i.e. fragile)?

It does not pick a better cell -- choosing the best corner of a fresh surface is how a
backtest gets fitted. The published setting stays 8% / 60d unless the surface shows it is
a spike, and that verdict is the deliverable.

  python scripts/etf_vol_target_sweep.py run
  python scripts/etf_vol_target_sweep.py --selftest     # offline invariants
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import numpy as np
import pandas as pd

import etf_composite_pf as E
import etf_robust_pf as R
import etf_book_production as P

OUT = os.path.join(E.PATHS.results_dir, "etf_vol_target_sweep.json")

WINDOWS = (30, 45, 60, 90, 120)
TARGETS = (0.06, 0.08, 0.10)
NAMES = (5, 12)
REBAL = 20
COST = P.COST
PUBLISHED = (60, 0.08)


def cell(close, openp, amt, score, n_hold, window, target):
    """One surface point, priced by the production backtest (one engine, no copies)."""
    m, ser = P.backtest(close, openp, amt, score, n_hold, REBAL, cost=COST,
                        vol_target=target, vol_window=window)
    return {"n": n_hold, "window": window, "target": target,
            "full": m["full"], "is": m["is"], "oos": m["oos"],
            "turnover": m["turnover_per_decision"]}, ser


def surface(close, openp, amt, score, n_hold):
    cells, curves = [], {}
    for window in WINDOWS:
        for target in TARGETS:
            c, ser = cell(close, openp, amt, score, n_hold, window, target)
            cells.append(c)
            curves[(window, target)] = ser
    return cells, curves


def summarize(cells, base):
    """Row/column spread around the published cell, and where it ranks.

    Axes are read off the cells themselves, so the same function works on the full grid
    and on a hand-built toy surface (selftest), instead of assuming WINDOWS/TARGETS.
    """
    cagr = {(c["window"], c["target"]): c["full"]["cagr"] for c in cells}
    dd = {(c["window"], c["target"]): c["full"]["maxdd"] for c in cells}
    sharpe = {(c["window"], c["target"]): c["full"]["sharpe"] for c in cells}
    wins = sorted({c["window"] for c in cells})
    tgts = sorted({c["target"] for c in cells})
    row = [v for (w, t), v in cagr.items() if t == PUBLISHED[1]]          # fixed target
    col = [v for (w, t), v in cagr.items() if w == PUBLISHED[0]]          # fixed window
    best = max(cagr.values())
    worst = min(cagr.values())
    order = sorted(cagr.values(), reverse=True)
    rank = order.index(cagr[PUBLISHED]) + 1 if PUBLISHED in cagr else None
    return {
        "published": {"cagr": cagr.get(PUBLISHED), "maxdd": dd.get(PUBLISHED),
                      "sharpe": sharpe.get(PUBLISHED)},
        "base_no_vt": {"cagr": base["full"]["cagr"], "maxdd": base["full"]["maxdd"],
                       "sharpe": base["full"]["sharpe"]},
        "window_axis": {"min": min(row), "max": max(row),
                        "range_pp": round((max(row) - min(row)) * 100, 2),
                        "values": {str(w): round(cagr[(w, PUBLISHED[1])] * 100, 2)
                                   for w in wins if (w, PUBLISHED[1]) in cagr},
                        "sharpe": {str(w): sharpe[(w, PUBLISHED[1])]
                                   for w in wins if (w, PUBLISHED[1]) in cagr},
                        "maxdd": {str(w): dd[(w, PUBLISHED[1])]
                                  for w in wins if (w, PUBLISHED[1]) in cagr}},
        "target_axis": {"min": min(col), "max": max(col),
                        "range_pp": round((max(col) - min(col)) * 100, 2),
                        "values": {str(t): round(cagr[(PUBLISHED[0], t)] * 100, 2)
                                   for t in tgts if (PUBLISHED[0], t) in cagr},
                        "sharpe": {str(t): sharpe[(PUBLISHED[0], t)]
                                   for t in tgts if (PUBLISHED[0], t) in cagr},
                        "maxdd": {str(t): dd[(PUBLISHED[0], t)]
                                  for t in tgts if (PUBLISHED[0], t) in cagr}},
        "sharpe_spread": {
            "window": round(max(sharpe[(w, PUBLISHED[1])] for w in wins
                                if (w, PUBLISHED[1]) in sharpe)
                            - min(sharpe[(w, PUBLISHED[1])] for w in wins
                                  if (w, PUBLISHED[1]) in sharpe), 3),
            "target": round(max(sharpe[(PUBLISHED[0], t)] for t in tgts
                                if (PUBLISHED[0], t) in sharpe)
                            - min(sharpe[(PUBLISHED[0], t)] for t in tgts
                                  if (PUBLISHED[0], t) in sharpe), 3)},
        "surface": {"best_cagr": best, "worst_cagr": worst,
                    "range_pp": round((best - worst) * 100, 2),
                    "published_rank": rank, "n_cells": len(order)},
        "maxdd_worst": min(dd.values()), "maxdd_best": max(dd.values()),
    }


def verdict(s, sharpe_tol=0.10):
    """Risk-adjusted read, because raw CAGR cannot referee either axis.

    A higher target mechanically buys more return in a rising sample, so a CAGR spread
    across targets is expected and proves nothing. The question is whether the dial
    changes risk-adjusted quality: if Sharpe is flat while CAGR and drawdown move
    together, the target is a risk preference. Same test for the window, where a spread
    in Sharpe WOULD mean the estimate length is quietly carrying the result.
    """
    t_sh = s["sharpe_spread"]["target"]
    w_sh = s["sharpe_spread"]["window"]
    ta, wa = s["target_axis"]["range_pp"], s["window_axis"]["range_pp"]
    t_dd = list(s["target_axis"]["maxdd"].values())
    if t_sh <= sharpe_tol:
        t_txt = ("target=RISK DIAL (Sharpe moves %.3f over %.2fpp of CAGR; drawdown runs"
                 " %.1f%%..%.1f%% => return and risk scale together, 8%% is a preference"
                 " not a fit)" % (t_sh, ta, max(t_dd) * 100, min(t_dd) * 100))
    else:
        t_txt = "target=LOAD-BEARING (Sharpe spread %.3f over %.2fpp)" % (t_sh, ta)
    if w_sh <= sharpe_tol:
        w_txt = ("window=INERT on risk-adjusted terms (Sharpe spread %.3f while CAGR moves"
                 " %.2fpp => the estimate length mostly times exposure)" % (w_sh, wa))
    else:
        w_txt = "window=LOAD-BEARING (Sharpe spread %.3f over %.2fpp)" % (w_sh, wa)
    return t_txt + "; " + w_txt


# ---------------------------------------------------------------- selftest

def _synth(seed=7, n_names=14, bars=420):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2022-01-03", periods=bars)
    steps = rng.normal(0.0002, 0.012, (bars, n_names))
    close = pd.DataFrame(100 * np.exp(np.cumsum(steps, axis=0)), index=idx,
                         columns=["S%02d" % i for i in range(n_names)])
    openp = close.shift(1).bfill() * (1 + rng.normal(0, 0.001, close.shape))
    amt = pd.DataFrame(5e7, index=idx, columns=close.columns)
    score = pd.DataFrame(rng.normal(0, 1, close.shape), index=idx, columns=close.columns)
    return close, openp, amt, score


def selftest():
    ok = []

    def chk(name, cond, note=""):
        ok.append((name, bool(cond), note))

    close, openp, amt, score = _synth()

    # 1. the default window must be the old behaviour, bit for bit
    a, ta = R.open_to_open_equity(close, openp, amt, score, 20, 5, 0.001, vol_target=0.08)
    b, tb = R.open_to_open_equity(close, openp, amt, score, 20, 5, 0.001, vol_target=0.08,
                                  vol_window=60)
    diff = float((a - b).abs().max()) if len(a) else np.inf
    chk("vol_window=60 is the legacy path", diff == 0.0 and ta == tb,
        "maxdiff=%.2e turn=%.6f/%.6f" % (diff, ta, tb))

    # 2. activity leg: a flat pair of curves matches for the wrong reason (r1261/r1268)
    chk("book actually trades", ta > 0, "turnover=%.3f" % ta)

    # 3. a higher target can never de-lever more: scale is min(1, target/vol)
    _, t_low = R.open_to_open_equity(close, openp, amt, score, 20, 5, 0.001, vol_target=0.06)
    _, t_high = R.open_to_open_equity(close, openp, amt, score, 20, 5, 0.001, vol_target=0.10)
    chk("higher target holds at least as much risk", t_high >= t_low - 1e-12,
        "turn6=%.3f turn10=%.3f" % (t_low, t_high))

    # 4. vol_target=None must be untouched by any window value
    base, tbase = R.open_to_open_equity(close, openp, amt, score, 20, 5, 0.001)
    base2, tbase2 = R.open_to_open_equity(close, openp, amt, score, 20, 5, 0.001,
                                          vol_window=30)
    d2 = float((base - base2).abs().max()) if len(base) else np.inf
    chk("window is inert without a target", d2 == 0.0 and tbase == tbase2,
        "maxdiff=%.2e" % d2)

    # 5. the window guard: fewer than 20 rows of history => no scaling applied at all
    #    (asserted as equality with the un-targeted run, not as "empty output")
    tiny_close = close.iloc[-10:]
    tiny_open = openp.iloc[-10:]
    tiny_close.index = pd.bdate_range("2025-01-01", periods=10)
    tiny_open.index = tiny_close.index
    tiny_amt = amt.iloc[-10:]
    tiny_amt.index = tiny_close.index
    tiny_score = score.iloc[-10:]
    tiny_score.index = tiny_close.index
    s_tgt, _ = R.open_to_open_equity(tiny_close, tiny_open, tiny_amt, tiny_score, 2, 3,
                                     0.001, vol_target=0.08, vol_window=60)
    s_unt, _ = R.open_to_open_equity(tiny_close, tiny_open, tiny_amt, tiny_score, 2, 3,
                                     0.001)
    d5 = float((s_tgt - s_unt).abs().max()) if len(s_tgt) else np.inf
    chk("short history degrades to no overlay", len(s_tgt) > 0 and d5 == 0.0,
        "bars=%d maxdiff=%.2e" % (len(s_tgt), d5))

    # 6. summarizer arithmetic on a hand-built 2x2 surface
    cells = [{"window": w, "target": t, "full": {"cagr": c, "maxdd": -0.1, "sharpe": 1.0},
              "is": {}, "oos": {}, "turnover": 1.0}
             for (w, t), c in {(60, 0.08): 0.090, (60, 0.10): 0.095,
                               (30, 0.08): 0.088, (30, 0.10): 0.093}.items()]
    s2 = summarize(cells, {"full": {"cagr": 0.085, "maxdd": -0.16, "sharpe": 0.9}})
    chk("window axis spread", abs(s2["window_axis"]["range_pp"] - 0.20) < 1e-9,
        "%s" % s2["window_axis"]["range_pp"])
    chk("target axis spread", abs(s2["target_axis"]["range_pp"] - 0.50) < 1e-9,
        "%s" % s2["target_axis"]["range_pp"])
    # toy surface: CAGR moves on both axes but every cell has the same Sharpe, so the
    # verdict must read "risk dial" + "inert", NOT a fragility alarm
    v2 = verdict(s2)
    chk("flat-Sharpe surface reads as dial+inert",
        "RISK DIAL" in v2 and "INERT" in v2, v2)
    n_pass = sum(1 for _, c, _ in ok if c)
    for name, c, note in ok:
        print("[%s] %s | %s" % ("PASS" if c else "FAIL", name, note))
    print("selftest %d/%d" % (n_pass, len(ok)))
    return 0 if n_pass == len(ok) else 1


# ---------------------------------------------------------------- run

def run():
    close, openp, amt, score = P.prep_panel()
    print("universe %d names, bars %d, last bar %s" % (
        close.shape[1], close.shape[0], close.index[-1].date()), flush=True)
    out = {"evidence_cutoff": str(close.index[-1].date()),
           "rebal": REBAL, "cost_bp": COST * 1e4, "published": list(PUBLISHED),
           "targets": list(TARGETS), "windows": list(WINDOWS), "books": {}}
    for n in NAMES:
        base, _ = P.backtest(close, openp, amt, score, n, REBAL, cost=COST)
        cells, curves = surface(close, openp, amt, score, n)
        s = summarize(cells, base)
        s["verdict"] = verdict(s)
        s["cells"] = cells
        out["books"]["n%d" % n] = s
        print("n=%d base cagr %.2f%% dd %.2f%% | published %s cagr %.2f%% dd %.2f%%" % (
            n, base["full"]["cagr"] * 100, base["full"]["maxdd"] * 100, PUBLISHED,
            s["published"]["cagr"] * 100, s["published"]["maxdd"] * 100), flush=True)
        print("   window axis %s | target axis %s" % (
            s["window_axis"]["values"], s["target_axis"]["values"]), flush=True)
        print("   %s" % s["verdict"], flush=True)
        # the pivot that a reader can sanity-check by eye: rows = target, cols = window
        piv = pd.DataFrame({w: {t: round(next(c["full"]["cagr"] for c in cells
                                              if c["window"] == w and c["target"] == t) * 100, 2)
                                for t in sorted({c["target"] for c in cells})}
                            for w in sorted({c["window"] for c in cells})})
        print(piv.to_string(), flush=True)

    os.makedirs(E.PATHS.results_dir, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, ensure_ascii=False, default=str)
    print("written %s" % OUT, flush=True)
    return 0


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "selftest"
    if arg == "--selftest":
        sys.exit(selftest())
    sys.exit(run())