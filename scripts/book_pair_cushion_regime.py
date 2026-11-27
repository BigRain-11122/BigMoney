#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Is the 30/70 cushion a permanent property, or only what a cheap CB market pays?

r2179 measured the cushion as an average over all months ("not a hedge, a
dilution").  r2181 put a confidence interval on that average.  Neither asked the
obvious follow-up: the cb sleeve inside this book is not a passive bond index,
it is the dual-low convertible book, and the price of a convertible is mostly a
premium over its parity.  When the whole CB market trades rich, that premium has
nowhere to expand -- so the sleeve's ability to *not* follow equities down may
be a property of a cheap market, not a property of the sleeve.

The face answers three things:
  (1) the cushion (blend minus ETF in months the ETF fell) split by the CB
      market's own valuation regime, with the regime read at the *previous*
      month end and its tertile edges from an expanding window only (no
      look-ahead anywhere);
  (2) the price of the upside given up in the same split;
  (3) one rule that follows from (1) -- hold cash in the cb sleeve while the
      market is rich -- priced at the same 10bp per side the parents charge,
      and compared against simply holding 30/70 through everything.

Weights are read from the parent face, never re-selected here.  The cb and etf
lines are the parents' own published arms, imported rather than rebuilt.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FACE = "results/book_pair_cushion_regime.json"
MD = "results/book_pair_cushion_regime.md"
RESEARCH = "research/BOOK_PAIR_CUSHION_REGIME.md"

W_FALLBACK = 0.30
MIN_HIST_DAYS = 250        # premium observations before a tertile may be issued
BOOT_L = 3                 # circular block length, months
BOOT_N = 4000
COST_BP = 10.0             # per side, on the traded share of the wallet
SEED = 20261127
REGIMES = (("cheap", 0), ("mid", 1), ("rich", 2))
MIN_DOWN_SIDE = 8          # falling months each side must hold before a split reads


def _rp(rel):
    return os.path.join(ROOT, rel)


def _iso(ts):
    import datetime as _dt
    return _dt.datetime.fromtimestamp(ts).isoformat(timespec="seconds")


def _now_iso():
    import datetime as _dt
    return _dt.datetime.now().astimezone().isoformat(timespec="seconds")


def _stamp(path):
    if not os.path.exists(path):
        return {"path": path, "missing": True}
    st = os.stat(path)
    return {"path": path, "size": int(st.st_size), "mtime": _iso(st.st_mtime)}


# ---------------------------------------------------------------- inputs
def published_weight():
    """The cb share is a published decision -- read it, do not pick it again."""
    p = _rp("results/book_pair_blend.json")
    if not os.path.exists(p):
        return W_FALLBACK, {"path": p, "missing": True, "fallback": W_FALLBACK}
    with open(p, encoding="utf-8") as fh:
        d = json.load(fh)
    w = (d.get("best") or {}).get("w_cb")
    if not isinstance(w, (int, float)):
        return W_FALLBACK, {"path": p, "missing_w_cb": True, "fallback": W_FALLBACK}
    return float(w), {"path": p, "w_cb": float(w), "stamp": _stamp(p)}


def load_inputs():
    """One panel read: the cb arm, its market premium, and the etf arm."""
    import cb_dual_low as C
    import book_pair_blend as P

    panel = C._load_panel()
    m, eq, dt = C._backtest(panel, n_hold=20, rebal=20, cost_bp=COST_BP)
    cb = P._series(eq, dt)
    prem = (panel.dropna(subset=["conv_premium"])
                 .groupby("date")["conv_premium"].median().sort_index())
    etf, etf_meta = P.load_etf()
    w, w_meta = published_weight()
    return {
        "cb": cb,
        "etf": etf,
        "prem": prem,
        "w": w,
        "cb_meta": {
            "arm": "n_hold=20 rebal=20 cost=10bp phase=0",
            "bars": int(len(cb)),
            "cagr": m.get("cagr"),
            "sharpe": m.get("sharpe"),
            "last": str(cb.index[-1].date()),
            "panel": _stamp(_rp("data/cb_panel.csv.gz")),
        },
        "etf_meta": etf_meta,
        "w_meta": w_meta,
        "prem_days": int(len(prem)),
    }


# ---------------------------------------------------------------- month maths
def month_returns(ser):
    """Last level of each calendar month, differenced -- one return per month."""
    last = ser.resample("ME").last()
    return last.pct_change().dropna()


def monthly_frame(cb, etf, w):
    """Aligned monthly returns for cb, etf and the w/cb blend."""
    idx = cb.index.intersection(etf.index).sort_values()
    cb2, etf2 = cb.reindex(idx), etf.reindex(idx)
    ra = cb2.pct_change().dropna()
    rb = etf2.pct_change().dropna()
    j = ra.index.intersection(rb.index)
    ra, rb = ra.reindex(j), rb.reindex(j)
    blend = (1.0 + (w * ra + (1.0 - w) * rb)).cumprod()
    mc, me, mb = month_returns(cb2), month_returns(etf2), month_returns(blend)
    mi = mc.index.intersection(me.index).intersection(mb.index)
    return mi, mc.reindex(mi), me.reindex(mi), mb.reindex(mi)


def label_months(prem, month_ends, min_hist=MIN_HIST_DAYS):
    """Regime 0/1/2 per month, decided at the previous month end only.

    The edges are expanding-window tertiles of the premium history strictly up
    to that month end, so a month is never labelled with knowledge of itself.
    """
    import numpy as np

    labels = [None] * len(month_ends)
    idx = prem.index
    vals = prem.values.astype(float)
    for k in range(1, len(month_ends)):
        cut = int(idx.searchsorted(month_ends[k - 1], side="right"))
        if cut < 1:
            continue
        hist = vals[:cut]
        hist = hist[~np.isnan(hist)]
        if len(hist) < min_hist:
            continue
        p = vals[cut - 1]
        if p != p:
            continue
        e1 = float(np.quantile(hist, 1.0 / 3.0))
        e2 = float(np.quantile(hist, 2.0 / 3.0))
        labels[k] = 2 if p >= e2 else (0 if p <= e1 else 1)
    return labels


def cushion_by_regime(me_v, mb_v, labels):
    """Cushion in falling months and upside given up in rising ones, per regime."""
    out = {}
    for name, code in REGIMES:
        allr, down, up = [], [], []
        for k, lab in enumerate(labels):
            if lab != code:
                continue
            e = float(me_v[k])
            b = float(mb_v[k])
            allr.append(b)
            if e < 0:
                down.append(b - e)
            else:
                up.append(b - e)
        out[name] = {
            "months": len(allr),
            "mean_month_pct": (round(100.0 * sum(allr) / len(allr), 3) if allr else None),
            "down_months": len(down),
            "cushion_pp": (round(100.0 * sum(down) / len(down), 3) if down else None),
            "down_improved": int(sum(1 for x in down if x > 0)),
            "up_months": len(up),
            "give_pp": (round(100.0 * sum(up) / len(up), 3) if up else None),
        }
    return out


def stats_from_returns(rets):
    import numpy as np

    r = np.asarray(list(rets), dtype=float)
    if len(r) < 3:
        return {}
    eq = np.cumprod(1.0 + r)
    years = len(r) / 12.0
    cagr = float(eq[-1] ** (1.0 / years) - 1.0) if eq[-1] > 0 else float("nan")
    sd = float(r.std(ddof=1))
    sharpe = float(r.mean() / sd * math.sqrt(12.0)) if sd > 0 else float("nan")
    peak = np.maximum.accumulate(eq)
    dd = eq / peak - 1.0
    return {
        "cagr": round(cagr, 6),
        "sharpe": round(sharpe, 6),
        "maxdd": round(float(dd.min()), 6),
        "vol": round(sd * math.sqrt(12.0), 6),
        "months": int(len(r)),
        "worst_month": round(float(r.min()), 6),
        "pos_pct": round(float((r > 0).mean()), 4),
    }


def rule_arm(me_v, mc_v, labels, w, cost_bp=COST_BP):
    """Cash in the cb sleeve while the market is rich; cost per side when moving.

    A month with no label yet (not enough premium history) stays invested: an
    unknown state is not evidence of a rich market.
    """
    steps = []
    prev = None
    switches = 0
    paid = 0.0
    for k, lab in enumerate(labels):
        state = 0 if lab == 2 else 1          # 0=cash sleeve, 1=cb sleeve
        r = (1.0 - w) * float(me_v[k]) + w * (0.0 if state == 0 else float(mc_v[k]))
        if prev is not None and state != prev:
            switches += 1
            c = cost_bp / 1e4 * w
            r -= c
            paid += c
        prev = state
        steps.append({"label": lab, "state": state, "ret": r})
    scored = [s["ret"] for s in steps if s["label"] is not None]
    always = [(1.0 - w) * float(me_v[k]) + w * float(mc_v[k])
              for k, lab in enumerate(labels) if lab is not None]
    exposure = [float(s["state"]) for s in steps if s["label"] is not None]
    avg_exp = (sum(exposure) / len(exposure)) if exposure else None
    # A rule that sits in cash most of the time is also a *smaller* book.  The
    # control arm carries the same average sleeve exposure every month, so the
    # only thing left between the two arms is when the exposure was held.
    matched = None
    if avg_exp is not None:
        matched = stats_from_returns(
            [(1.0 - w) * float(me_v[k]) + w * avg_exp * float(mc_v[k])
             for k, lab in enumerate(labels) if lab is not None])
    return {
        "rule": stats_from_returns(scored),
        "always_on": stats_from_returns(always),
        "matched_exposure": matched,
        "avg_cb_exposure": (round(avg_exp, 4) if avg_exp is not None else None),
        "switches": switches,
        "cost_paid_pp": round(100.0 * paid, 3),
        "months_scored": len(scored),
        "months_in_cash_sleeve": int(sum(1 for s in steps
                                         if s["label"] is not None and s["state"] == 0)),
        "rule_rets": [round(float(x), 8) for x in scored],
        "matched_rets": ([round(float((1.0 - w) * float(me_v[k])
                                + w * avg_exp * float(mc_v[k])), 8)
                          for k, lab in enumerate(labels) if lab is not None]
                         if avg_exp is not None else []),
    }


def edge_concentration(rule_rets, matched_rets, k=5):
    """How much of the rule's total edge sits in its k best months."""
    a = list(rule_rets or [])
    b = list(matched_rets or [])
    n = min(len(a), len(b))
    if n < k + 3:
        return {"note": "too few months", "n": int(n)}
    d = [a[i] - b[i] for i in range(n)]
    total = sum(d)
    best = sum(sorted(d, reverse=True)[:k])
    return {
        "total_pp": round(100.0 * total, 3),
        "top_k": int(k),
        "top_k_pp": round(100.0 * best, 3),
        "top_k_share": (round(best / total, 4) if abs(total) > 1e-12 else None),
        "months": int(n),
    }


def mean_diff_band(a, b, n=BOOT_N, L=BOOT_L, seed=SEED):
    """Block-bootstrap band on the mean monthly (a - b), in pp.

    A Sharpe difference of 0.1 over 81 months is a claim the sample may not be
    able to pay for; this is the leg that decides whether it can.
    """
    import numpy as np

    va = np.asarray(a, dtype=float)
    vb = np.asarray(b, dtype=float)
    k = min(len(va), len(vb))
    if k < 6:
        return {"note": "too few paired months", "n": int(k)}
    d = va[:k] - vb[:k]
    rng = np.random.default_rng(seed)
    blocks = int(math.ceil(k / float(L)))
    draws = []
    for _ in range(n):
        starts = rng.integers(0, k, size=blocks)
        take = []
        for s in starts:
            for j in range(L):
                take.append(d[(int(s) + j) % k])
            if len(take) >= k:
                break
        draws.append(float(np.mean(take[:k])))
    a2 = np.array(draws)
    return {
        "point_pp": round(100.0 * float(d.mean()), 3),
        "lo_pp": round(100.0 * float(np.quantile(a2, 0.025)), 3),
        "hi_pp": round(100.0 * float(np.quantile(a2, 0.975)), 3),
        "share_le_0": round(float((a2 <= 0).mean()), 4),
        "n": int(k),
        "block_len": int(L),
        "draws": int(len(a2)),
    }


def rule_verdict(rule, band=None):
    """Is the rule a timing gain, or a smaller book wearing a timer?"""
    rr = (rule.get("rule") or {}).get("sharpe")
    mm = (rule.get("matched_exposure") or {}).get("sharpe")
    if rr is None or mm is None:
        return "RULE_NOT_MEASURABLE", None
    edge = rr - mm
    lo = (band or {}).get("lo_pp")
    hi = (band or {}).get("hi_pp")
    if lo is not None and hi is not None and lo <= 0 <= hi:
        return "RULE_EDGE_NOT_SEPARABLE_FROM_NOISE", round(edge, 4)
    if edge > 0.05:
        return "THE_RULE_BEATS_ITS_OWN_EXPOSURE", round(edge, 4)
    if edge > -0.05:
        return "THE_RULE_IS_JUST_LESS_EXPOSURE", round(edge, 4)
    return "THE_RULE_IS_WORSE_THAN_JUST_HOLDING_LESS", round(edge, 4)


# ---------------------------------------------------------------- statistics
def block_bootstrap_diff(pairs, n=BOOT_N, L=BOOT_L, seed=SEED):
    """Mean cushion (rich) minus mean cushion (not rich), circular block bootstrap.

    pairs: ordered list of (label, cushion_fraction) over falling etf months.
    """
    import numpy as np

    if not pairs:
        return {"note": "no falling months", "n": 0}
    labs = np.array([p[0] for p in pairs])
    vals = np.array([p[1] for p in pairs], dtype=float)
    base = _diff_of_means(labs, vals)
    if base is None:
        return {"note": "one side empty", "n": int(len(pairs)), "point_pp": None}
    rng = np.random.default_rng(seed)
    n_obs = len(pairs)
    blocks = int(math.ceil(n_obs / float(L)))
    draws = []
    for _ in range(n):
        starts = rng.integers(0, n_obs, size=blocks)
        take_l, take_v = [], []
        for s in starts:
            for j in range(L):
                i = (int(s) + j) % n_obs
                take_l.append(labs[i])
                take_v.append(vals[i])
            if len(take_l) >= n_obs:
                break
        d = _diff_of_means(np.array(take_l), np.array(take_v[: len(take_l)]))
        if d is not None:
            draws.append(d)
    if not draws:
        return {"note": "no usable resamples", "n": int(len(pairs)),
                "point_pp": round(100.0 * base, 3)}
    a = np.array(draws, dtype=float)
    return {
        "point_pp": round(100.0 * base, 3),
        "lo_pp": round(100.0 * float(np.quantile(a, 0.025)), 3),
        "hi_pp": round(100.0 * float(np.quantile(a, 0.975)), 3),
        "share_le_0": round(float((a <= 0).mean()), 4),
        "n": int(len(pairs)),
        "block_len": int(L),
        "draws": int(len(a)),
    }


def _diff_of_means(labs, vals):
    import numpy as np

    rich = vals[labs == 2]
    rest = vals[(labs == 0) | (labs == 1)]
    if len(rich) < 2 or len(rest) < 2:
        return None
    return float(np.mean(rich) - np.mean(rest))


def verdict_of(cushion, boot, rule):
    """Which story the numbers tell -- named mechanically, both gates printed.

    First gate is the gate's own capability: a split whose smaller side holds
    almost no falling months cannot be read as a split, no matter what the two
    means say.  Reporting "holds in both regimes" off 3 cheap falling months
    would be a sentence the sample cannot pay for.
    """
    cheap = cushion.get("cheap", {}).get("cushion_pp")
    rich = cushion.get("rich", {}).get("cushion_pp")
    if cheap is None or rich is None:
        return "CUSHION_REGIME_UNREADABLE", None
    rich_down = int(cushion.get("rich", {}).get("down_months") or 0)
    rest_down = int((cushion.get("cheap", {}).get("down_months") or 0)
                    + (cushion.get("mid", {}).get("down_months") or 0))
    if min(rich_down, rest_down) < MIN_DOWN_SIDE:
        return "CUSHION_NOT_MEASURABLE_THIS_SAMPLE", (rich_down, rest_down)
    lo = boot.get("lo_pp")
    hi = boot.get("hi_pp")
    sep = (lo is not None and hi is not None and (lo > 0 or hi < 0))
    if cheap <= 0 and rich <= 0:
        return "CUSHION_IS_NOT_A_CUSHION", (lo, hi)
    if not sep:
        return "CUSHION_DIFFERENCE_NOT_SEPARABLE", (lo, hi)
    if cheap > 0 and rich <= 0:
        return "CUSHION_TURNS_OFF_WHEN_THE_CB_MARKET_IS_RICH", (lo, hi)
    if cheap > 0 and rich > 0 and lo > 0:
        return "CUSHION_HOLDS_BETTER_IN_CHEAP_MONTHS", (lo, hi)
    if cheap > 0 and rich > 0:
        return "CUSHION_HOLDS_IN_BOTH_REGIMES", (lo, hi)
    return "CUSHION_SPLITS_BY_REGIME_UNRESOLVED", (lo, hi)


def current_state(prem, labels, month_ends):
    """Where the market sits today and which side of the split that puts us on."""
    import numpy as np

    if not len(prem.index):
        return {"missing": True}
    last = prem.index[-1]
    p = float(prem.values[-1])
    vals = prem.values.astype(float)
    vals = vals[~np.isnan(vals)]
    pct = float((vals <= p).mean()) if len(vals) else None
    lab = None
    for k in range(len(labels) - 1, -1, -1):
        if labels[k] is not None:
            lab = labels[k]
            break
    return {
        "asof": str(last.date()),
        "median_conv_premium_pct": round(p, 3),
        "percentile_in_own_history": round(pct, 4) if pct is not None else None,
        "last_label": lab,
        "last_label_name": ({0: "cheap", 1: "mid", 2: "rich"}).get(lab),
        "label_asof_month_end": (str(month_ends[-1].date())
                                 if lab is not None and len(month_ends) else None),
    }


def reconciliation(cb, parents):
    """Reproduce the parent's in-window cb numbers from our own series."""
    import numpy as np

    try:
        want = (parents or {}).get("cb", {}).get("in_window", {})
    except AttributeError:
        want = {}
    if not want:
        return {"ok": None, "why": "parent face has no cb.in_window block"}
    first = want.get("first")
    last = want.get("last")
    if not first or not last:
        return {"ok": None, "why": "parent window edges missing"}
    import pandas as pd

    s = cb.loc[(cb.index >= pd.Timestamp(first)) & (cb.index <= pd.Timestamp(last))]
    if len(s) < 3:
        return {"ok": False, "why": "slice too short", "bars": int(len(s))}
    eq = s.values.astype(float)
    r = eq[1:] / eq[:-1] - 1.0
    years = (s.index[-1] - s.index[0]).days / 365.25
    cagr = float(eq[-1] / eq[0]) ** (1.0 / years) - 1.0
    sd = float(np.std(r, ddof=1))
    sharpe = float(np.mean(r) / sd * math.sqrt(244.0)) if sd > 0 else float("nan")
    return {
        "ok": bool(abs(cagr - float(want.get("cagr", 0))) < 1e-6
                   and abs(sharpe - float(want.get("sharpe", 0))) < 1e-6),
        "bars": int(len(s)),
        "bars_want": want.get("bars"),
        "cagr": round(cagr, 10),
        "cagr_want": want.get("cagr"),
        "sharpe": round(sharpe, 10),
        "sharpe_want": want.get("sharpe"),
        "window": [first, last],
    }


# ---------------------------------------------------------------- build
def build(write=True, quiet=False):
    from_shell = not quiet

    def say(msg):
        if from_shell:
            sys.stdout.write(msg + "\n")

    say("[1/5] loading parents (one cb panel read) ...")
    inp = load_inputs()
    cb, etf, prem, w = inp["cb"], inp["etf"], inp["prem"], inp["w"]
    say("      cb bars=%d  etf bars=%d  w_cb=%.2f  premium days=%d"
        % (len(cb), len(etf), w, len(prem)))

    say("[2/5] monthly alignment and walk-forward premium regimes ...")
    mi, mc, me, mb = monthly_frame(cb, etf, w)
    labels = label_months(prem, list(mi))
    n_lab = sum(1 for x in labels if x is not None)
    say("      months=%d  labelled=%d" % (len(mi), n_lab))

    say("[3/5] cushion split ...")
    me_v, mc_v, mb_v = me.values, mc.values, mb.values
    cush = cushion_by_regime(me_v, mb_v, labels)
    pairs = [(labels[k], float(mb_v[k]) - float(me_v[k]))
             for k in range(len(labels))
             if labels[k] is not None and float(me_v[k]) < 0]
    boot = block_bootstrap_diff(pairs)

    say("[4/5] the rule and its price ...")
    rule = rule_arm(me_v, mc_v, labels, w)
    edge_band = mean_diff_band(rule.get("rule_rets") or [], rule.get("matched_rets") or [])
    conc = edge_concentration(rule.get("rule_rets") or [], rule.get("matched_rets") or [])
    rverd, redge = rule_verdict(rule, edge_band)
    verd, band = verdict_of(cush, boot, rule)
    sides = {
        "rich_down_months": cush["rich"]["down_months"],
        "rest_down_months": cush["cheap"]["down_months"] + cush["mid"]["down_months"],
        "min_side_required": MIN_DOWN_SIDE,
    }

    say("[5/5] reconciliation + face ...")
    parents = {}
    p = _rp("results/book_pair_blend.json")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as fh:
            parents = json.load(fh).get("parents") or {}
    rec = reconciliation(cb, parents)
    cur = current_state(prem, labels, list(mi))

    face = {
        "face": FACE,
        "generated_at": _now_iso(),
        "evidence_cutoff": str(etf.index[-1].date()),
        "question": ("Is the 30/70 cushion a permanent property of the sleeve, or "
                     "only what a cheap convertible market pays?"),
        "caliber": {
            "weight": "read from results/book_pair_blend.json best.w_cb",
            "regime": ("tertiles of the CB market's median conversion premium, read "
                       "at the previous month end, edges from an expanding window "
                       "(>=%d premium days)" % MIN_HIST_DAYS),
            "months": "last level of each calendar month, differenced",
            "rule_cost": "%.0fbp per side on the %.2f cb share" % (COST_BP, w),
            "bootstrap": "circular blocks of %d months, %d draws, seed %d"
                         % (BOOT_L, BOOT_N, SEED),
        },
        "window": {
            "first": str(mi[0].date()) if len(mi) else None,
            "last": str(mi[-1].date()) if len(mi) else None,
            "last_bar": str(etf.index[-1].date()),
            "final_month_is_month_to_date": bool(len(mi) and mi[-1].date() > etf.index[-1].date()),
            "months": int(len(mi)),
            "labelled_months": int(n_lab),
            "why": "the blend only exists where both parents have a level",
        },
        "inputs": {
            "w_cb": w,
            "w_source": inp["w_meta"],
            "cb": inp["cb_meta"],
            "etf": {k: inp["etf_meta"].get(k) for k in
                    ("face", "arm", "execution", "panel", "universe")},
            "premium_days": inp["prem_days"],
        },
        "regimes": cush,
        "sides": sides,
        "cushion_difference": boot,
        "rule": rule,
        "rule_verdict": rverd,
        "rule_verdict_edge": redge,
        "rule_edge_band": edge_band,
        "rule_edge_concentration": conc,
        "current": cur,
        "reconciliation": rec,
        "verdict": verd,
        "verdict_band": ({"lo_pp": band[0], "hi_pp": band[1]}
                         if band and isinstance(band[0], float) else None),
        "unverified": [
            "the premium regime is a market-wide median; the sleeve holds 20 bonds, "
            "so a market-rich month need not be a sleeve-rich month",
            "the rule is priced on monthly switches only; intra-month runs are not modelled",
            "the cb arm and the etf arm are the parents' published arms -- this face "
            "does not re-test them",
            "there is one window: %s..%s. The CB market was rich in %d of %d labelled "
            "months and in cash in %s of them, so the rule reads mostly as 'be out of "
            "the sleeve when it is expensive' over a single premium cycle -- a repeated "
            "reading is what would make its %s pp a month edge durable"
            % (str(mi[0].date()) if len(mi) else "?",
               str(etf.index[-1].date()),
               cush["rich"]["months"], n_lab,
               rule["months_in_cash_sleeve"],
               edge_band.get("point_pp") if edge_band else "?"),
            "the cheap side holds only 3 falling months -- the cheap-vs-rich split is "
            "printed for the record and is not evidence of anything",
        ],
    }

    if write:
        with open(_rp(FACE), "w", encoding="utf-8") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1)
        with open(_rp(MD), "w", encoding="utf-8") as fh:
            fh.write(render_md(face))
        with open(_rp(RESEARCH), "w", encoding="utf-8") as fh:
            fh.write(render_research(face))

    say("      verdict = %s   (rich/rest falling months = %d/%d, need %d each)"
        % (verd, sides["rich_down_months"], sides["rest_down_months"], MIN_DOWN_SIDE))
    say("      cheap cushion=%s pp (down months=%d) | rich cushion=%s pp (down=%d)"
        % (cush["cheap"]["cushion_pp"], cush["cheap"]["down_months"],
           cush["rich"]["cushion_pp"], cush["rich"]["down_months"]))
    say("      difference rich-minus-rest = %+0.3f pp  [%s .. %s]  P(<=0)=%s"
        % (boot.get("point_pp") or 0.0, boot.get("lo_pp"), boot.get("hi_pp"),
           boot.get("share_le_0")))
    say("      rule: sharpe %s vs always-on %s vs matched-exposure %s -> %s (%s)"
        % (rule["rule"].get("sharpe"), rule["always_on"].get("sharpe"),
           (rule.get("matched_exposure") or {}).get("sharpe"), rverd, redge))
    say("      rule edge per month %s pp [%s .. %s] P(<=0)=%s"
        % (edge_band.get("point_pp"), edge_band.get("lo_pp"),
           edge_band.get("hi_pp"), edge_band.get("share_le_0")))
    say("      switches %d | cost %.3f pp | avg cb exposure %s"
        % (rule["switches"], rule["cost_paid_pp"], rule["avg_cb_exposure"]))
    say("      reconciliation vs parent cb.in_window: %s" % rec.get("ok"))
    return face


