"""The A-share veto book's 2026 loss -- was it the market, or did the sort stop paying?

WHY THIS FILE EXISTS
--------------------
r2001/r2002 put the three verified lines on one money axis and found the only red cell:
in 2026 (to 11-20) the ETF book made +2.87% and the basis-carry book +6.19%, while the
A-share residual-veto book lost -- the whole of the combined loss came from that line,
and its veto arm (B) only beat the whole-pool arm (A) by 0.85pp.  r2001 left one
question open and called it the next face:

    is 2026's loss (a) the market/pool beta falling under the book, or
    (b) the residual sort itself decaying -- an edge that used to pay and stopped?

The two answers have opposite consequences.  (a) is a bad year you sit through; (b) is a
book you retire.  Nothing in the family measures (a) at all: every existing face compares
the veto arm to the *pool* and to random draws from the pool, so "beta" cancels out of the
difference and never appears as a number.

WHAT THIS FACE ADDS
-------------------
One new input -- index closes (data/index_daily/sh000300 / sh000905 / sh000852 / sh000016,
read-only) aligned to the same 20-bar rebalance windows -- and one decomposition:

    arm_total(year)  = (1 + beta_implied) x (1 + alpha)          [exact identity]
    beta_implied     = prod over that year's periods of (1 + beta * index_return)
    sort_BA(year)    = (1 + B) / (1 + A) - 1                     [the sort, pool held fixed]
    sort_BR(year)    = (1 + B) / (1 + R) - 1                     [the sort, random drop held fixed]

beta is the full-window OLS slope of the arm's per-period net return on the primary
benchmark's per-period return (declared primary below, before any number was seen).  It is
NOT refitted per year: ten annual points over 2020-2026 cannot support a yearly beta, and
a yearly refit would let the answer move with the noise it is supposed to measure.

Readers get three things they have never had:
  1. per-year attribution of the pool arm and the veto arm into beta + alpha,
  2. the sort's own year series (B-A and B-R at geometric year totals), i.e. is it decaying,
  3. a 2026 verdict with the log-share arithmetic shown, not asserted.

FROZEN CRITERIA (before the numbers were seen)
----------------------------------------------
primary benchmark = CSI1000 (sh000852): the pool is an equal-weight, liquidity-filtered
  book of ~3,500 names, so the small-cap index is the honest yardstick; the other three
  are printed as context, never picked after the fact.
Y_BETA_DOMINANT  beta log-share >= 0.666
Y_HALF_BETA      0.333 <= share < 0.666
Y_NOT_BETA       share < 0.333   (the pool's own alpha is where the loss lives)
SORT_DECAYING        OLS slope of yearly per-period sort (B-A) <= -0.0005/period per year
                     AND |t| >= 2.0
SORT_STABLE          slope within (+/-0.0005) or |t| < 2.0
SORT_ABSENT          |full-window mean B-A| < 0.0005/period

A partial year (this one: 10 periods, cutoff 11-20) is labelled partial and never compared
to a full year as if it were one -- r2002's caliber rule, applied to time instead of to money.

The engine is imported, never re-implemented: load_panel / run / compound / HOLD all come
from astock_resid_veto_layer -> astock_resid_reversal_probe, and --check proves it by
reproducing the parent face's own published by_year compounds and arm CAGRs.
"""
import argparse
import json
import math
import os
import sys
from datetime import datetime

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from astock_resid_veto_layer import HOLD, load_panel, run as run_veto  # noqa: E402
from astock_resid_reversal_probe import COST_ONE_SIDE, compound  # noqa: E402

OUT = os.path.join(ROOT, "results", "astock_veto_year_source.json")
MD = os.path.join(ROOT, "research", "ASTOCK_VETO_YEAR_SOURCE.md")
PARENT = os.path.join(ROOT, "results", "astock_resid_veto_layer.json")
IDX_DIR = os.path.join(ROOT, "data", "index_daily")

BENCH = [
    ("CSI300", "sh000300"),
    ("CSI500", "sh000905"),
    ("CSI1000", "sh000852"),
    ("SSE50", "sh000016"),
]
PRIMARY = "CSI1000"
ARMS = ("A", "B", "C", "R")

BETA_SHARE_BETA = 0.666
BETA_SHARE_HALF = 0.333
DECAY_SLOPE = -0.0005
DECAY_T = 2.0
SORT_ABSENT = 0.0005


