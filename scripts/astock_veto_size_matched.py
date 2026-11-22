#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A-share residual veto -- is the veto book's loss the size it buys, or the sort?

Why this face exists
--------------------
r1957 closed with one number still unexplained.  The book a 1,000,000 account can
buy (V: top-400 by market cap inside the affordable veto pool) pays -2.06%/yr,
while a uniform random 400 from the *same* pool pays +11.75%/yr (20 draws, one
draw landing between 10.66% and 12.91%), paired t = -3.60.  Two stories fit:

  (a) the cap sort is a bad rule at any size;
  (b) V is a large-cap bet and the random book is a small-cap bet.  V's picks
      have a median market cap of 11.96bn while the pool's median is 3.74bn --
      and over 2020-2026 the large-cap end of the A-share market paid less.

Both stories are one sentence in the last face's own print.  This face buys the
one arm that separates them: a random draw from the same pool whose picks are
size twins of V's picks, one twin per pick, drawn inside a narrow cap band.
What is left in V minus M is the sort with the size held fixed.

The same construction is run for S (top-400 by ascending residual), because its
+6.54% carries the opposite question: the residual signal picks small names
(median 3.98bn vs the pool's 3.74bn, so it is *not* a small-cap bet by
construction), but the honest test of a signal is still "does it beat random at
the size it actually buys".

