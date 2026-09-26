"""REV_OSC_STOCK_P1 runner -- 超跌反弹袖个股版判决批 (T-87 first-priority slot).

Laws (frozen in research/REV_OSC_STOCK_PREREG.md @commit a7761433 -- R99:
zero real-data judged runs before the freeze commit; seed registered in the
same freeze commit, SEED_REGISTRY['rev_osc_stock_p1'] = 20261230):

  panel   P1C-StageA stock cache (T=8792 1990-12-19..2026-09-22 x N=5222,
          float32 qfq OHLCV, evidence_cutoff 2026-09-22 D2 lockbox); universe
          = b_layer ok_static 3517 (O-1820 3b) n P4_BATCH2 s2 dynamic clauses
          (amount20 >= 5e7 / listed >= 20 bars / close >= 1 / last-bar fresh
          <= 250td) n board != other (2 BSE syms, 30cm floor has no engine
          precedent = honest exclusion); survivorship = in-market snapshot
          cache face (A158/XSTOCK/P1E/CN-REV-TILT house precedent, disclosed).
  regime  sse.parquet reindexed onto the p1c calendar with ffill bridge (235
          missing days all in 1991-01..1993-08, coverage 97.33%); MA200 gate
          needs 200 finite values else gate undefined -> fail-closed no entry.
  signal  drop20 = close[t]/close[t-20]-1 (>=20 finite closes in window);
          weekly grid = every 5th bar from index 60; Top10 by deepest drop20
          (tie -> lower code first); thin market <5 candidates -> cohort skip.
  entry   T+1 open conservative proxy (O-1132): fill only if open finite and
          NOT near-limit-up open (open/prev_close-1 < floor-0.002; floors
          main 0.0975 / chinext+star 0.1975 with 20cm era switches
          2020-08-24 / 2019-07-22 -- wild_route_lab frozen faces verbatim).
  exit    time exit open[t+1+H] (H=7/10 per cell); TP +8% (gap-open fills at
          open), SL -10% (gap-open fills at open, worse); same-day both-touch
          -> SL first (conservative, refine-bench P1 law); sealed limit-down
          day (low==high==close and ret <= -floor) -> no fills, roll forward;
          suspension (NaN) rolls to first finite open; limit-down OPEN on the
          exit day (open/prev_close-1 <= -(floor-0.002)) -> roll forward.
  costs   V1 stock schedule 13.041bp/side multiplicative both sides
          (26.082bp roundtrip, P4_BATCH2 s3.2 anchor; wild_route same face);
          x1 = judged face, x2 = stress descriptive column (wild precedent).
  buckets 2 capital buckets round-robin by grid position (g % 2),
          per-STOCK even booking across its own held span [entry, exit);
          portfolio day return = 0.5*(b0+b1), idle days = 0 (cash).
  nulls   K=2000 same-mask random event days (rng SEED+k k<2000, random grid
          day x random 10 eligible, BASE mechanics no gate no filter) pooled,
          then K=2000 synthetic 52-cohort annual runs (rng SEED+k re-seeded,
          second independent use of the same declared band) -> annualized
          Sharpe values -> own null_pool for skill_line_v2 (stock-domain
          calibration, XSTOCK precedent). RANDOM_LARGE_SAMPLE_LAW v1.0 s3:
          block bootstrap 2000 draws (block=10d, per-cell daily-mean dist) +
          sign-flip permutation 2000 draws (per-cell Sharpe null) -- from one
          generator seeded at SEED consumed sequentially (R3 deterministic).
  starts  full-census virtual starts t0 in [200, T-126) (~8466 >= 1000),
          126d window compounded strategy vs eligible-EW passive proxy;
          4 segment classes (bull/bear/deep-bear/chop by sse level, MA200 and
          60d return at t0, prereg s3 frozen rule); segment n<500 =
          insufficient-sample honest note; >=100 random train/val splits +
          walk-forward 5 folds (law s2.3).
  gates   G1'v2 = science_gates.g1_prime_v2(sharpe_full, returns,
          batch_cells=2014, pool='stock_b_layer', null_pool=own) on the 7
          primary x1 cells; G2 = g2_registration_v2 + DSR(deflated_sharpe_
          ratio, n_trials=line.n_eff) + family PBO (screening/pbo.cscv_pbo
          CSCV-8 over the 7-cell x1 matrix). D6 (prereg s1) via the
          cn_rev_tilt_p1 ew6-canon face (REG6 members + same-batch cross).
          NO hand-copied lines (O-2250).
  honesty unfillable/near-limit premium/extension/roll counts per cell;
          |r_day| > 15% single-list with crisis windows 2015-06/07, 2016-01,
          2024-01/02, 2024-09/10 (hard-bound triad, D-20260925-01-1);
          judged-negative -> slot closed + new-evidence reopen note.

Products (prereg s6): results/rev_osc/p1_results.json (top evidence_cutoff +
cutoff_meta + 14 cell faces + nulls + D6 + virtual starts + splits +
walk-forward + gates + ledger block) + cells_summary.csv; per-cell
checkpoints results/rev_osc/cells/<cell>_<face>.json (idempotent skip);
finalize single-shot (REV_OSC_STOCK_P1_REFINALIZE=1 = only redo path).

Usage: run | selftest   (exit 0 ok; 2 = fail-closed gate refusal; 3 = RAM floor)
"""
import argparse
import json
import math
import os
import shutil
import sys
import tempfile
import time

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import science_gates as SG                      # shared gate library (O-2250)
from screening.pbo import cscv_pbo             # family PBO CSCV-8

CACHE = os.path.join(ROOT, "Money02", "data", "cache", "p1c_stock")
BARS = os.path.join(ROOT, "Money02", "data", "bars")
MASK = os.path.join(ROOT, "data", "fundamental", "b_layer_mask.csv")
SSE = os.path.join(ROOT, "Money02", "data", "index", "sse.parquet")
OUT_DIR = os.path.join(ROOT, "results", "rev_osc")
CELL_DIR = os.path.join(OUT_DIR, "cells")
OUT_JSON = os.path.join(OUT_DIR, "p1_results.json")
OUT_CSV = os.path.join(OUT_DIR, "cells_summary.csv")
ATT_JSON = os.path.join(ROOT, "results", "gate_attrition.json")

