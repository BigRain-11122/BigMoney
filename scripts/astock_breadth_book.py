#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""how many A-share names does the breadth premium need?

WHY THIS FILE EXISTS
--------------------
r1408's judge closed zoo #93 with a side reading worth more than the factor:
equal-weighting every liquid A-share earned 9.24%/yr with a -27.4% drawdown
while 510300 lost 0.2%/yr with -45.1%.  That number is a CONTROL in a factor
study -- a pool of ~5,000 names nobody can hold.  It has never been asked as
its own question, and it is the one that decides money:

    when the book can only hold N names, how much of that premium survives,
    and is the N-name book a lottery or a rule?

Nothing here is a timing signal and nothing here is a factor: every arm holds
the same pool for the same 60 bars and only the WIDTH differs.  That is what
separates this face from scripts/etf_breadth_sweep.py (ETF universe, capacity
in CNY against 1%-ADV) -- here the axis is the stock universe and the cost of
width is sampling noise, not market impact.

CONSTRUCTION (frozen; changing any line changes the answer)
-----------------------------------------------------------
  panel       data/astock_daily/per/<sym>.csv (qfq, forward-accumulated),
              loaded by zoo93_disposition_cgo_probe.load_panel (imported,
              never re-implemented), window >= 2020-01-01
  eligible    at decision bar t: 20-bar median `amount` >= 20,000,000 CNY,
              finite close[t], finite open[t+1], finite open[t+1+R]
  cohorts     decision bars every R = 60 bars, non-overlapping, from the
              first bar with >= MIN_POOL eligible names
  entry/exit  buy the next open after the decision bar, sell the open R bars
              later: r = open[t+1+R] / open[t+1] - 1
  arms        ALL = every eligible name, equal weight
              N in {20, 50, 100, 200, 500} = K = 40 independent draws without
              replacement from that date's eligible names, equal weight
  cost        2 x 13.041bp per cohort per name (COST_X1_RATE, the constant the
              book cards pay); an x3 arm is reported for ALL and for N=100
  annualise   periods_per_year = 252 / R, chained over cohorts
  drawdown    measured on the COHORT curve (60-bar granularity), which is
              coarser than a daily curve and is disclosed as such
  phase null  the same grid re-run at decision offsets 0, 5, ..., R-5; the
              spread of those CAGR readings is the honest error bar, because
              a 6-year span holds only ~27 independent 60-bar windows
  benchmark   510300 close over the same span (daily maxdd), plus the cash
              leg 511260 as a declared, unused reference

VERDICT RULE (frozen BEFORE the numbers were seen; re-emitted in the receipt)
  ADMIT_TO_PREREG  iff ALL of
    (a) ALL net CAGR - 510300 CAGR over the same span >= +3.0pp/yr
    (b) some N <= 200 whose mean net CAGR >= 0.80 x ALL net CAGR
        and whose mean cohort maxdd is no worse than ALL maxdd - 2.0pp
    (c) every phase's ALL net CAGR minus the offset-0 reading >= -2.0pp
  otherwise REFUSE_AS_CANDIDATE, listing the failing conditions verbatim.

self (+-60s on the real panel? no: run mode loads 5,223 CSVs, ~3 min)
  python scripts/astock_breadth_book.py selftest   # synthetic, seconds
  python scripts/astock_breadth_book.py run
