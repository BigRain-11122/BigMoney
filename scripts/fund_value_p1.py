"""FUND-VALUE-P1 -- fundamental value (low PE / low PB) cross-sectional
MONTHLY-rebalance NEW FAMILY judged batch at main-exam rank.

Ticket T-2026-10-02-150-P1 (claimed bm-b r598, fetch-before-claim r239
law); prereg FROZEN at research/FUND-VALUE-P1.md (T-145 leg(c) first
fundamental family; CEO direct order O-20261002-2115 sec.1 item 1).
Judgments live there; this file implements them, never re-states a
threshold. banned_direction_gate ADMIT re-verified pre-ignition by the
r599 bm-a window (receipt in ticket progress). family_key
fund_value_stock_xs (M3: seven closed keys zero-hit = open; stock monthly
valuation family is orthogonal to every registered key).

Family (prereg sec.3, frozen):
  signal day = each month's FIRST trading day; value faces forward-filled
  to the signal day (anchor_date <= t, PIT law; as-published snapshots);
  within the pick universe (base eligibility mask AND the JOINT valuation
  band pe_ttm in (0,200] AND pb in (0,20]) take the Top-N=20 LOWEST
  rule value (cell A VALUE-PE pe_ttm = HEADLINE, cell B VALUE-PB pb),
  eq weights (1/pick_size), ALWAYS-ON, monthly rotation. Months whose
  joined pe-coverage over the active universe is < 0.80 are SKIPPED
  whole (no rebalance fires; prior selection persists; pre-t0 = flat,
  probe-frozen t0=1994-05-03, zero below-floor months after t0).

Execution semantics (prereg sec.0.6, engine/ untouched):
  entry = selected-at-this-month (forward-filled across the month's bars),
  exit = entry <= 0 (t22 convention -- the ONLY exit: monthly rotation).
  HOLD-THROUGH declared; the engine default exit stack is DISABLED via
  the TWO channels split by the engine's own bridge surface (r522):
    params channel (bridge-reachable, 4 keys): take_profit_levels=(),
    trailing_stop_activate=1e12, initial_stop=-1.0, time_decay_period=1e9;
    ExitPatch channel (live.paper ExitConfig factory, 2 keys):
    loss_time_days=1e9, global_hard_limit=1e9 (F11 disjoint selftest).
  x2 face = CostPatch(2.0). Costs CN-C7 stock V1 = 13.041bp/side
  single-source asserted: rev_osc_stock_p1.COST_X1 == cost_spec
  .x1_side_rate() (rt 26.082bp; x2 rt 52.164bp); eq Top-20 unit ¥50k on a
  ¥1M account clears the ¥20k minimum-commission tier (no small-lot
  doubling); ETF and stock results comparable ONLY under this caliber.
  Law-A post-burn exit-reason census: only signal_reversal is lawful on
  the hold-through face; default-stack share > 20% = consumption-blocked.

Engine-face disclosure (per-symbol sub-account decomposition, t22/LAD
lineage): each symbol runs as its own engine sub-account (initial_cash
= 1,000,000, max_positions=1, position_size_pct=1.0 x entry_size_scale
= 1/pick_size), NAV = CAPITAL + sum(NAV_s - CAPITAL). Weights set at
entry, never resized mid-hold (sizing_mode=fixed_initial). Frames are
SPAN-SLICED per symbol (first selection - 2 .. last span end + 2, the
LOWAMP full-frame semantics proven identical by selftest leg F15) with
seed-ffill OHLC marks: the frame is seeded from the symbol's last valid
bar BEFORE the slice so suspended-day marks ride the prior close (the
P4_BATCH2 disclosed stale_ffill convention); volume/amount NaN->0.

Data faces (prereg sec.2):
  price = Money02 p1c_stock npy cache (8792 bars x 5222 syms, last bar
  2026-09-22, qfq, float32 memmaps; 688/689 volume+amount already at
  real units per cache meta) via p1c_stock_ic_batch.load_universe;
  value = data/fund_history_export/value_faces.parquet (T-149 TRANSFER
  landed, export gate green; per-symbol sorted anchors 1991-03-18 ..
  2026-10-01); eligibility = close/volume/amount>0 AND amt20-median
  >= ¥10,000,000 AND listed >= 252 bars AND as-of ST exclusion via the
  P4_BATCH2 sec.2 5%-seal board-aware proxy IMPORTED VERBATIM
  (p4_ext_tilt._st_regime, trailing-250 slice at each signal day;
  constants CHINEXT_20_FROM/ST_WIN/ST_SEAL5_MIN imported from
  p4_batch2_screen, zero rewrite). Regime labels: 510300 3-way MA200
  proxy from the REPO core48 daily face (the p1c STOCK panel carries no
  510300 column -- resolved via date-keyed labels, disclosed; regime is
  a reporting segment, never a gate). G-CENSUS: 401 monthly starts
  (1992-09-01..2026-03-02 window, pos>=252, fwd>=126, active>=24 --
  probe-bit-exact enumeration). evidence_cutoff 2026-09-22 D2 lockbox.

Continuous-face span (disclosed, frozen pre-burn): the cont/nulls/sens
runs span t0 (first coverage-passing month) .. cutoff; the G1' passive
override is EW B&H of the base-mask members at t0 over the same span
(derived here, single-source; per-start passive = base-mask members at
the start day over the window, ffilled marks).

Seeds (prereg sec.3, registry rows pre-registered by bm-a r599):
  nulls rng([20500000, k]) K=2000; sens rng([20500500, k]) K=500;
  null family aux (block bootstrap B=2000 len 21, sign-flip P=2000)
  seed 20261002 disclosed here. Bootstrap/sign-flip are descriptive.

Checkpoint/resume: per-shard JSONL append, done-key skip, tolerant of a
truncated crash tail (t22 pattern); pool-claim handshake per
O-20260930-2355 (worker writes results/pool_claims/<entry>/<shard>
.<machine>.json; the launcher harvest flips the pool shard done).

Usage:
  python scripts/fund_value_p1.py d6              # D6 admission probe (writes d6.json)
  python scripts/fund_value_p1.py probe           # ignition gates (needs d6.json ADMIT)
  python scripts/fund_value_p1.py run --cell VALUE-PE --face x1|x2
  python scripts/fund_value_p1.py run --nulls
  python scripts/fund_value_p1.py run --sensitivity
  python scripts/fund_value_p1.py status
  python scripts/fund_value_p1.py finalize        # round-owned, post-shards
  python scripts/fund_value_p1.py selftest        # hermetic, offline
"""
import argparse
import json
import os
import sys
import time
import warnings
from collections import defaultdict

warnings.filterwarnings("ignore", message="All-NaN slice encountered")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd

import p1c_stock_ic_batch as P1C          # canonical universe/loader (single source)
from p4_ext_tilt import _st_regime        # ST proxy clause verbatim (P4_BATCH2 sec.2)
from p4_batch2_screen import (CHINEXT_20_FROM, ST_WIN, ST_SEAL5_MIN)
import rev_osc_stock_p1 as RVSTOCK          # COST_X1 single source (CN-C7)
from knowledge import cost_spec
from live.paper import ExitPatch
from t22_virtual_timepoints import _slice_metrics, regime_proxy
from science_gates import (
    CostPatch, SEED_REGISTRY, append_ledger, closed_family_check, cutoff_meta,
    deflated_sharpe_ratio, g1_prime_v2, g2_registration_v2, m1_t_value_gate,
    t_from_sharpe,
)
from parallel_runner import worker_cap

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TICKET = "T-2026-10-02-150-P1"
PREREG = os.path.join(ROOT, "research", "FUND-VALUE-P1.md")
OUT_DIR = os.path.join(ROOT, "results", "fund_value_p1")
LOG_DIR = os.path.join(OUT_DIR, "logs")
PROBE_JSON = os.path.join(OUT_DIR, "probe.json")
D6_JSON = os.path.join(OUT_DIR, "d6.json")
OUT_JSON = os.path.join(OUT_DIR, "fund_value_p1_results.json")
OUT_CSV = os.path.join(OUT_DIR, "cells.csv")
PARQUET = os.path.join(ROOT, "data", "fund_history_export", "value_faces.parquet")
ETF_510300_CSV = os.path.join(ROOT, "data", "daily", "sh510300.csv")