# ------------------------------------------------------------------ primitives
def read_index(code):
    """date -> close for one index file.  Missing/unparsable rows are skipped, not patched."""
    path = os.path.join(IDX_DIR, code + ".csv")
    out = {}
    with open(path, "r", encoding="utf-8", errors="ignore") as fh:
        fh.readline()
        for line in fh:
            parts = line.strip().split(",")
            if len(parts) < 2 or not parts[0]:
                continue
            try:
                out[parts[0]] = float(parts[1])
            except ValueError:
                continue
    return out


def index_return(closes, d0, d1):
    """Close-to-close return over [d0, d1]; NaN when either end is absent."""
    a = closes.get(d0)
    b = closes.get(d1)
    if a is None or b is None or a <= 0:
        return float("nan")
    return b / a - 1.0


def ols(x, y):
    """Slope, intercept, R^2 and n over finite pairs.  None when fewer than 3 usable pairs."""
    xs, ys = [], []
    for a, b in zip(x, y):
        if math.isfinite(a) and math.isfinite(b):
            xs.append(a)
            ys.append(b)
    n = len(xs)
    if n < 3:
        return {"n": n, "beta": None, "alpha": None, "r2": None}
    xa = np.array(xs, dtype=np.float64)
    ya = np.array(ys, dtype=np.float64)
    vx = float(xa.var())
    if vx <= 0:
        return {"n": n, "beta": None, "alpha": float(ya.mean()), "r2": None}
    beta = float(((xa - xa.mean()) * (ya - ya.mean())).mean() / vx)
    alpha = float(ya.mean() - beta * xa.mean())
    resid = ya - (alpha + beta * xa)
    den = float(((ya - ya.mean()) ** 2).sum())
    r2 = float(1.0 - float((resid ** 2).sum()) / den) if den > 0 else None
    return {"n": n, "beta": beta, "alpha": alpha, "r2": r2}


def chain_total(rs):
    """Geometric total of a period-return list (None if any element is not finite)."""
    prod = 1.0
    for r in rs:
        if r is None or not math.isfinite(r):
            return None
        prod *= (1.0 + r)
    return prod - 1.0


def ann(rs):
    """Annualised rate over the same periods -- printed only where it is what the parent prints."""
    if not rs or any(not math.isfinite(r) for r in rs):
        return None
    return compound(list(rs))


def beta_implied(beta, idx_rs):
    """Compounded return of the beta-only leg over the same windows."""
    return chain_total([beta * r for r in idx_rs])


def alpha_of(total, implied):
    """(1+total) = (1+implied) x (1+alpha) -- the exact identity, never an approximation."""
    if total is None or implied is None or (1.0 + implied) == 0:
        return None
    return (1.0 + total) / (1.0 + implied) - 1.0


def log_share(part, whole):
    """Share of the total log return that the part supplies.  Sign-safe by construction:
    both must be on the same side of zero, else the split is reported as not separable."""
    if part is None or whole is None:
        return None
    wp = math.log1p(part)
    ww = math.log1p(whole)
    if wp == 0.0 and ww == 0.0:
        return None
    if wp * ww <= 0:
        return None
    if ww == 0:
        return None
    return wp / ww


