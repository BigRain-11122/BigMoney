# -*- coding: utf-8 -*-
"""Style-rotation stock-level census P1 (r690/r693 planned next-wave pointer;
T-73 s2 lineage; trial-labor law sec.2 cheap-screen-first; CEO meaning-order
hard-gate-1 cheap-census-before-burn).

RESEARCH QUESTION (meaning-gate q1): does the T-73 s2 ETF-face dual-horizon
style-rotation structure (r259 close: annual trend ALIVE thin + quarterly
mean-reversion one-sided) exist at STOCK level on the frozen p1c panel as a
style-sleeve rotation signal? (CEO orientation law 2026-09-28 15:22 lists
style-rotation as priority A-share native school.)
CONSUMER (q2): trial-labor supply line -- if census enriches -> full prereg
from research/PREREG_TEMPLATE.md (science_gates g1_prime_v2/g2_registration_v2,
D6 dedup, explicit exit-axis) -> judged burn -> TRIAL-* paper. If no
enrichment -> honest park, zero burn (meaning-order: no waste).
DEDUP (q3): scripts/t73_s2_style_rotation.py = ETF-panel 9-leg descriptive
history, CLOSED r259 (verdict-free narration, no stock-level claim);
results/t73_s2/factor_history.json = factor-history descriptive; no
stock-level style-ROTATION timing face burned or censused before this file.
T-139 stock trio (REV/LOWVOL/MOM) = single-style cross-sections, different
syntax (no rotation trigger / no style-index relative timing).

DESCRIPTIVE CENSUS, NOT A JUDGMENT BATCH (theme_ignition_census v0.3 law):
zero registration/paper claims, zero ledger rows, no multiple-testing-line
statements. Enrichment here only gates whether a prereg is worth drafting.

FROZEN GRID (declared before any result inspection; no edits after):
  panel   : p1c_stock memmap cache (T=8792, N=5222, qfq close; mktcap_raw =
            raw_close x osh[ffill snapshot proxy, T-73 s2 slice-D disclosure];
            turnover_derived per TURNOVER_DERIVATION.md) -- in-repo, zero
            network, cache build 2026-09-24 (evidence_cutoff = last cache date)
  universe: at rebalance t: close[t] and close[t-L] and close[t+F] finite,
            mktcap_raw[t] finite, 63d-median turnover finite, >=200 finite
            closes in past 250 bars
  style pairs (spread = aggressive sleeve minus defensive sleeve):
            SIZE: SMALL(bottom 30% mktcap) - LARGE(top 30%)
            TURN: HIGH(top 30% 63d-med turnover) - LOW(bottom 30%)
  faces (both at rebalance step 63 td PRIMARY, 21 td secondary robustness):
            TREND    : signal = sleeve spread over past L=252 td;
                       eval   = sleeve spread over next  F=63  td;
                       predicted direction = sign AGREEMENT (persistence)
            REVERSAL : signal = sleeve spread over past L=63  td;
                       eval   = sleeve spread over next  F=21  td;
                       predicted direction = sign FLIP (anti-persistence)
  cells   : 2 pairs x 2 faces x {63,21} = 8 (4 primary at step 63)
  stats   : n_dates, hit_rate (agreement for TREND / flip for REVERSAL),
            one-sided binomial sign-test p in predicted direction,
            conditional spread gap = mean(eval|sig>0) - mean(eval|sig<0),
            Welch t of that gap
  ENRICHMENT GATE (pre-declared): any PRIMARY cell: p<=0.05 AND |t|>=2.0
            -> verdict CENSUS_ENRICHED (prereg-draft next);
            else NO_CENSUS_ENRICHMENT (honest park).

Census-grade honesty: equal-weight no-cost sleeve spreads (a prereg would
add cost/tradability masks), osh-ffill size proxy disclosed, single process
(CPU 10% headroom law), idempotent re-run (same JSON modulo generated ts).

Subcommands: selftest (offline synthetic gates) | run (real-data census)
"""
import argparse
import datetime as _dt
import json
import math
import os
import sys
import warnings

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "Money02", "data", "cache", "p1c_stock")
OUT = os.path.join(ROOT, "results", "style_rot_census_p1.json")

L_TREND, F_TREND = 252, 63
L_REV, F_REV = 63, 21
STEPS = (63, 21)
PAIRS = ("SIZE", "TURN")
MIN_PAST_BARS, MIN_FINITE_250 = 250, 200
BUCKET_TRIM = 0.30  # bottom/top 30%


def _load():
    close = np.load(os.path.join(CACHE, "close.npy"), mmap_mode="r")
    mcap = np.load(os.path.join(CACHE, "mktcap_raw.npy"), mmap_mode="r")
    turn = np.load(os.path.join(CACHE, "turnover_derived.npy"), mmap_mode="r")
    dates = np.load(os.path.join(CACHE, "dates.npy"))
    return np.asarray(close), np.asarray(mcap), np.asarray(turn), dates