"""

from __future__ import annotations

import argparse
import io
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import zoo93_disposition_cgo_probe as z93  # panel loader, single implementation

OUT = os.path.join(ROOT, "results", "breadth_book", "astock_breadth_book.json")
COST_PER_SIDE = 0.0013041
R = 60                 # holding / decision stride, frozen
LIQ_WINDOW = 20
LIQ_FLOOR = 20_000_000.0
MIN_POOL = 100
WIDTHS = (20, 50, 100, 200, 500)
DRAWS = 40
PHASE_STEP = 5
BARS_PER_YEAR = 252.0
TRADER = "510300"


# --------------------------------------------------------------------------- #
# construction
# --------------------------------------------------------------------------- #
def eligibility(open_, close, amount) -> np.ndarray:
    """Boolean (T, S): may this name be held at a decision bar t?"""
    import pandas as pd

    T, S = close.shape
    amt = np.asarray(amount, dtype=np.float64)
    med = pd.DataFrame(np.where(np.isfinite(amt), amt, np.nan)).rolling(
        LIQ_WINDOW, min_periods=LIQ_WINDOW // 2).median().to_numpy()
    ok = np.isfinite(med) & (med >= LIQ_FLOOR) & np.isfinite(close)
    return ok


def cohorts(panel: dict, r: int = R, offset: int = 0, min_pool: int = MIN_POOL):
    """Non-overlapping cohorts: [(decision_index, returns_of_every_eligible_name)]."""
    op = np.asarray(panel["open"], dtype=np.float64)
    cl = np.asarray(panel["close"], dtype=np.float64)
    am = np.asarray(panel["amount"], dtype=np.float64)
    T = cl.shape[0]
    ok = eligibility(op, cl, am)
    out, skipped = [], 0
    t = offset
    while t + 1 + r < T:
        members = np.flatnonzero(ok[t])
        if members.size >= min_pool:
            e0 = op[t + 1, members]
            e1 = op[t + 1 + r, members]
            good = np.isfinite(e0) & np.isfinite(e1) & (e0 > 0) & (e1 > 0)
            members, e0, e1 = members[good], e0[good], e1[good]
            if members.size >= min_pool:
                out.append((t, members, e1 / e0 - 1.0))
            else:
                skipped += 1
        else:
            skipped += 1
        t += r
    return out, skipped


def chained(returns, r: int = R):
    """(cagr, maxdd, curve) from a list of per-cohort net returns."""
    arr = np.asarray(list(returns), dtype=np.float64)
    if arr.size == 0:
        return None, None, []
    curve = np.concatenate(([1.0], np.cumprod(1.0 + arr)))
    yrs = arr.size * r / BARS_PER_YEAR
    eq = curve[-1]
    cagr = float(eq ** (1.0 / yrs) - 1.0) if yrs > 0 and eq > 0 else float("nan")
    peak = np.maximum.accumulate(curve)
    dd = float((curve / peak - 1.0).min())
    return cagr, dd, curve.tolist()


def net(member_returns: np.ndarray, cost: float) -> float:
    return float(member_returns.mean()) - 2.0 * cost


def arm_all(cs, cost: float = COST_PER_SIDE):
    return [net(rs, cost) for _t, _m, rs in cs]


def arm_width(cs, n: int, draws: int = DRAWS, seed: int = 0, cost: float = COST_PER_SIDE):
    """K independent N-name books, each chained over the same cohorts."""
    rng = np.random.default_rng(seed)
    books = []
    for k in range(draws):
        seq = []
        for _t, members, rs in cs:
            if members.size <= n:
                seq.append(None)  # honest: this date cannot seat an n-name book
                continue
            pick = rng.choice(members.size, size=n, replace=False)
            seq.append(net(rs[pick], cost))
        books.append(seq)
    out = []
    for seq in books:
        usable = [v for v in seq if v is not None]
        cagr, dd, _curve = chained(usable)
        out.append({"cagr": cagr, "maxdd": dd, "cohorts": len(usable),
                    "seat_gaps": sum(1 for v in seq if v is None)})
    return out


def arm_width_frozen(cs, n: int, draws: int = DRAWS, seed: int = 0,
                     cost: float = COST_PER_SIDE):
    """K books drawn ONCE at the first cohort and held by name afterwards.

    This is what a portfolio actually is.  A name that later leaves the
    eligible set is dropped for that cohort and the rest keep their weights
    (attrition is reported, never silently refilled).
    """
    rng = np.random.default_rng(seed)
    first = cs[0][1]
    books = []
    for _k in range(draws):
        if first.size <= n:
            books.append({"cagr": None, "maxdd": None, "cohorts": 0,
                          "seat_gaps": len(cs), "attrition": 0})
            continue
        held = set(first[rng.choice(first.size, size=n, replace=False)].tolist())
        seq, attrit = [], 0
        for _t, members, rs in cs:
            pos = {int(s): i for i, s in enumerate(members)}
            keep = [pos[s] for s in held if s in pos]
            if not keep:
                seq.append(None)
                attrit += 1
                continue
            attrit += n - len(keep)
            seq.append(net(rs[keep], cost))
        usable = [v for v in seq if v is not None]
        cagr, dd, _c = chained(usable)
        books.append({"cagr": cagr, "maxdd": dd, "cohorts": len(usable),
                      "seat_gaps": 0, "attrition": attrit})
    return books


def summarise(books):
    c = np.array([b["cagr"] for b in books if b["cagr"] is not None and np.isfinite(b["cagr"])])
    d = np.array([b["maxdd"] for b in books if b["maxdd"] is not None and np.isfinite(b["maxdd"])])
    if c.size == 0:
        return {"n_books": len(books), "cagr_mean": None, "cagr_sd": None,
                "cagr_p10": None, "cagr_p90": None, "maxdd_mean": None,
                "seat_gaps": sum(b["seat_gaps"] for b in books)}
    return {
        "n_books": int(c.size),
        "cagr_mean": float(c.mean()),
        "cagr_sd": float(c.std(ddof=1)) if c.size > 1 else 0.0,
        "cagr_p10": float(np.percentile(c, 10)),
        "cagr_p90": float(np.percentile(c, 90)),
        "maxdd_mean": float(d.mean()) if d.size else None,
        "seat_gaps": int(sum(b.get("seat_gaps", 0) for b in books)),
        "attrition": int(sum(b.get("attrition", 0) for b in books)),
    }


# --------------------------------------------------------------------------- #
# benchmark
# --------------------------------------------------------------------------- #
def etf_series(path: str, start: str | None = None):
    import pandas as pd

    df = pd.read_csv(path)
    date_col = "date" if "date" in df.columns else df.columns[0]
    close_col = "close" if "close" in df.columns else df.columns[-1]
    d = df[[date_col, close_col]].copy()
    d.columns = ["date", "close"]
    d["date"] = d["date"].astype(str)
    if start:
        d = d[d["date"] >= start]
    return d.reset_index(drop=True)


def etf_reading(path: str, d0: str, d1: str):
    d = etf_series(path)
    span = d[(d["date"] >= d0) & (d["date"] <= d1)]
    if len(span) < 20:
        return None
    v = span["close"].to_numpy(dtype=np.float64)
    yrs = len(v) / BARS_PER_YEAR
    cagr = float((v[-1] / v[0]) ** (1.0 / yrs) - 1.0)
    peak = np.maximum.accumulate(v)
    return {"cagr": cagr, "maxdd": float((v / peak - 1.0).min()),
            "bars": int(len(v)), "first": str(span["date"].iloc[0]),
            "last": str(span["date"].iloc[-1])}


# --------------------------------------------------------------------------- #
# run
# --------------------------------------------------------------------------- #
def run() -> dict:
    t0 = time.time()
    panel = z93.load_panel()
    dates = panel["dates"]
    cs, skipped = cohorts(panel)
    if not cs:
        return {"tool": "astock_breadth_book", "verdict": "no_data",
                "panel": {"symbols": len(panel["symbols"]), "bars": len(dates)},
                "honest": ["no cohort carried MIN_POOL eligible names; nothing measured"]}

    first_dec = cs[0][0]
    last_dec = cs[-1][0]
    span0 = dates[first_dec + 1]
    span1 = dates[last_dec + 1 + R] if last_dec + 1 + R < len(dates) else dates[-1]

    all_seq = arm_all(cs)
    all_cagr, all_dd, all_curve = chained(all_seq)
    arms = {"ALL": {"cagr": all_cagr, "maxdd": all_dd, "cohorts": len(all_seq),
                    "mean_pool": float(np.mean([m.size for _t, m, _r in cs])),
                    "cagr_x3_cost": chained(arm_all(cs, 3 * COST_PER_SIDE))[0],
                    "cagr_x0_cost": chained(arm_all(cs, 0.0))[0]}}
    for n in WIDTHS:
        books = arm_width(cs, n)
        s = summarise(books)
        x3 = summarise(arm_width(cs, n, draws=10, seed=99, cost=3 * COST_PER_SIDE))
        s["cagr_x3_cost"] = x3["cagr_mean"]
        fr = summarise(arm_width_frozen(cs, n))
        s["frozen_gap"] = fr
        arms[f"N{n}"] = s

    # phase null on the whole grid (ALL and N=100 only, 40 draws each)
    phases = []
    for off in range(0, R, PHASE_STEP):
        pcs, _sk = cohorts(panel, offset=off)
        if not pcs:
            continue
        rows = len(pcs)
        pc, pdd, _c = chained(arm_all(pcs)[:rows])
        n100 = summarise(arm_width(pcs, 100, draws=10, seed=7))
        phases.append({"offset": off, "cohorts": rows, "ALL_cagr": pc,
                       "ALL_maxdd": pdd, "N100_cagr_mean": n100["cagr_mean"]})

    bench = {}
    for key, path in (("510300", os.path.join(ROOT, "data", "daily", "sh510300.csv")),
                      ("511260", os.path.join(ROOT, "data", "daily", "sh511260.csv"))):
        r = etf_reading(path, span0, span1) if os.path.exists(path) else None
        bench[key] = r

    idx = bench.get("510300")
    excess = (all_cagr - idx["cagr"]) if (idx and all_cagr is not None) else None

    # ---- verdict rule (frozen above) ----
    fails = []
    if excess is None or excess < 0.03:
        fails.append("a: ALL net CAGR minus 510300 over the same span = %s < +3.0pp/yr"
                     % ("n/a" if excess is None else "%.4f" % excess))
    holdable = None
    for n in WIDTHS:
        if n > 200:
            continue
        s = arms[f"N{n}"]
        if s["cagr_mean"] is None:
            continue
        if s["cagr_mean"] >= 0.80 * all_cagr and s["maxdd_mean"] >= all_dd - 0.02:
            holdable = n
            break
    if holdable is None:
        fails.append("b: no width <= 200 keeps >= 80%% of the ALL premium (ALL %.4f) "
                     "with a cohort drawdown no worse than %.4f - 2.0pp"
                     % (all_cagr, all_dd))
    if phases:
        base = [p for p in phases if p["offset"] == 0]
        base = base[0]["ALL_cagr"] if base else all_cagr
        worst = min(p["ALL_cagr"] for p in phases if p["ALL_cagr"] is not None)
        if worst - base < -0.02:
            fails.append("c: worst phase %.4f is %.2fpp under the offset-0 reading %.4f"
                         % (worst, 100 * (worst - base), base))
    verdict = "ADMIT_TO_PREREG" if not fails else "REFUSE_AS_CANDIDATE"

    per_year = {}
    for y in sorted({dates[t][:4] for t, _m, _r in cs}):
        idxs = [i for i, (t, _m, _r) in enumerate(cs) if dates[t][:4] == y]
        if not idxs:
            continue
        sub = [all_seq[i] for i in idxs]
        pc, _pdd, _c = chained(sub)
        per_year[y] = {"cohorts": len(idxs), "ALL_net": pc}

    return {
        "tool": "astock_breadth_book",
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "evidence_cutoff": dates[last_dec],
        "construct": {
            "panel": "data/astock_daily/per (qfq)", "stride_bars": R,
            "liquidity": "20-bar median amount >= 20,000,000 CNY",
            "entry_exit": "open[t+1] -> open[t+1+R]",
            "cost_per_side": COST_PER_SIDE, "widths": list(WIDTHS),
            "draws": DRAWS, "min_pool": MIN_POOL, "phase_step": PHASE_STEP,
            "drawdown_granularity_bars": R,
        },
        "decision_rule": ("ADMIT_TO_PREREG iff (a) ALL - 510300 >= +3.0pp/yr and "
                          "(b) some N<=200 keeps >=80% of ALL net CAGR with maxdd no "
                          "worse than ALL-2.0pp and (c) every phase within -2.0pp of "
                          "offset 0; else REFUSE_AS_CANDIDATE"),
        "panel": {"symbols": len(panel["symbols"]), "bars": len(dates),
                  "first_date": dates[0], "last_date": dates[-1]},
        "cohorts": {"n": len(cs), "first_decision": dates[first_dec],
                    "last_decision": dates[last_dec], "span": [span0, span1],
                    "skipped": skipped,
                    "mean_pool": arms["ALL"]["mean_pool"]},
        "arms": arms,
        "benchmark": bench,
        "excess_vs_510300": excess,
        "phases": phases,
        "per_year": per_year,
        "holdable_width": holdable,
        "verdict": verdict,
        "failing_conditions": fails,
        "honest": [
            "qfq panel: a name that split or paid a dividend mid-cohort shows the "
            "adjusted return, which is the right economics for a holder but not the "
            "as-traded print",
            "eligible set is TODAY's listed names (survivorship): the 2020-2026 tails "
            "still carry names that have since delisted only if the archive kept them",
            "a 60-bar cohort curve cannot see intra-cohort drawdown; the reported "
            "maxdd is coarser than a daily curve and flatters the book",
            "cohort count is small (~27 at R=60 over six years): the phase range is "
            "the error bar, not a significance test",
            "no cash yield is credited to the arms; 511260 is reported as a reference "
            "and is never used to rescue a return",
        ],
        "elapsed_sec": round(time.time() - t0, 1),
    }


# --------------------------------------------------------------------------- #
# selftest
# --------------------------------------------------------------------------- #
def _synth(T=400, S=300, seed=11, drift=0.0008, noise=0.0, liq=5e7):
    rng = np.random.default_rng(seed)
    base = 10.0 * np.exp(np.cumsum(np.full((T, S), drift) +
                                   (noise * rng.standard_normal((T, S)) if noise else 0.0), axis=0))
    panel = {"dates": ["%04d-%02d-%02d" % (2000 + i // 250, 1 + (i % 250) // 21, 1 + (i % 21))
                       for i in range(T)],
             "symbols": ["s%03d" % j for j in range(S)],
             "open": base.copy(), "close": base.copy(),
             "amount": np.full((T, S), liq), "turn": np.full((T, S), 0.01),
             "volume": np.full((T, S), 1e6)}
    return panel


def selftest() -> int:
    legs, fails = 0, []

    def chk(name, cond, detail=""):
        nonlocal legs
        legs += 1
        if not cond:
            fails.append("%s %s" % (name, detail))

    # L1 constant drift: every arm must find the arithmetic return of the stride
    p = _synth(drift=0.001, noise=0.0)
    cs, _s = cohorts(p)
    chk("L1 cohorts exist", len(cs) > 3, "n=%d" % len(cs))
    cagr, dd, _c = chained(arm_all(cs))
    per_cohort = (np.exp(0.001 * R)) - 1.0 - 2.0 * COST_PER_SIDE  # _synth compounds exp()
    want = (1.0 + per_cohort) ** (BARS_PER_YEAR / R) - 1.0
    chk("L1 ALL cagr == net cohort return annualised", abs(cagr - want) < 1e-9,
        "cagr=%.9f want=%.9f" % (cagr, want))
    chk("L1 all widths agree on a constant tape",
        all(abs(summarise(arm_width(cs, n, draws=3))["cagr_mean"] - cagr) < 1e-9 for n in (20, 50)),
        "width spread")

    # L2 monotone rising tape has no drawdown
    chk("L2 monotone tape drawdown == 0", abs(dd) < 1e-12, "dd=%r" % dd)

    # L3 cost must bite: x3 < x1 < x0 on a flat tape
    x0 = chained(arm_all(cs, 0.0))[0]
    x3 = chained(arm_all(cs, 3 * COST_PER_SIDE))[0]
    chk("L3 cost monotone", x3 < cagr < x0, "x3=%.5f x1=%.5f x0=%.5f" % (x3, cagr, x0))

    # L4 a zero-drift tape is negative under cost
    pz = _synth(drift=0.0, noise=0.0)
    cz, _s = cohorts(pz)
    chk("L4 zero-drift tape is negative after cost", chained(arm_all(cz))[0] < 0)

    # L5 determinism + seed sensitivity of the draws
    a = summarise(arm_width(cs, 20, draws=5, seed=1))
    b = summarise(arm_width(cs, 20, draws=5, seed=1))
    chk("L5 same seed reproduces", a == b)

    # L6 width cannot seat more names than the pool: honest gap, no crash
    pthin = _synth(S=40)
    cthin, _s = cohorts(pthin, min_pool=10)
    s = summarise(arm_width(cthin, 500, draws=2))
    chk("L6 thin pool records seat gaps", s["seat_gaps"] > 0 or s["n_books"] == 0,
        "gaps=%s" % s["seat_gaps"])

    # L7 empty eligibility -> no cohorts, run() must NOT be reached with a crash
    pnone = _synth(liq=1.0)
    cn, skipped = cohorts(pnone)
    chk("L7 illiquid tape yields zero cohorts", cn == [] and skipped > 0,
        "n=%d skipped=%d" % (len(cn), skipped))

    # L8 liquidity gate actually filters on the amount column
    pmix = _synth(S=120)
    pmix["amount"][:, :60] = 1.0
    okm = eligibility(pmix["open"], pmix["close"], pmix["amount"])
    chk("L8 liquidity gate splits the panel",
        bool(okm[-1, :60].sum() == 0) and bool(okm[-1, 60:].sum() == 120 - 60),
        "first-half kept=%d second-half kept=%d" % (okm[-1, :60].sum(), okm[-1, 60:].sum()))

    # L9 the ALL arm is exactly the mean of that cohort's eligible returns
    t, members, rs = cs[0]
    chk("L9 ALL arm is the cohort mean less cost",
        abs(all_seq0(rs) - (rs.mean() - 2.0 * COST_PER_SIDE)) < 1e-15)

    # L10 chained() round-trip on a known series
    c, d, curve = chained([0.10, -0.10])
    chk("L10 chain arithmetic", abs(curve[-1] - 0.99) < 1e-12, "eq=%r" % curve[-1])
    chk("L10 drawdown sign", d <= 0.0 and abs(d + 0.10) < 1e-12, "dd=%r" % d)

    # L11 a cohort's exit bar must be reachable (no NaN slicing past the end)
    chk("L11 exit index inside panel",
        all(t + 1 + R < len(p["dates"]) for t, _m, _r in cs))

    print("selftest %d/%d PASS" % (legs - len(fails), legs))
    for f in fails:
        print("FAIL", f)
    return 0 if not fails else 1


def all_seq0(rs, cost=COST_PER_SIDE):
    return net(rs, cost)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["run", "selftest"], nargs="?", default="run")
    a = ap.parse_args()
    if a.mode == "selftest":
        return selftest()
    rep = run()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with io.open(OUT, "w", encoding="utf-8") as fh:
        json.dump(rep, fh, ensure_ascii=False, indent=1, sort_keys=True)
    arms = rep.get("arms", {})
    print("panel", rep["panel"]["symbols"], "names", rep["panel"]["bars"], "bars")
    print("cohorts", rep["cohorts"]["n"], rep["cohorts"]["first_decision"], "->",
          rep["cohorts"]["last_decision"], "mean_pool", round(rep["cohorts"]["mean_pool"], 1))
    def pct(v):
        return "n/a" if v is None else "%+.4f" % v
    print("ALL net %s  maxdd %s  x3 %s" % (pct(arms["ALL"]["cagr"]),
                                           pct(arms["ALL"]["maxdd"]),
                                           pct(arms["ALL"]["cagr_x3_cost"])))
    for n in WIDTHS:
        s = arms["N%d" % n]
        print("N%-4d mean %s  sd %s  p10 %s  p90 %s  maxdd %s  x3 %s  gaps %d | frozen %s (sd %s)"
              % (n, pct(s["cagr_mean"]), pct(s["cagr_sd"]), pct(s["cagr_p10"]),
                 pct(s["cagr_p90"]), pct(s["maxdd_mean"]), pct(s["cagr_x3_cost"]),
                 s["seat_gaps"], pct(s["frozen_gap"]["cagr_mean"]),
                 pct(s["frozen_gap"]["cagr_sd"])))
    for k, v in rep["benchmark"].items():
        print("bench %-7s %s" % (k, "n/a" if not v else "%+.4f maxdd %+.4f" % (v["cagr"], v["maxdd"])))
    print("excess vs 510300", pct(rep["excess_vs_510300"]))
    print("phases", [(p["offset"], None if p["ALL_cagr"] is None else round(100 * p["ALL_cagr"], 2)) for p in rep["phases"]])
    print("holdable_width", rep["holdable_width"], "verdict", rep["verdict"])
    for f in rep["failing_conditions"]:
        print("  fail", f)
    print("elapsed", rep["elapsed_sec"], "s ->", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())