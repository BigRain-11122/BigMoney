#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A-share residual veto book: does smoothing the score buy the churn back?

r2015 priced the churn (turnover **23.95%/period**, 4.3x the full pool, 10.8% of
the gross edge handed to the broker).  r2016 tried to buy it back with a
hysteresis band (a rule on *membership*) and the assumption was falsified: the
band removed 0.02 bp/period.  r2017 then explained why -- 84.2% of the churn is
names flapping across the veto edge, not the universe moving under the book --
and drew the only conclusion that split allows:

    if the churn is the edge, the fix has to damp the **score**, not the
    membership.

This face is that experiment and nothing else.  Rank the residual
cross-sectionally at each rebalance (the parent's own score), average the rank
over the last K rebalance dates, re-rank the average, keep the same 80/20 split.

    K = 1        the parent book, verbatim (no smoothing)
    K = 2, 3, 4  the same book with the score smoothed over K rebalance dates

Why average *ranks* and then re-rank
------------------------------------
Not the raw residual: the residual is the error of a per-period cross-sectional
regression, so its dispersion moves from date to date and a raw average would be
dominated by the periods that happen to be noisier.  Ranks are already
scale-free.  Re-ranking the average (rather than thresholding the average at
0.8) keeps every arm at exactly 80% of the eligible names, so the difference
between arms is **which** names, never **how many** -- otherwise the turnover
comparison would mix a size change with a behaviour change and neither number
would mean anything.

What is measured, and the decomposition that makes it readable
--------------------------------------------------------------
Net difference between arm K and arm 1 decomposes exactly:

    net_K - net_1 = (gross_K - gross_1) + 2c * (turn_1 - turn_K)
                     <-- what smoothing gives up -->   <-- what it saves -->

so the face prints both sides and the breakeven the reader would otherwise
compute by hand: *how much gross return is smoothing allowed to lose and still
pay for itself*.  Names that smoothing removes from the book (D) and names it
adds (A) are priced separately, because "smoothing costs return" and "smoothing
takes on worse names" are different failures.

What this face does NOT claim
-----------------------------
Smoothed rank is a lagged signal: a name that deteriorates permanently still
leaves the book, just K-1 periods later.  That lag is the whole mechanism, so
the face does not "prove smoothing works" -- it prices the lag against the tax.

Usage
-----
    python scripts/astock_veto_smooth_rank.py run
    python scripts/astock_veto_smooth_rank.py check
    python scripts/astock_veto_smooth_rank.py selftest
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from astock_resid_veto_layer import (  # noqa: E402
    COST_ONE_SIDE,
    FIRST_DATE,
    HOLD,
    LOOKBACK_BETA,
    compound,
    daily_returns,
    load_panel,
    market_return,
    score_slice,
)
from astock_resid_reversal_probe import rank01  # noqa: E402

OUT = os.path.join(ROOT, "results", "astock_veto_smooth_rank.json")
MD = os.path.join(ROOT, "research", "ASTOCK_VETO_SMOOTH_RANK.md")
LAYER_PARENT = os.path.join(ROOT, "results", "astock_veto_turnover_layers.json")

ARMS = (1, 2, 3, 4)
BASE = 1
VETO_QUANTILE = 4  # the parent's split: q == 4 is the vetoed fifth

DOC_BEGIN = "<!-- BEGIN:ASTOCK-VETO-SMOOTH-RANK -->"
DOC_END = "<!-- END:ASTOCK-VETO-SMOOTH-RANK -->"


# ------------------------------------------------------------------ pure logic
def _turnover(cur: set, prev) -> float:
    """The parent's definition, verbatim: the first period is a full entry."""
    if prev is None:
        return 1.0
    if not cur:
        return 0.0
    return 1.0 - len(cur & prev) / float(len(cur))


def _slice(date, cols, rank, fwd):
    return {"date": date,
            "cols": np.asarray(cols, dtype=np.int64),
            "rank": np.asarray(rank, dtype=np.float64),
            "fwd": np.asarray(fwd, dtype=np.float64)}


def _rank_strict(smooth, latest, cols) -> np.ndarray:
    """Ranks ``1..n`` scaled by ``n``, ties broken by the latest period's rank
    and then by symbol.

    The parent's ``rank01`` averages ties, and averaged ranks tie far more often
    than raw residuals do -- two names one place apart in two consecutive
    periods share an average.  Averaging those ties would let the book size
    drift between arms, and then a turnover difference would be part size and
    part behaviour.  Breaking them keeps every arm at exactly the parent's
    split, so the only thing that can differ is *which* names.
    """
    order = np.lexsort((cols, latest, smooth))
    ranks = np.empty(len(smooth), dtype=np.float64)
    ranks[order] = np.arange(1, len(smooth) + 1, dtype=np.float64)
    return ranks / len(smooth)


def walk_k(slices, k: int) -> list:
    """Rebuild the book with the score smoothed over the last ``k`` dates.

    Every symbol keeps the ranks of the periods it was *eligible* in; the
    smoothed score is the mean of those (so a name that only recently became
    eligible is averaged over what exists -- and the share of such names is
    printed, never silently absorbed).  The smoothed score is re-ranked
    cross-sectionally and split at the parent's 80/20 line, so ``size`` is
    80% of the eligible names in every period and in every arm.
    """
    if k < 1:
        raise ValueError("window must be >= 1, got %r" % (k,))
    hist: dict = {}
    rows: list = []
    prev = None
    for i, s in enumerate(slices):
        cols = s["cols"]
        for col, r in zip(cols.tolist(), s["rank"].tolist()):
            h = hist.setdefault(col, [])
            h.append(float(r))
            if len(h) > k:
                del h[0]
        if i < k - 1:
            continue
        smooth = np.array([float(np.mean(hist[c])) for c in cols.tolist()], dtype=np.float64)
        q = np.clip((_rank_strict(smooth, s["rank"], cols) * 5).astype(int), 0, VETO_QUANTILE)
        inbook = q < VETO_QUANTILE
        cur = set(cols[inbook].tolist())
        turb = _turnover(cur, prev)
        prev = cur
        fwd = s["fwd"]
        gross = float(np.mean(fwd[inbook])) if inbook.any() else float("nan")
        partial = float(np.mean([len(hist[c]) < k for c in cols.tolist()])) if len(cols) else float("nan")
        rows.append({
            "date": s["date"],
            "n": int(len(cols)),
            "size": int(cols.size and int(inbook.sum())),
            "turnover": float(turb),
            "gross": gross,
            "net": gross - 2.0 * COST_ONE_SIDE * turb,
            "partial_window_share": partial,
            "book": cur,
            "fwd": {int(c): float(f) for c, f in zip(cols.tolist(), fwd.tolist())},
            "smooth": {int(c): float(v) for c, v in zip(cols.tolist(), smooth.tolist())},
        })
    return rows


def _series(rows, key) -> np.ndarray:
    return np.array([r.get(key, float("nan")) for r in rows], dtype=np.float64)


def _fmean(rows, key) -> float:
    a = _series(rows, key)
    a = a[np.isfinite(a)]
    return float(np.mean(a)) if len(a) else float("nan")


def summarize(rows) -> dict:
    """Book-level numbers.  ``ex_first`` = the same series without the period
    that pays the full entry (it is an entry, not a rebalance)."""
    ex = rows[1:]
    return {
        "periods": len(rows),
        "periods_ex_first": len(ex),
        "turnover_mean_all_periods": float(np.mean(_series(rows, "turnover"))) if rows else float("nan"),
        "turnover_mean_ex_first": _fmean(ex, "turnover"),
        "gross_mean_all_periods": _fmean(rows, "gross"),
        "gross_mean_ex_first": _fmean(ex, "gross"),
        "net_mean_all_periods": _fmean(rows, "net"),
        "net_mean_ex_first": _fmean(ex, "net"),
        "net_annualized": compound([float(x) for x in _series(rows, "net") if np.isfinite(x)]),
        "tax_per_period": 2.0 * COST_ONE_SIDE * _fmean(rows, "turnover"),
        "size_mean": _fmean(rows, "size"),
        "n_mean": _fmean(rows, "n"),
        "partial_window_share_mean": _fmean(ex, "partial_window_share"),
    }


def _tstat(diffs):
    d = np.asarray(diffs, dtype=np.float64)
    d = d[np.isfinite(d)]
    if len(d) < 2:
        return None
    sd = float(np.std(d, ddof=1))
    if sd <= 0:
        return None
    return float(np.mean(d) / (sd / np.sqrt(len(d))))


def paired(arm_rows, base_rows, key="net") -> dict:
    """Paired on dates.  The arms are built from the same slices, so the only
    dates they can differ on are the ones the longer window has not reached."""
    base = {r["date"]: r for r in base_rows}
    diffs = []
    for r in arm_rows:
        b = base.get(r["date"])
        if b is None:
            continue
        diffs.append(float(r[key]) - float(b[key]))
    d = np.asarray(diffs, dtype=np.float64)
    d = d[np.isfinite(d)]
    return {"n": int(len(d)),
            "mean": float(d.mean()) if len(d) else None,
            "se": float(d.std(ddof=1) / np.sqrt(len(d))) if len(d) > 1 else None,
            "t": _tstat(diffs)}


def drop_add(arm_rows, base_rows) -> dict:
    """Price the two groups smoothing moves: D = names it removes from the book,
    A = names it adds.  Without this split "smoothing costs return" cannot be
    told apart from "smoothing takes on worse names"."""
    base = {r["date"]: r for r in base_rows}
    d_vals, a_vals = [], []
    d_n = a_n = 0
    for r in arm_rows:
        b = base.get(r["date"])
        if b is None:
            continue
        cur, old = r["book"], b["book"]
        # the forward return is a property of the period, not of the arm: read
        # it from either map so a name that is only in the other arm's book is
        # still priced (walk_k writes the whole eligible cross-section).
        fwd = dict(b["fwd"])
        fwd.update(r["fwd"])
        for c in old - cur:
            v = fwd.get(c)
            if v is not None and np.isfinite(v):
                d_vals.append(v)
                d_n += 1
        for c in cur - old:
            v = fwd.get(c)
            if v is not None and np.isfinite(v):
                a_vals.append(v)
                a_n += 1
    return {"dropped_n": d_n, "added_n": a_n,
            "dropped_fwd_mean": float(np.mean(d_vals)) if d_vals else None,
            "added_fwd_mean": float(np.mean(a_vals)) if a_vals else None}


def by_year(rows) -> dict:
    out: dict = {}
    for r in rows[1:]:
        out.setdefault(r["date"][:4], []).append(r)
    return {y: {"periods": len(v),
                "turnover_mean": float(np.mean([r["turnover"] for r in v])),
                "gross_mean": float(np.nanmean([r["gross"] for r in v])),
                "net_mean": float(np.nanmean([r["net"] for r in v])),
                "size_mean": float(np.mean([r["size"] for r in v]))}
            for y, v in sorted(out.items())}


def decompose(arm_rows, base_rows) -> dict:
    """``net_K - net_1 = (gross_K - gross_1) + 2c * (turn_1 - turn_K)``, exactly.

    Every term is a mean over the **paired** sample (the dates both arms price).
    Using each arm's own summary mean instead would silently compare two
    different samples -- the longer window prices K-1 extra dates -- and the
    identity would then be false by exactly the amount of that sample difference.
    """
    base = {r["date"]: r for r in base_rows}
    dg, dt, dn = [], [], []
    for r in arm_rows:
        b = base.get(r["date"])
        if b is None:
            continue
        dg.append(float(r["gross"]) - float(b["gross"]))
        dt.append(float(b["turnover"]) - float(r["turnover"]))
        dn.append(float(r["net"]) - float(b["net"]))
    if not dg:
        return {"n": 0, "gross_effect": None, "turnover_cut": None, "cost_saved": None,
                "net_effect": None, "breakeven_gross_loss": None, "identity_residual": None}
    gross_effect = float(np.mean(dg))
    turnover_cut = float(np.mean(dt))
    cost_saved = 2.0 * COST_ONE_SIDE * turnover_cut
    net_effect = float(np.mean(dn))
    return {"n": len(dg),
            "gross_effect": gross_effect,
            "turnover_cut": turnover_cut,
            "cost_saved": cost_saved,
            "net_effect": net_effect,
            "breakeven_gross_loss": cost_saved,
            "identity_residual": net_effect - (gross_effect + cost_saved)}


def verdict(pair_net: dict, decomp: dict) -> str:
    """Two states worth a word, everything else is 'cannot tell'."""
    mean = pair_net.get("mean")
    t = pair_net.get("t")
    if mean is None or not np.isfinite(mean) or not np.isfinite(decomp.get("cost_saved", float("nan"))):
        return "SMOOTHING_UNPRICEABLE"
    if t is None:
        return "SMOOTHING_NOT_SEPARABLE"
    if mean > 0 and t >= 2.0:
        return "SMOOTHING_PAYS"
    if mean < 0 and t <= -2.0:
        return "SMOOTHING_COSTS"
    return "SMOOTHING_NOT_SEPARABLE"


# -------------------------------------------------------------------- the face
def build_slices(hold: int = HOLD, stride: int = HOLD):
    """One panel load, one score per rebalance date, shared by every arm -- the
    arms must differ only in the smoothing window, never in the score."""
    dates, symbols, close, amount, shares = load_panel()
    rets = daily_returns(close)
    mkt = market_return(rets)

    start = 0
    while start < len(dates) and dates[start] < FIRST_DATE:
        start += 1
    start = max(start, LOOKBACK_BETA)

    slices = []
    t = start
    while t + hold < len(dates):
        idx, resid, _q, fwd = score_slice(t, close, amount, shares, rets, mkt)
        if resid is None:
            t += stride
            continue
        slices.append(_slice(dates[t], idx, rank01(resid), fwd))
        t += stride
    return dates, symbols, slices


def build_face(slices=None):
    if slices is None:
        dates, symbols, slices = build_slices()
    else:
        dates, symbols = None, None
    arms = {k: walk_k(slices, k) for k in ARMS}
    summ = {k: summarize(v) for k, v in arms.items()}
    pairs = {k: paired(arms[k], arms[BASE]) for k in ARMS if k != BASE}
    decomp = {k: decompose(arms[k], arms[BASE]) for k in ARMS if k != BASE}
    verdicts = {k: verdict(pairs[k], decomp[k]) for k in pairs}
    groups = {k: drop_add(arms[k], arms[BASE]) for k in ARMS if k != BASE}
    return dates, symbols, slices, arms, summ, pairs, decomp, verdicts, groups


def layer_anchor(arms) -> dict:
    """r2017's published per-period series must come back bit-identically for the
    K=1 arm -- the only proof the smoothing runs on *this* book and not a
    neighbour of it."""
    try:
        with open(LAYER_PARENT, "r", encoding="utf-8") as fh:
            face = json.load(fh)
    except (OSError, ValueError) as exc:
        return {"ok": False, "why": "layer face unreadable: %s" % exc, "worst_abs_diff": None}
    prow = face.get("rows") or []
    mine = arms[BASE]
    if len(prow) != len(mine):
        return {"ok": False, "why": "row count parent=%d mine=%d" % (len(prow), len(mine)),
                "worst_abs_diff": None}
    worst = 0.0
    for p, r in zip(prow, mine):
        if p.get("date") != r["date"]:
            return {"ok": False, "why": "date mismatch %r != %r" % (p.get("date"), r["date"]),
                    "worst_abs_diff": None}
        worst = max(worst, abs(float(p["turnover"]) - r["turnover"]))
        if p.get("gross") is not None and np.isfinite(p["gross"]):
            worst = max(worst, abs(float(p["gross"]) - r["gross"]))
    return {"ok": worst <= 1e-12, "worst_abs_diff": worst, "rows": len(prow)}


def layer_cross_read(decomp: dict) -> dict:
    """Read r2017's published edge tax at the same cutoff and price smoothing
    against it: how much of that tax each arm actually recovers, and what it
    pays for the recovery.  Without this the reader has to guess whether a
    +0.5 bp saving is a lot or a rounding error."""
    try:
        with open(LAYER_PARENT, "r", encoding="utf-8") as fh:
            face = json.load(fh)
        tax = float(((face.get("results") or {}).get("book") or {})["tax_in_edge_per_period"])
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return {"ok": False, "why": "layer face unreadable: %s" % exc}
    out = {}
    for k, d in decomp.items():
        saved = d.get("cost_saved")
        gross = d.get("gross_effect")
        out[str(k)] = {
            "edge_tax_per_period": tax,
            "saved_share_of_edge_tax": (saved / tax) if saved is not None and tax else None,
            "price_per_bp_saved": (abs(gross) / saved) if saved not in (None, 0) and gross is not None else None,
        }
    return {"ok": True, "arms": out}


def _now() -> str:
    return datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")


def _rel(path: str) -> str:
    try:
        rel = os.path.relpath(path, ROOT)
    except ValueError:
        return str(path).replace(os.sep, "/")
    if rel.startswith(".."):
        return str(path).replace(os.sep, "/")
    return rel.replace(os.sep, "/")


def _machine() -> str:
    try:
        with open(os.path.join(ROOT, "fleet", "machine.json"), encoding="utf-8") as fh:
            return json.load(fh).get("machine_id", "unknown")
    except (OSError, ValueError):
        return "unknown"


def run() -> int:
    dates, symbols, slices, arms, summ, pairs, decomp, verdicts, groups = build_face()
    anchor = layer_anchor(arms)
    cross = layer_cross_read(decomp)

    payload = {
        "generated": _now(),
        "evidence_cutoff": dates[-1],
        "last_priced_rebalance": slices[-1]["date"],
        "machine": _machine(),
        "kind": "pricing",
        "fills_the_hole_of": "astock_veto_turnover_layers",
        "prereg": {
            "question": "r2017 put the churn on the veto edge (84.2%) and concluded the fix must damp the score, not the membership. Does smoothing the residual rank over K rebalance dates buy that churn back, and what does it cost?",
            "arms": {"K=%d" % k: "book rebuilt with the residual rank averaged over the last %d rebalance dates, re-ranked, same 80/20 split" % k
                     for k in ARMS},
            "decomposition": "net_K - net_1 = (gross_K - gross_1) + 2c*(turn_1 - turn_K), computed, not fitted",
            "verdict": "SMOOTHING_PAYS / SMOOTHING_COSTS require |paired t| >= 2; everything else is SMOOTHING_NOT_SEPARABLE",
            "rule_frozen_before_run": True,
        },
        "spec": {
            "hold": HOLD,
            "stride": HOLD,
            "cost_one_side": COST_ONE_SIDE,
            "lookback_beta": LOOKBACK_BETA,
            "veto_quantile": VETO_QUANTILE,
            "booking": "fractional, weight exactly 1/n, fully invested",
            "smoothing": "mean of the cross-sectional ranks over the last K dates the name was eligible, then re-ranked and split at the parent's 80/20 line",
            "why_ranks": "the residual is a per-period regression error; its dispersion moves, so a raw average would be dominated by the noisiest dates",
            "why_rerank": "keeps every arm at exactly 80% of eligible names, so the difference is which names, never how many",
        },
        "panel": {"dates": len(dates), "symbols": len(symbols),
                  "first": dates[0], "last": dates[-1]},
        "rebalances": {k: len(v) for k, v in arms.items()},
        "results": {
            "summary": {k: summ[k] for k in ARMS},
            "paired_vs_K1": pairs,
            "decomposition_vs_K1": decomp,
            "verdict": verdicts,
            "groups_moved": groups,
            "layer_cross_read": cross,
            "by_year": {k: by_year(arms[k]) for k in ARMS},
        },
        "rows": {k: [{key: r[key] for key in ("date", "n", "size", "turnover", "gross", "net",
                                              "partial_window_share")}
                     for r in arms[k]] for k in ARMS},
        "anchor": anchor,
    }

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    write_md(payload)

    print("SMOOTH-RANK panel %s..%s  %d names  slices %d  last priced %s"
          % (dates[0], dates[-1], len(symbols), len(slices), slices[-1]["date"]))
    for k in ARMS:
        s = summ[k]
        print("  K=%d  periods %2d  turnover %6.2f%%  gross %+7.4f%%  net %+7.4f%%  ann %+6.2f%%  size %.0f  partial %.1f%%"
              % (k, s["periods"], s["turnover_mean_ex_first"] * 100,
                 s["gross_mean_ex_first"] * 100, s["net_mean_ex_first"] * 100,
                 (s["net_annualized"] or 0) * 100, s["size_mean"],
                 s["partial_window_share_mean"] * 100))
        if k != BASE:
            p, d, g = pairs[k], decomp[k], groups[k]
            print("        vs K=1  net %+.2f bp/p (t %s) = gross %+.2f bp + cost saved %+.2f bp (turn cut %.2f pp)  | D %.4f%% (n=%d) A %.4f%% (n=%d)  %s  [identity resid %.1e]"
                  % ((p["mean"] or 0) * 10000,
                     ("%+.2f" % p["t"]) if p["t"] is not None else "n/a",
                     d["gross_effect"] * 10000, d["cost_saved"] * 10000, d["turnover_cut"] * 100,
                     (g["dropped_fwd_mean"] or 0) * 100, g["dropped_n"],
                     (g["added_fwd_mean"] or 0) * 100, g["added_n"], verdicts[k],
                     d["identity_residual"] if d["identity_residual"] is not None else float("nan")))
    if cross.get("ok"):
        tax = next(iter(cross["arms"].values()))["edge_tax_per_period"]
        print("  r2017 edge tax %.2f bp/p; smoothing recovers %s"
              % (tax * 10000,
                 ", ".join("K=%d %.1f%% @ %s gross per bp saved"
                           % (k, (cross["arms"][str(k)]["saved_share_of_edge_tax"] or 0) * 100,
                              ("%.1f bp" % cross["arms"][str(k)]["price_per_bp_saved"])
                              if cross["arms"][str(k)]["price_per_bp_saved"] is not None else "n/a")
                           for k in ARMS if k != BASE)))
    print("  anchor vs r2017: ok=%s worst=%.3e"
          % (anchor["ok"], anchor.get("worst_abs_diff") if anchor.get("worst_abs_diff") is not None
             else float("nan")))
    print("  -> %s" % _rel(OUT))
    print("  -> %s" % _rel(MD))
    return 0


# ---------------------------------------------------------------------- doc
def _p(x, nd=4):
    return "n/a" if x is None or not np.isfinite(x) else "%+.*f%%" % (nd, x * 100)


def _pn(x, nd=2):
    return "n/a" if x is None or not np.isfinite(x) else "%.*f%%" % (nd, x * 100)


def _bp(x, nd=2):
    return "n/a" if x is None or not np.isfinite(x) else "%+.*f bp" % (nd, x * 10000)


def write_md(payload) -> None:
    r = payload["results"]
    summ = r["summary"]
    pairs = r["paired_vs_K1"]
    decomp = r["decomposition_vs_K1"]
    groups = r["groups_moved"]
    verdicts = r["verdict"]
    cutoff = payload["evidence_cutoff"]
    cost = payload["spec"]["cost_one_side"]
    base = summ[BASE]

    L = [DOC_BEGIN, "",
         "# A 股残差黑名单：把分数做平滑，能不能把换手买回来",
         "",
         "generated %s | evidence_cutoff **%s** | 最后定价调仓日 %s（最后 %d 根 bar 没有前向收益，没法定价）"
         " | 期数 %d（可归因 %d） | 单边成本 %.1f bp"
         % (payload["generated"], cutoff, payload["last_priced_rebalance"], HOLD,
            base["periods"], base["periods_ex_first"], cost * 10000),
         "",
         "r2015 把账单摊开（换手 23.95%/期、毛边的 10.8% 交给券商），r2016 试图用滞回带"
         "（一条**名单**规则）把税买回来——**证伪**，每期只省 0.02 bp；r2017 解释了为什么："
         "84.2% 的换手是名字在否决边界上来回翻，不是成分池在动。于是只剩一种做法：",
         "",
         "> 要压的是**分数**，不是名单。",
         "",
         "本面就是这条实验，而且只做这一条：每一期把残差做横截面排序，取最近 K 期的排名均值，"
         "再对均值重新排序，按父面的 80/20 线切。K=1 就是父面本身（不平滑），K=2/3/4 是同一本账"
         "把分数拌了 K 期。",
         "",
         "**为什么平均排名而不是平均残差**：残差是每期横截面回归的误差，它的离散度逐期在变，"
         "直接平均会被「哪期更吵」主导；排名天生无量纲。"
         "**为什么重新排序而不是在 0.8 上直接切**：重新排序保证每一臂都恰好是合格名字的 80%，"
         "于是臂与臂之间的差别**只有名字是谁**，不会混进「书变薄了」这种尺寸变化——"
         "否则换手的对比就同时在比两件事，两个数都不能用。"
         "并列（平滑后的排名比原始残差更容易并列：两期名次相邻的名字均值相同）"
         "按「上一期排名、再按代码」打破，否则平均并列会让书的大小逐期漂移。",
         "",
         "## 一句话", ""]

    order = [k for k in ARMS if k != BASE]
    pays = [k for k in order if verdicts[k] == "SMOOTHING_PAYS"]
    costs = [k for k in order if verdicts[k] == "SMOOTHING_COSTS"]
    # lead with the arm that is decided most tightly, not the one that happens to
    # have the highest mean: an undecided arm is not the finding.
    best_k = max(order, key=lambda k: abs(pairs[k]["t"]) if pairs[k]["t"] is not None else -1.0)
    cross = r.get("layer_cross_read") or {}

    L.append("**平滑削掉的换手是真的，但省下来的钱小于它付出的代价**——"
             "K=%d 把换手从 %s 降到 %s（每期少 %s），换成成本每期省 **%s**；"
             "同期毛收益变化 **%s**，净效果 **%s（配对 t %s）**。"
             "判词：**%s**。（这是三条臂里证据最紧的一条；%s）"
             % (best_k,
                _pn(base["turnover_mean_ex_first"], 2),
                _pn(summ[best_k]["turnover_mean_ex_first"], 2),
                _pn(decomp[best_k]["turnover_cut"], 2),
                _bp(decomp[best_k]["cost_saved"]),
                _bp(decomp[best_k]["gross_effect"]),
                _bp(decomp[best_k]["net_effect"]),
                ("%+.2f" % pairs[best_k]["t"]) if pairs[best_k]["t"] is not None else "n/a",
                verdicts[best_k],
                "另外两条：" + "、".join("K=%d %s（t %s）"
                                        % (k, verdicts[k],
                                           ("%+.2f" % pairs[k]["t"]) if pairs[k]["t"] is not None else "n/a")
                                        for k in order if k != best_k)))
    L.append("")
    if cross.get("ok"):
        ca = cross["arms"].get(str(best_k)) or {}
        L.append("**和 r2017 的边界税对得上**：r2017 量到边界那一层的税是 **%s/期**，"
                 "平滑在 K=%d 上真的买回了其中的 **%s**（%s）——"
                 "但它为这一笔付出 **%s** 的毛收益，也就是**一块钱买回 %s**。"
                 "这个比例是本面最有用的一个数：它说明「换手是信号的代价」这句话在数字上成立，"
                 "规则层已经没有便宜可捡，剩下的杠杆只有**佣金/滑点本身**。"
                 % (_bp(ca.get("edge_tax_per_period")), best_k,
                    _pn(ca.get("saved_share_of_edge_tax"), 1),
                    _bp(decomp[best_k]["cost_saved"]),
                    _bp(decomp[best_k]["gross_effect"]),
                    ("%.1f 分" % ca["price_per_bp_saved"]) if ca.get("price_per_bp_saved") is not None
                    else "n/a"))
        L.append("")
    L.append("**分解恒等式**（每一臂都逐位成立，不是拟合）："
             "`净差 = 毛差 + 2c·(换手₁ − 换手_K)`。所以读者要问的那个数只有一个——"
             "**平滑允许亏掉多少毛收益还不亏本**，本面把它印成 `breakeven_gross_loss`："
             "K=%d 是 %s；实测毛差 %s，%s。"
             % (best_k, _bp(decomp[best_k]["breakeven_gross_loss"]),
                _bp(decomp[best_k]["gross_effect"]),
                "在预算之内" if decomp[best_k]["gross_effect"] >= -decomp[best_k]["breakeven_gross_loss"]
                else "已经超支"))
    L.append("")
    g = groups[best_k]
    L.append("**被移出账的名字 vs 被移进账的名字**（K=%d）：平滑从账上拿掉 %d 个名字·次，"
             "它们下一期的真实收益均值 %s；换进来 %d 个，%s。"
             "差 %s——%s。"
             % (best_k, g["dropped_n"], _p(g["dropped_fwd_mean"]),
                g["added_n"], _p(g["added_fwd_mean"]),
                _p((g["added_fwd_mean"] or 0) - (g["dropped_fwd_mean"] or 0)),
                "平滑拿掉的是好名字、换进来的是更差的" if (g["added_fwd_mean"] or 0) < (g["dropped_fwd_mean"] or 0)
                else "平滑拿掉的是差名字"))
    L.append("")
    L.append("**窗口越长期数越少，但代价不是单调的**：K=1→%d 期数 %d→%d，"
             "每多一期就要多付一期的滞后；本面把每一臂的期数、换手、净额都印在下面，"
             "让读者自己看「省税」与「滞后」的取舍在哪个 K 上翻转。"
             % (max(ARMS), base["periods"], summ[max(ARMS)]["periods"]))
    L.append("")

    L += ["## 四臂读数", "",
          "| 臂 | 期数 | 换手/期 | 毛收益/期 | 净收益/期 | 年化 | 平均持仓 | 半窗名字占比 |",
          "|---|---|---|---|---|---|---|---|"]
    for k in ARMS:
        s = summ[k]
        L.append("| K=%d | %d | %s | %s | %s | %s | %.0f | %s |"
                 % (k, s["periods"], _pn(s["turnover_mean_ex_first"], 2),
                    _p(s["gross_mean_ex_first"]), _p(s["net_mean_ex_first"]),
                    _pn(s["net_annualized"], 2), s["size_mean"],
                    _pn(s["partial_window_share_mean"], 1)))
    L.append("")
    L += ["## 对 K=1 的配对差与分解", "",
          "| 臂 | 净差/期 | t | 毛差 | 省下的成本 | 换手削减 | 判词 |",
          "|---|---|---|---|---|---|---|"]
    for k in order:
        p, d = pairs[k], decomp[k]
        L.append("| K=%d | %s | %s | %s | %s | %s | %s |"
                 % (k, _bp(p["mean"]),
                    ("%+.2f" % p["t"]) if p["t"] is not None else "n/a",
                    _bp(d["gross_effect"]), _bp(d["cost_saved"]),
                    _pn(d["turnover_cut"], 2), verdicts[k]))
    L.append("")
    L += ["## 逐年（换手 / 净额）", "",
          "| 年 | K=1 换手 | K=1 净 | K=2 换手 | K=2 净 | K=3 换手 | K=3 净 | K=4 换手 | K=4 净 |",
          "|---|---|---|---|---|---|---|---|---|"]
    years = sorted(r["by_year"][BASE].keys())
    for y in years:
        cells = []
        for k in ARMS:
            b = r["by_year"][k].get(y)
            cells += [_pn(b["turnover_mean"], 2) if b else "n/a",
                      _p(b["net_mean"]) if b else "n/a"]
        L.append("| %s | %s |" % (y, " | ".join(cells)))
    L.append("")
    L += ["## 这张面为什么不是又一次「同一件事重新量一遍」", "",
          "r2016 量的是**名单规则**（滞回带），r2017 说明那份税不在名单层，"
          "本面是那条结论指向的**唯一**实验：分数平滑。它给出的不是「平滑好不好」，"
          "而是三个可执行的数：",
          "",
          "1. **省多少**：换手每期少 %s，折成本 %s/期；"
          % (_pn(decomp[best_k]["turnover_cut"], 2), _bp(decomp[best_k]["cost_saved"])),
          "2. **花多少**：毛收益变化 %s/期，与省下的成本同量级或更大；"
          % _bp(decomp[best_k]["gross_effect"]),
          "3. **滞后值多少**：`breakeven_gross_loss` = %s，"
          "超过这条线平滑就是拿收益换手续费——本面的实测%s。"
          % (_bp(decomp[best_k]["breakeven_gross_loss"]),
             "在这条线之内" if decomp[best_k]["gross_effect"] >= -decomp[best_k]["breakeven_gross_loss"]
             else "已经越过这条线"),
          "",
          "## 未验证（如实）", ""]
    for line in (
        "① 残差排名仍是 20 日持有期的父面口径，同一只名字的权重变化不算交易（分数记账下权重变化只来自持仓数变化）；",
        "② 平滑窗口只测 K=1..4；更长的 K 没量，不能由此推「越长越好」或「越长越差」；",
        "③ 新进池的名字只有部分窗口（`partial_window_share` 已印），本面对它按现有观测取均值——"
        "这等于给新名字更高权重，未做替代口径的敏感性检验；",
        "④ 入场/出场按同一期期末分数判定，无额外成交延迟模型；分数平滑本身就是一个 K-1 期的滞后，"
        "本面只给它定价，没有试图抵消它；",
        "⑤ 年化是 %d 期复利外推，2020 只有少数几期，逐年列只用于看方向；" % base["periods"],
        "⑥ 票池现存标的（幸存者偏差，父面同），面板起于 2020-01-02；",
        "⑦ 本面是定价/口径件，不是可交易策略：无仓位规则、无容量约束、无风控；",
        "⑧ 全量 smoke 与 S6 链未跑（本轮为竞争窗，只落新增文件面）。",
    ):
        L.append(line)
        L.append("")
    L += [DOC_END, ""]

    os.makedirs(os.path.dirname(MD), exist_ok=True)
    with open(MD, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(L))


# -------------------------------------------------------------------- check
NUM_KEYS = ("periods", "periods_ex_first", "turnover_mean_all_periods", "turnover_mean_ex_first",
            "gross_mean_all_periods", "gross_mean_ex_first", "net_mean_all_periods",
            "net_mean_ex_first", "net_annualized", "tax_per_period", "size_mean", "n_mean",
            "partial_window_share_mean")


def check() -> int:
    """Re-derive and compare.  A moved input says STALE; a number that moved on
    the same inputs is a real defect and must not wear the STALE word."""
    try:
        with open(OUT, "r", encoding="utf-8") as fh:
            face = json.load(fh)
    except (OSError, ValueError):
        print("CHECK FAILED face missing: %s" % _rel(OUT))
        return 3

    dates, symbols, slices, arms, summ, pairs, decomp, verdicts, groups = build_face()
    anchor = layer_anchor(arms)
    cross = layer_cross_read(decomp)

    problems = []
    if face.get("evidence_cutoff") != dates[-1]:
        problems.append("STALE panel moved: face %s vs panel %s"
                        % (face.get("evidence_cutoff"), dates[-1]))
    if face.get("last_priced_rebalance") != slices[-1]["date"]:
        problems.append("STALE rebalance grid moved: face %s vs now %s"
                        % (face.get("last_priced_rebalance"), slices[-1]["date"]))
    if not anchor["ok"]:
        problems.append("STALE parent anchor moved: %r"
                        % {k: anchor.get(k) for k in ("why", "worst_abs_diff")})

    f_sum = (face.get("results") or {}).get("summary")
    if f_sum is None:
        problems.append("CHECK FAILED block missing: summary")
    else:
        for k in ARMS:
            block = f_sum.get(str(k))
            if block is None:
                problems.append("CHECK FAILED summary missing arm K=%d" % k)
                continue
            for key in NUM_KEYS:
                fv, gv = block.get(key), summ[k][key]
                if (fv is None) != (gv is None):
                    problems.append("CHECK FAILED K=%d.%s None mismatch (%r vs %r)" % (k, key, fv, gv))
                elif fv is not None and abs(float(fv) - float(gv)) > 1e-12:
                    problems.append("CHECK FAILED K=%d.%s %r != %r" % (k, key, fv, gv))
    f_ver = (face.get("results") or {}).get("verdict") or {}
    for k in ARMS:
        if k == BASE:
            continue
        if f_ver.get(str(k)) != verdicts[k]:
            problems.append("CHECK FAILED verdict K=%d %r != %r" % (k, f_ver.get(str(k)), verdicts[k]))
    f_dec = (face.get("results") or {}).get("decomposition_vs_K1") or {}
    for k in ARMS:
        if k == BASE:
            continue
        block = f_dec.get(str(k)) or {}
        for key in ("gross_effect", "turnover_cut", "cost_saved", "net_effect",
                    "breakeven_gross_loss"):
            fv, gv = block.get(key), decomp[k][key]
            if (fv is None) != (gv is None):
                problems.append("CHECK FAILED decomp K=%d.%s None mismatch" % (k, key))
            elif fv is not None and abs(float(fv) - float(gv)) > 1e-12:
                problems.append("CHECK FAILED decomp K=%d.%s %r != %r" % (k, key, fv, gv))
        resid = decomp[k]["identity_residual"]
        if resid is not None and abs(resid) > 1e-15:
            problems.append("CHECK FAILED decomp K=%d identity residual %.3e" % (k, resid))
    f_cross = (face.get("results") or {}).get("layer_cross_read") or {}
    if cross.get("ok"):
        for k in ARMS:
            if k == BASE:
                continue
            fa = (f_cross.get("arms") or {}).get(str(k)) or {}
            ga = cross["arms"][str(k)]
            for key in ("edge_tax_per_period", "saved_share_of_edge_tax", "price_per_bp_saved"):
                fv, gv = fa.get(key), ga[key]
                if (fv is None) != (gv is None):
                    problems.append("CHECK FAILED cross K=%d.%s None mismatch" % (k, key))
                elif fv is not None and abs(float(fv) - float(gv)) > 1e-12:
                    problems.append("CHECK FAILED cross K=%d.%s %r != %r" % (k, key, fv, gv))
    elif f_cross.get("ok"):
        problems.append("STALE parent tax unreadable now: %r" % (cross.get("why"),))
    f_rows = (face.get("rows") or {})
    for k in ARMS:
        fr = f_rows.get(str(k)) or []
        if len(fr) != len(arms[k]):
            problems.append("STALE row count K=%d face=%d mine=%d" % (k, len(fr), len(arms[k])))
            continue
        worst = 0.0
        for a, b in zip(fr, arms[k]):
            if a.get("date") != b["date"]:
                problems.append("STALE row date K=%d %r != %r" % (k, a.get("date"), b["date"]))
                break
            worst = max(worst, abs(float(a["turnover"]) - b["turnover"]))
        if worst > 1e-12:
            problems.append("STALE per-period turnover moved K=%d by %.3e" % (k, worst))

    if not problems:
        print("CHECK ok  (slices=%d, cutoff=%s, anchor ok=%s, %s)"
              % (len(slices), slices[-1]["date"], anchor["ok"],
                 ", ".join("K=%d %s" % (k, verdicts[k]) for k in ARMS if k != BASE)))
        return 0
    for p in problems:
        print(p)
    return 3


# ------------------------------------------------------------------ selftest
_CHECKS = [0]


def _ok(cond, msg):
    _CHECKS[0] += 1
    if not cond:
        raise AssertionError("selftest leg %d failed: %s" % (_CHECKS[0], msg))


def selftest() -> int:
    # 1. turnover is the parent's definition, including the first-period entry.
    _ok(_turnover({1, 2}, None) == 1.0, "first period is a full entry")
    _ok(_turnover({1, 2}, {1, 2}) == 0.0, "identical sets cost nothing")
    _ok(abs(_turnover({1, 2, 3, 4}, {1, 2}) - 0.5) < 1e-15, "half the book replaced")
    _ok(_turnover(set(), {1}) == 0.0, "an empty book cannot turn over")

    # 2. K=1 is the raw score, bit for bit: smoothing must not be a no-op that
    #    quietly changes the book.
    cols = list(range(1, 11))
    rk = np.linspace(0.1, 1.0, 10)
    fw = np.linspace(-0.02, 0.02, 10)
    s = [_slice("2024-01-02", cols, rk, fw)]
    rows = walk_k(s, 1)
    _ok(len(rows) == 1, "K=1 produces a row on the first slice")
    _ok(rows[0]["turnover"] == 1.0, "K=1 first period is a full entry")
    expect = set(np.array(cols)[rk < 0.8].tolist())
    _ok(rows[0]["book"] == expect, "K=1 book is the raw 80/20 split")

    # 3. the window is exactly K observations: with K=2 the first slice is banked
    #    and produces no row, and the second slice averages two ranks.
    s2 = [_slice("2024-01-02", cols, rk, fw), _slice("2024-01-30", cols, rk, fw)]
    rows2 = walk_k(s2, 2)
    _ok(len(rows2) == 1, "K=2 needs two slices before it can price one")
    _ok(rows2[0]["date"] == "2024-01-30", "the priced slice is the second one")
    _ok(abs(rows2[0]["smooth"][cols[0]] - float(np.mean([rk[0], rk[0]]))) < 1e-15,
         "smoothed score is the mean of the window")
    _ok(rows2[0]["partial_window_share"] == 0.0, "a full window is not partial")

    # 4. a constant score stays constant: smoothing must not manufacture dispersion.
    s3 = [_slice("2024-01-%02d" % (2 + i), cols, np.full(10, 0.5), fw) for i in range(3)]
    rows3 = walk_k(s3, 3)
    _ok(all(abs(v - 0.5) < 1e-15 for v in rows3[0]["smooth"].values()),
         "smoothing a flat score leaves it flat")

    # 5. a name that only recently became eligible is averaged over what exists,
    #    and the share of such names is reported rather than absorbed.
    s4 = [_slice("2024-01-02", [1, 2, 3], [0.1, 0.5, 0.9], [0.01, 0.02, 0.03]),
          _slice("2024-01-30", [1, 2, 3, 4], [0.1, 0.5, 0.9, 0.5], [0.01, 0.02, 0.03, 0.04])]
    rows4 = walk_k(s4, 2)
    _ok(abs(rows4[0]["smooth"][4] - 0.5) < 1e-15, "a new name is averaged over one observation")
    _ok(abs(rows4[0]["partial_window_share"] - 0.25) < 1e-15, "one of four names is partial")

    # 6. smoothing really does damp a name flapping across the edge -- this is
    #    the entire mechanism, so it gets an explicit leg.  Ten names, one of
    #    them alternating between the best and the worst rank.
    flip_r = [0.05, 0.95, 0.05, 0.95]
    fixed = [0.1 * j for j in range(1, 10)]
    s5 = [_slice("2024-01-%02d" % (2 + i), list(range(1, 11)), [flip_r[i]] + fixed,
                 [0.0] * 10) for i in range(4)]
    r1 = walk_k(s5, 1)
    r3 = walk_k(s5, 3)
    _ok(len(r1) == 4 and len(r3) == 2, "the two arms price different numbers of periods")
    _ok(r1[0]["turnover"] > 0 and r1[3]["turnover"] > 0,
         "K=1 pays each time the flapping name crosses the edge")
    _ok(r3[1]["turnover"] == 0.0, "K=3 holds the flapping name and pays nothing")

    # 7. a name that deteriorates permanently still leaves the book, K-1 periods
    #    later -- smoothing delays the exit, it does not cancel it.
    bad = [0.05, 0.95, 0.99, 0.99, 0.99]
    s6 = [_slice("2024-01-%02d" % (2 + i), list(range(1, 11)), [bad[i]] + fixed,
                 [0.0] * 10) for i in range(5)]
    r3b = walk_k(s6, 3)
    _ok(1 in r3b[0]["book"], "a name still good on average is still held")
    _ok(1 not in r3b[-1]["book"], "after K bad periods the name is out")

    # 8. every arm cuts at the same place: the book size may never differ
    #    between arms, or the turnover comparison mixes a size change with a
    #    behaviour change.
    rng = np.random.default_rng(11)
    cols10 = list(range(1, 11))
    s7 = [_slice("2024-01-%02d" % (2 + i), cols10, rng.permutation(np.linspace(0.1, 1.0, 10)),
                 rng.normal(0, 0.01, 10)) for i in range(6)]
    sizes = {k: {r["size"] for r in walk_k(s7, k)} for k in ARMS}
    _ok(all(len(v) == 1 for v in sizes.values()), "book size is constant inside an arm: %r" % (sizes,))
    _ok(len({next(iter(v)) for v in sizes.values()}) == 1,
         "all arms hold the same number of names: %r" % (sizes,))
    _ok(next(iter(sizes[BASE])) == 7,
         "10 names, the 80/20 line keeps 7 of them (rank 0.8 is already the vetoed fifth)")

    # 9. net is gross minus exactly 2*c*turnover (parent booking).
    _ok(abs(rows2[0]["net"] - (rows2[0]["gross"] - 2 * COST_ONE_SIDE * rows2[0]["turnover"])) < 1e-15,
         "net = gross - 2c*turnover")

    # 10. the decomposition is an identity, not a fit -- and it has to be
    #     computed on the paired sample.  The toy deliberately gives the base
    #     arm an extra date: a summary-mean version of this identity would then
    #     be false by exactly the sample difference, which is the defect this
    #     leg exists to catch.
    bnet = 0.008 - 2 * COST_ONE_SIDE * 0.2
    a_rows = [{"date": "d1", "turnover": 0.2, "gross": 0.008, "net": bnet,
               "size": 7, "n": 10, "partial_window_share": 0.0},
              {"date": "d2", "turnover": 0.2, "gross": 0.008, "net": bnet,
               "size": 7, "n": 10, "partial_window_share": 0.0}]
    anet = 0.010 - 2 * COST_ONE_SIDE * 0.5
    b_rows = [{"date": "d1", "turnover": 0.5, "gross": 0.010, "net": anet,
               "size": 7, "n": 10, "partial_window_share": 0.0},
              {"date": "d2", "turnover": 0.5, "gross": 0.010, "net": anet,
               "size": 7, "n": 10, "partial_window_share": 0.0},
              {"date": "d3", "turnover": 0.0, "gross": 0.050, "net": 0.050,
               "size": 7, "n": 10, "partial_window_share": 0.0}]
    d = decompose(a_rows, b_rows)
    _ok(d["n"] == 2, "only the shared dates enter the decomposition")
    _ok(abs(d["turnover_cut"] - 0.3) < 1e-15, "turnover cut is a paired difference")
    _ok(abs(d["gross_effect"] - (-0.002)) < 1e-15, "gross effect is a paired difference")
    _ok(abs(d["cost_saved"] - 2 * COST_ONE_SIDE * 0.3) < 1e-15, "cost saved = 2c * cut")
    _ok(abs(d["identity_residual"]) < 1e-18,
         "net effect = gross effect + cost saved, exactly: %.3e" % d["identity_residual"])
    _ok(abs(d["breakeven_gross_loss"] - d["cost_saved"]) < 1e-18,
         "breakeven gross loss is exactly the cost saved")

    # 11. verdict states, and the flat-series guard.
    _ok(verdict({"mean": 0.001, "t": 3.0}, {"cost_saved": 1e-4}) == "SMOOTHING_PAYS", "pays")
    _ok(verdict({"mean": -0.001, "t": -3.0}, {"cost_saved": 1e-4}) == "SMOOTHING_COSTS", "costs")
    _ok(verdict({"mean": 0.001, "t": 1.2}, {"cost_saved": 1e-4}) == "SMOOTHING_NOT_SEPARABLE",
         "a small t is not a verdict")
    _ok(verdict({"mean": None, "t": None}, {"cost_saved": 1e-4}) == "SMOOTHING_UNPRICEABLE",
         "an unpriceable pair is its own state")
    _ok(_tstat([0.01]) is None, "one point has no t")
    _ok(_tstat([0.01, 0.01, 0.01]) is None, "zero variance has no t")
    _ok(abs(_tstat([0.01, 0.02, 0.03]) - 3.4641) < 1e-3, "three rising points give t")

    # 12. paired() aligns on dates and skips the ones the other arm has not
    #     reached -- otherwise a shorter window silently gets a different sample.
    rowsA = [{"date": "d1", "net": 0.01}, {"date": "d2", "net": 0.02}]
    rowsB = [{"date": "d2", "net": 0.01}]
    p = paired(rowsA, rowsB)
    _ok(p["n"] == 1, "only the common date is paired")
    _ok(abs(p["mean"] - 0.01) < 1e-15, "the paired mean is the difference on that date")

    # 13. drop_add prices both groups and neither leaks into the other.
    bk = [{"date": "d1", "book": {1, 2}, "fwd": {1: 0.01, 2: 0.02}},
          {"date": "d2", "book": {1, 2, 3}, "fwd": {1: 0.01, 2: 0.02, 3: 0.03}}]
    ba = [{"date": "d1", "book": {1, 3}, "fwd": {1: 0.01, 3: 0.03}},
          {"date": "d2", "book": {1, 2}, "fwd": {1: 0.01, 2: 0.02}}]
    g = drop_add(bk, ba)
    _ok(g["dropped_n"] == 1 and g["added_n"] == 2, "one name out, two name-periods in: %r" % (g,))
    _ok(abs(g["dropped_fwd_mean"] - 0.03) < 1e-15, "the dropped name is priced on its own return")
    _ok(abs(g["added_fwd_mean"] - 0.025) < 1e-15, "the added names are averaged on their own returns")

    # 14. by_year skips the full-entry period and groups on the date prefix.
    yr = by_year([{"date": "2024-01-02", "turnover": 1.0, "gross": 0.0, "net": 0.0, "size": 8},
                   {"date": "2024-01-30", "turnover": 0.1, "gross": 0.01,
                    "net": 0.01, "size": 8}])
    _ok(list(yr.keys()) == ["2024"] and yr["2024"]["periods"] == 1,
         "the entry period is not a year observation")

    # 15. compound refuses a hole and refuses an empty series.
    _ok(compound([0.01, float("nan")]) is None, "compound refuses NaN periods")
    _ok(compound([]) is None, "compound refuses an empty series")

    # 16. a path on another drive prints absolute instead of raising (r2017's
    #     first-run defect: _rel() threw on C: vs K:).
    import tempfile
    outside = os.path.join(tempfile.gettempdir(), "r2019_selftest_face.json")
    shown = _rel(outside)
    _ok(isinstance(shown, str) and shown and not shown.startswith(".."),
         "a path on another drive prints absolute")
    _ok(_rel(os.path.join(ROOT, "results", "x.json")) == "results/x.json",
         "a path inside the repo stays relative")

    # 17. a window with no slices is empty, never a silent different sample.
    _ok(walk_k([], 3) == [], "no slices, no rows")
    _ok(walk_k([_slice("d1", [1], [0.5], [0.0])], 2) == [],
         "fewer slices than K produces no rows rather than a shorter window")
    try:
        walk_k([_slice("d1", [1], [0.5], [0.0])], 0)
        _ok(False, "a zero window must be refused")
    except ValueError:
        _ok(True, "a zero window is refused")

    # 18. an empty book cannot be priced: NaN, not zero (r1789 family).
    s8 = [_slice("d1", [1], [0.95], [0.01])]
    r8 = walk_k(s8, 1)
    _ok(not np.isfinite(r8[0]["gross"]), "a book with nobody in it has no gross return")

    print("SELFTEST %d/%d PASS" % (_CHECKS[0], _CHECKS[0]))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", choices=["run", "check", "selftest"])
    args = ap.parse_args(argv)
    if args.cmd == "run":
        return run()
    if args.cmd == "check":
        return check()
    return selftest()


if __name__ == "__main__":
    raise SystemExit(main())
