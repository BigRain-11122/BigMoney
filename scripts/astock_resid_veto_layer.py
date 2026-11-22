#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A-share residual veto layer: the implementable shape of the residual signal.

Why this face exists
--------------------
r1862 (scripts/astock_resid_reversal_probe.py) measured the 20-day residual
reversal on the full A-share panel and found the ordering informative but the
long-short spread unrealisable: A-shares cannot be shorted at portfolio scale,
and the only positive leg (q1, lowest residual) earned -0.42%/yr while q5
(highest residual) was the single negative cell (-0.26% per 20 days against
+1.32% for the middle).  The signal's executable form is therefore not "short
the top quintile" but "do not own it".

This face prices exactly that: three equal-weight arms on the same eligible
pool, same rebalance dates, same cost model.

    A  the whole eligible pool              (the do-nothing book)
    B  the pool minus the top 20% residuals (the veto)
    C  the pool minus the top 40% residuals

and one control that decides whether B is worth anything at all: dropping a
*random* 20% of the same pool.  Without it, "the veto helped" can simply mean
"high-residual names are high-volatility names".

Design (frozen in this file, not tuned on results)
--------------------------------------------------
* everything about the score is imported from astock_resid_reversal_probe
  (universe filter, beta window, cross-sectional residual, rank), so the two
  faces cannot drift apart.
* rebalance every 20 trading rows of the global calendar from 2020-01-02.
* cost = 2 * 8bp * turnover, turnover = 1 - |arm_t & arm_t-1| / |arm_t|.
* random control: 20 draws of the same drop fraction, fixed seed 20261120.
* verdict requires the paired per-rebalance difference to clear 2 standard
  errors against BOTH arm A and the random control, otherwise the honest
  answer is that the veto is indistinguishable from dropping names at random.

Usage
-----
    python scripts/astock_resid_veto_layer.py run
    python scripts/astock_resid_veto_layer.py check
    python scripts/astock_resid_veto_layer.py selftest

`check` (r1936) is the cheap freshness probe the chain pays for a rebuild on: it
asks the panel, not itself, whether the published `evidence_cutoff` is still the
last reachable bar.
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import os
import sys
from datetime import datetime

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from astock_resid_reversal_probe import (  # noqa: E402
    HOLD,
    LOOKBACK_BETA,
    MIN_AMOUNT_20D,
    MIN_BARS,
    COST_ONE_SIDE,
    FIRST_DATE,
    beta_window,
    compound,
    cross_sectional_residual,
    daily_returns,
    load_panel,
    market_return,
    rank01,
)

OUT = os.path.join(ROOT, "results", "astock_resid_veto_layer.json")
PANEL_PER = os.path.join(ROOT, "data", "astock_daily", "per")
RANDOM_DRAWS = 20
SEED = 20261120
FRONTIER_SAMPLE = 40


def score_slice(t, close, amount, shares, rets, mkt, need_forward=True):
    """Cross-sectional score at row t. Returns (idx, resid, q, fwd)."""
    c0 = close[t]
    c_past = close[t - HOLD]

    with np.errstate(invalid="ignore", divide="ignore"):
        r20 = c0 / c_past - 1.0
        f20 = close[t + HOLD] / c0 - 1.0 if need_forward else np.full_like(c0, np.nan)

    amt_win = amount[max(0, t - HOLD + 1):t + 1]
    with np.errstate(invalid="ignore"):
        amt20 = np.nanmean(amt_win, axis=0)

    win = rets[t - LOOKBACK_BETA + 1:t + 1]
    nbars = np.sum(np.isfinite(win), axis=0)
    beta = beta_window(win, mkt[t - LOOKBACK_BETA + 1:t + 1])
    with np.errstate(invalid="ignore", divide="ignore"):
        logsize = np.log(c0 * shares[t])

    ok = (
        np.isfinite(r20)
        & np.isfinite(beta)
        & np.isfinite(logsize)
        & (nbars >= MIN_BARS)
        & (amt20 >= MIN_AMOUNT_20D)
    )
    if need_forward:
        ok = ok & np.isfinite(f20)
    idx = np.nonzero(ok)[0]
    if len(idx) < 60:
        return idx, None, None, None
    resid = cross_sectional_residual(r20[idx], beta[idx], logsize[idx])
    q = np.clip((rank01(resid) * 5).astype(int), 0, 4)
    return idx, resid, q, (f20[idx] if need_forward else None)