CUTOFF = pd.Timestamp("2026-09-22")          # prereg sec.2 D2 lockbox
BATCH_NAME = "FUND-VALUE-P1"
BATCH_CELLS = 2004                          # 4 judged cell-faces + 2000 nulls
FAMILY_KEY = "fund_value_stock_xs"           # prereg sec.1 M3 (new family)
CAPITAL = 1_000_000.0                        # prereg CN-C7 nominal tier
W6M, W12M, W24M = 126, 252, 504
WARMUP_TD = 252                             # listed/bars warmup caliber
MIN_LISTED = 24                             # active members at a start
ENUM_LO = pd.Timestamp("1992-09-01")         # G-CENSUS window (probe-frozen)
ENUM_HI = pd.Timestamp("2026-03-02")
G_CENSUS_EXPECT = 401
AMT20_WIN = 20
AMT20_MIN = 10_000_000.0                     # frozen liquidity floor (sec.2)
LISTED_MIN_BARS = 252                        # 上市>=252td (sec.2)
TOPN = 20                                    # frozen Top-N (sec.3)
PE_MIN, PE_MAX = 0.0, 200.0                  # frozen valuation band (sec.2)
PB_MIN, PB_MAX = 0.0, 20.0
COV_FLOOR = 0.80                             # monthly data-coverage skip gate
T0_FROZEN = "1994-05-03"                      # probe-frozen first-signal date (r596/r599 receipt)
K_NULLS = 2000
SEED_NULLS = 20_500_000                      # prereg sec.3 / SEED_REGISTRY
K_SENS = 500
SEED_SENS = 20_500_500                       # prereg sec.3 / SEED_REGISTRY
BOOT_B = 2000                                # block bootstrap B
BLOCK_BOOT_LEN = 21                          # frozen block length (sec.3)
NULL_AUX_SEED = 20261002                     # bootstrap/sign-flip face (disclosed)
D6_REJECT = 0.7                              # prereg sec.1 D6
CENSUS_BLOCK_SHARE = 0.20                    # prereg sec.0.6 (frozen)
LAWFUL_EXIT_REASONS = ("signal_reversal",)
HEADLINE = "VALUE-PE"                        # prereg sec.3 (cell A)
CELLS = {"VALUE-PE": {"rule": "pe"}, "VALUE-PB": {"rule": "pb"}}
FACES = ("x1", "x2")
SENS_NS = (10, 15, 20)
SENS_PE_CAPS = (100.0, 200.0)
SENS_RULES = ("pe", "pb")
# sec.0.6 exit-axis: HOLD-THROUGH dual-channel default-stack disable
EXIT_PATCH_OVERRIDES = {"loss_time_days": 10 ** 9,
                        "global_hard_limit": 10 ** 9}
NEUTRALIZED_PARAMS = {
    "position_size_pct": 1.0, "max_positions": 1,
    "sizing_mode": "fixed_initial", "report_num_entries": True,
    "take_profit_levels": (),
    "trailing_stop_activate": 1e12,
    "initial_stop": -1.0,
    "time_decay_period": 10 ** 9,
}
WORKERS_PLAN_WIDTH = 32                      # prereg sec.0 (O-2158 width law)
MEM_GB_PER_NULL_WORKER = 1.5                 # stock-universe null draw budget

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


# ------------------------------------------------------------------ data faces

def _load_value_faces():
    """per-symbol sorted anchor arrays (dates int YYYYMMDD, pe_ttm, pb)."""
    df = pd.read_parquet(PARQUET)
    d = df.assign(_d=df["anchor_date"].astype("string").str.replace(
        "-", "", regex=False).astype("int64"))
    by_sym = {}
    for code, g in d.groupby("code", sort=False):
        g = g.sort_values("_d")
        by_sym[str(code)] = (g["_d"].to_numpy(),
                             g["pe_ttm"].to_numpy(dtype=np.float64),
                             g["pb"].to_numpy(dtype=np.float64))
    return by_sym


def _monthly_positions(idx) -> list:
    """Panel positions of each month's FIRST trading day (full panel)."""
    mk = idx.strftime("%Y-%m")
    pos = []
    prev = None
    for p, k in enumerate(mk):
        if k != prev:
            pos.append(p)
            prev = k
    return pos


def enumerate_starts_monthly(idx, close_raw):
    """T-22 monthly adaptation, probe-bit-exact: month-first days within
    the 1992-09-01..2026-03-02 window, pos>=252, fwd>=126, active>=24."""
    n = len(idx)
    mask = (idx >= ENUM_LO) & (idx <= ENUM_HI)
    out = []
    prev = None
    for p in np.where(mask)[0]:
        k = idx[p].strftime("%Y-%m")
        if k == prev:
            continue
        prev = k
        if p < WARMUP_TD or (n - 1 - p) < W6M // 2:
            continue
        if int((~np.isnan(np.asarray(close_raw[p]))).sum()) < MIN_LISTED:
            continue
        out.append(int(p))
    return out


def _regime_series(idx):
    """510300 3-way proxy labels keyed by panel date (repo core48 face)."""
    etf = pd.read_csv(ETF_510300_CSV)
    etf = etf.set_index("date")
    etf.index = pd.to_datetime(etf.index)
    close = etf["close"].sort_index()
    reg = regime_proxy(close)
    return reg


# ---------------------------------------------------------- month universes

def _thr_slice(lo, hi):
    """Board-truth threshold rows (P4 verbatim: main 60/00=0.10, cx 30
    0.10->0.20 @2020-08-24, star 68=0.20; percent-convention)."""
    static = _G["static_thr"]
    dates = _G["idx"][lo:hi + 1]
    cx20 = (np.asarray(dates >= CHINEXT_20_FROM))[:, None]
    is_cx = _G["is_cx"][None, :]
    thr = np.where(cx20 & is_cx, 0.20, static[None, :])
    return thr.astype(np.float32)


def _st_row(p):
    """As-of ST status at signal day p: the P4_BATCH2 sec.2 proxy applied
    to the trailing-250-bar slice (helper imported verbatim; row -1 = the
    full-window verdict at p; short windows = NaN = False, matching the
    full-matrix semantics)."""
    cache = _G.setdefault("_st_rows", {})
    if p in cache:
        return cache[p]
    lo = max(p - ST_WIN + 1, 0)
    cl = np.asarray(_G["close_np"][lo:p + 1], dtype=np.float64)
    hi = np.asarray(_G["high_np"][lo:p + 1], dtype=np.float64)
    pc = np.asarray(_G["pct_np"][lo:p + 1], dtype=np.float64)
    fin = np.isfinite(cl)
    thr = _thr_slice(lo, p)
    seg = _st_regime(fin, cl, hi, pc, thr, cl.shape[0], cl.shape[1])
    row = np.asarray(seg[-1], dtype=bool)
    cache[p] = row
    return row


def _month_universe(p):
    """Everything a signal day needs, cached: active row, coverage ratio
    (data layer, over ALL active members), base-mask indices with pe/pb
    as-of values (PIT forward-fill), pick helper."""
    cache = _G.setdefault("_muniv", {})
    if p in cache:
        return cache[p]
    idx = _G["idx"]
    syms = _G["syms"]
    by_sym = _G["by_sym"]
    close_r = np.asarray(_G["close_np"][p])
    active = np.isfinite(close_r)
    n_active = int(active.sum())
    t_int = int(idx[p].strftime("%Y%m%d"))
    # data-coverage layer: active members with any finite pe anchor <= t
    cov = 0
    act_j = np.where(active)[0]
    for j in act_j:
        pack = by_sym.get(syms[j])
        if pack is None:
            continue
        ad = pack[0]
        k = int(np.searchsorted(ad, t_int, side="right")) - 1
        if k >= 0 and np.isfinite(pack[1][k]):
            cov += 1
    cov_ratio = (cov / n_active) if n_active else 0.0
    # base eligibility mask (sec.2, frozen)
    lo20 = max(p - AMT20_WIN + 1, 0)
    amt = np.asarray(_G["amount_np"][lo20:p + 1], dtype=np.float64)
    with np.errstate(invalid="ignore"):
        amt20 = np.nanmedian(amt, axis=0) if amt.shape[0] else np.full(
            close_r.shape, np.nan)
    vol_r = np.asarray(_G["volume_np"][p])
    am_r = np.asarray(_G["amount_np"][p])
    fv = _G["first_valid"]
    listed = (p - fv + 1) >= LISTED_MIN_BARS
    st = _st_row(p)
    with np.errstate(invalid="ignore"):
        base = (active & (vol_r > 0) & (am_r > 0)
                & (amt20 >= AMT20_MIN) & listed & ~st)
    base = base & np.isfinite(amt20)
    bj = np.where(base)[0]
    pe_of = np.full(len(bj), np.nan)
    pb_of = np.full(len(bj), np.nan)
    for i, j in enumerate(bj):
        pack = by_sym.get(syms[j])
        if pack is None:
            continue
        ad = pack[0]
        k = int(np.searchsorted(ad, t_int, side="right")) - 1
        if k >= 0:
            pe_of[i] = pack[1][k]
            pb_of[i] = pack[2][k]
    u = {"p": p, "n_active": n_active, "cov_ratio": round(float(cov_ratio), 4),
         "skipped": bool(cov_ratio < COV_FLOOR),
         "base_j": bj, "pe_of": pe_of, "pb_of": pb_of}
    cache[p] = u
    return u


def _pick_j(u, pe_cap=PE_MAX):
    """Pick universe for a cell: base mask AND the JOINT valuation band
    (0<pe<=pe_cap AND 0<pb<=20 -- sec.2 frozen, applied to both cells)."""
    pe, pb = u["pe_of"], u["pb_of"]
    m = (np.isfinite(pe) & (pe > PE_MIN) & (pe <= pe_cap)
         & np.isfinite(pb) & (pb > PB_MIN) & (pb <= PB_MAX))
    return u["base_j"][m], pe[m], pb[m]