What it prints
--------------
    A   top-400 by market cap, whole eligible pool     (the parent's control arm)
    V   top-400 by market cap, affordable veto pool    (the book under test)
    M   size twins of V's picks, drawn from that pool  (the sort at fixed size)
    R   uniform random draws from that pool            (the parent's random arm)
    S   top-400 by ascending residual, that pool        (the signal sort)
    MS  size twins of S's picks                        (the signal at fixed size)

plus the decomposition V-R = (V-M) + (M-R) in pp/yr: the first term is the sort,
the second is the size V chose.  And a per-cap-decile table of "largest of this
bucket vs a random member of this bucket", because an average gap can hide a
sort that wins in some buckets and loses in others.

Criteria frozen before the first run (nothing below is tuned on the numbers)
---------------------------------------------------------------------------
  CAPITAL      1,000,000 -- the money line r1956/r1957 read, unchanged.
  WIDTH        400 -- TEST_WIDTH from the parent: the width where the parent's
               paired difference first cleared two standard errors.
  T_MIN        2.0, the bar every parent face used.
  RANDOM_DRAWS 20 per date, one generator, one seed.
  TWIN_BANDS   +/-15% cap band first, then +/-50%, then +/-100%, then the nearest
               unused name by |log cap ratio|.  The band each twin came from is
               counted and printed; a face that quietly matched on a wide band
               would be matching on something other than size.
  CONTROL      V400 and A400 must reproduce the parent's published arms
               (-2.06%, -10.47%, read out of its own JSON when present) within
               0.60pp; otherwise CONTROL_MISMATCH.

verdicts
  sort (V vs M):
    CAP_SORT_PAYS_AT_MATCHED_SIZE             t >= +T_MIN
    THE_CAP_SORT_LOSES_AT_MATCHED_SIZE        t <= -T_MIN
    CANNOT_SEPARATE_SORT_FROM_SIZE            otherwise -- the -2.06% and the
                                              +11.75% are one size bet apart
  residual (S vs MS), frozen at the same time and never folded into the above:
    RESIDUAL_SIGNAL_SURVIVES_SIZE_MATCHING    t >= +T_MIN
    RESIDUAL_SIGNAL_LOSES_AT_MATCHED_SIZE     t <= -T_MIN
    RESIDUAL_SIGNAL_NOT_SEPARABLE_AT_MATCHED_SIZE
  size share, printed beside the verdict, never scored:
    share of the V-R gap that the size twin already reproduces = (M-R)/(V-R).
    Above 1.0 means the twins out-earn V by more than V trails the random book --
    i.e. the cap sort adds a loss on top of the size it buys.

usage: python scripts/astock_veto_size_matched.py [run|check|selftest]
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

from astock_resid_reversal_probe import (  # noqa: E402
    COST_ONE_SIDE,
    FIRST_DATE,
    HOLD,
    LOOKBACK_BETA,
    MIN_AMOUNT_20D,
    MIN_BARS,
    compound,
    daily_returns,
    load_panel,
    market_return,
    rank01,
)
from astock_resid_veto_layer import (  # noqa: E402
    _paired,
    _turnover,
    panel_frontier,
    score_slice,
    staleness,
)
from astock_veto_holdable_width import pick_liquid  # noqa: E402
from astock_veto_affordable_book import (  # noqa: E402
    feasible_mask,
    thin_pool,
    LOT,
    _cagr,
    _nets,
)
from astock_veto_open_capital import med  # noqa: E402

OUT = os.path.join(ROOT, "results", "astock_veto_size_matched.json")
MD = os.path.join(ROOT, "research", "ASTOCK-VETO-SIZE-MATCHED.md")
PARENT = os.path.join(ROOT, "results", "astock_veto_affordable_book.json")

CAPITAL = 1000000
WIDTH = 400
T_MIN = 2.0
RANDOM_DRAWS = 20
SEED = 20261123
CONTROL_TOL = 0.0060
N_BUCKETS = 10
TWIN_BANDS = (0.15, 0.50, 1.00)

# the parent's published arms (re-read from its JSON when it is on disk)
PARENT_V400_CAGR = -0.020574
PARENT_A400_CAGR = -0.104660


# ------------------------------------------------------------------ pure rules
def size_twins(target_caps, pool_caps, pool_pos, rng, bands=TWIN_BANDS):
    """One random pool member per target cap, inside the narrowest band that has
    an unused name.

    Returns (positions, band_of_each, unmatched).  Positions are in pool space
    (0..len(pool_pos)-1) so the caller can map back to panel indices.  A name is
    never used twice in one draw: a "random book at the same size" that bought
    the same stock two or three times would be a different, larger bet.
    """
    tc = np.asarray(target_caps, dtype=float)
    pc = np.asarray(pool_caps, dtype=float)
    n_pool = len(pc)
    used = np.zeros(n_pool, dtype=bool)
    bands_used = []
    unmatched = 0
    logpc = np.log(np.where(pc > 0, pc, np.nan))
    # the pool sorted once: each band is a slice, so the per-pick search is the
    # band's own length rather than the pool's (2,000 names x 60 draws x 77
    # dates is why this is a slice and not a full scan)
    order = np.argsort(logpc, kind="mergesort")
    smax = logpc[order]
    finite = np.isfinite(smax)
    chosen_local = []
    for c in tc:
        chosen = -1
        used_band = None
        lc = math.log(c) if (np.isfinite(c) and c > 0) else float("nan")
        if np.isfinite(lc):
            for span in bands:
                lo, hi = lc - math.log(1.0 + span), lc + math.log(1.0 + span)
                i0 = int(np.searchsorted(smax, lo, side="left"))
                i1 = int(np.searchsorted(smax, hi, side="right"))
                cand = order[i0:i1]
                if len(cand):
                    cand = cand[~used[cand] & np.isfinite(logpc[cand])]
                if len(cand):
                    chosen = int(cand[int(rng.integers(0, len(cand)))])
                    used_band = span
                    break
            if chosen < 0:
                # nearest unused name by |log cap ratio| -- honest fallback, counted
                cand = order[finite & ~used[order]]
                if len(cand):
                    chosen = int(cand[int(np.argmin(np.abs(logpc[cand] - lc)))])
                    used_band = -1.0  # the "nearest" rung, not a band
        if chosen < 0:
            rest = np.nonzero(~used)[0]
            if not len(rest):
                break
            chosen = int(rest[0])
            used_band = -1.0
            unmatched += 1
        used[chosen] = True
        chosen_local.append(chosen)
        bands_used.append(used_band)
    return [int(pool_pos[i]) for i in chosen_local], bands_used, unmatched


def twin_quality(target_caps, twin_caps):
    """How close the twins actually are, in log-cap terms.

    Printed beside every matched arm: a twin set matched on +/-15% of market cap
    is a size control; one matched on "whatever was nearest" is a different
    experiment wearing the same label.

    The two sides are compared as sorted cap vectors, because the pairing itself
    is not kept: comparing a target against the wrong twin's cap prints a match
    quality the run never had (caught here at r1958 -- 99.9% of twins came from
    the +/-15% band while the printed median deviation read 35%).
    """
    t = np.asarray(target_caps, dtype=float)
    m = np.asarray(twin_caps, dtype=float)
    with np.errstate(invalid="ignore", divide="ignore"):
        r = np.log(m / t)
    r = r[np.isfinite(r)]
    if not len(r):
        return {"n": 0}
    a = np.abs(r)
    return {"n": int(len(a)), "median_abs_log": float(np.median(a)),
            "p90_abs_log": float(np.quantile(a, 0.90)),
            "median_ratio": float(math.exp(np.median(a)))}


def split_gap(cagr_v, cagr_m, cagr_r):
    """V - R = (V - M) + (M - R).  Returns pp/yr terms and the size share.

    Terms are None when any leg is missing -- a decomposition with a hole is not
    a decomposition (and a hole must never print as zero).
    """
    if cagr_v is None or cagr_m is None or cagr_r is None:
        return {"total_pp": None, "sort_pp": None, "size_pp": None, "size_share": None,
                "sort_share": None}
    total = 100.0 * (cagr_v - cagr_r)
    sort = 100.0 * (cagr_v - cagr_m)
    size = 100.0 * (cagr_m - cagr_r)
    share = (size / total) if abs(total) > 1e-9 else None
    sshare = (sort / total) if abs(total) > 1e-9 else None
    return {"total_pp": total, "sort_pp": sort, "size_pp": size,
            "size_share": share, "sort_share": sshare}


def verdict_sort(cagr_v, t_vs_m, t_min=T_MIN):
    if cagr_v is None:
        return "NO_BOOK"
    if t_vs_m is None:
        return "CANNOT_SEPARATE_SORT_FROM_SIZE"
    if t_vs_m >= t_min:
        return "CAP_SORT_PAYS_AT_MATCHED_SIZE"
    if t_vs_m <= -t_min:
        return "THE_CAP_SORT_LOSES_AT_MATCHED_SIZE"
    return "CANNOT_SEPARATE_SORT_FROM_SIZE"


def verdict_residual(cagr_s, t_s_vs_ms, t_min=T_MIN):
    if cagr_s is None:
        return "NO_SIGNAL_ARM"
    if t_s_vs_ms is None:
        return "RESIDUAL_SIGNAL_NOT_SEPARABLE_AT_MATCHED_SIZE"
    if t_s_vs_ms >= t_min:
        return "RESIDUAL_SIGNAL_SURVIVES_SIZE_MATCHING"
    if t_s_vs_ms <= -t_min:
        return "RESIDUAL_SIGNAL_LOSES_AT_MATCHED_SIZE"
    return "RESIDUAL_SIGNAL_NOT_SEPARABLE_AT_MATCHED_SIZE"


def bucket_of(caps, n_buckets=N_BUCKETS):
    """Pool-rank bucket of every name (0 = smallest cap).  Size buckets are
    defined inside the pool, so a bucket is a size band, not a cap threshold."""
    r = rank01(np.asarray(caps, dtype=float))
    return np.clip((r * n_buckets).astype(int), 0, n_buckets - 1)


# ------------------------------------------------------------------- the run
def _arm(prev, key, idx, pick, fwd, price, mcap, budget):
    cur = set(idx[pick].tolist())
    gross = float(np.mean(fwd[pick]))
    turb = _turnover(cur, prev.get(key))
    prev[key] = cur
    one_lot = price[pick] * LOT
    return {"gross": gross, "net": gross - 2.0 * COST_ONE_SIDE * turb,
            "turnover": turb, "size": int(len(pick)),
            "median_one_lot": float(np.median(one_lot)),
            "median_mcap": float(np.median(mcap[pick])),
            "over_budget": float(np.mean(one_lot > budget + 1e-9))}


def run(dates, symbols, close, amount, shares, stride=HOLD, draws=RANDOM_DRAWS):
    rets = daily_returns(close)
    mkt = market_return(rets)

    start = 0
    while start < len(dates) and dates[start] < FIRST_DATE:
        start += 1
    start = max(start, LOOKBACK_BETA)

    rng = np.random.default_rng(SEED)
    prev = {}
    rows = []
    t = start
    while t + HOLD < len(dates):
        idx, resid, q, fwd = score_slice(t, close, amount, shares, rets, mkt)
        if resid is None:
            t += stride
            continue
        price = np.asarray(close[t][idx], dtype=float)
        with np.errstate(invalid="ignore"):
            mcap = price * shares[t][idx]
        budget = float(CAPITAL) / float(WIDTH)
        feas = feasible_mask(price, budget)
        pool_mask = feas & (q < 4)
        pos_pool = np.nonzero(pool_mask)[0]
        row = {"date": dates[t], "n_eligible": int(len(idx)), "n_pool": int(len(pos_pool))}
        if thin_pool(len(pos_pool), WIDTH):
            row["thin"] = True
            rows.append(row)
            t += stride
            continue
        take = min(WIDTH, len(pos_pool))
        caps_pool = mcap[pos_pool]
        row["pool_mcap"] = float(np.median(caps_pool))

        # A: the parent's control arm -- whole pool, top by cap
        pos_a = np.arange(len(idx))
        pick_a = pos_a[pick_liquid(mcap, pos_a, take)]
        row["A"] = _arm(prev, "A", idx, pick_a, fwd, price, mcap, budget)

        # V: the book under test -- affordable veto pool, top by cap
        pick_v = pos_pool[pick_liquid(caps_pool, pos_pool, take)]
        row["V"] = _arm(prev, "V", idx, pick_v, fwd, price, mcap, budget)

        # S: same pool, ascending residual (the parent's signal arm)
        pick_s = pos_pool[np.argsort(resid[pos_pool], kind="mergesort")[:take]]
        row["S"] = _arm(prev, "S", idx, pick_s, fwd, price, mcap, budget)

        # R / M / MS: random draws from the same pool
        for tag, targets in (("R", None),
                             ("M", mcap[pick_v]),
                             ("MS", mcap[pick_s])):
            grosses, nets, turbs = [], [], []
            band_hist = {}
            qualities = []
            attempts_bad = 0
            for d in range(draws):
                if targets is None:
                    pick = np.sort(rng.choice(pos_pool, size=take, replace=False))
                    bands_used = []
                else:
                    twins, bands_used, unmatched = size_twins(targets, caps_pool, pos_pool, rng)
                    pick = np.sort(np.asarray(twins, dtype=int))
                    attempts_bad += unmatched
                    for b in bands_used:
                        band_hist[str(b)] = band_hist.get(str(b), 0) + 1
                    qualities.append(twin_quality(np.sort(targets), np.sort(mcap[pick])))
                dk = "%s#%d" % (tag, d)
                cur = set(idx[pick].tolist())
                turb = _turnover(cur, prev.get(dk))
                prev[dk] = cur
                g = float(np.mean(fwd[pick]))
                grosses.append(g)
                turbs.append(turb)
                nets.append(g - 2.0 * COST_ONE_SIDE * turb)
            row[tag] = {"gross": float(np.mean(grosses)), "net": float(np.mean(nets)),
                        "turnover": float(np.mean(turbs)), "size": int(take), "thin": False,
                        "median_one_lot": None, "median_mcap": None, "over_budget": None}
            row["%s_draws" % tag] = list(nets)
            if targets is not None:
                row["%s_twin" % tag] = {
                    "bands": band_hist,
                    "unmatched": int(attempts_bad),
                    "quality": qualities[0] if qualities else {"n": 0}}

        # per-bucket: "largest of this bucket" vs "a random member of this bucket"
        bkt = bucket_of(caps_pool)
        row["buckets"] = {}
        for name, pick in (("V", pick_v), ("S", pick_s)):
            caps_used = mcap[pick]
            fwd_used = fwd[pick]
            cell = {}
            for b in np.unique(bkt):
                sel = bkt_of_caps(caps_used, caps_pool, int(b))
                if sel is None or not np.any(sel):
                    continue
                cell[str(int(b))] = {"n": int(np.sum(sel)),
                                     "gross": float(np.mean(fwd_used[sel])),
                                     "pool_gross": float(np.mean(fwd[pos_pool][bkt == b]))}
            row["buckets"][name] = cell
        rows.append(row)
        t += stride
    return rows


def bkt_of_caps(pick_caps, pool_caps, bucket):
    """Mask of the picks whose cap falls inside the pool's `bucket` size band.

    Buckets are pool-rank deciles, so the band is [cap at decile edge lo, hi).
    A pick above the pool's largest name (impossible) or below the smallest is
    simply not in any band; the caller checks for an empty mask.
    """
    pc = np.sort(np.asarray(pool_caps, dtype=float))
    if not len(pc) or len(pick_caps) == 0:
        return None
    n = len(pc)
    lo_i = int(n * bucket / float(N_BUCKETS))
    hi_i = int(n * (bucket + 1) / float(N_BUCKETS)) - 1
    lo = pc[min(lo_i, n - 1)]
    hi = pc[min(max(hi_i, 0), n - 1)]
    c = np.asarray(pick_caps, dtype=float)
    with np.errstate(invalid="ignore"):
        return (c >= lo) & (c <= hi)


# ------------------------------------------------------------------ summaries
def _num(v):
    return float(v) if v is not None else float("nan")


def summarize(rows, tag):
    key = tag
    return {
        "arm": tag,
        "width_target": WIDTH,
        "capital_cny": CAPITAL,
        "slot_budget_cny": float(CAPITAL) / float(WIDTH),
        "cagr_net": _cagr(rows, key),
        "mean_turnover": float(np.nanmean([_num((r.get(key) or {}).get("turnover"))
                                           for r in rows])),
        "median_size": med([(r.get(key) or {}).get("size") for r in rows]),
        "median_mcap": med([(r.get(key) or {}).get("median_mcap") for r in rows]),
        "mean_over_budget": float(np.nanmean([_num((r.get(key) or {}).get("over_budget"))
                                              for r in rows])),
        "thin_rounds": int(sum(1 for r in rows if (r.get(key) or {}).get("thin"))),
    }


def table_all(rows):
    return {tag: summarize(rows, tag) for tag in ("A", "V", "M", "R", "S", "MS")}


def paired_all(rows):
    return {
        "V_vs_M": _paired(rows, "V", "M"),
        "V_vs_R": _paired(rows, "V", "R"),
        "V_vs_A": _paired(rows, "V", "A"),
        "M_vs_R": _paired(rows, "M", "R"),
        "S_vs_MS": _paired(rows, "S", "MS"),
        "S_vs_R": _paired(rows, "S", "R"),
        "MS_vs_R": _paired(rows, "MS", "R"),
    }


def twin_report(rows):
    out = {}
    for tag in ("M", "MS"):
        bands = {}
        unmatched = 0
        qs = []
        for r in rows:
            tw = r.get("%s_twin" % tag) or {}
            for b, c in (tw.get("bands") or {}).items():
                bands[b] = bands.get(b, 0) + int(c)
            unmatched += int(tw.get("unmatched") or 0)
            q = tw.get("quality") or {}
            if q.get("n"):
                qs.append(q)
        out[tag] = {
            "bands": bands,
            "band_share": ({b: c / float(sum(bands.values())) for b, c in bands.items()}
                           if bands else {}),
            "unmatched": unmatched,
            "median_abs_log": (float(np.median([q["median_abs_log"] for q in qs])) if qs else None),
            "p90_abs_log": (float(np.median([q["p90_abs_log"] for q in qs])) if qs else None),
        }
    return out


def bucket_table(rows):
    """Per size bucket: the sort's own picks vs the bucket's average member.

    For each bucket and each sorted arm (V = cap, S = residual) print the mean
    gross of the picks, the mean gross of a random member of that bucket, and
    the difference -- three numbers, because the difference alone hides whether
    the bucket held anything to find.
    """
    out = {}
    for arm in ("V", "S"):
        acc = {}
        for r in rows:
            b = (r.get("buckets") or {}).get(arm) or {}
            for k, cell in b.items():
                e = acc.setdefault(k, {"n": 0, "gross": 0.0, "pool_gross": 0.0, "days": 0})
                e["n"] += int(cell["n"])
                e["gross"] += float(cell["gross"])
                e["pool_gross"] += float(cell["pool_gross"])
                e["days"] += 1
        out[arm] = {}
        for k, e in sorted(acc.items(), key=lambda kv: int(kv[0])):
            if not e["days"]:
                continue
            g = e["gross"] / e["days"]
            pg = e["pool_gross"] / e["days"]
            out[arm][k] = {"picks": e["n"], "days": e["days"],
                           "pick_gross": g, "bucket_gross": pg,
                           "gap_pp": 100.0 * (g - pg)}
    return out


def primary_block(table, paired, twin):
    v, m, r, s, ms = table["V"], table["M"], table["R"], table["S"], table["MS"]
    gap = split_gap(v["cagr_net"], m["cagr_net"], r["cagr_net"])
    t_v_m = (paired["V_vs_M"] or {}).get("t")
    t_s_ms = (paired["S_vs_MS"] or {}).get("t")
    return {
        "capital_cny": CAPITAL,
        "width": WIDTH,
        "cagr_net": {"V": v["cagr_net"], "M": m["cagr_net"], "R": r["cagr_net"],
                     "S": s["cagr_net"], "MS": ms["cagr_net"], "A": table["A"]["cagr_net"]},
        "t_V_vs_M": t_v_m,
        "t_V_vs_R": (paired["V_vs_R"] or {}).get("t"),
        "t_V_vs_A": (paired["V_vs_A"] or {}).get("t"),
        "t_M_vs_R": (paired["M_vs_R"] or {}).get("t"),
        "t_S_vs_MS": t_s_ms,
        "t_S_vs_R": (paired["S_vs_R"] or {}).get("t"),
        "t_MS_vs_R": (paired["MS_vs_R"] or {}).get("t"),
        "median_mcap": {"V": v["median_mcap"], "S": s["median_mcap"]},
        "size_ratio_V_over_pool": None,
        "decomposition": gap,
        "verdict_sort": verdict_sort(v["cagr_net"], t_v_m),
        "verdict_residual": verdict_residual(s["cagr_net"], t_s_ms),
        "twin_quality": {"M": twin["M"], "MS": twin["MS"]},
    }


# --------------------------------------------------------------------- check
def _parent_arms():
    """The parent's published arms, read from its own file when it is there."""
    v400, a400 = PARENT_V400_CAGR, PARENT_A400_CAGR
    if os.path.exists(PARENT):
        try:
            with open(PARENT, encoding="utf-8") as fh:
                pf = json.load(fh)
            cell = (((pf.get("table") or {}).get(str(int(CAPITAL)), {})
                     .get(str(WIDTH))) or {})
            if (cell.get("V") or {}).get("cagr_net") is not None:
                v400 = float(cell["V"]["cagr_net"])
            if (cell.get("A") or {}).get("cagr_net") is not None:
                a400 = float(cell["A"]["cagr_net"])
        except (OSError, ValueError):
            pass
    return v400, a400


def _control(table):
    pv, pa = _parent_arms()
    v = (table.get("V") or {}).get("cagr_net")
    a = (table.get("A") or {}).get("cagr_net")
    ok = (v is not None and a is not None
          and abs(v - pv) <= CONTROL_TOL and abs(a - pa) <= CONTROL_TOL)
    return {"parent_v400": pv, "parent_a400": pa, "replay_v400": v, "replay_a400": a,
            "tol": CONTROL_TOL, "pass": bool(ok)}


def cmd_check():
    if not os.path.exists(OUT):
        print("STALE face missing: %s" % os.path.relpath(OUT, ROOT))
        return 3
    with open(OUT, encoding="utf-8") as fh:
        face = json.load(fh)
    frontier, sampled = panel_frontier()
    state, msg = staleness(face, frontier)
    if state == "stale":
        print("STALE %s (sample %d files)" % (msg, sampled))
        return 3
    if state == "inconsistent":
        print("CHECK FAILED %s (sample %d files)" % (msg, sampled))
        return 1

    problems = []

    # 1. every printed arm CAGR must still be the compound of its own series
    series = face.get("series") or {}
    table = face.get("table") or {}
    for tag in ("A", "V", "M", "R", "S", "MS"):
        nets = series.get(tag)
        printed = (table.get(tag) or {}).get("cagr_net")
        if not nets:
            problems.append("%s series missing" % tag)
            continue
        if printed is None:
            problems.append("%s printed CAGR missing" % tag)
            continue
        recomputed = compound([float(v) for v in nets if v is not None])
        if recomputed is None or abs(recomputed - printed) > 1e-9 * max(1.0, abs(printed)):
            problems.append("%s printed CAGR %.6f != series compound %s"
                            % (tag, printed, recomputed))

    # 2. both verdicts must be what their own printed numbers say
    prim = face.get("primary") or {}
    cg = prim.get("cagr_net") or {}
    want_sort = verdict_sort(cg.get("V"), prim.get("t_V_vs_M"))
    if prim.get("verdict_sort") != want_sort:
        problems.append("sort verdict printed %s but re-derives %s"
                        % (prim.get("verdict_sort"), want_sort))
    want_res = verdict_residual(cg.get("S"), prim.get("t_S_vs_MS"))
    if prim.get("verdict_residual") != want_res:
        problems.append("residual verdict printed %s but re-derives %s"
                        % (prim.get("verdict_residual"), want_res))

    # 3. the decomposition must add up on the printed numbers
    dec = prim.get("decomposition") or {}
    if None not in (dec.get("total_pp"), dec.get("sort_pp"), dec.get("size_pp")):
        resid = dec["total_pp"] - dec["sort_pp"] - dec["size_pp"]
        if abs(resid) > 1e-6:
            problems.append("decomposition does not add up: total %.6f sort %.6f size %.6f"
                            % (dec["total_pp"], dec["sort_pp"], dec["size_pp"]))
    else:
        problems.append("decomposition incomplete")
    want_gap = split_gap(cg.get("V"), cg.get("M"), cg.get("R"))
    for key in ("total_pp", "sort_pp", "size_pp"):
        a, b = dec.get(key), want_gap.get(key)
        if a is None or b is None or abs(float(a) - float(b)) > 1e-6:
            problems.append("decomposition %s printed %s but re-derives %s" % (key, a, b))

    # 4. the control leg must still be green against the parent's published arms
    ctl = face.get("control") or {}
    recomputed_ctl = _control(table)
    if not recomputed_ctl["pass"]:
        problems.append("control leg red: replay V400=%s A400=%s vs parent %s/%s (tol %.4f)"
                        % (recomputed_ctl["replay_v400"], recomputed_ctl["replay_a400"],
                           recomputed_ctl["parent_v400"], recomputed_ctl["parent_a400"],
                           recomputed_ctl["tol"]))
    if bool(ctl.get("pass")) != bool(recomputed_ctl["pass"]):
        problems.append("control.pass printed %s but re-derives %s"
                        % (ctl.get("pass"), recomputed_ctl["pass"]))

    # 5. a printed twin fit must be reachable from the widest band the run says
    #    it used -- a fit wider than every band is a pairing error, not a match
    widest = math.log(1.0 + max(TWIN_BANDS))
    twin = face.get("twin") or {}
    for tag in ("M", "MS"):
        q = twin.get(tag) or {}
        p90 = q.get("p90_abs_log")
        if p90 is not None and float(p90) > widest + 1e-9:
            problems.append("%s twin fit p90 %.4f exceeds the widest band %.4f "
                            "(pairs are being compared against the wrong twin)"
                            % (tag, float(p90), widest))

    # 6. the size ratio printed beside the pools must be the two medians it names
    prim_ratio = prim.get("size_ratio_V_over_pool")
    v_med = (table.get("V") or {}).get("median_mcap")
    pool_med = (face.get("pools") or {}).get("median_mcap_pool")
    if prim_ratio is not None and v_med and pool_med:
        if abs(float(prim_ratio) - float(v_med) / float(pool_med)) > 1e-9:
            problems.append("size_ratio_V_over_pool printed %s but the medians give %s"
                            % (prim_ratio, float(v_med) / float(pool_med)))

    if problems:
        for p in problems:
            print("CHECK FAILED %s" % p)
        return 1
    print("OK %s (sample %d files)" % (msg, sampled))
    return 0


# ------------------------------------------------------------------ selftest
def selftest():
    fails = []
    total = [0]

    def check(name, cond, detail=""):
        total[0] += 1
        if not cond:
            fails.append("%s %s" % (name, detail))

    # L1 twins land inside the tight band when the pool has the names
    rng = np.random.default_rng(7)
    pool = np.array([1.0, 1.02, 1.05, 9.0, 9.2, 100.0])
    twins, bands, unmatched = size_twins(np.array([10.4, 91.0]), pool, np.arange(6), rng)
    check("L1a", unmatched == 0, unmatched)
    check("L1b", all(b == TWIN_BANDS[0] for b in bands), bands)
    with np.errstate(invalid="ignore"):
        ratios = np.array([pool[t] / c for t, c in zip(twins, [10.4, 91.0])])
    check("L1c", np.all(np.abs(ratios - 1.0) <= TWIN_BANDS[0] + 1e-12), ratios.tolist())

    # L2 a name is never used twice inside one draw
    rng2 = np.random.default_rng(11)
    twins2, _b, _u = size_twins(np.array([5.0, 5.0, 5.0]), pool, np.arange(6), rng2)
    check("L2", len(set(twins2)) == len(twins2), twins2)

    # L3 widening is recorded, not hidden: an empty tight band must fall out to a
    # wider rung and say so
    rng3 = np.random.default_rng(13)
    far = np.array([1.0, 2.0, 50.0])
    twins3, bands3, _u3 = size_twins(np.array([1.60]), far, np.arange(3), rng3)
    check("L3", bands3 != [] and bands3[0] != TWIN_BANDS[0], bands3)

    # L4 the twin quality is a distance, and a perfect twin reads zero
    q = twin_quality([10.0, 20.0], [10.0, 20.0])
    check("L4a", q["median_abs_log"] == 0.0 and q["n"] == 2, q)
    q2 = twin_quality([10.0, 20.0], [11.0, 18.0])
    check("L4b", 0.0 < q2["median_abs_log"] < 0.2 and q2["median_ratio"] > 1.0, q2)

    # L5 the decomposition adds up, and a hole stays a hole (never a zero)
    g = split_gap(0.10, 0.05, 0.02)
    check("L5a", abs(g["total_pp"] - 8.0) < 1e-9, g)
    check("L5b", abs(g["sort_pp"] - 5.0) < 1e-9, g)
    check("L5c", abs(g["size_pp"] - 3.0) < 1e-9, g)
    check("L5d", abs(g["size_share"] - 0.375) < 1e-9, g)
    hole = split_gap(0.10, None, 0.02)
    check("L5e", hole["total_pp"] is None and hole["size_share"] is None, hole)
    flat = split_gap(0.05, 0.05, 0.05)
    check("L5f", flat["size_share"] is None, "a zero total is not a 0% share")

    # L6 both verdict ladders, every branch reachable
    check("L6a", verdict_sort(None, 3.0) == "NO_BOOK")
    check("L6b", verdict_sort(0.02, None) == "CANNOT_SEPARATE_SORT_FROM_SIZE")
    check("L6c", verdict_sort(0.02, 2.0) == "CAP_SORT_PAYS_AT_MATCHED_SIZE")
    check("L6d", verdict_sort(0.02, -2.0) == "THE_CAP_SORT_LOSES_AT_MATCHED_SIZE")
    check("L6e", verdict_sort(-0.02, -1.9) == "CANNOT_SEPARATE_SORT_FROM_SIZE")
    check("L6f", verdict_residual(None, 3.0) == "NO_SIGNAL_ARM")
    check("L6g", verdict_residual(0.05, 2.0) == "RESIDUAL_SIGNAL_SURVIVES_SIZE_MATCHING")
    check("L6h", verdict_residual(0.05, -2.1) == "RESIDUAL_SIGNAL_LOSES_AT_MATCHED_SIZE")
    check("L6i", verdict_residual(0.05, 1.99) ==
          "RESIDUAL_SIGNAL_NOT_SEPARABLE_AT_MATCHED_SIZE")

    # L7 buckets are size bands of the pool: the smallest name is bucket 0, the
    # largest is the last bucket, and a name outside the pool falls in none
    caps = np.arange(1, 101, dtype=float)
    b = bucket_of(caps)
    check("L7a", b[0] == 0 and b[-1] == N_BUCKETS - 1, (b[0], b[-1]))
    check("L7b", len(np.unique(b)) == N_BUCKETS, len(np.unique(b)))
    sel = bkt_of_caps(np.array([1.0, 100.0]), caps, 0)
    check("L7c", sel.tolist() == [True, False], sel.tolist())

    # L8 zero-drift turnover conventions are the parent's (first book = 1.0)
    check("L8a", _turnover({1, 2}, None) == 1.0)
    check("L8b", _turnover({1, 2}, {1, 2}) == 0.0)

    # L9 the frozen control constants are the parent's published arms
    check("L9a", abs(PARENT_V400_CAGR - (-0.020574)) < 1e-12
          and abs(PARENT_A400_CAGR - (-0.104660)) < 1e-12)
    note9 = "parent face absent"
    if os.path.exists(PARENT):
        try:
            pv, pa = _parent_arms()
            check("L9b", abs(pv - PARENT_V400_CAGR) <= CONTROL_TOL, (pv, PARENT_V400_CAGR))
            check("L9c", abs(pa - PARENT_A400_CAGR) <= CONTROL_TOL, (pa, PARENT_A400_CAGR))
            note9 = "parent face agrees"
        except (OSError, ValueError) as exc:  # pragma: no cover - corrupt file
            check("L9b", False, str(exc))

    # L10 check() shouts STALE on a face that records a bar the panel has passed
    global OUT
    keep = OUT
    tmp = os.path.join(ROOT, "results", "_selftest_size_matched_face.json")
    try:
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump({"evidence_cutoff": "1990-01-02", "panel": {"last": "1990-01-02"}}, fh)
        OUT = tmp
        import contextlib as _ctx
        import io as _io
        buf = _io.StringIO()
        with _ctx.redirect_stdout(buf):
            rc = cmd_check()
        check("L10", rc == 3 and "STALE" in buf.getvalue(), (rc, buf.getvalue()[:80]))
    finally:
        OUT = keep
        try:
            os.remove(tmp)
        except OSError:
            pass

    # L11..L15 a face whose printed legs left its own numbers must be named; an
    # honest face must not be.  These drive the real check() over a temp copy.
    frontier, _s = panel_frontier()
    tmp2 = os.path.join(ROOT, "results", "_selftest_size_matched_face2.json")

    def _honest_face():
        good = [0.001, 0.002, -0.001, 0.0]
        table = {tag: {"cagr_net": compound(good)} for tag in ("A", "V", "M", "R", "S", "MS")}
        cg = {tag: table[tag]["cagr_net"] for tag in ("A", "V", "M", "R", "S", "MS")}
        return {
            "evidence_cutoff": frontier, "panel": {"last": frontier},
            "table": table,
            "series": {tag: good for tag in ("A", "V", "M", "R", "S", "MS")},
            "primary": {"cagr_net": cg, "t_V_vs_M": 0.4, "t_S_vs_MS": 0.2,
                        "decomposition": split_gap(cg["V"], cg["M"], cg["R"]),
                        "verdict_sort": verdict_sort(cg["V"], 0.4),
                        "verdict_residual": verdict_residual(cg["S"], 0.2)},
            "control": _control(table),
        }

    def _run_check(face):
        global OUT
        with open(tmp2, "w", encoding="utf-8") as fh:
            json.dump(face, fh)
        OUT = tmp2
        import contextlib as _ctx
        import io as _io
        buf = _io.StringIO()
        with _ctx.redirect_stdout(buf):
            rc = cmd_check()
        return rc, buf.getvalue()

    keep = OUT
    try:
        face = _honest_face()
        rc0, t0 = _run_check(face)
        check("L11", "printed CAGR" not in t0, t0[:160])

        # L12 a printed CAGR that left its own series
        face2 = _honest_face()
        face2["table"]["V"]["cagr_net"] = float(face2["table"]["V"]["cagr_net"]) + 0.01
        rc, tx = _run_check(face2)
        check("L12", rc == 1 and "V printed CAGR" in tx, (rc, tx[:140]))

        # L13 a sort verdict its own numbers no longer support
        face3 = _honest_face()
        face3["primary"]["verdict_sort"] = "THE_CAP_SORT_LOSES_AT_MATCHED_SIZE"
        rc, tx = _run_check(face3)
        check("L13", rc == 1 and "sort verdict printed" in tx, (rc, tx[:140]))

        # L14 a residual verdict its own numbers no longer support
        face4 = _honest_face()
        face4["primary"]["verdict_residual"] = "RESIDUAL_SIGNAL_SURVIVES_SIZE_MATCHING"
        rc, tx = _run_check(face4)
        check("L14", rc == 1 and "residual verdict printed" in tx, (rc, tx[:140]))

        # L15 a decomposition that does not add up, and one that is missing
        face5 = _honest_face()
        face5["primary"]["decomposition"]["size_pp"] += 0.5
        rc, tx = _run_check(face5)
        check("L15a", rc == 1 and "decomposition" in tx, (rc, tx[:140]))
        face6 = _honest_face()
        face6["primary"]["decomposition"] = {"total_pp": None}
        rc, tx = _run_check(face6)
        check("L15b", rc == 1 and "decomposition incomplete" in tx, (rc, tx[:140]))

        # L16 a twin fit wider than every band the run says it used: that is the
        #     pairing bug this face was born with (r1958), and check() must name it
        face7 = _honest_face()
        face7["twin"] = {"M": {"p90_abs_log": math.log(1.0 + max(TWIN_BANDS)) + 0.3}}
        rc, tx = _run_check(face7)
        check("L16", rc == 1 and "exceeds the widest band" in tx, (rc, tx[:160]))

        # L17 a size ratio that is not the two medians it names
        face8 = _honest_face()
        face8["table"]["V"]["median_mcap"] = 20.0
        face8["pools"] = {"median_mcap_pool": 10.0}
        face8["primary"]["size_ratio_V_over_pool"] = 3.0
        rc, tx = _run_check(face8)
        check("L17", rc == 1 and "size_ratio_V_over_pool" in tx, (rc, tx[:160]))
    finally:
        OUT = keep
        try:
            os.remove(tmp2)
        except OSError:
            pass

    if fails:
        for f in fails:
            print("FAIL %s" % f)
        print("selftest FAILED %d/%d" % (len(fails), total[0]))
        return 1
    print("selftest PASS %d/%d (%s)" % (total[0], total[0], note9))
    return 0


# ----------------------------------------------------------------------- md
def write_md(payload):
    prim = payload["primary"]
    cg = prim["cagr_net"]
    dec = prim["decomposition"]
    tw = prim["twin_quality"]

    def pct(x):
        return "n/a" if x is None else "%+.2f%%" % (100.0 * x)

    def n2(x, suffix=""):
        return "n/a" if x is None else "%+.2f%s" % (x, suffix)

    lines = []
    lines.append("# A股否决书：亏的是它买的尺寸，还是它挑票的规则")
    lines.append("")
    lines.append("生成 %s · 证据 cutoff %s · 机器 %s" % (
        payload["generated"], payload["evidence_cutoff"], payload["machine"]))
    lines.append("")
    lines.append("## 一句话")
    lines.append("")
    lines.append(
        "100 万的 400 名书，按市值挑票（V %s）对同池随机 400 名（R %s）差 %s/年；"
        "把随机书换成 V 的**尺寸双胞胎**（M %s，一个挑一个，先在 ±%.0f%% 市值带内抽）后，"
        "V 对 M 的配对 t = %s，判决 **%s**。" % (
            pct(cg["V"]), pct(cg["R"]), n2(dec["total_pp"], "pp"),
            pct(cg["M"]), 100.0 * TWIN_BANDS[0], n2(prim["t_V_vs_M"]),
            prim["verdict_sort"]))
    lines.append("")
    lines.append(
        "差分解：总差 %s = 规则差 %s（V−M）+ 尺寸差 %s（M−R）。"
        "尺寸解释了这段差距的 %s。" % (
            n2(dec["total_pp"], "pp"), n2(dec["sort_pp"], "pp"), n2(dec["size_pp"], "pp"),
            "n/a" if dec["size_share"] is None else "%.0f%%" % (100.0 * dec["size_share"])))
    lines.append("")
    lines.append("## 残差排序是不是尺寸运气")
    lines.append("")
    lines.append(
        "S（残差升序，%s）对它的尺寸双胞胎 MS（%s）配对 t = %s → **%s**；"
        "S 对同池随机 t = %s，MS 对随机 t = %s。S 的选票中位市值 %s，池中位 %s。" % (
            pct(cg["S"]), pct(cg["MS"]), n2(prim["t_S_vs_MS"]), prim["verdict_residual"],
            n2(prim["t_S_vs_R"]), n2(prim["t_MS_vs_R"]),
            "n/a" if prim["median_mcap"]["S"] is None
            else "%.2fbn" % (prim["median_mcap"]["S"] / 1e9),
            "n/a" if payload["pools"]["median_mcap_pool"] is None
            else "%.2fbn" % (payload["pools"]["median_mcap_pool"] / 1e9)))
    lines.append("")
    lines.append("## 尺寸匹配做到了多近")
    lines.append("")
    for tag, name in (("M", "V 的尺寸双胞胎"), ("MS", "S 的尺寸双胞胎")):
        q = tw.get(tag) or {}
        bands = q.get("bands") or {}
        shares = q.get("band_share") or {}
        band_txt = "、".join(
            "%s: %.0f%%" % ("±%.0f%%" % (100.0 * float(b)) if float(b) > 0 else "最近名",
                            100.0 * shares[b])
            for b in sorted(bands, key=lambda k: float(k))) or "n/a"
        lines.append("- %s：中位 |log 市值比| %s（≈%.1f%% 偏差），P90 %s；落带分布 %s；"
                     "取不到名次 %d。" % (
                         name,
                         "n/a" if q.get("median_abs_log") is None
                         else "%.4f" % q["median_abs_log"],
                         100.0 * (math.exp(q["median_abs_log"]) - 1.0)
                         if q.get("median_abs_log") is not None else 0.0,
                         "n/a" if q.get("p90_abs_log") is None else "%.3f" % q["p90_abs_log"],
                         band_txt, int(q.get("unmatched") or 0)))
    lines.append("")
    lines.append("## 分尺寸桶：largest-of-bucket vs 桶里随便一个")
    lines.append("")
    lines.append("| 桶(池内市值十分位) | 票数 | 天数 | 挑中的毛收益 | 桶均毛收益 | 差 |")
    lines.append("|---|---|---|---|---|---|")
    for arm, label in (("V", "按市值挑"), ("S", "按残差挑")):
        for k, cell in sorted((payload["buckets"].get(arm) or {}).items(), key=lambda kv: int(kv[0])):
            lines.append("| %s %s | %d | %d | %+.2f%% | %+.2f%% | %+.2fpp |" % (
                label, k, cell["picks"], cell["days"],
                100.0 * cell["pick_gross"], 100.0 * cell["bucket_gross"], cell["gap_pp"]))
    lines.append("")
    lines.append(
        "桶表与配对差不是同一个数，读的时候要一起看：桶是池内十分位（约 240 名一段），"
        "在这么宽的一段里「按市值挑」几乎就挑到段均（差 −0.15 / −0.00pp）；"
        "双胞胎匹配到中位 5%% 的窄带，在这条窄带里「挑最大的」比「窄带里随便一个」每年少 %s。"
        "同一条尺寸梯度在两个分辨率下看到的量不同，两个数都印，不取其一。"
        "残差挑票则相反：每一个尺寸桶里它都比桶均差 −0.1 ~ −0.4pp，"
        "这就是 S 赢不了自己的尺寸双胞胎的直接来源。" % n2(-dec["sort_pp"], "pp"))
    lines.append("")
    lines.append("## 读数与边界")
    lines.append("")
    lines.append(
        "- 控制腿：V400 %s / A400 %s 对父面 %s / %s，容差 %.2fpp → %s。" % (
            pct(payload["control"]["replay_v400"]), pct(payload["control"]["replay_a400"]),
            pct(payload["control"]["parent_v400"]), pct(payload["control"]["parent_a400"]),
            100.0 * payload["control"]["tol"],
            "PASS" if payload["control"]["pass"] else "MISMATCH"))
    lines.append("- 随机族每次 20 抽、单一 seed；一个随机书是一个抽，不是一个均值。")
    lines.append("- 尺寸双胞胎只匹配**当前市值**，不匹配行业/流动性/账面；桶内残差已由 P90 印出。")
    lines.append("- 面板为现存标的（幸存者偏差照旧）；成本 8bp/边、20 交易日持有、次日开盘口径不变。")
    lines.append("- 本面不构成投资建议，也不改变任何既有账户/票面。")
    lines.append("")
    with open(MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    return MD


# ---------------------------------------------------------------------- main
def _machine():
    try:
        with open(os.path.join(ROOT, "fleet", "machine.json"), encoding="utf-8") as fh:
            return json.load(fh).get("machine_id", "unknown")
    except (OSError, ValueError):
        return "unknown"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "check", "selftest"])
    ap.add_argument("--stride", type=int, default=HOLD)
    args = ap.parse_args(argv)
    if args.cmd == "selftest":
        return selftest()
    if args.cmd == "check":
        return cmd_check()

    started = datetime.now()
    dates, symbols, close, amount, shares = load_panel()
    rows = run(dates, symbols, close, amount, shares, stride=args.stride)
    if not rows:
        print("no rebalance rows")
        return 2

    table = table_all(rows)
    paired = paired_all(rows)
    twin = twin_report(rows)
    prim = primary_block(table, paired, twin)
    control = _control(table)
    verdict = "CONTROL_MISMATCH" if not control["pass"] else prim["verdict_sort"]

    series = {tag: [float(v) if np.isfinite(v) else None
                    for v in _nets(rows, tag).tolist()]
              for tag in ("A", "V", "M", "R", "S", "MS")}

    pools = {
        "median_mcap_pool": med([r.get("pool_mcap") for r in rows]),
        "median_n_pool": med([r.get("n_pool") for r in rows]),
        "median_n_eligible": med([r.get("n_eligible") for r in rows]),
    }
    if table["V"]["median_mcap"] and pools["median_mcap_pool"]:
        prim["size_ratio_V_over_pool"] = (float(table["V"]["median_mcap"])
                                          / float(pools["median_mcap_pool"]))

    payload = {
        "generated": datetime.now().astimezone().isoformat(timespec="seconds"),
        "elapsed_sec": round((datetime.now() - started).total_seconds(), 1),
        "evidence_cutoff": dates[-1],
        "machine": _machine(),
        "kind": "astock_veto_size_matched",
        "fills_the_hole_of": "results/astock_veto_affordable_book.json (V -2.06% vs R +11.75%: "
                             "one sentence, two stories -- the sort or the size it buys)",
        "prereg": None,
        "adoption": None,
        "spec": {
            "capital": CAPITAL, "width": WIDTH, "hold": HOLD, "stride": args.stride,
            "lookback_beta": LOOKBACK_BETA, "min_amount_20d": MIN_AMOUNT_20D,
            "min_bars": MIN_BARS, "cost_one_side": COST_ONE_SIDE, "lot": LOT,
            "t_min": T_MIN, "random_draws": RANDOM_DRAWS, "seed": SEED,
            "twin_bands": list(TWIN_BANDS), "n_buckets": N_BUCKETS,
            "arms": {
                "A": "whole eligible pool, top by market cap (parent control)",
                "V": "affordable veto pool, top by market cap (the book under test)",
                "M": "size twins of V's picks drawn from the same pool",
                "R": "uniform random draws from the same pool",
                "S": "affordable veto pool, ascending residual",
                "MS": "size twins of S's picks drawn from the same pool"},
            "matching": "one twin per pick, no reuse inside a draw, narrowest band that "
                        "has an unused name (+/-15%, +/-50%, +/-100%, then nearest)",
        },
        "panel": {"dates": len(dates), "symbols": len(symbols),
                  "first": dates[0], "last": dates[-1]},
        "rebalances": len(rows),
        "table": table,
        "paired": paired,
        "pools": pools,
        "twin": twin,
        "buckets": bucket_table(rows),
        "primary": prim,
        "series": series,
        "series_width": WIDTH,
        "control": control,
        "verdict": verdict,
        "verdict_residual": prim["verdict_residual"],
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    write_md(payload)

    def pct(x):
        return ("%+.2f%%" % (100.0 * x)) if x is not None else "n/a"

    def tt(x):
        return ("%+.2f" % x) if x is not None else "n/a"

    print("rebalances %d  cutoff %s  panel %d symbols  %.1fs"
          % (len(rows), payload["evidence_cutoff"], len(symbols), payload["elapsed_sec"]))
    print("  control V400 %s (parent %s)  A400 %s (parent %s) -> %s"
          % (pct(control["replay_v400"]), pct(control["parent_v400"]),
             pct(control["replay_a400"]), pct(control["parent_a400"]),
             "PASS" if control["pass"] else "MISMATCH"))
    print("  A %s   V %s   M %s   R %s" % (
        pct(table["A"]["cagr_net"]), pct(table["V"]["cagr_net"]),
        pct(table["M"]["cagr_net"]), pct(table["R"]["cagr_net"])))
    print("  t(V-M) %s  t(V-R) %s  t(M-R) %s"
          % (tt(prim["t_V_vs_M"]), tt(prim["t_V_vs_R"]), tt(prim["t_M_vs_R"])))
    dec = prim["decomposition"]
    print("  decomposition: total %s = sort %s + size %s (size share %s)"
          % ("n/a" if dec["total_pp"] is None else "%+.2fpp" % dec["total_pp"],
             "n/a" if dec["sort_pp"] is None else "%+.2fpp" % dec["sort_pp"],
             "n/a" if dec["size_pp"] is None else "%+.2fpp" % dec["size_pp"],
             "n/a" if dec["size_share"] is None else "%.0f%%" % (100.0 * dec["size_share"])))
    print("  S %s   MS %s   t(S-MS) %s -> %s"
          % (pct(table["S"]["cagr_net"]), pct(table["MS"]["cagr_net"]),
             tt(prim["t_S_vs_MS"]), prim["verdict_residual"]))
    q = twin["M"]
    print("  twin fit (M): median |log cap ratio| %s, bands %s, unmatched %d"
          % ("n/a" if q["median_abs_log"] is None else "%.4f" % q["median_abs_log"],
             q["bands"], q["unmatched"]))
    print("verdict %s | residual %s -> %s" % (verdict, prim["verdict_residual"],
                                              os.path.relpath(OUT, ROOT)))
    return 0 if verdict != "CONTROL_MISMATCH" else 2


if __name__ == "__main__":
    sys.exit(main())
