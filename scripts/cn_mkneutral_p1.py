"""CN_MKTNEUTRAL_P1 runner -- A股市场中性批 (T-87 s2 queue #5,
market-neutral stock-quintile x IC constant-short beta-hedge face).

Laws frozen in research/CN_MKTNEUTRAL_PREREG.md @commit 3c71ddb4 (R99:
freeze precedes runner build precedes ANY run; seed
SEED_REGISTRY['cn_mkneutral_p1'] = 20279300 registered at the freeze
commit R303, band 20279300..20281300 construction-clean; N bill 2004 =
4 judged cells x1 judged face + 2000 own-nulls; x1/x3 = disclosure
columns not in N, CN family precedent CN_SECTOR_LEADER_P1):

  panel   Money02 cache p1c_stock (T=8792 x N=5222 float32, close/amount
          read-only, cutoff 2026-09-22) + bars parquet for the universe
          re-derive (probe-verbatim per-file method; count + skip ledger
          gated vs the frozen SECTOR probe -- identical formula, identical
          inputs) + data/futures_daily/IC.csv (2353 rows 2017-01-17 ..
          2026-09-24, truncated at cutoff, OHLC-only signal input,
          oi/settle excluded per CTA_P1 s2 case) + b_layer_mask ok_static
          face. Cross-check results/_r299bma_cache_crosscheck.json gated
          in place (0 mismatch); cache meta stamp gated == actual asset
          meta '2026-09-23 18:12:59' (r299 kenglu).
  window  joint window = [2017-01-17 (IC first bar), 2026-09-22 (cutoff)]
          on the stock calendar (calendar-primary face); IC rows past the
          cutoff dropped (2 bars, disclosed); IC-absent days = carry mark
          (r_ic = 0 that day, audit counted); IC bars absent from the
          stock calendar dropped (calendar-primary, disclosed).
  signal  REV_W(t) = -(C_t/C_{t-W} - 1), W in {20, 60}; cross-section
          descending REV; basket = bottom-quintile losers
          n_k = ceil(n_valid_k / 5) (~621 of 3106, EW).
  rebal   20td schedule, t_k = joint day k*20; signal at t_k close ->
          execution t_k+1. Entry anchor = close[t_k]: the prereg's own
          daily close-close accounting ("t+1 开盘调仓" x "篮日收益 =
          close-close EW") implies this V0 anchor approximation (the
          overnight gap of the incoming basket is not separately
          modeled, disclosed in batch JSON). Basket / lots / beta frozen
          within a period.
  hedge   constant-short IC leg (zero signal, zero direction claim):
          target notional = beta_k x 0.8 x NAV; lots = round(target /
          (ic_open x mult 200)) signed negative (short, futures_runner
          semantics); margin = |lots| x mult x px x 0.14 with equity
          budget gate (shrink-lot loop, futures_runner law); open beyond
          prev-close +/-12% -> no new position that day (carry old lots,
          audit); IC-absent execution day -> carry. Beta policies:
          MN-*-BETA = rolling-60d intercept OLS of basket returns on IC
          returns (known at signal close), truncated [0.5, 1.5];
          MN-*-H1 = 1.0 frozen. OLS pairs < 30 -> beta = 1.0 fallback
          (early-window face, audit counted).
  nav     daily r = 0.8 x r_basket - h x r_ic - cost / NAV_prev;
          h = lots-implied actual notional / NAV at execution, constant
          within the period (V0: within-period price-drift second-order
          term not booked, disclosed); NAV0 = 1e8 CNY (engineering
          freeze: institutional mid scale, lot-rounding noise < 1%;
          prereg leaves scale to the runner -- disclosed); idle cash 0%
          (V0 conservative, CTA_P1 precedent).
  costs   stock leg: V2 single source, per-trade direct face -- vectorized
          pointwise-equal twin of alloc_backtest.side_cost_v2 (selftest
          contract leg, incl. the x2 = 2x V2 pointwise identity);
          x2 judged face doubles every V2 component; futures leg:
          per-lot (fee_lot 34.6 + 1 tick x mult) x cost multiplier on
          |d_lots|; both legs same multiplier (prereg cost clause).
  nulls   RANDOM_LARGE_SAMPLE_LAW s3 same-mask face: K=2000 draws per
          cell, each draw = uniform random n_k-of-3106 basket per period,
          same rebalance schedule / execution / costs(x2) / hedge
          machinery (random-basket beta OLS included = the
          beta-drift-stripped null carrier); rng seed SEED+k; 8 shards
          x 250 npy checkpoints; own-null pool per cell.
  starts  census virtual starts [200, T_j - 126), 126d windows, beat vs
          unhedged_ew_universe proxy; 4 segment classes (sse/ma200
          face); segment n < 500 = insufficient-sample honest note;
          >= 100 random train/val splits + walk-forward 5 folds (s2.3).
  sobol   s2.2 space-filling descriptive leg: N=500 draws over
          (REV W in {10,20,40,60,120}) x (beta window in {40,60,120}) x
          (beta cap in {1.25,1.5,2.0}), x1 face, scramble seed-sequence
          default_rng([SEED, 2000]); description columns only -- NO
          N_eff, NO gates, NO survivorship claims.
  gates   G1'v2 per cell (batch_cells=2004, pool='stock_b_layer',
          null_pool=own, F6 dual trade gate: n_trades = rebalance count,
          n_entries = member change events) + DSR raw x2 + family PBO
          (cscv CSCV-8 over the 4-cell x2 matrix) + g2_registration_v2;
          batch disclosure: ann > 0 AND OOS(>=2025-01-01) > 0 AND maxDD
          >= -35% AND no crash year (calendar-year return <= -30%,
          operationalization of 无崩年, disclosed).
  audit   hedge machinery audit: beta list/dist, fallback/blocked/absent
          counts, lots stats, margin usage peak, roll-day proxy list
          (|r_ic| > 3 x trailing sigma20 excluding the day itself;
          contract-level data absent in V0 -- proxy face, disclosed),
          carry days, zero-finite basket days, cost split, turnover.
  ledger  science_gates.append_ledger single-count (prev-echo guard,
          REV_OSC r259 face); gate_attrition measurement row (entries
          -list face per r248 law).

Products (prereg s6): results/cn_mkneutral/p1_results.json (top
evidence_cutoff + cutoff_meta + panel/IC faces + hedge audit + cells
both faces + nulls + D6 + virtual starts + splits + robust + gates +
ledger + passive baselines + Sobol block + disclosures) +
cells/<cell>_<face>.json|.npy + nulls/<cell>_shard<k>.npy +
sobol/shard<k>.npy + cells_summary.csv.

Usage: run | selftest   (exit 0 ok; 2 = fail-closed gate refusal; 3 = RAM
floor)
"""
import argparse
import glob
import hashlib
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
from screening.pbo import cscv_pbo               # family PBO CSCV-8
from alloc_backtest import side_cost_v2, side_cost_x2, FEE  # V2 single source
from knowledge.rules import (SLIPPAGE_TIER_2BP, SLIPPAGE_TIER_5BP,
                             SLIPPAGE_TIER_10BP, ADV20_TIER_2BP_YUAN,
                             ADV20_TIER_5BP_YUAN)
from engine.futures_runner import FUT_META, yearly_returns

BARS = os.path.join(ROOT, "Money02", "data", "bars")
CACHE = os.path.join(ROOT, "Money02", "data", "cache", "p1c_stock")
MASK = os.path.join(ROOT, "data", "fundamental", "b_layer_mask.csv")
SSE = os.path.join(ROOT, "Money02", "data", "index", "sse.parquet")
IC_CSV = os.path.join(ROOT, "data", "futures_daily", "IC.csv")
SECTOR_PROBE = os.path.join(ROOT, "results", "cn_sector_leader_probe.json")
XCC_JSON = os.path.join(ROOT, "results", "_r299bma_cache_crosscheck.json")
OUT_DIR = os.path.join(ROOT, "results", "cn_mkneutral")
CELL_DIR = os.path.join(OUT_DIR, "cells")
NULL_DIR = os.path.join(OUT_DIR, "nulls")
SOBOL_DIR = os.path.join(OUT_DIR, "sobol")
OUT_JSON = os.path.join(OUT_DIR, "p1_results.json")
OUT_CSV = os.path.join(OUT_DIR, "cells_summary.csv")
ATT_JSON = os.path.join(ROOT, "results", "gate_attrition.json")

EVIDENCE_CUTOFF = "2026-09-22"
IC_FIRST_BAR = "2017-01-17"
IC_LAST_BAR_RAW = "2026-09-24"          # raw file last bar (pre-truncation)
IC_ROWS_EXPECT = 2353
N_FILES_EXPECT = 5222
UNIVERSE_EXPECT = 3106
CACHE_STAMP_EXPECTED = "2026-09-23 18:12:59"   # ACTUAL asset meta (r299 kenglu)
BATCH_NAME = "CN_MKTNEUTRAL_P1"
BATCH_CELLS = 2004                     # 4 judged cells x1 + 2000 nulls
K_NULLS = 2000
NULL_SHARDS = 8
SOBOL_N = 500
SOBOL_SHARDS = 10
SOBOL_DRAW_BALANCE = 512                # power-of-2 balance, first 500 used
PBP = 252
SEED = None                            # filled from SG.SEED_REGISTRY at run
MIN_ROWS = 500
MIN_AMT20 = 3e7
REV_LEAD = 120                          # max sobol W lookback lead rows
REB = 20                                # rebalance period (frozen)
BETA_WIN = 60                           # rolling OLS window
BETA_MIN_PAIRS = 30                      # fallback threshold
BETA_CAP = 1.5                          # truncation [0.5, 1.5]
BETA_FLOOR = 0.5
NAV0 = 1.0e8                            # CNY, engineering freeze (disclosed)
STOCK_LEG = 0.8                         # stock leg fraction of NAV
CASH_LEG = 0.2                          # cash fraction (margin + buffer)
IC = FUT_META["IC"]                     # margin 0.14 mult 200 fee 34.6
                                       # tick 0.2 limit 0.12 (frozen table)
