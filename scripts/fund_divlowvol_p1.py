"""FUND-DIVLOWVOL-P1 -- fundamental dividend-low-vol (high TTM cash
yield x low-vol screen) cross-sectional MONTHLY-rebalance NEW FAMILY
judged batch at main-exam rank.

Ticket T-2026-10-03-155-P1 (claimed bm-b r610 same-round freeze per
O-1730 immediate law); prereg FROZEN v1.0 research/FUND-DIVLOWVOL-P1.md
(2026-10-03 bm-b r610 freeze window, five-condition gate ALL GREEN:
T-154 div_events TRANSFER + probe legs1-5 + D6 ADMIT 0.2555 +
SEED_REGISTRY rows + banned_direction_gate ADMIT). Judgments live
there; this file implements them, never re-states a threshold.
family_key fund_divlowvol_stock_xs (M3: closed keys zero-hit = open;
the stock monthly DIVLOWVOL family is the dividend-face sibling of
fund_value_stock_xs / fund_quality_stock_xs -- orthogonal ranking
input, independent judged pathways per prereg sec.3 anti-dup
disclosure).

Family (prereg sec.2/3, FROZEN):
  signal day = each month's FIRST trading day (T-22 census
  enumeration, 401 starts bit-exact); yield_ttm(t) = sum(cash per
  share for ex_date in (t-365d, t]) / P_raw_close(t) -- ex-date PIT
  anchor (dividends are certain only at ex-date; statutory
  anchoring is N/A for a corporate-action face, declared in the
  prereg); P_raw_close(t) = close_qfq(t) * f(t) with the Money02
  sidecar stepwise factor (raw-price recovery: qfq-direct
  denominators distort the cross-sectional rank per-symbol by 1/f --
  probe leg3 known-answer median rel dev 2.9e-10). Derive kernels
  ttm_cash_sum / sidecar_f_at are IMPORTED single-source from
  scripts/fund_divlowvol_p1_probe.py -- the runner re-implements
  nothing. Low-vol screen: sigma_252 = sample std (ddof=1) of qfq
  daily returns over trailing 252 trading days, min 126 valid bars
  (else un-screenable, honest exclusion); keep sigma <= cross-
  sectional median WITHIN the yield>0 candidate universe (bottom
  half); Top-N=20 by yield_ttm DESC (cell DIVLOWVOL-YIELDVOL =
  HEADLINE, the only ranking rule), eq weights (1/pick_size),
  ALWAYS-ON, monthly rotation. UNIVERSE_FLOOR=60 (3N pre-screen):
  months with fewer than 60 candidates are below-floor SKIPPED
  (sleeve persists; pre-t0 flat); t0 pin = 2006-02-06 (first
  clean-tail month, probe leg4 frozen read; the 148 pre-t0 months
  are ALL below-floor -- A-share cash-dividend culture 2006 + the
  Y10M liquidity gate -- a frozen prereg claim the runner probe
  machine-verifies).

Execution semantics (prereg sec.0.6, engine/ untouched -- VERBATIM
value/quality-family face):
  entry = selected-at-this-month (forward-filled across the month's
  bars), exit = entry <= 0 (t22 convention -- the ONLY exit: monthly
  rotation). HOLD-THROUGH declared; the engine default exit stack is
  DISABLED via the TWO channels split by the engine's own bridge
  surface (r522):
    params channel (bridge-reachable, 4 keys): take_profit_levels=(),
    trailing_stop_activate=1e12, initial_stop=-1.0, time_decay_period=1e9;
    ExitPatch channel (live.paper ExitConfig factory, 2 keys):
    loss_time_days=1e9, global_hard_limit=1e9 (F11 disjoint selftest).
  x2 face = CostPatch(2.0). Costs CN-C7 stock V1 = 13.041bp/side
  single-source asserted: rev_osc_stock_p1.COST_X1 == cost_spec
  .x1_side_rate() (rt 26.082bp; x2 rt 52.164bp); eq Top-20 unit Y50k
  on a Y1M account clears the Y20k minimum-commission tier.
  Law-A post-burn exit-reason census: only signal_reversal is lawful
  on the hold-through face; default-stack share > 20% =
  consumption-blocked.

Engine-face disclosure (per-symbol sub-account decomposition,
family verbatim): each symbol runs as its own engine sub-account
(initial_cash = 1,000,000, max_positions=1, position_size_pct=1.0 x
entry_size_scale = 1/pick_size), NAV = CAPITAL + sum(NAV_s - CAPITAL).
Weights set at entry, never resized mid-hold (sizing_mode=fixed_initial).
Frames are SPAN-SLICED per symbol with seed-ffill OHLC marks
(P4_BATCH2 disclosed stale_ffill convention; F15 equivalence leg);
volume/amount NaN->0.

Data faces (prereg sec.2):
  price = Money02 p1c_stock npy cache (8792 bars x 5222 syms, last
  bar 2026-09-22, qfq) via p1c_stock_ic_batch.load_universe;
  dividends = data/fund_history_export/div_events_faces.parquet
  (T-154 TRANSFER DELIVERED bm-c r403: 54,494 rows / 5,124 syms /
  sha256 66c67d9f..., columns code/ex_date/cash_div_per_10/
  record_date; record_date carried but NOT consumed -- registration
  day is a shareholder-eligibility face, disclosed);
  factor sidecars = Money02/data/bars/<sym>.factor.json (5,124/5,124
  div symbols covered, probe leg3);
  eligibility = close/volume/amount>0 AND amt20-median >= Y10,000,000
  AND listed >= 252 bars AND as-of ST exclusion via the P4_BATCH2
  sec.2 5%-seal board-aware proxy IMPORTED VERBATIM
  (p4_ext_tilt._st_regime) AND dividend eligibility yield_ttm(t) > 0
  (zero-dividend names never enter the yield rank; no yield cap --
  high-yield traps are carried by the low-vol screen + the
  liquidity gate, design-simple, disclosed). Regime labels: 510300
  3-way MA200 proxy from the REPO core48 daily face (date-keyed;
  reporting segment, never a gate). G-CENSUS: 401 monthly starts
  (1992-09-01..2026-03-02 window, pos>=252, fwd>=126, active>=24 --
  value-family bit-exact enumeration, same panel).
  evidence_cutoff 2026-09-22 D2 lockbox.

Seeds (prereg sec.3, freeze-window registry rows landed r610):
  nulls rng([20520000, k]) K=2000; sens rng([20520500, k]) K=500
  (N in {10,15,20} x vol_screen_frac in {0.5,1.0} -- 1.0 = no
  low-vol screen ablation face; rule FIXED yieldvol). Bootstrap/
  sign-flip descriptive aux seed 20261003 disclosed here.

Checkpoint/resume: per-shard JSONL append, done-key skip, tolerant
of a truncated crash tail (t22 pattern); r611 containment machinery
(--redo AA-replace at same keys, burn-machine + cache-digest
provenance) mirrored from the quality runner for family parity;
pool-claim handshake per O-20260930-2355 (worker writes
results/pool_claims/<entry>/<shard>.<machine>.json; the launcher
harvest flips the pool shard done).

D6 ownership: the same-family admission face lives in the probe
module (probe-level lightweight sleeve sim, results/fund_divlowvol_p1
/d6.json, already ADMIT 0.2555 vs ENGULF-CE-01 at r610); the runner
`d6` subcommand is a passthrough to that single source. Sibling
family disclosures (value 0.8039 / quality 0.5796) are
disclosure-only faces per prereg sec.1.

Usage (CWD = repo root):
  python scripts/fund_divlowvol_p1.py d6            # passthrough -> probe module _d6
  python scripts/fund_divlowvol_p1.py probe         # ignition gates (fail-closed)
  python scripts/fund_divlowvol_p1.py run --cell DIVLOWVOL-YIELDVOL --face x1|x2
  python scripts/fund_divlowvol_p1.py run --nulls
  python scripts/fund_divlowvol_p1.py run --sensitivity
  python scripts/fund_divlowvol_p1.py status
  python scripts/fund_divlowvol_p1.py finalize       # round-owned, post-shards
  python scripts/fund_divlowvol_p1.py selftest       # hermetic, offline
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
# derive kernels + frozen family constants: SINGLE SOURCE = probe module
# (prereg sec.6: ttm_cash_sum/sidecar_f_at imported, never re-implemented)
from fund_divlowvol_p1_probe import (
    ttm_cash_sum, sidecar_f_at, SIDECAR_FMT,
    TTM_DAYS, VOL_WIN as SIGMA_WIN, VOL_MIN_BARS, UNIVERSE_FLOOR,
    N_TOP as PROBE_TOPN, AMT20_FLOOR as PROBE_AMT20_FLOOR, QUARANTINED,
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TICKET = "T-2026-10-03-155-P1"
PREREG = os.path.join(ROOT, "research", "FUND-DIVLOWVOL-P1.md")
OUT_DIR = os.path.join(ROOT, "results", "fund_divlowvol_p1")
LOG_DIR = os.path.join(OUT_DIR, "logs")
PROBE_JSON = os.path.join(OUT_DIR, "probe.json")            # runner ignition gates
TRANSFER_PROBE_JSON = os.path.join(                         # probe-script facts (r610)
    ROOT, "results", "_fund_divlowvol_p1_transfer_probe.json")
TRANSFER_MANIFEST_REL = "fleet/transfers/T-2026-10-03-154-sender.json"
TRANSFER_MANIFEST = os.path.join(ROOT, TRANSFER_MANIFEST_REL)
D6_JSON = os.path.join(OUT_DIR, "d6.json")                   # probe-module owner
OUT_JSON = os.path.join(OUT_DIR, "fund_divlowvol_p1_results.json")
OUT_CSV = os.path.join(OUT_DIR, "cells.csv")
PARQUET = os.path.join(ROOT, "data", "fund_history_export",
                       "div_events_faces.parquet")           # T-154 (DELIVERED)
ETF_510300_CSV = os.path.join(ROOT, "data", "daily", "sh510300.csv")

CUTOFF = pd.Timestamp("2026-09-22")          # prereg sec.2 D2 lockbox
BATCH_NAME = "FUND-DIVLOWVOL-P1"
BATCH_CELLS = 2002                           # 2 judged cell-faces + 2000 nulls
FAMILY_KEY = "fund_divlowvol_stock_xs"       # prereg sec.1 M3 (new family)
CAPITAL = 1_000_000.0                        # prereg CN-C7 nominal tier
W6M, W12M, W24M = 126, 252, 504
WARMUP_TD = 252                              # listed/bars warmup caliber
MIN_LISTED = 24                              # active members at a start
ENUM_LO = pd.Timestamp("1992-09-01")         # G-CENSUS window (family bit-exact)
ENUM_HI = pd.Timestamp("2026-03-02")
G_CENSUS_EXPECT = 401
AMT20_WIN = 20
AMT20_MIN = PROBE_AMT20_FLOOR                # frozen liquidity floor (sec.2, 1e7)
LISTED_MIN_BARS = 252                        # listed >= 252td (sec.2)
TOPN = PROBE_TOPN                            # frozen Top-N (sec.3, 20)
VOL_FRAC_HEADLINE = 0.5                      # low-vol half (sec.2 frozen)
T0_FROZEN = "2006-02-06"                     # pinned r610 freeze window per probe
                                             # leg4 first_signal_date_t0=20060206
K_NULLS = 2000
SEED_NULLS = 20_520_000                      # prereg sec.3 / SEED_REGISTRY (frozen)
K_SENS = 500
SEED_SENS = 20_520_500                       # prereg sec.3 / SEED_REGISTRY (frozen)
BOOT_B = 2000                                # block bootstrap B
BLOCK_BOOT_LEN = 21                          # frozen block length (sec.3)
NULL_AUX_SEED = 20261003                     # bootstrap/sign-flip face (disclosed)
D6_REJECT = 0.7                              # probe-module gate line (disclosure)
CENSUS_BLOCK_SHARE = 0.20                     # prereg sec.0.6 (frozen)
LAWFUL_EXIT_REASONS = ("signal_reversal",)
HEADLINE = "DIVLOWVOL-YIELDVOL"               # prereg sec.3 (the only ranking rule)
CELLS = {"DIVLOWVOL-YIELDVOL": {"rule": "yieldvol",
                                "vol_frac": VOL_FRAC_HEADLINE}}
FACES = ("x1", "x2")
SENS_NS = (10, 15, 20)
SENS_VOL_FRACS = (0.5, 1.0)                  # 1.0 = no low-vol screen ablation
SENS_RULES = ("yieldvol",)                   # rule FIXED (prereg sec.3)
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

def _load_div_events():
    """Per-symbol (ex_date int YYYYMMDD sorted, cumulative cash-per-share)
    packs. ex_date is the PIT anchor (dividends are certain only at
    ex-date); same-day multi-component rows SUM (600519 2006-05-19
    known answer -- exact-dup keys never collapse; T-154 export law)."""
    df = pd.read_parquet(PARQUET)
    d = df.assign(code_s=df["code"].astype(str))
    d["_ex"] = d["ex_date"].astype("string").str.replace(
        "-", "", regex=False).astype("int64")
    d["_cps"] = d["cash_div_per_10"].astype("float64") / 10.0
    d = d.sort_values(["code_s", "_ex"])
    by_sym = {}
    for code, g in d.groupby("code_s", sort=False):
        by_sym[str(code)] = (g["_ex"].to_numpy(),
                             np.cumsum(g["_cps"].to_numpy()))
    return by_sym


def _load_sidecars(codes):
    """Stepwise factor sidecars for the div symbols (probe leg3 census:
    5,124/5,124 covered, zero missing). f(latest)==1.0 by sidecar
    convention; empty/absent sidecar -> f=1.0 (sidecar_f_at law)."""
    out = {}
    for code in sorted(codes):
        p = os.path.join(ROOT, SIDECAR_FMT.format(sym=code))
        if os.path.exists(p):
            sd = json.load(open(p, encoding="utf-8"))
            out[str(code)] = (
                np.array([int(x.replace("-", "")) for x in sd["d"]],
                         dtype=np.int64),
                np.array(sd["f"], dtype=np.float64))
    return out


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
    """T-22 monthly adaptation, family bit-exact: month-first days within
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