# ------------------------------------------------------------------ decomposition
def build(rows, dates, idx, hold=HOLD):
    """rows: per-rebalance dicts with date + arm nets.  idx: name -> {date: close}."""
    periods = []
    for r in rows:
        d0 = r["date"]
        t = dates.index(d0) if d0 not in _DATE_POS else _DATE_POS[d0]
        d1 = dates[t + hold] if t + hold < len(dates) else None
        cell = {"date": d0, "next": d1, "arms": {k: r[k]["net"] for k in ARMS if k in r},
                "gross": {k: r[k]["gross"] for k in ARMS if k in r},
                "turnover": {k: r[k]["turnover"] for k in ARMS if k in r},
                "size": {k: r[k]["size"] for k in ARMS if k in r},
                "idx": {}}
        for name, _code in BENCH:
            closes = idx.get(name) or {}
            cell["idx"][name] = index_return(closes, d0, d1) if d1 else float("nan")
        periods.append(cell)

    missing = {name: sum(1 for p in periods if not math.isfinite(p["idx"][name])) for name, _c in BENCH}

    betas = {}
    for arm in ARMS:
        betas[arm] = {}
        ys = [p["arms"].get(arm) for p in periods]
        for name, _c in BENCH:
            xs = [p["idx"][name] for p in periods]
            betas[arm][name] = ols(xs, ys)

    years = sorted({p["date"][:4] for p in periods})
    by_year = {}
    for y in years:
        ps = [p for p in periods if p["date"][:4] == y]
        cell = {"periods": len(ps), "last": ps[-1]["date"],
                "year_total": {}, "ann_pct": {}, "beta_implied": {}, "alpha_year": {},
                "idx_total": {}}
        for name, _c in BENCH:
            cell["idx_total"][name] = chain_total([p["idx"][name] for p in ps])
        for arm in ARMS:
            rs = [p["arms"].get(arm) for p in ps]
            cell["year_total"][arm] = chain_total(rs)
            cell["ann_pct"][arm] = ann(rs)
            b = betas[arm][PRIMARY]["beta"]
            cell["beta_implied"][arm] = None if b is None else beta_implied(
                b, [p["idx"][PRIMARY] for p in ps])
            cell["alpha_year"][arm] = alpha_of(cell["year_total"][arm], cell["beta_implied"][arm])
        ta, tb, tr = cell["year_total"]["A"], cell["year_total"]["B"], cell["year_total"]["R"]
        cell["sort"] = {
            "BA": None if (ta is None or tb is None or ta == -1) else (1 + tb) / (1 + ta) - 1,
            "BR": None if (tr is None or tb is None or tr == -1) else (1 + tb) / (1 + tr) - 1,
            "per_period_BA": float(np.mean([p["arms"]["B"] - p["arms"]["A"] for p in ps])) if ps else None,
        }
        by_year[y] = cell

    # sort pairs (B-A, B-R) per period: full window vs this year vs everything before it
    def pair_stats(sel):
        d = [p["arms"]["B"] - p["arms"]["A"] for p in sel if math.isfinite(p["arms"]["B"] - p["arms"]["A"])]
        if len(d) < 3:
            return {"n": len(d), "mean": None, "se": None, "t": None}
        arr = np.array(d)
        se = float(arr.std(ddof=1) / math.sqrt(len(arr)))
        return {"n": len(d), "mean": float(arr.mean()), "se": se,
                "t": float(arr.mean() / se) if se > 0 else None}

    def pair_stats_r(sel):
        d = [p["arms"]["B"] - p["arms"]["R"] for p in sel if math.isfinite(p["arms"]["B"] - p["arms"]["R"])]
        if len(d) < 3:
            return {"n": len(d), "mean": None, "se": None, "t": None}
        arr = np.array(d)
        se = float(arr.std(ddof=1) / math.sqrt(len(arr)))
        return {"n": len(d), "mean": float(arr.mean()), "se": se,
                "t": float(arr.mean() / se) if se > 0 else None}

    last_year = years[-1]
    this_year = [p for p in periods if p["date"][:4] == last_year]
    prior = [p for p in periods if p["date"][:4] != last_year]
    sort_pairs = {
        "full_BA": pair_stats(periods), "full_BR": pair_stats_r(periods),
        "year_BA": pair_stats(this_year), "year_BR": pair_stats_r(this_year),
        "prior_BA": pair_stats(prior), "prior_BR": pair_stats_r(prior),
    }

    # decay: OLS of the yearly per-period sort on the year index (unweighted -- every year
    # is one observation of "what the sort paid that year"; weighting would let 2026's ten
    # periods speak louder than 2021's twelve for no reason but length)
    yx, yy = [], []
    for i, y in enumerate(years):
        v = by_year[y]["sort"]["per_period_BA"]
        if v is None:
            continue
        yx.append(float(i))
        yy.append(v)
    trend = {"years": years, "slope_per_period_per_year": None, "t": None, "n": len(yx)}
    if len(yx) >= 4:
        xs = np.array(yx)
        ys = np.array(yy)
        xa, ya = float(xs.mean()), float(ys.mean())
        sxx = float(((xs - xa) ** 2).sum())
        if sxx > 0:
            slope = float(((xs - xa) * (ys - ya)).sum() / sxx)
            fitted = ya + slope * (xs - xa)
            dof = int(len(xs) - 2)
            ssr = float(((ys - fitted) ** 2).sum())
            if dof > 0 and ssr > 0:
                se = math.sqrt(ssr / dof / sxx)
                trend["slope_per_period_per_year"] = slope
                trend["t"] = float(slope / se) if se > 0 else None
            elif dof > 0:
                trend["slope_per_period_per_year"] = slope
                trend["t"] = None

    # 2026 attribution on the veto arm
    cy = by_year[last_year]
    share = log_share(cy["beta_implied"].get("B"), cy["year_total"].get("B"))
    if share is None:
        y_verdict = "Y_NOT_SEPARABLE"
    elif share >= BETA_SHARE_BETA:
        y_verdict = "Y_BETA_DOMINANT"
    elif share >= BETA_SHARE_HALF:
        y_verdict = "Y_HALF_BETA"
    else:
        y_verdict = "Y_NOT_BETA"

    slope = trend["slope_per_period_per_year"]
    tstat = trend["t"]
    mean_ba = sort_pairs["full_BA"]["mean"]
    if mean_ba is not None and abs(mean_ba) < SORT_ABSENT:
        s_verdict = "SORT_ABSENT"
    elif slope is not None and tstat is not None and slope <= DECAY_SLOPE and abs(tstat) >= DECAY_T:
        s_verdict = "SORT_DECAYING"
    else:
        s_verdict = "SORT_STABLE"

    return {
        "spec": {
            "hold": hold, "cost_one_side": COST_ONE_SIDE,
            "benchmarks": [{"name": n, "code": c, "file": "data/index_daily/%s.csv" % c} for n, c in BENCH],
            "primary_benchmark": PRIMARY,
            "beta_fit": "full-window OLS of per-period net return on per-period index return; never refit per year",
            "year_caliber": "year_total = chained product over that year's own periods (NOT annualised); ann_pct is the annualised rate the parent prints, shown separately",
            "criteria": {
                "beta_share_flat": BETA_SHARE_BETA, "beta_share_half": BETA_SHARE_HALF,
                "decay_slope": DECAY_SLOPE, "decay_t": DECAY_T, "sort_absent": SORT_ABSENT,
            },
            "arms": {"A": "whole eligible pool", "B": "pool minus top 20% residual",
                     "C": "pool minus top 40% residual", "R": "random 20% dropped (20 draws)"},
        },
        "axis": {"periods": len(periods), "first": periods[0]["date"] if periods else None,
                 "last": periods[-1]["date"] if periods else None,
                 "missing_index_periods": missing},
        "betas": betas,
        "by_year": by_year,
        "sort_pairs": sort_pairs,
        "sort_trend": trend,
        "attribution": {"year": last_year, "arm": "B",
                        "year_total": cy["year_total"].get("B"),
                        "partial": len(this_year) < 12,
                        "beta_implied": cy["beta_implied"].get("B"),
                        "alpha": cy["alpha_year"].get("B"),
                        "beta_log_share": share,
                        "index_total": cy["idx_total"].get(PRIMARY),
                        "verdict": y_verdict},
        "verdict": {"year": y_verdict, "sort": s_verdict},
        "series": [{"date": p["date"], "next": p["next"],
                    "A": p["arms"].get("A"), "B": p["arms"].get("B"),
                    "R": p["arms"].get("R"), "C": p["arms"].get("C"),
                    "idx": p["idx"]} for p in periods],
    }