WIN_DAYS = 126
STARTS_FROM = 200
SEG_MIN = 500
OOS_FROM = np.datetime64("2025-01-01")
D6_REJECT = 0.7
CRASH_YEAR = -0.30                      # operationalization of 无崩年
RAM_FLOOR_GB = 16.0
ROLL_SIGMA_N = 3.0                      # roll-day proxy threshold (sigma)
ROLL_WIN = 20

SOBOL_W_GRID = (10, 20, 40, 60, 120)
SOBOL_BW_GRID = (40, 60, 120)
SOBOL_CAP_GRID = (1.25, 1.5, 2.0)

CELLS = [
    {"name": "MN-REV20-BETA", "W": 20, "beta_mode": "beta"},
    {"name": "MN-REV60-BETA", "W": 60, "beta_mode": "beta"},
    {"name": "MN-REV20-H1",  "W": 20, "beta_mode": "h1"},
    {"name": "MN-REV60-H1",  "W": 60, "beta_mode": "h1"},
]
CELL_NAMES = [c["name"] for c in CELLS]


def _free_ram_gb():
    try:
        import psutil
        return psutil.virtual_memory().available / 1e9
    except Exception:
        return RAM_FLOOR_GB + 1.0        # psutil absent -> guard off (disclosed)


def gate_refuse(msg):
    print(f"GATE-REFUSE(exit2): {msg}")
    return 2


# ------------------------------------------------------------------ costs
def _slip_vec(adv_arr):
    """Vectorized krules.cost_v2_slippage (tier table + NaN -> 10bp)."""
    a = np.asarray(adv_arr, dtype=np.float64)
    slip = np.where(np.isnan(a), SLIPPAGE_TIER_10BP,
                    np.where(a >= ADV20_TIER_2BP_YUAN, SLIPPAGE_TIER_2BP,
                             np.where(a >= ADV20_TIER_5BP_YUAN,
                                      SLIPPAGE_TIER_5BP,
                                      SLIPPAGE_TIER_10BP)))
    return slip


def v2_side_cost_vec(g_arr, adv_arr, mult=1.0):
    """Pointwise twin of alloc_backtest.side_cost_v2 (mult=1) /
    side_cost_x2 (mult=2). Selftest asserts exact equality on random
    faces incl. the commission floor and the NaN-adv fallback."""
    g = np.asarray(g_arr, dtype=np.float64)
    comm = np.maximum(g * FEE.commission_rate * mult,
                      FEE.commission_min * mult)
    return comm + g * mult * (FEE.handling_fee + FEE.supervision_fee) \
        + g * mult * _slip_vec(adv_arr)


def apply_margin_gate(lots, px, nav, mult, margin_rate, cap=1.0):
    """Equity budget gate: shrink |lots| toward zero until margin usage
    <= cap x nav (futures_runner shrink-the-largest-occupant law, single
    variety face: lot-by-lot). Returns gated lots."""
    lots = int(lots)
    guard = 0
    while abs(lots) * mult * px * margin_rate > cap * nav and lots != 0:
        lots += 1 if lots < 0 else -1
        guard += 1
        if guard > 100000:
            break
    return lots


# ------------------------------------------------------------------ panel
def load_panel():
    """Fail-closed gate battery (prereg s2 data-completeness gate) +
    panel assembly: stock slice, IC alignment, rebalance schedule, ADV /
    slip precompute at execution days, passive baselines."""
    files = sorted(glob.glob(os.path.join(BARS, "*.parquet")))
    if len(files) != N_FILES_EXPECT:
        return None, f"bars census drift: {len(files)} != {N_FILES_EXPECT}"
    if not os.path.exists(XCC_JSON):
        return None, "cache cross-check reference absent"
    xcc = json.load(open(XCC_JSON, encoding="utf-8"))
    if int(xcc.get("bars_files", -1)) != N_FILES_EXPECT:
        return None, "cross-check bars_files drift"
    if xcc.get("cache_last_date") != EVIDENCE_CUTOFF:
        return None, "cross-check cache_last_date drift"
    bad = [k for k, v in xcc.items()
           if isinstance(v, dict) and v.get("finite_mask_mismatches")]
    if bad:
        return None, f"cross-check mismatches: {bad}"
    meta = json.load(open(os.path.join(CACHE, "meta.json"), encoding="utf-8"))
    # r299 kenglu: gate constant IS the actual asset meta stamp
    if meta.get("generated") != CACHE_STAMP_EXPECTED:
        return None, (f"cache meta stamp drift: {meta.get('generated')} "
                      f"!= {CACHE_STAMP_EXPECTED}")
    idx = pd.to_datetime(np.load(os.path.join(CACHE, "dates.npy")), unit="us")
    if str(idx[-1].date()) != EVIDENCE_CUTOFF:
        return None, "panel end != cutoff"
    close32 = np.load(os.path.join(CACHE, "close.npy"), mmap_mode="r")
    amt32 = np.load(os.path.join(CACHE, "amount.npy"), mmap_mode="r")
    T, N = len(idx), close32.shape[1]
    if meta.get("shape", {}).get("T") != T or meta.get("shape", {}).get("N") != N:
        return None, f"cache shape drift: ({T},{N}) vs meta {meta.get('shape')}"
    syms = [os.path.basename(p)[:-8] for p in files]
    if len(syms) != N or len(idx) != T:
        return None, "cache shape vs bars census drift"
    col = {s: j for j, s in enumerate(syms)}

    # ---- universe re-derive (KLINE/SECTOR per-file method, str codes)
    mask = pd.read_csv(MASK, dtype={"code": str})
    ok = set(mask.loc[mask["ok_static"] == True, "code"])
    u_cols = []
    skip = {"not_ok": 0, "rows": 0, "last": 0, "liq": 0}
    for p in files:
        code = os.path.basename(p)[:-8]
        if code not in ok:
            skip["not_ok"] += 1
            continue
        df = pd.read_parquet(p, columns=["date", "amount"])
        if len(df) < MIN_ROWS:
            skip["rows"] += 1
            continue
        if str(df["date"].iloc[-1])[:10] != EVIDENCE_CUTOFF:
            skip["last"] += 1
            continue
        if float(np.median(df["amount"].values[-20:])) < MIN_AMT20:
            skip["liq"] += 1
            continue
        u_cols.append(col[code])
    u_cols = np.array(sorted(u_cols), dtype=np.int64)
    if len(u_cols) != UNIVERSE_EXPECT:
        return None, f"universe re-derive drift: n={len(u_cols)}"
    # identical formula + identical inputs -> skip ledger must equal the
    # frozen SECTOR probe face (stronger zero-drift gate, zero extra cost)
    probe = json.load(open(SECTOR_PROBE, encoding="utf-8"))
    if int(probe.get("universe_n", -1)) != UNIVERSE_EXPECT:
        return None, "sector probe universe_n drift (shared face)"
    if skip != probe.get("universe_skipped"):
        return None, (f"universe skip ledger drift: {skip} "
                      f"vs sector probe {probe.get('universe_skipped')}")
    n_u = len(u_cols)
    syms_u = [syms[j] for j in u_cols]

    # ---- joint window positions on the stock calendar
    p0 = int(np.searchsorted(idx.values, np.datetime64(IC_FIRST_BAR)))
    if p0 <= 0 or str(idx[p0].date()) != IC_FIRST_BAR:
        return None, "joint window start bar absent from stock calendar"
    p_end = T - 1
    if str(idx[p_end].date()) != EVIDENCE_CUTOFF:
        return None, "cutoff bar absent"
    lead0 = p0 - REV_LEAD
    if lead0 < 0:
        return None, "panel history shorter than REV lead"

    # ---- IC panel: gates + truncation + calendar alignment (carry face)
    ic_raw = pd.read_csv(IC_CSV)
    if len(ic_raw) != IC_ROWS_EXPECT:
        return None, f"IC rows drift: {len(ic_raw)} != {IC_ROWS_EXPECT}"
    ic_raw["date"] = pd.to_datetime(ic_raw["date"])
    ic_raw = ic_raw.sort_values("date")
    if str(ic_raw["date"].iloc[0].date()) != IC_FIRST_BAR:
        return None, "IC first bar drift"
    if str(ic_raw["date"].iloc[-1].date()) != IC_LAST_BAR_RAW:
        return None, f"IC last bar drift: {ic_raw['date'].iloc[-1].date()}"
    ic_cut = ic_raw[ic_raw["date"] <= pd.Timestamp(EVIDENCE_CUTOFF)].copy()
    dropped_past_cutoff = int(len(ic_raw) - len(ic_cut))
    jcal = idx[p0:p_end + 1]                       # joint calendar
    T_j = len(jcal)
    ic_idx = pd.DatetimeIndex(ic_cut["date"])
    on_cal = ic_idx.isin(jcal)
    ic_on_cal = ic_cut[on_cal]
    bars_off_cal = int((~on_cal).sum())
    ic_s = ic_on_cal.set_index("date")
    ic_close = ic_s["close"].reindex(jcal).ffill()
    ic_open = ic_s["open"].reindex(jcal).ffill()
    ic_bar_day = pd.Series(False, index=jcal)
    ic_bar_day.loc[ic_s.index] = True
    if not ic_bar_day.iloc[0] or not bool(ic_bar_day.iloc[-1]):
        return None, "joint window end bars absent on IC face"
    ic_c = ic_close.to_numpy(dtype=np.float64)
    ic_o = ic_open.to_numpy(dtype=np.float64)
    r_ic = np.zeros(T_j)
    r_ic[1:] = ic_c[1:] / ic_c[:-1] - 1.0
    carry_days = int((~ic_bar_day.to_numpy()).sum())

    # roll-day proxy (V0: contract-level data absent; |r| > 3 sigma20
    # trailing, window EXCLUDES the day itself, min 10)
    roll_days = []
    for j in range(T_j):
        lo = max(0, j - ROLL_WIN)
        w = r_ic[lo:j]
        if len(w) >= 10 and w.std(ddof=1) > 0:
            if abs(r_ic[j]) > ROLL_SIGMA_N * float(w.std(ddof=1)):
                roll_days.append(str(jcal[j].date()))

    # ---- stock slice (joint window + REV lead), float64
    lead0b = p0 - REV_LEAD
    close_u = np.asarray(close32[lead0b:p_end + 1][:, u_cols],
                         dtype=np.float64)       # rows [lead0b, p_end]
    lead = p0 - lead0b                          # = REV_LEAD
    amt_u = np.asarray(amt32[p0 - ROLL_WIN:p_end + 1][:, u_cols],
                       dtype=np.float64)         # rows [p0-20, p_end]

    # ---- sse onto calendar (ffill bridge, REV_OSC face) -> joint slice
    sse_df = pd.read_parquet(SSE)
    sse_df["date"] = pd.to_datetime(sse_df["date"])
    sse_close = sse_df.set_index("date")["close"].reindex(idx).ffill()
    sse_v = sse_close.to_numpy(dtype=np.float64)
    ma200 = pd.Series(sse_v).rolling(200, min_periods=200).mean().to_numpy()

    # ---- unhedged universe-EW passive (renorm face, joint window)
    cj = close_u[lead:]                          # joint rows only
    with np.errstate(invalid="ignore"):
        rj = cj[1:] / cj[:-1] - 1.0
    fin = np.isfinite(rj)
    ssum = np.where(fin, rj, 0.0).sum(axis=1)
    cnt = fin.sum(axis=1)
    ew = np.where(cnt > 0, ssum / np.maximum(cnt, 1), 0.0)   # T_j-1 days
    ew = np.concatenate([[0.0], ew])              # day-0 anchor 0

    # ---- rebalance schedule (frozen: t_k = k*REB, exec t_k+1)
    sig_days = []
    k = 0
    while k * REB <= T_j - 2:
        sig_days.append(k * REB)
        k += 1
    K = len(sig_days)
    exec_days = [t + 1 for t in sig_days]

    # ---- ADV20 + slip precompute at execution days (per rebalance row)
    adv_exec = np.full((K, n_u), np.nan, dtype=np.float64)
    for i, e in enumerate(exec_days):
        row = p0 + e                             # calendar row of exec day
        lo = row - 19
        blk = amt_u[lo - (p0 - ROLL_WIN):row + 1 - (p0 - ROLL_WIN)]
        finm = np.isfinite(blk)
        c = finm.sum(axis=0)
        s = np.where(finm, blk, 0.0).sum(axis=0)
        okm = c >= 10
        adv_exec[i, okm] = s[okm] / c[okm]
    slip_exec = _slip_vec(adv_exec)

    face = {
        "files": N_FILES_EXPECT, "universe_n": n_u, "skip": skip,
        "cutoff": EVIDENCE_CUTOFF, "cache_stamp": CACHE_STAMP_EXPECTED,
        "cache_stamp_note": "gate constant = actual asset meta value "
                            "(r299 kenglu)",
        "universe_gate": "count 3106 + skip ledger == frozen SECTOR probe "
                         "(identical formula + inputs, zero-drift face)",
        "joint_window": {"start": IC_FIRST_BAR, "end": EVIDENCE_CUTOFF,
                         "T_j": int(T_j),
                         "calendar_primary": "stock panel calendar is the "
                         "master; IC reindexed onto it"},
        "ic_face": {"rows_raw": int(len(ic_raw)),
                    "rows_after_cutoff_truncation": int(len(ic_cut)),
                    "bars_dropped_past_cutoff": dropped_past_cutoff,
                    "bars_off_stock_calendar": bars_off_cal,
                    "carry_days": carry_days,
                    "signal_input": "OHLC only (oi/settle excluded, "
                                    "CTA_P1 s2 case)",
                    "roll_proxy": {"rule": f"|r_ic| > {ROLL_SIGMA_N} x "
                                           f"sigma20(trailing, excl. day, "
                                           f"min {ROLL_WIN})",
                                   "n_days": len(roll_days),
                                   "days": roll_days,
                                   "note": "contract-level roll data "
                                           "absent in V0 (main-continuous "
                                           "panel); proxy face disclosed"},
                    },
        "rebalance": {"period_td": REB, "n_rebalances": int(K),
                      "first_signal_day": str(jcal[sig_days[0]].date()),
                      "last_signal_day": str(jcal[sig_days[-1]].date())},
    }
    P = {"idx": idx, "jcal": jcal, "T_j": T_j, "n_u": n_u, "syms_u": syms_u,
         "u_cols": u_cols, "close_u": close_u, "lead": lead,
         "amt_u": amt_u, "ic_c": ic_c, "ic_o": ic_o, "ic_bar": ic_bar_day,
         "r_ic": r_ic, "carry_days": carry_days, "roll_days": roll_days,
         "sig_days": sig_days, "exec_days": exec_days, "K": K,
         "adv_exec": adv_exec, "slip_exec": slip_exec,
         "sse_j": sse_v[p0:p_end + 1], "ma200_j": ma200[p0:p_end + 1],
         "ew": ew, "face": face}
    return P, None