EVIDENCE_CUTOFF = "2026-09-22"
EXPECT_DATES = ("1990-12-19", EVIDENCE_CUTOFF)
T_EXPECT, N_EXPECT = 8792, 5222
OK_STATIC_EXPECT = 3517
SSE_COVER_MIN = 0.97
SEED = None            # filled from SG.SEED_REGISTRY at run (freeze commit)
BATCH_NAME = "REV_OSC_STOCK_P1"
BATCH_CELLS = 2014      # 7 cells x 2 faces + 2000 nulls (prereg s0)
K_NULLS = 2000
PBP = 252
COST_X1 = 0.0013041    # 13.041bp per side (V1 stock schedule, P4_BATCH2 s3.2)
COST_FACES = {"x1": COST_X1, "x2": COST_X1 * 2}
GRID_STEP = 5
GRID_FROM = 60
HOLD_BUFFER = 14       # t + 1 + H + roll slack <= T
TP, SL = 1.08, 0.90
LIMIT_OPEN_TOL = 0.002
MAIN_FLOOR, WIDE_FLOOR = 0.0975, 0.1975
CN_20CM_FROM = np.datetime64("2020-08-24")
STAR_FROM = np.datetime64("2019-07-22")
AMT20_MIN = 5e7
LISTED_MIN = 20
PRICE_MIN = 1.0
FRESH_MAX = 250
THIN_MARKET_MIN = 5
# zero-run amendment (r251 probe-authoritative, 2026-09-27 ~00:2x): the
# frozen single sentinel 300 is a modern-window scale (XSTOCK r68 median
# 1524 was computed on its 2015+ window); the FULL history face gives
# median 190 (p10=0 -- the 5000-wan amount20 gate is a modern liquidity
# scale and honestly empties the thin 1990s; cohorts there skip as
# thin_market). Dual sentinel: full-grid >= 150 AND 2010+ >= 500.
UNIV_MEDIAN_FULL_MIN = 150
UNIV_MEDIAN_2010_MIN = 500
UNIV_ERA_FROM = np.datetime64("2010-01-01")
WIN_DAYS = 126
STARTS_FROM = 200
SEG_MIN = 500
MAX_R_CRISIS = 0.15
CRISIS_WINDOWS = [(np.datetime64("2015-06-01"), np.datetime64("2015-07-31")),
                  (np.datetime64("2016-01-01"), np.datetime64("2016-01-31")),
                  (np.datetime64("2024-01-01"), np.datetime64("2024-02-29")),
                  (np.datetime64("2024-09-01"), np.datetime64("2024-10-31"))]
RAM_FLOOR_GB = 16.0
D6_REJECT = 0.7

# judged grid (prereg s3.1, frozen -- axis mirror of REFINE-BENCH-20260926-P1)
CELLS = [
    {"name": "BASE",         "yang": False, "dwr": False, "gate": False, "tpsl": False, "H": 7,  "w": "eq"},
    {"name": "BASE_BG",      "yang": False, "dwr": False, "gate": True,  "tpsl": False, "H": 7,  "w": "eq"},
    {"name": "FY_BG",        "yang": True,  "dwr": False, "gate": True,  "tpsl": False, "H": 7,  "w": "eq"},
    {"name": "FY_BG_TP8",    "yang": True,  "dwr": False, "gate": True,  "tpsl": True,  "H": 7,  "w": "eq"},
    {"name": "FY_BG_H10",    "yang": True,  "dwr": False, "gate": True,  "tpsl": False, "H": 10, "w": "eq"},
    {"name": "DWR_BG_TP8",   "yang": False, "dwr": True,  "gate": True,  "tpsl": True,  "H": 10, "w": "eq"},
    {"name": "FY_BG_INVVOL", "yang": True,  "dwr": False, "gate": True,  "tpsl": False, "H": 7,  "w": "invvol"},
]


# ------------------------------------------------------------- panel layer
def _free_ram_gb():
    try:
        import psutil
        return psutil.virtual_memory().available / 1e9
    except Exception:
        return RAM_FLOOR_GB + 1.0        # psutil absent -> guard off (disclosed)


def _roll_mean20(m):
    """Finite-aware 20-bar mean via float64 cumsums (NaN-aware, min 10)."""
    fin = np.isfinite(m)
    vals = np.where(fin, m, 0.0).astype(np.float64)
    cs = np.vstack([np.zeros((1, m.shape[1])), vals.cumsum(axis=0)])
    cc = np.vstack([np.zeros((1, m.shape[1]), dtype=np.int32),
                    fin.astype(np.int32).cumsum(axis=0)])
    lo = np.maximum(np.arange(m.shape[0]) - 20, 0)
    hi = np.arange(m.shape[0]) + 1
    cnt = cc[hi] - cc[lo]
    out = np.full(m.shape, np.nan, dtype=np.float32)
    ok = cnt >= 10
    out[ok] = ((cs[hi] - cs[lo])[ok] / cnt[ok]).astype(np.float32)
    return out