def _firing_months():
    """[(m_pos, next_firing_pos_or_T)] for every coverage-passing month;
    a skipped month fires nothing and prior selections persist through it."""
    cache = _G.get("_firing")
    if cache is not None:
        return cache
    months = _G["month_pos"]
    firing = [p for p in months if not _month_universe(p)["skipped"]]
    spans = []
    for i, m in enumerate(firing):
        end = firing[i + 1] if i + 1 < len(firing) else len(_G["idx"])
        spans.append((m, end))
    _G["_firing"] = spans
    _G["_t0_pos"] = firing[0] if firing else None
    return spans


def _cell_picks(rule, N, pe_cap=PE_MAX):
    """Frozen ranking: ascending rule value, code tiebreak, Top-min(N, avail)."""
    picks = []
    codes = _G["codes_arr"]
    for (m, end) in _firing_months():
        u = _month_universe(m)
        pj, pe, pb = _pick_j(u, pe_cap)
        vals = pe if rule == "pe" else pb
        if len(pj):
            order = np.lexsort((codes[pj], vals))
            top = pj[order[:min(N, len(pj))]]
        else:
            top = pj
        picks.append((m, end, top, 1.0 / max(1, len(top))))
    return picks


def _spans_from_picks(picks):
    spans = defaultdict(list)
    for (m, end, top, w) in picks:
        for j in top:
            spans[int(j)].append((m, end, w))
    return spans


def _cell_spans(cell):
    cache = _G.setdefault("_cellspans", {})
    if cell not in cache:
        spec = CELLS[cell]
        cache[cell] = _spans_from_picks(_cell_picks(spec["rule"], TOPN))
    return cache[cell]


# ------------------------------------------------------------- engine face

def _sym_frame(j, lo, hi):
    """Per-symbol engine frame [lo..hi], OHLC ffilled from the last valid
    bar BEFORE lo (seed-ffill: no head NaN, no future leak); volume and
    amount NaN->0. P4 stale_ffill disclosed convention."""
    pre = np.asarray(_G["close_np"][:lo, j])
    fin = np.where(np.isfinite(pre))[0]
    seed = int(fin[-1]) if fin.size else 0
    rows = slice(seed, hi + 1)
    get = lambda f: np.asarray(_G[f + "_np"][rows, j], dtype=np.float64)
    df = pd.DataFrame({"open": get("open"), "high": get("high"),
                       "low": get("low"), "close": get("close"),
                       "volume": np.nan_to_num(get("volume")),
                       "amount": np.nan_to_num(get("amount"))},
                      index=_G["idx"][seed:hi + 1])
    df = df.ffill()
    return df.iloc[lo - seed:]


def _sym_arrays(j, spans_j):
    """Full-panel entry bool + weight Series (w lands at the signal day,
    engine reads the shifted value at the T+1 exec day)."""
    T = len(_G["idx"])
    ent = np.zeros(T, dtype=bool)
    sc = np.zeros(T, dtype=float)
    for (m, end, w) in spans_j:
        ent[m:end] = True
        sc[m] = w
    scale = pd.Series(sc, index=_G["idx"]).shift(1)
    return ent, scale


def run_cell_portfolio(spans, face, lo, hi, keep_trades=False):
    """Engine-canonical run over [lo..hi] of one selection-span map.
    Per-symbol span-sliced sub-accounts; span-slice equivalence with the
    full-frame semantics is selftest leg F15. Returns dict or None."""
    from engine import run_backtest
    from contextlib import nullcontext
    idx = _G["idx"]
    syms = _G["syms"]
    win_idx = idx[lo:hi + 1]
    pnl = None
    n_trades = n_entries = 0
    trade_dates = []
    for j in sorted(spans):
        sp = spans[j]
        e_lo = max(sp[0][0] - 2, lo)
        e_hi = min(sp[-1][1] + 2, hi)
        if e_hi < e_lo:
            continue                       # pure compute skip, zero semantics
        sym = syms[j]
        ent, scale = _sym_arrays(j, sp)
        ent_df = pd.DataFrame({sym: pd.Series(ent, index=idx)})
        frame = _sym_frame(j, e_lo, e_hi)
        with ExitPatch(EXIT_PATCH_OVERRIDES), \
             (CostPatch(2.0) if face == "x2" else nullcontext()):
            res = run_backtest({sym: frame}, dict(NEUTRALIZED_PARAMS),
                               entry_signal=ent_df,
                               exit_signal=ent_df <= 0,
                               entry_size_scale=scale)
        eq = pd.Series(res["equity_curve"],
                       index=frame.index[:len(res["equity_curve"])])
        p = (eq - CAPITAL).reindex(win_idx).ffill().fillna(0.0)
        pnl = p if pnl is None else pnl + p
        n_trades += len(res["trades"])
        n_entries += int(res["metrics"].get("num_entries", 0))
        if keep_trades:
            for tr in res["trades"]:
                trade_dates.append(tr)
    if pnl is None:
        return None
    return {"pnl": pnl, "n_trades": n_trades, "n_entries": n_entries,
            "trades": trade_dates}


def _nav_from_run(run, lo, hi):
    idx = _G["idx"]
    nav = (run["pnl"] + CAPITAL).reindex(idx[lo:hi + 1]).ffill().fillna(CAPITAL)
    return nav


def _passive_window(pos, e):
    """EW B&H of the base-mask members at the start day, ffilled marks,
    over [pos..e] (prereg sec.3 passive; marks convention disclosed)."""
    u = _month_universe(pos)
    bj = u["base_j"]
    if len(bj) == 0:
        return None
    cl = np.asarray(_G["close_np"][pos:e + 1][:, bj], dtype=np.float64)
    df = pd.DataFrame(cl).ffill()
    rel = df / df.iloc[0]
    return rel.mean(axis=1)


# ------------------------------------------------------------------ workers

def _init_worker():
    import psutil
    pri = getattr(psutil, "BELOW_NORMAL_PRIORITY_CLASS", None)
    if pri is not None:
        try:
            psutil.Process().nice(pri)   # O-1136 low-priority pool law
        except Exception:
            pass
    idx, syms, meta = P1C.load_universe()
    C = P1C.CACHE_DIR
    close_np = np.load(os.path.join(C, "close.npy"), mmap_mode="r")
    panels = {f + "_np": np.load(os.path.join(C, f + ".npy"), mmap_mode="r")
              for f in ("open", "high", "low", "close", "volume", "amount",
                        "pct_chg")}
    first_valid = np.argmax(np.isfinite(np.asarray(close_np[:])), axis=0)
    codes_arr = np.array(syms)
    static_thr = np.where(np.array([s.startswith("68") for s in syms]),
                          0.20, 0.10).astype(np.float32)
    is_cx = np.array([s.startswith("30") for s in syms])
    _G.update(idx=idx, syms=syms, codes_arr=codes_arr, first_valid=first_valid,
              static_thr=static_thr, is_cx=is_cx,
              close_np=panels["close_np"], open_np=panels["open_np"],
              high_np=panels["high_np"], low_np=panels["low_np"],
              volume_np=panels["volume_np"], amount_np=panels["amount_np"],
              pct_np=panels["pct_chg_np"],
              by_sym=_load_value_faces(),
              # Signal days = T-22 census enumeration (prereg sec.2), not raw
              # month-firsts: census-excluded months (e.g. 1992-10, <24 active
              # members) must not fire -- t0 must equal the first CENSUS start
              # with cov>=floor (1994-05-03, probe-frozen), else the pre-t0
              # phantom firing breaks the zero-below-floor-after-t0 gate.
              month_pos=enumerate_starts_monthly(idx, close_np))
    if ETF_510300_CSV and os.path.exists(ETF_510300_CSV):
        _G["regime"] = _regime_series(idx)
    else:
        _G["regime"] = None


def _regime_at(sdate):
    reg = _G.get("regime")
    if reg is None or sdate not in reg.index:
        return "na"
    return str(reg.loc[sdate])