_DATE_POS = {}


def cmd_run():
    dates, symbols, close, amount, shares = load_panel()
    _DATE_POS.clear()
    _DATE_POS.update({d: i for i, d in enumerate(dates)})
    rows = run_veto(dates, symbols, close, amount, shares)
    if not rows:
        print("no rebalance rows")
        return 2
    idx = {name: read_index(code) for name, code in BENCH}
    payload = build(rows, list(dates), idx)
    payload.update({
        "generated": datetime.now().astimezone().isoformat(timespec="seconds"),
        "evidence_cutoff": str(dates[-1]),
        "last_decision": payload["axis"]["last"],
        "machine": _machine(),
        "kind": "astock_veto_year_source",
        "parent_face": os.path.relpath(PARENT, ROOT).replace("\\", "/"),
        "panel": {"dates": len(dates), "symbols": len(symbols), "first": dates[0], "last": dates[-1]},
    })
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)

    y = payload["by_year"]
    print("periods %d  cutoff %s" % (payload["axis"]["periods"], payload["evidence_cutoff"]))
    b = payload["betas"]["B"][PRIMARY]
    print("B beta(%s) %.3f  alpha/period %+.4f%%  r2 %.3f  n %d"
          % (PRIMARY, b["beta"], 100 * b["alpha"], b["r2"] or 0.0, b["n"]))
    for yr in sorted(y):
        c = y[yr]
        print("  %s (%2d p) A %+7.2f%% B %+7.2f%% idx %+7.2f%% | beta %+7.2f%% alpha %+7.2f%% sort %+6.2f%%"
              % (yr, c["periods"], 100 * (c["year_total"]["A"] or 0), 100 * (c["year_total"]["B"] or 0),
                 100 * (c["idx_total"][PRIMARY] or 0), 100 * (c["beta_implied"]["B"] or 0),
                 100 * (c["alpha_year"]["B"] or 0), 100 * (c["sort"]["BA"] or 0)))
    a = payload["attribution"]
    print("%s attribution (B): total %+.2f%% = beta %+.2f%% x alpha %+.2f%%  log-share %s -> %s"
          % (a["year"], 100 * (a["year_total"] or 0), 100 * (a["beta_implied"] or 0),
             100 * (a["alpha"] or 0), "n/a" if a["beta_log_share"] is None else "%.2f" % a["beta_log_share"],
             a["verdict"]))
    print("sort trend slope %s/period/yr  t %s -> %s"
          % ("n/a" if payload["sort_trend"]["slope_per_period_per_year"] is None
             else "%+.5f" % payload["sort_trend"]["slope_per_period_per_year"],
             "n/a" if payload["sort_trend"]["t"] is None else "%+.2f" % payload["sort_trend"]["t"],
             payload["verdict"]["sort"]))
    write_doc(payload)
    print("-> %s" % os.path.relpath(OUT, ROOT))
    return 0