# ------------------------------------------------------------------ masks
def rev_masks(P, W):
    """REV_W bottom-quintile loser baskets at each signal day (frozen
    encoding). Returns (list of index arrays, list of n_k)."""
    lead = P["lead"]
    cl = P["close_u"]
    masks, n_ks = [], []
    for t in P["sig_days"]:
        c_now = cl[lead + t]
        c_then = cl[lead + t - W]
        with np.errstate(invalid="ignore"):
            rev = -(c_now / c_then - 1.0)
        valid = np.flatnonzero(np.isfinite(rev) & np.isfinite(c_now)
                               & np.isfinite(c_then))
        n_k = max(1, int(math.ceil(len(valid) / 5.0)))
        if len(valid) <= n_k:
            sel = valid
        else:
            sel = valid[np.argsort(-rev[valid], kind="stable")[:n_k]]
        masks.append(np.sort(sel))
        n_ks.append(int(len(sel)))
    return masks, n_ks


def random_masks(P, n_ks, rng):
    """Uniform random n_k-of-universe baskets (same-mask null face)."""
    n_u = P["n_u"]
    masks = []
    for n_k in n_ks:
        key = rng.random(n_u)
        masks.append(np.sort(np.argpartition(-key, n_k - 1)[:n_k]
                             if n_k < n_u else np.arange(n_u)))
    return masks


# ------------------------------------------------------------------ sim
def simulate(P, masks, n_ks, beta_mode="h1", beta_w=BETA_WIN,
             beta_cap=BETA_CAP, cost_mult=1.0, want_audit=False):
    """One basket-config daily NAV series on the joint window (frozen
    accounting). beta_mode 'h1' = 1.0 frozen; 'beta' = rolling intercept
    OLS truncated [BETA_FLOOR, beta_cap] with <BETA_MIN_PAIRS fallback.
    Returns dict with 'series' (daily returns) + counters/audit."""
    T_j = P["T_j"]
    K = P["K"]
    r_ic = P["r_ic"]
    ic_o = P["ic_o"]
    ic_c = P["ic_c"]
    ic_bar = P["ic_bar"].to_numpy()
    cl = P["close_u"]
    lead = P["lead"]
    slip_exec = P["slip_exec"]
    mult = IC["mult"]
    margin_rate = IC["margin"]
    per_lot = (IC["fee_lot"] + IC["tick"] * IC["mult"]) * float(cost_mult)

    ser = np.zeros(T_j)
    rb = np.zeros(T_j)                 # basket returns (0-subst. face)
    h_day = np.zeros(T_j)              # hedge notional ratio (>=0, short)
    cost_day = np.zeros(T_j)

    lots_prev = 0
    h_prev = 0.0
    nav = float(NAV0)
    n_entries = 0
    n_rebalances = 0
    blocked = absent = fallbacks = zero_finite = 0
    stock_cost_tot = fut_cost_tot = turnover = 0.0
    lots_list, beta_list, h_list = [], [], []
    margin_peak = 0.0
    prev_mask = np.zeros(P["n_u"], dtype=bool)

    # OLS window day-count helper: r_b defined from day 1
    for k in range(K):
        t = P["sig_days"][k]
        e = P["exec_days"][k]
        d1 = P["sig_days"][k + 1] if k + 1 < K else T_j - 1
        # ---- beta (known at signal close t)
        if beta_mode == "h1":
            beta = 1.0
        else:
            n_pairs = min(beta_w, t)          # days 1..t within window
            if n_pairs < BETA_MIN_PAIRS:
                beta = 1.0
                fallbacks += 1
            else:
                lo = t - n_pairs + 1
                sb = rb[lo:t + 1].sum()
                sy = r_ic[lo:t + 1].sum()
                sxy = (rb[lo:t + 1] * r_ic[lo:t + 1]).sum()
                sxx = (r_ic[lo:t + 1] * r_ic[lo:t + 1]).sum()
                den = sxx - sy * sy / n_pairs
                if den <= 0:
                    beta = 1.0
                    fallbacks += 1
                else:
                    beta = (sxy - sb * sy / n_pairs) / den
                    beta = float(min(max(beta, BETA_FLOOR), beta_cap))
        # ---- execution at e: lots / margin gate / blocked / absent
        if ic_bar[e]:
            px_open = float(ic_o[e])
            prev_c = float(ic_c[e - 1])
            if abs(px_open / prev_c - 1.0) >= IC["limit"]:
                blocked += 1
                lots = lots_prev
                h = h_prev
            else:
                target = beta * STOCK_LEG * nav
                lots = int(-round(target / (px_open * mult)))
                lots = apply_margin_gate(lots, px_open, nav, mult,
                                         margin_rate)
                h = abs(lots) * mult * px_open / nav
                usage = abs(lots) * mult * px_open * margin_rate / nav
                margin_peak = max(margin_peak, usage)
        else:
            absent += 1
            lots = lots_prev
            h = h_prev
        d_lots = abs(lots - lots_prev)
        fut_cost = d_lots * per_lot
        # ---- stock turnover cost (V2 vectorized twin, EW equal notional)
        mask_k = np.zeros(P["n_u"], dtype=bool)
        mask_k[masks[k]] = True
        enter = mask_k & ~prev_mask
        exit_ = ~mask_k & prev_mask
        n_enter = int(enter.sum())
        n_exit = int(exit_.sum())
        n_entries += n_enter + n_exit
        g_e = STOCK_LEG * nav / max(n_ks[k], 1)
        g_x = STOCK_LEG * nav / max(n_ks[k - 1] if k else n_ks[0], 1)
        stock_cost = 0.0
        if n_enter:
            stock_cost += float(v2_side_cost_vec(
                np.full(n_enter, g_e), P["slip_exec"][k][enter],
                cost_mult).sum())
        if n_exit:
            stock_cost += float(v2_side_cost_vec(
                np.full(n_exit, g_x), P["slip_exec"][k][exit_],
                cost_mult).sum())
        cost_k = stock_cost + fut_cost
        stock_cost_tot += stock_cost
        fut_cost_tot += fut_cost
        turnover += n_enter * g_e + n_exit * g_x + d_lots * mult \
            * (float(ic_o[e]) if np.isfinite(ic_o[e]) else 0.0)
        n_rebalances += 1
        # ---- period returns: basket (new mask, close[t] anchor)
        sel = masks[k]
        sub = cl[lead + e - 1: lead + d1 + 1][:, sel]
        with np.errstate(invalid="ignore"):
            rr = sub[1:] / sub[:-1] - 1.0
        fin = np.isfinite(rr)
        s = np.where(fin, rr, 0.0).sum(axis=1)
        c = fin.sum(axis=1)
        r_b = np.where(c > 0, s / np.maximum(c, 1), 0.0)
        zero_finite += int((c == 0).sum())
        rb[e:d1 + 1] = r_b
        # ---- NAV path over the period (vectorized)
        days = np.arange(e, d1 + 1)
        r_nav = STOCK_LEG * r_b - h * r_ic[e:d1 + 1]
        r_nav[0] -= cost_k / nav
        ser[days] = r_nav
        h_day[days] = h
        cost_day[e] = cost_k
        nav = nav * float(np.prod(1.0 + r_nav))
        lots_prev = lots
        h_prev = h
        prev_mask = mask_k
        if want_audit:
            lots_list.append(int(lots))
            beta_list.append(round(beta, 6))
            h_list.append(round(h, 6))

    out = {"series": ser, "n_rebalances": n_rebalances,
           "n_entries": n_entries, "blocked": blocked, "absent": absent,
           "beta_fallbacks": fallbacks, "zero_finite_days": zero_finite,
           "stock_cost_total": stock_cost_tot,
           "fut_cost_total": fut_cost_tot, "turnover": turnover}
    if want_audit:
        out["lots_list"] = lots_list
        out["beta_list"] = beta_list
        out["h_list"] = h_list
        out["margin_peak"] = margin_peak
    return out