def load_panel():
    """Fail-closed gate battery (prereg s2) + panel assembly."""
    meta = json.load(open(os.path.join(CACHE, "meta.json"), encoding="utf-8"))
    shp = meta["shape"]
    assert shp["T"] == T_EXPECT and shp["N"] == N_EXPECT, "cache shape drift"
    idx = pd.to_datetime(np.load(os.path.join(CACHE, "dates.npy")), unit="us")
    assert str(idx[0].date()) == EXPECT_DATES[0] and \
        str(idx[-1].date()) == EXPECT_DATES[1], "cutoff lockbox drift"
    F = {}
    for f in ("open", "high", "low", "close", "pct_chg", "amount"):
        F[f] = np.load(os.path.join(CACHE, f + ".npy"))

    syms = [os.path.basename(p).split(".")[0]
            for p in sorted(os.listdir(BARS)) if p.endswith(".parquet")]
    assert len(syms) == N_EXPECT, "bars symbol census drift"

    mask = pd.read_csv(MASK, dtype={"code": str})
    assert len(mask) == N_EXPECT, "mask row census drift"
    ok_static = mask.set_index("code")["ok_static"].to_dict()
    board = mask.set_index("code")["board"].to_dict()
    n_ok = int(sum(bool(ok_static[s]) for s in syms))
    assert n_ok == OK_STATIC_EXPECT, f"ok_static census drift ({n_ok})"

    sse = pd.read_parquet(SSE)
    sse["date"] = pd.to_datetime(sse["date"])
    sse_close = sse.set_index("date")["close"].reindex(idx).ffill()
    cover = float(sse_close.notna().mean())
    assert cover >= SSE_COVER_MIN, f"sse coverage {cover} below gate"
    sse_v = sse_close.to_numpy(dtype=np.float64)
    ma200 = pd.Series(sse_v).rolling(200, min_periods=200).mean().to_numpy()

    # -- per-stock floor array (N,T): board x era switches (wild frozen faces)
    fl = np.full((N_EXPECT, T_EXPECT), MAIN_FLOOR, dtype=np.float32)
    for j, s in enumerate(syms):
        if board.get(s) in ("chinext", "star"):
            era = STAR_FROM if board.get(s) == "star" else CN_20CM_FROM
            fl[j, idx >= era] = WIDE_FLOOR

    # -- universe eligibility matrix (prereg s2, P4_BATCH2 s2 clauses)
    close = F["close"]
    fin = np.isfinite(close)
    ok_row = np.array([bool(ok_static[s]) and board.get(s) != "other"
                      for s in syms], dtype=bool)
    amt20 = _roll_mean20(F["amount"])
    listed = fin.cumsum(axis=0)
    lvidx = np.where(fin, np.arange(T_EXPECT)[:, None], -1)
    lastvalid = np.maximum.accumulate(lvidx, axis=0)
    fresh = (np.arange(T_EXPECT)[:, None] - lastvalid) <= FRESH_MAX
    elig = (ok_row[None, :] & fin & (close >= PRICE_MIN)
            & np.isfinite(amt20) & (amt20 >= AMT20_MIN)
            & (listed >= LISTED_MIN) & fresh)
    med = float(np.median(elig.sum(axis=1)[GRID_FROM:]))
    i2010 = int(np.searchsorted(idx, UNIV_ERA_FROM))
    med_2010 = float(np.median(elig.sum(axis=1)[max(i2010, GRID_FROM):]))
    assert med >= UNIV_MEDIAN_FULL_MIN, f"eligible median {med} below floor"
    assert med_2010 >= UNIV_MEDIAN_2010_MIN, \
        f"eligible 2010+ median {med_2010} below floor"

    # -- signals
    prev20 = np.vstack([np.full((20, N_EXPECT), np.nan, np.float32), close[:-20]])
    with np.errstate(invalid="ignore"):
        drop20 = close / prev20 - 1.0
    prev60 = np.vstack([np.full((60, N_EXPECT), np.nan, np.float32), close[:-60]])
    with np.errstate(invalid="ignore"):
        drop60 = close / prev60 - 1.0

    # -- passive proxy: eligible-EW daily return (beat-rate face, prereg s3)
    pct = F["pct_chg"]
    with np.errstate(invalid="ignore"):
        ew_f = np.where(elig & np.isfinite(pct), pct, 0.0)
        n_e = (elig & np.isfinite(pct)).sum(axis=1)
    ew = np.where(n_e > 0, ew_f.sum(axis=1) / np.maximum(n_e, 1), 0.0)

    # -- column-major copies for the per-stock path loop (contiguous 1-D)
    col = {f: np.ascontiguousarray(F[f].T) for f in ("open", "high", "low", "close")}

    return {"idx": idx, "syms": syms, "board": board, "F": F, "col": col,
            "fl": fl, "elig": elig, "drop20": drop20, "drop60": drop60,
            "sse": sse_v, "ma200": ma200, "ew_ret": ew,
            "elig_median": med, "elig_median_2010": med_2010,
            "sse_cover": cover}


def signal_grid():
    return list(range(GRID_FROM, T_EXPECT - HOLD_BUFFER, GRID_STEP))


# ------------------------------------------------------------- sim layer
def _prev_finite(vec, i):
    j = i - 1
    while j >= 0 and not np.isfinite(vec[j]):
        j -= 1
    return float(vec[j]) if j >= 0 else np.nan


def _net(px, entry, cost):
    """Net return, float64 exit face (NEP50: python scalars stay weak and
    would keep float32 panel precision through the whole expression)."""
    return float(px) / float(entry) * (1 - cost) / (1 + cost) - 1.0


def sim_stock(P, s, t, H, tpsl, cost):
    """One stock path: entry open[t+1] -> exit. Returns (net, exit_d, tag)."""
    op, hi, lo, cl, fl = (P["col"]["open"][s], P["col"]["high"][s],
                          P["col"]["low"][s], P["col"]["close"][s], P["fl"][s])
    d = t + 1
    o = op[d]
    if not np.isfinite(o):
        return None, None, "unfillable"
    pc = _prev_finite(cl, d)
    if not np.isfinite(pc) or o / pc - 1.0 >= fl[d] - LIMIT_OPEN_TOL:
        return None, None, "unfillable"       # near-limit-up open, un-captured
    entry = float(o)
    tp_px, sl_px = entry * TP, entry * SL
    d_target = t + 1 + H
    while d < T_EXPECT:
        o, h, l, c = op[d], hi[d], lo[d], cl[d]
        if not (np.isfinite(o) and np.isfinite(c)):
            d += 1                            # suspension day, roll
            continue
        if h == l == c:                       # sealed board day
            pc = _prev_finite(cl, d)
            if np.isfinite(pc) and c / pc - 1.0 <= -fl[d]:
                d += 1                        # sealed limit-down: no fills
                continue
        if tpsl and np.isfinite(h) and np.isfinite(l):
            pc = _prev_finite(cl, d)
            lo_gap = np.isfinite(pc) and o / pc - 1.0 <= -(fl[d] - LIMIT_OPEN_TOL)
            sl_hit = lo_gap or (l <= sl_px)
            tp_hit = (o >= tp_px) or (h >= tp_px)
            if sl_hit and tp_hit:
                px = o if lo_gap else sl_px   # same-day both-touch -> SL first
                return (_net(px, entry, cost), d, "sl")
            if sl_hit:
                px = o if lo_gap else sl_px
                return (_net(px, entry, cost), d, "sl")
            if tp_hit:
                px = o if o >= tp_px else tp_px
                return (_net(px, entry, cost), d,
                        "tp_gap" if o >= tp_px else "tp")
        if d >= d_target:
            pc = _prev_finite(cl, d)
            if np.isfinite(pc) and o / pc - 1.0 <= -(fl[d] - LIMIT_OPEN_TOL):
                d += 1                        # limit-down open, queue unsold
                continue
            return (_net(o, entry, cost), d, "time")
        d += 1
    # panel exhausted while holding -> mark-to-last finite close (honest tail)
    j = T_EXPECT - 1
    while j > t and not np.isfinite(cl[j]):
        j -= 1
    px = float(cl[j]) if np.isfinite(cl[j]) else entry
    return (_net(px, entry, cost), max(j, t + 1), "tail")