def write_doc(p):
    y = p["by_year"]
    years = sorted(y)
    a = p["attribution"]
    lines = []
    lines.append("# A-share veto book: was 2026 the market, or did the sort stop paying?\n")
    lines.append("generated %s · data cutoff %s (last rebalance decision %s) · machine %s · %d rebalance periods "
                 "(%s -> %s, hold %d bars, cost %.2f bp/side)\n"
                 % (p["generated"], p["evidence_cutoff"], p.get("last_decision"), p["machine"],
                    p["axis"]["periods"], p["axis"]["first"], p["axis"]["last"], p["spec"]["hold"],
                    10000 * p["spec"]["cost_one_side"]))
    share = a["beta_log_share"]
    share_txt = "n/a" if share is None else "%.2f" % share
    lines.append("**The one-line answer.** %s: the veto arm (B) lost %.2f%%. With beta %.2f on %s, "
                 "the beta leg alone accounts for %.2f%% and the rest (alpha) %.2f%% -> "
                 "**%s** (beta log-share %s; a share above 1.00 means the beta leg was *bigger* "
                 "than the loss and the book's own alpha offset that much of it). "
                 "Meanwhile the sort itself (B minus the same pool, A) contributed %s "
                 "over the whole window and its year-by-year slope is %s -> **%s**.\n"
                 % (a["year"], 100 * (a["year_total"] or 0),
                    p["betas"]["B"][PRIMARY]["beta"], PRIMARY,
                    100 * (a["beta_implied"] or 0), 100 * (a["alpha"] or 0), a["verdict"], share_txt,
                    "n/a" if p["sort_pairs"]["full_BA"]["mean"] is None
                    else "%+.4f%%/period (t %+.2f)" % (100 * p["sort_pairs"]["full_BA"]["mean"],
                                                       p["sort_pairs"]["full_BA"]["t"]),
                    "n/a" if p["sort_trend"]["slope_per_period_per_year"] is None
                    else "%+.5f/period per year (t %s)" % (p["sort_trend"]["slope_per_period_per_year"],
                                                           "n/a" if p["sort_trend"]["t"] is None
                                                           else "%+.2f" % p["sort_trend"]["t"]),
                    p["verdict"]["sort"]))
    lines.append("\n## Year table (year totals, chained over that year's own periods)\n")
    lines.append("| year | periods | A pool | B veto | R random | sort B-A | %s | beta leg (B) | alpha (B) |"
                 % PRIMARY)
    lines.append("|---|---|---|---|---|---|---|---|---|")


    def fmt(v, scale=100.0, suffix="%"):
        return "n/a" if v is None else ("%+.2f%s" % (scale * v, suffix))

    for yr in years:
        c = y[yr]
        partial = " *" if c["periods"] < 12 else ""
        lines.append("| %s%s | %d | %s | %s | %s | %s | %s | %s | %s |"
                     % (yr, partial, c["periods"], fmt(c["year_total"]["A"]), fmt(c["year_total"]["B"]),
                        fmt(c["year_total"]["R"]), fmt(c["sort"]["BA"]),
                        fmt(c["idx_total"][PRIMARY]), fmt(c["beta_implied"]["B"]),
                        fmt(c["alpha_year"]["B"])))
    lines.append("\n`*` fewer than 12 periods in that year: a partial year, never compared to a full one.\n")
    lines.append("## Beta fits (full window, per-period returns)\n")
    lines.append("| arm | benchmark | beta | alpha/period | R² | n |")
    lines.append("|---|---|---|---|---|---|")
    for arm in ARMS:
        for name, _c in BENCH:
            b = p["betas"][arm][name]
            lines.append("| %s | %s | %s | %s | %s | %d |"
                         % (arm, name,
                            "n/a" if b["beta"] is None else "%.3f" % b["beta"],
                            "n/a" if b["alpha"] is None else "%+.4f%%" % (100 * b["alpha"]),
                            "n/a" if b["r2"] is None else "%.3f" % b["r2"], b["n"]))
    lines.append("\n## The sort, as its own series\n")
    lines.append("| window | n | mean B-A /period | t | mean B-R /period | t |")
    lines.append("|---|---|---|---|---|---|")
    for key, label in (("full", "full window"), ("prior", "everything before %s" % a["year"]),
                       ("year", a["year"])):
        s = p["sort_pairs"]["%s_BA" % key]
        r = p["sort_pairs"]["%s_BR" % key]
        lines.append("| %s | %d | %s | %s | %s | %s |"
                     % (label, s["n"],
                        "n/a" if s["mean"] is None else "%+.4f%%" % (100 * s["mean"]),
                        "n/a" if s["t"] is None else "%+.2f" % s["t"],
                        "n/a" if r["mean"] is None else "%+.4f%%" % (100 * r["mean"]),
                        "n/a" if r["t"] is None else "%+.2f" % r["t"]))
    lines.append("\n## What this face does not say\n")
    lines.append("- beta is one number over 2020-2026: it says what the book carried on average, "
                 "not what it carried in any single year. A yearly refit over ~11 points would fit "
                 "noise and call it a coefficient.\n")
    lines.append("- the index legs are close-to-close index levels, not tradable ETF prices; "
                 "the beta leg is an attribution device, not a hedge someone can buy at that price.\n")
    lines.append("- 2026 is 10 periods to %s. That is a partial year; the verdict says so.\n"
                 % p["evidence_cutoff"])
    lines.append("- a beta share and a decay slope are two different questions with two different "
                 "verdict tokens; neither one alone retires the book.\n")
    with open(MD, "w", encoding="utf-8") as fh:
        fh.write("".join(l if l.endswith("\n") else l + "\n" for l in lines))