# ------------------------------------------------------------------ stats
def cell_stats(series, calendar_d):
    r = np.asarray(series, dtype=np.float64)
    mu = float(r.mean())
    sd = float(r.std(ddof=1)) if len(r) > 1 else 0.0
    sharpe = mu / sd * math.sqrt(PBP) if sd > 0 else 0.0
    eq = np.cumprod(1.0 + r)
    peak = np.maximum.accumulate(eq)
    dd = float((eq / peak - 1.0).min())
    ann = float(eq[-1] ** (PBP / max(len(r), 1)) - 1.0)
    i_oos = int(np.searchsorted(calendar_d, OOS_FROM))
    oos = r[i_oos:]
    oos_ann = None
    oos_sh = 0.0
    if len(oos):
        oos_eq = np.cumprod(1.0 + oos)
        oos_ann = float(oos_eq[-1] ** (PBP / max(len(oos), 1)) - 1.0)
        oos_sd = float(oos.std(ddof=1)) if len(oos) > 1 else 0.0
        oos_sh = float(oos.mean() / oos_sd * math.sqrt(PBP)) \
            if oos_sd > 0 else 0.0
    return {"sharpe_full": round(sharpe, 4), "ann_ret": round(ann, 6),
            "max_dd": round(dd, 6), "n_days": int(len(r)),
            "oos_from": str(pd.Timestamp(OOS_FROM).date()),
            "oos_ann": round(oos_ann, 6) if oos_ann is not None else None,
            "oos_sharpe": round(oos_sh, 4)}


def crash_years(series, calendar_d):
    """Calendar-year returns (engine.futures_runner.yearly_results
    single source) + crash-year face (<= CRASH_YEAR, operationalization
    of the prereg's 无崩年, disclosed)."""
    r = np.asarray(series, dtype=np.float64)
    eq = pd.Series(np.cumprod(1.0 + r),
                   index=pd.DatetimeIndex(calendar_d))
    yr = yearly_returns(eq)
    crash = [y for y, v in yr.items() if v <= CRASH_YEAR]
    return {"yearly_returns": yr, "crash_year_line": CRASH_YEAR,
            "crash_years": crash, "no_crash_year": not crash}


# ------------------------------------------------------------------ nulls
def null_draw(P, cell, n_ks, k):
    rng = np.random.default_rng(SEED + k)
    masks = random_masks(P, n_ks, rng)
    sim = simulate(P, masks, n_ks, beta_mode=cell["beta_mode"],
                   cost_mult=2.0)
    st = cell_stats(sim["series"], P["jcal"].values.astype("datetime64[D]"))
    return float(st["sharpe_full"])


def run_cell_nulls(P, cell, n_ks):
    """K=2000 own-null pool, sharded npy checkpoints (idempotent)."""
    per = K_NULLS // NULL_SHARDS
    vals = np.empty(K_NULLS)
    for s in range(NULL_SHARDS):
        path = os.path.join(NULL_DIR, f"{cell['name']}_shard{s}.npy")
        if os.path.exists(path):
            vals[s * per:(s + 1) * per] = np.load(path)
            continue
        chunk = np.empty(per)
        for i in range(per):
            k = s * per + i
            chunk[i] = null_draw(P, cell, n_ks, k)
        np.save(path, chunk)
        vals[s * per:(s + 1) * per] = chunk
        print(f"  nulls {cell['name']} shard {s + 1}/{NULL_SHARDS} done",
              flush=True)
    cov = {"mu": round(float(vals.mean()), 4),
           "sigma": round(float(vals.std(ddof=1)), 4),
           "n_values": int(len(vals))}
    return {"values": [round(float(v), 4) for v in vals], "coverage": cov,
            "null_face": "same-mask uniform random n_k-of-3106 baskets, "
                         "same rebalance schedule / execution / cost(x2) "
                         "/ hedge machinery (random-basket beta OLS "
                         "included = beta-drift-stripped carrier)",
            "seed_base": int(SEED)}


# ------------------------------------------------- virtual starts & robust
def seg_class(P, t0):
    s, m = P["sse_j"][t0], P["ma200_j"][t0]
    if not (np.isfinite(s) and np.isfinite(m)):
        return "na"
    s60 = P["sse_j"][max(t0 - 60, 0)]
    if not np.isfinite(s60):
        return "na"
    r60 = s / s60 - 1.0
    if s > m:
        return "bull" if r60 > 0.05 else "chop"
    return "deep_bear" if r60 < -0.15 else "bear"


def virtual_starts(P, series_by_cell):
    T = P["T_j"]
    starts = list(range(STARTS_FROM, T - WIN_DAYS))
    segs = np.array([seg_class(P, t0) for t0 in starts])
    sa = np.array(starts)
    ew = np.asarray(P["ew"], dtype=np.float64)
    ew_cs = np.cumsum(np.log1p(ew))
    out = {"n_starts": len(starts), "segments": {},
           "beat_baseline": "unhedged_ew_universe (prereg s3 passive 2 "
                            "proxy face)"}
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
                           round(100.0 * agree / valid, 1) if valid else None}
    out["cells"] = cells
    return out


def robust_stats(series):
    """Block bootstrap (block=10) + sign-flip, 2000 each (law s3)."""
    r = np.asarray(series, dtype=np.float64)
    n = len(r)
    sd0 = r.std(ddof=1)
    obs = r.mean() / sd0 * math.sqrt(PBP) if sd0 > 0 else 0.0
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
    return {"obs_sharpe": round(obs, 4),
            "block_bootstrap_p95_mean": round(float(np.percentile(bb, 95)), 6),
            "block_bootstrap_p05_mean": round(float(np.percentile(bb, 5)), 6),
            "block_bootstrap_p_le_0": round(float((bb <= 0).mean()), 4),
            "sign_flip_p": round(float(
                (np.abs(sf) >= abs(obs)).mean()), 4)}


def d6_block(P, series_by_cell):
    """s1 reject face vs REGISTERED members (ew6 canon, SECTOR-verbatim)."""
    from cn_rev_tilt_p1 import REG6, load_member_rets, _corr
    member_rets, _member_cutoffs = load_member_rets()
    cal = pd.DatetimeIndex(P["jcal"])
    out = {"reject_line": D6_REJECT, "members": list(REG6), "cells": {}}
    mat = {}
    for name, series in series_by_cell.items():
        s = pd.Series(np.asarray(series, dtype=np.float64), index=cal)
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


# ------------------------------------------------------------------ sobol
def sobol_params():
    """Sobol(3) scrambled, seed-sequence [SEED, 2000]; 512 drawn
    (power-of-2 balance), first SOBOL_N consumed."""
    from scipy.stats import qmc
    eng = qmc.Sobol(d=3, scramble=True,
                    seed=np.random.default_rng([int(SEED), 2000]))
    pts = eng.random(SOBOL_DRAW_BALANCE)[:SOBOL_N]
    Ws = np.floor(pts[:, 0] * len(SOBOL_W_GRID)).astype(int)
    BWs = np.floor(pts[:, 1] * len(SOBOL_BW_GRID)).astype(int)
    CAPs = np.floor(pts[:, 2] * len(SOBOL_CAP_GRID)).astype(int)
    return np.stack([np.array(SOBOL_W_GRID)[Ws],
                     np.array(SOBOL_BW_GRID)[BWs],
                     np.array(SOBOL_CAP_GRID)[CAPs]], axis=1)


