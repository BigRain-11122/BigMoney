"""FUND-VALUE-P1 batch runner -- fundamental value family (low-PE / low-PB)
stock cross-sectional MONTHLY-rebalance new-family main-exam judged batch.

Prereg (FROZEN, r599 data gates green): research/FUND-VALUE-P1.md.
Ticket: T-2026-10-02-150-P1. CEO order chain O-20261002-2115 sec.1.1
-> T-145 leg(c) first fundamental family. Lane host bm-a (p1c_stock
panel local + value faces TRANSFER landed + probe green r599).

Semantics (prereg sec.3, frozen):
  signal day = first trading day of each month t; value face =
  forward-fill of the latest anchor_date <= t (PIT law, as-published
  snapshot face); frozen mask M = close/volume/amount alive AND
  amt20-median >= 1e7 AND listed >= 252td AND P4_BATCH2-s2-verbatim
  as-of-date ST-regime/delisting exclusions AND valuation bands
  pe_ttm in (0,200] AND pb in (0,20]; cell A VALUE-PE = Top-20 lowest
  pe_ttm (HEADLINE), cell B VALUE-PB = Top-20 lowest pb; eq weights
  1/N; ALWAYS-ON; monthly rebalance, engine-canonical T+1 open exec
  (O-1132 conservative proxy). Exit axis = 2 hold-through: members
  leave ONLY via rank rotation (exit_signal = entry <= 0, full-matrix
  injection).

Exit-stack dual-channel disable (sec.0.6, r522 E1 face):
  params channel (bridge-reachable, 4 keys): take_profit_levels=(),
  trailing_stop_activate=1e12, initial_stop=-1.0, time_decay_period=1e9
  ExitPatch channel (live.paper ExitConfig factory, 2 keys):
  loss_time_days=1e9, global_hard_limit=1e9
  Mutual-exclusion key-set assert = selftest leg F11 (dead-letter
  regression guard). engine/ zero-touch.

Costs (CN-C7, single source): stock V1 = 13.041 bp/side ==
  rev_osc_stock_p1.COST_X1 (imported, never hand-copied; runner
  asserts identity) == engine default FeeSchedule face (knowledge/
  cost_spec Face A x1). x2 face = CostPatch(2.0) = 26.082 bp/side.
  ETF-vs-stock comparability holds only under this convention.

N_eff = 2,004 = 4 judged cells (2 rules x 2 cost faces) + 2,000
  same-mask random-selection nulls. Sensitivity (500 draws) is
  descriptive only, never counts toward N_eff (sec.0).

Pools (6 entries, O-20260924-2100 execution-face split): 4 cell-face
  units (401 starts each + cont face), NULLS (2000 draws, checkpoint
  JSONL done-key skip), SENS (500 draws). workers=32 BelowNormal
  (O-20261002-2158 width law, frozen-prereg alignment r597).

Nulls (RANDOM_LARGE_SAMPLE_LAW sec.3 verbatim): per draw k, each month
  the SAME headline mask universe M, N=20 uniform random picks,
  rng([20500000, k]) substream law, eq weights, same execution,
  full-panel continuous run -> Sharpe distribution (G1' skill-line
  source). G-MASK: null day universe == real cell day universe
  bit-for-bit (holds by construction, selftest leg asserts).

Sensitivity draws rng([20500500, k]): uniform over
  N in {10,15,20} x pe_cap in {100,200} x rule in {pe,pb}; monthly
  fixed; descriptive only.

Law-A post-burn exit-reason census (LOWAMP-P2 sec.9, carried per
  O-20261002-2115): headline re-run through the SAME frozen machinery;
  the ONLY lawful reason on the hold-through face is signal_reversal;
  default-stack share > CENSUS_BLOCK_SHARE (0.20) -> consumption-blocked.

Engine face: engine.run_backtest per-symbol sub-account decomposition
  + eq weight mapping via entry_size_scale (weights shift(1) to the
  execution day, engine contract). T+1 and cost model untouched.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

sys.path.insert(0, "scripts")
sys.path.insert(0, ".")

import numpy as np
import pandas as pd

from live.paper import ExitPatch
from t22_virtual_timepoints import _slice_metrics, regime_proxy
from science_gates import (
    CostPatch, SEED_REGISTRY, append_ledger, closed_family_check,
    cutoff_meta, deflated_sharpe_ratio, g1_prime_v2, g2_registration_v2,
    t_from_sharpe, m1_t_value_gate,
)
from rev_osc_stock_p1 import COST_X1          # CN-C7 single source
from cn_rev_tilt_p1 import REG6, load_member_rets

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TICKET = "T-2026-10-02-150-P1"
PREREG = os.path.join(ROOT, "research", "FUND-VALUE-P1.md")
OUT_DIR = os.path.join(ROOT, "results", "fund_value_p1")
LOG_DIR = os.path.join(OUT_DIR, "logs")
PROBE_JSON = os.path.join(OUT_DIR, "probe.json")
OUT_JSON = os.path.join(OUT_DIR, "fund_value_p1_results.json")
OUT_CSV = os.path.join(OUT_DIR, "cells.csv")
ELIG_NPY = os.path.join(OUT_DIR, "_elig.npy")       # (T,N) frozen mask M
SIGVAL_NPY = os.path.join(OUT_DIR, "_sigvals.npy")  # (n_sig, N, 2) pe/pb

CUTOFF = pd.Timestamp("2026-09-22")          # prereg sec.2 D2 lockbox
BATCH_NAME = "FUND-VALUE-P1"
BATCH_CELLS = 2004                            # sec.0 N_eff verbatim
FAMILY_KEY = "fund_value_stock_xs"            # sec.1 M3 new key
CAPITAL = 1_000_000.0                         # CN-C7 nominal tier
WARMUP_TD = 252
W6M, W12M, W24M = 126, 252, 504
MIN_LISTED_TD = 252                           # sec.2 mask (listed >= 252td)
MIN_ACTIVE = 24                                # T-22 start census face
AMT20_WIN = 20
AMT20_MIN = 10_000_000.0                      # sec.2 liquidity floor (median)
PE_MIN, PE_MAX = 0.0, 200.0                   # frozen valuation band
PB_MIN, PB_MAX = 0.0, 20.0
TOP_N = 20                                    # sec.3 frozen
K_NULLS = 2000
SEED_NULLS = SEED_REGISTRY["fund_value_p1_nulls"]     # 20500000, r599 band
K_SENS = 500
SEED_SENS = SEED_REGISTRY["fund_value_p1_sens"]       # 20500500
BOOT_B = 2000                                  # block bootstrap B
BOOT_BLOCK = 21                                # block length (td)
D6_REJECT = 0.7                                # sec.1 D6
G_CENSUS_N = 401                               # sec.2 frozen start census
HEADLINE = "VALUE-PE"
OOS_FROM = pd.Timestamp("2025-01-01")          # descriptive OOS disclosure
CENSUS_WINDOW = ("1992-09-01", "2026-03-02")   # T-22 census window (probe)
CELLS = {"VALUE-PE": "pe_ttm", "VALUE-PB": "pb"}    # sec.3 cells A/B
FACES = ("base", "x2")
# sec.0.6 exit-axis HOLD-THROUGH: params channel = bridge-reachable
# keys ONLY; the two non-bridged keys ride ExitPatch (r522 E1 face)
EXIT_PARAMS_KEYS = {"take_profit_levels", "trailing_stop_activate",
                    "initial_stop", "time_decay_period"}
EXIT_PATCH_OVERRIDES = {"loss_time_days": 10 ** 9,
                        "global_hard_limit": 10 ** 9}
LAWFUL_EXIT_REASONS = ("signal_reversal",)
CENSUS_BLOCK_SHARE = 0.20
# single source for run_cell_portfolio AND the law-A census re-run
NEUTRALIZED_PARAMS = {
    "position_size_pct": 1.0, "max_positions": 1,
    "sizing_mode": "fixed_initial", "report_num_entries": True,
    "take_profit_levels": (),
    "trailing_stop_activate": 1e12,
    "initial_stop": -1.0,
    "time_decay_period": 10 ** 9,
}
F1_BM = 1e12                                   # trailing-stop neutral value
# P4_BATCH2 s2 ST-regime proxy constants (verbatim)
ST_WIN = 250
ST_SEAL5_MIN = 2
STALE_TD = 250
CHINEXT_20_FROM = np.datetime64("2020-08-24")
STAR_FROM_D = np.datetime64("2019-07-22")
# p1c cache face
CACHE_DIR = os.path.join(ROOT, "Money02", "data", "cache", "p1c_stock")
T_EXPECT, N_EXPECT = 8792, 5222
MASK_CSV = os.path.join(ROOT, "data", "fundamental", "b_layer_mask.csv")
PARQUET = os.path.join(ROOT, "data", "fund_history_export",
                       "value_faces.parquet")
ETF510300_CSV = os.path.join(ROOT, "data", "daily", "sh510300.csv")
FIELDS = ("open", "high", "low", "close", "volume", "amount", "pct_chg")

_G = {}   # per-worker globals
_CLAIM_STARTED = ""


def _machine_id() -> str:
    try:
        return json.load(open(os.path.join(ROOT, "fleet", "machine.json"),
                              encoding="utf-8"))["machine_id"]
    except Exception:
        return "unknown"


def _log(name: str, msg: str):
    os.makedirs(LOG_DIR, exist_ok=True)
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(os.path.join(LOG_DIR, name + ".log"), "a", encoding="utf-8") as fh:
        fh.write(f"{stamp} {msg}\n")


def _dump(obj, path):
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=2, sort_keys=True)


def _now_iso() -> str:
    import datetime
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


# ------------------------------------------------------------------ data face

def load_axis() -> tuple:
    """p1c_stock frozen cache: memmap 7-field face + dates + syms.
    syms = P1C canonical loader single source (bars glob order == cache
    column order, p1c_stock_ic_batch.load_universe contract); the
    b_layer_mask csv only supplies the board dict keyed by code (row
    order deliberately NOT consumed). Anchor-facts gate mirrors probe
    leg1 (fail-closed)."""
    import p1c_stock_ic_batch as P1C
    idx, syms, meta = P1C.load_universe()
    assert len(idx) == T_EXPECT, "cache T drift"
    assert len(syms) == N_EXPECT, "cache N drift"
    mask = pd.read_csv(MASK_CSV, dtype={"code": str})
    assert len(mask) == N_EXPECT, "b_layer_mask row census drift"
    F = {f: np.load(os.path.join(CACHE_DIR, f + ".npy"), mmap_mode="r")
         for f in FIELDS}
    for f in FIELDS:
        assert F[f].shape == (T_EXPECT, N_EXPECT), f"cache {f} shape drift"
    assert str(idx[-1].date()) == "2026-09-22", "panel end drift (cutoff)"
    board = mask.set_index("code")["board"].to_dict()
    return idx, syms, F, board, meta


def _roll_sum(x: np.ndarray, w: int) -> np.ndarray:
    """Rolling sum axis 0, NaN-free float array, full windows (P4_BATCH2
    verbatim helper semantics -- imported face, not rewritten)."""
    cs = np.cumsum(x, axis=0, dtype=np.float64)
    out = np.full(x.shape, np.nan, dtype=np.float64)
    if len(out) > w:
        out[w:] = cs[w:] - cs[:-w]
        out[w - 1] = cs[w - 1]
    return out


def build_elig(idx, F, board, syms) -> np.ndarray:
    """Frozen mask M face (prereg sec.2): liquidity/listing/alive +
    P4_BATCH2 s2 verbatim as-of-date ST-regime + delisting(stale)
    exclusions + valuation bands. bool (T, N)."""
    close = F["close"]
    fin = np.isfinite(close)
    vol_ok = np.greater(F["volume"], 0, where=fin, out=np.zeros_like(fin, bool))
    amt_ok = np.greater(F["amount"], 0, where=fin, out=np.zeros_like(fin, bool))
    # amt20 median over trailing 20 td (sec.2: MEDIAN, frozen -- differs
    # from the P4_BATCH2 mean face by design)
    amt = np.where(fin, F["amount"], np.nan).astype(np.float64)
    amt20 = (pd.DataFrame(amt).rolling(AMT20_WIN, min_periods=AMT20_WIN)
             .median().to_numpy())
    amt20_ok = np.isfinite(amt20) & (amt20 >= AMT20_MIN)
    listed = np.cumsum(fin, axis=0) >= MIN_LISTED_TD
    # stale / delisting (P4_BATCH2 s2 verbatim): last valid bar > 250 td
    lvidx = np.where(fin, np.arange(T_EXPECT)[:, None], -1)
    last_valid = np.maximum.accumulate(lvidx, axis=0)
    stale = ((np.arange(T_EXPECT)[:, None] - last_valid) > STALE_TD) \
        | (last_valid < 0)
    # ST-regime proxy (P4_BATCH2 s2 verbatim, board-aware): rolling-250d
    # sealed-5% days >= 2 AND sealed-10% days == 0 on 10%-threshold
    # segments (main board always; chinext before 2020-08-24)
    hi = F["high"]
    pct = F["pct_chg"]
    is_main = np.zeros((T_EXPECT, N_EXPECT), dtype=bool)
    is_cx = np.zeros((T_EXPECT, N_EXPECT), dtype=bool)
    is_star = np.zeros((T_EXPECT, N_EXPECT), dtype=bool)
    for j, c in enumerate(syms):
        b = board.get(c)
        if b == "main":
            is_main[:, j] = True
        elif b == "chinext":
            is_cx[:, j] = True
        elif b == "star":
            is_star[:, j] = True
    cx20 = (idx.values >= CHINEXT_20_FROM)[:, None]
    thr = np.full((T_EXPECT, N_EXPECT), np.nan, dtype=np.float32)
    thr[is_main] = 0.10
    thr[is_star] = 0.20
    thr[is_cx & ~cx20] = 0.10
    thr[is_cx & cx20] = 0.20
    s5 = (fin & (close == hi) & (pct >= 4.6) & (pct <= 5.4)).astype(np.float64)
    s10 = (fin & (close == hi) & (pct >= 9.4) & (pct <= 10.6)).astype(np.float64)
    r5 = _roll_sum(s5, ST_WIN)
    r10 = _roll_sum(s10, ST_WIN)
    with np.errstate(invalid="ignore"):
        st_seg = (r5 >= ST_SEAL5_MIN) & (r10 == 0) & (thr == 0.10)
    st_seg = np.where(np.isnan(r5), False, st_seg)
    del s5, s10, r5, r10, thr, is_main, is_cx, is_star, cx20
    # valuation bands (sec.2: selection-eligibility layer over the
    # forward-filled value face -- computed per signal row below; here
    # the mask M skeleton carries the non-valuation clauses)
    base = fin & vol_ok & amt_ok & amt20_ok & listed & ~stale & ~st_seg
    return base


def month_first_positions(idx: pd.DatetimeIndex) -> list:
    """Signal-day rows: first trading day of each month, census window
    bounds applied (T-22 monthly enumeration face, probe-frozen)."""
    lo = pd.Timestamp(CENSUS_WINDOW[0])
    hi = pd.Timestamp(CENSUS_WINDOW[1])
    mask = (idx >= lo) & (idx <= hi)
    sub = idx[mask]
    keys = sub.strftime("%Y-%m")
    out, prev = [], None
    for p, k in zip(np.where(mask)[0], keys):
        if k != prev:
            out.append(int(p))
            prev = k
    return out


def enumerate_starts(idx: pd.DatetimeIndex, close: np.ndarray) -> list:
    """T-22 monthly adapted: pos >= 252td AND >= 126td forward AND
    active members >= 24 (raw close notna). G-CENSUS: == 401."""
    starts = []
    for p in month_first_positions(idx):
        if p < WARMUP_TD or (T_EXPECT - 1 - p) < 126:
            continue
        if int((~np.isnan(close[p])).sum()) < MIN_ACTIVE:
            continue
        starts.append(p)
    return starts


def build_sigvals(idx, syms) -> tuple:
    """Value-face forward-fill at each signal row (PIT law): latest
    anchor_date <= t. Returns (sig_positions, pe (n_sig,N) f32,
    pb (n_sig,N) f32). Signals span [t0 first month with coverage gate
    satisfied per probe, end of panel] -- pre-t0 months below-floor by
    probe evidence are skipped honestly. Vectorized: ONE searchsorted
    call per symbol over all signal dates (210w-call python loop is a
    5-min stall -- this face is ~10s)."""
    df = pd.read_parquet(PARQUET)
    d = df.assign(_d=df["anchor_date"].astype("string")
                  .str.replace("-", "", regex=False).astype("int64"))
    sig_pos = month_first_positions(idx)
    sig_pos = [p for p in sig_pos if idx[p] >= FIRST_SIG_DATE]
    sig_dates = np.array([int(idx[p].strftime("%Y%m%d")) for p in sig_pos])
    n = len(sig_pos)
    pe = np.full((n, N_EXPECT), np.nan, dtype=np.float32)
    pb = np.full((n, N_EXPECT), np.nan, dtype=np.float32)
    sym_row = {s: j for j, s in enumerate(syms)}
    d = d.sort_values(["code", "_d"], kind="stable")
    codes = d["code"].to_numpy()
    jd = d["_d"].to_numpy()
    ape = d["pe_ttm"].to_numpy(dtype=float)
    apb = d["pb"].to_numpy(dtype=float)
    # group boundaries per code (stable-sorted)
    starts_g = np.flatnonzero(np.r_[True, codes[1:] != codes[:-1]])
    ends_g = np.r_[starts_g[1:], len(codes)]
    for gi in range(len(starts_g)):
        j = sym_row.get(str(codes[starts_g[gi]]))
        if j is None:
            continue
        s, e = starts_g[gi], ends_g[gi]
        ad = jd[s:e]
        k = np.searchsorted(ad, sig_dates, side="right") - 1
        ok = k >= 0
        if not ok.any():
            continue
        kk = np.where(ok, k, 0)
        pev = ape[s:e][kk]
        pbv = apb[s:e][kk]
        okv = ok & np.isfinite(pev)
        pe[okv, j] = pev[okv].astype(np.float32)
        okv = ok & np.isfinite(pbv)
        pb[okv, j] = pbv[okv].astype(np.float32)
    return sig_pos, pe, pb


def build_signal(rule: str, elig_sig: np.ndarray, pe: np.ndarray,
                 pb: np.ndarray, top_n: int = TOP_N,
                 pe_max: float = PE_MAX) -> tuple:
    """Monthly cross-sectional value rank over the frozen mask M
    (sec.3): ascending valuation rank -> Top-N lowest, eq 1/N weights.
    elig_sig: (n_sig, N) bool mask at signal rows (M incl. bands).
    Returns (entry bool (n_sig,N), weights f32 (n_sig,N))."""
    key = pe if rule == "pe_ttm" else pb
    other = pb if rule == "pe_ttm" else pe
    other_max = PB_MAX if rule == "pe_ttm" else pe_max
    band = ((pe > PE_MIN) & (pe <= pe_max) & np.isfinite(pe)
            & (other > PB_MIN) & (other <= other_max) & np.isfinite(other))
    universe = elig_sig & band
    n_sig = elig_sig.shape[0]
    entry = np.zeros((n_sig, N_EXPECT), dtype=bool)
    weights = np.full((n_sig, N_EXPECT), np.nan, dtype=np.float32)
    for i in range(n_sig):
        cols = np.where(universe[i])[0]
        if cols.size == 0:
            continue
        kv = key[i, cols]
        order = cols[np.argsort(kv, kind="stable")[:min(top_n, cols.size)]]
        entry[i, order] = True
        weights[i, order] = 1.0 / order.size
    return entry, weights


# ------------------------------------------------------------- engine face

def prices_window(F, idx, j: int, lo: int, hi: int) -> dict:
    """Per-symbol engine window dict (T+1/cost machinery untouched)."""
    sl = slice(lo, hi + 1)
    df = pd.DataFrame({
        "open": np.asarray(F["open"][sl, j]),
        "high": np.asarray(F["high"][sl, j]),
        "low": np.asarray(F["low"][sl, j]),
        "close": np.asarray(F["close"][sl, j]),
        "volume": np.asarray(F["volume"][sl, j]),
        "amount": np.asarray(F["amount"][sl, j]),
    }, index=idx[sl])
    return df


def run_cell_portfolio(F, idx, entry_sig, sig_pos, weights, face: str,
                       active: list, sdate, e) -> dict:
    """Engine-canonical run of one cell window (per-symbol sub-account
    decomposition; weights map to the execution day via shift-by-one
    signal-row alignment -- monthly rows land on the next bar)."""
    from engine import run_backtest
    from contextlib import nullcontext
    params = dict(NEUTRALIZED_PARAMS)
    lo = 0 if sdate is None else sdate
    hi = T_EXPECT - 1 if e is None else e
    win_idx = idx[lo:hi + 1]
    lo_sig, hi_sig = _sig_span(sig_pos, lo, hi)
    pnl = None
    n_trades = n_entries = 0
    trade_dates = []
    for j in active:
        w = prices_window(F, idx, j, lo, hi)
        if not np.isfinite(w["close"].to_numpy()).any():
            continue
        ent, sc = _sym_entry_scale(entry_sig, sig_pos, weights, j,
                                   lo_sig, hi_sig, win_idx, lo)
        with ExitPatch(EXIT_PATCH_OVERRIDES), \
             (CostPatch(2.0) if face == "x2" else nullcontext()):
            res = run_backtest({str(j): w}, params,
                               entry_signal=ent,
                               exit_signal=ent <= 0,
                               entry_size_scale=sc)
        eq = pd.Series(res["equity_curve"], index=w.index[:len(res["equity_curve"])])
        p = (eq - CAPITAL).reindex(win_idx).ffill().fillna(0.0)
        pnl = p if pnl is None else pnl + p
        n_trades += len(res["trades"])
        n_entries += int(res["metrics"].get("num_entries", 0))
        for tr in res["trades"]:
            trade_dates.append(pd.Timestamp(tr["date"]))
    if pnl is None:
        return None
    return {"pnl": pnl, "n_trades": n_trades, "n_entries": n_entries,
            "trade_dates": trade_dates}


def _sig_span(sig_pos, lo, hi):
    """Signal-row index span covering window rows [lo, hi]."""
    lo_sig = 0
    hi_sig = len(sig_pos) - 1
    for i, p in enumerate(sig_pos):
        if p >= lo:
            lo_sig = i
            break
    for i in range(len(sig_pos) - 1, -1, -1):
        if sig_pos[i] <= hi:
            hi_sig = i
            break
    return lo_sig, hi_sig


def _sym_entry_scale(entry_sig, sig_pos, weights, j, lo_sig, hi_sig,
                     win_idx, lo_bar):
    """Per-symbol entry bool + exec-day weight Series on win_idx bars.
    Engine contract: signal row p carries entry=True (engine enters on
    the NEXT bar open, T+1 canonical); the signal-row weight maps to
    bar p+1 = the execution day (positional shift, O-1132 face)."""
    n = len(win_idx)
    ent = np.zeros(n, dtype=bool)
    sc = np.full(n, np.nan)
    for i in range(lo_sig, hi_sig + 1):
        if not entry_sig[i, j]:
            continue
        p_pos = int(sig_pos[i]) - int(lo_bar)
        if p_pos < 0 or p_pos >= n:
            continue
        ent[p_pos] = True
        if p_pos + 1 < n:
            sc[p_pos + 1] = float(weights[i, j])
    return (pd.DataFrame(ent, index=win_idx, columns=["s"]),
            pd.Series(sc, index=win_idx, dtype=float))


# ------------------------------------------------------------------ workers

def _init_worker():
    import psutil
    pri = getattr(psutil, "BELOW_NORMAL_PRIORITY_CLASS", None)
    if pri is not None:
        try:
            psutil.Process().nice(pri)   # CEO 10% CPU headroom law
        except Exception:
            pass
    idx, syms, F, board, meta = load_axis()
    elig = np.load(ELIG_NPY, mmap_mode="r")     # frozen mask M (T, N)
    sig_pos = _signal_positions(idx)            # pure date logic
    arr = np.load(SIGVAL_NPY, mmap_mode="r")    # (n_sig, N, 2) frozen
    pe = arr[:, :, 0]
    pb = arr[:, :, 1]
    regime = _regime_face(idx)
    _G.update(idx=idx, syms=syms, F=F, board=board, elig=elig,
              sig_pos=sig_pos, pe=pe, pb=pb, regime=regime, _sig={})


FIRST_SIG_DATE = pd.Timestamp("1994-05-03")   # probe leg3 t0 (frozen)


def _signal_positions(idx) -> list:
    """Signal rows: month-first bars within the census window, from the
    frozen first-signal date t0 (pre-t0 months are below-floor by probe
    evidence -> skipped honestly). Pure date logic, no data IO."""
    pos = month_first_positions(idx)
    return [p for p in pos if idx[p] >= FIRST_SIG_DATE]


def _regime_face(idx) -> pd.Series | None:
    """510300 t22 3-way proxy (sec.3): from the daily csv (in-place since
    2012-05; pre-2012 starts carry 'na' honestly -- G-SEG counts only
    labelled segments)."""
    if not os.path.exists(ETF510300_CSV):
        return None
    df = pd.read_csv(ETF510300_CSV)
    df["date"] = pd.to_datetime(df["date"])
    s = df.set_index("date")["close"].sort_index()
    if len(s) < 210:
        return None
    return regime_proxy(s)


def _band_at(pe, pb, sig_pos, pos):
    """Valuation-band bool row (N,) at the signal row covering bar pos
    (the latest signal row at or before pos; pre-t0 = all-False, honest
    -- no passive universe before the first signal row)."""
    i = None
    for k, p in enumerate(sig_pos):
        if p <= pos:
            i = k
        else:
            break
    if i is None:
        return np.zeros(pe.shape[1], dtype=bool)
    return (((pe[i] > PE_MIN) & (pe[i] <= PE_MAX) & np.isfinite(pe[i])
             & (pb[i] > PB_MIN) & (pb[i] <= PB_MAX) & np.isfinite(pb[i]))
            .astype(bool))


def _elig_sig_rows(elig, sig_pos) -> np.ndarray:
    """(n_sig, N) bool: frozen mask M at each signal row."""
    return np.asarray(elig[sig_pos, :])


def _cell_task(payload):
    """One (cell, startpoint, face) row -- t22 pattern: longest window
    once, 6m/12m/24m sliced off the same equity curve; passive = EW
    B&H of the MASK members at the start over the identical span."""
    cell, pos, face = payload["cell"], payload["pos"], payload["face"]
    rule = CELLS[cell]
    cache = _G.setdefault("_sig", {})
    if rule not in cache:
        es = _elig_sig_rows(_G["elig"], _G["sig_pos"])
        cache[rule] = build_signal(rule, es, _G["pe"], _G["pb"])
    entry_sig, weights = cache[rule]
    F, idx, sig_pos = _G["F"], _G["idx"], _G["sig_pos"]
    sdate = idx[pos]
    e = idx[min(pos + W24M - 1, T_EXPECT - 1)]
    lo_sig, hi_sig = _sig_span(sig_pos, pos, min(pos + W24M - 1, T_EXPECT - 1))
    span = range(lo_sig, hi_sig + 1)
    active = sorted({j for i in span for j in np.where(entry_sig[i])[0]})
    if active:
        run = run_cell_portfolio(F, idx, entry_sig, sig_pos, weights,
                                 face, active, pos, min(pos + W24M - 1,
                                                        T_EXPECT - 1))
    else:
        run = None
    win_idx = idx[pos:pos + W24M]
    if run is None:
        eq = pd.Series(CAPITAL, index=win_idx)
        trades = []
    else:
        eq = (run["pnl"] + CAPITAL).reindex(win_idx).ffill().fillna(CAPITAL)
        trades = [{"date": d} for d in run["trade_dates"]]
    m6 = _slice_metrics(eq, trades, W6M)
    m12 = _slice_metrics(eq, trades, W12M)
    m24 = _slice_metrics(eq, trades, W24M)
    # passive: EW B&H of mask-M members alive at start -- M INCLUDES the
    # frozen valuation bands (sec.2 mask block carries the eligibility
    # clauses; band row derived on the signal row at/preceding the start)
    close = F["close"]
    base_row = np.asarray(close[pos])
    mask_row = np.asarray(_G["elig"][pos])
    band_row = _band_at(_G["pe"], _G["pb"], _G["sig_pos"], pos)
    syms_idx = np.where(np.isfinite(base_row) & mask_row & band_row)[0]
    if syms_idx.size:
        rel = np.full((W24M, syms_idx.size), np.nan)
        for k, j in enumerate(syms_idx):
            col = np.asarray(close[pos:pos + W24M, j])
            rel[:, k] = col / base_row[j]
        pnav = np.nanmean(rel, axis=1)
        pser = pd.Series(pnav, index=win_idx)
    else:
        pser = pd.Series(1.0, index=win_idx)
    p6 = _slice_metrics(pser, [], W6M)
    p12 = _slice_metrics(pser, [], W12M)
    p24 = _slice_metrics(pser, [], W24M)
    reg = _G.get("regime")
    rlabel = "na"
    if reg is not None and sdate in reg.index:
        rlabel = str(reg.loc[sdate])
    return {"key": f"{cell}|{face}|{pos}", "cell": cell, "face": face,
            "pos": pos, "start": str(sdate.date()), "regime": rlabel,
            "n_mask_members": int(syms_idx.size), "n_active": len(active),
            "partial_12m": m12["n_bars"] < W12M,
            "partial_24m": m24["n_bars"] < W24M,
            "ret_6m": m6["ret"], "ret_12m": m12["ret"], "ret_24m": m24["ret"],
            "p_ret_6m": p6["ret"], "p_ret_12m": p12["ret"],
            "p_ret_24m": p24["ret"],
            "dd_6m": m6["dd"], "dd_12m": m12["dd"], "dd_24m": m24["dd"],
            "sharpe_6m": m6["sharpe"], "sharpe_12m": m12["sharpe"],
            "sharpe_24m": m24["sharpe"],
            "trades_6m": m6["trades"], "trades_12m": m12["trades"],
            "trades_24m": m24["trades"],
            "beat_6m": m6["ret"] > p6["ret"],
            "beat_12m": m12["ret"] > p12["ret"],
            "beat_24m": m24["ret"] > p24["ret"]}


def _cont_task(payload):
    """Continuous full-panel run of one (cell, face) -- the
    headline/G1'/M1/DSR/x2/PBO supply face."""
    cell, face = payload["cell"], payload["face"]
    rule = CELLS[cell]
    es = _elig_sig_rows(_G["elig"], _G["sig_pos"])
    entry_sig, weights = build_signal(rule, es, _G["pe"], _G["pb"])
    active = sorted({j for i in range(len(_G["sig_pos"]))
                     for j in np.where(entry_sig[i])[0]})
    run = run_cell_portfolio(_G["F"], _G["idx"], entry_sig, _G["sig_pos"],
                             weights, face, active, None, None)
    F, idx = _G["F"], _G["idx"]
    nav = (run["pnl"] + CAPITAL).reindex(idx).ffill().fillna(CAPITAL)
    rets = nav.pct_change().dropna()
    from engine.metrics import max_drawdown, sharpe
    yrs = len(nav) / 252.0
    row = {"key": f"cont|{cell}|{face}", "cell": cell, "face": face,
           "sharpe_full": round(float(sharpe(nav)), 6),
           "ret_full": round(float(nav.iloc[-1] / nav.iloc[0] - 1), 6),
           "ann_ret": round(float((nav.iloc[-1] / nav.iloc[0])
                                  ** (1 / yrs) - 1), 6),
           "max_dd": round(float(max_drawdown(nav)), 6),
           "n_trades": run["n_trades"], "n_entries": run["n_entries"],
           "trades_per_year": round(run["n_trades"] / yrs, 3),
           "n_days": int(len(nav)), "nav_last": round(float(nav.iloc[-1]), 2),
           "n_active_members": len(active)}
    # OOS descriptive (sec.4): post-2025 dual-positive face
    oos = rets[rets.index >= OOS_FROM]
    row["oos_sharpe"] = (round(float((oos.mean() / oos.std(ddof=1))
                                     * np.sqrt(252)), 6)
                         if len(oos) > 30 and oos.std(ddof=1) > 0 else None)
    row["oos_ret"] = (round(float((1 + oos).prod() - 1), 6)
                      if len(oos) else None)
    row["returns"] = [round(float(x), 8) for x in rets.to_numpy()]
    row["return_dates"] = [str(d.date()) for d in rets.index]
    return row