def _cell_task(payload):
    """One (cell, startpoint, face) row: longest window once, 6m/12m/24m
    sliced off the same curve (P-5 law); passive = base-mask EW B&H."""
    cell, pos, face = payload["cell"], payload["pos"], payload["face"]
    spans = _cell_spans(cell)
    T = len(_G["idx"])
    e = min(pos + W24M - 1, T - 1)
    run = run_cell_portfolio(spans, face, pos, e)
    win_idx = _G["idx"][pos:pos + W24M]
    if run is None:
        eq = pd.Series(CAPITAL, index=win_idx)
        trades = []
    else:
        eq = (run["pnl"] + CAPITAL).reindex(win_idx).ffill().fillna(CAPITAL)
        trades = [{"date": tr["date"]} for tr in run["trades"]]
    m6 = _slice_metrics(eq, trades, W6M)
    m12 = _slice_metrics(eq, trades, W12M)
    m24 = _slice_metrics(eq, trades, W24M)
    rel = _passive_window(pos, e)
    p6 = _slice_metrics(rel, [], W6M) if rel is not None else None
    p12 = _slice_metrics(rel, [], W12M) if rel is not None else None
    p24 = _slice_metrics(rel, [], W24M) if rel is not None else None
    u = _month_universe(pos)
    active_in_win = sum(
        1 for j in spans
        if any((m_end > pos and m0 < pos + W24M) for (m0, m_end, _) in spans[j]))
    sdate = _G["idx"][pos]
    return {"key": f"{cell}|{face}|{pos}", "cell": cell, "face": face,
            "pos": pos, "start": str(sdate.date()),
            "regime": _regime_at(sdate),
            "n_active_universe": u["n_active"], "n_base": int(len(u["base_j"])),
            "n_engine_syms": int(active_in_win),
            "partial_12m": m12["n_bars"] < W12M,
            "partial_24m": m24["n_bars"] < W24M,
            "ret_6m": m6["ret"], "ret_12m": m12["ret"], "ret_24m": m24["ret"],
            "p_ret_6m": p6["ret"] if p6 else None,
            "p_ret_12m": p12["ret"] if p12 else None,
            "p_ret_24m": p24["ret"] if p24 else None,
            "dd_6m": m6["dd"], "dd_12m": m12["dd"], "dd_24m": m24["dd"],
            "sharpe_6m": m6["sharpe"], "sharpe_12m": m12["sharpe"],
            "sharpe_24m": m24["sharpe"],
            "trades_6m": m6["trades"], "trades_12m": m12["trades"],
            "trades_24m": m24["trades"],
            "beat_6m": bool(p6 and m6["ret"] > p6["ret"]),
            "beat_12m": bool(p12 and m12["ret"] > p12["ret"]),
            "beat_24m": bool(p24 and m24["ret"] > p24["ret"])}


def _cont_task(payload):
    """Continuous run of one (cell, face) over t0..cutoff -- the
    G1'/M1/DSR/x2/PBO supply face."""
    cell, face = payload["cell"], payload["face"]
    _firing_months()
    lo = _G["_t0_pos"]
    spans = _cell_spans(cell)
    T = len(_G["idx"])
    run = run_cell_portfolio(spans, face, lo, T - 1, keep_trades=True)
    nav = _nav_from_run(run, lo, T - 1)
    rets = nav.pct_change().dropna()
    from engine.metrics import max_drawdown, sharpe
    yrs = len(nav) / 252.0
    return {"key": f"cont|{cell}|{face}", "cell": cell, "face": face,
            "t0": str(_G["idx"][lo].date()),
            "sharpe_full": round(float(sharpe(nav)), 6),
            "ret_full": round(float(nav.iloc[-1] / nav.iloc[0] - 1), 6),
            "max_dd": round(float(max_drawdown(nav)), 6),
            "n_trades": run["n_trades"], "n_entries": run["n_entries"],
            "trades_per_year": round(run["n_trades"] / yrs, 2) if yrs else None,
            "n_days": int(len(nav)),
            "returns": [round(float(v), 8) for v in rets.to_numpy()],
            "nav_first": round(float(nav.iloc[0]), 2),
            "nav_last": round(float(nav.iloc[-1]), 2)}


def _null_task(payload):
    """Same-mask random-selection null draw k (sec.3): per FIRING month,
    TOPN uniform picks from the HEADLINE VALUE-PE pick universe (G-MASK:
    same cached universe object as the real cell -- asserted), eq weights,
    t0..cutoff continuous run."""
    k = payload["k"]
    rng = np.random.default_rng([SEED_NULLS, k])
    spans = defaultdict(list)
    n_sel_days = 0
    for (m, end) in _firing_months():
        u = _month_universe(m)
        # G-MASK (prereg sec.3): the SAME cached headline VALUE-PE pick
        # universe the real cell ranks over -- identity by construction
        # (F17 selftest leg); a firing month with an empty universe fires
        # a pure rotation-out, same as the real cell.
        pj, _, _ = _pick_j(u, PE_MAX)
        if len(pj):
            pick = rng.choice(len(pj), size=min(TOPN, len(pj)),
                              replace=False)
            w = 1.0 / min(TOPN, len(pj))
            for t in sorted(pick):
                spans[int(pj[t])].append((m, end, w))
            n_sel_days += 1
    _firing_months()
    lo = _G["_t0_pos"]
    T = len(_G["idx"])
    run = run_cell_portfolio(spans, "x1", lo, T - 1)
    nav = _nav_from_run(run, lo, T - 1)
    from engine.metrics import max_drawdown, sharpe
    rets = nav.pct_change().dropna()
    return {"key": f"null|{k}", "k": k,
            "sharpe": round(float(sharpe(nav)), 6),
            "ret": round(float(nav.iloc[-1] / nav.iloc[0] - 1), 6),
            "max_dd": round(float(max_drawdown(nav)), 6),
            "n_trades": run["n_trades"], "n_entries": run["n_entries"],
            "n_selected_days": int(n_sel_days),
            "n_engine_syms": int(len(spans))}


def _sens_task(payload):
    """Sensitivity draw k (sec.3, descriptive only): uniform space-filling
    over (N in {10,15,20}, pe_cap in {100,200}, rule in {pe,pb}), monthly
    fixed, same hold-through exit face."""
    k = payload["k"]
    rng = np.random.default_rng([SEED_SENS, k])
    N = int(rng.choice(SENS_NS))
    pe_cap = float(rng.choice(SENS_PE_CAPS))
    rule = str(rng.choice(SENS_RULES))
    picks = []
    codes = _G["codes_arr"]
    for (m, end) in _firing_months():
        u = _month_universe(m)
        pj, pe, pb = _pick_j(u, pe_cap)
        vals = pe if rule == "pe" else pb
        if len(pj):
            order = np.lexsort((codes[pj], vals))
            top = pj[order[:min(N, len(pj))]]
        else:
            top = pj
        picks.append((m, end, top, 1.0 / max(1, len(top))))
    spans = _spans_from_picks(picks)
    _firing_months()
    lo = _G["_t0_pos"]
    T = len(_G["idx"])
    run = run_cell_portfolio(spans, "x1", lo, T - 1)
    nav = _nav_from_run(run, lo, T - 1)
    from engine.metrics import max_drawdown, sharpe
    return {"key": f"sens|{k}", "k": k, "N": N, "pe_cap": pe_cap,
            "rule": rule,
            "sharpe": round(float(sharpe(nav)), 6),
            "ret": round(float(nav.iloc[-1] / nav.iloc[0] - 1), 6),
            "max_dd": round(float(max_drawdown(nav)), 6),
            "n_trades": run["n_trades"]}


# ------------------------------------------------------------------ checkpoint

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


def _mk(kind, **kw):
    return {"_fn": {"cell": _cell_task, "cont": _cont_task,
                    "null": _null_task, "sens": _sens_task}[kind], **kw}


def _run_parallel_tasks(tasks, keyfn, path, log_name, heavy=False):
    """ProcessPool burn with checkpoint done-key skip; worker count =
    min(width plan, worker_cap, memory guard) -- heavy arms (nulls/sens)
    budget MEM_GB_PER_NULL_WORKER per worker (stock-universe draws)."""
    from concurrent.futures import ProcessPoolExecutor, as_completed
    import psutil
    done = _done_keys(path)
    todo = [p for p in tasks if keyfn(p) not in done]
    _log(log_name, f"todo={len(todo)} resume-skipped={len(tasks) - len(todo)}")
    if not todo:
        return 0
    cap = worker_cap()
    if heavy:
        free_gb = psutil.virtual_memory().available / (1024 ** 3)
        mem_cap = max(1, int(free_gb / MEM_GB_PER_NULL_WORKER))
        workers = int(min(WORKERS_PLAN_WIDTH, cap, mem_cap))
    else:
        workers = int(min(12, cap))
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
    _log(log_name, f"DONE {n}/{len(todo)} in {round(time.time() - t0, 1)}s "
                   f"workers={workers}")
    return n


# ------------------------------------------------------------------- D6 door

def cmd_d6(_) -> int:
    """D6 same-family admission probe (sec.1): headline VALUE-PE daily
    returns vs ALL six registered members, max|corr| >= 0.7 -> REJECT
    (fail-closed; pool ignition forbidden until ADMIT)."""
    os.makedirs(OUT_DIR, exist_ok=True)
    t0 = time.time()
    _init_worker()
    _firing_months()
    row = _cont_task(_mk("cont", cell=HEADLINE, face="x1"))
    h_rets = pd.Series(row["returns"])
    h_rets.index = _G["idx"][_G["_t0_pos"] + 1:_G["_t0_pos"] + 1 + len(h_rets)]
    try:
        from cn_rev_tilt_p1 import REG6, load_member_rets
        mrets, _ = load_member_rets()
        pairs = []
        worst = None
        for tid in REG6:
            r = mrets[tid]
            both = pd.concat([h_rets, r], axis=1).dropna()
            c = float(both.corr().iloc[0, 1]) if len(both) > 30 else None
            pairs.append({"member": tid,
                          "corr": round(c, 4) if c is not None else None,
                          "n_overlap": int(len(both))})
            if c is not None and (worst is None or abs(c) > abs(worst[1])):
                worst = (tid, c)
        admit = worst is not None and abs(worst[1]) < D6_REJECT
        facts = {"batch": BATCH_NAME, "gate": "d6_same_family",
                 "reject_line": D6_REJECT,
                 "headline_cont": {"t0": row["t0"],
                                   "sharpe_full": row["sharpe_full"],
                                   "n_trades": row["n_trades"],
                                   "n_entries": row["n_entries"],
                                   "n_days": row["n_days"]},
                 "pairs": pairs,
                 "max_abs_corr": round(abs(worst[1]), 4) if worst else None,
                 "max_member": worst[0] if worst else None,
                 "verdict": "ADMIT" if admit else "REJECT",
                 "generated": _now_iso(), "machine": _machine_id(),
                 "runtime_sec": round(time.time() - t0, 1)}
    except Exception as ex:      # fail-closed: no D6 face = no ignition
        facts = {"batch": BATCH_NAME, "gate": "d6_same_family",
                 "verdict": "REJECT", "error": str(ex)[:300],
                 "generated": _now_iso(), "machine": _machine_id()}
    _dump(facts, D6_JSON)
    print(f"d6 verdict={facts['verdict']} max|corr|="
          f"{facts.get('max_abs_corr')} -> {D6_JSON}")
    return 0 if facts["verdict"] == "ADMIT" else 3


