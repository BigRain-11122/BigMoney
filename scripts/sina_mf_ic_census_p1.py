# -*- coding: utf-8 -*-
"""Sina four-tier money-flow stock-level IC census P1 (bandit next_pick
event-attention lane; SINA_MF_PREREG frozen data lane consumed here for the
first time as an INDEPENDENT causal sub-face per its sec.2 isolation law).

RESEARCH QUESTION (meaning-gate q1): do sina four-tier money-flow factors
(net-flow ratio + per-tier net-flow shares of same-row buy amount) carry
forward-return rank IC at stock level on the frozen p1c panel? The EM
main-force panel (original next_pick data face) is source-blocked 53/5222
since 09-25; the sina panel is COMPLETE (5228 stocks x ~250td). Per frozen
SINA_MF spec law: sina tiers are sina's OWN decomposition -- this census
frames them as an independent sub-face, NOT an EM substitute (quantity
fabrication prohibited there).
CONSUMER (q2): trial-labor supply line -- if census enriches -> full prereg
from research/PREREG_TEMPLATE.md (g1_prime_v2/g2_registration_v2, D6 dedup,
explicit exit-axis) -> judged burn -> TRIAL-* paper. If no enrichment ->
honest park, zero burn (CEO meaning-order: no waste).
DEDUP (q3): zero prior sina_mf factor consumption in repo (S6 collectors
only); EM moneyflow IC batch never burned (panel blocked); theme-judge /
LHB / P-1e zoo = different faces; smart_retail is an IN-BATCH declared
linear composite (r0_net+r1_net-r3_net), disclosed not hidden.

DESCRIPTIVE CENSUS, NOT A JUDGMENT BATCH (theme_ignition_census v0.3 law;
style_rot_census_p1 r717 lineage): zero registration/paper claims, zero
ledger rows, no multiple-testing-line statements. Enrichment here only
gates whether a prereg is worth drafting.

FROZEN GRID (declared before any result inspection; no edits after):
  panels  : data/sina_mf/per/<code>.csv (frozen schema 14 cols,
            opendate 2025-09-15..2026-09-24, 5228 files) x p1c_stock cache
            close (qfq, T=8792 N=5222, evidence_cutoff = 2026-09-22);
            sina tail rows after the p1c cutoff are UNCONSUMABLE (no
            forward returns) -- disclosed, not truncated silently.
  universe: 5222 p1c syms (sina intersection = 5222/5222; 6 sina-only
            newer IPOs structurally excluded, count disclosed).
  factors (scale-free same-row shares; unit-honest by construction --
            numerators and the buy_total denominator come from the same
            row and the same tier decomposition, so any common unit factor
            cancels; net_ratio uses sina's own ratio column as-is):
            net_ratio    = ratioamount                        predicted +
            super_share  = r0_net / (r0+r1+r2+r3)             predicted +
            large_share  = r1_net / (r0+r1+r2+r3)            predicted +
            mid_share    = r2_net / (r0+r1+r2+r3)             predicted +
            small_share  = r3_net / (r0+r1+r2+r3)            predicted -
            smart_retail = (r0_net+r1_net-r3_net)/buy_total   predicted +
            (folk direction declaration: inflow of big tiers -> up,
             retail-small absorbing -> down; one-sided tests below)
  smooth  : d1 (raw) | d5 (trailing 5-td mean, min_periods=3)
  horizon : h5/h10/h20 fwd close-to-close; h10 PRIMARY (p1c/p1e convention)
  cells   : 6 factors x 2 smoothings x 3 horizons = 36 IC series reported;
            GATE applies to the 12 PRIMARY (h10) cells only.
  mask    : per-date pairwise-complete (factor finite & fwd finite),
            cross-section >= 300 valid names else date skipped;
            close NOT ffilled here (suspended names excluded honestly,
            stricter than the p1c harness ffill convention).
  stats   : n_dates, mean rank IC, ic_std, ic_ir, one-sample t
            (ic_mean / (ic_std/sqrt(n))), one-sided binomial sign-test p
            in the declared predicted direction.
  ENRICHMENT GATE (pre-declared AND-gate, r717 lineage): any PRIMARY cell:
            p <= 0.05 AND |t| >= 2.0 -> CENSUS_ENRICHED (prereg draft next);
            else NO_CENSUS_ENRICHMENT (honest park).
  reuse   : shortline_p1_ic._ic_series_fast (gated spearman path) -- the
            only IC methodology in this file; stats computed unrounded on
            the raw series (census stat face, not a stats_block rewrite).

Census-grade honesty: single process (CEO CPU 10% headroom law), zero
network, Money02 read-only (memmap), idempotent re-run (same JSON modulo
generated ts), panel self-check (netamount vs sum(r*_net), R215 verifier
aggregate) disclosed as a data-integrity face, no gate.

Subcommands: selftest (offline synthetic gates) | run (real-data census)
"""
import argparse
import datetime as _dt
import glob
import json
import math
import os
import sys
import warnings

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from shortline_p1_ic import _ic_series_fast          # gated reuse (only IC path)