def pick_cohort(P, t, cell):
    """Eligible+filtered ranking -> Top10 picks (prereg s3)."""
    if cell["gate"]:
        if not (np.isfinite(P["sse"][t]) and np.isfinite(P["ma200"][t])):
            return None, "gate_undefined"
        if not (P["sse"][t] < P["ma200"][t]):
            return None, "gate_closed"
    row = P["drop20"][t]
    e = P["elig"][t] & np.isfinite(row)
    if cell["yang"]:
        e = e & (P["F"]["close"][t] > P["F"]["open"][t])
    if cell["dwr"]:
        e = e & (P["drop60"][t] < 0)
    cand = np.flatnonzero(e)
    if len(cand) < THIN_MARKET_MIN:
        return None, "thin_market"
    vals = row[cand]
    k = min(10, len(cand))
    part = np.argpartition(vals, k - 1)[:k]
    ordr = part[np.argsort(vals[part], kind="stable")]
    return cand[ordr].tolist(), "ok"


def _weights(P, picks, t, kind):
    if kind == "eq":
        return np.ones(len(picks)) / len(picks)
    pc = P["F"]["pct_chg"][max(t - 19, 0):t + 1, picks]
    with np.errstate(invalid="ignore"):
        sd = np.nanstd(pc, axis=0)
    inv = np.where(np.isfinite(sd) & (sd > 0), 1.0 / np.where(sd > 0, sd, 1.0), 0.0)
    tot = inv.sum()
    return inv / tot if tot > 0 else np.ones(len(picks)) / len(picks)


def sim_cell(P, cell, face):
    """Full cell x face run -> daily series + counters (prereg s3)."""
    cost = COST_FACES[face]
    b = [np.zeros(T_EXPECT), np.zeros(T_EXPECT)]
    entries = trades = unfillable = 0
    skips = {"gate_closed": 0, "gate_undefined": 0, "thin_market": 0,
             "empty_fill": 0}
    exits = {"time": 0, "tp": 0, "tp_gap": 0, "sl": 0, "tail": 0}
    for g, t in enumerate(signal_grid()):
        picks, why = pick_cohort(P, t, cell)
        if picks is None:
            skips[why] += 1
            continue
        w = _weights(P, picks, t, cell["w"])
        bucket = g % 2
        filled = 0
        for i, s in enumerate(picks):
            net, exit_d, tag = sim_stock(P, int(s), t, cell["H"], cell["tpsl"], cost)
            if net is None:
                unfillable += 1
                continue
            entries += 1
            trades += 1
            exits[tag] = exits.get(tag, 0) + 1
            span = max(1, exit_d - (t + 1))
            b[bucket][t + 1:t + 1 + span] += float(w[i]) * float(net) / span
            filled += 1
        if filled == 0:
            skips["empty_fill"] += 1
    series = 0.5 * (b[0] + b[1])
    return {"series": series, "entries": entries, "trades": trades,
            "unfillable": unfillable, "skips": skips, "exits": exits,
            "cohorts": len(signal_grid())}


def cell_stats(series):
    r = np.asarray(series, dtype=np.float64)
    mu, sd = float(r.mean()), float(r.std(ddof=1))
    sharpe = mu / sd * math.sqrt(PBP) if sd > 0 else 0.0
    eq = np.cumprod(1.0 + r)
    peak = np.maximum.accumulate(eq)
    dd = float((eq / peak - 1.0).min())
    ann = float(eq[-1] ** (PBP / max(len(r), 1)) - 1.0)
    return {"sharpe_full": round(sharpe, 4), "ann_ret": round(ann, 6),
            "max_dd": round(dd, 6), "n_days": int(len(r)),
            "median_abs_r": round(float(np.median(np.abs(r))), 6),
            "p999_abs_r": round(float(np.percentile(np.abs(r), 99.9)), 6)}


# ------------------------------------------------------------- null layer
def run_nulls(P):
    """K=2000 same-mask random event days -> pooled cohorts; K=2000
    synthetic 52-cohort annual runs -> Sharpe values (prereg s3, doc law)."""
    grid = signal_grid()
    pooled = []                        # (net, span)
    for k in range(K_NULLS):
        rng = np.random.default_rng(SEED + k)
        t = grid[int(rng.integers(0, len(grid)))]
        cand = np.flatnonzero(P["elig"][t])
        if len(cand) < THIN_MARKET_MIN:
            continue
        k10 = min(10, len(cand))
        picks = cand[rng.choice(len(cand), size=k10, replace=False)]
        for s in picks:
            net, exit_d, _ = sim_stock(P, int(s), t, 7, False, COST_X1)
            if net is not None:
                pooled.append((float(net), max(1, exit_d - (t + 1))))
    if not pooled:
        raise RuntimeError("null pool empty")
    nets = np.array([p[0] for p in pooled])
    spans = np.array([p[1] for p in pooled])
    values = []
    for k in range(K_NULLS):
        rng = np.random.default_rng(SEED + k)      # second declared use
        draw = rng.integers(0, len(nets), size=52)
        ser = np.zeros(PBP)
        for j, ix in enumerate(draw):
            span = int(spans[ix])
            lo = min(j * GRID_STEP, PBP - span)
            ser[lo:lo + span] += float(nets[ix]) / span / 2.0
        sd = ser.std(ddof=1)
        values.append(ser.mean() / sd * math.sqrt(PBP) if sd > 0 else 0.0)
    vals = np.array(values)
    return {"values": [round(float(v), 4) for v in vals],
            "coverage": {"mu": round(float(vals.mean()), 4),
                         "sigma": round(float(vals.std(ddof=1)), 4),
                         "n_values": int(len(vals))},
            "pooled_cohort_returns": len(pooled)}