def _turnover(cur: set, prev) -> float:
    if prev is None:
        return 1.0
    if not cur:
        return 0.0
    return 1.0 - len(cur & prev) / float(len(cur))


def run(dates, symbols, close, amount, shares, stride: int = HOLD):
    rets = daily_returns(close)
    mkt = market_return(rets)

    start = 0
    while start < len(dates) and dates[start] < FIRST_DATE:
        start += 1
    start = max(start, LOOKBACK_BETA)

    rng = np.random.default_rng(SEED)
    prev = {"A": None, "B": None, "C": None, "R": None}
    rows = []
    t = start
    while t + HOLD < len(dates):
        idx, resid, q, fwd = score_slice(t, close, amount, shares, rets, mkt)
        if resid is None:
            t += stride
            continue

        n = len(idx)
        masks = {
            "A": np.ones(n, dtype=bool),
            "B": q < 4,
            "C": q < 3,
        }
        # random control: drop the same fraction as B, averaged over draws
        drop_n = int(n - np.sum(masks["B"]))
        rand_means, rand_sets = [], []
        for _ in range(RANDOM_DRAWS):
            perm = rng.permutation(n)
            keep = np.zeros(n, dtype=bool)
            keep[perm[: n - drop_n]] = True
            rand_means.append(float(np.mean(fwd[keep])))
            rand_sets.append(set(idx[keep].tolist()))

        row = {"date": dates[t], "n": int(n), "q_counts": [int(np.sum(q == k)) for k in range(5)]}
        for name, m in masks.items():
            cur = set(idx[m].tolist())
            gross = float(np.mean(fwd[m]))
            turb = _turnover(cur, prev[name])
            net = gross - 2.0 * COST_ONE_SIDE * turb
            row[name] = {"gross": gross, "net": net, "turnover": turb, "size": int(np.sum(m))}
            prev[name] = cur
        # random arm: mean cost uses the mean turnover of the draws
        rg = float(np.mean(rand_means))
        rcur = set.union(*rand_sets) if rand_sets else set()
        rturb = _turnover(rcur, prev["R"])
        prev["R"] = rcur
        row["R"] = {"gross": rg, "net": rg - 2.0 * COST_ONE_SIDE * rturb, "turnover": rturb,
                    "size": int(n - drop_n)}
        rows.append(row)
        t += stride
    return rows


def _paired(rows, arm, base):
    d = np.array([r.get(arm, {}).get("net", float("nan")) - r.get(base, {}).get("net", float("nan"))
                  for r in rows], dtype=np.float64)
    d = d[np.isfinite(d)]
    if len(d) < 3:
        return {"n": int(len(d)), "mean": None, "se": None, "t": None}
    mean = float(d.mean())
    se = float(d.std(ddof=1) / math.sqrt(len(d)))
    return {"n": int(len(d)), "mean": mean, "se": se, "t": (mean / se) if se > 0 else None}


def _by_year(rows, key):
    out = {}
    for r in rows:
        y = r["date"][:4]
        out.setdefault(y, []).append(r[key]["net"])
    return {y: {"periods": len(v), "compound": compound(v)} for y, v in sorted(out.items())}


def _arm_summary(rows, key):
    nets = [r[key]["net"] for r in rows]
    gross = [r[key]["gross"] for r in rows]
    return {
        "periods": len(nets),
        "cagr_net": compound(nets),
        "cagr_gross": compound(gross),
        "mean_net_per_rebalance": float(np.mean(nets)) if nets else None,
        "mean_turnover": float(np.mean([r[key]["turnover"] for r in rows])) if rows else None,
        "mean_size": float(np.mean([r[key]["size"] for r in rows])) if rows else None,
    }