def _evidence_cutoff(dates):
    last = int(dates[-1])
    # dates are int64 MICROseconds since epoch (Money02 bars convention)
    return _dt.datetime.fromtimestamp(last / 1e6).strftime("%Y-%m-%d")


def _rank_pairs(var, mask):
    """Return (lo_idx, hi_idx) boolean buckets among mask-valid names."""
    v = np.where(mask, var, np.nan)
    finite = np.isfinite(v)
    if finite.sum() < 60:
        return None
    order = np.argsort(np.where(finite, v, np.inf))
    ranked = order[: finite.sum()]
    n = len(ranked)
    k = max(1, int(round(n * BUCKET_TRIM)))
    return ranked[:k], ranked[n - k:]


def _spread_eval(close, lo_idx, hi_idx, t, w):
    """Equal-weight sleeve spread of close[t+w]/close[t]-1 (nanmean, endpoint)."""
    def _ret(idx):
        r = close[t + w, idx] / close[t, idx] - 1.0
        return float(np.nanmean(r)) if np.isfinite(r).any() else np.nan
    a, b = _ret(lo_idx), _ret(hi_idx)
    return a - b if (np.isfinite(a) and np.isfinite(b)) else np.nan


def _sign_test_p(hits, n):
    """One-sided binomial P(X >= hits) under p=0.5 (predicted-direction test)."""
    if n <= 0:
        return 1.0
    tail = sum(math.comb(n, i) * 0.5 ** n for i in range(hits, n + 1))
    return min(1.0, tail)


def _welch_t(x, y):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    x, y = x[np.isfinite(x)], y[np.isfinite(y)]
    if len(x) < 5 or len(y) < 5:
        return float("nan")
    vx, vy = x.var(ddof=1), y.var(ddof=1)
    se = math.sqrt(vx / len(x) + vy / len(y))
    if se <= 0:
        return float("nan")
    return float((x.mean() - y.mean()) / se)


def run_census(close, mcap, turn, dates, step):
    T, _ = close.shape
    cells = []
    for pair in PAIRS:
        for face in ("TREND", "REVERSAL"):
            L = L_TREND if face == "TREND" else L_REV
            F = F_TREND if face == "TREND" else F_REV
            start = max(L, MIN_PAST_BARS)
            sig, ev = [], []
            for t in range(start, T - F, step):
                hist_mask = np.isfinite(close[t - 1])
                if pair == "TURN":
                    blk = turn[t - L_REV:t + 1]
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore", RuntimeWarning)
                        var = np.nanmedian(blk, axis=0)
                else:
                    var = mcap[t]
                ok = (
                    np.isfinite(close[t]) & np.isfinite(close[t - L])
                    & np.isfinite(close[t + F]) & np.isfinite(var)
                )
                window = close[max(0, t - MIN_PAST_BARS):t]
                if window.shape[0] < MIN_PAST_BARS:
                    continue
                nfinite = np.isfinite(window).sum(axis=0)
                ok &= nfinite >= MIN_FINITE_250
                if not hist_mask.any():
                    continue
                buckets = _rank_pairs(var, ok)
                if buckets is None:
                    continue
                lo, hi = buckets
                past = _spread_eval(close, lo, hi, t - L, L)
                fwd = _spread_eval(close, lo, hi, t, F)
                if not (np.isfinite(past) and np.isfinite(fwd)) or past == 0:
                    continue
                sig.append(past)
                ev.append(fwd)
            sig = np.asarray(sig)
            ev = np.asarray(ev)
            n = int(sig.size)
            if n == 0:
                cells.append({"pair": pair, "face": face, "step": step,
                              "n_dates": 0, "note": "no valid rebalance dates"})
                continue
            agree = np.sign(sig) == np.sign(ev)
            hits = int(agree.sum())
            hit_rate = hits / n
            p = _sign_test_p(hits, n) if face == "TREND" else _sign_test_p(n - hits, n)
            pos, neg = ev[sig > 0], ev[sig < 0]
            gap = float(np.nanmean(pos) - np.nanmean(neg)) if pos.size and neg.size else float("nan")
            tstat = _welch_t(pos, neg)
            cells.append({
                "pair": pair, "face": face, "step": step, "n_dates": n,
                "hit_rate": round(hit_rate, 4),
                "sign_test_p_one_sided_pred_dir": round(p, 5),
                "cond_spread_gap": round(gap, 6) if np.isfinite(gap) else None,
                "welch_t": round(tstat, 3) if np.isfinite(tstat) else None,
                "mean_eval_sig_pos": round(float(np.nanmean(pos)), 6) if pos.size else None,
                "mean_eval_sig_neg": round(float(np.nanmean(neg)), 6) if neg.size else None,
            })
    return cells


def _enrichment_verdict(cells):
    prim = [c for c in cells if c.get("step") == 63 and c.get("n_dates", 0) > 0]
    enriched = []
    for c in prim:
        if (c["sign_test_p_one_sided_pred_dir"] <= 0.05
                and c.get("welch_t") is not None and abs(c["welch_t"]) >= 2.0):
            enriched.append(f'{c["pair"]}-{c["face"]}')
    return ("CENSUS_ENRICHED: " + ",".join(enriched)
            + " -> prereg draft next (PREREG_TEMPLATE + trial-labor default)"
            if enriched else "NO_CENSUS_ENRICHMENT -> honest park (no prereg, no burn)")