CACHE = os.path.join(ROOT, "Money02", "data", "cache", "p1c_stock")
BARS = os.path.join(ROOT, "Money02", "data", "bars")
SINA_DIR = os.path.join(ROOT, "data", "sina_mf", "per")
OUT = os.path.join(ROOT, "results", "sina_mf_ic_census_p1.json")

HORIZONS = [5, 10, 20]
H_PRIMARY = 10
SMOOTHINGS = [("d1", 1), ("d5", 5)]
D5_MIN_PERIODS = 3
MIN_XS_NAMES = 300
GATE_P, GATE_T = 0.05, 2.0
SELFCHK_TOL = 1e-3

PRED = {
    "net_ratio": 1, "super_share": 1, "large_share": 1, "mid_share": 1,
    "small_share": -1, "smart_retail": 1,
}
FACTOR_COLS = ["opendate", "ratioamount", "r0", "r1", "r2", "r3",
               "r0_net", "r1_net", "r2_net", "r3_net", "netamount"]


def _factor_frames(df):
    """One stock's raw sina rows -> dict factor Series indexed by opendate.
    buy_total = same-row tier buy sum (unit cancels in every share)."""
    r0, r1, r2, r3 = (df[c].to_numpy(dtype=float) for c in ("r0", "r1", "r2", "r3"))
    n0 = df["r0_net"].to_numpy(dtype=float)
    n1 = df["r1_net"].to_numpy(dtype=float)
    n2 = df["r2_net"].to_numpy(dtype=float)
    n3 = df["r3_net"].to_numpy(dtype=float)
    buy = r0 + r1 + r2 + r3
    with np.errstate(invalid="ignore", divide="ignore"):
        ok = np.isfinite(buy) & (buy > 0) & np.isfinite(n0) & np.isfinite(n1) \
            & np.isfinite(n2) & np.isfinite(n3)
        safe_buy = np.where(ok, buy, np.nan)
        super_s = np.where(ok, n0 / safe_buy, np.nan)
        large_s = np.where(ok, n1 / safe_buy, np.nan)
        mid_s = np.where(ok, n2 / safe_buy, np.nan)
        small_s = np.where(ok, n3 / safe_buy, np.nan)
        smart_s = np.where(ok, (n0 + n1 - n3) / safe_buy, np.nan)
    ratio = pd.to_numeric(df["ratioamount"], errors="coerce").to_numpy(dtype=float)
    idx = df["opendate"].astype(str).to_numpy()
    return {
        "net_ratio": pd.Series(ratio, index=idx),
        "super_share": pd.Series(super_s, index=idx),
        "large_share": pd.Series(large_s, index=idx),
        "mid_share": pd.Series(mid_s, index=idx),
        "small_share": pd.Series(small_s, index=idx),
        "smart_retail": pd.Series(smart_s, index=idx),
    }


def _panel_selfcheck(df):
    """Aggregate R215-verifier face: |netamount - sum(r*_net)| rel tol."""
    na = pd.to_numeric(df["netamount"], errors="coerce").to_numpy(dtype=float)
    tot = (df["r0_net"].to_numpy(float) + df["r1_net"].to_numpy(float)
           + df["r2_net"].to_numpy(float) + df["r3_net"].to_numpy(float))
    d = np.abs(na - tot)
    scale = np.maximum(np.abs(tot), 1.0)
    fin = np.isfinite(d) & np.isfinite(tot)
    return int((d[fin] <= SELFCHK_TOL * scale[fin]).sum()), int(fin.sum())