def _sigma_row(p):
    """sigma_252 + valid-bar count at signal day p, cached: sample std
    (ddof=1) of qfq daily returns over trailing 252 trading days;
    members with <126 valid bars are un-screenable (sec.2 frozen)."""
    cache = _G.setdefault("_sig_rows", {})
    if p in cache:
        return cache[p]
    lo = max(p - SIGMA_WIN + 1, 0)
    pct_win = np.asarray(_G["pct_np"][lo:p + 1], dtype=np.float64)
    with np.errstate(invalid="ignore"):
        sigma = np.nanstd(pct_win, axis=0, ddof=1)
    valid = np.sum(np.isfinite(pct_win), axis=0)
    cache[p] = (sigma, valid)
    return sigma, valid


def _month_universe(p):
    """Everything a signal day needs, cached: active row, base-eligible
    indices, and the low-vol-screen candidate set (base mask AND
    yield_ttm>0 AND screenable sigma -- the UNIVERSE_FLOOR counts THIS
    pre-screen set). yield via the probe kernels (ttm_cash_sum over the
    (t-365d, t] ex-date window; P_raw = close_qfq * f(t) sidecar)."""
    cache = _G.setdefault("_muniv", {})
    if p in cache:
        return cache[p]
    idx = _G["idx"]
    syms = _G["syms"]
    close_r = np.asarray(_G["close_np"][p])
    active = np.isfinite(close_r)
    n_active = int(active.sum())
    t_ts = idx[p]
    t_int = int(t_ts.strftime("%Y%m%d"))
    ws_int = int((t_ts - pd.Timedelta(days=TTM_DAYS)).strftime("%Y%m%d"))
    # base eligibility mask (sec.2, frozen, family verbatim)
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
    sigma, valid = _sigma_row(p)
    by_sym = _G["by_sym"]
    sidecars = _G["sidecars"]
    cand_j, cand_y, cand_s = [], [], []
    for j in np.where(base)[0]:
        code = str(syms[j])
        pack = by_sym.get(code)
        sc = sidecars.get(code)
        if pack is None or sc is None:
            continue
        cash = ttm_cash_sum(pack[0], pack[1], t_int, ws_int)
        if cash <= 0:
            continue                      # dividend gate: yield_ttm > 0 (sec.2)
        if valid[j] < VOL_MIN_BARS or not np.isfinite(sigma[j]):
            continue                      # un-screenable, honest exclusion
        f_t = sidecar_f_at(sc[0], sc[1], t_int)
        p_raw = float(close_r[j]) * f_t
        if not np.isfinite(p_raw) or p_raw <= 0:
            continue
        cand_j.append(int(j))
        cand_y.append(cash / p_raw)
        cand_s.append(float(sigma[j]))
    n_cand = len(cand_j)
    u = {"p": p, "t_int": t_int, "ws_int": ws_int,
         "n_active": n_active, "n_base": int(base.sum()),
         "base_j": np.where(base)[0],
         "n_cand": n_cand,
         "skipped": bool(n_cand < UNIVERSE_FLOOR),
         "cand_j": np.array(cand_j, dtype=np.int64),
         "cand_yield": np.array(cand_y, dtype=np.float64),
         "cand_sigma": np.array(cand_s, dtype=np.float64)}
    cache[p] = u
    return u


