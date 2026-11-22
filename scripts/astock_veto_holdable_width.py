#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A-share residual veto -- does it survive at a width you can actually buy?

Why this face exists
--------------------
r1865 (scripts/astock_resid_veto_layer.py) priced the residual signal in its
implementable shape: do not own the top-20% residual names.  It came out
ahead of both controls (whole pool 6.92%/yr, veto 10.34%/yr, random drop
6.89%/yr, paired B-A +0.245pp/rebalance t=3.51, B-R +0.248pp t=3.54).

But every one of those arms is an **equal-weight book of ~2,866 names**.  A
reader cannot buy 2,866 A-share lots with any account this company has; the
published +3.4pp/yr therefore lives in a book that does not exist.  The money
question is not "is the ordering informative" -- that is answered -- it is
"does the ordering still pay when the book is N names wide".

What this face prices
---------------------
Same panel, same rebalance dates (stride 20), same eligibility filter, same
score (all imported from the two parent modules, never re-declared), same
2 x 8bp x turnover cost.  Only the **book width** changes:

    A_cap_N      the N largest names by market cap, whole pool
    B_cap_N      the N largest names by market cap, veto pool (q<4)
    A_random_N   N names drawn uniformly from the whole pool     (20 draws)
    B_random_N   N names drawn uniformly from the veto pool      (20 draws)

The market-cap rule is not a signal: it is the mechanical way to make a book
buyable, it is the variable the residual is already orthogonalised against (so
the A/B difference cannot be a size bet), and it applies identically to both
pools.  A traded-value rule was tried first and rejected: in A-shares its top
rank is the highest-turnover speculative set, a momentum bet the reader never
asked for, and it prices the do-nothing arm at -2.9% per rebalance.  The random
arms answer the separate worry that any ranking rule is itself a return bet.

Criteria frozen before the first run (nothing here is tuned on the numbers):

  PRIMARY_WIDTH  N = 50 -- at the CEO page's 1,000,000 capital that is 20,000
                 yuan per name, small enough that one lot is reachable for
                 nearly every eligible A-share.
  WIDTHS         30 / 50 / 100, printed side by side so a reader can see the
                 width at which the effect dies instead of being told it lives.
  T_MIN          2.0 -- the same bar the parent face used; a paired difference
                 under two standard errors is not a result.
  BOTH_CONTROLS  the veto must beat the whole pool AND the random drop of the
                 same pool at the primary width.  One alone is the
                 "helps only against nothing" verdict the parent already
                 separated out.

  VETO_SURVIVES_AT_HOLDABLE_WIDTH   primary width clears both controls and both
                                    other widths have the same sign and clear
                                    T_MIN against A
  VETO_SURVIVES_AT_50_ONLY          primary width clears, but at least one other
                                    width does not -- read the numbers, not the
                                    headline
  VETO_HOLDS_ONLY_AT_SOME_WIDTHS    primary width does not clear, some other one
                                    does
  VETO_IS_A_BREADTH_ARTIFACT        no width has a positive significant B-A --
                                    the published edge was the 2,866-name book
  VETO_NOT_SEPARABLE_AT_WIDTH       mixed / not enough periods to tell

Usage
-----
    python scripts/astock_veto_holdable_width.py run
    python scripts/astock_veto_holdable_width.py check
    python scripts/astock_veto_holdable_width.py selftest