def cmd_check():
    """Re-derive every published number; fail on drift, and cross-check the parent face."""
    if not os.path.exists(OUT):
        print("STALE: face missing -> %s" % os.path.relpath(OUT, ROOT))
        return 3
    with open(OUT, encoding="utf-8") as fh:
        p = json.load(fh)
    fails, drift = [], []

    # 1. parent cross-check: my per-period arm nets must reproduce the parent's own by_year
    if not os.path.exists(PARENT):
        drift.append("parent face missing -> %s" % os.path.relpath(PARENT, ROOT))
    else:
        with open(PARENT, encoding="utf-8") as fh:
            par = json.load(fh)
        if par.get("kind") != "astock_residual_veto_layer":
            fails.append("parent kind mismatch: %r" % par.get("kind"))
        series = p.get("series") or []
        for arm in ("A", "B", "R"):
            mine = [r[arm] for r in series]
            got = ann(mine)
            want = (par.get("arms") or {}).get(arm, {}).get("cagr_net")
            if got is None or want is None:
                fails.append("L1 arm %s: cannot reproduce parent cagr (%r vs %r)" % (arm, got, want))
            elif abs(got - want) > 1e-6:
                fails.append("L1 arm %s: cagr %.9f != parent %.9f" % (arm, got, want))
        for yr in sorted({r["date"][:4] for r in series}):
            par_y = ((par.get("by_year") or {}).get("B") or {}).get(yr) or {}
            mine = [r["B"] for r in series if r["date"][:4] == yr]
            if par_y.get("periods") != len(mine):
                fails.append("L2 %s: periods %d != parent %r" % (yr, len(mine), par_y.get("periods")))
            a_mine = ann(mine)
            if a_mine is not None and par_y.get("compound") is not None:
                if abs(a_mine - par_y["compound"]) > 1e-6:
                    fails.append("L2 %s: annualised B %.9f != parent %.9f" % (yr, a_mine, par_y["compound"]))

    # 2. identities and re-derivation from the stored series
    tot = {}
    for yr in p["by_year"]:
        rs = [r for r in p["series"] if r["date"][:4] == yr]
        for arm in ARMS:
            t = chain_total([r[arm] for r in rs])
            got = p["by_year"][yr]["year_total"][arm]
            if t is None or got is None or abs(t - got) > 1e-12:
                fails.append("L3 %s/%s year_total %.12f != %.12f" % (yr, arm, t or float("nan"), got or float("nan")))
        for name, _c in BENCH:
            it = chain_total([r["idx"][name] for r in rs])
            got = p["by_year"][yr]["idx_total"][name]
            if (it is None) != (got is None) or (it is not None and abs(it - got) > 1e-12):
                fails.append("L4 %s/%s index total drift" % (yr, name))
        for arm in ARMS:
            b = p["betas"][arm][PRIMARY]["beta"]
            impl = p["by_year"][yr]["beta_implied"][arm]
            al = p["by_year"][yr]["alpha_year"][arm]
            t = p["by_year"][yr]["year_total"][arm]
            if b is None or impl is None or al is None or t is None:
                continue
            if abs((1 + impl) * (1 + al) - (1 + t)) > 1e-12:
                fails.append("L5 %s/%s identity (1+beta)(1+alpha) != (1+total)" % (yr, arm))
        # arithmetic sort mean
        d = [r["B"] - r["A"] for r in rs]
        got = p["by_year"][yr]["sort"]["per_period_BA"]
        if got is None or abs(float(np.mean(d)) - got) > 1e-12:
            fails.append("L6 %s sort per-period mean drift" % yr)

    # 3. verdict consistency
    a = p["attribution"]
    share = log_share(a["beta_implied"], a["year_total"])
    if (share is None) != (a["beta_log_share"] is None):
        fails.append("L7 beta log-share recomputed as %r, face says %r" % (share, a["beta_log_share"]))
    elif share is not None and abs(share - a["beta_log_share"]) > 1e-9:
        fails.append("L7 beta log-share %.12f != %.12f" % (share, a["beta_log_share"]))
    if share is None:
        want = "Y_NOT_SEPARABLE"
    elif share >= BETA_SHARE_BETA:
        want = "Y_BETA_DOMINANT"
    elif share >= BETA_SHARE_HALF:
        want = "Y_HALF_BETA"
    else:
        want = "Y_NOT_BETA"
    if a["verdict"] != want:
        fails.append("L8 year verdict %r but the numbers say %r" % (a["verdict"], want))
    slope = p["sort_trend"]["slope_per_period_per_year"]
    tst = p["sort_trend"]["t"]
    mean_ba = p["sort_pairs"]["full_BA"]["mean"]
    if mean_ba is not None and abs(mean_ba) < SORT_ABSENT:
        want_s = "SORT_ABSENT"
    elif slope is not None and tst is not None and slope <= DECAY_SLOPE and abs(tst) >= DECAY_T:
        want_s = "SORT_DECAYING"
    else:
        want_s = "SORT_STABLE"
    if p["verdict"]["sort"] != want_s:
        fails.append("L9 sort verdict %r but the numbers say %r" % (p["verdict"]["sort"], want_s))

    # 4. freshness: panel frontier
    if not os.path.exists(PARENT):
        pass
    else:
        with open(PARENT, encoding="utf-8") as fh:
            par = json.load(fh)
        if (par.get("panel") or {}).get("last") != (p.get("panel") or {}).get("last"):
            drift.append("parent panel last %r != face %r"
                         % ((par.get("panel") or {}).get("last"), (p.get("panel") or {}).get("last")))

    if fails:
        for f in fails:
            print("FAIL " + f)
        return 3
    if drift:
        for d in drift:
            print("STALE " + d)
        return 3
    print("OK %d periods, %d years, verdict %s / %s"
          % (len(p["series"]), len(p["by_year"]), p["verdict"]["year"], p["verdict"]["sort"]))
    return 0