def _null_task(payload):
    """Same-mask random-selection null draw k (sec.3 verbatim): per
    month, N=20 uniform picks from the HEADLINE (VALUE-PE) mask
    universe, eq weights, full-panel continuous run. G-MASK holds by
    construction (same universe frame)."""
    k = payload["k"]
    es = _elig_sig_rows(_G["elig"], _G["sig_pos"])
    entry_h, weights_h = build_signal(HEADLINE_RULE, es, _G["pe"], _G["pb"])
    universe = _headline_universe(es, _G["pe"], _G["pb"])
    rng = np.random.default_rng([SEED_NULLS, k])
    entry_sig = np.zeros_like(entry_h)
    weights = np.full_like(weights_h, np.nan, dtype=np.float32)
    for i in range(len(_G["sig_pos"])):
        cols = np.where(universe[i])[0]
        if cols.size < 2:
            continue
        pick = rng.choice(cols, size=min(TOP_N, cols.size), replace=False)
        entry_sig[i, pick] = True
        weights[i, pick] = 1.0 / pick.size
    active = sorted({j for i in range(entry_sig.shape[0])
                     for j in np.where(entry_sig[i])[0]})
    run = run_cell_portfolio(_G["F"], _G["idx"], entry_sig, _G["sig_pos"],
                             weights, "base", active, None, None)
    from engine.metrics import max_drawdown, sharpe
    nav = (run["pnl"] + CAPITAL).reindex(_G["idx"]).ffill().fillna(CAPITAL)
    rets = nav.pct_change().dropna()
    return {"key": f"null|{k}", "k": k,
            "sharpe": round(float(sharpe(nav)), 6),
            "ret": round(float(nav.iloc[-1] / nav.iloc[0] - 1), 6),
            "max_dd": round(float(max_drawdown(nav)), 6),
            "n_trades": run["n_trades"], "n_entries": run["n_entries"],
            "n_active_members": len(active),
            "n_selected_months": int(entry_sig.any(axis=1).sum())}