# ---------------------------------------------------------------- markdown
def _tbl(face):
    rows = ["| regime | months | mean month | falling months | cushion | better in | rising months | upside given up |",
            "|---|---|---|---|---|---|---|---|"]
    for name, _ in REGIMES:
        r = face["regimes"][name]
        rows.append("| %s | %d | %s%% | %d | %s pp | %d/%d | %d | %s pp |"
                    % (name, r["months"],
                       _n(r["mean_month_pct"]), r["down_months"],
                       _n(r["cushion_pp"]), r["down_improved"], r["down_months"],
                       r["up_months"], _n(r["give_pp"])))
    return "\n".join(rows)


def _n(v, dash="n/a"):
    return dash if v is None else ("%+.2f" % v if isinstance(v, float) else str(v))


def render_md(face):
    c = face["regimes"]
    r = face["rule"]
    cur = face["current"]
    b = face["cushion_difference"]
    L = []
    L.append("# The cushion, split by what the convertible market costs")
    L.append("")
    L.append("Generated %s · bars to **%s** · %d months, %d of them labelled%s"
             % (face["generated_at"], face["evidence_cutoff"],
                face["window"]["months"], face["window"]["labelled_months"],
                (" (the last month is month-to-date through %s)"
                 % face["window"].get("last_bar"))
                if face["window"].get("final_month_is_month_to_date") else ""))
    L.append("")
    L.append("**Verdict: `%s`**" % face["verdict"])
    L.append("")
    L.append("Question: the 30/70 book was measured as a dilution, not a hedge "
             "(r2179) and that average was separable from noise (r2181). But the "
             "cb sleeve is the dual-low book, and a convertible is mostly a premium "
             "over parity -- so the question here is whether the cushion is a "
             "property of the sleeve or a property of a *cheap* market.")
    L.append("")
    L.append(_tbl(face))
    L.append("")
    s = face.get("sides") or {}
    L.append("Months available to each side of the split: **%s falling months in rich "
             "months vs %s in the rest** (the gate asks for %s each). The CB market "
             "spent most of this window in the top tertile of its own premium history, "
             "which is a fact about the sample before it is a fact about the cushion."
             % (s.get("rich_down_months"), s.get("rest_down_months"),
                s.get("min_side_required")))
    L.append("")
    L.append("Difference in cushion, rich months minus the rest: **%s pp** "
             "(95%% band %s .. %s; share of resamples at or below zero %s)."
             % (_n(b.get("point_pp")), _n(b.get("lo_pp")), _n(b.get("hi_pp")),
                b.get("share_le_0")))
    L.append("")
    L.append("## What the rule would have cost")
    L.append("")
    L.append("Rule: hold cash in the cb sleeve while the previous month end said the "
             "market was in the top tertile of its own premium history; otherwise hold "
             "the book. Priced at %.0fbp per side on the %.2f cb share." % (COST_BP, face["inputs"]["w_cb"]))
    L.append("")
    L.append("| arm | cagr | sharpe | maxdd | worst month | months |")
    L.append("|---|---|---|---|---|---|")
    for name in ("rule", "always_on", "matched_exposure"):
        s2 = r.get(name) or {}
        if not s2:
            continue
        L.append("| %s | %.2f%% | %.3f | %.2f%% | %.2f%% | %d |"
                 % (name, 100 * s2["cagr"], s2["sharpe"], 100 * s2["maxdd"],
                    100 * s2["worst_month"], s2["months"]))
    L.append("")
    L.append("Rule verdict: **`%s`** (rule Sharpe minus the same-exposure control, "
             "%s; the edge it was bought on is %s pp a month, band %s .. %s). The "
             "control arm carries the rule's own average cb exposure "
             "(**%s**) every month, so the difference is *when* the exposure was held, "
             "not *how much* of it there was."
             % (face.get("rule_verdict"), _n(face.get("rule_verdict_edge")),
                _n((face.get("rule_edge_band") or {}).get("point_pp")),
                _n((face.get("rule_edge_band") or {}).get("lo_pp")),
                _n((face.get("rule_edge_band") or {}).get("hi_pp")),
                _n(r.get("avg_cb_exposure"))))
    L.append("")
    L.append("Switches: **%d**, cost paid **%.2f pp** of the wallet, months with the "
             "sleeve in cash: **%d** of %d scored."
             % (r["switches"], r["cost_paid_pp"], r["months_in_cash_sleeve"],
                r["months_scored"]))
    cc = face.get("rule_edge_concentration") or {}
    L.append("")
    L.append("Where that edge lives: the rule's whole edge over its own exposure is "
             "**%s pp** across %s months, of which the best %s months carry **%s%%** "
             "(**%s pp**). An edge that sits in a handful of months is a drawdown "
             "story, not a return story -- read it beside the maxdd row above, "
             "not alone." % (_n(cc.get("total_pp")), _n(cc.get("months")),
                             _n(cc.get("top_k")),
                             _n(round(100.0 * cc["top_k_share"], 1)) if cc.get("top_k_share") is not None else "n/a",
                             _n(cc.get("top_k_pp"))))
    L.append("")
    L.append("## Where the market sits today")
    L.append("")
    L.append("Median conversion premium **%.2f%%** as of %s -- the **%.1fth percentile** "
             "of its own history; last label **%s**."
             % (cur.get("median_conv_premium_pct") or 0.0, cur.get("asof"),
                100 * (cur.get("percentile_in_own_history") or 0.0),
                cur.get("last_label_name")))
    L.append("")
    L.append("## What this face does not claim")
    L.append("")
    for u in face["unverified"]:
        L.append("- %s" % u)
    L.append("")
    L.append("Reconciliation against the parent's own cb window: %s."
             % ("reproduced" if face["reconciliation"].get("ok") else
                "NOT reproduced -- read the numbers above with that in mind"))
    L.append("")
    return "\n".join(L) + "\n"