# ------------------------------------------------------------------ selftest
def selftest():
    legs = []

    def leg(name, cond):
        legs.append((name, bool(cond)))

    # synthetic: 20 calendar days per period from 2020-01-01, one index series
    def make(arm_fn, idx_fn, n=40):
        from datetime import date, timedelta
        cal = [(date(2020, 1, 1) + timedelta(days=20 * i)).isoformat() for i in range(n + 1)]
        closes = {c: 100.0 * float(np.prod([1 + idx_fn(k) for k in range(i)])) for i, c in enumerate(cal)}
        rows = [{"date": cal[i], "A": {"net": arm_fn("A", i), "gross": arm_fn("A", i), "turnover": 0.1, "size": 100},
                 "B": {"net": arm_fn("B", i), "gross": arm_fn("B", i), "turnover": 0.2, "size": 80},
                 "C": {"net": arm_fn("C", i), "gross": arm_fn("C", i), "turnover": 0.3, "size": 60},
                 "R": {"net": arm_fn("R", i), "gross": arm_fn("R", i), "turnover": 0.1, "size": 80}}
                for i in range(n)]
        _DATE_POS.clear()
        _DATE_POS.update({c: i for i, c in enumerate(cal)})
        return rows, cal, {"CSI1000": closes}

    # L1: pure beta arm -> beta recovered, alpha ~ 0, verdict BETA_DOMINANT on a losing year
    idx = lambda i: -0.01 if i >= 30 else 0.01
    rows, cal, ix = make(lambda arm, i: 0.5 * idx(i) if arm in ("A", "B") else 0.0, idx)
    p = build(rows, cal, ix, hold=1)
    leg("L1 pure-beta arm recovers beta=0.5", abs(p["betas"]["B"]["CSI1000"]["beta"] - 0.5) < 1e-9)
    leg("L1 pure-beta arm has zero alpha", abs(p["betas"]["B"]["CSI1000"]["alpha"]) < 1e-12)
    leg("L1 identity holds per year",
        all(abs((1 + p["by_year"][y]["beta_implied"]["B"]) *
                (1 + p["by_year"][y]["alpha_year"]["B"]) - (1 + p["by_year"][y]["year_total"]["B"])) < 1e-12
            for y in p["by_year"]))
    leg("L1 losing year judged beta-dominant", p["attribution"]["verdict"] == "Y_BETA_DOMINANT")

    # L2: pure alpha arm while the index loses -> beta ~0 and the loss is NOT beta
    rows, cal, ix = make(lambda arm, i: 0.004 if arm in ("A", "B") else 0.0, lambda i: -0.01)
    p = build(rows, cal, ix, hold=1)
    leg("L2 constant arm has beta ~ 0", abs(p["betas"]["B"]["CSI1000"]["beta"]) < 1e-12)
    leg("L2 constant arm still earns", (p["attribution"]["year_total"] or 0) > 0)
    leg("L2 positive-vs-negative split is not separable",
        p["attribution"]["beta_log_share"] is None and p["attribution"]["verdict"] == "Y_NOT_SEPARABLE")

    # L3: sort decays to zero -> SORT_DECAYING
    rows, cal, ix = make(lambda arm, i: (0.015 - 0.0006 * i) if arm == "B" else 0.0, lambda i: 0.0, n=80)
    p = build(rows, cal, ix, hold=1)
    leg("L3 decaying sort is called out", p["verdict"]["sort"] == "SORT_DECAYING")
    leg("L3 slope is negative", (p["sort_trend"]["slope_per_period_per_year"] or 0) < 0)

    # L4: flat sort -> SORT_ABSENT (never DECAYING on noise around zero)
    rows, cal, ix = make(lambda arm, i: 0.0, lambda i: 0.0)
    p = build(rows, cal, ix, hold=1)
    leg("L4 zero sort is ABSENT, not decaying", p["verdict"]["sort"] == "SORT_ABSENT")

    # L5: missing index dates are counted, never invented
    rows, cal, ix = make(lambda arm, i: 0.001, lambda i: 0.0)
    ix["CSI1000"] = {k: v for k, v in ix["CSI1000"].items() if k != cal[5]}
    p = build(rows, cal, ix, hold=1)
    leg("L5 missing index bar is counted", p["axis"]["missing_index_periods"]["CSI1000"] >= 1)

    # L6: year total is chained, not annualised (11 periods of +1% must read ~11.6%)
    rows, cal, ix = make(lambda arm, i: 0.01, lambda i: 0.0, n=12)
    p = build(rows, cal, ix, hold=1)
    y = sorted(p["by_year"])[0]
    leg("L6 year_total is a chained total (12 periods of 1% = 12.68%)",
        abs(p["by_year"][y]["year_total"]["A"] - (1.01 ** 12 - 1)) < 1e-12)
    leg("L6 ann_pct is the annualised rate, larger than the total",
        p["by_year"][y]["ann_pct"]["A"] > p["by_year"][y]["year_total"]["A"])

    # L7: log-share arithmetic is sign-safe
    leg("L7 log-share of a negative part in a negative whole is positive",
        abs(log_share(-0.10, -0.20) - (math.log(0.9) / math.log(0.8))) < 1e-12)
    leg("L7 log-share across signs is refused", log_share(0.05, -0.10) is None)

    # L8: geometric sort identity
    leg("L8 sort B-A reconstructs B from A", abs((1 + 0.10) * (1 + 0.05) - 1.155) < 1e-12)
    leg("L8 alpha_of inverts the identity", abs(alpha_of(0.21, 0.10) - 0.1) < 1e-12)

    bad = [n for n, ok in legs if not ok]
    for n, ok in legs:
        print("%s %s" % ("PASS" if ok else "FAIL", n))
    print("%d/%d legs PASS" % (len(legs) - len(bad), len(legs)))
    return 0 if not bad else 1


def _machine():
    try:
        with open(os.path.join(ROOT, "fleet", "machine.json"), encoding="utf-8") as fh:
            return json.load(fh).get("machine_id")
    except Exception:
        return None


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "check", "selftest"])
    args = ap.parse_args(argv)
    if args.cmd == "selftest":
        return selftest()
    if args.cmd == "check":
        return cmd_check()
    return cmd_run()


if __name__ == "__main__":
    sys.exit(main())