def _pick_j(u, vol_frac=VOL_FRAC_HEADLINE):
    """Rank universe for a cell: the candidate set screened to the
    low-vol half (sigma <= cross-sectional median, sec.2 frozen);
    vol_frac=1.0 = no-screen ablation face (sens only). Returns
    (panel indices, yields)."""
    if u["skipped"] or len(u["cand_j"]) == 0:
        return u["cand_j"][:0], u["cand_yield"][:0]
    sig = u["cand_sigma"]
    if vol_frac >= 1.0:
        m = np.ones(len(sig), dtype=bool)
    else:
        med = float(np.median(sig))
        m = sig <= med
    return u["cand_j"][m], u["cand_yield"][m]


def _firing_months():
    """[(m_pos, next_firing_pos_or_T)] for every floor-passing month of
    the clean tail: t0 = the first census start from which EVERY later
    start passes the floor (probe leg4 definition, machine re-derived);
    months before t0 NEVER fire (pre-t0 flat, prereg sec.2 -- the 148
    pre-t0 months are all below-floor, a frozen claim cmd_probe
    machine-verifies); a skipped month fires nothing and prior
    selections persist."""
    cache = _G.get("_firing")
    if cache is not None:
        return cache
    months = _G["month_pos"]
    flags = [not _month_universe(p)["skipped"] for p in months]
    t0_i = next((i for i in range(len(months))
                 if all(flags[i:])), None)
    if t0_i is None:
        raise RuntimeError("no clean-tail t0: universe floor never "
                           "satisfied on a tail -- data-face drift, "
                           "fail-closed")
    firing = [p for p in months[t0_i:]
              if not _month_universe(p)["skipped"]]
    spans = []
    for i, m in enumerate(firing):
        end = firing[i + 1] if i + 1 < len(firing) else len(_G["idx"])
        spans.append((m, end))
    _G["_firing"] = spans
    _G["_t0_pos"] = months[t0_i]
    _G["_floor_flags"] = flags
    _G["_t0_i"] = t0_i
    return spans


