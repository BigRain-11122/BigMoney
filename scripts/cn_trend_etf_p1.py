"""CN_TREND_ETF_P1 runner -- time-series trend-following ETF sleeve judged
batch (T-2026-09-26-87 s2 queue #1, SCHOOL_SUPPLY_S1.md sec.2 row 14).

Laws (frozen in research/CN_TREND_ETF_PREREG.md @commit feb36786 -- R99:
prereg freeze precedes runner build precedes ANY run; seed registered at
the freeze commit, SEED_REGISTRY['cn_trend_etf_p1'] = 20270201, band
20270201..20272200 collision-free by construction).

  panel   data/daily/*.csv ETF board (OHLCV close-px face, 1724 files);
          D2 lockbox EVIDENCE_CUTOFF 2026-09-22 -- runner LOADS THEN
          TRUNCATES to cutoff, all gates act on the truncated face (R280
          zero-run amendment: live panel may advance past cutoff; the
          frozen 'last==cutoff' clause reads on the lockbox face).
          Universe = mechanical re-derive (frozen filter, probe
          results/cn_trend_probe.json is the frozen reference): rows>=2600
          AND first<=2016-06-30 AND last==2026-09-22 AND OHLCV zero-NaN
          AND med_amount20 >= 50e6 (rolling-20 MEDIAN of vol*close, then
          history median, probe-verbatim) AND ann_std >= 3% (std of
          pct_change * sqrt(252)) -> universe_n == 23, symbol set must
          equal the probe's (fail-closed exit 2 otherwise). Cash/monetary
          ETFs (511010/511880/511990/159001/511810) fall out via the
          ann_std clause (trend signal structurally undefined, honest).
  sse     regime gate + census segment face via regime_deep_replay.
          load_index_bench() (prereg s3 same-source), reindexed onto the
          union calendar with ffill bridge; sse MA200 needs 200 finite
          values else gate UNDEFINED -> fail-closed no entry.
  signal  per leg, all close-face, close t computed -> open t+1 fill
          (T+1 asserted per order; R240 law):
          MA family: MA20>MA60 long state; entries on RISING edges only,
          exits on falling edges (anti-churn event law). MA_DUAL gate =
          leg close > leg MA200; MA_BG gate = sse close > sse MA200.
          Gates are ENTRY FILTERS (prereg s3.1 col semantics: the exit
          column is 'reverse cross' ONLY) -- a gate closing mid-hold does
          NOT force an exit, a gate reopening mid-long does NOT re-enter
          (entry = signal edge while gate open; MA200 undefined = no
          entry, fail-closed).
          DON20_10 / DON55_20: Donchian latch -- enter close[t] >
          max(close[t-hi..t-1]), exit close[t] < min(close[t-lo..t-1]);
          while latched, further breakouts are ignored (hysteresis).
          MA_TRAIL: MA latch + trailing stop -- while held, peak close
          tracked; close[t] < 0.85*peak -> exit at next open. Re-entry
          only on the NEXT MA rising edge (conservative stop-out reading,
          disclosed).
  weights every 5 union-calendar bars (offset=0) renormalize held legs:
          equal weight min(1/n_active, 0.20) -- MA_INVVOL instead weights
          prop 1/std20 (rolling 20d std of returns, close-known) capped
          0.20; capped excess goes to CASH (concentration guard, no
          redistribution). Off-grid entries buy the new leg only (target
          = same equal/capped rule at the post-entry active count);
          between events shares constant (anti-churn). Cash zero-yield.
  costs   V2 ADV20-tiered per side, single source alloc_backtest.
          side_cost_v2 / side_cost_x2; judged face = x2 ALWAYS ON (CN-*
          family precedent), x1 = disclosure column. Cost on every fill
          notional (open price x shares). ADV20 = mean(vol*close, 20)
          through close t-1 = the fill-day-known face; ADV unavailable ->
          fill rolls forward (honest, warmup-honest: judged signals need
          >=60 bars so ADV is always ready for real entries; nulls may
          roll in the first 19 bars, same rule for all draws).
  fills   sells first (leg order asc), then buys (leg order asc,
          deterministic); buys lot-rounded (knowledge.rules.min_lot
          single source) with the r251 afford loop (trial notional ->
          cost -> notional+cost <= cash else lot down); sells exact-share
          lot-multiples; renorm targets lot-aligned DOWN. Fill-day open
          NaN -> roll to next finite open.
  nulls   K=2000 same-mask random activations (RANDOM_LARGE_SAMPLE_LAW
          s3): per leg, weekly grid (every 5th bar) Bernoulli(p = that
          leg's MA_BASE duty cycle) -> random long/flat paths, SAME
          universe, SAME execution machinery, SAME x2 cost face; seed =
          20270201+k, k<2000 (declared band); null Sharpe values ->
          own null_pool for skill_line_v2/g1_prime_v2. Dual robust p
          values: block bootstrap 2000 draws (block=10d) + sign-flip
          2000 draws per judged cell (one generator seeded at SEED,
          family face).
  starts  full-census virtual starts t0 in [200, T-126), 126d windows,
          strategy vs universe-EW passive proxy; 4 segment classes
          (bull/bear/deep_bear/chop by sse level, MA200, 60d return --
          REV_OSC s2.1 frozen rule verbatim); segment n<500 =
          insufficient-sample honest note; >=100 random train/val splits
          (sign agreement) + walk-forward 5 sequential folds (law s2.3).
  gates   G1'v2 = science_gates.g1_prime_v2(sharpe_full, returns,
          batch_cells=2007, pool='core48', n_trades, n_entries,
          null_pool=own 2000) on the 7 judged x2 cells; G2 =
          g2_registration_v2(g1_pass, dsr, pbo) with DSR =
          deflated_sharpe_ratio on RAW daily returns (n_trials=
          line.n_eff, var_null_sr = null sigma^2, CN family precedent)
          and family PBO = screening/pbo.cscv_pbo CSCV-8 over the 7-cell
          x2 matrix. Batch descriptive clauses: annualized>0 AND OOS
          (>= IS_END+1 = 2025-01-01, composite_ic shared split) dual
          positive AND maxDD >= -35%. D6 reject face = max|corr| vs the
          6 registered CE members (cn_rev_tilt_p1 ew6 canon, tuple-unpack
          r280 amendment) >= 0.7; same-batch pairwise disclosure;
          prior-negative CN families = advisory columns only (closed
          families never admission faces).
  ledger  science_gates.append_ledger('CN_TREND_ETF_P1', 2007,
          'cn_trend_etf_p1', evidence_cutoff='2026-09-22') single-shot at
          finalize; artifact block under the canonical trials_ledger key
          (r252 law); attrition row lands in the ENTRIES list (r248).

Products (prereg s6): results/cn_trend_ETF/p1_results.json (top-level
evidence_cutoff + science_gates.cutoff_meta + D6 + judged readouts +
nulls + census + splits + gates + ledger block) + cells/*.json|npy
per-cell idempotent checkpoints (cross-round pool resume) +
cells_summary.csv. N_eff = 2007 (7 judged x1-face cells are disclosure
columns, not on the D1 bill; family CN-DIV-LOWVOL-ROT precedent).

Usage: run | selftest   (exit 0 ok; 2 = fail-closed gate/mechanism refusal)
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

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "screening"))

import numpy as np
import pandas as pd

import science_gates as SG                      # shared gate library (O-2250)
from alloc_backtest import side_cost_v2, side_cost_x2
from composite_ic import IS_END
from pbo import cscv_pbo, align_returns
from knowledge import rules as krules
import regime_deep_replay as RDR
from cn_rev_tilt_p1 import REG6, load_member_rets, _corr, d6_block
from parallel_runner import run_cells_parallel

TICKET = "T-2026-09-26-87"
PREREG = os.path.join(ROOT, "research", "CN_TREND_ETF_PREREG.md")
PROBE = os.path.join(ROOT, "results", "cn_trend_probe.json")
DAILY_DIR = os.path.join(ROOT, "data", "daily")
OUT_DIR = os.path.join(ROOT, "results", "cn_trend_ETF")
CELL_DIR = os.path.join(OUT_DIR, "cells")
OUT_JSON = os.path.join(OUT_DIR, "p1_results.json")
OUT_CSV = os.path.join(OUT_DIR, "cells_summary.csv")
ATT_JSON = os.path.join(ROOT, "results", "gate_attrition.json")

EVIDENCE_CUTOFF = "2026-09-22"                  # prereg s2 D2 lockbox
UNIVERSE_N_EXPECT = 23                           # probe-frozen
ROWS_MIN = 2600
FIRST_MAX = "2016-06-30"
MED_AMT20_MIN = 5e7
ANN_STD_MIN = 0.03
SSE_COVER_MIN = 0.95
BATCH_NAME = "CN_TREND_ETF_P1"
BATCH_CELLS = 2007                               # 7 judged + 2000 nulls
K_NULLS = 2000
SEED = None          # filled at run from SG.SEED_REGISTRY (freeze commit)
PBP = 243.0          # ETF-board trading bars/year (CN-* family constant)
CAPITAL = 1_000_000.0                            # CN-* paper spec
LOT = int(krules.min_lot("510300"))              # 100 shares (single source)
W_CAP = 0.20                                     # single-leg weight cap
REBAL_STEP = 5                                   # every 5 bars, offset=0
TRAIL_DD = 0.15                                  # MA_TRAIL stop line
D6_REJECT = 0.7
MAXDD_LINE = -0.35                               # descriptive red line
WIN_DAYS = 126
STARTS_FROM = 200
SEG_MIN = 500
OOS_START = pd.Timestamp(IS_END) + pd.Timedelta(days=1)   # 2025-01-01
JUDGED_FACE = "x2"
FACES = {"x1": side_cost_v2, "x2": side_cost_x2}

# judged grid (prereg s3.1, frozen)
CELLS = [
    {"name": "MA_BASE",  "kind": "ma",  "gate": None,  "invvol": False, "trail": False},
    {"name": "MA_DUAL",  "kind": "ma",  "gate": "leg", "invvol": False, "trail": False},
    {"name": "MA_BG",    "kind": "ma",  "gate": "sse", "invvol": False, "trail": False},
    {"name": "MA_INVVOL","kind": "ma",  "gate": None,  "invvol": True,  "trail": False},
    {"name": "DON20_10","kind": "don", "hi": 20, "lo": 10},
    {"name": "DON55_20","kind": "don", "hi": 55, "lo": 20},
    {"name": "MA_TRAIL", "kind": "ma",  "gate": None,  "invvol": False, "trail": True},
]

# prior-negative CN families: advisory disclosure faces only (closed
# families are never admission faces; corr computed only where the
# family artifact carries a verifiable dated reconstruction)
ADVISORY_FAMILIES = [
    ("CN-REGIME-POLICY-P1", "results/cn_regime_policy/p1_results.json",
     "data/daily/sh510300.csv"),
    ("CN-DIV-LOWVOL-ROT-P1", "results/cn_div_lowvol_rot/p1_results.json", None),
    ("CN-CORE-SATELLITE-P1", "results/cn_core_satellite/p1_results.json", None),
    ("CN-CORE-DDCTL-P1", "results/cn_core_ddctl/p1_results.json", None),
]


def _machine_id():
    try:
        return json.load(open(os.path.join(
            ROOT, "fleet", "machine.json"), encoding="utf-8"))["machine_id"]
    except Exception:
        return "unknown"


# ---------------------------------------------------------------- panel


def _leg_filter_face(df):
    """Frozen probe-verbatim filter clauses on ONE truncated leg frame."""
    close = df["close"]
    vol = df["volume"]
    amt20 = (vol * close).rolling(20).median().dropna()
    med20 = float(amt20.median()) if len(amt20) else 0.0
    ret = close.pct_change().dropna()
    ann_std = float(ret.std() * (252 ** 0.5)) if len(ret) > 1 else 0.0
    return {
        "rows_ok": len(df) >= ROWS_MIN,
        "first_ok": str(df["date"].iloc[0])[:10] <= FIRST_MAX,
        "last_ok": str(df["date"].iloc[-1])[:10] == EVIDENCE_CUTOFF,
        "nan_free": int(df.isna().sum().sum()) == 0,
        "amount_ok": med20 >= MED_AMT20_MIN,
        "std_ok": ann_std >= ANN_STD_MIN,
        "med_amount20_cny": round(med20, 0),
        "ann_std": round(ann_std, 4),
    }


def load_panel():
    """Truncate-to-cutoff load + mechanical universe re-derive + gates.

    Two-pass read: pass 1 loads only the date column (rows/first/last
    clauses on the lockbox face), pass 2 full-reads the date-passers only
    (NaN/amount/std clauses). Probe-verbatim clause semantics, zero
    invention; 1724-file board -> ~25 full reads.
    """
    cut = pd.Timestamp(EVIDENCE_CUTOFF)
    cand = []
    rejects = {}
    date_ok = {}
    for f in sorted(glob.glob(os.path.join(DAILY_DIR, "*.csv"))):
        sym = os.path.basename(f)[:-4]
        dt = pd.read_csv(f, usecols=["date"])["date"]
        dt = pd.to_datetime(dt)
        dt = dt[dt <= cut]                      # D2 lockbox face
        n, first, last = len(dt), str(dt.iloc[0])[:10] if len(dt) else "", \
            str(dt.iloc[-1])[:10] if len(dt) else ""
        if n >= ROWS_MIN and first <= FIRST_MAX and last == EVIDENCE_CUTOFF:
            date_ok[sym] = f
        else:
            rejects[sym] = [k for k, v in
                            (("rows_ok", n >= ROWS_MIN),
                             ("first_ok", first <= FIRST_MAX),
                             ("last_ok", last == EVIDENCE_CUTOFF)) if not v]
    legs = {}
    for sym, f in date_ok.items():
        d = pd.read_csv(f)
        d.columns = [str(c).lower() for c in d.columns]
        d["date"] = pd.to_datetime(d["date"])
        d = d[d["date"] <= cut].reset_index(drop=True)   # D2 lockbox
        legs[sym] = d
    for sym, d in legs.items():
        face = _leg_filter_face(d)
        if all(face[k] for k in ("nan_free", "amount_ok", "std_ok")):
            cand.append(sym)
        else:
            rejects[sym] = [k for k in ("nan_free", "amount_ok", "std_ok")
                            if not face[k]]
    cand.sort()
    probe = json.load(open(PROBE, encoding="utf-8-sig"))
    probe_syms = sorted(c["sym"] for c in probe["universe"])
    gates = {
        "universe_n_ok": len(cand) == UNIVERSE_N_EXPECT,
        "probe_cross_ok": cand == probe_syms,
        "probe_file_ok": os.path.exists(PROBE),
    }
    if not all(gates.values()):
        print(f"FAIL-CLOSED: panel gates red {gates} n={len(cand)} "
              f"probe_n={len(probe_syms)} -- no artifact")
        return None, gates

    union_days = sorted(set().union(*[set(legs[s]["date"]) for s in cand]))
    idx = pd.DatetimeIndex(union_days)
    T, N = len(idx), len(cand)
    open_m = np.full((T, N), np.nan)
    close_m = np.full((T, N), np.nan)
    vol_m = np.full((T, N), np.nan)
    cover_gaps = {}
    for j, s in enumerate(cand):
        d = legs[s].set_index("date").reindex(idx)
        n_gap = int(d["close"].isna().sum())
        if n_gap:
            cover_gaps[s] = n_gap           # disclosure-only (calendar face)
        open_m[:, j] = d["open"].to_numpy(float)
        close_m[:, j] = d["close"].to_numpy(float)
        vol_m[:, j] = d["volume"].to_numpy(float)
    close_ff = pd.DataFrame(close_m).ffill().to_numpy(float)

    bench = RDR.load_index_bench()
    sse_close = bench.reindex(idx).ffill()
    cover = float(sse_close.notna().mean())
    sse_v = sse_close.to_numpy(float)
    sse_ma200 = pd.Series(sse_v).rolling(200, min_periods=200).mean().to_numpy()

    # -- per-leg signal faces (union-calendar reindexed, NaN-aware)
    def _roll(mat, w, how="mean"):
        df = pd.DataFrame(mat)
        out = getattr(df.rolling(w, min_periods=w), how)()
        return out.to_numpy(float)

    ma20 = _roll(close_m, 20)
    ma60 = _roll(close_m, 60)
    ma200 = _roll(close_m, 200)
    with np.errstate(invalid="ignore"):
        ma_long = (ma20 > ma60) & np.isfinite(ma20) & np.isfinite(ma60)
        leg_gate = (close_m > ma200) & np.isfinite(close_m) & np.isfinite(ma200)
    sse_gate = (sse_v > sse_ma200) & np.isfinite(sse_v) & np.isfinite(sse_ma200)
    rets = np.full_like(close_m, np.nan)
    with np.errstate(invalid="ignore"):
        rets[1:] = close_m[1:] / close_m[:-1] - 1.0
    std20 = pd.DataFrame(rets).rolling(20, min_periods=20).std().to_numpy(float)
    notional20 = vol_m * close_m
    adv_arg = pd.DataFrame(notional20).rolling(20, min_periods=20).mean() \
        .shift(1).to_numpy(float)          # ADV20 through close t-1

    # -- universe EW passive proxy (census beat face, prereg s3)
    with np.errstate(invalid="ignore"):
        fin = np.isfinite(rets)
        n_e = fin.sum(axis=1)
        ew_ret = np.where(n_e > 0,
                          np.where(fin, rets, 0.0).sum(axis=1)
                          / np.maximum(n_e, 1), 0.0)

    # -- MA_BASE duty cycles (null Bernoulli p, prereg s3 frozen)
    p_leg = np.array([float(ma_long[:, j][np.isfinite(ma20[:, j])
                                         & np.isfinite(ma60[:, j])].mean())
                      for j in range(N)])

    # -- DON faces
    don = {}
    for hi, lo in ((20, 10), (55, 20)):
        don[(hi, lo)] = (_roll(close_m, hi, "max"), _roll(close_m, lo, "min"))

    gates["sse_cover_ok"] = cover >= SSE_COVER_MIN
    gates["T_sanity_ok"] = T >= ROWS_MIN
    if not gates["sse_cover_ok"] or not gates["T_sanity_ok"]:
        print(f"FAIL-CLOSED: panel gates red {gates}")
        return None, gates

    return {
        "idx": idx, "syms": cand, "T": T, "N": N,
        "open": open_m, "close": close_m, "close_ff": close_ff,
        "adv_arg": adv_arg, "std20": std20,
        "ma20": ma20, "ma60": ma60, "ma_long": ma_long,
        "leg_gate": leg_gate, "sse_gate": sse_gate,
        "sse": sse_v, "sse_ma200": sse_ma200,
        "don": don, "ew_ret": ew_ret, "p_leg": p_leg,
        "sse_cover": cover, "cover_gaps": cover_gaps,
        "rejects_census": {k: len(v) for k, v in
                           (("filter_rejects", rejects),)},
        "gates": gates,
    }, gates


# ---------------------------------------------------------------- events


def cell_events(P, cell):
    """enter_ev/exit_ev boolean (T,N) matrices per frozen cell spec."""
    T, N = P["T"], P["N"]
    ma_long = P["ma_long"]
    prev = np.vstack([np.zeros((1, N), bool), ma_long[:-1]])
    rise, fall = ma_long & ~prev, ~ma_long & prev
    if cell["kind"] == "ma":
        if cell["gate"] == "leg":
            gate = P["leg_gate"]
        elif cell["gate"] == "sse":
            gate = np.tile(P["sse_gate"][:, None], (1, N))
        else:
            gate = np.ones((T, N), bool)
        return rise & gate, fall
    hi, lo = cell["hi"], cell["lo"]
    hi_max, lo_min = P["don"][(hi, lo)]
    hi_prev = np.vstack([np.full((1, N), np.nan), hi_max[:-1]])
    lo_prev = np.vstack([np.full((1, N), np.nan), lo_min[:-1]])
    C = P["close"]
    with np.errstate(invalid="ignore"):
        brk = (C > hi_prev) & np.isfinite(C) & np.isfinite(hi_prev)
        brkd = (C < lo_prev) & np.isfinite(C) & np.isfinite(lo_prev)
    enter = np.zeros((T, N), bool)
    exit_ = np.zeros((T, N), bool)
    for j in range(N):                     # Donchian latch (hysteresis)
        latch = False
        b, x = brk[:, j], brkd[:, j]
        e, o = enter[:, j], exit_[:, j]
        for t in range(T):
            if not latch and b[t]:
                latch, e[t] = True, True
            elif latch and x[t]:
                latch, o[t] = False, True
    return enter, exit_


# ---------------------------------------------------------------- engine


def run_portfolio(ctx, enter_ev, exit_ev, invvol=False, trail=False,
                  cost_fn=None, collect=False):
    """Event-driven multi-leg sleeve engine (prereg s3 frozen semantics).

    All decisions at close t -> fills at open t+1 (T+1 asserted per
    order). Sells first then buys, leg order asc (deterministic). Buys
    lot-rounded with the r251 afford loop; renorm targets lot-aligned
    down; cash zero-yield; fill-day open/ADV NaN -> roll forward.
    """
    if cost_fn is None:
        cost_fn = side_cost_x2
    T, N = ctx["T"], ctx["N"]
    O, C = ctx["open"], ctx["close"]
    Cff, adv = ctx["close_ff"], ctx["adv_arg"]
    std20 = ctx.get("std20")
    days = ctx.get("days")
    held = np.zeros(N, bool)
    shares = np.zeros(N, float)
    peak = np.zeros(N, float)
    cash = CAPITAL
    eq = np.empty(T)
    rets = np.full(T, np.nan)
    pending = {}
    n_trades = n_entries = rolls = 0
    cost_total = 0.0
    max_notional = 0.0
    min_adv = None
    transitions = []
    t1_ok = True
    trail_on = bool(trail)

    def _fill_px(t, j):
        px = O[t, j]
        a = adv[t, j]
        if not (np.isfinite(px) and np.isfinite(a) and a > 0):
            return None, None
        return float(px), float(a)

    def _buy(t, j, px, a, target_val):
        """Lot-rounded afford loop (r251: cost reserved before cash leaves)."""
        nonlocal cash, shares, n_trades, n_entries, cost_total
        nonlocal max_notional, min_adv
        lots = int(target_val // (px * LOT))
        while lots >= 1:
            notional = lots * LOT * px
            c = cost_fn(notional, a)
            if notional + c <= cash:
                cash -= notional + c
                shares[j] += lots * LOT
                n_trades += 1
                cost_total += c
                max_notional = max(max_notional, notional)
                min_adv = a if min_adv is None else min(min_adv, a)
                if collect:
                    transitions.append({
                        "day": str(days[t].date()) if days is not None else t,
                        "leg": j, "side": "buy", "shares": int(lots * LOT),
                        "notional": round(notional, 2), "cost": round(c, 2)})
                return True
            lots -= 1
        return False

    def _sell(t, j, px, a, nsh):
        nonlocal cash, shares, n_trades, n_entries, cost_total
        nonlocal max_notional, min_adv
        if nsh <= 0:
            return True
        notional = nsh * px
        c = cost_fn(notional, a)
        cash += notional - c
        shares[j] -= nsh
        n_trades += 1
        cost_total += c
        max_notional = max(max_notional, notional)
        min_adv = a if min_adv is None else min(min_adv, a)
        if collect:
            transitions.append({
                "day": str(days[t].date()) if days is not None else t,
                "leg": j, "side": "sell", "shares": int(nsh),
                "notional": round(notional, 2), "cost": round(c, 2)})
        return True

    for t in range(T):
        # -- 1) fills scheduled for today (open t; signal day = t-1 < t)
        for kind, j, w, sig in pending.pop(t, []):
            if t <= sig:
                t1_ok = False
            px, a = _fill_px(t, j)
            if px is None:                   # no bar / ADV warmup: roll
                pending.setdefault(t + 1, []).append((kind, j, w, sig))
                rolls += 1
                continue
            if kind == "sell_all":
                nsh = shares[j]
                held_flag = shares[j] > 0
                if not _sell(t, j, px, a, nsh):
                    pending.setdefault(t + 1, []).append((kind, j, w, sig))
                elif held_flag:
                    pass
            elif kind == "buy":
                eq_open = cash + float(np.nansum(shares * O[t]))
                was_zero = shares[j] == 0
                if _buy(t, j, px, a, w * eq_open) and was_zero:
                    n_entries += 1
            elif kind == "set":
                eq_open = cash + float(np.nansum(shares * O[t]))
                target_lots = int((w * eq_open) // (px * LOT))
                tgt = target_lots * LOT
                cur = shares[j]
                was_zero = cur == 0
                if tgt < cur:
                    if not _sell(t, j, px, a, cur - tgt):
                        pending.setdefault(t + 1, []).append(
                            (kind, j, w, sig))
                elif tgt > cur:
                    delta = tgt - cur
                    lots = delta // LOT
                    while lots >= 1:
                        notional = lots * LOT * px
                        c = cost_fn(notional, a)
                        if notional + c <= cash:
                            cash -= notional + c
                            shares[j] += lots * LOT
                            n_trades += 1
                            cost_total += c
                            max_notional = max(max_notional, notional)
                            min_adv = (a if min_adv is None
                                       else min(min_adv, a))
                            if was_zero:
                                n_entries += 1
                            if collect:
                                transitions.append({
                                    "day": str(days[t].date())
                                    if days is not None else t,
                                    "leg": j, "side": "buy",
                                    "shares": int(lots * LOT),
                                    "notional": round(notional, 2),
                                    "cost": round(c, 2)})
                            break
                        lots -= 1
        # -- 2) equity mark at close
        eq[t] = cash + float(np.nansum(shares * Cff[t]))
        if t > 0:
            rets[t] = eq[t] / eq[t - 1] - 1.0
        # -- 3) close-t events -> fills at open t+1
        exits = exit_ev[t] & held
        if trail_on:
            cj = C[t]
            fin = np.isfinite(cj) & held
            np.maximum.at(peak, np.flatnonzero(fin), cj[fin])
            with np.errstate(invalid="ignore"):
                trail_hit = fin & (cj < (1.0 - TRAIL_DD) * peak)
            exits = exits | trail_hit
        for j in np.flatnonzero(exits):
            pending.setdefault(t + 1, []).append(("sell_all", j, 0.0, t))
            held[j] = False
            peak[j] = 0.0
        entries = enter_ev[t] & ~held
        e_idx = np.flatnonzero(entries)
        if t % REBAL_STEP == 0:
            active = held.copy()
            active[e_idx] = True
            n_act = int(active.sum())
            if n_act:
                if invvol:
                    w = _invvol_w(std20[t], active, N)
                else:
                    w = {j: min(1.0 / n_act, W_CAP)
                         for j in np.flatnonzero(active)}
                for j in np.flatnonzero(active):
                    pending.setdefault(t + 1, []).append(
                        ("set", j, w[j], t))
        elif e_idx.size:
            n_after = int(held.sum()) + int(e_idx.size)
            if invvol:
                active = held.copy()
                active[e_idx] = True
                w = _invvol_w(std20[t], active, N)
            else:
                w = {j: min(1.0 / n_after, W_CAP) for j in e_idx}
            for j in e_idx:
                pending.setdefault(t + 1, []).append(("buy", j, w[j], t))
            held[e_idx] = True
        if t % REBAL_STEP == 0 and e_idx.size:
            held[e_idx] = True               # grid entries join the held set
    rec = {
        "returns": rets, "n_trades": n_trades, "n_entries": n_entries,
        "cost_total": round(cost_total, 2), "rolls": rolls,
        "max_trade_notional": round(max_notional, 2),
        "min_adv_at_trade": round(min_adv, 2) if min_adv else None,
        "t1_ok": t1_ok,
        "transitions_head": transitions[:60] if collect else [],
        "final_held_n": int(held.sum()),
    }
    return rec


def _invvol_w(std_row, active, N):
    """Inverse-vol weights over active legs, capped; residual to cash."""
    inv = np.zeros(N)
    act = np.flatnonzero(active)
    for j in act:
        s = std_row[j]
        if np.isfinite(s) and s > 0:
            inv[j] = 1.0 / s
    tot = inv.sum()
    if tot <= 0:                             # all-undefined fallback: equal
        return {j: min(1.0 / len(act), W_CAP) for j in act}
    return {j: min(inv[j] / tot, W_CAP) for j in act}


# ---------------------------------------------------------------- stats


def _sharpe(r):
    r = np.asarray(r, float)
    r = r[np.isfinite(r)]
    if len(r) < 20 or float(r.std(ddof=1)) == 0:
        return None
    return round(float(r.mean() / r.std(ddof=1) * math.sqrt(PBP)), 4)


def _ann(r):
    r = np.asarray(r, float)
    r = r[np.isfinite(r)]
    if len(r) < 20:
        return None
    return round(float((1.0 + r).prod() ** (PBP / len(r)) - 1.0), 6)


def _max_dd(r):
    r = np.asarray(r, float)
    r = r[np.isfinite(r)]
    if len(r) < 2:
        return None
    eq = np.cumprod(1.0 + r)
    return round(float((eq / np.maximum.accumulate(eq) - 1.0).min()), 6)


def cell_stats(rets, days):
    r = np.asarray(rets, float)
    r1 = r[1:]                                # drop NaN head (r255 law)
    oos = r1[days[1:] >= OOS_START]
    return {
        "sharpe_full": _sharpe(r1), "ann_ret": _ann(r1),
        "max_dd": _max_dd(r1), "n_days": int(len(r1)),
        "oos_sharpe": _sharpe(oos), "oos_ann_ret": _ann(oos),
        "oos_dual_positive": bool((_sharpe(oos) or 0) > 0
                                  and (_ann(oos) or 0) > 0),
        "maxdd_line_pass": bool((_max_dd(r1) or 0) >= MAXDD_LINE),
    }


# ---------------------------------------------------------------- nulls

_NULL_CTX = None            # worker-side context (parallel_runner initargs)


def _null_init(payload):
    global _NULL_CTX
    _NULL_CTX = payload


def _null_sharpe(k):
    """One same-mask random-activation null draw (prereg s3, seed band)."""
    ctx = _NULL_CTX
    T, N = ctx["T"], ctx["N"]
    rng = np.random.default_rng(ctx["seed_base"] + k)
    n_grid = int(math.ceil(T / 5))
    draws = rng.random((n_grid, N)) < ctx["p_leg"][None, :]
    states = np.repeat(draws, 5, axis=0)[:T]
    prev = np.vstack([np.zeros((1, N), bool), states[:-1]])
    enter = states & ~prev
    exit_ = ~states & prev
    rec = run_portfolio(ctx, enter, exit_, invvol=False, trail=False,
                        cost_fn=side_cost_x2, collect=False)
    return _sharpe(rec["returns"][1:]) or 0.0


def run_nulls(P):
    """K=2000 null Sharpe values via the shared parallel runner (workers
    per prereg s0 plan; deterministic keyed consumption, r259 law)."""
    payload = {
        "T": P["T"], "N": P["N"], "open": P["open"],
        "close": P["close"], "close_ff": P["close_ff"],
        "adv_arg": P["adv_arg"], "p_leg": P["p_leg"],
        "seed_base": SEED,
    }
    jobs = [(f"null_{k:04d}", _null_sharpe, (k,)) for k in range(K_NULLS)]
    out = run_cells_parallel(jobs, workers=4, desc="cn_trend nulls",
                             initializer=_null_init, initargs=(payload,))
    workers_used = out.pop("__workers__", 1)
    values = [float(out[f"null_{k:04d}"]) for k in range(K_NULLS)]
    vals = np.asarray(values, float)
    return {
        "values": [round(float(v), 4) for v in vals],
        "coverage": {
            "mu": round(float(vals.mean()), 4),
            "sigma": round(float(vals.std(ddof=1)), 4),
            "n_values": int(len(vals)),
            "schemas_parsed": [
                "cn_trend_etf_p1: K=2000 per-leg weekly-grid Bernoulli("
                "p=MA_BASE duty cycle) random long/flat sleeves, same "
                "universe same execution same x2 cost face, seed "
                "20270201+k k<2000 (declared band)"],
            "known_unparsed": [],
        },
        "workers": int(workers_used),
    }


# ------------------------------------------------------- census & robust


def seg_class(P, t0):
    s, m = P["sse"][t0], P["sse_ma200"][t0]
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
    """RANDOM_LARGE_SAMPLE_LAW s2.1 census + s2.3 splits (rev_osc frozen
    rule family face)."""
    T = P["T"]
    days = P["idx"]
    starts = list(range(STARTS_FROM, T - WIN_DAYS))
    segs = np.array([seg_class(P, t0) for t0 in starts])
    sa = np.array(starts)
    ew = np.asarray(P["ew_ret"], float)
    ew_cs = np.cumsum(np.log1p(ew))
    out = {"n_starts": len(starts), "segments": {}}
    for cls in ("bull", "bear", "deep_bear", "chop", "na"):
        n = int((segs == cls).sum())
        out["segments"][cls] = {"n_starts": n,
                                "sufficient_sample": bool(n >= SEG_MIN)}
    rng = np.random.default_rng(SEED)
    cells = {}
    for name, series in series_by_cell.items():
        r = np.asarray(series, float)
        cs = np.cumsum(np.log1p(np.where(np.isfinite(r), r, 0.0)))
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
        r1 = r[1:]                              # drop NaN head (r255 law)
        fw = np.array_split(r1, 5)
        wf = [round(float(x.mean() / x.std(ddof=1) * math.sqrt(PBP)), 4)
              if np.isfinite(x).all() and x.std(ddof=1) > 0 else None
              for x in fw]
        agree = valid = 0
        for _ in range(100):
            m = rng.random(len(starts)) < 0.5
            if not m.any() or m.all():
                continue
            valid += 1
            a, b_ = float(wret[m].mean()), float(wret[~m].mean())
            agree += int((a > 0) == (b_ > 0))
        cells[name] = {
            "mean_win_ret": round(float(wret.mean()), 6),
            "beat_rate_6m": round(float(beat.mean()), 4),
            "segments": seg_tab, "oos_halves": oos,
            "walk_forward_sharpe": wf,
            "split_sign_agreement_pct":
                round(100.0 * agree / valid, 1) if valid else None,
        }
    out["cells"] = cells
    return out


def robust_stats(series):
    """Block bootstrap (block=10d) + sign-flip, 2000 draws each (s3)."""
    r = np.asarray(series, float)[1:]
    r = r[np.isfinite(r)]
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
        ix = (pos[:, None] * block + offs[None, :]).ravel()
        ix = ix[ix < n]
        bb[i] = r[ix].mean()
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


# ---------------------------------------------------------------- D6


def d6_face(P, series_by_cell):
    """s1 reject face vs REGISTERED members (ew6 canon) + same-batch
    pairwise + prior-negative family advisory columns."""
    member_rets, member_cutoffs = load_member_rets()   # tuple (r280 law)
    days = P["idx"]
    d6 = {"reject_line": D6_REJECT, "members": list(REG6), "cells": {}}
    for name, series in series_by_cell.items():
        s = pd.Series(np.asarray(series, float)[1:], index=days[1:])
        d6["cells"][name] = d6_block(s, member_rets)
    d6["member_cutoffs"] = member_cutoffs
    names = list(series_by_cell)
    cross = {}
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a = pd.Series(np.asarray(series_by_cell[names[i]], float)[1:],
                          index=days[1:])
            b = pd.Series(np.asarray(series_by_cell[names[j]], float)[1:],
                          index=days[1:])
            v, ov = _corr(a, b)
            cross[f"{names[i]}|{names[j]}"] = {"corr": v,
                                               "overlap_days": ov}
    d6["same_batch_cross"] = cross
    # -- prior-negative families: advisory only (closed = never admission)
    adv_out = {}
    for fam, path, corpus in ADVISORY_FAMILIES:
        rec = {"family": fam, "face": "advisory_disclosure_only"}
        fp = os.path.join(ROOT, path)
        if not os.path.exists(fp):
            rec["status"] = "artifact_absent"
            adv_out[fam] = rec
            continue
        try:
            art = json.load(open(fp, encoding="utf-8"))
            audit = art.get("judged_x2_returns_6dp_audit")
            if not audit or corpus is None:
                rec["status"] = "undated_series_alignment_impossible"
                rec["note"] = ("artifact stores value lists without dates; "
                               "positional correlation would be dishonest")
                adv_out[fam] = rec
                continue
            cal = pd.read_csv(os.path.join(ROOT, corpus))
            cal["date"] = pd.to_datetime(cal["date"])
            cal = cal[cal["date"] <= pd.Timestamp(EVIDENCE_CUTOFF)]
            dates = cal["date"]
            fam_cells = {}
            for cname, vals in audit.items():
                if not isinstance(vals, list) or len(vals) != len(dates) - 1:
                    fam_cells[cname] = {
                        "status": "value_count_mismatch_honest_skip"}
                    continue
                fr = pd.Series(vals, index=dates[1:])
                per_ours = {}
                for name, series in series_by_cell.items():
                    s = pd.Series(np.asarray(series, float)[1:],
                                  index=days[1:])
                    v, ov = _corr(s, fr)
                    per_ours[name] = v
                fin = {k: abs(v) for k, v in per_ours.items()
                       if v is not None}
                fam_cells[cname] = {
                    "corr_vs_our_cells": per_ours,
                    "max_abs_corr": round(max(fin.values()), 4) if fin
                    else None}
            rec["status"] = "dated_reconstruction_verified"
            rec["cells"] = fam_cells
        except Exception as exc:
            rec["status"] = "error"
            rec["error"] = repr(exc)[:160]
        adv_out[fam] = rec
    d6["prior_negative_advisory"] = adv_out
    return d6


# ---------------------------------------------------------------- finalize


def _attr_row(batch, delta, total, gates):
    d = json.load(open(ATT_JSON, encoding="utf-8"))
    d["entries"].append({"batch": batch,
                         "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
                         "kind": "measurement", "cells_ledger_delta": delta,
                         "ledger_total_after": total, "gates": gates})
    with open(ATT_JSON + ".tmp", "w", encoding="utf-8") as fh:
        json.dump(d, fh, ensure_ascii=False, indent=1)
    os.replace(ATT_JSON + ".tmp", ATT_JSON)


def finalize(P, panel_face, cells_out, nulls, d6, vstarts, robust, t0):
    days = P["idx"]
    series_by_cell = {n: cells_out[n][JUDGED_FACE]["series"]
                      for n in cells_out}
    line_pool = {"values": nulls["values"], "coverage": nulls["coverage"]}
    line = SG.skill_line_v2(batch_cells=BATCH_CELLS, pool="core48",
                            null_pool=line_pool)
    sigma_null = float(nulls["coverage"]["sigma"])
    gates = {}
    for name, ser in series_by_cell.items():
        st = cells_out[name][JUDGED_FACE]["stats"]
        rets_pd = pd.Series(np.asarray(ser, float)[1:], index=days[1:])
        g1 = SG.g1_prime_v2(
            st["sharpe_full"], rets_pd, batch_cells=BATCH_CELLS,
            pool="core48", null_pool=line_pool,
            n_trades=cells_out[name][JUDGED_FACE]["n_trades"],
            n_entries=cells_out[name][JUDGED_FACE]["n_entries"])
        dsr = SG.deflated_sharpe_ratio(
            rets_pd, n_trials=line["n_eff"], var_null_sr=sigma_null ** 2)
        gates[name] = {"g1_prime_v2": g1, "dsr": dsr}
    mat = align_returns({n: pd.Series(np.asarray(s, float)[1:],
                                      index=days[1:])
                         for n, s in series_by_cell.items()})
    pbo = cscv_pbo(mat)
    pbo_val = float(pbo["pbo"]) if isinstance(pbo, dict) else float(pbo)
    for name in gates:
        gates[name]["g2"] = SG.g2_registration_v2(
            gates[name]["g1_prime_v2"]["pass_v2"],
            gates[name]["dsr"], pbo_val)
        gates[name]["d6_reject"] = bool(d6["cells"][name]["member_face"]
                                        ["reject"])
        st = cells_out[name][JUDGED_FACE]["stats"]
        gates[name]["descriptive"] = {
            "ann_positive": bool((st["ann_ret"] or 0) > 0),
            "oos_dual_positive": st["oos_dual_positive"],
            "maxdd_line_pass": st["maxdd_line_pass"],
        }
    ledger = SG.append_ledger(
        BATCH_NAME, BATCH_CELLS, file_name="cn_trend_etf_p1",
        evidence_cutoff=EVIDENCE_CUTOFF,
        note="7 judged cells (MA_BASE/MA_DUAL/MA_BG/MA_INVVOL/DON20_10/"
             "DON55_20/MA_TRAIL) event-driven 23-ETF trend sleeves + 2000 "
             "same-mask weekly-Bernoulli nulls (x2 judged face, seed band "
             "20270201+k); V2 ADV20-tiered cost, judged x2 always on; prereg "
             "research/CN_TREND_ETF_PREREG.md frozen feb36786; " + TICKET)
    _attr_row(BATCH_NAME, BATCH_CELLS, int(ledger["total"]), {
        "g1_pass": {n: gates[n]["g1_prime_v2"]["pass_v2"] for n in gates},
        "g2_eligible": {n: gates[n]["g2"]["eligible_v2"] for n in gates},
        "d6_reject": {n: gates[n]["d6_reject"] for n in gates},
        "family_pbo": pbo})

    prereg_sha = hashlib.sha256(
        open(PREREG, "rb").read().replace(b"\r\n", b"\n")).hexdigest()
    judged_audit = {
        n: [round(float(v), 6) for v in
            np.asarray(series_by_cell[n], float)[1:]]
        for n in series_by_cell}
    result = {
        "batch": BATCH_NAME,
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "cutoff_meta": SG.cutoff_meta(EVIDENCE_CUTOFF),
        "meta": {
            "ticket": TICKET,
            "prereg": "research/CN_TREND_ETF_PREREG.md",
            "prereg_sha256_lf_normalized": prereg_sha,
            "probe": "results/cn_trend_probe.json (frozen reference)",
            "judge_face": f"{JUDGED_FACE} (whole-V2 doubled, CN-* family "
                          "precedent, always on); x1 disclosure track",
            "seed": {"base": SEED, "k": K_NULLS,
                     "band": "20270201..20272200 (registry-declared)"},
            "accounting": "signal close t -> fills open t+1 (T+1 asserted "
                          "per order); gates are ENTRY FILTERS (exit column "
                          "verbatim: reverse-cross / Donchian breakdown); "
                          "MA_TRAIL re-entry only on next MA rising edge; "
                          "renorm every 5 bars offset=0, equal weight "
                          "min(1/n,0.20) (MA_INVVOL prop 1/std20), capped "
                          "excess to cash; off-grid entries buy the new leg "
                          "only; buys lot-rounded with r251 afford loop, "
                          "renorm targets lot-aligned down, sells "
                          "lot-multiples exact; sells before buys (leg "
                          "order asc); fill-day open/ADV NaN rolls forward; "
                          "PBP=243 (ETF-board family constant)",
            "machine": _machine_id(),
        },
        "panel_face": panel_face,
        "cells": {n: {f: {"stats": cells_out[n][f]["stats"],
                          "n_trades": cells_out[n][f]["n_trades"],
                          "n_entries": cells_out[n][f]["n_entries"],
                          "cost_total": cells_out[n][f]["cost_total"],
                          "rolls": cells_out[n][f]["rolls"],
                          "max_trade_notional":
                              cells_out[n][f]["max_trade_notional"],
                          "min_adv_at_trade":
                              cells_out[n][f]["min_adv_at_trade"],
                          "final_held_n": cells_out[n][f]["final_held_n"],
                          "transitions_head":
                              cells_out[n][f]["transitions_head"]}
                      for f in cells_out[n]} for n in cells_out},
        "nulls": nulls,
        "skill_line": line,
        "d6_correlation": d6,
        "virtual_starts": vstarts,
        "robust": robust,
        "family_pbo": {k: pbo[k] for k in
                       ("pbo", "n_blocks", "n_trials", "n_rows",
                        "n_combinations") if k in pbo},
        "gates": gates,
        "judged_x2_returns_6dp_audit": judged_audit,
        "n_trials": BATCH_CELLS,
        "verdict_line": ("judged per prereg s4: G1'v2 on x2 faces vs "
                         "own-null skill line; judged-negative = slot "
                         "closed + new-evidence reopen note"),
        "audit": {
            "elapsed_sec": round(time.time() - t0, 1),
            "workers": int(nulls.get("workers", 1)),
            "units_expected": BATCH_CELLS,
            "deterministic_sim": "no wall-clock inside sim outputs; "
                                 "double-run identity via selftest",
        },
        "trials_ledger": ledger,
    }
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


# ---------------------------------------------------------------- driver


def cmd_run():
    global SEED
    SEED = SG.SEED_REGISTRY["cn_trend_etf_p1"]
    t0 = time.time()
    P, gates = load_panel()
    if P is None:
        return 2
    os.makedirs(CELL_DIR, exist_ok=True)
    cells_out = {}
    for cell in CELLS:
        name = cell["name"]
        enter_ev, exit_ev = cell_events(P, cell)
        cells_out[name] = {}
        for face, fn in FACES.items():
            ck = os.path.join(CELL_DIR, f"{name}_{face}.json")
            if os.path.exists(ck):
                blob = json.load(open(ck, encoding="utf-8"))
                blob["series"] = np.load(ck.replace(".json", ".npy"))
            else:
                rec = run_portfolio(P, enter_ev, exit_ev,
                                   invvol=cell.get("invvol", False),
                                   trail=cell.get("trail", False),
                                   cost_fn=fn, collect=(face == JUDGED_FACE))
                if not rec["t1_ok"]:
                    print(f"FAIL-CLOSED: T+1 violation in {name}/{face}")
                    return 2
                blob = {"series": rec["returns"],
                        "stats": cell_stats(rec["returns"], P["idx"]),
                        "n_trades": rec["n_trades"],
                        "n_entries": rec["n_entries"],
                        "cost_total": rec["cost_total"],
                        "rolls": rec["rolls"],
                        "max_trade_notional": rec["max_trade_notional"],
                        "min_adv_at_trade": rec["min_adv_at_trade"],
                        "final_held_n": rec["final_held_n"],
                        "transitions_head": rec["transitions_head"]}
                np.save(ck.replace(".json", ".npy"), rec["returns"])
                dump = {k: v for k, v in blob.items() if k != "series"}
                with open(ck + ".tmp", "w", encoding="utf-8") as fh:
                    json.dump(dump, fh, ensure_ascii=False, indent=1)
                os.replace(ck + ".tmp", ck)
                print(f"cell {name}/{face}: sharpe="
                      f"{blob['stats']['sharpe_full']} trades="
                      f"{rec['n_trades']} entries={rec['n_entries']}",
                      flush=True)
        if cells_out[name][JUDGED_FACE]["n_trades"] == 0:
            print(f"VOID: {name} zero trades -- signal machinery broken")
            return 2
        cells_out[name] = {f: cells_out[name][f] for f in ("x1", "x2")}
    nulls = run_nulls(P)
    series_by_cell = {n: cells_out[n][JUDGED_FACE]["series"]
                      for n in cells_out}
    d6 = d6_face(P, series_by_cell)
    vstarts = virtual_starts(P, series_by_cell)
    robust = {n: robust_stats(s) for n, s in series_by_cell.items()}
    panel_face = {
        "T": P["T"], "N": P["N"], "universe": P["syms"],
        "universe_n": len(P["syms"]),
        "sse_cover": round(P["sse_cover"], 4),
        "cover_gaps_postlisting": P["cover_gaps"],
        "duty_cycles_p_leg": [round(float(v), 4) for v in P["p_leg"]],
        "gates": P["gates"],
        "ew_bars": int(len(P["ew_ret"])),
    }
    res = finalize(P, panel_face, cells_out, nulls, d6, vstarts, robust, t0)
    g1_all = [res["gates"][n]["g1_prime_v2"]["pass_v2"]
              for n in res["gates"]]
    print(f"finalize ok: cells={len(res['cells'])} "
          f"ledger={res['trials_ledger']['total']} "
          f"g1_pass={g1_all} "
          f"elapsed={res['audit']['elapsed_sec']}s")
    return 0


# ---------------------------------------------------------------- selftest


def _mk_board(tmp, T=520, n_pass=4):
    """Hermetic synthetic ETF board + probe: N pass legs + crafted rejects
    per filter clause (rows/first/NaN/amount/std)."""
    board = os.path.join(tmp, "daily")
    os.makedirs(board)
    end = pd.Timestamp(EVIDENCE_CUTOFF)
    cal = pd.bdate_range(end=end, periods=T)
    rng = np.random.default_rng(11)
    syms_pass = []
    for i in range(n_pass):
        px = 2.0 + 0.5 * i
        drift = np.cumprod(1.0 + rng.normal(0.0004, 0.012, T))
        close = px * drift
        open_ = close * (1 + rng.normal(0, 0.003, T))
        high = np.maximum(open_, close) * 1.004
        low = np.minimum(open_, close) * 0.996
        vol = np.full(T, 6e6) + rng.random(T) * 2e6
        sym = f"sh5101{i:02d}"
        pd.DataFrame({"date": cal, "open": open_, "high": high,
                      "low": low, "close": close, "volume": vol,
                      "amount": vol * close}).to_csv(
            os.path.join(board, sym + ".csv"), index=False)
        syms_pass.append(sym)
    # reject: rows too short
    sym = "sh500001"
    k = 200
    pd.DataFrame({"date": cal[-k:], "open": np.full(k, 3.0),
                  "high": np.full(k, 3.0), "low": np.full(k, 3.0),
                  "close": np.full(k, 3.0), "volume": np.full(k, 6e6),
                  "amount": np.full(k, 1.8e7)}).to_csv(
        os.path.join(board, sym + ".csv"), index=False)
    # reject: NaN row
    sym = "sh500002"
    df = pd.DataFrame({"date": cal, "open": np.full(T, 3.0),
                       "high": np.full(T, 3.0), "low": np.full(T, 3.0),
                       "close": np.full(T, 3.0), "volume": np.full(T, 6e6),
                       "amount": np.full(T, 1.8e7)})
    df.loc[T // 2, "close"] = np.nan
    df.to_csv(os.path.join(board, sym + ".csv"), index=False)
    # reject: amount too thin
    sym = "sh500003"
    pd.DataFrame({"date": cal, "open": np.full(T, 3.0), "high": np.full(T, 3.0),
                  "low": np.full(T, 3.0), "close": np.full(T, 3.0),
                  "volume": np.full(T, 1e2), "amount": np.full(T, 3e2)}
                 ).to_csv(os.path.join(board, sym + ".csv"), index=False)
    # reject: ann_std ~ 0 (flat cash-like)
    sym = "sh500004"
    pd.DataFrame({"date": cal, "open": np.full(T, 100.0),
                  "high": np.full(T, 100.0), "low": np.full(T, 100.0),
                  "close": np.full(T, 100.0), "volume": np.full(T, 6e6),
                  "amount": np.full(T, 6e8)}).to_csv(
        os.path.join(board, sym + ".csv"), index=False)
    # reject: first too late (> FIRST_MAX rebound)
    sym = "sh500005"
    k = 430
    pd.DataFrame({"date": cal[-k:], "open": np.linspace(3, 4, k),
                  "high": np.linspace(3, 4, k) * 1.01,
                  "low": np.linspace(3, 4, k) * 0.99,
                  "close": np.linspace(3, 4, k),
                  "volume": np.full(k, 6e6),
                  "amount": np.full(k, 2e7)}).to_csv(
        os.path.join(board, sym + ".csv"), index=False)
    probe_path = os.path.join(tmp, "probe.json")
    json.dump({"universe": [{"sym": s} for s in sorted(syms_pass)]},
              open(probe_path, "w"))
    return board, probe_path, sorted(syms_pass), cal


def cmd_selftest():
    global DAILY_DIR, PROBE, OUT_DIR, CELL_DIR, OUT_JSON, OUT_CSV, ATT_JSON
    global UNIVERSE_N_EXPECT, ROWS_MIN, FIRST_MAX, MED_AMT20_MIN, ANN_STD_MIN
    global SSE_COVER_MIN, SEED, K_NULLS, EVIDENCE_CUTOFF, cscv_pbo
    tmp = tempfile.mkdtemp(prefix="cn_trend_selftest_")
    board, probe_path, syms_expect, cal = _mk_board(tmp)
    DAILY_DIR, PROBE = board, probe_path
    OUT_DIR = os.path.join(tmp, "out")
    CELL_DIR = os.path.join(OUT_DIR, "cells")
    OUT_JSON = os.path.join(OUT_DIR, "p1_results.json")
    OUT_CSV = os.path.join(OUT_DIR, "cells_summary.csv")
    ATT_JSON = os.path.join(tmp, "attr.json")
    json.dump({"entries": []}, open(ATT_JSON, "w"))
    UNIVERSE_N_EXPECT = len(syms_expect)
    ROWS_MIN, FIRST_MAX = 300, "2024-12-31"
    MED_AMT20_MIN, ANN_STD_MIN = 1e6, 0.005
    SSE_COVER_MIN = 0.0
    SEED = 20270201
    K_NULLS = 32       # skill_line_v2 null-pool floor is 30 values
    ok = []

    def check(name, cond, detail=""):
        ok.append((name, bool(cond), detail))
        print(f"  [{'PASS' if cond else 'FAIL'}] {name} {detail}")

    # hermetic stubs for repo-state-coupled faces (rev_osc precedent)
    _ne, _pb, _al = SG.n_eff, SG.passive_baseline, SG.append_ledger
    SG.n_eff = lambda bc, rd=None: int(bc)
    SG.passive_baseline = lambda pool, rd=None: 0.4606
    SG.append_ledger = lambda *a, **k: {"prev_total": 0, "total": 100,
                                        "batch": BATCH_NAME}
    _cp = cscv_pbo
    cscv_pbo = lambda mat: {"pbo": 0.1}       # 1-cell fixture: PBO not
    _lr = None                                # under test here (rev_osc [15])
    try:
        # [1] panel gates: universe re-derive + probe cross-check + rejects
        P, gates = load_panel()
        check("[1] panel loads, universe == crafted pass set",
              P is not None and P["syms"] == syms_expect,
              f"n={0 if P is None else P['N']}")
        T, N = P["T"], P["N"]

        # [2] MA edge + gate entry-filter semantics
        enter, exit_ = cell_events(P, CELLS[0])
        j = 0
        col = P["close"][:, j]
        ml = P["ma_long"][:, j]
        rises = np.flatnonzero(enter[:, j])
        check("[2] MA entry = rising edges of ma_long",
              all(ml[t] and not ml[t - 1] for t in rises))
        enter_dg, _ = cell_events(P, CELLS[1])
        # leg MA200 undefined early -> no gated entries before bar 200
        check("[2b] MA_DUAL fail-closed while MA200 undefined",
              not enter_dg[:200, :].any())

        # [3] Donchian latch: one entry per episode, held through new highs
        ent, ext = cell_events(P, CELLS[4])
        for jj in range(N):
            ev = np.flatnonzero(ent[:, jj])
            xv = np.flatnonzero(ext[:, jj])
            if len(ev) and len(xv):
                assert all(xv[i] < ev[i + 1] for i in range(min(len(ev),
                                                                len(xv)) - 1))
        check("[3] DON latch exits before re-entries", True)

        # [3b] MA_TRAIL stop: 15% drawdown from holding-peak fires the exit
        #      and NO re-entry while ma_long stays true (single-leg ctx)
        Tk = 300
        close = np.full((Tk, 1), 100.0)
        close[60:120, 0] = np.linspace(100.0, 130.0, 60)   # ramp -> MA long
        close[120:123, 0] = [120.0, 112.0, 109.0]          # -16% off peak
        close[123:, 0] = 109.0
        ctx1 = {"T": Tk, "N": 1, "open": np.vstack([close[1:], close[-1]]),
                "close": close, "close_ff": close,
                "adv_arg": np.full((Tk, 1), 1e9), "std20": None}
        ma20k = pd.Series(close[:, 0]).rolling(20, min_periods=20).mean()
        ma60k = pd.Series(close[:, 0]).rolling(60, min_periods=60).mean()
        ml = np.asarray((ma20k > ma60k) & ma20k.notna() & ma60k.notna(),
                        bool)[:, None]
        prev = np.vstack([np.zeros((1, 1), bool), ml[:-1]])
        rt = run_portfolio(ctx1, ml & ~prev, ~ml & prev, trail=True,
                           cost_fn=side_cost_x2, collect=True)
        sells = [tr for tr in rt["transitions_head"]
                 if tr["side"] == "sell"]
        check("[3b] trail exit fires on 15% peak drawdown",
              rt["final_held_n"] == 0 and len(sells) >= 1
              and sells[-1]["day"] < 130,
              f"sells={len(sells)} last={sells[-1]['day'] if sells else '-'}")
        check("[3b2] no re-entry while ma_long stays true",
              rt["n_entries"] == 1)

        # [4] T+1 + afford + lot integrity on tiny capital
        global CAPITAL
        saved_cap = CAPITAL
        CAPITAL = 3_000.0
        rec = run_portfolio(P, enter, exit_, invvol=False, trail=False,
                            cost_fn=side_cost_x2, collect=True)
        CAPITAL = saved_cap
        check("[4a] T+1 asserted", rec["t1_ok"])
        check("[4b] trades executed under tiny capital",
              rec["n_trades"] >= 1 and rec["n_entries"] >= 0)
        bad = [tr for tr in rec["transitions_head"]
               if tr["shares"] % LOT != 0]
        check("[4c] all fills lot-multiples", not bad)

        # [5] 20% cap: 2 active legs -> 20% each, residual cash
        act = np.zeros((T, N), bool)
        act[:, 0] = True
        act[:, 1] = True
        prev = np.vstack([np.zeros((1, N), bool), act[:-1]])
        ent2 = act & ~prev
        rec2 = run_portfolio(P, ent2, ~act & prev, cost_fn=side_cost_x2,
                             collect=False)
        eq = np.cumprod(1.0 + np.nan_to_num(rec2["returns"][1:]))
        # with 2 legs capped at 20% each, portfolio vol <= 0.4x leg vol
        leg_vol = np.nanstd(np.diff(np.log(P["close_ff"][:, 0])) )
        port_vol = np.nanstd(rec2["returns"][1:])
        check("[5] cap 20%: 2-leg portfolio vol < single-leg vol",
              port_vol < leg_vol, f"p={port_vol:.5f} l={leg_vol:.5f}")

        # [6] determinism: double-run identity (equal_nan r255 law)
        r1 = run_portfolio(P, enter, exit_, cost_fn=side_cost_x2)
        r2 = run_portfolio(P, enter, exit_, cost_fn=side_cost_x2)
        check("[6] deterministic double-run identity",
              bool(np.array_equal(r1["returns"], r2["returns"],
                                  equal_nan=True))
              and r1["n_trades"] == r2["n_trades"])

        # [7] null machinery: deterministic, finite, p in (0,1)
        n1 = run_nulls(P)
        n2 = run_nulls(P)
        check("[7a] nulls deterministic (double-run identity)",
              n1["values"] == n2["values"])
        check("[7b] null coverage finite + count",
              n1["coverage"]["n_values"] == K_NULLS
              and all(np.isfinite(v) for v in n1["values"]))
        check("[7c] duty cycles in (0,1]",
              all(0.0 < v < 1.0 for v in P["p_leg"]))

        # [8] census + splits structure (REV_OSC s2.1/s2.3 family face)
        vs = virtual_starts(P, {"MA_BASE": r1["returns"]})
        check("[8] census n_starts == T-126-200",
              vs["n_starts"] == T - WIN_DAYS - STARTS_FROM,
              f"{vs['n_starts']}")
        check("[8b] splits + walk-forward present",
              "split_sign_agreement_pct" in vs["cells"]["MA_BASE"]
              and len(vs["cells"]["MA_BASE"]["walk_forward_sharpe"]) == 5)

        # [9] robust dual p values in [0,1]
        rb = robust_stats(r1["returns"])
        check("[9] robust p faces in [0,1]",
              0.0 <= rb["sign_flip_p"] <= 1.0
              and 0.0 <= rb["block_bootstrap_p_le_0"] <= 1.0)

        # [10] D6 real path: identical series -> |corr| 1 -> reject;
        #      value-reversed (same index) -> no reject (cn_rev_tilt
        #      d6_block verbatim; iloc[::-1] preserves pairs = trap)
        s = pd.Series(np.asarray(r1["returns"], float)[1:],
                      index=P["idx"][1:])
        twin = d6_block(s, {"TRADER-X": s.copy()})
        rev_vals = pd.Series(s.to_numpy()[::-1], index=s.index)
        ortho = d6_block(s, {"TRADER-Y": rev_vals})
        check("[10] D6 twin reject / ortho no-reject",
              bool(twin["member_face"]["reject"]) is True
              and bool(ortho["member_face"]["reject"]) is False)

        # [11] gates wiring smoke (stubbed line faces, hermetic)
        g1 = SG.g1_prime_v2(1.2, s, batch_cells=10, pool="core48",
                            null_pool={"values": n1["values"],
                                       "coverage": n1["coverage"]},
                            n_trades=100, n_entries=100)
        check("[11] g1 dict face with skill_line",
              "skill_line" in g1 and "pass_v2" in g1)

        # [12] finalize product on synthetic (trials_ledger r252 + entries
        #      r248 + cutoff meta)
        stats = cell_stats(r1["returns"], P["idx"])
        cells_out = {}
        for cname in ("MA_BASE", "MA_DUAL"):   # >=2 series: align_returns
            cells_out[cname] = {                 # contract (real fn under
                f: {"series": r1["returns"], "stats": stats,
                    "n_trades": r1["n_trades"], "n_entries": r1["n_entries"],
                    "cost_total": r1["cost_total"], "rolls": r1["rolls"],
                    "max_trade_notional": r1["max_trade_notional"],
                    "min_adv_at_trade": r1["min_adv_at_trade"],
                    "final_held_n": r1["final_held_n"],
                    "transitions_head": r1["transitions_head"]}
                for f in ("x1", "x2")}
        d6 = d6_block(s, {"TRADER-X": s.copy()})
        d6w = {"cells": {c: d6 for c in cells_out}, "member_cutoffs": {},
               "prior_negative_advisory": {},
               "same_batch_cross": {}, "reject_line": D6_REJECT,
               "members": []}
        res = finalize(P, {"T": T, "N": N}, cells_out, n1, d6w,
                       {"n_starts": 1, "segments": {}, "cells": {}},
                       {"MA_BASE": rb}, time.time())
        check("[12] finalize product + trials_ledger key law",
              os.path.exists(OUT_JSON)
              and "trials_ledger" in res
              and res["evidence_cutoff"] == EVIDENCE_CUTOFF
              and "cutoff_meta" in res)
        att = json.load(open(ATT_JSON, encoding="utf-8"))
        check("[12b] attrition row in entries (r248)",
              len(att["entries"]) == 1
              and att["entries"][0]["batch"] == BATCH_NAME)
    finally:
        SG.n_eff, SG.passive_baseline, SG.append_ledger = _ne, _pb, _al
        cscv_pbo = _cp
        shutil.rmtree(tmp, ignore_errors=True)

    n_ok = sum(1 for _, v, _ in ok if v)
    print(f"cn_trend_etf_p1 selftest: {n_ok}/{len(ok)} PASS")
    for name, v, d in ok:
        if not v:
            print(f"  FAIL: {name} {d}")
    return 0 if n_ok == len(ok) else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "selftest"])
    a = ap.parse_args()
    if a.cmd == "selftest":
        return cmd_selftest()
    if os.path.exists(OUT_JSON) and \
            os.environ.get("CN_TREND_ETF_P1_REFINALIZE") != "1":
        print("idempotent no-op: p1_results.json exists "
              "(CN_TREND_ETF_P1_REFINALIZE=1 = only redo)")
        return 0
    return cmd_run()


if __name__ == "__main__":
    sys.exit(main())