def _load_sina(syms):
    """Single pass over the 5228 csvs -> per-factor dict {code: Series} +
    selfcheck aggregates + file counts. Window alignment happens later."""
    per = {f: {} for f in PRED}
    n_rows = n_files = n_read_err = 0
    chk_ok = chk_n = 0
    for path in sorted(glob.glob(os.path.join(SINA_DIR, "*.csv"))):
        code = os.path.basename(path)[:-4]
        n_files += 1
        if code not in syms:
            continue
        try:
            df = pd.read_csv(path, usecols=FACTOR_COLS)
        except Exception:
            n_read_err += 1
            continue
        n_rows += len(df)
        a, b = _panel_selfcheck(df)
        chk_ok += a
        chk_n += b
        for fname, ser in _factor_frames(df).items():
            per[fname][code] = ser
    meta = {"sina_files": n_files, "sina_only_structural_exclusions":
            n_files - sum(1 for c in per["net_ratio"]),
            "panel_rows_read": n_rows, "read_errors": n_read_err,
            "selfcheck_rows_within_1e-3": chk_ok, "selfcheck_rows_total": chk_n}
    return per, meta


def _block(s, dirn):
    """Census stat block on raw IC series; one-sided p in declared dir."""
    s = s.dropna()
    n = int(s.size)
    if n < 30:
        return {"n_dates": n, "note": "insufficient periods"}
    mean = float(s.mean())
    sd = float(s.std(ddof=1))
    t = mean / (sd / math.sqrt(n)) if sd > 0 else float("nan")
    hits = int((s > 0).sum()) if dirn > 0 else int((s < 0).sum())
    p = _sign_test_p(hits, n)
    return {"n_dates": n, "ic_mean": round(mean, 5), "ic_std": round(sd, 5),
            "ic_ir": round(mean / sd, 3) if sd > 0 else 0.0,
            "one_sample_t": round(t, 3) if np.isfinite(t) else None,
            "sign_test_p_one_sided_pred": round(p, 5),
            "ic_pos_pct": round(float((s > 0).mean()), 3)}


def _sign_test_p(hits, n):
    if n <= 0:
        return 1.0
    tail = sum(math.comb(n, i) * 0.5 ** n for i in range(hits, n + 1))
    return min(1.0, tail)


def _enrichment_verdict(cells):
    prim = [c for c in cells if c.get("h") == H_PRIMARY and c.get("n_dates", 0) >= 30]
    enriched = []
    for c in prim:
        if (c["sign_test_p_one_sided_pred"] <= GATE_P
                and c.get("one_sample_t") is not None
                and abs(c["one_sample_t"]) >= GATE_T):
            enriched.append(f'{c["factor"]}-{c["smooth"]}')
    return ("CENSUS_ENRICHED: " + ",".join(enriched)
            + " -> prereg draft next (PREREG_TEMPLATE + trial-labor default)"
            if enriched else
            "NO_CENSUS_ENRICHMENT -> honest park (no prereg, no burn)")


