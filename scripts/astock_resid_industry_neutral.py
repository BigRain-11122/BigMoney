#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A-share residual reversal: does the industry dimension change the answer?

Why this face exists
--------------------
r1862 (scripts/astock_resid_reversal_probe.py) closed the beta+log-size
neutralisation question with a negative verdict and left exactly one hole in the
open: "行业中性化那半条缺行业映射源、如实留白" (the industry half was left blank
because no industry map source was on disk).

The map was on disk all along, just not in the panel: data/basic/sw_stock_classify_2021.xls
carries 12,925 rows of (stock code, entry date, industry code, update date) covering
5,221 of 5,221 panel symbols -- a point-in-time industry history, not a snapshot.
So the blank can be filled without any new download.

This probe asks one question, frozen before the run:

    after the beta and log-size exposures are already removed (r1862's arm),
    does adding the industry dimension -- either as a cross-sectional dummy in the
    same regression, or as a rank computed inside each industry -- make the 20-day
    reversal residual predict the next 20 days better, worse, or the same?

It is a census: no prereg, no registration, no pool burn, no adoption. Every arm
prints beside the others so a negative answer is as readable as a positive one.

Frozen criterion (written here, before any run; not tuned afterwards)
---------------------------------------------------------------------
Let g = |mean IC(industry arm)| - |mean IC(r1862 beta+size arm)| on the same panel,
the same rebalances, the same eligible set.

    INDUSTRY_NEUTRAL_HELPS  g >= +0.005 AND |t(industry)| >= 2.0
                            AND long-short net annual > 0
                            AND implementable Q1 excess improves vs the beta+size arm
    INDUSTRY_NEUTRAL_HURTS  g <= -0.005
    WITHIN_NOISE            otherwise

The within-industry rank arm is reported as a second reading with its own line; it
does not feed the main verdict (it answers a different question: "is the ordering
inside an industry better than the ordering across industries?").

Data
----
data/astock_daily/per/<sym>.csv          (reused through r1862's loader, byte-for-byte)
data/basic/sw_stock_classify_2021.xls    (PIT industry: latest entry_date <= rebalance date)

Point-in-time rule: a name whose first industry entry date is after the rebalance date
is DROPPED from that rebalance (not back-filled). The drop count is published per
rebalance so the reader can see how much of the early sample the rule costs.

Usage
-----
    python scripts/astock_resid_industry_neutral.py run [--stride 20]
    python scripts/astock_resid_industry_neutral.py selftest
    python scripts/astock_resid_industry_neutral.py --check
"""
from __future__ import annotations

import argparse
import bisect
import json
import math
import os
import sys
from datetime import datetime, timezone

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import astock_resid_reversal_probe as base  # noqa: E402  (single source: loader+maths)

SW_XLS = os.path.join(ROOT, "data", "basic", "sw_stock_classify_2021.xls")
OUT = os.path.join(ROOT, "results", "astock_resid_industry_neutral.json")

COST_ONE_SIDE = base.COST_ONE_SIDE
HOLD = base.HOLD
LOOKBACK_BETA = base.LOOKBACK_BETA
MIN_AMOUNT_20D = base.MIN_AMOUNT_20D
MIN_BARS = base.MIN_BARS
FIRST_DATE = base.FIRST_DATE

IC_GAIN_MIN = 0.005
T_MIN = 2.0
MIN_GROUP_MEMBERS = 3  # industries thinner than this are pooled into OTHER
INDUSTRY_LEVEL_DIGITS = 2  # first two digits of the code = the top-level industry


# ---------------------------------------------------------------- industry map
def load_industry(path: str = SW_XLS) -> dict:
    """Return {symbol: (entry_dates_sorted, industry_codes)} -- point-in-time history."""
    import pandas as pd

    df = pd.read_excel(path, dtype={"股票代码": str, "行业代码": str})
    need = {"股票代码", "计入日期", "行业代码"}
    missing = need - set(df.columns)
    if missing:
        raise SystemExit("industry file missing columns: %s" % sorted(missing))

    df = df.dropna(subset=["股票代码", "计入日期", "行业代码"])
    df["sym"] = df["股票代码"].astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(6)
    df["day"] = df["计入日期"].astype(str).str[:10]
    df["ind"] = df["行业代码"].astype(str).str.strip().str[:INDUSTRY_LEVEL_DIGITS]

    out = {}
    for sym, g in df.groupby("sym"):
        gg = g.sort_values("day")
        # a later entry supersedes an earlier one; keep the last code per day
        gg = gg.drop_duplicates(subset=["day"], keep="last")
        out[sym] = (list(gg["day"]), list(gg["ind"]))
    return out


def industry_at(hist, sym: str, day: str):
    """Latest industry code whose entry date <= day, else None (never back-filled)."""
    item = hist.get(sym)
    if not item:
        return None
    days, inds = item
    i = bisect.bisect_right(days, day) - 1
    if i < 0:
        return None
    return inds[i]


# ---------------------------------------------------------------- maths
def industry_residual(r20, beta, logsize, groups) -> np.ndarray:
    """Residual of r20 on [1, beta, logsize, industry dummies].

    Industries with fewer than MIN_GROUP_MEMBERS members are pooled into one OTHER
    category so the dummy block cannot eat the sample.
    """
    n = len(r20)
    counts = {}
    for g in groups:
        counts[g] = counts.get(g, 0) + 1
    rare = {g for g, c in counts.items() if c < MIN_GROUP_MEMBERS}
    labels = ["OTHER" if g in rare else g for g in groups]

    keep = sorted({g for g in labels}, key=lambda x: (-counts.get(x, 0), x))
    # drop the first level as the reference so the design matrix stays identified
    dummies = keep[1:] if len(keep) > 1 else []
    cols = [np.ones(n), np.asarray(beta, dtype=float), np.asarray(logsize, dtype=float)]
    for lvl in dummies:
        cols.append(np.array([1.0 if g == lvl else 0.0 for g in labels]))
    X = np.column_stack(cols)
    coef, *_ = np.linalg.lstsq(X, np.asarray(r20, dtype=float), rcond=None)
    return np.asarray(r20, dtype=float) - X @ coef


def rank_within_industry(groups, values) -> np.ndarray:
    """Average-tie rank inside each industry, scaled to (0,1]; single-member -> 0.5."""
    values = np.asarray(values, dtype=float)
    out = np.full(len(values), 0.5)
    buckets = {}
    for i, g in enumerate(groups):
        buckets.setdefault(g, []).append(i)
    for idx in buckets.values():
        if len(idx) < 2:
            continue
        sub = base.rank01(values[idx])
        out[idx] = sub
    return out


def quintile(fractions) -> np.ndarray:
    return np.clip((np.asarray(fractions) * 5).astype(int), 0, 4)


# ---------------------------------------------------------------- core
def run(dates, symbols, close, amount, shares, hist, stride: int = HOLD):
    rets = base.daily_returns(close)
    mkt = base.market_return(rets)
    start = 0
    while start < len(dates) and dates[start] < FIRST_DATE:
        start += 1
    start = max(start, LOOKBACK_BETA)

    rows = []
    t = start
    while t + HOLD < len(dates):
        d = dates[t]
        c0 = close[t]
        c_past = close[t - HOLD]
        c_fwd = close[t + HOLD]
        with np.errstate(invalid="ignore", divide="ignore"):
            r20 = c0 / c_past - 1.0
            f20 = c_fwd / c0 - 1.0
        amt_win = amount[max(0, t - HOLD + 1):t + 1]
        with np.errstate(invalid="ignore"):
            amt20 = np.nanmean(amt_win, axis=0)
        win = rets[t - LOOKBACK_BETA + 1:t + 1]
        nbars = np.sum(np.isfinite(win), axis=0)
        beta = base.beta_window(win, mkt[t - LOOKBACK_BETA + 1:t + 1])
        with np.errstate(invalid="ignore", divide="ignore"):
            logsize = np.log(c0 * shares[t])

        ok = (
            np.isfinite(r20)
            & np.isfinite(f20)
            & np.isfinite(beta)
            & np.isfinite(logsize)
            & (nbars >= MIN_BARS)
            & (amt20 >= MIN_AMOUNT_20D)
        )
        n_eligible = int(np.sum(ok))
        cols = np.where(ok)[0]
        groups = [industry_at(hist, symbols[j], d) for j in cols]
        mapped = np.array([g is not None for g in groups], dtype=bool)
        n_dropped = int(np.sum(~mapped))
        if np.sum(mapped) < 60:
            t += stride
            continue

        cols = cols[mapped]
        groups = [g for g, m in zip(groups, mapped) if m]
        rr = r20[cols]
        bb = beta[cols]
        ll = logsize[cols]
        ff = f20[cols]
        mean_f = float(np.mean(ff))

        resid = base.cross_sectional_residual(rr, bb, ll)          # r1862 arm
        ind_resid = industry_residual(rr, bb, ll, groups)          # this face, regression arm
        ind_rank = rank_within_industry(groups, rr)                # this face, rank arm

        q_ind = quintile(base.rank01(ind_resid))
        q_rk = quintile(base.rank01(ind_rank))
        q_res = quintile(base.rank01(resid))

        def qmeans(qarr):
            return [float(np.mean(ff[qarr == k])) if np.any(qarr == k) else float("nan")
                    for k in range(5)]

        qi = qmeans(q_ind)
        qk = qmeans(q_rk)
        qr = qmeans(q_res)

        rows.append({
            "date": d,
            "n": int(len(cols)),
            "n_eligible_before_industry": n_eligible,
            "n_dropped_no_industry": n_dropped,
            "n_industries": int(len({g for g in groups})),
            "ic_resid": base.spearman(resid, ff),
            "ic_ind": base.spearman(ind_resid, ff),
            "ic_rankind": base.spearman(ind_rank, ff),
            "ic_raw": base.spearman(rr, ff),
            "q_ind": qi,
            "q_rankind": qk,
            "q_resid": qr,
            "ls_ind_net": qi[0] - qi[4] - 2 * COST_ONE_SIDE,
            "ls_rankind_net": qk[0] - qk[4] - 2 * COST_ONE_SIDE,
            "ls_resid_net": qr[0] - qr[4] - 2 * COST_ONE_SIDE,
            "q1_excess_ind": qi[0] - mean_f,
            "q1_excess_rankind": qk[0] - mean_f,
            "q1_excess_resid": qr[0] - mean_f,
            # what the implementable rank-arm long leg actually holds, relative to the panel:
            # a +Q1 excess that is only a small-size tilt must be labelled as such (r1865 rule)
            "size_expo_rankind_q1": float(np.mean(ll[q_rk == 0])) - float(np.mean(ll)),
            "beta_expo_rankind_q1": float(np.mean(bb[q_rk == 0])) - float(np.mean(bb)),
            "n_industries_rankind_q1": int(len({g for g, k in zip(groups, q_rk) if k == 0})),
        })
        t += stride

    return rows


def summarise(rows, key):
    vals = np.array([r[key] for r in rows if np.isfinite(r.get(key, float("nan")))])
    if len(vals) < 3:
        return {"n": int(len(vals)), "mean": None, "t": None}
    sd = float(vals.std(ddof=1))
    mean = float(vals.mean())
    t = mean / (sd / math.sqrt(len(vals))) if sd > 0 else None
    return {"n": int(len(vals)), "mean": mean, "t": t, "hit": float(np.mean(vals > 0))}


def summarise_array(vals):
    a = np.array([v for v in vals if np.isfinite(v)], dtype=np.float64)
    if len(a) < 3:
        return {"n": int(len(a)), "mean": None, "t": None}
    sd = float(a.std(ddof=1))
    mean = float(a.mean())
    t = mean / (sd / math.sqrt(len(a))) if sd > 0 else None
    return {"n": int(len(a)), "mean": mean, "t": t, "hit": float(np.mean(a > 0))}


def verdict_of(rows):
    """Frozen decision rule (see module docstring). Returns (verdict, details)."""
    s_r = summarise(rows, "ic_resid")
    s_i = summarise(rows, "ic_ind")
    s_k = summarise(rows, "ic_rankind")
    ls_ind = base.compound([r["ls_ind_net"] for r in rows])
    ls_rk = base.compound([r["ls_rankind_net"] for r in rows])
    ls_res = base.compound([r["ls_resid_net"] for r in rows])
    q1_ind = base.compound([r["q1_excess_ind"] for r in rows])
    q1_rk = base.compound([r["q1_excess_rankind"] for r in rows])
    q1_res = base.compound([r["q1_excess_resid"] for r in rows])

    details = {
        "ic_resid": s_r, "ic_ind": s_i, "ic_rankind": s_k,
        "ls_ind_net_annual": ls_ind, "ls_rankind_net_annual": ls_rk,
        "ls_resid_net_annual": ls_res,
        "q1_excess_ind_annual": q1_ind, "q1_excess_rankind_annual": q1_rk,
        "q1_excess_resid_annual": q1_res,
    }
    if s_r["mean"] is None or s_i["mean"] is None:
        return "NOT_ENOUGH_REBALANCES", details

    gain = abs(s_i["mean"]) - abs(s_r["mean"])
    details["ic_gain_abs"] = gain
    details["same_sign"] = (s_i["mean"] < 0) == (s_r["mean"] < 0)

    if (gain >= IC_GAIN_MIN
            and s_i["t"] is not None and abs(s_i["t"]) >= T_MIN
            and (ls_ind or 0.0) > 0
            and q1_ind is not None and q1_res is not None and q1_ind > q1_res):
        return "INDUSTRY_NEUTRAL_HELPS", details
    if gain <= -IC_GAIN_MIN:
        return "INDUSTRY_NEUTRAL_HURTS", details
    return "WITHIN_NOISE", details


# ---------------------------------------------------------------- selftest
def selftest() -> int:
    legs = []

    hist = {"000001": (["2015-10-27", "2021-07-30"], ["440101", "480301"]),
            "600000": (["2019-01-02"], ["220101"])}

    # L1 latest entry at or before the day
    legs.append(("industry_at picks the latest prior entry",
                 industry_at(hist, "000001", "2022-01-01") == "480301"
                 and industry_at(hist, "000001", "2018-05-05") == "440101"))
    # L2 no back-fill before the first entry
    legs.append(("industry_at is None before the first entry",
                 industry_at(hist, "600000", "2018-12-31") is None))
    # L3 unknown symbol is None, not an exception
    legs.append(("industry_at unknown symbol -> None", industry_at(hist, "999999", "2022-01-01") is None))

    # L4 dummies absorb a pure industry-level shift
    n = 60
    groups = ["A"] * 20 + ["B"] * 20 + ["C"] * 20
    shift = {"A": 0.05, "B": -0.02, "C": 0.01}
    r20 = np.array([shift[g] for g in groups]) + 0.0001 * np.arange(n)
    beta = np.zeros(n)
    size = np.zeros(n)
    res = industry_residual(r20, beta, size, groups)
    legs.append(("industry dummies absorb the group means",
                 float(np.max(np.abs([np.mean(res[np.array(groups) == g]) for g in "ABC"]))) < 5e-4))

    # L5 a third signal orthogonal by construction is kept
    parts = []
    for k, g in enumerate("ABC"):
        idx = [i for i, x in enumerate(groups) if x == g]
        parts.append(base.cross_sectional_residual(
            r20[idx] + r20[idx][::-1], np.zeros(len(idx)), np.zeros(len(idx)), ))
    legs.append(("residual keeps within-group variation", float(np.std(res)) > 1e-5))

    # L6 rank inside an industry is uniform, single member is 0.5, and order is kept
    rw = rank_within_industry(["A", "A", "A", "B"], [0.03, 0.01, 0.02, 0.99])
    legs.append(("within-industry ranks", abs(rw[1] - 1 / 3) < 1e-12 and abs(rw[2] - 2 / 3) < 1e-12
                 and rw[0] == 1.0 and rw[3] == 0.5))

    # L7 thin industries are pooled, not dropped
    groups2 = ["A"] * 10 + ["B"] * 10 + ["TINY"]
    res2 = industry_residual(np.arange(21.0), np.zeros(21), np.zeros(21), groups2)
    legs.append(("thin industry pooled into OTHER", np.all(np.isfinite(res2)) and len(res2) == 21))

    # L8 quintile mapping is closed on the ends
    q = quintile(np.array([0.0, 0.2, 0.4, 0.6, 0.8, 1.0]))
    legs.append(("quintile edges", q[0] == 0 and q[-1] == 4))

    # L9 compound of flat zero
    legs.append(("compound flat", abs(base.compound([0.0] * 10)) < 1e-12))

    # L10 the published map is cut to the top-level industry, not the raw 6-digit code
    try:
        real = load_industry()
        widths = {len(code) for _, codes in real.values() for code in codes}
        legs.append(("load_industry cuts to %d digits" % INDUSTRY_LEVEL_DIGITS,
                     widths == {INDUSTRY_LEVEL_DIGITS} and len(real) > 5000))
    except (OSError, SystemExit):
        legs.append(("load_industry cuts to %d digits (file absent -> skipped)" % INDUSTRY_LEVEL_DIGITS, True))

    bad = [name for name, ok in legs if not ok]
    print("astock_resid_industry_neutral selftest %d/%d" % (len(legs) - len(bad), len(legs)))
    for name, ok in legs:
        print("  %s %s" % ("PASS" if ok else "FAIL", name))
    return 0 if not bad else 1


# ---------------------------------------------------------------- check
def check() -> int:
    """Re-derive the verdict from the published rows; no network, no re-run."""
    if not os.path.exists(OUT):
        print("CHECK FAILED missing face %s" % OUT)
        return 2
    with open(OUT, encoding="utf-8") as fh:
        face = json.load(fh)
    rows = face.get("rows") or []
    if not rows:
        print("CHECK FAILED no rows in face")
        return 2
    verdict, details = verdict_of(rows)
    stored = face.get("verdict")
    diffs = []
    if verdict != stored:
        diffs.append("verdict %r != stored %r" % (verdict, stored))
    for key, face_key in (("ic_resid", "resid"), ("ic_ind", "ind"), ("ic_rankind", "rankind")):
        got = details.get(key, {})
        want = (face.get("ic") or {}).get(face_key, {})
        for field in ("n", "mean", "t"):
            a, b = got.get(field), want.get(field)
            if a is None and b is None:
                continue
            if a is None or b is None or abs(float(a) - float(b)) > 1e-9:
                diffs.append("%s.%s: %r != %r" % (key, field, a, b))
    if diffs:
        print("CHECK FAILED")
        for d in diffs:
            print("  " + d)
        return 3
    print("CHECK_OK verdict=%s rows=%d" % (stored, len(rows)))
    return 0


# ---------------------------------------------------------------- main
def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "selftest", "check"])
    ap.add_argument("--stride", type=int, default=HOLD)
    ap.add_argument("--first-date", default=FIRST_DATE)
    args = ap.parse_args(argv)

    if args.cmd == "selftest":
        return selftest()
    if args.cmd == "check":
        return check()

    base.FIRST_DATE = args.first_date
    started = datetime.now(timezone.utc).astimezone()
    hist = load_industry()
    print("industry map %d symbols" % len(hist))
    dates, symbols, close, amount, shares = base.load_panel(first_date=args.first_date)
    print("panel %d dates x %d symbols (%s..%s)" % (len(dates), len(symbols), dates[0], dates[-1]))
    rows = run(dates, symbols, close, amount, shares, hist, stride=args.stride)
    if len(rows) < 6:
        print("NOT_ENOUGH_REBALANCES rows=%d" % len(rows))
        return 2

    verdict, details = verdict_of(rows)
    quint_ind = [float(np.nanmean([r["q_ind"][k] for r in rows])) for k in range(5)]
    quint_rk = [float(np.nanmean([r["q_rankind"][k] for r in rows])) for k in range(5)]
    quint_res = [float(np.nanmean([r["q_resid"][k] for r in rows])) for k in range(5)]

    payload = {
        "generated": started.isoformat(timespec="seconds"),
        "evidence_cutoff": dates[-1],
        "machine": base._machine(),
        "kind": "census",
        "prereg": None,
        "adoption": None,
        "fills_the_hole_of": "research/digests/DIGEST-20261120-r1862-astock-resid-reversal.md (industry half left blank)",
        "spec": {
            "hold": HOLD,
            "stride": args.stride,
            "lookback_beta": LOOKBACK_BETA,
            "min_amount_20d": MIN_AMOUNT_20D,
            "min_bars": MIN_BARS,
            "cost_one_side": COST_ONE_SIDE,
            "industry_source": "data/basic/sw_stock_classify_2021.xls (PIT, entry_date <= rebalance)",
            "industry_level": "first %d digits of the classification code" % INDUSTRY_LEVEL_DIGITS,
            "min_group_members": MIN_GROUP_MEMBERS,
            "arms": ["resid_beta_size (r1862 control)", "resid_beta_size_industry", "rank_within_industry"],
            "frozen_criterion": {
                "ic_gain_min": IC_GAIN_MIN,
                "t_min": T_MIN,
                "rule": "HELPS iff gain>=%.3f and |t|>=%.1f and LS net>0 and Q1 excess improves; "
                        "HURTS iff gain<=-%.3f; else WITHIN_NOISE" % (IC_GAIN_MIN, T_MIN, IC_GAIN_MIN),
            },
        },
        "panel": {"dates": len(dates), "symbols": len(symbols),
                  "first": dates[0], "last": dates[-1],
                  "industry_map_symbols": len(hist)},
        "rebalances": len(rows),
        "coverage": {
            "median_eligible": int(np.median([r["n_eligible_before_industry"] for r in rows])),
            "median_dropped_no_industry": int(np.median([r["n_dropped_no_industry"] for r in rows])),
            "median_industries": int(np.median([r["n_industries"] for r in rows])),
        },
        "ic": {
            "resid": details["ic_resid"],
            "ind": details["ic_ind"],
            "rankind": details["ic_rankind"],
            "raw": summarise(rows, "ic_raw"),
        },
        "ic_gain_abs": details.get("ic_gain_abs"),
        "same_sign": details.get("same_sign"),
        "ls_net_annual": {
            "resid": details["ls_resid_net_annual"],
            "ind": details["ls_ind_net_annual"],
            "rankind": details["ls_rankind_net_annual"],
        },
        "q1_excess_annual": {
            "resid": details["q1_excess_resid_annual"],
            "ind": details["q1_excess_ind_annual"],
            "rankind": details["q1_excess_rankind_annual"],
        },
        "q1_excess_per_rebalance": {
            "resid": summarise_array([r["q1_excess_resid"] for r in rows]),
            "ind": summarise_array([r["q1_excess_ind"] for r in rows]),
            "rankind": summarise_array([r["q1_excess_rankind"] for r in rows]),
        },
        "quintile_mean_forward": {
            "resid": quint_res,
            "ind": quint_ind,
            "rankind": quint_rk,
        },
        "verdict": verdict,
        "rank_arm_diagnostics": {
            "size_expo_q1_mean": float(np.nanmean([r["size_expo_rankind_q1"] for r in rows])),
            "beta_expo_q1_mean": float(np.nanmean([r["beta_expo_rankind_q1"] for r in rows])),
            "median_industries_in_q1": int(np.median([r["n_industries_rankind_q1"] for r in rows])),
            "note": "Q1 = within-industry losers; a large negative size exposure means the "
                    "long-only excess is partly a small-size tilt, not pure reversal",
        },
        "rows": rows,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)

    def p(v):
        return "n/a" if v is None else "%+.2f%%" % (v * 100)

    print("rebalances=%d median_eligible=%d median_industries=%d" % (
        len(rows), payload["coverage"]["median_eligible"], payload["coverage"]["median_industries"]))
    print("IC resid(beta+size)  mean=%.4f t=%s" % (details["ic_resid"]["mean"], _fmt(details["ic_resid"]["t"])))
    print("IC +industry         mean=%.4f t=%s" % (details["ic_ind"]["mean"], _fmt(details["ic_ind"]["t"])))
    print("IC rank-within-ind   mean=%.4f t=%s" % (details["ic_rankind"]["mean"], _fmt(details["ic_rankind"]["t"])))
    print("gain(|IC|)=%s" % ("n/a" if details.get("ic_gain_abs") is None else "%+.4f" % details["ic_gain_abs"]))
    print("LS net annual: resid=%s ind=%s rankind=%s" % (
        p(details["ls_resid_net_annual"]), p(details["ls_ind_net_annual"]),
        p(details["ls_rankind_net_annual"])))
    print("Q1 excess annual: resid=%s ind=%s rankind=%s" % (
        p(details["q1_excess_resid_annual"]), p(details["q1_excess_ind_annual"]),
        p(details["q1_excess_rankind_annual"])))
    print("quintiles resid(loser->winner)=%s" % " ".join("%.4f" % v for v in quint_res))
    print("quintiles ind  (loser->winner)=%s" % " ".join("%.4f" % v for v in quint_ind))
    diag = payload["rank_arm_diagnostics"]
    print("rank-arm Q1 exposure: size=%+.3f beta=%+.3f industries_in_q1=%d" % (
        diag["size_expo_q1_mean"], diag["beta_expo_q1_mean"], diag["median_industries_in_q1"]))
    q1pr = payload["q1_excess_per_rebalance"]
    print("Q1 per-rebalance: resid mean=%+.5f t=%s | ind %+.5f t=%s | rankind %+.5f t=%s" % (
        q1pr["resid"]["mean"], _fmt(q1pr["resid"]["t"]),
        q1pr["ind"]["mean"], _fmt(q1pr["ind"]["t"]),
        q1pr["rankind"]["mean"], _fmt(q1pr["rankind"]["t"])))
    print("VERDICT=%s" % verdict)
    print("wrote %s" % OUT)
    return 0


def _fmt(v):
    return "n/a" if v is None else "%.2f" % v


if __name__ == "__main__":
    sys.exit(main())