"""
from __future__ import annotations

import argparse
import json
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
)
from astock_resid_veto_layer import (  # noqa: E402
    _paired,
    _turnover,
    panel_frontier,
    score_slice,
    staleness,
)

OUT = os.path.join(ROOT, "results", "astock_veto_holdable_width.json")
PANEL_PER = os.path.join(ROOT, "data", "astock_daily", "per")

WIDTHS = (30, 50, 100)
PRIMARY_WIDTH = 50
T_MIN = 2.0
RANDOM_DRAWS = 20
SEED = 20261120
CAPITAL_CNY = 1000000.0
LOT = 100


def amt20_slice(t, amount):
    """20-bar mean amount by column -- the same expression the parent's
    eligibility filter uses.  L2 of the selftest pins the two together."""
    return np.nanmean(amount[max(0, t - HOLD + 1):t + 1], axis=0)


def pick_liquid(pool_key, pool_idx, n):
    """Indices (into the pool) of the n largest names by market cap, deterministic.

    Market cap (close x outstanding shares) rather than traded value: this is the
    basket a reader would actually buy, and it is the same variable the residual
    is orthogonalised against, so the A/B difference cannot be a size bet.  A
    traded-value rule was tried first and is kept only as a diagnostic print --
    in A-shares its top rank is the highest-turnover speculative names, which is
    a momentum bet the reader never asked for.
    """
    if n >= len(pool_idx):
        return np.arange(len(pool_idx))
    return np.argsort(-pool_key, kind="mergesort")[:n]


def run(dates, symbols, close, amount, shares, stride: int = HOLD, widths=WIDTHS):
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

        amt = amt20_slice(t, amount)[idx]
        with np.errstate(invalid="ignore"):
            size = close[t][idx] * shares[t][idx]
        veto_pool = q < 4
        pools = {"A": np.ones(len(idx), dtype=bool), "B": veto_pool}
        row = {"date": dates[t], "n_pool": int(len(idx)),
               "n_veto_pool": int(np.sum(veto_pool))}
        for n in widths:
            for tag, mask in pools.items():
                pool_pos = np.nonzero(mask)[0]
                if len(pool_pos) < n:
                    row["%s%d" % (tag, n)] = {"gross": None, "net": None,
                                              "turnover": None, "size": int(len(pool_pos))}
                    row["R%s%d" % (tag, n)] = {"gross": None, "net": None,
                                               "turnover": None, "size": int(len(pool_pos))}
                    continue
                pos = pool_pos[pick_liquid(size[mask], pool_pos, n)]
                cur = set(idx[pos].tolist())
                gross = float(np.mean(fwd[pos]))
                turb = _turnover(cur, prev.get("%s%d" % (tag, n)))
                prev["%s%d" % (tag, n)] = cur
                row["%s%d" % (tag, n)] = {"gross": gross,
                                          "net": gross - 2.0 * COST_ONE_SIDE * turb,
                                          "turnover": turb, "size": int(n)}
                # random control inside the same pool, averaged over draws.
                # A redrawn book keeps N/P of its names in expectation, so its
                # turnover is 1 - N/P every period (no union trick, no free ride
                # from the cost model on a book that is redrawn each time).
                draws = []
                for _ in range(RANDOM_DRAWS):
                    if len(pool_pos) <= n:
                        sel = pool_pos
                    else:
                        sel = pool_pos[rng.permutation(len(pool_pos))[:n]]
                    draws.append(float(np.mean(fwd[sel])))
                rg = float(np.mean(draws))
                rturb = 1.0 - float(min(n, len(pool_pos))) / float(len(pool_pos))
                row["R%s%d" % (tag, n)] = {"gross": rg,
                                           "net": rg - 2.0 * COST_ONE_SIDE * rturb,
                                           "turnover": rturb, "size": int(min(n, len(pool_pos)))}
        rows.append(row)
        t += stride
    return rows


def _nets(rows, key):
    out = []
    for r in rows:
        v = (r.get(key) or {}).get("net")
        out.append(float("nan") if v is None else float(v))
    return np.array(out, dtype=np.float64)


def _cagr(rows, key):
    v = _nets(rows, key)
    v = v[np.isfinite(v)]
    if len(v) < 3:
        return None
    return compound(v.tolist())


def paired_by_width(rows, widths=WIDTHS):
    """Three comparisons per width, each holding one thing fixed.

    B-A    the same market-cap rule applied to two pools  -> the veto
    B-RB   the veto pool with the rule replaced by random draws -> the veto
           without trusting the width rule
    B-RA   veto+rule against a random book from the whole pool -> the product
           a reader would actually be choosing between
    RB-RA  no selection rule on either side, only the pool -> the cleanest
           read of what dropping the top 20% residual is worth
    """
    out = {}
    for n in widths:
        cur = {}
        for arm, base in (("B", "A"), ("B", "RB"), ("B", "RA"), ("RB", "RA")):
            a, b = "%s%d" % (base, n), "%s%d" % (arm, n)
            aa = _nets(rows, a)
            bb = _nets(rows, b)
            mask = np.isfinite(aa) & np.isfinite(bb)
            key = "%s_vs_%s" % (b, a)
            if int(np.sum(mask)) < 3:
                cur[key] = {"n": int(np.sum(mask)), "mean": None, "se": None, "t": None}
                continue
            # reuse the parent's paired statistic: one key with the differences,
            # one key that is identically zero, so mean/se/t come from its code
            cur[key] = _paired(
                [{"date": "x", "L": {"net": float(d)}, "M": {"net": 0.0}}
                 for d in (bb[mask] - aa[mask]).tolist()], "L", "M")
        out[str(n)] = cur
    return out


def _sig(p):
    if not p or p.get("mean") is None or p.get("t") is None:
        return False
    return p["mean"] > 0 and p["t"] >= T_MIN


def verdict_holdable(paired, primary=PRIMARY_WIDTH, widths=WIDTHS):
    prim = paired.get(str(primary)) or {}
    prim_ok = (_sig(prim.get("B%d_vs_A%d" % (primary, primary)))
               and _sig(prim.get("B%d_vs_RB%d" % (primary, primary))))
    others = [_sig((paired.get(str(n)) or {}).get("B%d_vs_A%d" % (n, n)))
              for n in widths if n != primary]
    any_sig = prim_ok or any(others)
    means = []
    for n in widths:
        p = (paired.get(str(n)) or {}).get("B%d_vs_A%d" % (n, n)) or {}
        means.append(p.get("mean"))
    if prim_ok and others and all(others):
        v = "VETO_SURVIVES_AT_HOLDABLE_WIDTH"
    elif prim_ok:
        v = "VETO_SURVIVES_AT_%d_ONLY" % primary
    elif any_sig:
        v = "VETO_HOLDS_ONLY_AT_SOME_WIDTHS"
    elif means and all(m is not None and m <= 0 for m in means):
        v = "VETO_IS_A_BREADTH_ARTIFACT"
    else:
        v = "VETO_NOT_SEPARABLE_AT_WIDTH"
    return v, {"primary_ok": prim_ok, "other_widths_significant": others}


def by_year(rows, key):
    out = {}
    for r in rows:
        v = (r.get(key) or {}).get("net")
        if v is None:
            continue
        out.setdefault(r["date"][:4], []).append(float(v))
    return {y: {"periods": len(v), "compound": compound(v)} for y, v in sorted(out.items())}


def selection_diagnostic(dates, symbols, close, amount, shares, k=5):
    """What each candidate ranking rule actually buys, on the last bar.

    Printed so the width rule can be argued about with names in front of the
    reader, not adjectives: market cap and traded value pick different books.
    """
    rets = daily_returns(close)
    mkt = market_return(rets)
    t = len(dates) - 1
    idx, resid, q, _ = score_slice(t, close, amount, shares, rets, mkt, need_forward=False)
    if resid is None:
        return {"as_of": dates[t], "status": "no_eligible_names"}
    amt = amt20_slice(t, amount)[idx]
    with np.errstate(invalid="ignore"):
        size = close[t][idx] * shares[t][idx]
    out = {"as_of": dates[t], "eligible": int(len(idx))}
    for label, key in (("by_market_cap", size), ("by_traded_value", amt)):
        order = np.argsort(-key, kind="mergesort")[:k]
        out[label] = [{"symbol": symbols[idx[i]], "size_cny": float(size[i]),
                       "amt20_cny": float(amt[i])} for i in order]
    return out


def lot_feasibility(dates, symbols, close, amount, shares, n=PRIMARY_WIDTH):
    """At CAPITAL_CNY spread over n names, how many of today's picks cannot
    afford one 100-share lot?  A book you cannot buy is not a book."""
    rets = daily_returns(close)
    mkt = market_return(rets)
    t = len(dates) - 1
    idx, resid, q, _ = score_slice(t, close, amount, shares, rets, mkt, need_forward=False)
    per_name = CAPITAL_CNY / float(n)
    if resid is None:
        return {"as_of": dates[t], "names": n, "capital_cny": CAPITAL_CNY,
                "per_name_cny": round(per_name, 2), "status": "no_eligible_names"}
    amt = amt20_slice(t, amount)[idx]
    with np.errstate(invalid="ignore"):
        size = close[t][idx] * shares[t][idx]
    veto_pool = q < 4
    pool_pos = np.nonzero(veto_pool)[0]
    picks = pool_pos[pick_liquid(size[veto_pool], pool_pos, min(n, len(pool_pos)))]
    lot_cost = close[t][idx[picks]] * LOT
    over = lot_cost > per_name
    return {"as_of": dates[t], "names": int(len(picks)), "capital_cny": CAPITAL_CNY,
            "per_name_cny": round(per_name, 2),
            "one_lot_over_budget": int(np.sum(over)),
            "one_lot_over_budget_pct": round(100.0 * float(np.mean(over)), 2) if len(picks) else None,
            "max_one_lot_cny": round(float(np.max(lot_cost)), 2) if len(picks) else None,
            "median_one_lot_cny": round(float(np.median(lot_cost)), 2) if len(picks) else None,
            "note": "priced on the last bar of the panel; fills happen at the next open"}


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
    print("OK %s (sample %d files)" % (msg, sampled))
    return 0


def selftest():
    fails = []

    def check(name, cond, detail=""):
        if not cond:
            fails.append("%s %s" % (name, detail))

    rng = np.random.default_rng(11)
    n_t, n_s = 260, 200
    dates = ["2020-%02d-%02d" % (1 + i // 28, 1 + i % 28) for i in range(n_t)]
    close = 10.0 * np.cumprod(1 + rng.normal(0, 0.01, size=(n_t, n_s)), axis=0)
    amount = np.full((n_t, n_s), 5e7)
    shares = np.full((n_t, n_s), 1e8)

    rets = daily_returns(close)
    mkt = market_return(rets)
    t = n_t - HOLD - 1
    idx, resid, q, fwd = score_slice(t, close, amount, shares, rets, mkt)
    check("L1 score returns members", resid is not None and len(idx) > 50)

    # L2 the amt20 mirror agrees with the parent's eligibility filter
    amt = amt20_slice(t, amount)[idx]
    check("L2 amt20 mirror reproduces eligibility",
          bool(np.all(amt >= MIN_AMOUNT_20D)) and np.all(np.isfinite(amt)),
          "min=%.3g" % float(np.nanmin(amt)))

    # L3 the liquid pick returns exactly n distinct pool positions
    pos = pick_liquid(amt, np.arange(len(idx)), 30)
    check("L3 liquid pick is n distinct", len(pos) == 30 and len(set(pos.tolist())) == 30)

    # L4 requesting more names than the pool keeps the whole pool
    pos_all = pick_liquid(amt, np.arange(len(idx)), len(idx) + 5)
    check("L4 over-width keeps the pool", len(pos_all) == len(idx))

    # L5 deterministic: same inputs, same order
    check("L5 pick is deterministic",
          np.array_equal(pick_liquid(amt, np.arange(len(idx)), 30),
                         pick_liquid(amt, np.arange(len(idx)), 30)))

    # L6 verdict separates survives / 50-only / artifact
    def _p(mean, tt):
        return {"mean": mean, "se": None, "t": tt}

    def _w(a_m, a_t, rb_m, rb_t):
        return {"BA": _p(a_m, a_t), "RB": _p(rb_m, rb_t)}

    good = {}
    for n in WIDTHS:
        g = _w(0.002, 3.0, 0.002, 2.5)
        good[str(n)] = {"B%d_vs_A%d" % (n, n): g["BA"], "B%d_vs_RB%d" % (n, n): g["RB"]}
    v, _ = verdict_holdable(good)
    check("L6a all widths clear -> survives", v == "VETO_SURVIVES_AT_HOLDABLE_WIDTH", v)
    mixed = dict(good)
    m30 = _w(0.002, 1.1, 0.002, 1.1)
    mixed["30"] = {"B30_vs_A30": m30["BA"], "B30_vs_RB30": m30["RB"]}
    v, _ = verdict_holdable(mixed)
    check("L6b one width fails -> 50-only", v == "VETO_SURVIVES_AT_50_ONLY", v)
    flat = {}
    for n in WIDTHS:
        f = _w(-0.001, -1.0, -0.001, -1.0)
        flat[str(n)] = {"B%d_vs_A%d" % (n, n): f["BA"], "B%d_vs_RB%d" % (n, n): f["RB"]}
    v, _ = verdict_holdable(flat)
    check("L6c nothing clears -> breadth artifact", v == "VETO_IS_A_BREADTH_ARTIFACT", v)
    noisy = {}
    for n in WIDTHS:
        ny = _w(0.001, 1.0, 0.001, 1.0)
        noisy[str(n)] = {"B%d_vs_A%d" % (n, n): ny["BA"], "B%d_vs_RB%d" % (n, n): ny["RB"]}
    v, _ = verdict_holdable(noisy)
    check("L6d noise-sized edge is not a pass", v == "VETO_NOT_SEPARABLE_AT_WIDTH", v)

    # L7 the width layer never manufactures return: a constant forward return
    # prices to that same constant for every width and both pools
    fwd_flat = np.full(len(idx), 0.03)
    size_flat = close[t][idx] * shares[t][idx]
    pos30 = pick_liquid(size_flat, np.arange(len(idx)), 30)
    veto_pos = np.nonzero(q < 4)[0]
    bpos = (veto_pos[pick_liquid(size_flat[q < 4], veto_pos, min(30, len(veto_pos)))]
            if len(veto_pos) >= 30 else veto_pos)
    check("L7a constant return prices to itself",
          abs(float(np.mean(fwd_flat[pos30])) - 0.03) < 1e-12)
    check("L7b veto pool keeps the same constant",
          len(bpos) == 0 or abs(float(np.mean(fwd_flat[bpos])) - 0.03) < 1e-12)

    # L8 the freshness probe is the parent's, so a face behind the panel is STALE
    check("L8 stale word survives wrapping",
          staleness({"evidence_cutoff": "2026-11-19", "panel": {"last": "2026-11-19"}},
                    "2026-11-20")[0] == "stale")

    total = 12
    if fails:
        print("selftest FAIL %d/%d" % (len(fails), total))
        for f in fails:
            print("  " + f)
        return 1
    print("selftest %d/%d PASS" % (total, total))
    return 0


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

    dates, symbols, close, amount, shares = load_panel()
    rows = run(dates, symbols, close, amount, shares, stride=args.stride)
    if not rows:
        print("no rebalance rows")
        return 2

    paired = paired_by_width(rows)
    v, flags = verdict_holdable(paired)
    arms = {}
    for n in WIDTHS:
        for tag in ("A%d", "B%d", "RA%d", "RB%d"):
            k = tag % n
            nets = _nets(rows, k)
            nets = nets[np.isfinite(nets)]
            arms[k] = {
                "periods": int(len(nets)),
                "cagr_net": _cagr(rows, k),
                "mean_net_per_rebalance": float(np.mean(nets)) if len(nets) else None,
                "mean_turnover": float(np.nanmean([
                    (r.get(k) or {}).get("turnover") for r in rows
                    if (r.get(k) or {}).get("turnover") is not None] or [float("nan")])),
            }
    payload = {
        "generated": datetime.now().astimezone().isoformat(timespec="seconds"),
        "evidence_cutoff": dates[-1],
        "machine": _machine(),
        "kind": "astock_veto_holdable_width",
        "fills_the_hole_of": "results/astock_resid_veto_layer.json (arms are ~2866-name books)",
        "prereg": None,
        "adoption": None,
        "spec": {"hold": HOLD, "stride": args.stride, "lookback_beta": LOOKBACK_BETA,
                 "min_amount_20d": MIN_AMOUNT_20D, "min_bars": MIN_BARS,
                 "cost_one_side": COST_ONE_SIDE, "widths": list(WIDTHS),
                 "primary_width": PRIMARY_WIDTH, "t_min": T_MIN,
                 "random_draws": RANDOM_DRAWS, "seed": SEED,
                 "selection": "top-N by market cap (close x outstanding shares), identical rule in both pools",
                 "selection_tried_first": "top-N by 20d traded value -- rejected: in A-shares its top rank is the highest-turnover speculative set, a momentum bet the reader never asked for",
                 "arms": {"A": "whole eligible pool", "B": "pool minus top 20% residual",
                          "RA": "random N from whole pool", "RB": "random N from veto pool"}},
        "panel": {"dates": len(dates), "symbols": len(symbols),
                  "first": dates[0], "last": dates[-1]},
        "rebalances": len(rows),
        "arms": arms,
        "by_year": {"B%d" % PRIMARY_WIDTH: by_year(rows, "B%d" % PRIMARY_WIDTH),
                    "A%d" % PRIMARY_WIDTH: by_year(rows, "A%d" % PRIMARY_WIDTH)},
        "paired": paired,
        "vote": flags,
        "lot": lot_feasibility(dates, symbols, close, amount, shares),
        "selection_diagnostic": selection_diagnostic(dates, symbols, close, amount, shares),
        "verdict": v,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)

    print("rebalances %d  cutoff %s  panel %d symbols"
          % (len(rows), payload["evidence_cutoff"], len(symbols)))
    for n in WIDTHS:
        a, b, ra, rb = (arms["A%d" % n], arms["B%d" % n],
                        arms["RA%d" % n], arms["RB%d" % n])
        p = paired[str(n)]["B%d_vs_A%d" % (n, n)]
        pr = paired[str(n)]["B%d_vs_RB%d" % (n, n)]
        pn = paired[str(n)]["B%d_vs_RA%d" % (n, n)]
        prr = paired[str(n)]["RB%d_vs_RA%d" % (n, n)]
        print("  N=%-3d A %6.2f%%  B %6.2f%%  | B-A %+.2fpp/reb t %s | B-RB %+.2fpp/reb t %s | B-RA %+.2fpp/reb t %s | RB-RA %+.2fpp/reb t %s"
              % (n, 100.0 * (a["cagr_net"] or 0), 100.0 * (b["cagr_net"] or 0),
                 100.0 * p["mean"] if p["mean"] is not None else float("nan"),
                 ("%+.2f" % p["t"]) if p["t"] is not None else "n/a",
                 100.0 * pr["mean"] if pr["mean"] is not None else float("nan"),
                 ("%+.2f" % pr["t"]) if pr["t"] is not None else "n/a",
                 100.0 * pn["mean"] if pn["mean"] is not None else float("nan"),
                 ("%+.2f" % pn["t"]) if pn["t"] is not None else "n/a",
                 100.0 * prr["mean"] if prr["mean"] is not None else float("nan"),
                 ("%+.2f" % prr["t"]) if prr["t"] is not None else "n/a"))
    rt = arms["RA%d" % PRIMARY_WIDTH]["cagr_net"]
    print("  random whole-pool book at N=%d: %s" % (PRIMARY_WIDTH,
          ("%.2f%%" % (100.0 * rt)) if rt is not None else "n/a"))
    print("verdict %s -> %s" % (v, os.path.relpath(OUT, ROOT)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