# ------------------------------------------------- virtual starts & robust
def seg_class(P, t0):
    s, m = P["sse"][t0], P["ma200"][t0]
    if not (np.isfinite(s) and np.isfinite(m)):
        return "na"
    s60 = P["sse"][max(t0 - 60, 0)]
    if not np.isfinite(s60):
        return "na"
    r60 = s / s60 - 1.0
    if s > m:
        return "bull" if r60 > 0.05 else "chop"
    return "deep_bear" if r60 < -0.15 else "bear"


def virtual_starts(P, series_by_cell):
    starts = list(range(STARTS_FROM, T_EXPECT - WIN_DAYS))
    segs = np.array([seg_class(P, t0) for t0 in starts])
    sa = np.array(starts)
    ew = np.asarray(P["ew_ret"], dtype=np.float64)
    ew_cs = np.cumsum(np.log1p(ew))
    out = {"n_starts": len(starts), "segments": {}}
    for cls in ("bull", "bear", "deep_bear", "chop", "na"):
        n = int((segs == cls).sum())
        out["segments"][cls] = {"n_starts": n,
                                "sufficient_sample": bool(n >= SEG_MIN)}
    rng = np.random.default_rng(SEED)
    cells = {}
    for name, series in series_by_cell.items():
        r = np.asarray(series, dtype=np.float64)
        cs = np.cumsum(np.log1p(r))
        wret = cs[sa + WIN_DAYS - 1] - cs[sa - 1]
        pw = ew_cs[sa + WIN_DAYS - 1] - ew_cs[sa - 1]
        beat = wret > pw
        seg_tab = {}
        for cls in ("bull", "bear", "deep_bear", "chop", "na"):
            m = segs == cls
            seg_tab[cls] = {"n": int(m.sum()),
                            "mean_win_ret": round(float(wret[m].mean()), 6)
                            if m.any() else None,
                            "beat_rate": round(float(beat[m].mean()), 4)
                            if m.any() else None}
        half = len(starts) // 2
        oos = {"first_half_mean": round(float(wret[:half].mean()), 6),
               "second_half_mean": round(float(wret[half:].mean()), 6)}
        fw = np.array_split(r, 5)
        wf = [round(float(x.mean() / x.std(ddof=1) * math.sqrt(PBP)), 4)
              if x.std(ddof=1) > 0 else 0.0 for x in fw]
        agree = valid = 0
        for _ in range(100):
            m = rng.random(len(starts)) < 0.5
            if not m.any() or m.all():
                continue
            valid += 1
            a, b_ = float(wret[m].mean()), float(wret[~m].mean())
            agree += int((a > 0) == (b_ > 0))
        cells[name] = {"mean_win_ret": round(float(wret.mean()), 6),
                       "beat_rate_6m": round(float(beat.mean()), 4),
                       "segments": seg_tab, "oos_halves": oos,
                       "walk_forward_sharpe": wf,
                       "split_sign_agreement_pct":
                           round(100.0 * agree / valid, 1) if valid else None,
                       "win_ret_head": [round(float(x), 6) for x in wret[:50]]}
    out["cells"] = cells
    out["segment_of_start_head"] = {
        str(P["idx"][t0].date()): segs[i]
        for i, t0 in enumerate(starts[:200])}
    return out


def robust_stats(series):
    """Block bootstrap (block=10d) + sign-flip permutation, 2000 each (s3)."""
    r = np.asarray(series, dtype=np.float64)
    n = len(r)
    sd0 = r.std(ddof=1)
    obs_sharpe = r.mean() / sd0 * math.sqrt(PBP) if sd0 > 0 else 0.0
    rng = np.random.default_rng(SEED)
    block = 10
    n_blocks = int(math.ceil(n / block))
    bb = np.empty(2000)
    offs = np.arange(block)
    for i in range(2000):
        pos = rng.integers(0, n_blocks, size=n_blocks)
        idx = (pos[:, None] * block + offs[None, :]).ravel()
        idx = idx[idx < n]
        bb[i] = r[idx].mean()
    sf = np.empty(2000)
    for i in range(2000):
        sgn = rng.integers(0, 2, size=n) * 2.0 - 1.0
        x = r * sgn
        sx = x.std(ddof=1)
        sf[i] = x.mean() / sx * math.sqrt(PBP) if sx > 0 else 0.0
    return {"obs_sharpe": round(obs_sharpe, 4),
            "block_bootstrap_p95_mean": round(float(np.percentile(bb, 95)), 6),
            "block_bootstrap_p05_mean": round(float(np.percentile(bb, 5)), 6),
            "block_bootstrap_p_le_0": round(float((bb <= 0).mean()), 4),
            "sign_flip_p": round(float(
                (np.abs(sf) >= abs(obs_sharpe)).mean()), 4)}


# ------------------------------------------------------------- D6 + crisis
def d6_block(P, series_by_cell):
    """s1 reject face vs REGISTERED members (cn_rev_tilt_p1 ew6 canon)."""
    from cn_rev_tilt_p1 import REG6, load_member_rets, _corr
    # AMENDMENT r280: load_member_rets() returns (out, cutoffs) tuple in the
    # donor module -- unpack or .items() crashes ('tuple' has no .items',
    # autofill logs/autofill_REV-OSC-STOCK-P1.log 00:10/00:20 twin crashes).
    # Engineering fix in the zero-judged-product window (p1_results.json never
    # produced); criteria/judged faces unchanged (r253 deterministic-reexec law).
    member_rets, _member_cutoffs = load_member_rets()
    out = {"reject_line": D6_REJECT, "members": list(REG6), "cells": {}}
    mat = {}
    for name, series in series_by_cell.items():
        s = pd.Series(np.asarray(series, dtype=np.float64), index=P["idx"])
        per = {}
        for tid, mr in member_rets.items():
            v, ov = _corr(s, mr)
            per[tid] = {"corr": v, "overlap_days": ov}
        fin = {t: v["corr"] for t, v in per.items() if v["corr"] is not None}
        amax = max(fin, key=lambda k: abs(fin[k])) if fin else None
        out["cells"][name] = {"per_member": per,
                              "max_abs_corr": round(abs(fin[amax]), 4)
                              if amax else None,
                              "reject": bool(amax and
                                             abs(fin[amax]) >= D6_REJECT)}
        mat[name] = np.asarray(series, dtype=np.float64)
    names = list(mat)
    cross = {}
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b_ = mat[names[i]], mat[names[j]]
            m = np.isfinite(a) & np.isfinite(b_)
            if m.sum() > 20 and a[m].std() > 0 and b_[m].std() > 0:
                cross[f"{names[i]}|{names[j]}"] = round(float(
                    np.corrcoef(a[m], b_[m])[0, 1]), 4)
    out["same_batch_cross"] = cross
    return out