def verdict(rows):
    b_a = _paired(rows, "B", "A")
    b_r = _paired(rows, "B", "R")
    c_a = _paired(rows, "C", "A")
    if b_a["t"] is None or b_r["t"] is None:
        # a zero-variance difference is still a difference when it is negative:
        # report the loss, but never let a flat constant pretend to be an edge
        if b_a["mean"] is not None and b_a["mean"] < 0:
            return "VETO_HURTS", {"vs_A": b_a, "vs_random": b_r, "C_vs_A": c_a}
        return "INSUFFICIENT_PERIODS", {"vs_A": b_a, "vs_random": b_r, "C_vs_A": c_a}
    if b_a["t"] >= 2.0 and b_r["t"] >= 2.0:
        v = "VETO_ADDS_VALUE"
    elif b_a["t"] >= 2.0 and b_r["t"] < 2.0:
        v = "HELPS_ONLY_AGAINST_NOTHING_NOT_AGAINST_RANDOM"
    elif b_a["mean"] is not None and b_a["mean"] <= 0:
        v = "VETO_HURTS"
    else:
        v = "VETO_NOT_SEPARABLE"
    return v, {"vs_A": b_a, "vs_random": b_r, "C_vs_A": c_a}


def current_veto(dates, symbols, close, amount, shares):
    rets = daily_returns(close)
    mkt = market_return(rets)
    t = len(dates) - 1
    idx, resid, q, _ = score_slice(t, close, amount, shares, rets, mkt, need_forward=False)
    if resid is None:
        return {"as_of": dates[t], "status": "no_eligible_names"}
    order = np.argsort(-resid)  # highest residual first
    veto = [
        {"symbol": symbols[idx[k]], "resid": float(resid[k])}
        for k in order[:60]
    ]
    best = np.argsort(resid)
    hold = [
        {"symbol": symbols[idx[k]], "resid": float(resid[k])}
        for k in best[:40]
    ]
    return {"as_of": dates[t], "eligible": int(len(idx)),
            "veto_share": 0.2, "veto_top": veto, "lowest_resid": hold}