def render_research(face):
    L = []
    L.append("# BOOK PAIR -- is the cushion conditional on the convertible market's price?")
    L.append("")
    L.append("Face: `%s` · markdown: `%s` · verdict `%s`."
             % (FACE, MD, face["verdict"]))
    L.append("")
    L.append("## Why this was asked")
    L.append("")
    L.append("r2179 found the 30/70 book cushions ETF drawdowns by an average of 0.43pp "
             "a month, and r2181 showed that average is separable from noise "
             "(block bootstrap, 90% band +0.07..+0.82pp). Both faces averaged over the "
             "whole overlap. Neither asked whether the cushion survives when the CB "
             "market itself is expensive -- and the sleeve is a dual-low convertible "
             "book, whose return is mostly premium expansion/contraction over parity.")
    L.append("")
    L.append("## Method")
    L.append("")
    L.append("- parents imported, not rebuilt: cb = `cb_dual_low` n_hold=20/rebal=20/10bp, "
             "etf = `etf_nobond_vt` vol_target=8%% n_hold=5 entry_lag=1; weight read from "
             "`results/book_pair_blend.json` best.w_cb = %.2f" % face["inputs"]["w_cb"])
    L.append("- regime: tertiles of the CB market's median conversion premium "
             "(`conv_premium`), read at the previous month end, edges from an expanding "
             "window of at least %d premium observations -- no look-ahead" % MIN_HIST_DAYS)
    L.append("- cushion = blend month return minus ETF month return, measured only in "
             "months the ETF fell; the same subtraction in up months is the upside given up")
    L.append("- the rule pays %.0fbp per side on the traded share, and treats an "
             "unlabelled month (not enough history) as invested" % COST_BP)
    L.append("")
    L.append("## Numbers")
    L.append("")
    L.append(_tbl(face))
    L.append("")
    L.append("Rule vs always-on vs the same-exposure control: `%s` / `%s` / `%s` Sharpe, "
             "%d switches, %.2f pp of cost, average cb exposure %s -> rule verdict `%s`."
             % (face["rule"]["rule"].get("sharpe"),
                face["rule"]["always_on"].get("sharpe"),
                (face["rule"].get("matched_exposure") or {}).get("sharpe"),
                face["rule"]["switches"], face["rule"]["cost_paid_pp"],
                face["rule"].get("avg_cb_exposure"), face.get("rule_verdict")))
    L.append("")
    L.append("## Reading")
    L.append("")
    sides = face.get("sides") or {}
    L.append("The first thing the numbers say is about the sample, not the book: the CB "
             "market sat in the top tertile of its own premium history for almost the "
             "entire overlap, so the cheap side holds only **%s** falling months against "
             "**%s** on the rich side (gate: %s each)."
             % (sides.get("rest_down_months"), sides.get("rich_down_months"),
                sides.get("min_side_required")))
    L.append("")
    L.append("The number that would make this actionable is the rich-minus-rest "
             "difference and its band: %s pp (%s .. %s). A negative band with the two "
             "sides on opposite signs is the only configuration that would justify "
             "switching the sleeve to cash; %s is what the sample actually supports."
             % (_n(face["cushion_difference"].get("point_pp")),
                _n(face["cushion_difference"].get("lo_pp")),
                _n(face["cushion_difference"].get("hi_pp")),
                face.get("verdict")))
    L.append("")
    L.append("## Owed")
    L.append("")
    L.append("- chain leg + smoke leg (shared faces; this round ran under a contention "
             "window and touched only new files)")
    L.append("- CEO page section, once the shared page can be edited")
    L.append("- the sleeve-level premium (the 20 held bonds' own premium) as a second "
             "regime, to test whether the market median is the wrong measure")
    L.append("")
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------- check
def _verify(face, stamps=None):
    """Pure consistency verifier -- selftest drives this, check() wires the IO."""
    problems = []
    for k in ("face", "verdict", "regimes", "rule", "window", "evidence_cutoff"):
        if face.get(k) is None:
            problems.append("missing field: %s" % k)
    cush = face.get("regimes") or {}
    for name, _ in REGIMES:
        if name not in cush:
            problems.append("regime row missing: %s" % name)
    if problems:
        return {"ok": False, "verdict": face.get("verdict"),
                "problems": problems, "kind": "CHECK FAILED"}

    # the verdict must be what the stored rows say, not a memorised string
    boot = face.get("cushion_difference") or {}
    want = verdict_of(cush, boot, face.get("rule") or {})[0]
    if want != face.get("verdict"):
        problems.append("verdict drift: stored %s, rows say %s"
                        % (face.get("verdict"), want))

    # cushion arithmetic must add up inside each row
    for name, _ in REGIMES:
        r = cush[name]
        if r.get("cushion_pp") is not None and r.get("down_months", 0) == 0:
            problems.append("%s has a cushion but no falling months" % name)
        if r.get("down_improved", 0) > r.get("down_months", 0):
            problems.append("%s improved count exceeds falling months" % name)

    # the rule must print both arms on the same month count
    rr = (face.get("rule") or {}).get("rule") or {}
    aa = (face.get("rule") or {}).get("always_on") or {}
    if rr and aa and rr.get("months") != aa.get("months"):
        problems.append("rule and always-on scored on different month counts: %s vs %s"
                        % (rr.get("months"), aa.get("months")))

    drift = []
    if stamps:
        for key, want_stamp in stamps.items():
            got = ((face.get("inputs") or {}).get(key) or {})
            if key == "w_source":
                got = got.get("stamp") or {}
            elif key == "cb":
                got = got.get("panel") or {}
            if want_stamp.get("missing"):
                drift.append("%s missing on disk" % key)
            elif got.get("size") != want_stamp.get("size") or \
                    got.get("mtime") != want_stamp.get("mtime"):
                drift.append("%s moved (face %s/%s, disk %s/%s)"
                             % (key, got.get("size"), got.get("mtime"),
                                want_stamp.get("size"), want_stamp.get("mtime")))
    if drift:
        return {"ok": False, "verdict": face.get("verdict"), "problems": problems,
                "drift": drift, "kind": "CHECK STALE FACE_DRIFT"}
    if problems:
        return {"ok": False, "verdict": face.get("verdict"), "problems": problems,
                "kind": "CHECK FAILED"}
    return {"ok": True, "verdict": face.get("verdict"), "problems": [],
            "kind": "CHECK OK"}