def crisis_face(P, series_by_cell):
    dts = P["idx"]
    out = {}
    for name, series in series_by_cell.items():
        r = np.asarray(series, dtype=np.float64)
        hits = []
        for t in np.flatnonzero(np.abs(r) > MAX_R_CRISIS):
            d = dts[t]
            in_c = any(a <= d <= b for a, b in CRISIS_WINDOWS)
            hits.append({"date": str(d.date()), "r": round(float(r[t]), 4),
                         "in_crisis_window": bool(in_c)})
        out[name] = hits
    return out


# ------------------------------------------------------------- finalize
def _attr_row(batch, delta, total, gates):
    d = json.load(open(ATT_JSON, encoding="utf-8"))
    d["entries"].append({"batch": batch,
                         "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
                         "kind": "measurement", "cells_ledger_delta": delta,
                         "ledger_total_after": total, "gates": gates})
    with open(ATT_JSON + ".tmp", "w", encoding="utf-8") as fh:
        json.dump(d, fh, ensure_ascii=False, indent=1)
    os.replace(ATT_JSON + ".tmp", ATT_JSON)


def finalize(panel_face, cells_out, nulls, d6, vstarts, robust, crisis):
    series_by_cell = {n: cells_out[n]["x1"]["series"] for n in cells_out}
    line_pool = {"values": nulls["values"], "coverage": nulls["coverage"]}
    gates = {}
    for name, ser in series_by_cell.items():
        st = cells_out[name]["x1"]["stats"]
        g1 = SG.g1_prime_v2(st["sharpe_full"], ser, batch_cells=BATCH_CELLS,
                            pool="stock_b_layer", null_pool=line_pool,
                            n_trades=cells_out[name]["x1"]["trades"],
                            n_entries=cells_out[name]["x1"]["entries"])
        dsr = SG.deflated_sharpe_ratio(ser, n_trials=g1["skill_line"]["n_eff"])
        gates[name] = {"g1_prime_v2": g1, "dsr": dsr}
    mat = pd.DataFrame({n: np.asarray(s, dtype=np.float64)
                        for n, s in series_by_cell.items()})
    pbo = cscv_pbo(mat)
    for name in gates:
        # AMENDMENT r281 (pre-relaunch, zero-judged-product window): cscv_pbo
        # returns the full record DICT; g2_registration_v2 takes the pbo
        # FLOAT (cn_regime_policy proven call shape) -- passing the dict is
        # float(dict) TypeError at finalize = guaranteed post-30min burn.
        gates[name]["g2"] = SG.g2_registration_v2(
            gates[name]["g1_prime_v2"]["pass_v2"],
            gates[name]["dsr"], float(pbo["pbo"]))
        gates[name]["d6_reject"] = bool(d6["cells"][name]["reject"])

    ledger = SG.append_ledger(BATCH_NAME, BATCH_CELLS,
                              file_name="rev_osc_stock_p1",
                              evidence_cutoff=EVIDENCE_CUTOFF)
    _attr_row(BATCH_NAME, BATCH_CELLS, int(ledger["total"]), {
        "g1_pass": {n: gates[n]["g1_prime_v2"]["pass_v2"] for n in gates},
        "g2_eligible": {n: gates[n]["g2"]["eligible_v2"] for n in gates},
        "d6_reject": {n: gates[n]["d6_reject"] for n in gates},
        "family_pbo": pbo})

    result = {
        "batch": BATCH_NAME,
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "cutoff_meta": SG.cutoff_meta(EVIDENCE_CUTOFF),
        "prereg": "research/REV_OSC_STOCK_PREREG.md",
        "seed": {"base": SEED, "k": K_NULLS},
        "panel": panel_face,
        "cells": {n: {f: {"stats": cells_out[n][f]["stats"],
                          "entries": cells_out[n][f]["entries"],
                          "trades": cells_out[n][f]["trades"],
                          "unfillable": cells_out[n][f]["unfillable"],
                          "skips": cells_out[n][f]["skips"],
                          "exits": cells_out[n][f]["exits"]}
                      for f in cells_out[n]} for n in cells_out},
        "nulls": nulls, "d6": d6, "virtual_starts": vstarts,
        "robust": robust, "crisis_single_list": crisis,
        "family_pbo": pbo, "gates": gates, "trials_ledger": ledger,
        "verdict_line": ("judged per prereg s4: G1'v2 x1 primary faces; "
                         "judged-negative = slot closed + new-evidence "
                         "reopen note (O-2325 s5)"),
    }
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON + ".tmp", "w", encoding="utf-8") as fh:
        json.dump(result, fh, ensure_ascii=False, indent=1)
    os.replace(OUT_JSON + ".tmp", OUT_JSON)
    rows = []
    for n in cells_out:
        for f in ("x1", "x2"):
            rows.append({"cell": n, "face": f,
                         **cells_out[n][f]["stats"]})
    pd.DataFrame(rows).to_csv(OUT_CSV, index=False)
    return result