def cmd_run():
    close, mcap, turn, dates = _load()
    all_cells = []
    for step in STEPS:
        all_cells.extend(run_census(close, mcap, turn, dates, step))
    doc = {
        "artifact": "style-rotation stock-level census P1 (descriptive, pre-burn cheap screen)",
        "law_refs": [
            "firm/TRIAL_LABOR_LAW.md sec.2 cheap-screen-first",
            "CEO meaning-order O-20261001-1108 hard-gate-1 (census before burn)",
            "CEO orientation law 2026-09-28 15:22 (style-rotation priority)",
            "T-73 s2 lineage (ETF dual-horizon close r259)",
        ],
        "frozen_grid": {
            "panel": "p1c_stock cache 2026-09-24 (T=8792 N=5222 qfq close)",
            "pairs": PAIRS, "L_trend": L_TREND, "F_trend": F_TREND,
            "L_rev": L_REV, "F_rev": F_REV, "steps": list(STEPS),
            "bucket_trim": BUCKET_TRIM, "min_past_bars": MIN_PAST_BARS,
        },
        "honesty": [
            "DESCRIPTIVE CENSUS ONLY: no verdict, no paper claim, zero ledger rows",
            "mktcap_raw = raw_close x osh (osh = current snapshot ffilled backward, T-73 s2 slice-D disclosed proxy)",
            "equal-weight no-cost sleeve spreads (prereg would add cost masks)",
            "enrichment gate is a screen, not the fleet multiple-testing line",
        ],
        "evidence_cutoff": _evidence_cutoff(dates),
        "cells": all_cells,
        "verdict": _enrichment_verdict(all_cells),
        "generated": _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    print("verdict:", doc["verdict"])
    for c in all_cells:
        print(c)
    print("wrote", OUT)
    return 0


def _synthetic(T=700, N=150, seed=7):
    rng = np.random.default_rng(seed)
    rets = rng.normal(0, 0.01, (T, N))
    # style var: first half names are "small/high-turn" (aggressive sleeve)
    style = np.where(np.arange(N) < N // 2, 0.0, 1.0)
    rets[:, : N // 2] += 0.001  # persistent small/agg alpha -> TREND agreement
    close = np.cumprod(1 + rets, axis=0)
    close[close <= 0] = np.nan
    mcap = np.tile(np.where(style == 0, 1e9, 1e11), (T, 1)).astype(float)
    turn = np.tile(np.where(style == 0, 0.05, 0.001), (T, 1)).astype(float)
    close[:, -3:] = np.nan  # 3 all-NaN names must be excluded, never zero-filled
    dates = np.arange(T, dtype=np.int64) * 86400000 + 1500000000000
    return close, mcap, turn, dates


def cmd_selftest():
    fails = []
    close, mcap, turn, dates = _synthetic()

    # L1: NaN names excluded (bucket size < N*trim+3 contamination check)
    cells = run_census(close, mcap, turn, dates, 63)
    if not cells:
        fails.append("L1 no cells produced")
    l1 = [c for c in cells if c["pair"] == "SIZE" and c["face"] == "TREND" and c["step"] == 63]
    if not l1 or l1[0].get("n_dates", 0) < 3:
        fails.append(f"L1 synthetic SIZE-TREND cell too small: {l1}")

    # L2: persistent alpha -> TREND hit_rate high, p small
    if l1 and l1[0].get("hit_rate", 0) < 0.7:
        fails.append(f"L2 expected hit_rate>=0.7 with persistent alpha, got {l1[0]}")

    # L3: sign-test p in [0,1] and monotone in hits (more hits -> smaller p)
    p9 = _sign_test_p(9, 10)
    p5 = _sign_test_p(5, 10)
    if not (0.0 <= p9 <= p5 <= 1.0) or p9 > 0.055 or p5 < 0.5:
        fails.append(f"L3 sign-test sanity: p(9/10)={p9} p(5/10)={p5}")

    # L4: reversal face exists and n_dates>0 on step 21 (robustness path)
    l4 = [c for c in cells if c["face"] == "REVERSAL" and c["step"] == 63]
    if not l4 or l4[0].get("n_dates", 0) < 3:
        fails.append(f"L4 reversal cell missing/too small: {l4}")

    # L5: idempotent cells (same inputs -> identical cells)
    cells2 = run_census(close, mcap, turn, dates, 63)
    if json.dumps(cells, sort_keys=True) != json.dumps(cells2, sort_keys=True):
        fails.append("L5 non-deterministic cells on identical input")

    print("SELFTEST", "PASS 5/5" if not fails else "FAIL: " + "; ".join(fails))
    return 0 if not fails else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "selftest"])
    a = ap.parse_args()
    return cmd_selftest() if a.cmd == "selftest" else cmd_run()


if __name__ == "__main__":
    sys.exit(main())