def cmd_run():
    dates = np.load(os.path.join(CACHE, "dates.npy"))
    close_mm = np.load(os.path.join(CACHE, "close.npy"), mmap_mode="r")
    syms = [os.path.basename(p)[:-8]
            for p in sorted(glob.glob(os.path.join(BARS, "*.parquet")))]
    symset = set(syms)
    all_str = [_dt.datetime.fromtimestamp(int(d) / 1e6).strftime("%Y-%m-%d")
               for d in dates]
    cutoff = all_str[-1]

    per, meta = _load_sina(symset)
    print(f"sina meta: {meta}", flush=True)

    earliest = min(ser.index.min() for ser in per["net_ratio"].values())
    ws = next(i for i, s in enumerate(all_str) if s >= earliest)
    win_str = all_str[ws:]
    print(f"window {win_str[0]}..{cutoff} rows={len(win_str)}", flush=True)

    close = np.asarray(close_mm[ws:], dtype=np.float64)
    close_df = pd.DataFrame(close, index=pd.Index(win_str), columns=syms)
    fwd = {h: close_df.shift(-h) / close_df - 1.0 for h in HORIZONS}
    del close_df, close

    frames = {}
    for fname in PRED:
        fdf = pd.DataFrame(per[fname])
        fdf.index = pd.Index(fdf.index.astype(str), name="date")
        frames[fname] = fdf.reindex(win_str)
    del per

    cells = []
    t0 = _dt.datetime.now()
    for fname in PRED:
        base = frames[fname]
        for sname, w in SMOOTHINGS:
            fdf = base if w == 1 else base.rolling(w, min_periods=D5_MIN_PERIODS).mean()
            for h in HORIZONS:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", RuntimeWarning)
                    cnt = (fdf.notna() & fwd[h].notna()).sum(axis=1)
                    ok_dates = cnt[cnt >= MIN_XS_NAMES].index
                    if len(ok_dates) == 0:
                        cells.append({"factor": fname, "smooth": sname, "h": h,
                                      "n_dates": 0,
                                      "note": "no date with enough names"})
                        continue
                    s = _ic_series_fast(fdf.loc[ok_dates], fwd[h].loc[ok_dates])
                blk = _block(s, PRED[fname])
                cells.append({"factor": fname, "smooth": sname, "h": h, **blk})
    elapsed = (_dt.datetime.now() - t0).total_seconds()

    doc = {
        "artifact": "sina four-tier money-flow stock-level IC census P1 "
                    "(descriptive, pre-burn cheap screen)",
        "law_refs": [
            "firm/TRIAL_LABOR_LAW.md sec.2 cheap-screen-first",
            "CEO meaning-order O-20261001-1108 hard-gate-1 (census before burn)",
            "SINA_MF_PREREG sec.2 isolation law (independent sub-face, no EM mapping)",
            "bandit next_pick event-attention lane (EM face source-blocked, disclosed)",
            "style_rot_census_p1 r717 lineage (census gate paradigm)",
        ],
        "frozen_grid": {
            "panel_sina": "data/sina_mf/per 5228 csv (frozen schema, ~250td rolling)",
            "panel_p1c": f"p1c_stock cache close qfq (T=8792 N=5222, cutoff {cutoff})",
            "factors": list(PRED),
            "predicted_direction": {k: ("+" if v > 0 else "-") for k, v in PRED.items()},
            "smoothings": {n: w for n, w in SMOOTHINGS},
            "d5_min_periods": D5_MIN_PERIODS,
            "horizons": HORIZONS, "h_primary": H_PRIMARY,
            "min_xs_names": MIN_XS_NAMES,
            "gate": f"primary cells: p<={GATE_P} AND |t|>={GATE_T}",
        },
        "honesty": [
            "DESCRIPTIVE CENSUS ONLY: no verdict, no paper claim, zero ledger rows",
            "sina tail rows after p1c cutoff (2026-09-23/24) unconsumable -- disclosed",
            "sina-only newer IPOs structurally excluded (not in p1c bars universe)",
            "close NOT ffilled: suspended names excluded per-date (stricter than harness)",
            "smart_retail = declared in-batch linear composite of super/large/small",
            "enrichment gate is a screen, not the fleet multiple-testing line",
        ],
        "panel_selfcheck": meta,
        "evidence_cutoff": cutoff,
        "cells": cells,
        "verdict": _enrichment_verdict(cells),
        "elapsed_s": round(elapsed, 1),
        "generated": _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    print("verdict:", doc["verdict"])
    for c in cells:
        if c.get("h") == H_PRIMARY:
            print(c)
    print("wrote", OUT)
    return 0


# ------------------------------------------------------------- selftest

def _synthetic_close(T=300, N=240, seed=11):
    rng = np.random.default_rng(seed)
    rets = rng.normal(0, 0.01, (T, N))
    rets[:, : N // 2] += 0.004          # first half names drift up
    close = np.cumprod(1 + rets, axis=0)
    close[:, -5:] = np.nan              # 5 never-traded names
    return close


def _synthetic_factor(close_df, kind, seed=13):
    """kind 'alpha': cross-section matching true drift (positive IC).
    kind 'noise': pure white noise."""
    T, N = close_df.shape
    rng = np.random.default_rng(seed)
    if kind == "alpha":
        v = np.tile(np.linspace(0.004, 0.000, N), (T, 1))
    else:
        v = rng.standard_normal((T, N))
    return pd.DataFrame(v, index=close_df.index, columns=close_df.columns)


def _cells_from(close_df, factor_df, h=H_PRIMARY, dirn=1, min_names=20):
    fwd = close_df.shift(-h) / close_df - 1.0
    cnt = (factor_df.notna() & fwd.notna()).sum(axis=1)
    ok_dates = cnt[cnt >= min_names].index
    s = _ic_series_fast(factor_df.loc[ok_dates], fwd.loc[ok_dates])
    return _block(s, dirn)


def cmd_selftest():
    fails = []
    T, N = 300, 240
    win_str = [f"d{i:03d}" for i in range(T)]
    close = _synthetic_close(T, N)
    close_df = pd.DataFrame(close, index=pd.Index(win_str))

    # L1: alpha factor -> primary gate fires (positive direction)
    blk = _cells_from(close_df, _synthetic_factor(close_df, "alpha"), dirn=1)
    if not (blk.get("sign_test_p_one_sided_pred", 1) <= GATE_P
            and abs(blk.get("one_sample_t") or 0) >= GATE_T):
        fails.append(f"L1 alpha not detected: {blk}")

    # L2: noise factor -> gate does not fire
    blk2 = _cells_from(close_df, _synthetic_factor(close_df, "noise"), dirn=1)
    if (blk2.get("sign_test_p_one_sided_pred", 1) <= GATE_P
            and abs(blk2.get("one_sample_t") or 0) >= GATE_T):
        fails.append(f"L2 noise false-enriched: {blk2}")

    # L3: factor construction scale-invariance + buy_total guard
    row = pd.DataFrame({
        "opendate": ["2026-01-05", "2026-01-06"],
        "ratioamount": [0.05, -0.02],
        "r0": [100.0, 200.0], "r1": [50.0, 100.0],
        "r2": [30.0, 60.0], "r3": [20.0, 40.0],
        "r0_net": [10.0, -20.0], "r1_net": [5.0, -10.0],
        "r2_net": [2.0, -4.0], "r3_net": [1.0, -2.0],
        "netamount": [18.0, -36.0],
    })
    f1 = _factor_frames(row)
    row2 = row.copy()
    for c in ("r0", "r1", "r2", "r3", "r0_net", "r1_net", "r2_net", "r3_net"):
        row2[c] = row2[c] * 100.0                       # common unit change
    f2 = _factor_frames(row2)
    for k in ("super_share", "large_share", "mid_share", "small_share",
              "smart_retail"):
        if not np.allclose(f1[k].to_numpy(float), f2[k].to_numpy(float),
                           equal_nan=True):
            fails.append(f"L3 scale-invariance broken for {k}")
    row3 = row.copy()
    row3[["r0", "r1", "r2", "r3"]] = 0.0               # buy_total = 0
    f3 = _factor_frames(row3)
    if np.isfinite(f3["super_share"].to_numpy(float)).any():
        fails.append("L3 buy_total=0 guard failed (finite share produced)")

    # L4: window reindex -- in-window rows map, out-of-window rows drop
    f4 = _factor_frames(row)
    aligned = pd.DataFrame({c: f4["net_ratio"] for c in ("A", "B")}).reindex(
        ["2026-01-05", "2026-01-06", "2026-01-07"])
    if not (np.isfinite(aligned.loc["2026-01-05", "A"])
            and aligned.loc["2026-01-05", "A"] == 0.05
            and aligned.loc["2026-01-07", "A"] != aligned.loc["2026-01-07", "A"]):
        fails.append("L4 window reindex mapping wrong")

    # L5: determinism -- identical cells on identical input
    b1 = _cells_from(close_df, _synthetic_factor(close_df, "alpha"), dirn=1)
    b2 = _cells_from(close_df, _synthetic_factor(close_df, "alpha"), dirn=1)
    if json.dumps(b1, sort_keys=True) != json.dumps(b2, sort_keys=True):
        fails.append("L5 non-deterministic cells")

    # L6: sign-test sanity (monotone in hits; P(X>=5|n=10)=638/1024=0.623
    # -- tail includes the exact-5 mass, NOT 0.5)
    p9, p5 = _sign_test_p(9, 10), _sign_test_p(5, 10)
    if not (0.0 <= p9 <= p5 <= 1.0) or p9 > 0.055 or abs(p5 - 638 / 1024) > 1e-9:
        fails.append(f"L6 sign-test sanity: p(9/10)={p9} p(5/10)={p5}")

    print("SELFTEST", "PASS 6/6" if not fails else "FAIL: " + "; ".join(fails))
    return 0 if not fails else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "selftest"])
    a = ap.parse_args()
    return cmd_selftest() if a.cmd == "selftest" else cmd_run()


if __name__ == "__main__":
    sys.exit(main())