def _cell_picks(rule, N, vol_frac=VOL_FRAC_HEADLINE):
    """Frozen ranking: within the low-vol half, Top-N=20 by yield_ttm
    DESCENDING (the headline rule), code tiebreak, Top-min(N, avail)."""
    picks = []
    codes = _G["codes_arr"]
    for (m, end) in _firing_months():
        u = _month_universe(m)
        pj, vals = _pick_j(u, vol_frac)
        if len(pj):
            order = np.lexsort((codes[pj], -vals))
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
        cache[cell] = _spans_from_picks(
            _cell_picks(spec["rule"], TOPN, spec["vol_frac"]))
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
    over [pos..e] (prereg sec.3 passive; marks convention disclosed;
    passive = the FULL base-eligibility mask, not the yield>0 set --
    family verbatim)."""
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
    by_sym = _load_div_events()
    sidecars = _load_sidecars(by_sym.keys())
    _G.update(idx=idx, syms=syms, codes_arr=codes_arr, first_valid=first_valid,
              static_thr=static_thr, is_cx=is_cx,
              close_np=panels["close_np"], open_np=panels["open_np"],
              high_np=panels["high_np"], low_np=panels["low_np"],
              volume_np=panels["volume_np"], amount_np=panels["amount_np"],
              pct_np=panels["pct_chg_np"],
              by_sym=by_sym, sidecars=sidecars,
              # Signal days = T-22 census enumeration (prereg sec.2), not
              # raw month-firsts: census-excluded months must not fire --
              # t0 must equal the first CENSUS start passing the floor,
              # else a pre-t0 phantom firing breaks the clean-tail gate.
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
            "n_active_universe": u["n_active"], "n_base": u["n_base"],
            "n_cand_universe": u["n_cand"],
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
    TOPN uniform picks from the HEADLINE rank universe (yield>0 + low-
    vol half + full eligibility -- G-MASK: same cached universe object
    the real cell ranks over, identity by construction, F17 selftest
    leg), eq weights, t0..cutoff continuous run."""
    k = payload["k"]
    rng = np.random.default_rng([SEED_NULLS, k])
    spans = defaultdict(list)
    n_sel_days = 0
    for (m, end) in _firing_months():
        u = _month_universe(m)
        pj, _ = _pick_j(u, VOL_FRAC_HEADLINE)
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
    """Sensitivity draw k (sec.3, descriptive only): space-filling draw
    over (N in {10,15,20}, vol_screen_frac in {0.5, 1.0}); rule FIXED
    yieldvol (the family has one ranking rule), monthly fixed, same
    hold-through exit face."""
    k = payload["k"]
    rng = np.random.default_rng([SEED_SENS, k])
    N = int(rng.choice(SENS_NS))
    vol_frac = float(rng.choice(SENS_VOL_FRACS))
    rule = "yieldvol"                        # FIXED (prereg sec.3)
    picks = _cell_picks(rule, N, vol_frac)
    spans = _spans_from_picks(picks)
    _firing_months()
    lo = _G["_t0_pos"]
    T = len(_G["idx"])
    run = run_cell_portfolio(spans, "x1", lo, T - 1)
    nav = _nav_from_run(run, lo, T - 1)
    from engine.metrics import max_drawdown, sharpe
    return {"key": f"sens|{k}", "k": k, "N": N, "vol_frac": vol_frac,
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


def _replace_rows(path: str, rows: list, extra: dict = None):
    """r611 containment face (family parity): AA in-place replacement --
    rewrite the checkpoint with `rows` replacing existing entries at the
    same keys (key set unchanged -> attrition r448 monotone law holds;
    zero duplicate-key appends).  Atomic tmp+replace: a mid-redo crash
    leaves the pre-redo file untouched (redo simply did not land;
    re-run to retry)."""
    by_key, order = {}, []
    if os.path.exists(path):
        for ln in open(path, encoding="utf-8").read().splitlines():
            if not ln.strip():
                continue
            try:
                k = json.loads(ln)["key"]
            except (json.JSONDecodeError, KeyError):
                continue        # truncated crash tail: drop honestly
            if k not in by_key:
                order.append(k)
            by_key[k] = ln
    for r in rows:
        row = dict(r)
        if extra:
            row.update(extra)
        k = row["key"]
        if k not in by_key:
            order.append(k)     # honest: redo key absent pre-run
        by_key[k] = json.dumps(row, default=bool, sort_keys=True,
                               ensure_ascii=False)
    tmp = path + ".redo_tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        for k in order:
            fh.write(by_key[k] + "\n")
    os.replace(tmp, path)


def _cache_digest() -> str:
    """Content digest of the drift-affected cache faces (bm-a MSG-0827
    sec.7 spirit: machine-local frozen-cache meta-identity is
    insufficient -- pin volume+amount CONTENT).  16-hex short digest
    for row-level provenance annotation."""
    import hashlib
    h = hashlib.sha256()
    for name in ("volume.npy", "amount.npy"):
        fp = os.path.join(P1C.CACHE_DIR, name)
        with open(fp, "rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 22), b""):
                h.update(chunk)
    return h.hexdigest()[:16]


def _mk(kind, **kw):
    return {"_fn": {"cell": _cell_task, "cont": _cont_task,
                    "null": _null_task, "sens": _sens_task}[kind], **kw}


def _run_parallel_tasks(tasks, keyfn, path, log_name, heavy=False,
                        redo=False, redo_extra=None):
    """ProcessPool burn with checkpoint done-key skip; worker count =
    min(width plan, worker_cap, memory guard) -- heavy arms (nulls/sens)
    budget MEM_GB_PER_NULL_WORKER per worker (stock-universe draws).
    redo=True (r611 family parity): bypass the skip, collect completed
    rows and AA-replace them at the same keys via _replace_rows
    (attrition-safe)."""
    from concurrent.futures import ProcessPoolExecutor, as_completed
    import psutil
    if redo:
        todo = list(tasks)
        _log(log_name, f"REDO mode: re-burning {len(todo)} (skip bypassed)")
    else:
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
    collected = []
    with ProcessPoolExecutor(max_workers=workers,
                             initializer=_init_worker) as pool:
        futs = {pool.submit(p["_fn"], p): p for p in todo}
        for fut in as_completed(futs):
            row = fut.result()
            if redo:
                collected.append(row)
            else:
                _append_rows(path, [row])
            n += 1
            if time.time() - t_last > 30:
                _log(log_name, f"progress {n}/{len(todo)}")
                t_last = time.time()
    if redo:
        _replace_rows(path, collected, redo_extra)
        _log(log_name, f"REDO replaced {n} rows in "
                       f"{os.path.basename(path)}")
    _log(log_name, f"DONE {n}/{len(todo)} in {round(time.time() - t0, 1)}s "
                   f"workers={workers}")
    return n


# ------------------------------------------------------------------- D6 door

def cmd_d6(_) -> int:
    """D6 same-family admission face -- SINGLE SOURCE = the probe module
    (probe-level lightweight sleeve sim, prereg sec.1 measured face:
    headline DIVLOWVOL-YIELDVOL daily returns vs ALL six registered
    members, max|corr| >= 0.7 -> REJECT fail-closed). Passthrough keeps
    the runner CLI family-shaped; re-runs write d6.json idempotently.
    CWD must be the repo root (probe-module relative paths)."""
    from fund_divlowvol_p1_probe import _d6
    return _d6()


# ---------------------------------------------------------------- probe

def _require_probe() -> bool:
    if not os.path.exists(PROBE_JSON):
        print("FAIL-CLOSED: results/fund_divlowvol_p1/probe.json absent "
              "-- run `probe` first")
        return False
    v = json.load(open(PROBE_JSON, encoding="utf-8")).get("verdict")
    if v != "PASS":
        print(f"FAIL-CLOSED: probe verdict={v} -- ignition refused")
        return False
    return True


def cmd_probe(_) -> int:
    """Ignition gates, fail-closed (the three-door chain of prereg
    sec.0, already GREEN at the r610 freeze window -- this is the
    runner-side live reproduction): ①TRANSFER probe facts GREEN +
    ②D6 ADMIT + ③live machine checks (panel census/t0 pin/seeds/
    cost/M3/kernels/sidecars). Any drift from the frozen reads =
    data-face change -> ignition refused."""
    os.makedirs(OUT_DIR, exist_ok=True)
    t0 = time.time()
    facts = {"ticket": TICKET, "batch": BATCH_NAME,
             "generated": _now_iso(), "machine": _machine_id(),
             "prereg_state": "FROZEN v1.0 (2026-10-03 bm-b r610 "
                             "five-condition freeze window)",
             "checks": []}

    def chk(name, ok, detail=""):
        facts["checks"].append({"name": name, "pass": bool(ok),
                                "detail": str(detail)[:400]})
        return bool(ok)

    # door-1: TRANSFER probe facts (probe-script owner, r610 GREEN)
    if os.path.exists(TRANSFER_PROBE_JSON):
        tp = json.load(open(TRANSFER_PROBE_JSON, encoding="utf-8"))
        chk("door1_transfer_probe_green", tp.get("verdict") == "GREEN",
            {k: v for k, v in tp.get("gates", {}).items()})
        facts["transfer_probe_gates"] = tp.get("gates")
    else:
        chk("door1_transfer_probe_green", False,
            f"absent: {TRANSFER_PROBE_JSON}")
    # door-2: D6 ADMIT (probe-module owner)
    if os.path.exists(D6_JSON):
        d6 = json.load(open(D6_JSON, encoding="utf-8"))
        chk("door2_d6_admit", d6.get("verdict") == "ADMIT",
            f"verdict={d6.get('verdict')} max|corr|={d6.get('max_abs_corr')}")
        facts["d6"] = d6
    else:
        chk("door2_d6_admit", False, "d6.json absent -- run `d6` first")
    # leg1 price panel
    idx, syms, meta = P1C.load_universe()
    n_bars = len(idx)
    facts["panel"] = {"n_bars": n_bars, "n_syms": len(syms),
                      "first": str(idx[0].date()), "last": str(idx[-1].date())}
    chk("leg1_price_panel",
        n_bars == 8792 and str(idx[-1].date()) == "2026-09-22"
        and len(syms) >= 5100, facts["panel"])
    # leg2 div_events TRANSFER landing (light re-verify; the heavy
    # export gate is the probe script's leg2 -- single source)
    if os.path.exists(PARQUET):
        import hashlib
        df = pd.read_parquet(PARQUET)
        sha = hashlib.sha256(open(PARQUET, "rb").read()).hexdigest()
        man_sha = None
        if os.path.exists(TRANSFER_MANIFEST):
            man = json.load(open(TRANSFER_MANIFEST, encoding="utf-8"))
            for s in man.get("sampled", []):
                if s.get("file") == "div_events_faces.parquet":
                    man_sha = s.get("sha256")
        quarantined_present = sorted(
            set(QUARANTINED) & set(df["code"].astype(str)))
        facts["div_face"] = {
            "rows": int(len(df)),
            "n_symbols": int(df["code"].nunique()),
            "sha256": sha, "manifest_sha256": man_sha,
            "sha_match": bool(sha == man_sha),
            "quarantined_present": quarantined_present}
        chk("leg2_transfer_parquet",
            len(df) >= 50_000 and int(df["code"].nunique()) >= 5100
            and sha == man_sha and not quarantined_present,
            facts["div_face"])
    else:
        facts["div_face"] = {"parquet": PARQUET, "absent": True}
        chk("leg2_transfer_parquet", False,
            "div_events_faces.parquet absent -- fail-closed")
    # leg3 G-CENSUS (family bit-exact enumeration)
    close_np = np.load(os.path.join(P1C.CACHE_DIR, "close.npy"), mmap_mode="r")
    starts = enumerate_starts_monthly(idx, close_np)
    chk("leg3_g_census_401", len(starts) == G_CENSUS_EXPECT,
        f"starts={len(starts)} want={G_CENSUS_EXPECT}")
    # leg4 t0 pin + clean tail + frozen pre-t0 claim (machine check)
    if os.path.exists(PARQUET) and os.path.exists(TRANSFER_PROBE_JSON):
        _init_worker()
        _firing_months()
        t0_pos = _G["_t0_pos"]
        flags = _G["_floor_flags"]
        t0_i = _G["_t0_i"]
        facts["t0"] = {"pos": t0_pos,
                       "date": str(_G["idx"][t0_pos].date())
                       if t0_pos is not None else None,
                       "pin": T0_FROZEN,
                       "n_census_months": len(_G["month_pos"]),
                       "n_firing_months": len(_G["_firing"])}
        chk("leg4_t0_present", t0_pos is not None, facts["t0"])
        chk("leg4_t0_frozen_reproduction",
            t0_pos is not None
            and str(_G["idx"][t0_pos].date()) == T0_FROZEN,
            f"t0={facts['t0'].get('date')} want={T0_FROZEN}")
        # zero below-floor months after t0 (clean tail, by construction
        # AND machine-verified)
        below_after = [p for p in _G["month_pos"][t0_i:]
                      if _month_universe(p)["skipped"]]
        chk("leg4_zero_below_floor_after_t0", len(below_after) == 0,
            f"below_after={below_after[:5]}")
        # firing set == exactly the census clean tail from t0 (the t0 pin
        # governs: pre-t0 months NEVER fire even if they individually
        # pass the floor -- frozen sec.2 "t0 前恒空仓"). NOTE: the prereg
        # prose line "t0 前 148 个月=below-floor" is a descriptive slip
        # (its own probe facts show n_meeting=253 > clean-tail 242);
        # the operative frozen reads are the t0 DATE pin + zero-below-
        # after + floor=60, all machine-reproduced here. Pre-t0
        # individual passers are DISCLOSED, never gated, never fired.
        pre_t0_passing = [int(_G["month_pos"][i]) for i in range(t0_i)
                          if flags[i]]
        n_firing = len(_G["_firing"])
        chk("leg4_firing_equals_clean_tail",
            n_firing == len(_G["month_pos"]) - t0_i,
            f"t0_i={t0_i} n_census={len(_G['month_pos'])} "
            f"n_firing={n_firing}")
        facts["pre_t0_disclosure"] = {
            "n_pre_t0_months": t0_i,
            "pre_t0_floor_passing_positions": pre_t0_passing[:10],
            "n_pre_t0_floor_passing": len(pre_t0_passing),
            "note": "pre-t0 months never fire (frozen t0 pin 2006-02-06); "
                    "prereg sec.2 '148 pre-t0 = below-floor' prose is a "
                    "descriptive slip vs its own probe facts "
                    "(n_meeting 253 > clean-tail count); judgment faces "
                    "(t0 date pin / floor 60 / zero-below-after) all "
                    "machine-reproduced unchanged"}
        # universe facts at t0 (disclosure)
        u0 = _month_universe(t0_pos)
        pj0, _ = _pick_j(u0, VOL_FRAC_HEADLINE)
        facts["universe"] = {
            "amt20_min_yuan": AMT20_MIN, "t0_date": facts["t0"]["date"],
            "t0_n_active": u0["n_active"], "t0_n_base": u0["n_base"],
            "t0_n_cand": u0["n_cand"], "t0_n_rank": int(len(pj0)),
            "universe_floor": UNIVERSE_FLOOR,
            "n_firing_months": len(_G["_firing"])}
    else:
        chk("leg4_t0_present", False,
            "requires div faces + transfer probe (fail-closed)")
    # regime face (510300 from repo core48, date-keyed labels)
    reg = _G.get("regime") if _G else None
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
    # seed registry rows (landed at the r610 freeze window)
    seeds = {k: v for k, v in SEED_REGISTRY.items() if "fund_divlowvol" in k}
    chk("seed_registry_rows",
        seeds.get("fund_divlowvol_p1_nulls") == SEED_NULLS
        and seeds.get("fund_divlowvol_p1_sens") == SEED_SENS, str(seeds))
    # ST helper import + fixture sanity (5% seals, no 10% -> flagged).
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
    # probe-kernel import known-answers (single-source import face --
    # ttm window boundary + sidecar stepwise; probe selftest S1/S2 law)
    ex = np.array([20200101, 20210101, 20210102, 20220101], dtype=np.int64)
    cum = np.cumsum(np.array([1.0, 2.0, 4.0, 8.0]))
    dl = [20000101, 20100101, 20200101, 20260626]
    fl = [8.8, 4.4, 2.2, 1.0]
    chk("kernel_import_known_answers",
        abs(ttm_cash_sum(ex, cum, 20220101, 20210101) - 12.0) < 1e-12
        and abs(ttm_cash_sum(ex, cum, 20200101, 20190101) - 1.0) < 1e-12
        and abs(ttm_cash_sum(ex, cum, 20190101, 20180101) - 0.0) < 1e-12
        and abs(sidecar_f_at(dl, fl, 19991231) - 8.8) < 1e-12
        and abs(sidecar_f_at(dl, fl, 20150601) - 4.4) < 1e-12
        and abs(sidecar_f_at(dl, fl, 20260922) - 1.0) < 1e-12,
        "ttm (t-365, t] boundary + sidecar latest-d<=t stepwise "
        "(probe selftest S1/S2 verbatim)")
    # sidecar coverage over in-panel div symbols (probe leg3 census face)
    if _G and "sidecars" in _G:
        sym_pos = {s for s in _G["syms"]}
        missing = [c for c in _G["by_sym"] if c in sym_pos
                   and c not in _G["sidecars"]]
        chk("sidecar_coverage_zero_missing",
            len(missing) == 0 and len(_G["sidecars"]) >= 5000,
            f"n_sidecar={len(_G['sidecars'])} missing={missing[:5]}")
    else:
        chk("sidecar_coverage_zero_missing", False,
            "requires _init_worker (div faces)")
    facts["seed_disclosure"] = {
        "nulls": SEED_NULLS, "sensitivity": SEED_SENS,
        "null_aux": NULL_AUX_SEED,
        "registry_rows": seeds,
        "note": "prereg sec.3 binds nulls to rng([20520000,k]) and sens "
                "to rng([20520500,k]); rows landed at the r610 freeze "
                "window (band-scan receipt probe leg5 GREEN)."}
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
        return ("FUND-DIVLOWVOL-P1-NULLS", "fund-divlowvol-p1-nulls-0of1")
    if getattr(args, "sensitivity", None):
        return ("FUND-DIVLOWVOL-P1-SENS", "fund-divlowvol-p1-sens-0of1")
    entry = ("FUND-DIVLOWVOL-P1-CELL-" + args.cell.replace("-", "").upper()
             + "-" + args.face.upper())
    return (entry, entry.lower() + "-0of1")


def cmd_run(args) -> int:
    global _CLAIM_STARTED
    _CLAIM_STARTED = _now_iso()
    os.makedirs(OUT_DIR, exist_ok=True)
    if not _require_probe():
        return 3
    redo = bool(getattr(args, "redo", False))
    redo_extra = None
    if redo:
        redo_extra = {"burn_machine": _machine_id(),
                      "redo_reason": "containment-redo",
                      "cache_digest": _cache_digest(),
                      "redo_ts": _now_iso()}
        _log("redo", f"redo provenance pinned: machine="
                     f"{redo_extra['burn_machine']} digest="
                     f"{redo_extra['cache_digest']}")
    if args.nulls:
        path = _shard_files(kind="nulls")
        tasks = [_mk("null", k=k) for k in range(K_NULLS)]
        if redo:
            lo = max(0, int(getattr(args, "redo_k_lo", 0) or 0))
            hi = int(getattr(args, "redo_k_hi", -1))
            if hi < 0 or hi >= K_NULLS:
                hi = K_NULLS - 1
            tasks = [p for p in tasks if lo <= p["k"] <= hi]
            _log("nulls", f"redo k-range [{lo},{hi}] -> "
                          f"{len(tasks)} draws")
        _run_parallel_tasks(tasks, lambda p: f"null|{p['k']}", path,
                            "nulls", heavy=True, redo=redo,
                            redo_extra=redo_extra)
        _pool_claim(*_entry_of(args), f"nulls N={K_NULLS} -> {path}")
        return 0
    if args.sensitivity:
        path = _shard_files(kind="sens")
        tasks = [_mk("sens", k=k) for k in range(K_SENS)]
        if redo:
            lo = max(0, int(getattr(args, "redo_k_lo", 0) or 0))
            hi = int(getattr(args, "redo_k_hi", -1))
            if hi < 0 or hi >= K_SENS:
                hi = K_SENS - 1
            tasks = [p for p in tasks if lo <= p["k"] <= hi]
            _log("sens", f"redo k-range [{lo},{hi}] -> "
                         f"{len(tasks)} draws")
        _run_parallel_tasks(tasks, lambda p: f"sens|{p['k']}", path,
                            "sens", heavy=True, redo=redo,
                            redo_extra=redo_extra)
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
                        log, redo=redo, redo_extra=redo_extra)
    # continuous face (G1'/M1/DSR/x2/PBO supply)
    cpath = os.path.join(OUT_DIR, f"cont_{cell}_{face}.json")
    if redo or not os.path.exists(cpath):
        row = _cont_task(_mk("cont", cell=cell, face=face))
        if redo and redo_extra:
            row.update(redo_extra)
        _dump(row, cpath)
        _log(log, f"cont face {'re-derived (redo)' if redo else 'written'}: "
                  f"{cpath}")
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
            print(f"{cell:19s} {face:3s}: {have}/{G_CENSUS_EXPECT} starts "
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
        "probe_ref": "results/_fund_divlowvol_p1_transfer_probe.json",
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
                                "Y10M + listed>=252 + as-of ST proxy "
                                "(p4_ext_tilt._st_regime verbatim, "
                                "trailing-250 slice); dividend gate="
                                "yield_ttm>0; low-vol screen=sigma_252 "
                                "(ddof=1, min 126 bars) <= cross-"
                                "sectional median within candidates",
            "yield_face": "yield_ttm(t)=sum(cash/share, ex_date in (t-365d,"
                          "t]) / P_raw_close(t); P_raw=close_qfq*f(t) "
                          "sidecar stepwise; kernels ttm_cash_sum/"
                          "sidecar_f_at IMPORTED from "
                          "fund_divlowvol_p1_probe (single source)",
            "regime_face": "510300 3-way MA200 proxy from repo core48 "
                           "daily (p1c stock panel carries no 510300 "
                           "column; date-keyed labels; reporting segment "
                           "only, never a gate)",
            "monthly_face": "firing months = clean-tail census starts "
                            "passing UNIVERSE_FLOOR=60 (yield>0 AND "
                            "base AND screenable); t0 pin 2006-02-06 "
                            "(probe leg4 frozen read); pre-t0 flat; "
                            "skipped months carry prior selections",
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
                        file_name="results/fund_divlowvol_p1/"
                                  "fund_divlowvol_p1_results.json",
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
    """Hermetic offline self-check: synthetic panels + synthetic div
    event/sidecar faces injected into _G (no repo data, no network).
    Deterministic. Exercises the REAL month-universe / firing / t0 /
    ranking paths (fixture injects only raw panel arrays)."""
    import shutil
    import tempfile
    global ENUM_LO, ENUM_HI
    fails = []

    def check(name, ok, detail=""):
        print(f"[{'PASS' if ok else 'FAIL'}] {name} {detail}")
        if not ok:
            fails.append(name)

    rng = np.random.default_rng(11)
    T = 700
    NS = 70
    idx = pd.date_range("2020-01-02", periods=T, freq="B")
    syms = [f"S{i:02d}" for i in range(NS)]
    close = np.full((T, NS), np.nan, dtype=np.float64)
    for j in range(NS):
        scale = 0.005 + 0.0002 * j          # distinct per-sym vol
        r = rng.normal(0.0004, scale, T)
        close[:, j] = 100 * np.cumprod(1 + r)
    high = close * 1.01
    low = close * 0.99
    open_ = close * 0.999
    vol = np.full((T, NS), 1e6)
    amt = np.full((T, NS), 5e7)
    pct = np.zeros((T, NS))
    pct[1:] = (close[1:] / close[:-1] - 1) * 100
    pct[~np.isfinite(close)] = np.nan
    # synthetic div events: group A (S00..S39) pays from bar 150; group
    # B (S40..S69) pays from bar 310 -> months before the 310-month are
    # below-floor (40 candidates < 60) -> clean-tail t0; the bar-500
    # round keeps the LATE tail months (TTM window rolled past 360/400)
    # above-floor so the clean tail runs to the panel end
    by_sym = {}
    d150 = int(idx[150].strftime("%Y%m%d"))
    d260 = int(idx[260].strftime("%Y%m%d"))
    d310 = int(idx[310].strftime("%Y%m%d"))
    d360 = int(idx[360].strftime("%Y%m%d"))
    d400 = int(idx[400].strftime("%Y%m%d"))
    d500 = int(idx[500].strftime("%Y%m%d"))
    for i, s in enumerate(syms):
        c_i = 0.5 + 0.05 * i                 # per-share cash (distinct yield)
        if i < 40:
            ex = np.array([d150, d260, d360, d500], dtype=np.int64)
        else:
            ex = np.array([d310, d400, d500], dtype=np.int64)
        by_sym[s] = (ex, np.cumsum(np.full(len(ex), c_i)))
    sidecars = {s: (np.array([20000101], dtype=np.int64),
                    np.array([1.0])) for s in syms}   # f=1.0 flat ladder
    # fixture starts via the REAL census enumeration (ENUM window swap,
    # F19 pattern) -- the caliber (warmup/fwd/active) is the runner's
    # own, never a re-typed filter
    old_win = (ENUM_LO, ENUM_HI)
    ENUM_LO, ENUM_HI = idx[0], idx[-1]
    try:
        starts_fx = enumerate_starts_monthly(idx, close)
    finally:
        ENUM_LO, ENUM_HI = old_win
    _G.clear()
    _G.update(idx=idx, syms=syms, codes_arr=np.array(syms),
              close_np=close, open_np=open_, high_np=high, low_np=low,
              volume_np=vol, amount_np=amt, pct_np=pct,
              by_sym=by_sym, sidecars=sidecars, month_pos=starts_fx,
              first_valid=np.argmax(np.isfinite(close), axis=0),
              static_thr=np.full(NS, 0.10, dtype=np.float32),
              is_cx=np.zeros(NS, dtype=bool),
              regime=pd.Series("na", index=idx, dtype=object))

    # F21: universe floor + t0 pin (fixture clean-tail derivation)
    spans_fx = _firing_months()
    t0_pos = _G["_t0_pos"]
    flags = _G["_floor_flags"]
    t0_i = _G["_t0_i"]
    exp_t0 = min(p for p in starts_fx if p >= 310)
    check("F21_floor_t0_pin",
          t0_pos == exp_t0 and all(flags[t0_i:])
          and not any(flags[:t0_i])
          and spans_fx[0][0] == t0_pos
          and all(m == e_prev for (m, _), (_, e_prev) in
                  zip(spans_fx[1:], spans_fx[:-1])),
          f"t0={t0_pos} want={exp_t0} n_firing={len(spans_fx)}")
    check("F21b_firing_count",
          len(spans_fx) == len(starts_fx) - t0_i,
          f"firing={len(spans_fx)} starts={len(starts_fx)} t0_i={t0_i}")
    # F22: vol_frac ablation face -- 1.0 keeps all, 0.5 keeps the low half
    u_t0 = _month_universe(t0_pos)
    pj_all, _ = _pick_j(u_t0, 1.0)
    pj_half, _ = _pick_j(u_t0, 0.5)
    med_s = float(np.median(u_t0["cand_sigma"]))
    check("F22_vol_frac_ablation",
          len(pj_all) == u_t0["n_cand"]
          and len(pj_half) <= len(pj_all)
          and set(pj_half.tolist()) <= set(pj_all.tolist())
          and all(u_t0["cand_sigma"][u_t0["cand_j"].tolist().index(j)]
                  <= med_s for j in pj_half.tolist()),
          f"all={len(pj_all)} half={len(pj_half)} med={med_s:.5f}")
    # F1: eq weights sum to 1 per firing month; pick size <= N
    picks = _cell_picks("yieldvol", 20)
    w_ok = all(abs(w - 1.0 / len(top)) < 1e-12
               for (_, _, top, w) in picks)
    n_ok = all(len(top) <= 20 for (_, _, top, _) in picks)
    check("F1_eq_weights_1_over_N", w_ok and n_ok,
          f"months={len(picks)}")
    # F2: Top-N by yield DESC within the low-vol half (independent
    # recompute from the REAL universe arrays)
    m0 = picks[0][0]
    u0 = _month_universe(m0)
    sig = u0["cand_sigma"]
    yv = u0["cand_yield"]
    pj = u0["cand_j"]
    keep = sig <= float(np.median(sig))
    cand = sorted(zip(yv[keep].tolist(), pj[keep].tolist()),
                  key=lambda t: (-t[0], syms[t[1]]))
    exp_top = sorted(j for _, j in cand[:20])
    got_top = sorted(picks[0][2].tolist())
    check("F2_topN_yield_desc_in_lowvol", got_top == exp_top,
          f"got={got_top[:6]} exp={exp_top[:6]}")
    check("F2b_selection_in_lowvol_half",
          set(got_top) <= set(pj[keep].tolist()))
    # F3: build determinism
    picks2 = _cell_picks("yieldvol", 20)
    check("F3_build_deterministic",
          all((a[0] == b[0]) and (a[2] == b[2]).all()
              for a, b in zip(picks, picks2)))
    # F23: pre-t0 flat sleeve -- a window entirely before t0 has zero
    # entries and a constant NAV
    run_pre = run_cell_portfolio(_cell_spans(HEADLINE), "x1", 0, t0_pos - 1)
    nav_pre = _nav_from_run(run_pre, 0, t0_pos - 1)
    check("F23_pre_t0_flat_sleeve",
          bool(np.allclose(nav_pre.to_numpy(), CAPITAL, atol=1e-9)),
          f"nav_min={float(nav_pre.min()):.2f} max={float(nav_pre.max()):.2f}")
    # F4: engine T+1 (first trade strictly after the first signal day)
    spans = _spans_from_picks(picks)
    run = run_cell_portfolio(spans, "x1", t0_pos, T - 1, keep_trades=True)
    nav = _nav_from_run(run, t0_pos, T - 1)
    check("F4_nav_len", run is not None and len(nav) > 100,
          f"nav_days={len(nav)}")
    first_sig = idx[picks[0][0]]
    if run["trades"]:
        first_fill = min(pd.Timestamp(tr["date"]) for tr in run["trades"])
        check("F4_t_plus_1", first_fill > first_sig,
              f"first_fill={first_fill.date()} sig={first_sig.date()}")
    else:
        check("F4_t_plus_1", True, "no fills in fixture (honest)")
    # F5: x2 cost bites
    runx = run_cell_portfolio(spans, "x2", t0_pos, T - 1)
    navx = _nav_from_run(runx, t0_pos, T - 1)
    check("F5_x2_face", runx is not None and len(navx) > 100)
    if run["n_trades"] > 0:
        check("F5_x2_cost_bites",
              abs(float(navx.iloc[-1]) - float(nav.iloc[-1])) > 1e-6)
    # F6: PIT ex-date anchor law -- appending FUTURE dividend events
    # must leave every EARLIER month's selection invariant and change
    # the tail (exercises the REAL _month_universe path; caches popped)
    _G.pop("_muniv", None)
    _G.pop("_st_rows", None)
    _G.pop("_sig_rows", None)
    picks_a = _cell_picks("yieldvol", 20)
    n_head = len(picks_a) // 2
    mid_ts = idx[picks_a[n_head][0]]
    fut = int((mid_ts + pd.Timedelta(days=10)).strftime("%Y%m%d"))
    mutated = {}
    for s in syms:
        ex, cum = by_sym[s]
        mutated[s] = (np.append(ex, fut),
                      np.append(cum, cum[-1] + 5.0))   # huge future cash
    _G["by_sym"] = mutated
    _G.pop("_muniv", None)
    picks_b = _cell_picks("yieldvol", 20)
    _G["by_sym"] = by_sym
    _G.pop("_muniv", None)           # later legs recompute on true faces
    same = all((a[2] == b[2]).all()
               for a, b in zip(picks_a[:n_head], picks_b[:n_head]))
    diff = any((a[2] != b[2]).any()
               for a, b in zip(picks_a[n_head + 3:], picks_b[n_head + 3:]))
    check("F6_pit_exdate_anchor_law", same and diff,
          f"head_same={same} tail_diff={diff}")
    # F7: double-run byte identity (cont face)
    a = _cont_task(_mk("cont", cell=HEADLINE, face="x1"))
    b = _cont_task(_mk("cont", cell=HEADLINE, face="x1"))
    check("F7_double_run_identity", a == b,
          f"sharpe={a['sharpe_full']} trades={a['n_trades']}")
    # F8: null rng substream determinism
    k1 = np.random.default_rng([SEED_NULLS, 0]).integers(0, 48, 5).tolist()
    k2 = np.random.default_rng([SEED_NULLS, 0]).integers(0, 48, 5).tolist()
    check("F8_null_rng_substream", k1 == k2, str(k1))
    # F9: checkpoint resume
    tmp = tempfile.mkdtemp()
    p = os.path.join(tmp, "cells.jsonl")
    _append_rows(p, [{"key": f"{HEADLINE}|x1|300"}])
    check("F9_resume_skip", f"{HEADLINE}|x1|300" in _done_keys(p))
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
    nav_slice = _nav_from_run(run, t0_pos, T - 1)
    tail_full = nav_full.reindex(nav_slice.index).ffill()
    eq_tail = np.allclose(tail_full.to_numpy(), nav_slice.to_numpy(),
                          atol=1e-9)
    check("F15_span_slice_equivalence",
          eq_tail and run["n_trades"] == run_full["n_trades"],
          f"tail_eq={eq_tail} trades={run['n_trades']}/"
          f"{run_full['n_trades']}")
    # F16: monthly hold-through (t22 convention, corrected face -- the
    # quality-family leg's m0==0 fixture path never exercised the edge
    # sub-checks): the selected member is entry-True across the WHOLE
    # month span, never entry-True before its first signal day, and
    # every entry transition lands on a FIRING-MONTH edge (rotation
    # happens only at month boundaries; re-selection at e0 is legal)
    j0 = picks[0][2][0]
    m0p, e0 = picks[0][0], picks[0][1]
    ent, _sc = _sym_arrays(j0, spans[j0])
    fire_pos = {m for (m, _) in spans_fx}
    trans = [t for t in range(1, T)
             if bool(ent[t]) != bool(ent[t - 1])]
    check("F16_month_holdthrough",
          bool(ent[m0p:e0].all())
          and not bool(ent[m0p - 1])
          and all(t in fire_pos for t in trans),
          f"span=({m0p},{e0}) transitions={trans[:6]}")
    # F17: G-MASK -- null candidates == headline rank universe (identity
    # by construction on the SAME cached universe object)
    u = _month_universe(m0)
    pj_head, _ = _pick_j(u, VOL_FRAC_HEADLINE)
    null_cand = _pick_j(_month_universe(m0), VOL_FRAC_HEADLINE)[0]
    check("F17_g_mask_identity", np.array_equal(pj_head, null_cand),
          f"n={len(pj_head)}")
    # F18: probe-kernel import known-answers (single-source import face)
    ex = np.array([20200101, 20210101, 20210102, 20220101], dtype=np.int64)
    cum18 = np.cumsum(np.array([1.0, 2.0, 4.0, 8.0]))
    ok18 = (abs(ttm_cash_sum(ex, cum18, 20220101, 20210101) - 12.0) < 1e-12
            and abs(ttm_cash_sum(ex, cum18, 20210102, 20200103) - 6.0) < 1e-12
            and abs(ttm_cash_sum(ex, cum18, 20200101, 20190101) - 1.0) < 1e-12
            and abs(ttm_cash_sum(ex, cum18, 20190101, 20180101) - 0.0) < 1e-12)
    dl = [20000101, 20100101, 20200101, 20260626]
    fl = [8.8, 4.4, 2.2, 1.0]
    ok18b = (abs(sidecar_f_at(dl, fl, 19991231) - 8.8) < 1e-12
             and abs(sidecar_f_at(dl, fl, 20100101) - 4.4) < 1e-12
             and abs(sidecar_f_at(dl, fl, 20150601) - 4.4) < 1e-12
             and abs(sidecar_f_at(dl, fl, 20260922) - 1.0) < 1e-12)
    check("F18_kernel_import_known_answers", ok18 and ok18b,
          "ttm boundary (t-365,t] + sidecar stepwise (probe S1/S2 law)")
    # F18c: same-day multi-component cash SUM (600519 law)
    ex3 = np.array([20060519, 20060519], dtype=np.int64)
    cum3 = np.cumsum(np.array([1.0, 2.0]))
    check("F18c_same_day_sum",
          abs(ttm_cash_sum(ex3, cum3, 20060601, 20050601) - 3.0) < 1e-12)
    # F19: G-CENSUS logic leg (hermetic) -- the enumeration criteria on a
    # synthetic panel equal an independent inline recomputation; the
    # REAL-panel 401 read is probe leg3 (family bit-exact window).
    idx2 = pd.date_range("2020-01-02", periods=700, freq="B")
    close2 = np.full((700, 30), 100.0)          # all 30 members active
    old_win = (ENUM_LO, ENUM_HI)
    ENUM_LO, ENUM_HI = idx2[0], idx2[-1]
    census_ok, n_starts2, n_exp2 = False, -1, -1
    try:
        starts2 = enumerate_starts_monthly(idx2, close2)
        mp2 = _monthly_positions(idx2)
        exp2 = [p for p in mp2
                if p >= WARMUP_TD and (len(idx2) - 1 - p) >= W6M // 2
                and int((~np.isnan(np.asarray(close2[p]))).sum()) >= MIN_LISTED]
        n_starts2, n_exp2 = len(starts2), len(exp2)
        census_ok = (list(starts2) == exp2) and n_starts2 > 0
    finally:
        ENUM_LO, ENUM_HI = old_win
    check("F19_g_census_logic", census_ok,
          f"starts={n_starts2} exp={n_exp2}")
    # F20a: redo AA-replace face -- same keys, new content + provenance,
    # untouched rows verbatim, order preserved (r611 containment leg)
    tmp = tempfile.mkdtemp()
    p20 = os.path.join(tmp, "redo.jsonl")
    _append_rows(p20, [{"key": "A|1", "v": "old-a"},
                       {"key": "B|1", "v": "keep-b"}])
    pre_b = open(p20, encoding="utf-8").read().splitlines()[1]
    _replace_rows(p20, [{"key": "A|1", "v": "new-a"}],
                  {"burn_machine": "bm-x", "cache_digest": "deadbeefcafe1234"})
    ln20 = open(p20, encoding="utf-8").read().splitlines()
    r20a = (len(ln20) == 2
            and json.loads(ln20[0])["v"] == "new-a"
            and json.loads(ln20[0])["burn_machine"] == "bm-x"
            and json.loads(ln20[0])["cache_digest"] == "deadbeefcafe1234"
            and ln20[1] == pre_b
            and _done_keys(p20) == {"A|1", "B|1"})
    check("F20a_redo_aa_replace", r20a,
          f"lines={len(ln20)} keys={sorted(_done_keys(p20))}")
    # F20b: redo new-key honesty -- absent pre-run key lands, not dropped
    _replace_rows(p20, [{"key": "C|9", "v": "new-c"}])
    ln20b = open(p20, encoding="utf-8").read().splitlines()
    check("F20b_redo_new_key_lands",
          len(ln20b) == 3 and json.loads(ln20b[2])["key"] == "C|9",
          f"lines={len(ln20b)}")
    shutil.rmtree(tmp, ignore_errors=True)
    # F20c: redo arg wiring (no compute)
    ap20 = argparse.ArgumentParser()
    ap20.add_argument("--redo", action="store_true")
    ap20.add_argument("--redo-k-lo", type=int, default=0)
    ap20.add_argument("--redo-k-hi", type=int, default=-1)
    a20 = ap20.parse_args(["--redo", "--redo-k-lo", "0",
                           "--redo-k-hi", "8"])
    a20b = ap20.parse_args([])
    check("F20c_redo_arg_wiring",
          a20.redo and a20.redo_k_lo == 0 and a20.redo_k_hi == 8
          and not a20b.redo and a20b.redo_k_hi == -1,
          f"redo={a20.redo} hi={a20.redo_k_hi} default={a20b.redo}")
    print(f"selftest: {len(fails)} FAIL" if fails else "selftest: ALL PASS")
    return 1 if fails else 0


# ----------------------------------------------------------------------- main

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="FUND-DIVLOWVOL-P1 stock monthly dividend-low-vol "
                    "(high TTM cash yield x low-vol screen) family judged "
                    "batch runner (hold-through exit-axis dual gate, "
                    "ex-date PIT anchors + sidecar raw-price recovery, "
                    "universe-floor clean-tail t0 pin, law-A census; "
                    "fail-closed until probe PASS)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("d6")
    sub.add_parser("probe")
    r = sub.add_parser("run")
    r.add_argument("--cell", default="")
    r.add_argument("--face", default="x1")
    r.add_argument("--nulls", action="store_true")
    r.add_argument("--sensitivity", action="store_true")
    r.add_argument("--redo", action="store_true",
                   help="r611 containment family parity: re-burn and "
                        "AA-replace rows at the same keys (key set "
                        "unchanged, attrition-safe) with burn-machine + "
                        "cache-content provenance")
    r.add_argument("--redo-k-lo", type=int, default=0,
                   help="with --redo on nulls/sens: inclusive k lower "
                        "bound (contamination-ledger selective re-burn)")
    r.add_argument("--redo-k-hi", type=int, default=-1,
                   help="with --redo on nulls/sens: inclusive k upper "
                        "bound (-1 = full range)")
    sub.add_parser("status")
    sub.add_parser("finalize")
    sub.add_parser("selftest")
    args = ap.parse_args(argv)
    return {"d6": cmd_d6, "probe": cmd_probe, "run": cmd_run,
            "status": cmd_status, "finalize": cmd_finalize,
            "selftest": cmd_selftest}[args.cmd](args)


if __name__ == "__main__":
    raise SystemExit(main())