def run_sobol(P, mask_cache):
    """Space-filling descriptive leg: per-draw REV re-encode (W) + beta
    window/cap grid + x1 face sim. Sharded npy checkpoints."""
    os.makedirs(SOBOL_DIR, exist_ok=True)
    params = sobol_params()
    per = SOBOL_N // SOBOL_SHARDS
    rows_all = np.empty((SOBOL_N, 7))
    for s in range(SOBOL_SHARDS):
        path = os.path.join(SOBOL_DIR, f"shard{s}.npy")
        if os.path.exists(path):
            rows_all[s * per:(s + 1) * per] = np.load(path)
            continue
        chunk = np.empty((per, 7))
        for i in range(per):
            k = s * per + i
            W_, BW_ = int(params[k, 0]), int(params[k, 1])
            CAP_ = float(params[k, 2])   # cap is a float grid value
            if W_ not in mask_cache:
                mask_cache[W_] = rev_masks(P, W_)
            masks, n_ks = mask_cache[W_]
            sim = simulate(P, masks, n_ks, beta_mode="beta", beta_w=BW_,
                          beta_cap=CAP_, cost_mult=1.0)
            st = cell_stats(sim["series"],
                            P["jcal"].values.astype("datetime64[D]"))
            chunk[i] = (W_, BW_, CAP_, st["sharpe_full"],
                        float(sim["series"].mean()), st["max_dd"],
                        sim["n_entries"])
        np.save(path, chunk)
        rows_all[s * per:(s + 1) * per] = chunk
        print(f"  sobol shard {s + 1}/{SOBOL_SHARDS} done", flush=True)
    desc = {}
    for nm, arr in (("sharpe", rows_all[:, 3]), ("mean_daily", rows_all[:, 4]),
                    ("max_dd", rows_all[:, 5])):
        desc[nm] = {"p05": round(float(np.percentile(arr, 5)), 6),
                    "p25": round(float(np.percentile(arr, 25)), 6),
                    "p50": round(float(np.percentile(arr, 50)), 6),
                    "p75": round(float(np.percentile(arr, 75)), 6),
                    "p95": round(float(np.percentile(arr, 95)), 6),
                    "mean": round(float(arr.mean()), 6),
                    "min": round(float(arr.min()), 6),
                    "max": round(float(arr.max()), 6)}
    return {
        "n_draws": int(SOBOL_N),
        "space": {"REV_W": list(SOBOL_W_GRID),
                  "beta_window": list(SOBOL_BW_GRID),
                  "beta_cap": list(SOBOL_CAP_GRID), "grid": "discrete"},
        "seed_sequence": f"[{int(SEED)}, 2000]",
        "engine_note": f"scipy qmc.Sobol(3) scrambled; {SOBOL_DRAW_BALANCE} "
                       "drawn (power-of-2 balance), first "
                       f"{SOBOL_N} consumed per prereg s3.2.2",
        "cost_face": "x1 (V2 basis)",
        "rows": [[int(r[0]), int(r[1]), float(r[2]), round(float(r[3]), 4),
                  round(float(r[4]), 8), round(float(r[5]), 6), int(r[6])]
                 for r in rows_all],
        "description": desc,
        "claims_note": "descriptive only: NO N_eff, NO gates, NO "
                       "survivorship claims (prereg s3.2.2)",
    }


# ------------------------------------------------------------------ finalize
def _attr_row(batch, delta, total, gates, entries):
    d = json.load(open(ATT_JSON, encoding="utf-8"))
    row = {"batch": batch,
           "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
           "kind": "measurement", "cells_ledger_delta": delta,
           "ledger_total_after": total, "gates": gates,
           "entries": entries}            # r248 entries-list face
    own = [i for i, e in enumerate(d["entries"])
           if e.get("batch") == batch and e.get("kind") == "measurement"]
    if own:
        d["entries"][own[-1]] = row
    else:
        d["entries"].append(row)
    with open(ATT_JSON + ".tmp", "w", encoding="utf-8") as fh:
        json.dump(d, fh, ensure_ascii=False, indent=1)
    os.replace(ATT_JSON + ".tmp", ATT_JSON)


def finalize(P, cells_out, nulls, d6, vstarts, robust, sobol):
    series_by_cell = {n: cells_out[n]["x2"]["series"] for n in cells_out}
    cal_d = P["jcal"].values.astype("datetime64[D]")
    # r259 prev-echo guard (re-finalize single-count law)
    prev_total = None
    if os.path.exists(OUT_JSON):
        try:
            with open(OUT_JSON, encoding="utf-8") as fh:
                prev_total = int(
                    json.load(fh)["trials_ledger"]["prev_total"])
        except Exception:
            prev_total = None
    head_base = (prev_total if prev_total is not None
                 else int(SG.ledger_head()["total"]))
    gates = {}
    for name, ser in series_by_cell.items():
        st = cells_out[name]["x2"]["stats"]
        g1 = SG.g1_prime_v2(st["sharpe_full"], ser, batch_cells=BATCH_CELLS,
                            pool="stock_b_layer",
                            null_pool={"values": nulls[name]["values"],
                                       "coverage": nulls[name]["coverage"]},
                            n_trades=cells_out[name]["x2"]["n_rebalances"],
                            n_entries=cells_out[name]["x2"]["n_entries"],
                            n_eff_override=head_base + BATCH_CELLS)
        dsr = SG.deflated_sharpe_ratio(ser, n_trials=g1["skill_line"]["n_eff"])
        gates[name] = {"g1_prime_v2": g1, "dsr": dsr}
    mat = pd.DataFrame({n: np.asarray(s, dtype=np.float64)
                        for n, s in series_by_cell.items()})
    pbo = cscv_pbo(mat)
    for name in gates:
        gates[name]["g2"] = SG.g2_registration_v2(
            gates[name]["g1_prime_v2"]["pass_v2"],
            gates[name]["dsr"], float(pbo["pbo"]))
        gates[name]["d6_reject"] = bool(d6["cells"][name]["reject"])

    ledger = SG.append_ledger(BATCH_NAME, BATCH_CELLS,
                              file_name="cn_mkneutral_p1",
                              evidence_cutoff=EVIDENCE_CUTOFF,
                              prev_total=prev_total)
    _attr_row(BATCH_NAME, BATCH_CELLS, int(ledger["total"]),
              {"g1_pass": {n: gates[n]["g1_prime_v2"]["pass_v2"]
                          for n in gates},
               "g2_eligible": {n: gates[n]["g2"]["eligible_v2"]
                               for n in gates},
               "d6_reject": {n: gates[n]["d6_reject"] for n in gates},
               "family_pbo": pbo},
              {"entries_x2": {n: cells_out[n]["x2"]["n_entries"]
                              for n in cells_out},
               "rebalances_x2": {n: cells_out[n]["x2"]["n_rebalances"]
                                  for n in cells_out},
               "blocked": {n: cells_out[n]["x2"]["audit"]["blocked"]
                           for n in cells_out},
               "ic_absent_exec": {n: cells_out[n]["x2"]["audit"]["absent"]
                                  for n in cells_out},
               "roll_proxy_days": P["roll_days"]})

    # passive baselines (disclosure only, prereg s3 passive-2)
    passives = {}
    for nm, s in (("unhedged_ew_universe", P["ew"]),
                  ("ic_replication", P["r_ic"])):
        st = cell_stats(s, cal_d)
        passives[nm] = {"stats": st,
                        "note": "disclosure column, NOT in skill_line "
                                "(no same-risk passive exists for a "
                                "hedged book; own-null pool is the sole "
                                "judgment line, CTA_P1 domain-null law)"}

    result = {
        "batch": BATCH_NAME,
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "cutoff_meta": SG.cutoff_meta(EVIDENCE_CUTOFF),
        "prereg": "research/CN_MKTNEUTRAL_PREREG.md (@3c71ddb4 freeze)",
        "seed": {"base": SEED, "k": K_NULLS,
                 "sobol_seedseq": f"[{int(SEED)}, 2000]"},
        "panel": P["face"],
        "nav_model": {"nav0_cny": NAV0,
                      "nav0_note": "engineering freeze (institutional mid "
                      "scale, lot-rounding noise < 1%; prereg leaves scale "
                      "to the runner)",
                      "stock_leg": STOCK_LEG, "cash_leg": CASH_LEG,
                      "idle_cash_rate": 0.0,
                      "entry_anchor": "close[t_k] (t+1-open execution, "
                      "daily close-close accounting V0 approximation; "
                      "overnight gap of the incoming basket not "
                      "separately modeled, disclosed)",
                      "h_ratio_face": "lots-implied actual notional / NAV "
                      "at execution, constant within period (within-period "
                      "price-drift second-order term not booked, V0)",
                      "beta_face": "BETA cells: rolling-60d intercept OLS "
                      "cov/var, truncated [0.5, 1.5], <30 pairs -> 1.0 "
                      "fallback (audit); H1 cells: 1.0 frozen"},
        "cost": {"face_judged": "x2 (every V2 component doubled + futures "
                                "per-lot doubled; both legs same "
                                "multiplier)",
                 "x1": "V2 basis disclosure column",
                 "stock_leg": "per-trade direct V2 (vectorized twin, "
                              "selftest pointwise-equal)",
                 "futures_leg": f"per-lot (fee {IC['fee_lot']} + 1 tick "
                                f"{IC['tick']}) x mult on |d_lots|",
                 "fut_meta": {k: IC[k] for k in
                              ("margin", "mult", "fee_lot", "tick",
                               "limit")}},
        "cells": {n: {f: {"stats": cells_out[n][f]["stats"],
                          "n_rebalances": cells_out[n][f]["n_rebalances"],
                          "n_entries": cells_out[n][f]["n_entries"],
                          "audit": cells_out[n][f]["audit"]}
                      for f in ("x1", "x2")} for n in cells_out},
        "nulls": nulls, "d6": d6, "virtual_starts": vstarts,
        "robust": robust, "family_pbo": pbo, "sobol": sobol,
        "passive_baselines": passives, "gates": gates,
        "trials_ledger": ledger,
        "batch_disclosure": {
            "rule": "ann>0 AND OOS(>=2025-01-01) ann>0 AND maxDD>=-35% "
                    "AND no crash year (prereg s4 disclosure columns)",
            "crash_year_line": CRASH_YEAR,
            "crash_year_note": "operationalization of the prereg's 无崩年 "
                               "(calendar-year return <= -30%), disclosed",
            "cells_ok": {}, "crash_years_x2": {}},
        "verdict_line": ("judged per prereg s4 on x2 faces; judged-negative "
                         "= 行16 中性面全闭 per prereg boundary clause "
                         "(claim != verify)"),
    }
    for n in cells_out:
        stx = cells_out[n]["x2"]["stats"]
        cy = crash_years(cells_out[n]["x2"]["series"], cal_d)
        result["batch_disclosure"]["cells_ok"][n] = bool(
            stx["ann_ret"] > 0 and (stx["oos_ann"] or -1) > 0
            and stx["max_dd"] >= -0.35 and cy["no_crash_year"])
        result["batch_disclosure"]["crash_years_x2"][n] = cy
    os.makedirs(OUT_DIR, exist_ok=True)
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