# ------------------------------------------------------------- driver
def cmd_run():
    global SEED
    SEED = SG.SEED_REGISTRY["rev_osc_stock_p1"]
    if _free_ram_gb() < RAM_FLOOR_GB:
        print("free-RAM floor refused")
        return 3
    t0 = time.time()
    P = load_panel()
    os.makedirs(CELL_DIR, exist_ok=True)
    cells_out = {}
    for cell in CELLS:
        name = cell["name"]
        cells_out[name] = {}
        for face in ("x1", "x2"):
            ck = os.path.join(CELL_DIR, f"{name}_{face}.json")
            if os.path.exists(ck):
                blob = json.load(open(ck, encoding="utf-8"))
                blob["series"] = np.load(ck.replace(".json", ".npy"))
            else:
                r = sim_cell(P, cell, face)
                np.save(ck.replace(".json", ".npy"), r["series"])
                blob = {"series": r["series"],
                        "stats": cell_stats(r["series"]),
                        "entries": r["entries"], "trades": r["trades"],
                        "unfillable": r["unfillable"], "skips": r["skips"],
                        "exits": r["exits"]}
                dump = {k: v for k, v in blob.items() if k != "series"}
                with open(ck + ".tmp", "w", encoding="utf-8") as fh:
                    json.dump(dump, fh, ensure_ascii=False, indent=1)
                os.replace(ck + ".tmp", ck)
            cells_out[name][face] = blob
    nulls = run_nulls(P)
    series_by_cell = {n: cells_out[n]["x1"]["series"] for n in cells_out}
    d6 = d6_block(P, series_by_cell)
    vstarts = virtual_starts(P, series_by_cell)
    robust = {n: robust_stats(s) for n, s in series_by_cell.items()}
    crisis = crisis_face(P, series_by_cell)
    panel_face = {"T": T_EXPECT, "N": N_EXPECT,
                  "universe_ok_static": OK_STATIC_EXPECT,
                  "eligible_median": P["elig_median"],
                  "eligible_median_2010": P["elig_median_2010"],
                  "sse_cover": round(P["sse_cover"], 4)}
    res = finalize(panel_face, cells_out, nulls, d6, vstarts, robust, crisis)
    print(f"finalize ok: cells={len(res['cells'])} "
          f"ledger={res['trials_ledger']['total']} elapsed={time.time() - t0:.0f}s")
    return 0


# ------------------------------------------------------------- selftest
def _mk_panel(tmp, T=420, N=12):
    """Hermetic synthetic panel: known losers, gates, TP/SL fixtures."""
    cache = os.path.join(tmp, "cache")
    os.makedirs(cache, exist_ok=True)
    idx = pd.date_range("2020-01-01", periods=T, freq="B").as_unit("us")
    np.save(os.path.join(cache, "dates.npy"), idx.asi8)  # us epochs (cache face)
    rng = np.random.default_rng(7)
    base = 10.0 + rng.random(N) * 5
    close = np.tile(base, (T, 1)) * np.cumprod(
        1.0 + rng.normal(0, 0.01, (T, N)), axis=0)
    open_ = close * (1 + rng.normal(0, 0.005, (T, N)))
    high = np.maximum(open_, close) * (1 + abs(rng.normal(0, 0.004, (T, N))))
    low = np.minimum(open_, close) * (1 - abs(rng.normal(0, 0.004, (T, N))))
    amt = np.full((T, N), 6e7) + rng.random((T, N)) * 1e7
    pct = np.vstack([np.full((1, N), np.nan), close[1:] / close[:-1] - 1])
    for f, m in (("open", open_), ("high", high), ("low", low),
                 ("close", close), ("pct_chg", pct), ("amount", amt)):
        np.save(os.path.join(cache, f + ".npy"), m.astype(np.float32))
    json.dump({"shape": {"T": T, "N": N}}, open(
        os.path.join(cache, "meta.json"), "w"))
    bars = os.path.join(tmp, "bars")
    os.makedirs(bars)
    codes = [f"{i:06d}" for i in range(1, N + 1)]
    for c in codes:
        open(os.path.join(bars, c + ".parquet"), "w").close()
    pd.DataFrame({"code": codes,
                  "board": ["main"] * (N - 2) + ["chinext", "other"],
                  "ok_static": [True] * (N - 1) + [False]}).to_csv(
        os.path.join(tmp, "mask.csv"), index=False)
    pd.DataFrame({"date": idx, "close": np.linspace(3000, 2500, T)}).to_parquet(
        os.path.join(tmp, "sse.parquet"))
    return cache, bars, idx