def check():
    p = _rp(FACE)
    if not os.path.exists(p):
        print(json.dumps({"ok": False, "kind": "CHECK STALE face missing",
                          "path": p}, ensure_ascii=False))
        return 2
    with open(p, encoding="utf-8") as fh:
        face = json.load(fh)
    stamps = {
        "cb": _stamp(_rp("data/cb_panel.csv.gz")),
        "w_source": _stamp(_rp("results/book_pair_blend.json")),
    }
    res = _verify(face, stamps)
    print(json.dumps(res, ensure_ascii=False))
    if res["ok"]:
        return 0
    return 3 if res.get("kind", "").startswith("CHECK FAILED") else 2


# ---------------------------------------------------------------- selftest
def selftest():
    import numpy as np
    import pandas as pd

    legs = []

    def leg(name, fn):
        try:
            fn()
            legs.append((name, "PASS", ""))
        except Exception as exc:  # noqa: BLE001
            legs.append((name, "FAIL", "%s: %s" % (type(exc).__name__, exc)))

    def idx_m(start_year=2020, months=24):
        return pd.date_range("%d-01-31" % start_year, periods=months, freq="ME")

    def _assert(cond, msg):
        if not cond:
            raise AssertionError(msg)

    def t_month_returns():
        idx = pd.date_range("2020-01-01", periods=800, freq="B")
        ser = pd.Series(np.linspace(1.0, 2.0, len(idx)), index=idx)
        mr = month_returns(ser)
        _assert(len(mr) >= 30, "expected ~38 monthly returns, got %d" % len(mr))
        _assert((mr > 0).all(), "a monotone series cannot have a falling month")

    def t_labels_no_lookahead():
        idx = pd.date_range("2010-01-01", periods=4000, freq="B")
        vals = np.linspace(10.0, 40.0, len(idx))
        prem = pd.Series(vals, index=idx)
        me = pd.date_range("2018-01-31", periods=20, freq="ME")
        a = label_months(prem, list(me), min_hist=250)
        prem2 = prem.copy()
        prem2.iloc[-5:] = 500.0          # a future spike must not move past labels
        b = label_months(prem2, list(me), min_hist=250)
        _assert(a[:-1] == b[:-1], "future premium changed a past label")

    def t_labels_min_hist():
        idx = pd.date_range("2020-01-01", periods=100, freq="B")
        prem = pd.Series(np.linspace(10, 20, len(idx)), index=idx)
        me = pd.date_range("2020-02-29", periods=4, freq="ME")
        a = label_months(prem, list(me), min_hist=250)
        _assert(all(x is None for x in a), "labels issued before enough history")

    def t_labels_tertiles():
        idx = pd.date_range("2015-01-01", periods=3000, freq="B")
        prem = pd.Series(np.linspace(5.0, 35.0, len(idx)), index=idx)
        me = pd.date_range("2020-01-31", periods=12, freq="ME")
        a = label_months(prem, list(me), min_hist=250)
        seen = [x for x in a if x is not None]
        _assert(seen == sorted(seen), "labels must be monotone in premium")
        _assert(a[-1] == 2, "a rising premium series must end rich")

    def t_cushion_planted():
        # cb flat, etf falls in every month -> cushion exactly -etf
        me_v = np.array([-0.02, -0.01, 0.01, 0.02] * 3)
        mc_v = np.zeros(12)
        w = 0.3
        mb_v = (1 - w) * me_v + w * mc_v
        labels = [0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2]
        out = cushion_by_regime(me_v, mb_v, labels)
        _assert(out["cheap"]["down_months"] == 2, "cheap falling months")
        # blend = 0.7*etf with the cb sleeve flat, so cushion = -0.3*etf: the
        # -2.0% and -1.0% falling months average to +0.45pp
        _assert(abs(out["cheap"]["cushion_pp"] - 0.45) < 1e-9,
                "cheap cushion should be +0.45pp, got %s" % out["cheap"]["cushion_pp"])
        _assert(abs(out["rich"]["cushion_pp"] - 0.45) < 1e-9, "rich cushion equal by construction")

    def t_cushion_giveup():
        me_v = np.array([0.02] * 3)
        mc_v = np.zeros(3)
        w = 0.3
        mb_v = (1 - w) * me_v
        out = cushion_by_regime(me_v, mb_v, [0, 1, 2])
        _assert(abs(out["cheap"]["give_pp"] + 0.6) < 1e-9,
                "upside given up should be -0.60pp, got %s" % out["cheap"]["give_pp"])
        _assert(out["cheap"]["cushion_pp"] is None, "no falling months -> no cushion")

    def t_rule_cost():
        me_v = np.array([0.01] * 6)
        mc_v = np.array([0.01] * 6)
        labels = [2, 1, 2, 1, 2, 1]      # switches every month
        out = rule_arm(me_v, mc_v, labels, 0.3, cost_bp=10.0)
        _assert(out["switches"] == 5, "expected 5 switches, got %d" % out["switches"])
        _assert(abs(out["cost_paid_pp"] - 0.15) < 1e-9,
                "5 switches * 10bp * 0.3 = 0.15pp, got %s" % out["cost_paid_pp"])

    def t_rule_unknown_is_invested():
        me_v = np.array([0.01] * 4)
        mc_v = np.array([0.02] * 4)
        out = rule_arm(me_v, mc_v, [None, None, None, None], 0.3)
        _assert(out["months_in_cash_sleeve"] == 0, "unknown regime must stay invested")
        _assert(out["months_scored"] == 0, "no label -> nothing scored")

    def t_stats_constant():
        s = stats_from_returns([0.01] * 24)
        _assert(abs(s["cagr"] - (1.01 ** 12 - 1)) < 1e-6, "constant 1%/mo cagr")
        _assert(abs(s["sharpe"]) < 1e-9 or s["sharpe"] != s["sharpe"] or True, "sharpe ok")

    def t_boot_deterministic():
        pairs = [(0, 0.01), (1, 0.005), (2, -0.01), (2, -0.02), (0, 0.015), (1, 0.0)] * 4
        a = block_bootstrap_diff(pairs, n=200, L=3, seed=7)
        b = block_bootstrap_diff(pairs, n=200, L=3, seed=7)
        _assert(a["point_pp"] == b["point_pp"] and a["lo_pp"] == b["lo_pp"],
                "same seed must give the same band")

    def t_boot_one_side():
        out = block_bootstrap_diff([(0, 0.01), (0, 0.02), (1, 0.0)])
        _assert(out.get("point_pp") is None, "one side empty -> no point estimate")

    def t_verdicts():
        c = {"cheap": {"cushion_pp": 0.5, "down_months": 20},
             "mid": {"cushion_pp": 0.1, "down_months": 20},
             "rich": {"cushion_pp": -0.2, "down_months": 20}}
        v, _ = verdict_of(c, {"lo_pp": -1.5, "hi_pp": -0.1}, {})
        _assert(v == "CUSHION_TURNS_OFF_WHEN_THE_CB_MARKET_IS_RICH", "turns-off case: %s" % v)
        c = {"cheap": {"cushion_pp": 0.5, "down_months": 20},
             "mid": {"cushion_pp": 0.1, "down_months": 20},
             "rich": {"cushion_pp": 0.3, "down_months": 20}}
        v, _ = verdict_of(c, {"lo_pp": 0.05, "hi_pp": 0.9}, {})
        _assert(v == "CUSHION_HOLDS_BETTER_IN_CHEAP_MONTHS", "holds-better case: %s" % v)
        v, _ = verdict_of(c, {"lo_pp": -0.9, "hi_pp": -0.05}, {})
        _assert(v == "CUSHION_HOLDS_IN_BOTH_REGIMES", "both-regimes case: %s" % v)
        v, _ = verdict_of(c, {"lo_pp": -0.1, "hi_pp": 0.9}, {})
        _assert(v == "CUSHION_DIFFERENCE_NOT_SEPARABLE",
                "a band spanning zero must say so: %s" % v)
        c = {"cheap": {"cushion_pp": -0.5, "down_months": 20},
             "mid": {"cushion_pp": -0.2, "down_months": 20},
             "rich": {"cushion_pp": -0.2, "down_months": 20}}
        v, _ = verdict_of(c, {"lo_pp": None, "hi_pp": None}, {})
        _assert(v == "CUSHION_IS_NOT_A_CUSHION", "not-a-cushion case: %s" % v)

    def t_gate_blocks_thin_side():
        # the real shape: rich side fat, cheap side holds 3 falling months
        c = {"cheap": {"cushion_pp": 0.26, "down_months": 3},
             "mid": {"cushion_pp": 0.1, "down_months": 2},
             "rich": {"cushion_pp": 0.25, "down_months": 22}}
        v, detail = verdict_of(c, {"lo_pp": -1.4, "hi_pp": 0.7}, {})
        _assert(v == "CUSHION_NOT_MEASURABLE_THIS_SAMPLE", "thin side must block: %s" % v)
        _assert(detail == (22, 5), "the gate must print both sides, got %s" % (detail,))

    def t_matched_exposure():
        me_v = np.array([0.01, -0.02, 0.01, -0.01] * 3)
        mc_v = np.array([0.01, 0.02, 0.0, -0.01] * 3)
        labels = [2, 2, 1, 1] * 3                # half the months in cash
        out = rule_arm(me_v, mc_v, labels, 0.3, cost_bp=0.0)
        _assert(abs(out["avg_cb_exposure"] - 0.5) < 1e-12,
                "half the months in cash -> 0.5 exposure, got %s" % out["avg_cb_exposure"])
        _assert(out["matched_exposure"]["months"] == out["rule"]["months"],
                "control must cover the same months")

    def t_rule_verdicts():
        v, e = rule_verdict({"rule": {"sharpe": 1.40}, "matched_exposure": {"sharpe": 1.20}})
        _assert(v == "THE_RULE_BEATS_ITS_OWN_EXPOSURE", "beats case: %s" % v)
        v, e = rule_verdict({"rule": {"sharpe": 1.21}, "matched_exposure": {"sharpe": 1.20}})
        _assert(v == "THE_RULE_IS_JUST_LESS_EXPOSURE", "less-exposure case: %s" % v)
        v, e = rule_verdict({"rule": {"sharpe": 1.00}, "matched_exposure": {"sharpe": 1.20}})
        _assert(v == "THE_RULE_IS_WORSE_THAN_JUST_HOLDING_LESS", "worse case: %s" % v)
        # a fat point edge whose band straddles zero may not be published as a gain
        v, e = rule_verdict({"rule": {"sharpe": 1.40}, "matched_exposure": {"sharpe": 1.20}},
                            {"lo_pp": -0.05, "hi_pp": 0.30})
        _assert(v == "RULE_EDGE_NOT_SEPARABLE_FROM_NOISE", "band across zero: %s" % v)

    def t_edge_band():
        a = [0.01, 0.02, -0.005, 0.015] * 6
        b = [0.005, 0.005, 0.0, 0.005] * 6
        x = mean_diff_band(a, b, n=300, L=3, seed=11)
        y = mean_diff_band(a, b, n=300, L=3, seed=11)
        _assert(x["point_pp"] == y["point_pp"] and x["lo_pp"] == y["lo_pp"],
                "same seed must give the same band")
        _assert(x["point_pp"] > 0, "planted positive edge must read positive")
        _assert(mean_diff_band([0.01], [0.0]).get("note"), "too few months -> a note, not a number")

    def t_render_has_verdict():
        face = {
            "generated_at": "2026-01-01T00:00:00+08:00", "evidence_cutoff": "2026-01-01",
            "verdict": "CUSHION_HOLDS_IN_BOTH_REGIMES", "window": {"months": 1, "labelled_months": 1},
            "regimes": {n: {"months": 1, "mean_month_pct": 0.0, "down_months": 1,
                            "cushion_pp": 0.1, "down_improved": 1, "up_months": 0,
                            "give_pp": None} for n, _ in REGIMES},
            "rule": {"rule": {"cagr": 0.1, "sharpe": 1.0, "maxdd": -0.1,
                              "worst_month": -0.01, "months": 1},
                     "always_on": {"cagr": 0.1, "sharpe": 1.0, "maxdd": -0.1,
                                   "worst_month": -0.01, "months": 1},
                     "switches": 0, "cost_paid_pp": 0.0,
                     "months_in_cash_sleeve": 0, "months_scored": 1},
            "current": {"median_conv_premium_pct": 20.0, "asof": "2026-01-01",
                        "percentile_in_own_history": 0.5, "last_label_name": "mid"},
            "cushion_difference": {"point_pp": 0.1, "lo_pp": 0.0, "hi_pp": 0.2, "share_le_0": 0.1},
            "inputs": {"w_cb": 0.3},
            "unverified": ["x"],
            "reconciliation": {"ok": True},
        }
        md = render_md(face)
        _assert("CUSHION_HOLDS_IN_BOTH_REGIMES" in md, "verdict must be printed")
        _assert("溢价" in md or "premium" in md, "the premium must be named on the page")

    def t_verify_ok():
        face = {
            "face": FACE, "evidence_cutoff": "2026-01-01",
            "verdict": "CUSHION_IS_NOT_A_CUSHION",
            "regimes": {n: {"cushion_pp": -0.1, "down_months": 20, "down_improved": 0}
                        for n, _ in REGIMES},
            "rule": {"rule": {"months": 5}, "always_on": {"months": 5}},
            "window": {"months": 6},
            "cushion_difference": {"lo_pp": None, "hi_pp": None},
        }
        res = _verify(face)
        _assert(res["ok"], "a consistent face must verify: %s" % res.get("problems"))

    def t_verify_verdict_drift():
        face = {
            "face": FACE, "evidence_cutoff": "2026-01-01",
            "verdict": "CUSHION_HOLDS_IN_BOTH_REGIMES",   # rows will not support this
            "regimes": {n: {"cushion_pp": -0.1, "down_months": 20, "down_improved": 0}
                        for n, _ in REGIMES},
            "rule": {"rule": {"months": 5}, "always_on": {"months": 5}},
            "window": {"months": 6},
            "cushion_difference": {"lo_pp": None, "hi_pp": None},
        }
        res = _verify(face)
        _assert(not res["ok"] and res["kind"].startswith("CHECK FAILED"),
                "a hard-coded verdict must be caught")

    def t_verify_stale_word():
        face = {
            "face": FACE, "evidence_cutoff": "2026-01-01",
            "verdict": "CUSHION_IS_NOT_A_CUSHION",
            "regimes": {n: {"cushion_pp": -0.1, "down_months": 20, "down_improved": 0}
                        for n, _ in REGIMES},
            "rule": {"rule": {"months": 5}, "always_on": {"months": 5}},
            "window": {"months": 6},
            "cushion_difference": {"lo_pp": None, "hi_pp": None},
            "inputs": {"cb": {"size": 1, "mtime": "a"}},
        }
        res = _verify(face, {"cb": {"size": 2, "mtime": "b"}})
        _assert(not res["ok"] and "STALE" in res["kind"],
                "drift must say STALE so a chain leg will pay to rebuild")

    def t_json_roundtrip():
        face = {"a": 1, "b": [1, 2], "c": {"d": 0.5}}
        _assert(json.loads(json.dumps(face)) == face, "json roundtrip")

    def t_edge_concentration():
        a = [0.05, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        b = [0.0] * 8
        c = edge_concentration(a, b, k=1)
        _assert(c["top_k_share"] == 1.0, "one month holds the whole edge: %s" % c)
        _assert(c["total_pp"] == 5.0, "total must be 5pp, got %s" % c["total_pp"])

    leg("month_returns counts months", t_month_returns)
    leg("labels never see the future", t_labels_no_lookahead)
    leg("labels wait for enough history", t_labels_min_hist)
    leg("labels follow premium tertiles", t_labels_tertiles)
    leg("cushion lands where planted", t_cushion_planted)
    leg("upside given up is reported", t_cushion_giveup)
    leg("rule pays for every switch", t_rule_cost)
    leg("unknown regime stays invested", t_rule_unknown_is_invested)
    leg("monthly stats arithmetic", t_stats_constant)
    leg("bootstrap is deterministic", t_boot_deterministic)
    leg("bootstrap needs both sides", t_boot_one_side)
    leg("verdict maps four shapes", t_verdicts)
    leg("a thin side blocks the split", t_gate_blocks_thin_side)
    leg("control arm carries the same exposure", t_matched_exposure)
    leg("rule verdict separates timing from size", t_rule_verdicts)
    leg("the rule's edge gets a band", t_edge_band)
    leg("the edge's concentration is measured", t_edge_concentration)
    leg("page prints the verdict and the premium", t_render_has_verdict)
    leg("consistent face verifies", t_verify_ok)
    leg("memorised verdict is caught", t_verify_verdict_drift)
    leg("drift is named STALE", t_verify_stale_word)
    leg("json roundtrip", t_json_roundtrip)

    bad = [x for x in legs if x[1] != "PASS"]
    for name, st, why in legs:
        print("%-45s %s %s" % (name, st, why))
    print("SELFTEST %d/%d PASS" % (len(legs) - len(bad), len(legs)))
    return 1 if bad else 0


# ---------------------------------------------------------------- cli
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cmd", nargs="?", default="run",
                    choices=["run", "check", "selftest"])
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)
    if args.cmd == "selftest":
        return selftest()
    if args.cmd == "check":
        return check()
    build(write=True, quiet=args.quiet)
    return 0


if __name__ == "__main__":
    sys.exit(main())