# ------------------------------------------------------------------ driver
def cmd_run():
    global SEED
    SEED = SG.SEED_REGISTRY["cn_mkneutral_p1"]
    if _free_ram_gb() < RAM_FLOOR_GB:
        print("free-RAM floor refused")
        return 3
    t0 = time.time()
    P, err = load_panel()
    if err:
        return gate_refuse(err)
    print(f"panel ok: universe={P['face']['universe_n']} "
          f"T_j={P['T_j']} K={P['K']} "
          f"({time.time() - t0:.0f}s)", flush=True)
    os.makedirs(CELL_DIR, exist_ok=True)
    os.makedirs(NULL_DIR, exist_ok=True)

    mask_cache = {}
    cells_out = {}
    n_ks_by_cell = {}
    for cell in CELLS:
        name = cell["name"]
        W = cell["W"]
        if W not in mask_cache:
            mask_cache[W] = rev_masks(P, W)
        masks, n_ks = mask_cache[W]
        n_ks_by_cell[name] = n_ks
        cells_out[name] = {}
        for face in ("x1", "x2"):
            ck = os.path.join(CELL_DIR, f"{name}_{face}.json")
            if os.path.exists(ck):
                blob = json.load(open(ck, encoding="utf-8"))
                blob["series"] = np.load(ck.replace(".json", ".npy"))
            else:
                r = simulate(P, masks, n_ks, beta_mode=cell["beta_mode"],
                             cost_mult=2.0 if face == "x2" else 1.0,
                             want_audit=True)
                np.save(ck.replace(".json", ".npy"), r["series"])
                blob = {"series": r["series"],
                        "stats": cell_stats(
                            r["series"],
                            P["jcal"].values.astype("datetime64[D]")),
                        "n_rebalances": r["n_rebalances"],
                        "n_entries": r["n_entries"],
                        "audit": {k: v for k, v in r.items()
                                  if k not in ("series", "n_rebalances",
                                               "n_entries")}}
                dump = {k: v for k, v in blob.items() if k != "series"}
                with open(ck + ".tmp", "w", encoding="utf-8") as fh:
                    json.dump(dump, fh, ensure_ascii=False, indent=1)
                os.replace(ck + ".tmp", ck)
                print(f"  cell {name}/{face}: entries={r['n_entries']} "
                      f"({time.time() - t0:.0f}s)", flush=True)
            cells_out[name][face] = blob

    nulls = {}
    for cell in CELLS:
        nulls[cell["name"]] = run_cell_nulls(
            P, cell, n_ks_by_cell[cell["name"]])
        print(f"  nulls {cell['name']}: mu="
              f"{nulls[cell['name']]['coverage']['mu']} "
              f"({time.time() - t0:.0f}s)", flush=True)

    series_by_cell = {n: cells_out[n]["x2"]["series"] for n in cells_out}
    d6 = d6_block(P, series_by_cell)
    vstarts = virtual_starts(P, series_by_cell)
    robust = {n: robust_stats(s) for n, s in series_by_cell.items()}
    print(f"d6/vstarts/robust done ({time.time() - t0:.0f}s)", flush=True)
    sobol = run_sobol(P, mask_cache)
    print(f"sobol done ({time.time() - t0:.0f}s)", flush=True)
    res = finalize(P, cells_out, nulls, d6, vstarts, robust, sobol)
    print(f"finalize ok: cells={len(res['cells'])} "
          f"ledger={res['trials_ledger']['total']} "
          f"elapsed={time.time() - t0:.0f}s")
    return 0


# ------------------------------------------------------------------ selftest
def _mk_fixture(tmp, T=620):
    """Hermetic synthetic panel: bars parquets + p1c-style cache + mask +
    sse + IC csv. Joint window = rows [200, T-1]; T_j = 420 (row 200 keeps
    REV_LEAD=120 headroom for the max sobol W).

    Stock faces (15 universe members, positions i=0..14 in sorted order):
    - per-day return = k_phase(j) * r_ic(j) + drift_i,
      drift_i = -0.00002 * i  -> REV ranking is drift-ordered ->
      bottom quintile (n_k = ceil(15/5) = 3) = {12, 13, 14} EVERY period
      (stable basket; only period 0 books entries).
    - beta phases (JOINT day j = panel row 200+j):
      A [0,59): k=1.2   B [60,119): k=3.0 (capped 1.5)
      C [120,179): k=0.1 (capped 0.5)   D [180,419): k=1.0
      -> pure-phase OLS windows give EXACT betas (drift is a constant,
      the intercept absorbs it).
    - IC blocked day: joint day 181 open = prev close * 1.13 (a
      rebalance execution day where lots WOULD change).
    - IC absent day: joint day 205 has no IC row (carry mark, r_ic=0).
    - roll proxy day: joint day 300 r_ic = +5% (10+ sigma).
    - IC file carries 2 extra rows past the cutoff (truncation gate).
    - controls: 600091 not_ok / 600092 60-row / 600093 thin amount /
      600094 early-last -> skip ledger {not_ok, rows, last, liq} = 1 each.
    """
    bars = os.path.join(tmp, "bars")
    os.makedirs(bars)
    cal = pd.date_range(end=EVIDENCE_CUTOFF, periods=T,
                        freq="B").as_unit("us")
    cal_arr = cal.values
    n_u = 15
    u_syms = [f"60000{i:02d}" for i in range(1, 16)]
    ctrl = ["600091", "600092", "600093", "600094"]
    all_syms = u_syms + ctrl
    N = len(all_syms)

    JJ = 200                              # joint start panel row
    T_j = T - JJ
    # r_ic pattern (nonzero mean + variance), joint coords
    r_ic = np.array([0.004 if j % 5 < 2 else -0.006 for j in range(T_j)])
    r_ic[300] = 0.05                       # roll proxy day (10+ sigma)
    r_ic[205] = 0.0                         # overridden below (absent)

    def k_phase(j):
        if j < 60:
            return 1.2
        if j < 120:
            return 3.0
        if j < 180:
            return 0.1
        return 1.0

    drift = {s: -0.00002 * i for i, s in enumerate(u_syms)}
    close_paths = {}
    for s in all_syms:
        c = np.full(T, 10.0)
        d = drift.get(s, 0.0)
        for j in range(1, T):
            jj = j - JJ
            if jj >= 0:
                c[j] = c[j - 1] * (1.0 + k_phase(jj) * r_ic[jj] + d)
        close_paths[s] = c
    frames = {}
    for s in all_syms:
        df = pd.DataFrame(index=range(T))
        df["date"] = cal
        c = close_paths[s]
        df["close"] = c
        df["open"] = np.concatenate([[c[0]], c[:-1]])
        df["high"] = np.maximum(df["open"].values, c) + 0.01
        df["low"] = np.minimum(df["open"].values, c) - 0.01
        df["volume"] = 1e6
        df["amount"] = 5e7
        if s == "600093":
            df["amount"] = 0.5                      # liq skip
        frames[s] = df
    frames["600092"] = frames["600092"].iloc[T - 60:].reset_index(drop=True)
    frames["600094"] = frames["600094"].iloc[:T - 10].reset_index(drop=True)
    for s, df in frames.items():
        df.to_parquet(os.path.join(bars, f"{s}.parquet"))

    pd.DataFrame({"code": all_syms,
                  "ok_static": [s != "600091" for s in all_syms]}).to_csv(
        os.path.join(tmp, "mask.csv"), index=False)
    pd.DataFrame({"date": cal,
                  "close": np.linspace(3000, 3400, T)}).to_parquet(
        os.path.join(tmp, "sse.parquet"))

    # IC csv: joint days 0..T_j-1 minus the absent day; open = prev close
    # except the planted blocked day; 2 extra rows past cutoff
    ic_rows = []
    px = 5000.0
    prev_c = None
    for j in range(T_j):
        row_date = cal[JJ + j]
        if j == 0:
            close_px = px
        else:
            close_px = prev_c * (1.0 + r_ic[j])
        open_px = prev_c if prev_c is not None else px
        if j == 181:                              # blocked rebalance exec
            open_px = prev_c * 1.13
        if j != 205:                              # absent IC day
            ic_rows.append([str(row_date.date()), open_px, close_px * 1.001,
                            close_px * 0.999, close_px, 5000, 0, 0.0])
        prev_c = close_px
    nb = pd.bdate_range(EVIDENCE_CUTOFF, periods=3)   # cutoff + 2 more
    for b in nb[1:]:
        ic_rows.append([str(b.date()), prev_c, prev_c * 1.001,
                        prev_c * 0.999, prev_c, 5000, 0, 0.0])
    ic_csv = os.path.join(tmp, "IC.csv")
    pd.DataFrame(ic_rows, columns=["date", "open", "high", "low", "close",
                                   "volume", "oi", "settle"]).to_csv(
        ic_csv, index=False)

    # cache npy: aligned calendar x N, float32, NaN elsewhere
    syms_sorted = sorted(all_syms)
    colmap = {s: i for i, s in enumerate(syms_sorted)}
    cache = os.path.join(tmp, "cache")
    os.makedirs(cache)
    for fld in ("open", "high", "low", "close", "volume", "amount"):
        arr = np.full((T, N), np.nan, dtype=np.float32)
        for s in all_syms:
            df = frames[s]
            pos = np.searchsorted(cal_arr, df["date"].values)
            vals = df[fld].values
            fin = np.isfinite(vals)
            arr[pos[fin], colmap[s]] = vals[fin].astype(np.float32)
        np.save(os.path.join(cache, f"{fld}.npy"), arr)
    np.save(os.path.join(cache, "dates.npy"), cal.values)
    json.dump({"batch": "fixture", "generated": "FIXTURE-CACHE-STAMP",
               "shape": {"T": T, "N": N}},
              open(os.path.join(cache, "meta.json"), "w"))
    return {"bars": bars, "cache": cache, "ic_csv": ic_csv,
            "syms": syms_sorted, "u_syms": u_syms, "all_syms": all_syms,
            "N": N, "T": T, "T_j": T_j, "r_ic": r_ic,
            "ctrl": ctrl}