# ------------------------------------------------------------- freshness probe
def panel_frontier(per_dir: str = PANEL_PER, sample: int = FRONTIER_SAMPLE):
    """Last bar date reachable in the per-symbol panel, from a stride sample.

    Deliberately cheap: load_panel() walks 5k CSVs and costs minutes, and a probe
    that expensive is a probe nobody runs (the r1850 family).  A stride sample of
    the sorted names bounds the reachable frontier from below, which is all the
    probe has to know: a face whose cutoff is at or past that bound cannot be
    behind the panel.  Returns (frontier_date or None, files_sampled).
    """
    files = sorted(glob.glob(os.path.join(per_dir, "*.csv")))
    if not files:
        return None, 0
    step = max(1, len(files) // sample)
    picked = files[::step][:sample]
    best = ""
    seen = 0
    for path in picked:
        try:
            with open(path, "rb") as fh:
                fh.seek(0, os.SEEK_END)
                size = fh.tell()
                fh.seek(max(0, size - 4096))
                chunk = fh.read().decode("utf-8", "ignore")
        except OSError:
            continue
        rows = [ln for ln in chunk.splitlines() if ln.strip()]
        if not rows:
            continue
        last = rows[-1].split(",")[0]
        if len(last) != 10 or last[4] != "-":
            continue
        seen += 1
        if last > best:
            best = last
    return (best or None), seen


def staleness(face: dict, frontier):
    """Pure verdict over the published face and the panel's reachable frontier.

    (state, message); state is 'ok' / 'stale' / 'inconsistent'.  Only 'stale'
    means "rebuilding fixes this" -- the chain pays for a run on that word alone
    (r1850: the walk is expensive, so it must be asked a cheap question first).
    """
    cutoff = face.get("evidence_cutoff")
    panel_last = (face.get("panel") or {}).get("last")
    if not cutoff:
        return "inconsistent", "face has no evidence_cutoff"
    if panel_last and panel_last != cutoff:
        return ("inconsistent",
                "face disagrees with itself: evidence_cutoff=%s panel.last=%s"
                % (cutoff, panel_last))
    if frontier is None:
        return "stale", "panel unreadable: %s (sample found no rows)" % (
            os.path.relpath(PANEL_PER, ROOT))
    if cutoff < frontier:
        return ("stale", "panel moved: face cutoff %s, panel reaches %s"
                % (cutoff, frontier))
    if cutoff > frontier:
        return ("inconsistent",
                "face claims a bar the panel does not reach: %s > %s"
                % (cutoff, frontier))
    return "ok", "cutoff %s == panel frontier %s" % (cutoff, frontier)


def cmd_check():
    if not os.path.exists(OUT):
        print("STALE face missing: %s" % os.path.relpath(OUT, ROOT))
        return 3
    with open(OUT, encoding="utf-8") as fh:
        face = json.load(fh)
    frontier, n = panel_frontier()
    state, msg = staleness(face, frontier)
    if state == "stale":
        print("STALE %s (sample %d files)" % (msg, n))
        return 3
    if state == "inconsistent":
        print("CHECK FAILED %s (sample %d files)" % (msg, n))
        return 1
    print("OK %s (sample %d files)" % (msg, n))
    return 0


# ---------------------------------------------------------------- selftest
def selftest():
    fails = []

    def check(name, cond, detail=""):
        if not cond:
            fails.append("%s %s" % (name, detail))

    rng = np.random.default_rng(7)
    n_t, n_s = 260, 120
    dates = ["2020-%02d-%02d" % (1 + i // 28, 1 + i % 28) for i in range(n_t)]
    close = 10.0 * np.cumprod(1 + rng.normal(0, 0.01, size=(n_t, n_s)), axis=0)
    amount = np.full((n_t, n_s), 5e7)
    shares = np.full((n_t, n_s), 1e8)

    rets = daily_returns(close)
    mkt = market_return(rets)
    idx, resid, q, fwd = score_slice(n_t - HOLD - 1, close, amount, shares, rets, mkt)
    check("L1 score returns members", resid is not None and len(idx) > 50)
    check("L2 residual orthogonal to size", abs(float(np.corrcoef(resid, np.log(close[n_t - HOLD - 1][idx] * 1e8))[0, 1])) < 0.2,
          "corr=%.3f" % float(np.corrcoef(resid, np.log(close[n_t - HOLD - 1][idx] * 1e8))[0, 1]))

    # L3: an arm that keeps everyone must equal the pool mean exactly
    m_all = np.ones(len(idx), dtype=bool)
    check("L3 arm A is the pool mean", abs(float(np.mean(fwd[m_all])) - float(np.mean(fwd))) < 1e-12)

    # L4: turnover of an unchanged set is zero, of a disjoint set is one
    s = set(idx[:10].tolist())
    check("L4 same set -> turnover 0", _turnover(s, s) == 0.0)
    check("L5 disjoint -> turnover 1", _turnover(set([999999, 999998]), s) == 1.0)
    check("L6 first period pays full turnover", _turnover(s, None) == 1.0)

    # L7-L9: paired statistics behave
    rows = [{"date": "2020-01-01", "A": {"net": 0.01}, "B": {"net": 0.02}, "R": {"net": 0.015}}] * 5
    check("L7 paired mean", abs(_paired(rows, "B", "A")["mean"] - 0.01) < 1e-12)
    rows2 = [{"date": "2020-01-01", "A": {"net": 0.0}, "B": {"net": -0.01}, "R": {"net": 0.0}}] * 5
    v, _ = verdict(rows2)
    check("L8 veto that loses is named", v == "VETO_HURTS", v)

    # L9: verdict separates 'beats nothing' from 'beats random'
    rows3 = []
    for i in range(30):
        rows3.append({"date": "2020-01-01",
                      "A": {"net": 0.0}, "B": {"net": 0.01}, "R": {"net": 0.0099}})
    v3, _ = verdict(rows3)
    check("L9 noise-sized edge does not clear random", v3 != "VETO_ADDS_VALUE", v3)

    # L10-L13: the probe's four answers. Only 'stale' may buy a rebuild; a face
    # that disagrees with itself or claims a bar the panel cannot reach must stay
    # red rather than be rebuilt until it looks green (r1345/r1850 trap).
    check("L10 in sync -> ok",
          staleness({"evidence_cutoff": "2026-11-20", "panel": {"last": "2026-11-20"}},
                    "2026-11-20")[0] == "ok")
    check("L11 face behind panel -> stale",
          staleness({"evidence_cutoff": "2026-11-19", "panel": {"last": "2026-11-19"}},
                    "2026-11-20")[0] == "stale")
    check("L12 face ahead of panel -> inconsistent",
          staleness({"evidence_cutoff": "2026-11-23", "panel": {"last": "2026-11-23"}},
                    "2026-11-20")[0] == "inconsistent")
    check("L13 face disagrees with itself -> inconsistent",
          staleness({"evidence_cutoff": "2026-11-20", "panel": {"last": "2026-11-19"}},
                    "2026-11-20")[0] == "inconsistent")

    # L14: the cheap frontier really reads the files it claims to read
    import shutil
    import tempfile
    td = tempfile.mkdtemp()
    try:
        for code, last in (("600000", "2026-11-19"), ("000001", "2026-11-20")):
            with open(os.path.join(td, code + ".csv"), "w", encoding="utf-8") as fh:
                fh.write("date,close,amount,outstanding_share\n")
                fh.write("%s,10.0,1e8,1e8\n" % last)
        fr, n_seen = panel_frontier(td, sample=10)
        check("L14 frontier reads the sampled files",
              fr == "2026-11-20" and n_seen == 2, "fr=%r n=%r" % (fr, n_seen))
    finally:
        shutil.rmtree(td, ignore_errors=True)

    if fails:
        print("selftest FAIL %d/%d" % (len(fails), 14))
        for f in fails:
            print("  " + f)
        return 1
    print("selftest 14/14 PASS")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run",
                    choices=["run", "check", "selftest"])
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

    v, paired = verdict(rows)
    payload = {
        "generated": datetime.now().astimezone().isoformat(timespec="seconds"),
        "evidence_cutoff": dates[-1],
        "machine": _machine(),
        "kind": "astock_residual_veto_layer",
        "prereg": None,
        "adoption": None,
        "spec": {
            "hold": HOLD, "stride": args.stride, "lookback_beta": LOOKBACK_BETA,
            "min_amount_20d": MIN_AMOUNT_20D, "min_bars": MIN_BARS,
            "cost_one_side": COST_ONE_SIDE, "random_draws": RANDOM_DRAWS, "seed": SEED,
            "arms": {"A": "whole eligible pool", "B": "pool minus top 20% residual",
                     "C": "pool minus top 40% residual", "R": "random 20% dropped (20 draws)"},
        },
        "panel": {"dates": len(dates), "symbols": len(symbols),
                  "first": dates[0], "last": dates[-1]},
        "rebalances": len(rows),
        "arms": {k: _arm_summary(rows, k) for k in ("A", "B", "C", "R")},
        "by_year": {k: _by_year(rows, k) for k in ("A", "B", "C", "R")},
        "paired_per_rebalance": paired,
        "current": current_veto(dates, symbols, close, amount, shares),
        "verdict": v,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)

    a, b, c, r = (payload["arms"][k] for k in ("A", "B", "C", "R"))
    print("rebalances %d  cutoff %s  panel %d symbols" % (len(rows), payload["evidence_cutoff"], len(symbols)))
    for name, s in (("A pool", a), ("B -top20", b), ("C -top40", c), ("R random20", r)):
        print("  %-10s cagr_net %7.2f%%  gross %7.2f%%  turn %.3f  size %.0f"
              % (name, 100 * s["cagr_net"], 100 * s["cagr_gross"], s["mean_turnover"], s["mean_size"]))
    print("  B-A  mean %+.4f%%/reb  t %+.2f | B-R mean %+.4f%%/reb  t %+.2f"
          % (100 * paired["vs_A"]["mean"], paired["vs_A"]["t"],
             100 * paired["vs_random"]["mean"], paired["vs_random"]["t"]))
    print("verdict %s -> %s" % (v, os.path.relpath(OUT, ROOT)))
    cur = payload["current"]
    print("current veto list %s (%d names shown of %d eligible)"
          % (cur["as_of"], len(cur.get("veto_top", [])), cur.get("eligible", 0)))
    return 0


def _machine() -> str:
    try:
        with open(os.path.join(ROOT, "fleet", "machine.json"), encoding="utf-8") as fh:
            return json.load(fh).get("machine_id", "unknown")
    except (OSError, ValueError):
        return "unknown"


if __name__ == "__main__":
    sys.exit(main())