def _headline_universe(es, pe, pb):
    """Headline VALUE-PE mask universe (sec.3 null face): frozen mask M
    AND the frozen valuation bands (identical frame to the real cell --
    G-MASK bit-for-bit)."""
    band = ((pe > PE_MIN) & (pe <= PE_MAX) & np.isfinite(pe)
            & (pb > PB_MIN) & (pb <= PB_MAX) & np.isfinite(pb))
    return es & band


def _sens_task(payload):
    """Sensitivity draw k (sec.3 descriptive): uniform over N in
    {10,15,20} x pe_cap in {100,200} x rule in {pe,pb}; monthly fixed;
    full-panel continuous run. Never counts toward N_eff."""
    k = payload["k"]
    rng = np.random.default_rng([SEED_SENS, k])
    N = int(rng.choice(np.array([10, 15, 20])))
    pe_cap = float(rng.choice(np.array([100.0, 200.0])))
    rule = str(rng.choice(np.array(["pe_ttm", "pb"])))
    es = _elig_sig_rows(_G["elig"], _G["sig_pos"])
    entry_sig, weights = build_signal(rule, es, _G["pe"], _G["pb"],
                                      top_n=N, pe_max=pe_cap)
    active = sorted({j for i in range(entry_sig.shape[0])
                     for j in np.where(entry_sig[i])[0]})
    run = run_cell_portfolio(_G["F"], _G["idx"], entry_sig, _G["sig_pos"],
                             weights, "base", active, None, None)
    from engine.metrics import max_drawdown, sharpe
    nav = (run["pnl"] + CAPITAL).reindex(_G["idx"]).ffill().fillna(CAPITAL)
    return {"key": f"sens|{k}", "k": k, "N": N, "pe_cap": pe_cap,
            "rule": rule,
            "sharpe": round(float(sharpe(nav)), 6),
            "ret": round(float(nav.iloc[-1] / nav.iloc[0] - 1), 6),
            "max_dd": round(float(max_drawdown(nav)), 6),
            "n_trades": run["n_trades"],
            "n_active_members": len(active)}