def cmd_selftest():
    global BARS, CACHE, MASK, SSE, IC_CSV, SECTOR_PROBE, XCC_JSON, OUT_DIR, \
        CELL_DIR, NULL_DIR, SOBOL_DIR, OUT_JSON, OUT_CSV, ATT_JSON, SEED, \
        K_NULLS, NULL_SHARDS, SOBOL_N, SOBOL_SHARDS, SOBOL_DRAW_BALANCE, \
        N_FILES_EXPECT, UNIVERSE_EXPECT, IC_ROWS_EXPECT, IC_LAST_BAR_RAW, \
        IC_FIRST_BAR, CACHE_STAMP_EXPECTED, MIN_ROWS, MIN_AMT20, REV_LEAD, \
        NAV0
    tmp = tempfile.mkdtemp(prefix="cn_mkneutral_selftest_")
    K_NULLS, NULL_SHARDS = 30, 2       # skill_line_v2 thin-line floor = 30
    SOBOL_N, SOBOL_SHARDS, SOBOL_DRAW_BALANCE = 6, 2, 8
    SEED = 20279300
    fx = _mk_fixture(tmp)
    BARS = fx["bars"]
    CACHE = fx["cache"]
    MASK = os.path.join(tmp, "mask.csv")
    SSE = os.path.join(tmp, "sse.parquet")
    IC_CSV = fx["ic_csv"]
    ic_df = pd.read_csv(IC_CSV)
    IC_ROWS_EXPECT = len(ic_df)
    last_d = pd.to_datetime(ic_df["date"]).max()
    IC_LAST_BAR_RAW = str(last_d.date())
    cal = pd.to_datetime(np.load(os.path.join(CACHE, "dates.npy")),
                         unit="us")
    IC_FIRST_BAR = str(cal[200].date())   # fixture joint start (row 200)
    XCC_JSON = os.path.join(tmp, "xcc.json")
    json.dump({"bars_files": len(fx["all_syms"]),
               "cache_last_date": EVIDENCE_CUTOFF,
               "600001": {"finite_mask_mismatches": 0}},
              open(XCC_JSON, "w"))
    OUT_DIR = os.path.join(tmp, "out")
    CELL_DIR = os.path.join(OUT_DIR, "cells")
    NULL_DIR = os.path.join(OUT_DIR, "nulls")
    SOBOL_DIR = os.path.join(OUT_DIR, "sobol")
    OUT_JSON = os.path.join(OUT_DIR, "p1_results.json")
    OUT_CSV = os.path.join(OUT_DIR, "cells_summary.csv")
    ATT_JSON = os.path.join(tmp, "attr.json")
    os.makedirs(CELL_DIR, exist_ok=True)
    os.makedirs(NULL_DIR, exist_ok=True)
    os.makedirs(SOBOL_DIR, exist_ok=True)
    json.dump({"entries": []}, open(ATT_JSON, "w"))
    N_FILES_EXPECT = len(fx["all_syms"])
    MIN_ROWS = 100
    MIN_AMT20 = 1.0
    NAV0 = 1.0e8
    UNIVERSE_EXPECT = len(fx["u_syms"])
    SECTOR_PROBE = os.path.join(tmp, "probe.json")
    json.dump({"universe_n": UNIVERSE_EXPECT,
               "universe_skipped": {"not_ok": 1, "rows": 1, "last": 1,
                                    "liq": 1}},
              open(SECTOR_PROBE, "w"))
    CACHE_STAMP_EXPECTED = "FIXTURE-CACHE-STAMP"
    ok = []

    def check(name, cond):
        ok.append((name, bool(cond)))

    # hermetic stubs (SECTOR face)
    _ne, _pb, _al, _lh = SG.n_eff, SG.passive_baseline, SG.append_ledger, \
        SG.ledger_head
    SG.n_eff = lambda bc, rd=None: int(bc)
    SG.passive_baseline = lambda pool, rd=None: 0.4606
    SG.append_ledger = lambda *a, **k: {"prev_total": 0, "total": 100,
                                        "batch": BATCH_NAME}
    SG.ledger_head = lambda rd=None: {"total": 500, "file": None,
                                      "note": None}
    _real_cscv = globals()["cscv_pbo"]
    globals()["cscv_pbo"] = lambda mat: {"pbo": 0.1}

    try:
        P, err = load_panel()
        check("panel gate battery pass (incl. IC truncation + skip "
              "ledger vs probe face)", err is None)
        if err:
            raise RuntimeError(err)
        check("universe == 15 planted", P["face"]["universe_n"] == 15)
        check("skip ledger == planted",
              P["face"]["skip"] == {"not_ok": 1, "rows": 1, "last": 1,
                                    "liq": 1})
        check("IC truncation dropped 2 past-cutoff bars",
              P["face"]["ic_face"]["bars_dropped_past_cutoff"] == 2)
        check("IC carry day present (planted absent day)",
              P["face"]["ic_face"]["carry_days"] == 1)
        check("roll proxy day flagged (planted 5% jump)",
              len(P["face"]["ic_face"]["roll_proxy"]["days"]) >= 1)
        check("joint window 420 days", P["T_j"] == fx["T_j"])
        check("rebalance schedule K >= 15", P["K"] >= 15)

        # ---- masks: REV ranking drift-ordered -> {12,13,14}
        masks20, n_ks20 = rev_masks(P, 20)
        m60, n_ks60 = rev_masks(P, 60)
        check("n_k = ceil(15/5) = 3 every period",
              all(n == 3 for n in n_ks20) and all(n == 3 for n in n_ks60))
        want = np.array([12, 13, 14])
        check("REV20 basket == planted loser trio every period",
              all(np.array_equal(m, want) for m in masks20))
        check("REV60 basket == planted loser trio (W robustness)",
              all(np.array_equal(m, want) for m in m60))

        # ---- H1 sim + full independent NAV identity re-check
        sim_h1 = simulate(P, masks20, n_ks20, beta_mode="h1",
                          cost_mult=2.0, want_audit=True)
        check("H1 beta list all 1.0", all(
            b == 1.0 for b in sim_h1["beta_list"]))
        # independent recompute: stable basket {12,13,14}, close paths
        # from the fixture frames; hand NAV loop
        cl = P["close_u"][P["lead"]:]
        sel = want
        exp_nav = float(NAV0)
        exp_ser = np.zeros(P["T_j"])
        lots_prev = 0
        h_prev = 0.0
        for k in range(P["K"]):
            t = P["sig_days"][k]
            e = P["exec_days"][k]
            d1 = P["sig_days"][k + 1] if k + 1 < K_FIX(P) else P["T_j"] - 1
            if P["ic_bar"].iloc[e]:
                px_open = float(P["ic_o"][e])
                prev_c = float(P["ic_c"][e - 1])
                if abs(px_open / prev_c - 1.0) >= 0.12:
                    lots = lots_prev
                    h = h_prev
                else:
                    lots = int(-round(1.0 * 0.8 * exp_nav
                                      / (px_open * 200)))
                    h = abs(lots) * 200 * px_open / exp_nav
            else:
                lots = lots_prev
                h = h_prev
            mask_k = np.zeros(P["n_u"], dtype=bool)
            mask_k[masks20[k]] = True
            prev_m = np.zeros(P["n_u"], dtype=bool)
            if k:
                prev_m[masks20[k - 1]] = True
            enter = int((mask_k & ~prev_m).sum())
            exit_ = int((~mask_k & prev_m).sum())
            g_e = 0.8 * exp_nav / 3
            cost_k = 0.0
            if enter:
                cost_k += float(v2_side_cost_vec(
                    np.full(enter, g_e), P["slip_exec"][k][mask_k & ~prev_m],
                    2.0).sum())
            if exit_:
                g_x = 0.8 * exp_nav / 3
                cost_k += float(v2_side_cost_vec(
                    np.full(exit_, g_x), P["slip_exec"][k][~mask_k & prev_m],
                    2.0).sum())
            cost_k += abs(lots - lots_prev) * (34.6 + 0.2 * 200) * 2.0
            sub = cl[e - 1:d1 + 1][:, sel]
            with np.errstate(invalid="ignore"):
                rr = sub[1:] / sub[:-1] - 1.0
            fin = np.isfinite(rr)
            s_ = np.where(fin, rr, 0.0).sum(axis=1)
            c_ = fin.sum(axis=1)
            r_b = np.where(c_ > 0, s_ / np.maximum(c_, 1), 0.0)
            r_nav = 0.8 * r_b - h * P["r_ic"][e:d1 + 1]
            r_nav[0] -= cost_k / exp_nav
            exp_ser[e:d1 + 1] = r_nav
            exp_nav = exp_nav * float(np.prod(1.0 + r_nav))
            lots_prev = lots
            h_prev = h
        check("NAV identity: simulate == independent hand loop (H1/x2)",
              np.allclose(sim_h1["series"], exp_ser, atol=1e-9))

        # ---- BETA machinery: pure-phase OLS + caps + fallback (float32
        # cache roundtrip: 1e-4 tolerance face, exact-in-float64 math)
        sim_beta = simulate(P, masks20, n_ks20, beta_mode="beta",
                            cost_mult=2.0, want_audit=True)
        bl = sim_beta["beta_list"]
        # t=40 window days 1..40 all phase A -> 1.2
        check("beta OLS ~1.2 (pure phase A, t=40, float32 tol)",
              abs(bl[2] - 1.2) < 1e-4)
        # t=120 all phase B -> 3.0 -> capped 1.5
        check("beta cap upper 1.5 (phase B, t=120)", bl[6] == 1.5)
        # t=180 all phase C -> 0.1 -> floored 0.5
        check("beta floor 0.5 (phase C, t=180)", bl[9] == 0.5)
        # t=240 window [181,240] all phase D -> 1.0
        check("beta back to ~1.0 (pure phase D, t=240, float32 tol)",
              abs(bl[12] - 1.0) < 1e-4)
        check("beta fallbacks == 2 (t=0 and t=20 windows <30 pairs)",
              sim_beta["beta_fallbacks"] == 2)

        # ---- hedge lots: blocked day keeps old lots; short sign
        ll = sim_beta["lots_list"]
        check("lots short-signed (all <= 0)", all(v <= 0 for v in ll))
        check("blocked rebalance keeps old lots (planted +13% open "
              "at joint 181)", ll[9] == ll[8]
              and sim_beta["blocked"] >= 1)
        # lots formula hand check (t=240 exec): replay the per-period NAV
        # products (identical float path) + the ACTUAL beta the sim used
        # (beta_list is rounded 6dp; +/-1 lot = rounding-boundary face)
        k22 = 12
        nav_replay = float(NAV0)
        ser_b = sim_beta["series"]
        for kk in range(k22):
            a0, b0 = P["sig_days"][kk] + 1, P["sig_days"][kk + 1] + 1
            nav_replay *= float(np.prod(1.0 + ser_b[a0:b0]))
        px = float(P["ic_o"][P["exec_days"][k22]])
        exp_lots = int(-round(bl[k22] * 0.8 * nav_replay / (px * 200)))
        check("lots formula hand check (t=240 exec, +/-1 rounding face)",
              abs(ll[k22] - exp_lots) <= 1)

        # ---- margin budget gate unit (synthetic bind)
        gated = apply_margin_gate(-10000, 5000.0, 1.0e8, 200, 0.14)
        check("margin gate shrinks to fit (|lots|*200*5000*0.14 <= 1e8)",
              gated == -714)

        # ---- cost twins: vectorized V2 == scalar side_cost_v2
        rng = np.random.default_rng(7)
        gs = np.concatenate([rng.uniform(50, 3e5, 200),
                             [5.0, 5000.0, 20000.0, 200000.0]])
        advs = np.concatenate([rng.uniform(1e6, 9e8, 200),
                               [np.nan, 9.99e7, 1.0e8, 5.0e8]])
        v1 = v2_side_cost_vec(gs, advs, 1.0)
        s1 = np.array([side_cost_v2(g, a) for g, a in zip(gs, advs)])
        v2 = v2_side_cost_vec(gs, advs, 2.0)
        s2_ = np.array([side_cost_x2(g, a) for g, a in zip(gs, advs)])
        check("v2_side_cost_vec == side_cost_v2 pointwise (incl. floor/"
              "NaN/tier faces)",
              np.allclose(v1, s1, rtol=0, atol=1e-9))
        check("v2_side_cost_vec(x2) == side_cost_x2 pointwise",
              np.allclose(v2, s2_, rtol=0, atol=1e-9))
        check("x2 == 2x V2 pointwise identity",
              np.allclose(2.0 * s1, s2_, rtol=0, atol=1e-9))

        # ---- both faces + B7b contract leg (r297): every stats key
        # subscripted downstream exists in cell_stats
        cells_out = {}
        for cell in CELLS:
            W = cell["W"]
            mm, nk = (masks20, n_ks20) if W == 20 else (m60, n_ks60)
            cells_out[cell["name"]] = {}
            for face in ("x1", "x2"):
                r = simulate(P, mm, nk, beta_mode=cell["beta_mode"],
                             cost_mult=2.0 if face == "x2" else 1.0,
                             want_audit=True)
                cells_out[cell["name"]][face] = {
                    "series": r["series"],
                    "stats": cell_stats(
                        r["series"],
                        P["jcal"].values.astype("datetime64[D]")),
                    "n_rebalances": r["n_rebalances"],
                    "n_entries": r["n_entries"],
                    "audit": {k2: v2_ for k2, v2_ in r.items()
                              if k2 not in ("series", "n_rebalances",
                                            "n_entries")}}
        stc = cell_stats(cells_out["MN-REV20-H1"]["x2"]["series"],
                         P["jcal"].values.astype("datetime64[D]"))
        check("B7b cell_stats downstream key contract (sharpe_full/ann_ret/"
              "max_dd/oos_ann/oos_sharpe/n_days all present, non-None)",
              {"sharpe_full", "ann_ret", "max_dd", "oos_ann",
               "oos_sharpe", "n_days"} <= set(stc)
              and stc["sharpe_full"] is not None
              and stc["oos_ann"] is not None)
        check("H1 vs BETA differ only via beta (same masks/costs)",
              not np.allclose(cells_out["MN-REV20-BETA"]["x2"]["series"],
                              cells_out["MN-REV20-H1"]["x2"]["series"]))
        check("stable basket: n_entries == 3 (first period only)",
              cells_out["MN-REV20-H1"]["x2"]["n_entries"] == 3)

        # ---- crash-year face: fixture has no planted crash; synthetic
        # -40% series must flag (positive detection leg)
        cy = crash_years(cells_out["MN-REV20-H1"]["x2"]["series"],
                         P["jcal"].values.astype("datetime64[D]"))
        check("crash-year face clean on fixture (no planted crash)",
              cy["no_crash_year"] and len(cy["yearly_returns"]) >= 1)
        crash_ser = np.zeros(P["T_j"])
        crash_ser[:] = 0.0005
        crash_ser[100:320] = -0.004    # deep synthetic crash year (~-44%)
        cy2 = crash_years(crash_ser,
                          P["jcal"].values.astype("datetime64[D]"))
        check("crash-year face flags a synthetic crash year",
              not cy2["no_crash_year"] and len(cy2["crash_years"]) >= 1)
        ew_st = cell_stats(P["ew"],
                           P["jcal"].values.astype("datetime64[D]"))
        ic_st = cell_stats(P["r_ic"],
                           P["jcal"].values.astype("datetime64[D]"))
        check("passive baselines finite (unhedged_ew + ic_replication)",
              np.isfinite(ew_st["sharpe_full"])
              and np.isfinite(ic_st["sharpe_full"]))

        # ---- nulls: deterministic + sharded pools
        v1n = null_draw(P, CELLS[2], n_ks20, 0)
        v2n = null_draw(P, CELLS[2], n_ks20, 0)
        check("null draw deterministic (seed SEED+k)",
              v1n == v2n and np.isfinite(v1n))
        nulls = {}
        for c in CELLS:
            nk = n_ks20 if c["W"] == 20 else n_ks60
            nulls[c["name"]] = run_cell_nulls(P, c, nk)
        check("null pools 4 x 30 finite", len(nulls) == 4 and all(
            len(v["values"]) == 30 and np.isfinite(v["values"]).all()
            for v in nulls.values()))

        # ---- vstarts / robust / roll-day audit
        sbc = {n: cells_out[n]["x2"]["series"] for n in cells_out}
        vs = virtual_starts(P, sbc)
        check("vstarts census bounds",
              vs["n_starts"] == P["T_j"] - WIN_DAYS - STARTS_FROM)
        rb = robust_stats(sbc["MN-REV20-H1"])
        check("robust finite", np.isfinite(rb["obs_sharpe"]) and
              0.0 <= rb["sign_flip_p"] <= 1.0)
        audit = cells_out["MN-REV20-H1"]["x2"]["audit"]
        check("hedge audit faces present (lots/beta/h/margin lists)",
              {"lots_list", "beta_list", "h_list", "margin_peak"}
              <= set(audit) and len(audit["lots_list"]) == P["K"])

        # ---- sobol mini: deterministic, in-grid, finite
        mc = {20: (masks20, n_ks20), 60: (m60, n_ks60)}
        sb1 = run_sobol(P, mc)
        rows1 = [tuple(r) for r in sb1["rows"]]
        for f in os.listdir(SOBOL_DIR):
            os.remove(os.path.join(SOBOL_DIR, f))
        sb2 = run_sobol(P, mc)
        rows2 = [tuple(r) for r in sb2["rows"]]
        check("sobol deterministic + in-grid + finite",
              rows1 == rows2 and len(rows1) == 6 and all(
                  r[0] in SOBOL_W_GRID and r[1] in SOBOL_BW_GRID
                  and r[2] in SOBOL_CAP_GRID
                  and np.isfinite(r[3]) and np.isfinite(r[5])
                  for r in rows1))

        # ---- D6 stub (real member files read repo paths; hermetic tmp
        # has none -- arg face, SECTOR precedent)
        d6 = {"cells": {n: {"reject": False} for n in sbc}}

        # ---- finalize product (stubbed SG faces)
        res = finalize(P, cells_out, nulls, d6, vs,
                       {"MN-REV20-H1": rb}, sb1)
        check("finalize product", os.path.exists(OUT_JSON) and
              res["trials_ledger"]["total"] == 100)
        check("cutoff_meta + evidence_cutoff keys",
              "cutoff_meta" in res and
              res["evidence_cutoff"] == EVIDENCE_CUTOFF)
        check("hedge audit block in product (roll proxy + nav model)",
              "nav_model" in res and "roll_proxy" in
              res["panel"]["ic_face"])
        check("batch disclosure faces (crash years + cells_ok)",
              "cells_ok" in res["batch_disclosure"] and
              "crash_years_x2" in res["batch_disclosure"])
        att = json.load(open(ATT_JSON, encoding="utf-8"))
        check("attrition row entries face (r248)",
              att["entries"][-1]["batch"] == BATCH_NAME and
              "entries" in att["entries"][-1] and
              "rebalances_x2" in att["entries"][-1]["entries"])
    finally:
        SG.n_eff, SG.passive_baseline, SG.append_ledger = _ne, _pb, _al
        SG.ledger_head = _lh
        globals()["cscv_pbo"] = _real_cscv
        shutil.rmtree(tmp, ignore_errors=True)

    n_ok = sum(1 for _, v in ok if v)
    print(f"cn_mkneutral_p1 selftest: {n_ok}/{len(ok)} PASS")
    for name, v in ok:
        if not v:
            print(f"  FAIL: {name}")
    return 0 if n_ok == len(ok) else 1


def K_FIX(P):
    """selftest helper: K bound mirror of the driver schedule."""
    return P["K"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "selftest"])
    a = ap.parse_args()
    if a.cmd == "selftest":
        return cmd_selftest()
    if os.path.exists(OUT_JSON) and \
            os.environ.get("CN_MKTNEUTRAL_P1_REFINALIZE") != "1":
        print("idempotent no-op: p1_results.json exists "
              "(CN_MKTNEUTRAL_P1_REFINALIZE=1 = only redo)")
        return 0
    return cmd_run()


if __name__ == "__main__":
    sys.exit(main())