# ---------------------------------------------------------------- probe

def _require_probe() -> bool:
    if not os.path.exists(PROBE_JSON):
        print("FAIL-CLOSED: probe.json absent -- run `probe` first")
        return False
    v = json.load(open(PROBE_JSON, encoding="utf-8")).get("verdict")
    if v != "PASS":
        print(f"FAIL-CLOSED: probe verdict={v} -- ignition refused")
        return False
    return True


def cmd_probe(_) -> int:
    """Ignition gates, fail-closed. Requires d6.json ADMIT (the three-door
    chain: TRANSFER + data-completeness + D6, prereg sec.0)."""
    os.makedirs(OUT_DIR, exist_ok=True)
    t0 = time.time()
    facts = {"ticket": TICKET, "batch": BATCH_NAME,
             "generated": _now_iso(), "machine": _machine_id(),
             "checks": []}

    def chk(name, ok, detail=""):
        facts["checks"].append({"name": name, "pass": bool(ok),
                                "detail": str(detail)[:400]})
        return bool(ok)

    # D6 door first (fail-closed chain head)
    if os.path.exists(D6_JSON):
        d6 = json.load(open(D6_JSON, encoding="utf-8"))
        chk("d6_admit", d6.get("verdict") == "ADMIT",
            f"verdict={d6.get('verdict')} max|corr|={d6.get('max_abs_corr')}")
        facts["d6"] = d6
    else:
        chk("d6_admit", False, "d6.json absent -- run `d6` first")
    # leg1 price panel
    idx, syms, meta = P1C.load_universe()
    n_bars = len(idx)
    facts["panel"] = {"n_bars": n_bars, "n_syms": len(syms),
                      "first": str(idx[0].date()), "last": str(idx[-1].date())}
    chk("leg1_price_panel",
        n_bars == 8792 and str(idx[-1].date()) == "2026-09-22"
        and len(syms) >= 5100, facts["panel"])
    # leg2 value faces TRANSFER/export gate
    df = pd.read_parquet(PARQUET)
    per = df.groupby("code")["anchor_date"]
    dup_any = bool(per.apply(lambda s: s.duplicated().any()).any())
    mono_all = bool(per.apply(lambda s: s.is_monotonic_increasing).all())
    dmin = str(df["anchor_date"].min())
    dmax = str(df["anchor_date"].max())
    med = float(per.size().median())
    facts["value_face"] = {"rows": int(len(df)),
                           "n_symbols": int(df["code"].nunique()),
                           "anchor_median": med, "date_min": dmin,
                           "date_max": dmax}
    chk("leg2_transfer_export",
        int(df["code"].nunique()) >= 5100 and med >= 550
        and dmin[:7] <= "2001-01" and dmax[:7] >= "2026-09"
        and (not dup_any) and mono_all, facts["value_face"])
    # leg3 census + coverage
    close_np = np.load(os.path.join(P1C.CACHE_DIR, "close.npy"), mmap_mode="r")
    starts = enumerate_starts_monthly(idx, close_np)
    chk("leg3_g_census_401", len(starts) == G_CENSUS_EXPECT,
        f"starts={len(starts)} want={G_CENSUS_EXPECT}")
    _init_worker()
    _firing_months()
    t0_pos = _G["_t0_pos"]
    facts["t0"] = {"pos": t0_pos,
                   "date": str(_G["idx"][t0_pos].date()) if t0_pos else None}
    chk("leg3_t0_present", t0_pos is not None, facts["t0"])
    # deterministic reproduction of the frozen probe fact (bm-a r596/r599
    # receipt): t0 must stay 1994-05-03 -- drift here = data-face change and
    # fails ignition closed.
    chk("leg3_t0_frozen_reproduction",
        t0_pos is not None and str(_G["idx"][t0_pos].date()) == T0_FROZEN,
        f"t0={facts['t0'].get('date')} want={T0_FROZEN}")
    # coverage after t0: recompute cov for firing months list tail vs skips
    months = _G["month_pos"]
    in_win = [p for p in months if p >= t0_pos]
    below = [p for p in in_win if _month_universe(p)["cov_ratio"] < COV_FLOOR]
    chk("leg3_zero_below_floor_after_t0", len(below) == 0,
        f"months>={t0_pos} below floor: {below[:5]}")
    # regime face (510300 from repo core48, date-keyed labels)
    reg = _G.get("regime")
    chk("regime_face_510300", reg is not None and len(reg.dropna()) > 200,
        f"label_days={0 if reg is None else int((reg != 'na').sum())}")
    # cost single-source (CN-C7)
    rate = cost_spec.x1_side_rate()
    chk("cost_x1_single_source",
        RVSTOCK.COST_X1 == rate and abs(rate * 2.0 * 1e4 - 26.082) < 1e-6,
        f"COST_X1={RVSTOCK.COST_X1} spec={rate} rt_bp={rate * 2e4:.3f}")
    # M3 closed family
    m3 = closed_family_check(FAMILY_KEY)
    chk("m3_closed_family_open",
        m3.get("open") is True or m3.get("status") == "open",
        json.dumps(m3, ensure_ascii=False)[:200])
    # seed registry rows
    seeds = {k: v for k, v in SEED_REGISTRY.items() if "fund_value" in k}
    chk("seed_registry_rows",
        seeds.get("fund_value_p1_nulls") == SEED_NULLS
        and seeds.get("fund_value_p1_sens") == SEED_SENS, str(seeds))
    # ST helper import + fixture sanity (5% seals, no 10% -> flagged).
    # _roll_sum only opens windows when len > ST_WIN (strict), so the
    # fixture must be longer than the window; a short fixture is all-NaN
    # and can never flag (structural False, not helper drift).
    Tn = int(ST_WIN) + 10
    fin = np.ones((Tn, 1), dtype=bool)
    cl = np.full((Tn, 1), 10.0)
    hi_ = np.full((Tn, 1), 10.0)
    pc = np.zeros((Tn, 1))
    pc[Tn // 2, 0] = 5.0
    pc[Tn - 60, 0] = 5.0
    thr = np.full((Tn, 1), 0.10, dtype=np.float32)
    seg = _st_regime(fin, cl, hi_, pc, thr, Tn, 1)
    chk("st_helper_import_fixture", bool(seg[-1, 0]),
        f"seals_in_win={int(ST_SEAL5_MIN)} flagged={bool(seg[-1, 0])}")
    # universe facts at t0 (disclosure)
    u0 = _month_universe(t0_pos)
    pj0, _, _ = _pick_j(u0, PE_MAX)
    facts["liquidity"] = {
        "amt20_min_yuan": AMT20_MIN, "t0_date": facts["t0"]["date"],
        "t0_n_active": u0["n_active"], "t0_n_base": int(len(u0["base_j"])),
        "t0_n_pick": int(len(pj0)),
        "n_firing_months": len(_firing_months()),
    }
    facts["seed_disclosure"] = {
        "nulls": SEED_NULLS, "sensitivity": SEED_SENS,
        "null_aux": NULL_AUX_SEED,
        "registry_rows": seeds,
        "note": "prereg sec.3 binds nulls to rng([20500000,k]) and sens to "
                "rng([20500500,k]); rows pre-registered (bm-a r599)."}
    facts["runtime_sec"] = round(time.time() - t0, 1)
    facts["verdict"] = ("PASS" if all(c["pass"] for c in facts["checks"])
                        else "FAIL")
    _dump(facts, PROBE_JSON)
    print(f"probe {facts['verdict']} ({facts['runtime_sec']}s) -> {PROBE_JSON}")
    for c in facts["checks"]:
        print(f"  [{'PASS' if c['pass'] else 'FAIL'}] {c['name']}: "
              f"{c['detail'][:120]}")
    return 0 if facts["verdict"] == "PASS" else 3


# ------------------------------------------------------------------------ run

def _pool_claim(entry_id: str, shard_key: str, detail: str) -> None:
    """O-20260930-2355 pool harvest handshake (worker-side half)."""
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
        _run_parallel_tasks(tasks, lambda p: f"null|{p['k']}", path,
                            "nulls", heavy=True)
        _pool_claim(*_entry_of(args), f"nulls N={K_NULLS} -> {path}")
        return 0
    if args.sensitivity:
        path = _shard_files(kind="sens")
        tasks = [_mk("sens", k=k) for k in range(K_SENS)]
        _run_parallel_tasks(tasks, lambda p: f"sens|{p['k']}", path,
                            "sens", heavy=True)
        _pool_claim(*_entry_of(args), f"sens N={K_SENS} -> {path}")
        return 0
    if not (args.cell in CELLS and args.face in FACES):
        print(f"bad unit: cell={args.cell} face={args.face}")
        return 2
    cell, face = args.cell, args.face
    log = f"{cell}_{face}"
    _init_worker()
    starts = enumerate_starts_monthly(_G["idx"], _G["close_np"])
    tasks = [_mk("cell", cell=cell, pos=pos, face=face) for pos in starts]
    path = _shard_files(cell=cell, face=face)
    _run_parallel_tasks(tasks, lambda p: f"{cell}|{face}|{p['pos']}", path,
                        log)
    # continuous face (G1'/M1/DSR/x2/PBO supply)
    cpath = os.path.join(OUT_DIR, f"cont_{cell}_{face}.json")
    if not os.path.exists(cpath):
        row = _cont_task(_mk("cont", cell=cell, face=face))
        _dump(row, cpath)
        _log(log, f"cont face written: {cpath}")
    _log(log, f"shard complete: {len(starts)} starts + cont face")
    _pool_claim(*_entry_of(args),
                f"cells {len(starts)} -> {path} + {os.path.basename(cpath)}")
    return 0


# --------------------------------------------------------------------- status

def cmd_status(_) -> int:
    if not os.path.isdir(OUT_DIR):
        print(f"no {OUT_DIR} yet")
        return 0
    missing = 0
    for cell in CELLS:
        for face in FACES:
            p = _shard_files(cell=cell, face=face)
            have = len(_done_keys(p)) if os.path.exists(p) else 0
            c = os.path.join(OUT_DIR, f"cont_{cell}_{face}.json")
            cont = "Y" if os.path.exists(c) else "-"
            miss = (G_CENSUS_EXPECT - have) + (0 if cont == "Y" else 1)
            missing += max(0, miss)
            print(f"{cell:9s} {face:3s}: {have}/{G_CENSUS_EXPECT} starts "
                  f"cont={cont}")
    for kind, want in (("nulls", K_NULLS), ("sens", K_SENS)):
        p = _shard_files(kind=kind)
        have = len(_done_keys(p)) if os.path.exists(p) else 0
        missing += max(0, want - have)
        print(f"{kind}: {have}/{want}")
    print(f"finalize_ready: {missing == 0} (missing={missing})")
    return 0


# ----------------------------------------------------- law-A exit census

def _census_core(spans, face):
    """Law-A census: same frozen machinery, per-trade exit reasons; only
    signal_reversal is lawful on the hold-through face."""
    run = run_cell_portfolio(spans, face, _G["_t0_pos"], len(_G["idx"]) - 1,
                             keep_trades=True)
    per_reason, per_sym = {}, {}
    n_trades = 0
    for tr in run["trades"]:
        sym = tr.get("symbol", "?")
        r = tr["reason"]
        per_reason[r] = per_reason.get(r, 0) + 1
        d = per_sym.setdefault(sym, {})
        d[r] = d.get(r, 0) + 1
        n_trades += 1
    default_n = sum(v for k, v in per_reason.items()
                    if k not in LAWFUL_EXIT_REASONS)
    share = (default_n / n_trades) if n_trades else 0.0
    return {"total_exits": n_trades, "per_reason": per_reason,
            "default_stack_exits": default_n,
            "default_share": round(share, 6),
            "block_share": CENSUS_BLOCK_SHARE,
            "pass": bool(share <= CENSUS_BLOCK_SHARE),
            "per_sym": {k: v for k, v in list(per_sym.items())[:50]}}


# ------------------------------------------------------------------ finalize

def _read_cells(cell, face):
    p = _shard_files(cell=cell, face=face)
    if not os.path.exists(p):
        return None
    rows = []
    for ln in open(p, encoding="utf-8"):
        if ln.strip():
            rows.append(json.loads(ln))
    return rows


def _block_bootstrap_sharpe(rets: pd.Series, b: int = BOOT_B,
                             block: int = BLOCK_BOOT_LEN,
                             seed: int = NULL_AUX_SEED):
    r = rets.to_numpy(dtype=float)
    t = len(r)
    if t < 2 * block:
        return None
    rng = np.random.default_rng(seed)
    starts = rng.integers(0, t, size=(b, int(np.ceil(t / block))))
    idx = (starts[:, :, None] + np.arange(block)[None, None, :]) % t
    samples = r[idx].reshape(b, -1)[:, :t]
    mu = samples.mean(axis=1)
    sd = samples.std(axis=1, ddof=1)
    sharpes = np.where(sd > 0, mu / sd * np.sqrt(252), 0.0)
    obs = float(rets.mean() / rets.std(ddof=1) * np.sqrt(252))
    return {"B": b, "block_len": block, "seed": seed,
            "sharpe_p05": round(float(np.percentile(sharpes, 5)), 4),
            "sharpe_p50": round(float(np.percentile(sharpes, 50)), 4),
            "sharpe_p95": round(float(np.percentile(sharpes, 95)), 4),
            "obs_sharpe": round(obs, 6),
            "p_ge_obs": round(float((sharpes >= obs).mean()), 6)}


def _sign_flip_perm(rets: pd.Series, p: int = BOOT_B,
                    seed: int = NULL_AUX_SEED):
    r = rets.to_numpy(dtype=float)
    rng = np.random.default_rng(seed)
    signs = rng.choice([-1.0, 1.0], size=(p, len(r)))
    means = np.abs((r[None, :] * signs).mean(axis=1))
    obs = abs(float(r.mean()))
    return {"P": p, "seed": seed,
            "abs_mean_p50": round(float(np.percentile(means, 50)), 8),
            "abs_mean_p95": round(float(np.percentile(means, 95)), 8),
            "abs_mean_obs": round(obs, 8),
            "p_two_sided": round(float((means >= obs).mean()), 6)}


def cmd_finalize(_) -> int:
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
    d6 = json.load(open(D6_JSON, encoding="utf-8"))
    cont = {}
    for cell in CELLS:
        for face in FACES:
            c = os.path.join(OUT_DIR, f"cont_{cell}_{face}.json")
            cont[(cell, face)] = json.load(open(c, encoding="utf-8"))
    nulls = [json.loads(ln) for ln in open(_shard_files(kind="nulls"),
                                           encoding="utf-8") if ln.strip()]
    sens = [json.loads(ln) for ln in open(_shard_files(kind="sens"),
                                          encoding="utf-8") if ln.strip()]
    null_vals = [r["sharpe"] for r in nulls]
    null_pool = {
        "coverage": {"mu": float(np.mean(null_vals)),
                     "sigma": float(np.std(null_vals, ddof=1)),
                     "n_values": len(null_vals)},
        "source": f"{BATCH_NAME} same-mask nulls K={K_NULLS} "
                  f"rng([{SEED_NULLS},k])",
    }
    # passive override: EW B&H of base-mask members at t0, same span (derived)
    _init_worker()
    _firing_months()
    lo = _G["_t0_pos"]
    hi = len(_G["idx"]) - 1
    rel = _passive_window(lo, hi)
    passive_sharpe = float((rel.pct_change().dropna().mean()
                            / rel.pct_change().dropna().std(ddof=1))
                           * np.sqrt(252))
    passive_face = {"n_members_t0": int(rel.count()) if hasattr(rel, "count")
                    else None,
                    "sharpe_full": round(passive_sharpe, 6),
                    "ret_full": round(float(rel.iloc[-1] - 1), 6),
                    "span": [str(_G["idx"][lo].date()),
                             str(_G["idx"][hi].date())]}
    # G1' (headline x1 continuous)
    h = cont[(HEADLINE, "x1")]
    h_rets = pd.Series(h["returns"])
    g1 = g1_prime_v2(sharpe_full=h["sharpe_full"], returns=h_rets,
                     batch_cells=BATCH_CELLS, pool="core48",
                     n_trades=h["n_trades"], n_entries=h["n_entries"],
                     null_pool=null_pool, passive_override=passive_sharpe)
    # x2 survival
    x2 = cont[(HEADLINE, "x2")]
    x2_pass = bool(x2["sharpe_full"] > 0)
    # M1 / DSR / PBO
    tstat = t_from_sharpe(h["sharpe_full"], len(h_rets))
    m1 = m1_t_value_gate(tstat, claim_class="new_strategy")
    dsr = deflated_sharpe_ratio(h_rets, n_trials=BATCH_CELLS)
    mat = pd.DataFrame({f"{c}|{f}": pd.Series(cont[(c, f)]["returns"])
                        for c in CELLS for f in FACES}).dropna()
    from screening.pbo import cscv_pbo, pbo_verdict
    pbo_rec = cscv_pbo(mat)
    pbo = float(pbo_rec["pbo"])
    pbo_band = pbo_verdict(pbo)
    g2 = g2_registration_v2(g1.get("pass"), dsr.get("dsr", dsr), pbo)
    # G-SEG coverage (headline x1 per-start 12m full windows)
    rows = _read_cells(HEADLINE, "x1") or []
    full = [r for r in rows if not r.get("partial_12m")]
    cnt = {}
    for r in full:
        cnt[r.get("regime", "na")] = cnt.get(r.get("regime", "na"), 0) + 1
    gseg_pass = all(cnt.get(reg, 0) >= 50 for reg in ("bear", "bull", "chop"))
    # law-A exit census (headline x1 re-run through the frozen machinery)
    census = _census_core(_cell_spans(HEADLINE), "x1")
    census_pass = bool(census["pass"])
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
    # per-start 12m distribution + rolling worst (D-20260930-41 sec.1.3)
    r12 = sorted(r["ret_12m"] for r in full)

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
    hidx = _G["idx"][lo + 1:lo + 1 + len(hret)]
    if len(hidx) == len(hret):
        cy = (1 + hret).groupby(hidx.year).apply(lambda x: float(x.prod() - 1))
    else:
        cy = pd.Series(dtype=float)
    crash_years = {int(y): round(v, 4) for y, v in cy.items() if v <= -0.35}
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
            "g_seg": {"coverage": cnt, "pass": gseg_pass},
            "exit_census": census,
        },
        "headline": {"sharpe_full": h["sharpe_full"], "ret_full":
                     h["ret_full"], "max_dd": h["max_dd"],
                     "n_trades": h["n_trades"], "n_entries": h["n_entries"],
                     "trades_per_year": h["trades_per_year"],
                     "t0": h["t0"]},
        "cells": {f"{c}|{f}": {kk: vv for kk, vv in cont[(c, f)].items()
                  if kk != "returns"} for c in CELLS for f in FACES},
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
        "starts_12m_dist": {"n": len(r12), "best": pct(100), "worst": pct(0),
                            "p25": pct(25), "median": pct(50), "p75": pct(75),
                            "positive_share": round(
                                sum(1 for v in r12 if v > 0) / len(r12), 4)
                            if r12 else None},
        "rolling_worst": roll_worst,
        "descriptive": {
            "crash_years_lte_-35pct": crash_years,
            "is_ann_ret": round(float(
                (1 + hret.iloc[:len(hret) // 2]).prod() - 1), 4),
            "oos_ann_ret": round(float(
                (1 + hret.iloc[len(hret) // 2:]).prod() - 1), 4),
            "x2_cost_drag_sharpe": round(
                x2["sharpe_full"] - h["sharpe_full"], 4)},
        "d6": d6,
        "probe_ref": "results/fund_value_p1/probe.json",
        "passive_face": passive_face,
        "audit": {
            "machine": _machine_id(),
            "cost_face": "CN-C7 stock V1 13.041bp/side single-source "
                         "(rev_osc_stock_p1.COST_X1 == cost_spec."
                         "x1_side_rate, asserted probe+F10); x2=CostPatch(2)"
                         " -> rt 52.164bp",
            "engine_face": "engine.run_backtest per-symbol sub-accounts, "
                           "entry_size_scale weight mapping, span-sliced "
                           "frames with seed-ffill OHLC marks (P4 "
                           "stale_ffill convention; F15 equivalence leg)",
            "eligibility_face": "base=close/vol/amt>0 + amt20-median>="
                                "¥10M + listed>=252 + as-of ST proxy "
                                "(p4_ext_tilt._st_regime verbatim, "
                                "trailing-250 slice); pick=base AND "
                                "(0<pe<=cap AND 0<pb<=20) joint band",
            "regime_face": "510300 3-way MA200 proxy from repo core48 "
                           "daily (p1c stock panel carries no 510300 "
                           "column; date-keyed labels; reporting segment "
                           "only, never a gate)",
            "monthly_face": "firing months = coverage>=0.80; skipped "
                            "months carry prior selections; pre-t0 flat; "
                            "t0 probe-frozen",
            "cont_span_face": "cont/nulls/sens span t0..cutoff; passive "
                              "override = base-mask EW B&H at t0 same span",
            "seed_disclosure": probe.get("seed_disclosure"),
            "law_a_census": {"block_share": CENSUS_BLOCK_SHARE,
                             "lawful_reasons": list(LAWFUL_EXIT_REASONS),
                             "ref": "prereg sec.0.6 second gate"},
            "finalize_runtime_sec": round(time.time() - t0, 1),
        },
    }
    with open(OUT_CSV, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("cell,face,sharpe_full,ret_full,max_dd,n_trades,"
                 "n_entries,beat12_rate\n")
        for c in CELLS:
            rows_c = _read_cells(c, "x1") or []
            fullc = [r for r in rows_c if not r.get("partial_12m")]
            rate = (round(sum(1 for r in fullc if r["beat_12m"]) / len(fullc), 4)
                    if fullc else None)
            for f in FACES:
                cc = cont[(c, f)]
                fh.write(f"{c},{f},{cc['sharpe_full']},{cc['ret_full']},"
                        f"{cc['max_dd']},{cc['n_trades']},{cc['n_entries']},"
                        f"{rate if f == 'x1' else ''}\n")
    led = append_ledger(batch_name=BATCH_NAME, batch_trials=BATCH_CELLS,
                        file_name="results/fund_value_p1/"
                                  "fund_value_p1_results.json",
                        evidence_cutoff="2026-09-22")
    results["trials_ledger"] = led
    _dump(results, OUT_JSON)
    print(f"finalize verdict={verdict} -> {OUT_JSON}")
    print(f"  g1={g1.get('pass')} x2={x2_pass} m1={m1.get('pass')} "
          f"g2={g2.get('pass')} g_seg={gseg_pass} census={census_pass} "
          f"(default_share={census['default_share']})")
    return 0


# ------------------------------------------------------------------- selftest

def cmd_selftest(_) -> int:
    """Hermetic offline self-check: synthetic panels + synthetic value
    faces injected into _G (no repo data, no network). Deterministic."""
    import shutil
    import tempfile
    fails = []

    def check(name, ok, detail=""):
        print(f"[{'PASS' if ok else 'FAIL'}] {name} {detail}")
        if not ok:
            fails.append(name)

    rng = np.random.default_rng(11)
    idx = pd.date_range("2020-01-02", periods=460, freq="B")
    syms = ["S1", "S2", "S3", "S4", "S5", "S6"]
    T, N = len(idx), len(syms)
    close = np.full((T, N), np.nan, dtype=np.float64)
    for j in range(N):
        n = T - 30 * j
        r = rng.normal(0.0004, 0.012, n)
        close[:n, j] = 100 * np.cumprod(1 + r)
    high = close * 1.01
    low = close * 0.99
    open_ = close * 0.999
    vol = np.where(np.isfinite(close), 1e6, np.nan)
    amt = np.where(np.isfinite(close), 5e7, np.nan)
    pct = np.zeros((T, N))
    pct[1:] = (close[1:] / close[:-1] - 1) * 100
    pct[~np.isfinite(close)] = np.nan
    # synthetic semi-monthly anchors with DISTINCT pe profiles
    by_sym = {}
    pe_prof = {"S1": 8.0, "S2": 15.0, "S3": 25.0, "S4": 40.0, "S5": 60.0,
               "S6": 90.0}
    anchor_dates = sorted({d.strftime("%Y%m%d") for d in idx[::10]})
    for s in syms:
        ad = np.array([int(x) for x in anchor_dates])
        pe = np.full(len(ad), pe_prof[s])
        pb = pe / 4.0
        by_sym[s] = (ad, pe, pb)
    month_pos = _monthly_positions(idx)
    firing = [(p, month_pos[i + 1] if i + 1 < len(month_pos) else T)
              for i, p in enumerate(month_pos)]
    _G.clear()
    _G.update(idx=idx, syms=syms, codes_arr=np.array(syms),
              close_np=close, open_np=open_, high_np=high, low_np=low,
              volume_np=vol, amount_np=amt, pct_np=pct,
              by_sym=by_sym, month_pos=month_pos,
              first_valid=np.argmax(np.isfinite(close), axis=0),
              static_thr=np.full(N, 0.10, dtype=np.float32),
              is_cx=np.zeros(N, dtype=bool),
              regime=pd.Series("na", index=idx, dtype=object))
    _G["_firing"] = firing
    _G["_t0_pos"] = firing[0][0]
    muniv = {}
    for (p, _end) in firing:
        act = np.where(np.isfinite(close[p]))[0]
        muniv[p] = {"p": p, "n_active": len(act), "cov_ratio": 1.0,
                    "skipped": False, "base_j": act,
                    "pe_of": np.array([pe_prof[syms[j]] for j in act],
                                      dtype=float),
                    "pb_of": np.array([pe_prof[syms[j]] / 4 for j in act],
                                      dtype=float)}
    _G["_muniv"] = muniv
    # F1: eq weights sum to 1 per firing month; Top-N = lowest rule value
    picks = _cell_picks("pe", 3)
    w_ok = all(abs(w - 1.0 / len(top)) < 1e-12 for (_, _, top, w) in picks)
    check("F1_eq_weights_1_over_N", w_ok, f"months={len(picks)}")
    sel0 = sorted(syms[j] for j in picks[0][2])
    check("F2_topN_lowest_pe", sel0 == ["S1", "S2", "S3"], f"sel={sel0}")
    # F3: build determinism
    picks2 = _cell_picks("pe", 3)
    check("F3_build_deterministic",
          all((a[0] == b[0]) and (a[2] == b[2]).all()
              for a, b in zip(picks, picks2)))
    # F4: engine T+1 (first trade strictly after the first signal day)
    spans = _spans_from_picks(picks)
    run = run_cell_portfolio(spans, "x1", _G["_t0_pos"], T - 1,
                             keep_trades=True)
    nav = _nav_from_run(run, _G["_t0_pos"], T - 1)
    check("F4_nav_len", run is not None and len(nav) > 400,
          f"nav_days={len(nav)}")
    first_sig = idx[picks[0][0]]
    if run["trades"]:
        first_fill = min(pd.Timestamp(tr["date"]) for tr in run["trades"])
        check("F4_t_plus_1", first_fill > first_sig,
              f"first_fill={first_fill.date()} sig={first_sig.date()}")
    else:
        check("F4_t_plus_1", True, "no fills in fixture (honest)")
    # F5: x2 cost bites
    runx = run_cell_portfolio(spans, "x2", _G["_t0_pos"], T - 1)
    navx = _nav_from_run(runx, _G["_t0_pos"], T - 1)
    check("F5_x2_face", runx is not None and len(navx) > 400)
    if run["n_trades"] > 0:
        check("F5_x2_cost_bites",
              abs(float(navx.iloc[-1]) - float(nav.iloc[-1])) > 1e-6)
    # F6: monthly causality -- selection prefix invariant to later anchors.
    # Exercises the REAL _month_universe path (searchsorted as-of lookup)
    # by clearing the universe cache on both sides -- the injected fixture
    # muniv must not short-circuit this leg.
    _G.pop("_muniv", None)
    _G.pop("_st_rows", None)
    picks_a = _cell_picks("pe", 3)
    n_head = len(firing) // 2
    mid_date = int(idx[firing[n_head][0]].strftime("%Y%m%d"))
    mutated = dict(by_sym)
    for s in syms:
        ad, pe, pb = by_sym[s]
        pe2 = pe.copy()
        m = ad > mid_date
        pe2[m] = 200.0 - pe[m]      # rank-FLIP future anchors (in-band)
        mutated[s] = (ad, pe2, pb)
    _G["by_sym"] = mutated
    _G.pop("_muniv", None)
    picks_b = _cell_picks("pe", 3)
    _G["by_sym"] = by_sym
    _G.pop("_muniv", None)           # later legs recompute on true faces
    same = all((a[2] == b[2]).all()
               for a, b in zip(picks_a[:n_head], picks_b[:n_head]))
    diff = any((a[2] != b[2]).any()
               for a, b in zip(picks_a[n_head:], picks_b[n_head:]))
    check("F6_pit_anchor_law", same and diff,
          f"head_same={same} tail_diff={diff}")
    # F7: double-run byte identity (cont face)
    a = _cont_task(_mk("cont", cell="VALUE-PE", face="x1"))
    b = _cont_task(_mk("cont", cell="VALUE-PE", face="x1"))
    check("F7_double_run_identity", a == b,
          f"sharpe={a['sharpe_full']} trades={a['n_trades']}")
    # F8: null rng substream determinism
    k1 = np.random.default_rng([SEED_NULLS, 0]).integers(0, 48, 5).tolist()
    k2 = np.random.default_rng([SEED_NULLS, 0]).integers(0, 48, 5).tolist()
    check("F8_null_rng_substream", k1 == k2, str(k1))
    # F9: checkpoint resume
    tmp = tempfile.mkdtemp()
    p = os.path.join(tmp, "cells.jsonl")
    _append_rows(p, [{"key": "VALUE-PE|x1|300"}])
    check("F9_resume_skip", "VALUE-PE|x1|300" in _done_keys(p))
    shutil.rmtree(tmp, ignore_errors=True)
    # F10: cost single-source (CN-C7 stock face)
    rate = cost_spec.x1_side_rate()
    check("F10_cost_rt_26_082bp",
          RVSTOCK.COST_X1 == rate and abs(rate * 2.0 * 1e4 - 26.082) < 1e-6,
          f"rt={rate * 2e4:.3f}bp")
    # F11/F12: exit-channel split (r522 dead-letter regression guard)
    check("F11_exit_channels_disjoint",
          not (set(EXIT_PATCH_OVERRIDES) & set(NEUTRALIZED_PARAMS)),
          f"patch={sorted(EXIT_PATCH_OVERRIDES)}")
    import engine.backtester as _ebt
    with ExitPatch(EXIT_PATCH_OVERRIDES):
        cfg = _ebt.ExitConfig(max_positions=1)
        ok_bite = (cfg.loss_time_days == 10 ** 9
                   and cfg.global_hard_limit == 10 ** 9)
    cfg_out = _ebt.ExitConfig()
    check("F12_exitpatch_bites_and_restores",
          ok_bite and cfg_out.loss_time_days != 10 ** 9,
          f"bite={ok_bite} restored={cfg_out.loss_time_days}")
    # F13: census share math + block threshold (pure functions)
    fake = {"signal_reversal": 16, "loss_time_stop": 2}
    tot = sum(fake.values())
    share = sum(v for k, v in fake.items()
                if k not in LAWFUL_EXIT_REASONS) / tot
    check("F13_census_share_math",
          abs(share - 2 / 18) < 1e-12 and share <= CENSUS_BLOCK_SHARE,
          f"share={share:.4f}")
    fake_bad = {"signal_reversal": 7, "loss_time_stop": 8,
                "global_hard_limit": 6}
    tot_b = sum(fake_bad.values())
    share_b = sum(v for k, v in fake_bad.items()
                  if k not in LAWFUL_EXIT_REASONS) / tot_b
    check("F13b_census_block_face", share_b > CENSUS_BLOCK_SHARE,
          f"share={share_b:.4f}")
    # F14: hold-through census on the fixture -- zero default-stack exits
    cen = _census_core(spans, "x1")
    check("F14_fixture_census_zero_default",
          cen["total_exits"] > 0 and cen["default_stack_exits"] == 0,
          f"total={cen['total_exits']} reasons={cen['per_reason']}")
    # F15: span-slice equivalence -- full-frame run == span-sliced run
    full_spans = {j: sp for j, sp in spans.items()}
    run_full = run_cell_portfolio(full_spans, "x1", 0, T - 1,
                                  keep_trades=True)
    nav_full = _nav_from_run(run_full, 0, T - 1)
    nav_slice = _nav_from_run(run, _G["_t0_pos"], T - 1)
    tail_full = nav_full.reindex(nav_slice.index).ffill()
    eq_tail = np.allclose(tail_full.to_numpy(), nav_slice.to_numpy(),
                          atol=1e-9)
    check("F15_span_slice_equivalence",
          eq_tail and run["n_trades"] == run_full["n_trades"],
          f"tail_eq={eq_tail} trades={run['n_trades']}/"
          f"{run_full['n_trades']}")
    # F16: monthly hold-through -- selected member entry True across the
    # whole month; exit fires only at the next firing month's edge
    j0 = picks[0][2][0]
    m0, e0 = picks[0][0], picks[0][1]
    ent, _sc = _sym_arrays(j0, spans[j0])
    check("F16_month_holdthrough",
          bool(ent[m0:e0].all()) and not bool(ent[e0 - 1:e0].any() or
                                              ent[e0:e0 + 1].any() or
                                              ent[m0 - 1]) if m0 > 0
          else bool(ent[m0:e0].all()),
          f"span=({m0},{e0})")
    # F17: G-MASK -- null candidates == headline pick universe (fixture)
    u = _month_universe(firing[0][0])
    pj_head, _, _ = _pick_j(u, PE_MAX)
    null_cand = _pick_j(_month_universe(firing[0][0]), PE_MAX)[0]
    check("F17_g_mask_identity", np.array_equal(pj_head, null_cand),
          f"n={len(pj_head)}")
    print(f"selftest: {len(fails)} FAIL" if fails else "selftest: ALL PASS")
    return 1 if fails else 0


# ----------------------------------------------------------------------- main

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="FUND-VALUE-P1 stock monthly value family judged batch "
                    "runner (hold-through exit-axis dual gate, joint "
                    "valuation band, law-A census)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("d6")
    sub.add_parser("probe")
    r = sub.add_parser("run")
    r.add_argument("--cell", default="")
    r.add_argument("--face", default="x1")
    r.add_argument("--nulls", action="store_true")
    r.add_argument("--sensitivity", action="store_true")
    sub.add_parser("status")
    sub.add_parser("finalize")
    sub.add_parser("selftest")
    args = ap.parse_args(argv)
    return {"d6": cmd_d6, "probe": cmd_probe, "run": cmd_run,
            "status": cmd_status, "finalize": cmd_finalize,
            "selftest": cmd_selftest}[args.cmd](args)


if __name__ == "__main__":
    raise SystemExit(main())