HEADLINE_RULE = "pe_ttm"


# ------------------------------------------------------------------- checkpoint

def _shard_files(cell=None, face=None, kind=None):
    if kind == "nulls":
        return os.path.join(OUT_DIR, "nulls.jsonl")
    if kind == "sens":
        return os.path.join(OUT_DIR, "sens.jsonl")
    return os.path.join(OUT_DIR, f"cells_{cell}_{face}.jsonl")


def _done_keys(path: str) -> set:
    keys = set()
    if not os.path.exists(path):
        return keys
    lines = open(path, encoding="utf-8").read().splitlines()
    for i, ln in enumerate(lines):
        if not ln.strip():
            continue
        try:
            keys.add(json.loads(ln)["key"])
        except (json.JSONDecodeError, KeyError):
            if i == len(lines) - 1:
                continue        # truncated crash tail: skip honestly
            raise
    return keys


def _append_rows(path: str, rows: list):
    with open(path, "a", encoding="utf-8", newline="\n") as fh:
        for r in rows:
            fh.write(json.dumps(r, default=bool, sort_keys=True,
                                ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------- probe

def cmd_probe(args) -> int:
    d6_only = bool(getattr(args, "d6", False))
    os.makedirs(OUT_DIR, exist_ok=True)
    t0 = time.time()
    if d6_only:
        return _probe_d6_leg(t0)
    facts = {"ticket": TICKET, "batch": BATCH_NAME,
             "ts": time.strftime("%Y-%m-%d %H:%M:%S"), "checks": []}

    def chk(name, ok, detail=""):
        facts["checks"].append({"name": name, "pass": bool(ok),
                                "detail": str(detail)[:400]})
        return bool(ok)

    # cost single-source assert (CN-C7): stock V1 == rev_osc COST_X1
    chk("cost_x1_single_source", abs(COST_X1 - 0.0013041) < 1e-12,
        f"COST_X1={COST_X1} (13.041bp/side, roundtrip 26.082bp)")
    # M3 closed family (new key fund_value_stock_xs -> open expected)
    m3 = closed_family_check(FAMILY_KEY)
    chk("closed_family_open", m3.get("open") is True
        or m3.get("status") == "open",
        json.dumps(m3, ensure_ascii=False)[:200])
    # panel anchors (probe leg1 mirror)
    idx, syms, F, board, meta = load_axis()
    chk("panel_end_2026_09_22", str(idx[-1].date()) == "2026-09-22",
        str(idx[-1].date()))
    chk("panel_census", len(idx) == T_EXPECT and len(syms) == N_EXPECT,
        f"T={len(idx)} N={len(syms)}")
    # starts census (G-CENSUS 401)
    close = F["close"]
    starts = enumerate_starts(idx, close)
    chk("g_census_401", len(starts) == G_CENSUS_N,
        f"starts={len(starts)} want={G_CENSUS_N}")
    # frozen mask build + persist (launcher-side single build)
    elig = build_elig(idx, F, board, syms)
    np.save(ELIG_NPY, elig.astype(bool))
    sig_pos, pe, pb = build_sigvals(idx, syms)
    np.save(SIGVAL_NPY, np.stack([pe, pb], axis=2).astype(np.float32))
    es = np.asarray(elig[sig_pos, :])
    n_mask = es.sum(axis=1)
    facts["mask"] = {
        "amt20_min_yuan": AMT20_MIN, "listed_min_td": MIN_LISTED_TD,
        "stale_td": STALE_TD, "st_win": ST_WIN, "st_seal5_min": ST_SEAL5_MIN,
        "pe_band": [PE_MIN, PE_MAX], "pb_band": [PB_MIN, PB_MAX],
        "sig_rows": len(sig_pos),
        "mask_members_median": float(np.median(n_mask)),
        "mask_members_min": int(n_mask.min()),
        "first_sig": str(idx[sig_pos[0]].date()),
        "last_sig": str(idx[sig_pos[-1]].date()),
    }
    chk("mask_nonempty", int(n_mask.min()) >= TOP_N,
        f"min mask members per sig row={int(n_mask.min())}")
    # headline signal smoke: Top-20 selectability on every signal row
    entry_h, weights_h = build_signal(HEADLINE_RULE, es, pe, pb)
    picked = entry_h.sum(axis=1)
    chk("headline_top20_all_rows", bool((picked == TOP_N).all()),
        f"picked rows: min={int(picked.min())} max={int(picked.max())}")
    # eq weight identity (1/N exact)
    wv = weights_h[entry_h]
    chk("eq_weights_identity",
        bool(np.isfinite(wv).all()) and abs(float(wv.max()) - 1.0 / TOP_N) < 1e-9,
        f"w min={float(wv.min()):.6f} max={float(wv.max()):.6f}")
    # D6 same-family admission probe (sec.1): headline continuous daily
    # returns vs ALL six registered members, fail-closed. The leg is a
    # HEAVY full-panel engine burn (thousands of per-symbol full-history
    # runs) -> runs as the separate `probe --d6` sub-step (r324 inline-
    # timeout law); this fast face consumes its on-disk receipt.
    d6_path = os.path.join(OUT_DIR, "d6.json")
    if os.path.exists(d6_path):
        d6j = json.load(open(d6_path, encoding="utf-8"))
        facts["headline"] = d6j.get("headline")
        facts["d6"] = d6j.get("d6")
        chk("d6_admission",
            bool(d6j.get("d6", {}).get("max_abs_corr") is not None
                 and d6j["d6"]["max_abs_corr"] < D6_REJECT),
            f"max|corr|={d6j.get('d6', {}).get('max_abs_corr')} "
            f"vs {D6_REJECT} (from d6.json receipt)")
    else:
        chk("d6_admission", False,
            "d6.json receipt absent -- run `probe --d6` (heavy engine leg, "
            "separate step per r324 timeout law)")
    # 510300 regime face presence (sec.3 G-SEG source)
    reg = _regime_face(idx)
    n_reg = int(reg.notna().sum()) if reg is not None else 0
    chk("regime_510300_face", reg is not None and n_reg > 0,
        f"labelled bars={n_reg} (2012-05 onward honest)")
    # seeds disclosure (registry single source)
    facts["seed_disclosure"] = {
        "nulls": int(SEED_NULLS), "sensitivity": int(SEED_SENS),
        "registry_echo": {"fund_value_p1_nulls": SEED_REGISTRY[
            "fund_value_p1_nulls"],
            "fund_value_p1_sens": SEED_REGISTRY["fund_value_p1_sens"]},
        "note": "prereg sec.3 binds nulls to rng([20500000,k]) and sens "
                "to rng([20500500,k]) verbatim; band 20500000/20500500 "
                "disjoint-verified r599 (stock_face_furnace band avoided)."}
    facts["runtime_sec"] = round(time.time() - t0, 1)
    facts["verdict"] = ("PASS" if all(c["pass"] for c in facts["checks"])
                        else "FAIL")
    _dump(facts, PROBE_JSON)
    print(f"probe {facts['verdict']} ({facts['runtime_sec']}s) -> {PROBE_JSON}")
    for c in facts["checks"]:
        print(f"  [{'PASS' if c['pass'] else 'FAIL'}] {c['name']}: "
              f"{c['detail'][:120]}")
    return 0 if facts["verdict"] == "PASS" else 3


def _probe_d6_leg(t0) -> int:
    """The heavy D6 leg as its own step (r324 law): headline full-panel
    continuous run (per-symbol engine burns) then max|corr| vs the six
    registered members; receipt -> results/fund_value_p1/d6.json."""
    if not (os.path.exists(ELIG_NPY) and os.path.exists(SIGVAL_NPY)):
        print("FAIL-CLOSED: run `probe` first (frozen npy face absent)")
        return 3
    idx, syms, F, board, meta = load_axis()
    sig_pos = _signal_positions(idx)
    elig = np.load(ELIG_NPY, mmap_mode="r")
    arr = np.load(SIGVAL_NPY, mmap_mode="r")
    pe, pb = arr[:, :, 0], arr[:, :, 1]
    es = np.asarray(elig[sig_pos, :])
    entry_h, weights_h = build_signal(HEADLINE_RULE, es, pe, pb)
    active = sorted({j for i in range(entry_h.shape[0])
                     for j in np.where(entry_h[i])[0]})
    print(f"d6 leg: headline full-panel run, active members={len(active)}",
          flush=True)
    run = run_cell_portfolio(F, idx, entry_h, sig_pos, weights_h, "base",
                            active, None, None)
    nav = (run["pnl"] + CAPITAL).reindex(idx).ffill().fillna(CAPITAL)
    headline_rets = nav.pct_change().dropna()
    facts = {"headline": {"sharpe_full": round(float(
        (headline_rets.mean() / headline_rets.std(ddof=1)) * np.sqrt(252)), 6),
        "ret_full": round(float(nav.iloc[-1] / nav.iloc[0] - 1), 6),
        "n_trades": run["n_trades"], "n_entries": run["n_entries"],
        "n_active_members": len(active)}}
    try:
        mrets, _ = load_member_rets()
        pairs = []
        worst = None
        for tid in REG6:
            r = mrets[tid]
            both = pd.concat([headline_rets, r], axis=1).dropna()
            c = float(both.corr().iloc[0, 1]) if len(both) > 30 else None
            pairs.append({"member": tid,
                          "corr": round(c, 4) if c is not None else None,
                          "n_overlap": int(len(both))})
            if c is not None and (worst is None or abs(c) > abs(worst[1])):
                worst = (tid, c)
        facts["d6"] = {"reject_line": D6_REJECT, "pairs": pairs,
                       "max_abs_corr": round(abs(worst[1]), 4) if worst
                       else None,
                       "max_member": worst[0] if worst else None}
        ok = worst is not None and abs(worst[1]) < D6_REJECT
    except Exception as ex:
        facts["d6"] = {"error": str(ex)}
        ok = False
    facts["verdict"] = "PASS" if ok else "FAIL"
    facts["runtime_sec"] = round(time.time() - t0, 1)
    _dump(facts, os.path.join(OUT_DIR, "d6.json"))
    print(f"d6 leg verdict={facts['verdict']} "
          f"(max|corr|={facts['d6'].get('max_abs_corr')}) -> d6.json",
          flush=True)
    return 0 if ok else 3


def _require_probe():
    if not os.path.exists(PROBE_JSON):
        print("FAIL-CLOSED: probe.json absent -- run `probe` first "
              "(prereg sec.2 gates)")
        return False
    v = json.load(open(PROBE_JSON, encoding="utf-8")).get("verdict")
    if v != "PASS":
        print(f"FAIL-CLOSED: probe verdict={v} -- ignition refused")
        return False
    if not (os.path.exists(ELIG_NPY) and os.path.exists(SIGVAL_NPY)):
        print("FAIL-CLOSED: frozen mask/sigvals npy absent (probe persists)")
        return False
    return True


# ------------------------------------------------------------------------ run

def _mk(kind, **kw):
    d = {"_fn": {"cell": _cell_task, "cont": _cont_task,
                 "null": _null_task, "sens": _sens_task}[kind], **kw}
    return d


def _pool_claim(entry_id: str, shard_key: str, detail: str) -> None:
    """O-20260930-2355 pool harvest handshake: worker-side closed-claim
    receipt (launcher harvest flips the shard done; worker NEVER writes
    runnable_pool.json -- pool single-writer law)."""
    d = os.path.join(ROOT, "results", "pool_claims",
                     entry_id.replace("/", "_"))
    os.makedirs(d, exist_ok=True)
    fp = os.path.join(d, f"{shard_key}.{_machine_id()}.json")
    now = _now_iso()
    _dump({"machine_id": _machine_id(), "state": "closed",
           "pid": os.getpid(), "heartbeat": now, "outcome": "ok",
           "exit_code": 0, "started": _CLAIM_STARTED, "closed_at": now,
           "result_ref": detail}, fp)
    _log(entry_id.lower(), f"pool claim closed: {os.path.basename(fp)}")


def _entry_of(args) -> tuple:
    if getattr(args, "nulls", None):
        return ("FUND-VALUE-P1-NULLS", "fund-value-p1-nulls-0of1")
    if getattr(args, "sensitivity", None):
        return ("FUND-VALUE-P1-SENS", "fund-value-p1-sens-0of1")
    entry = ("FUND-VALUE-P1-CELL-" + args.cell.replace("-", "").upper()
             + "-" + args.face.upper())
    return (entry, entry.lower() + "-0of1")


def cmd_run(args) -> int:
    global _CLAIM_STARTED
    _CLAIM_STARTED = _now_iso()
    os.makedirs(OUT_DIR, exist_ok=True)
    if not _require_probe():
        return 3
    if args.nulls:
        path = _shard_files(kind="nulls")
        tasks = [_mk("null", k=k) for k in range(K_NULLS)]
        _run_parallel_tasks(tasks, lambda p: f"null|{p['k']}", path, "nulls")
        _pool_claim(*_entry_of(args), f"nulls N={K_NULLS} -> {path}")
        return 0
    if args.sensitivity:
        path = _shard_files(kind="sens")
        tasks = [_mk("sens", k=k) for k in range(K_SENS)]
        _run_parallel_tasks(tasks, lambda p: f"sens|{p['k']}", path, "sens")
        _pool_claim(*_entry_of(args), f"sens N={K_SENS} -> {path}")
        return 0
    if not (args.cell in CELLS and args.face in FACES):
        print(f"bad unit: cell={args.cell} face={args.face}")
        return 2
    cell, face = args.cell, args.face
    import p1c_stock_ic_batch as P1C
    idx, _, _ = P1C.load_universe()
    close = np.load(os.path.join(CACHE_DIR, "close.npy"), mmap_mode="r")
    starts = enumerate_starts(idx, close)
    if len(starts) != G_CENSUS_N:
        print(f"FAIL-CLOSED: start census {len(starts)} != {G_CENSUS_N}")
        return 3
    tasks = [_mk("cell", cell=cell, pos=p, face=face) for p in starts]
    path = _shard_files(cell=cell, face=face)
    _run_parallel_tasks(tasks,
                        lambda p: f"{cell}|{face}|{p['pos']}",
                        path, f"{cell}_{face}")
    cpath = os.path.join(OUT_DIR, f"cont_{cell}_{face}.json")
    if not os.path.exists(cpath):
        _init_worker()
        row = _cont_task(_mk("cont", cell=cell, face=face))
        _dump(row, cpath)
        _log(f"{cell}_{face}", f"cont face written: {cpath}")
    _log(f"{cell}_{face}",
         f"shard complete: {len(starts)} starts + cont face")
    _pool_claim(*_entry_of(args),
                f"cells {len(starts)} -> {path} + {os.path.basename(cpath)}")
    return 0


def _run_parallel_tasks(tasks, keyfn, path, log_name):
    """t22-pattern parallel burn: ProcessPool, checkpoint done-key skip,
    JSONL append. workers=32 BelowNormal (O-2158 width law, frozen)."""
    from concurrent.futures import ProcessPoolExecutor, as_completed
    done = _done_keys(path)
    todo = [p for p in tasks if keyfn(p) not in done]
    _log(log_name, f"todo={len(todo)} resume-skipped={len(tasks)-len(todo)}")
    if not todo:
        return 0
    workers = 32                      # frozen-prereg workers_plan
    t0, t_last, n = time.time(), time.time(), 0
    with ProcessPoolExecutor(max_workers=workers,
                             initializer=_init_worker) as pool:
        futs = {pool.submit(p["_fn"], p): p for p in todo}
        for fut in as_completed(futs):
            row = fut.result()
            _append_rows(path, [row])
            n += 1
            if time.time() - t_last > 30:
                _log(log_name, f"progress {n}/{len(todo)}")
                t_last = time.time()
    _log(log_name, f"DONE {n}/{len(todo)} in {round(time.time()-t0,1)}s "
                   f"workers={workers}")
    return n


# --------------------------------------------------------------------- status

def cmd_status(_) -> int:
    if not os.path.isdir(OUT_DIR):
        print("no results/fund_value_p1 yet")
        return 0
    total_missing = 0
    for cell in CELLS:
        for face in FACES:
            p = _shard_files(cell=cell, face=face)
            have = len(_done_keys(p)) if os.path.exists(p) else 0
            c = os.path.join(OUT_DIR, f"cont_{cell}_{face}.json")
            cont = "Y" if os.path.exists(c) else "-"
            miss = G_CENSUS_N - have
            total_missing += max(0, miss) + (0 if cont == "Y" else 1)
            print(f"{cell:9s} {face:4s}: {have}/{G_CENSUS_N} starts cont={cont}")
    for kind, want in (("nulls", K_NULLS), ("sens", K_SENS)):
        p = _shard_files(kind=kind)
        have = len(_done_keys(p)) if os.path.exists(p) else 0
        total_missing += max(0, want - have)
        print(f"{kind}: {have}/{want}")
    print(f"finalize_ready: {total_missing == 0} (missing={total_missing})")
    return 0


# ----------------------------------------------------- law-A exit census

def _census_core(F, idx, entry_sig, sig_pos, weights, face, active):
    """Law-A census engine loop: per-symbol runs through the SAME frozen
    machinery (NEUTRALIZED_PARAMS + ExitPatch + run_backtest), capturing
    per-trade exit reasons. Single source shared by finalize and
    selftest fixture legs (r303 single-source law)."""
    from engine import run_backtest
    from contextlib import nullcontext
    per_reason, per_sym = {}, {}
    n_trades = 0
    for j in active:
        w = prices_window(F, idx, j, 0, T_EXPECT - 1)
        ent, sc = _sym_entry_scale(entry_sig, sig_pos, weights, j,
                                   0, len(sig_pos) - 1, w.index, 0)
        with ExitPatch(EXIT_PATCH_OVERRIDES), \
             (CostPatch(2.0) if face == "x2" else nullcontext()):
            res = run_backtest({str(j): w}, dict(NEUTRALIZED_PARAMS),
                               entry_signal=ent,
                               exit_signal=ent <= 0,
                               entry_size_scale=sc)
        reasons = {}
        for tr in res["trades"]:
            r = tr["reason"]
            per_reason[r] = per_reason.get(r, 0) + 1
            reasons[r] = reasons.get(r, 0) + 1
            n_trades += 1
        per_sym[int(j)] = reasons
    return {"per_reason": per_reason, "per_sym": per_sym,
            "n_trades": n_trades}


def _exit_reason_census(cell, face):
    """Law-A census (LOWAMP-P2 sec.9 / O-20261002-2115): headline
    re-run; only signal_reversal is lawful on the hold-through face."""
    _init_worker()
    es = _elig_sig_rows(_G["elig"], _G["sig_pos"])
    entry_sig, weights = build_signal(CELLS[cell], es, _G["pe"], _G["pb"])
    active = sorted({j for i in range(entry_sig.shape[0])
                     for j in np.where(entry_sig[i])[0]})
    core = _census_core(_G["F"], _G["idx"], entry_sig, _G["sig_pos"],
                        weights, face, active)
    lawful = sum(core["per_reason"].get(r, 0) for r in LAWFUL_EXIT_REASONS)
    total = core["n_trades"]
    default = total - lawful
    share = (default / total) if total else 0.0
    return {"per_reason": core["per_reason"], "n_trades": total,
            "lawful": lawful, "default_stack": default,
            "default_share": round(share, 6),
            "block_share": CENSUS_BLOCK_SHARE,
            "pass": bool(share <= CENSUS_BLOCK_SHARE),
            "lawful_reasons": list(LAWFUL_EXIT_REASONS)}


# ------------------------------------------------ null aux (bootstrap etc.)

def _block_bootstrap_sharpe(rets: pd.Series, b: int = BOOT_B,
                            seed: int | None = None):
    """Stationary block bootstrap on the headline daily returns,
    block length 21 td (sec.3 face 2)."""
    x = rets.to_numpy(dtype=float)
    n = len(x)
    if n < BOOT_BLOCK * 2:
        return {"n_blocks": 0, "sharpe_p05": None, "note": "short series"}
    rng = np.random.default_rng(seed if seed is not None else 20261003)
    nblocks = int(np.ceil(n / BOOT_BLOCK))
    stats = []
    for _ in range(b):
        starts = rng.integers(0, n - BOOT_BLOCK + 1, size=nblocks)
        sample = np.concatenate([x[s:s + BOOT_BLOCK] for s in starts])[:n]
        mu, sd = sample.mean(), sample.std(ddof=1)
        if sd > 0:
            stats.append(mu / sd * np.sqrt(252))
    return {"b": b, "block_td": BOOT_BLOCK,
            "sharpe_p05": round(float(np.percentile(stats, 5)), 4) if stats else None,
            "sharpe_p50": round(float(np.percentile(stats, 50)), 4) if stats else None,
            "sharpe_p95": round(float(np.percentile(stats, 95)), 4) if stats else None}


def _sign_flip_perm(rets: pd.Series, p: int = BOOT_B,
                    seed: int = 20261003) -> dict:
    """Sign-flip permutation on the headline daily returns (sec.3
    face 3): P(mean > 0 under random signs)."""
    x = rets.to_numpy(dtype=float)
    rng = np.random.default_rng(seed)
    signs = rng.choice(np.array([-1.0, 1.0]), size=(p, len(x)))
    perms = (signs * x).mean(axis=1)
    obs = x.mean()
    pval = float((perms >= obs).mean())
    return {"p": p, "p_value_mean_positive": round(pval, 4)}


# -------------------------------------------------------------------- finalize

def cmd_finalize(_) -> int:
    # completeness gate (fail-closed; finalize is round-owned)
    missing = []
    for cell in CELLS:
        for face in FACES:
            p = _shard_files(cell=cell, face=face)
            c = os.path.join(OUT_DIR, f"cont_{cell}_{face}.json")
            if not os.path.exists(p) or not os.path.exists(c):
                missing.append(f"{cell}/{face}")
    for kind, want in (("nulls", K_NULLS), ("sens", K_SENS)):
        p = _shard_files(kind=kind)
        have = len(_done_keys(p)) if os.path.exists(p) else 0
        if have < want:
            missing.append(f"{kind}:{have}/{want}")
    if missing:
        print("finalize REFUSED -- incomplete: " + ", ".join(missing[:8]))
        return 3
    if os.path.exists(OUT_JSON):
        try:
            j = json.load(open(OUT_JSON, encoding="utf-8"))
            if j.get("trials_ledger"):
                print(f"idempotent: {OUT_JSON} already finalized")
                return 0
        except Exception:
            pass
    t0 = time.time()
    probe = json.load(open(PROBE_JSON, encoding="utf-8"))
    cont = {}
    for cell in CELLS:
        for face in FACES:
            c = os.path.join(OUT_DIR, f"cont_{cell}_{face}.json")
            cont[(cell, face)] = json.load(open(c, encoding="utf-8"))
    nulls = [json.loads(ln) for ln in
             open(_shard_files(kind="nulls"), encoding="utf-8") if ln.strip()]
    sens = [json.loads(ln) for ln in
            open(_shard_files(kind="sens"), encoding="utf-8") if ln.strip()]
    null_vals = [r["sharpe"] for r in nulls]
    null_pool = {
        "coverage": {"mu": float(np.mean(null_vals)),
                     "sigma": float(np.std(null_vals, ddof=1)),
                     "n_values": len(null_vals)},
        "source": f"{BATCH_NAME} same-mask nulls K={K_NULLS} "
                  f"rng([{SEED_NULLS},k])",
    }
    # passive face (sec.4 single-source): full-panel EW B&H of the mask
    # members alive on the FIRST signal row, derived here (never copied)
    _init_worker()
    idx, F = _G["idx"], _G["F"]
    sig_pos = _G["sig_pos"]
    first_row = sig_pos[0]
    mrow = np.asarray(_G["elig"][first_row])
    close0 = np.asarray(F["close"][first_row])
    pas_idx = np.where(np.isfinite(close0) & mrow)[0]
    base0 = close0[pas_idx]
    rel = np.full((T_EXPECT - first_row, pas_idx.size), np.nan)
    for k, j in enumerate(pas_idx):
        col = np.asarray(F["close"][first_row:, j])
        rel[:, k] = col / base0[k]
    passive_nav = pd.Series(np.nanmean(rel, axis=1),
                            index=idx[first_row:])
    passive_rets = passive_nav.pct_change().dropna()
    passive_sharpe = float((passive_rets.mean() / passive_rets.std(ddof=1))
                           * np.sqrt(252))
    passive_face = {"n_members_first_sig_row": int(pas_idx.size),
                    "sharpe_full": round(passive_sharpe, 6),
                    "ret_full": round(float(passive_nav.iloc[-1] - 1), 6)}
    # G1' (headline VALUE-PE base continuous; batch-own null pool +
    # batch-own passive override, both derived this batch)
    h = cont[(HEADLINE, "base")]
    h_rets = pd.Series(h["returns"])
    g1 = g1_prime_v2(sharpe_full=h["sharpe_full"], returns=h_rets,
                     batch_cells=BATCH_CELLS, pool="core48",
                     n_trades=h["n_trades"], n_entries=h["n_entries"],
                     null_pool=null_pool,
                     passive_override=passive_sharpe)
    # x2 survival
    x2 = cont[(HEADLINE, "x2")]
    x2_pass = bool(x2["sharpe_full"] > 0)
    # M1 t face (sec.1/§4)
    tstat = t_from_sharpe(h["sharpe_full"], len(h_rets))
    m1 = m1_t_value_gate(tstat, claim_class="new_strategy")
    # DSR on raw returns (never dsr_from_stats)
    dsr = deflated_sharpe_ratio(h_rets, n_trials=BATCH_CELLS)
    # PBO: 4 judged cells, base-face daily returns matrix
    mat = pd.DataFrame({c: pd.Series(cont[(c, "base")]["returns"])
                        for c in CELLS}).dropna()
    from screening.pbo import cscv_pbo, pbo_verdict
    pbo_rec = cscv_pbo(mat)
    pbo = float(pbo_rec["pbo"])
    pbo_band = pbo_verdict(pbo)
    g2 = g2_registration_v2(g1.get("pass"), dsr.get("dsr", dsr), pbo)
    # G-SEG coverage (headline starts, 12m full windows)
    seg_cov = {}
    gseg_pass = True
    rows = _read_cells(HEADLINE, "base") or []
    full = [r for r in rows if not r.get("partial_12m")]
    cnt = {}
    for r in full:
        cnt[r.get("regime", "na")] = cnt.get(r.get("regime", "na"), 0) + 1
    seg_cov = cnt
    for regm in ("bear", "bull", "chop"):
        if cnt.get(regm, 0) < 50:
            gseg_pass = False
    # law-A post-burn exit-reason census (dual gate second piece)
    census = _exit_reason_census(HEADLINE, "base")
    census_pass = bool(census["pass"])
    # verdict (three-state, conjunctive)
    gates_pass = bool(g1.get("pass") and x2_pass and m1.get("pass")
                      and g2.get("pass"))
    if not gseg_pass:
        verdict = "insufficient-sample"
    elif not census_pass:
        verdict = "consumption-blocked"
    elif gates_pass:
        verdict = "PASS"
    else:
        verdict = "judged-negative"
    # headline per-start 12m distribution (sec.8 all-starts law)
    lrows = [r for r in _read_cells(HEADLINE, "base")
             if not r.get("partial_12m")]
    r12 = sorted(r["ret_12m"] for r in lrows)

    def pct(q):
        return round(float(np.percentile(r12, q)), 4) if r12 else None

    hret = pd.Series(h["returns"])
    roll_worst = {}
    for yrs, bars in (("3y", 756), ("5y", 1260), ("10y", 2520)):
        if len(hret) >= bars:
            roll = (1 + hret).rolling(bars).apply(np.prod, raw=True) - 1
            roll_worst[yrs] = round(float(roll.min()), 4)
        else:
            roll_worst[yrs] = None
    # calendar-year returns (crash-year descriptive)
    rdates = pd.to_datetime(h.get("return_dates"))
    if len(rdates) == len(hret):
        cy = (1 + hret).groupby(rdates.year).apply(
            lambda x: float(x.prod() - 1))
    else:
        cy = pd.Series(dtype=float)
    crash_years = {int(y): round(v, 4) for y, v in cy.items() if v <= -0.35}
    # x2 year-by-year stability (cost-stress descriptive)
    x2ret = pd.Series(x2["returns"])
    x2_dates = pd.to_datetime(x2.get("return_dates"))
    x2_yearly = {}
    if len(x2_dates) == len(x2ret):
        x2_yearly = {int(y): round(v, 4) for y, v in
                     ((1 + x2ret).groupby(x2_dates.year).apply(
                         lambda x: float(x.prod() - 1))).items()}
    results = {
        **cutoff_meta("2026-09-22"),
        "batch": BATCH_NAME, "ticket": TICKET,
        "family_key": FAMILY_KEY,
        "verdict": verdict,
        "gates": {
            "g1_prime": g1,
            "x2_survival": {"sharpe_full": x2["sharpe_full"],
                            "pass": x2_pass},
            "m1": m1, "dsr": dsr,
            "pbo": {"pbo": round(pbo, 4), "band": pbo_band},
            "g2": g2,
            "g_seg": {"coverage": seg_cov, "pass": gseg_pass},
            "exit_census": census,
        },
        "headline": {"sharpe_full": h["sharpe_full"],
                     "ret_full": h["ret_full"], "max_dd": h["max_dd"],
                     "n_trades": h["n_trades"],
                     "n_entries": h["n_entries"],
                     "trades_per_year": h["trades_per_year"]},
        "cells": {f"{c}|{f}": {kk: vv for kk, vv in
                  cont[(c, f)].items() if kk != "returns"}
                  for c in CELLS for f in FACES},
        "nulls": {"same_mask": {
            "k": len(null_vals),
            "mu": round(float(np.mean(null_vals)), 4),
            "sigma": round(float(np.std(null_vals, ddof=1)), 4),
            "p05": round(float(np.percentile(null_vals, 5)), 4),
            "p50": round(float(np.percentile(null_vals, 50)), 4),
            "p95": round(float(np.percentile(null_vals, 95)), 4)},
            "block_bootstrap": _block_bootstrap_sharpe(h_rets),
            "sign_flip": _sign_flip_perm(h_rets)},
        "sensitivity": {
            "k": len(sens),
            "sharpe_p05": round(float(np.percentile(
                [r["sharpe"] for r in sens], 5)), 4),
            "sharpe_p50": round(float(np.percentile(
                [r["sharpe"] for r in sens], 50)), 4),
            "sharpe_p95": round(float(np.percentile(
                [r["sharpe"] for r in sens], 95)), 4),
            "maxdd_worst": round(float(min(r["max_dd"] for r in sens)), 4)},
        "starts_12m_dist": {"n": len(r12), "best": pct(100),
                            "worst": pct(0), "p25": pct(25),
                            "median": pct(50), "p75": pct(75),
                            "positive_share": round(
                                sum(1 for v in r12 if v > 0) / len(r12), 4)
                            if r12 else None},
        "rolling_worst": roll_worst,
        "descriptive": {
            "crash_years_lte_-35pct": crash_years,
            "is_ann_ret": round(float((1 + hret.iloc[:len(hret) // 2])
                                       .prod() - 1), 4),
            "oos_ann_ret": round(float((1 + hret.iloc[len(hret) // 2:])
                                       .prod() - 1), 4),
            "oos_from_2025_sharpe": h.get("oos_sharpe"),
            "oos_from_2025_ret": h.get("oos_ret"),
            "x2_cost_drag_sharpe": round(
                x2["sharpe_full"] - h["sharpe_full"], 4),
            "x2_yearly": x2_yearly},
        "d6": probe.get("d6"),
        "probe_ref": "results/fund_value_p1/probe.json",
        "passive_face": passive_face,
        "audit": {
            "machine": _machine_id(),
            "seed_disclosure": probe.get("seed_disclosure"),
            "engine_face": "engine.run_backtest, per-symbol sub-account "
                           "decomposition, entry_size_scale weight mapping",
            "cost_face": {"x1_side_bp": COST_X1 * 1e4,
                          "source": "rev_osc_stock_p1.COST_X1 (imported)",
                          "x2_face": "CostPatch(2.0)"},
            "law_a_census": {"block_share": CENSUS_BLOCK_SHARE,
                             "lawful_reasons": list(LAWFUL_EXIT_REASONS),
                             "ref": "LOWAMP-P2 sec.9 / O-20261002-2115"},
            "mask_face": probe.get("mask"),
            "finalize_runtime_sec": round(time.time() - t0, 1),
        },
    }
    # cells.csv small table (git face)
    with open(OUT_CSV, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("cell,face,sharpe_full,ret_full,max_dd,n_trades,"
                 "n_entries,beat12_rate\n")
        for c in CELLS:
            crows = _read_cells(c, "base") or []
            cfull = [r for r in crows if not r.get("partial_12m")]
            rate = (round(sum(1 for r in cfull if r["beat_12m"])
                          / len(cfull), 4) if cfull else None)
            for f in FACES:
                cc = cont[(c, f)]
                fh.write(f"{c},{f},{cc['sharpe_full']},{cc['ret_full']},"
                         f"{cc['max_dd']},{cc['n_trades']},"
                         f"{cc['n_entries']},{rate if f == 'base' else ''}\n")
    # trials ledger (dict schema, embed-order law: append BEFORE results
    # json dump carries the ledger block)
    led = append_ledger(batch_name=BATCH_NAME, batch_trials=BATCH_CELLS,
                        file_name="results/fund_value_p1/"
                                   "fund_value_p1_results.json",
                        evidence_cutoff="2026-09-22")
    results["trials_ledger"] = led
    # gate attrition row (sec.8)
    _attrition_row(g1, m1, g2, census, gseg_pass)
    _dump(results, OUT_JSON)
    print(f"finalize verdict={verdict} -> {OUT_JSON}")
    print(f"  g1={g1.get('pass')} x2={x2_pass} m1={m1.get('pass')} "
          f"g2={g2.get('pass')} g_seg={gseg_pass} census={census_pass} "
          f"(default_share={census['default_share']})")
    return 0


def _read_cells(cell, face):
    p = _shard_files(cell=cell, face=face)
    if not os.path.exists(p):
        return []
    return [json.loads(ln) for ln in open(p, encoding="utf-8")
            if ln.strip()]


def _attrition_row(g1, m1, g2, census, gseg_pass):
    """sec.8 attrition account: one honest append row."""
    path = os.path.join(ROOT, "results", "gate_attrition.json")
    try:
        data = json.load(open(path, encoding="utf-8"))
        rows = data.get("rows", data if isinstance(data, list) else [])
    except Exception:
        rows = []
    rows.append({"batch": BATCH_NAME, "ts": _now_iso(),
                 "g1_pass": bool(g1.get("pass")),
                 "m1_pass": bool(m1.get("pass")),
                 "g2_pass": bool(g2.get("pass")),
                 "exit_census_pass": bool(census.get("pass")),
                 "g_seg_pass": bool(gseg_pass)})
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"rows": rows[-500:]}, fh, ensure_ascii=False, indent=1)


# ------------------------------------------------------------------- selftest

def cmd_selftest(_) -> int:
    """Hermetic offline self-check: synthetic panel, no repo data face,
    no network. Deterministic double-run, F11 dual-channel
    mutual-exclusion, G-MASK construction identity, monthly signal
    semantics, engine T+1 causality."""
    import shutil
    import tempfile
    ok = True

    def check(name, cond, detail=""):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name} {detail}")
        ok = ok and bool(cond)

    # F11: dual-channel key-set mutual exclusion (dead-letter guard)
    check("F11_dual_channel_key_mutex",
          len(EXIT_PARAMS_KEYS & set(EXIT_PATCH_OVERRIDES)) == 0
          and set(EXIT_PATCH_OVERRIDES) == {"loss_time_days",
                                            "global_hard_limit"}
          and EXIT_PARAMS_KEYS == {"take_profit_levels",
                                   "trailing_stop_activate",
                                   "initial_stop", "time_decay_period"},
          "params 4 keys vs ExitPatch 2 keys disjoint")
    # F11b: neutralized values really neutralize the default stack
    np_ = NEUTRALIZED_PARAMS
    check("F11b_neutral_values",
          np_["take_profit_levels"] == ()
          and np_["trailing_stop_activate"] == F1_BM
          and np_["initial_stop"] == -1.0
          and np_["time_decay_period"] == 10 ** 9
          and EXIT_PATCH_OVERRIDES["loss_time_days"] == 10 ** 9
          and EXIT_PATCH_OVERRIDES["global_hard_limit"] == 10 ** 9)
    # cost single-source identity (CN-C7)
    check("cost_x1_identity", abs(COST_X1 - 0.0013041) < 1e-12,
          f"{COST_X1}")
    # seeds registry identity
    check("seeds_registry",
          SEED_REGISTRY["fund_value_p1_nulls"] == 20_500_000
          and SEED_REGISTRY["fund_value_p1_sens"] == 20_500_500)
    # build_signal: synthetic monthly face
    n_sig, n_sym = 6, 12
    es = np.ones((n_sig, n_sym), dtype=bool)
    pe = np.tile(np.arange(1, n_sym + 1, dtype=np.float32), (n_sig, 1)) * 3.0
    pb = np.tile(np.arange(1, n_sym + 1, dtype=np.float32), (n_sig, 1)) * 0.4
    ent, w = build_signal("pe_ttm", es, pe, pb, top_n=5)
    check("signal_topn", int(ent.sum()) == n_sig * 5
          and all(int(ent[i].sum()) == 5 for i in range(n_sig)))
    check("signal_asc_rank",
          bool((np.argsort(pe[0])[:5] == np.where(ent[0])[0]).all()),
          "lowest pe picked first")
    # valuation band excludes out-of-band members
    pe2 = pe.copy(); pe2[:, 3] = 500.0      # out of (0,200]
    ent2, _ = build_signal("pe_ttm", es, pe2, pb, top_n=5)
    check("band_excludes", not ent2[:, 3].any(),
          "pe=500 excluded from selection")
    pb2 = pb.copy(); pb2[:, 5] = 0.0       # out of (0,20]
    ent3, _ = build_signal("pe_ttm", es, pe2, pb2, top_n=5)
    check("band_excludes_pb", not ent3[:, 5].any())
    # eq weight identity (f32 face: 1e-6 tolerance)
    wv = w[ent]
    check("eq_weight", bool(np.isfinite(wv).all())
          and abs(float(wv.max()) - 0.2) < 1e-6
          and abs(float(wv.min()) - 0.2) < 1e-6,
          f"{float(wv.min()):.6f}..{float(wv.max()):.6f}")
    # G-MASK construction identity: null universe == headline universe
    univ = _headline_universe(es, pe2, pb)
    band = ((pe2 > PE_MIN) & (pe2 <= PE_MAX) & np.isfinite(pe2)
            & (pb > PB_MIN) & (pb <= PB_MAX) & np.isfinite(pb))
    check("G_MASK_identity", bool((univ == (es & band)).all()))
    # null draw determinism (substream law)
    r1 = np.random.default_rng([SEED_NULLS, 7])
    r2 = np.random.default_rng([SEED_NULLS, 7])
    cols = np.arange(100)
    check("null_rng_substream",
          bool((r1.choice(cols, 20, replace=False)
                == r2.choice(cols, 20, replace=False)).all()))
    # month_first_positions on a synthetic calendar
    idx = pd.to_datetime(["2024-01-02", "2024-01-15", "2024-02-01",
                          "2024-02-20", "2024-03-04", "2024-04-01"])
    mfp = month_first_positions_full(idx)
    check("month_first_rows", mfp == [0, 2, 4, 5],
          f"{mfp}")
    # _sig_span window logic: sigs [10,70,130,200] over window [71,199]
    # -> first in-window sig = 130 (row 2), last = 130 (row 2)
    sp = [10, 70, 130, 200]
    lo_s, hi_s = _sig_span(sp, 71, 199)
    check("sig_span", lo_s == 2 and hi_s == 2, f"{lo_s},{hi_s}")
    # engine T+1 causality on a tiny synthetic window (real engine)
    try:
        from engine import run_backtest
        tidx = pd.date_range("2024-01-01", periods=8, freq="B")
        wdf = pd.DataFrame({"open": np.linspace(10, 11, 8),
                            "high": np.linspace(10.2, 11.2, 8),
                            "low": np.linspace(9.8, 10.8, 8),
                            "close": np.linspace(10, 11, 8),
                            "volume": np.full(8, 1e6),
                            "amount": np.full(8, 1e7)}, index=tidx)
        ent_df = pd.DataFrame(False, index=tidx, columns=["s"])
        ent_df.iloc[2, 0] = True
        with ExitPatch(EXIT_PATCH_OVERRIDES):
            res = run_backtest({"s": wdf}, dict(NEUTRALIZED_PARAMS),
                               entry_signal=ent_df,
                               exit_signal=ent_df <= 0,
                               entry_size_scale=None)
        td = [pd.Timestamp(t["date"]) for t in res["trades"]]
        after = all(d > tidx[2] for d in td) if td else True
        check("engine_t_plus_one",
              bool(after and len(res["equity_curve"]) == 8),
              f"trades@{[str(d.date()) for d in td]}")
    except Exception as ex:
        check("engine_t_plus_one", False, f"error: {ex}")
    # determinism: double run of build_signal identity (NaN-safe compare)
    e1, w1 = build_signal("pb", es, pe, pb, top_n=3)
    e2, w2 = build_signal("pb", es, pe, pb, top_n=3)
    check("determinism_build", bool((e1 == e2).all()
                                    and np.array_equal(w1, w2,
                                                       equal_nan=True)))
    print(f"SELFTEST {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


def month_first_positions_full(idx: pd.DatetimeIndex) -> list:
    """Unbounded month-first rows (selftest face; the bounded census
    face lives in month_first_positions)."""
    keys = idx.strftime("%Y-%m")
    out, prev = [], None
    for p, k in enumerate(keys):
        if k != prev:
            out.append(int(p))
            prev = k
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="FUND-VALUE-P1 batch runner "
                                            "(prereg research/FUND-VALUE-P1.md)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("probe")
    p.add_argument("--d6", action="store_true",
                   help="run the heavy D6 engine leg only "
                        "(separate step, r324 timeout law)")
    sub.add_parser("status")
    sub.add_parser("finalize")
    sub.add_parser("selftest")
    r = sub.add_parser("run")
    r.add_argument("--cell", default=None)
    r.add_argument("--face", default=None)
    r.add_argument("--nulls", action="store_true")
    r.add_argument("--sensitivity", action="store_true")
    args = ap.parse_args(argv)
    if args.cmd == "probe":
        return cmd_probe(args)
    if args.cmd == "run":
        return cmd_run(args)
    if args.cmd == "status":
        return cmd_status(args)
    if args.cmd == "finalize":
        return cmd_finalize(args)
    if args.cmd == "selftest":
        return cmd_selftest(args)
    return 2


if __name__ == "__main__":
    sys.exit(main())