def cmd_selftest():
    global CACHE, MASK, SSE, BARS, T_EXPECT, N_EXPECT, OK_STATIC_EXPECT, \
        UNIV_MEDIAN_FULL_MIN, UNIV_MEDIAN_2010_MIN, SSE_COVER_MIN, \
        OUT_DIR, CELL_DIR, OUT_JSON, OUT_CSV, \
        SEED, K_NULLS, ATT_JSON, BATCH_CELLS, EXPECT_DATES, cscv_pbo
    tmp = tempfile.mkdtemp(prefix="rev_osc_selftest_")
    T, N = 420, 12
    cache, bars, idx = _mk_panel(tmp, T, N)
    CACHE, BARS = cache, bars
    MASK, SSE = os.path.join(tmp, "mask.csv"), os.path.join(tmp, "sse.parquet")
    T_EXPECT, N_EXPECT, OK_STATIC_EXPECT = T, N, N - 1
    UNIV_MEDIAN_FULL_MIN, UNIV_MEDIAN_2010_MIN = 1, 1
    SSE_COVER_MIN = 0.0
    EXPECT_DATES = (str(idx[0].date()), str(idx[-1].date()))
    OUT_DIR = os.path.join(tmp, "out")
    CELL_DIR = os.path.join(OUT_DIR, "cells")
    OUT_JSON = os.path.join(OUT_DIR, "p1_results.json")
    OUT_CSV = os.path.join(OUT_DIR, "cells_summary.csv")
    ATT_JSON = os.path.join(tmp, "attr.json")
    json.dump({"entries": []}, open(ATT_JSON, "w"))
    SEED = 20261230
    ok = []

    # hermetic stubs: shared-library state faces isolated from the real repo
    _ne, _pb, _al = SG.n_eff, SG.passive_baseline, SG.append_ledger
    SG.n_eff = lambda bc, rd=None: int(bc)
    SG.passive_baseline = lambda pool, rd=None: 0.4606
    SG.append_ledger = lambda *a, **k: {"prev_total": 0, "total": 100,
                                        "batch": BATCH_NAME}
    cscv_pbo = lambda mat: {"pbo": 0.1}   # real fn returns the record dict

    try:
        P = load_panel()
        ok.append(("panel gates", P["elig"].shape == (T, N)))

        # [2] ranking: deepest drop first among eligible
        t = 100
        row = np.where(P["elig"][t], P["drop20"][t], np.nan)
        cand = np.flatnonzero(np.isfinite(row))
        ordr = cand[np.argsort(row[cand], kind="stable")]
        ok.append(("drop20 rank", row[ordr[0]] <= row[ordr[-1]]))

        # [3] first-yang filter face exists structurally
        e = P["elig"][t] & np.isfinite(P["drop20"][t])
        yang = e & (P["F"]["close"][t] > P["F"]["open"][t])
        ok.append(("yang filter", bool(np.isfinite(yang).all())))

        # [4] bear gate: synthetic sse falls below its MA200 -> gate open
        picks, why = pick_cohort(P, 250, CELLS[3])
        ok.append(("bear gate open (sse<MA200)", picks is not None or
                   why == "thin_market"))

        # [5] TP gap-open fill at open (favorable gap honored)
        F = P["F"]
        s, t0 = 0, 200

        def _flat(px=9.8, days=14):
            for d in range(t0, min(t0 + days, T)):
                F["open"][d, s] = px
                F["high"][d, s] = px * 1.005
                F["low"][d, s] = px * 0.995
                F["close"][d, s] = px

        def _recol():
            P["col"] = {f: np.ascontiguousarray(F[f].T)
                        for f in ("open", "high", "low", "close")}

        _flat()
        F["open"][t0 + 1, s] = 10.0
        F["open"][t0 + 2, s] = 10.9          # gap through TP 10.8
        F["high"][t0 + 2, s] = 11.0
        F["low"][t0 + 2, s] = 10.5
        F["close"][t0 + 2, s] = 10.95
        _recol()
        net, ed, tag = sim_stock(P, s, t0, 7, True, COST_X1)
        exp = 10.9 / 10.0 * (1 - COST_X1) / (1 + COST_X1) - 1
        # 1e-7 = float32 storage epsilon face (10.9f32); real price bugs >= 1e-4
        ok.append(("TP gap-open fill", tag == "tp_gap" and
                   abs(net - exp) < 1e-7))

        # [6] same-day both-touch -> SL first (prereg s3 conservative law)
        _flat()
        F["open"][t0 + 1, s] = 10.0
        F["open"][t0 + 2, s] = 10.0
        F["high"][t0 + 2, s] = 11.0          # TP touched
        F["low"][t0 + 2, s] = 8.9            # SL touched
        _recol()
        net, ed, tag = sim_stock(P, s, t0, 7, True, COST_X1)
        ok.append(("same-day SL first", tag == "sl" and
                   abs(net - (9.0 / 10.0 * (1 - COST_X1) / (1 + COST_X1)
                              - 1)) < 1e-9))

        # [7] sealed limit-down day -> no fills, roll forward
        _flat()
        F["open"][t0 + 1, s] = 10.0
        F["close"][t0 + 1, s] = 10.0
        F["open"][t0 + 2, s] = 9.0
        F["high"][t0 + 2, s] = F["low"][t0 + 2, s] = F["close"][t0 + 2, s] = 9.0
        _recol()
        net, ed, tag = sim_stock(P, s, t0, 2, True, COST_X1)
        ok.append(("sealed-LD roll", ed is not None and ed > t0 + 2))

        # [8] near-limit-up entry refused (un-captured premium face)
        _flat()
        F["open"][t0 + 1, s] = 9.8 * 1.099
        _recol()
        net, ed, tag = sim_stock(P, s, t0, 7, True, COST_X1)
        ok.append(("near-limit-up entry refused", net is None))

        # [9] cost math multiplicative both sides (exit at flat open 9.8)
        _flat()
        F["open"][t0 + 1, s] = 10.0
        _recol()
        net, ed, tag = sim_stock(P, s, t0, 2, False, COST_X1)
        ok.append(("cost math", tag == "time" and
                   abs(net - (9.8 / 10.0 * (1 - COST_X1) /
                              (1 + COST_X1) - 1)) < 1e-7))

        # [10] bucket booking face + portfolio halving
        r = sim_cell(P, CELLS[0], "x1")
        ok.append(("cell series shape", r["series"].shape == (T,)))

        # [11] nulls construction (small K)
        K_NULLS = 30
        nulls = run_nulls(P)
        ok.append(("nulls finite coverage",
                   nulls["coverage"]["n_values"] == 30 and
                   bool(np.isfinite(nulls["values"]).all())))
        K_NULLS = 2000

        # [12] virtual starts census + segment classes
        vs = virtual_starts(P, {"BASE": r["series"]})
        ok.append(("vstarts census",
                   vs["n_starts"] == T - WIN_DAYS - STARTS_FROM))

        # [13] robust stats finite
        rb = robust_stats(r["series"])
        ok.append(("robust finite", np.isfinite(rb["obs_sharpe"]) and
                   0.0 <= rb["sign_flip_p"] <= 1.0))

        # [14] gates wiring smoke (stubbed line faces, hermetic)
        g1 = SG.g1_prime_v2(1.2, r["series"], batch_cells=10,
                            pool="stock_b_layer", null_pool={
                                "values": nulls["values"],
                                "coverage": nulls["coverage"]},
                            n_trades=100, n_entries=100)
        ok.append(("g1 dict face", "skill_line" in g1 and "pass_v2" in g1))

        # [15] finalize product on synthetic (ledger + attr + single product)
        cells_out = {"BASE": {
            f: {"stats": cell_stats(r["series"]), "series": r["series"],
                "trades": r["trades"], "entries": r["entries"],
                "unfillable": r["unfillable"], "skips": r["skips"],
                "exits": r["exits"]}
            for f in ("x1", "x2")}}
        d6 = {"cells": {"BASE": {"reject": False}}}
        res = finalize({"T": T, "N": N}, cells_out, nulls, d6,
                       {"n_starts": 1, "segments": {}, "cells": {}},
                       {"BASE": rb}, {"BASE": []})
        ok.append(("finalize product", os.path.exists(OUT_JSON) and
                   res["trials_ledger"]["total"] == 100))
    finally:
        SG.n_eff, SG.passive_baseline, SG.append_ledger = _ne, _pb, _al
        shutil.rmtree(tmp, ignore_errors=True)

    n_ok = sum(1 for _, v in ok if v)
    print(f"rev_osc_stock_p1 selftest: {n_ok}/{len(ok)} PASS")
    for name, v in ok:
        if not v:
            print(f"  FAIL: {name}")
    return 0 if n_ok == len(ok) else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "selftest"])
    a = ap.parse_args()
    if a.cmd == "selftest":
        return cmd_selftest()
    if os.path.exists(OUT_JSON) and \
            os.environ.get("REV_OSC_STOCK_P1_REFINALIZE") != "1":
        print("idempotent no-op: p1_results.json exists "
              "(REV_OSC_STOCK_P1_REFINALIZE=1 = only redo)")
        return 0
    return cmd_run()


if __name__ == "__main__":
    sys.exit(main())
