"""CN_SOE_ETF_P1 runner -- zhongtegu/SOE central-enterprise ETF sleeve
judged batch (T-2026-09-26-87 s2 queue #2, SCHOOL_SUPPLY_S1.md sec.2).

Laws (frozen in research/CN_SOE_ETF_PREREG.md @commit ba54b43f -- R99:
prereg freeze precedes runner build precedes ANY run; seed registered
at the freeze commit, SEED_REGISTRY['cn_soe_etf_p1'] = 20272301, band
20272301..20274300 collision-free by construction).

  panel   data/basic/etf_list.csv NAME FACE (name contains 央企|国企,
          excluding 港|恒生 HK faces) -> data/daily board clauses on the
          D2 lockbox face (truncate-to-cutoff load, R280 zero-run
          amendment): first<=2021-12-31 AND rows>=1100 AND
          last==2026-09-22 AND OHLCV zero-NaN AND MED_AMT20>=5e6
          (BATCH-SPECIFIC thin-sleeve gate; the 5e7 family gate would
          zero this face -- prereg s2 frozen). Universe re-derive MUST
          equal the frozen 8-member roster (fail-closed exit 2,
          probe cross-check = prereg s2 table):
          510810/512950/512960/515600/515900/159719/517090/517180.
          2023+ pure-zhongtegu cohort = IS-depth honest exclusion
          (prereg), forward-watch only, zero judged claim.
  sleeve  staggered: per leg warmup=200 OWN bars (union-calendar
          availability mask, listing lag honest); sleeve EW daily
          returns of available legs; sleeve index = cumprod from 1.0
          at the first available leg's warmup end (first accrual day =
          warmup-end next day); aggregate-gate cells (HOLD_MA200 /
          REPAIR) eval start = index age>=200 bars AND available
          legs>=3; per-leg cells evaluate each leg from its own
          warmup end. Passive baseline for the census beat face =
          this sleeve staggered EW series (prereg s2, in-batch
          derive).
  cells   (prereg s3.1 frozen, zero in-batch optimization)
          SOE_HOLD      per-leg staggered entry at warmup end, hold,
                        21d renorm-only, no gate no exit (F6 trade
                        gate structurally tight: entries==8, prereg s5
                        prediction 2 = honest judged-negative path).
          SOE_HOLD_MA200 policy-bottom gate on the SLEEVE INDEX:
                        STATE semantics -- position follows the
                        index>MA200 regime (entry at eval start if the
                        gate is already open, then rising edges;
                        break below -> ALL cash). Full available
                        sleeve, weights min(1/n_active, 0.20).
          SOE_LEGMA200  per-leg state on leg close>leg MA200 from the
                        leg's warmup end (entry if open at warmup
                        end, rising edges re-enter; per-leg break ->
                        that leg to cash).
          SOE_REPAIR    deep-drawdown repair: sleeve index 252d
                        rolling-high drawdown crossing to <=-20% ->
                        enter full available sleeve (crossing =
                        dd[t-1] finite > -0.20 AND dd[t] <= -0.20;
                        undefined dd face = fail-closed no entry);
                        hold; exit when the index makes a 63d closing
                        high (close > max of prior 63 closes) -> all
                        out; latch resets (re-entry needs a fresh
                        crossing).
          SOE_LOWVOL3   every 63 bars (offset=0) select the 3
                        available legs with the lowest 60d return std
                        (min(3, available) honest); membership-change
                        events at grid points only; weights
                        min(1/n_selected, 0.20) -> with 3 selected the
                        20% concentration cap leaves 40% cash (frozen
                        cap clause, no redistribution, disclosed).
  weights renorm every 21 union-calendar bars (offset=0) to equal
          weight min(1/n_active, W_CAP=0.20); capped excess to CASH;
          off-grid entries (staggered warmup / aggregate-gate state
          entries) buy the new legs only at the same capped rule;
          between events shares constant (anti-churn family
          semantics). Cash zero-yield.
  fills   signal/decision at close t -> fills at open t+1 (T+1
          asserted per order, R240 law). Sells first then buys, leg
          order asc (deterministic). Buys lot-rounded
          (knowledge.rules.min_lot single source) with the r251
          afford loop (trial notional -> cost -> notional+cost <=
          cash else lot down); renorm targets lot-aligned DOWN; sell
          exact-share lot-multiples; fill-day open/ADV NaN -> roll
          forward (honest: legs list 2016..2021, ADV warmup rolls
          apply to every draw alike).
  costs   V2 ADV20-tiered per side, single source alloc_backtest
          (side_cost_v2 / side_cost_x2); judged face = x2 ALWAYS ON
          (CN-* family precedent), x1 = disclosure column. ADV20 =
          mean(vol*close, 20) through close t-1. Thin-sleeve capacity
          note: MED_AMT20 4.9M-19.9M -> x2 costs bite (prereg s0
          honest note; 8-digit capital NOT scalable = disclosed
          non-defect).
  nulls   K=2000 same-mask random activations (RANDOM_LARGE_SAMPLE_LAW
          s3): per leg, weekly grid (every 5th bar) Bernoulli(p = that
          leg's SOE_LEGMA200 duty cycle -- the per-leg activation cell
          of this batch; SOE_HOLD duty is degenerate 1.0) -> random
          long/flat paths, SAME universe, SAME execution machinery
          (21d renorm), SAME x2 cost face; seed = 20272301+k, k<2000
          (declared band); null Sharpe values -> own null_pool for
          skill_line_v2/g1_prime_v2. Dual robust p values: block
          bootstrap 2000 draws (block=10d) + sign-flip 2000 draws per
          judged cell.
  starts  full-census virtual starts t0 in [200, T-126), 126d
          windows, strategy vs the sleeve staggered-EW passive proxy
          (prereg s2); 4 segment classes (bull/bear/deep_bear/chop by
          sse level, MA200, 60d return -- REV_OSC s2.1 frozen rule
          verbatim); segment n<500 = insufficient-sample honest note;
          >=100 random train/val splits (sign agreement) +
          walk-forward 5 sequential folds (law s2.3).
  gates   G1'v2 = science_gates.g1_prime_v2(sharpe_full, returns,
          batch_cells=2005, pool='core48', n_trades, n_entries,
          null_pool=own 2000) on the 5 judged x2 cells; G2 =
          g2_registration_v2(g1_pass, dsr, pbo) with DSR =
          deflated_sharpe_ratio on RAW daily returns (n_trials=
          line.n_eff, var_null_sr = null sigma^2) and family PBO =
          screening/pbo.cscv_pbo CSCV-8 over the 5-cell x2 matrix.
          Batch descriptive clauses: annualized>0 AND OOS (>=
          IS_END+1 = 2025-01-01, composite_ic shared split) dual
          positive AND maxDD >= -35%. D6 reject face = max|corr| vs
          the 6 registered CE members (cn_rev_tilt_p1 ew6 canon,
          tuple-unpack r280 amendment) >= 0.7; same-batch pairwise
          disclosure. Advisory-only cross legs (prior-negative
          families are NEVER admission faces): CN-DIV-LOWVOL-ROT
          judged cells via DATED reconstruction (their panel calendar
          = INTERSECTION of sh510880/sh512890 dates truncated at
          cutoff, cn_div_lowvol_rot_p1.py loader-verbatim; value-list
          positional alignment without dates would be dishonest --
          calendar is reconstructed and length-verified against their
          panel_gates.T before any corr) + CN_TREND_ETF_P1 judged
          cells (union calendar of their frozen universe; artifact
          absent while in-flight -> honest status, prereg s1
          post-landing backfill leg).
  ledger  science_gates.append_ledger('CN_SOE_ETF_P1', 2005,
          'cn_soe_etf_p1', evidence_cutoff='2026-09-22') single-shot
          at finalize; artifact block under the canonical
          trials_ledger key (r252 law); attrition row lands in the
          ENTRIES list (r248).

Products (prereg s6): results/cn_soe_ETF/p1_results.json (top-level
evidence_cutoff + cutoff_meta + D6 + judged readouts + nulls + census
+ splits + gates + ledger block) + cells/*.json|npy per-cell idempotent
checkpoints (cross-round pool resume) + cells_summary.csv. N_eff =
2005 (5 judged cells + 2000 nulls; x1 disclosure faces not on the D1
bill, family CN-TREND-ETF precedent).

Usage: run | selftest   (exit 0 ok; 2 = fail-closed gate/mechanism
refusal)

Build notes (r286 law family): all dump sites numpy-native-coerced
via _jsonable; the cells_out assembly glue lives in _compute_cells
(assignment in BOTH branches) and is selftest-exercised (leg [14]) --
component greens are not driver greens.
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
PREREG = os.path.join(ROOT, "research", "CN_SOE_ETF_PREREG.md")
ETF_LIST = os.path.join(ROOT, "data", "basic", "etf_list.csv")
DAILY_DIR = os.path.join(ROOT, "data", "daily")
OUT_DIR = os.path.join(ROOT, "results", "cn_soe_ETF")
CELL_DIR = os.path.join(OUT_DIR, "cells")
OUT_JSON = os.path.join(OUT_DIR, "p1_results.json")
OUT_CSV = os.path.join(OUT_DIR, "cells_summary.csv")
ATT_JSON = os.path.join(ROOT, "results", "gate_attrition.json")

EVIDENCE_CUTOFF = "2026-09-22"                  # prereg s2 D2 lockbox
FROZEN_EIGHT = ("sh510810", "sh512950", "sh512960", "sh515600",
                "sh515900", "sz159719", "sh517090", "sh517180")
ROWS_MIN = 1100                                 # prereg s2 frozen clauses
FIRST_MAX = "2021-12-31"
MED_AMT20_MIN = 5e6                              # batch-specific thin gate
SSE_COVER_MIN = 0.95
BATCH_NAME = "CN_SOE_ETF_P1"
BATCH_CELLS = 2005                               # 5 judged + 2000 nulls
K_NULLS = 2000
SEED = None          # filled at run from SG.SEED_REGISTRY (freeze commit)
PBP = 243.0          # ETF-board trading bars/year (CN-* family constant)
CAPITAL = 1_000_000.0                            # CN-* paper spec
LOT = int(krules.min_lot("510300"))              # 100 shares (single source)
W_CAP = 0.20                                     # single-leg weight cap
WARMUP = 200                                     # per-leg own-bars warmup
AGG_AGE_MIN = 200                                 # sleeve-index age gate
AGG_LEGS_MIN = 3                                  # available-legs gate
MA_WIN = 200                                     # leg MA200 face
REBAL_STEP = 21                                   # renorm grid, offset=0
SELECT_STEP = 63                                  # LOWVOL3 re-selection grid
LOWVOL_N = 3                                      # lowest-std selection size
STD_WIN = 60                                     # LOWVOL3 return-std window
REPAIR_DD_WIN = 252                              # rolling-high window
REPAIR_DD = 0.20                                 # drawdown entry line
REPAIR_HI_WIN = 63                                # closing-new-high exit
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
    {"name": "SOE_HOLD"},
    {"name": "SOE_HOLD_MA200"},
    {"name": "SOE_LEGMA200"},
    {"name": "SOE_REPAIR"},
    {"name": "SOE_LOWVOL3"},
]

# prior-negative family cross faces (advisory disclosure only; closed
# families are never admission faces -- prereg s1)
DIV_ARTIFACT = os.path.join(ROOT, "results/cn_div_lowvol_rot/p1_results.json")
DIV_LEGS = ("sh510880", "sh512890")              # cn_div_lowvol_rot_p1 LEGS
TREND_ARTIFACT = os.path.join(ROOT, "results/cn_trend_ETF/p1_results.json")


def _machine_id():
    try:
        return json.load(open(os.path.join(
            ROOT, "fleet", "machine.json"), encoding="utf-8"))["machine_id"]
    except Exception:
        return "unknown"


# ---------------------------------------------------------------- panel


def name_face():
    """etf_list name face: name contains 央企|国企, excluding 港|恒生."""
    d = pd.read_csv(ETF_LIST, encoding="utf-8-sig")
    code_col, name_col = d.columns[0], d.columns[1]
    names = d[[code_col, name_col]].dropna()
    code_s = names[code_col].astype(str).str.strip()
    name_s = names[name_col].astype(str)
    keep = name_s.str.contains("央企|国企", na=False) \
        & ~name_s.str.contains("港|恒生", na=False)
    return sorted(code_s[keep].tolist())


def _leg_filter_face(df):
    """Frozen board clauses on ONE truncated leg frame (lockbox face)."""
    close = df["close"]
    vol = df["volume"]
    amt20 = (vol * close).rolling(20).median().dropna()
    med20 = float(amt20.median()) if len(amt20) else 0.0
    return {
        "rows_ok": len(df) >= ROWS_MIN,
        "first_ok": str(df["date"].iloc[0])[:10] <= FIRST_MAX,
        "last_ok": str(df["date"].iloc[-1])[:10] == EVIDENCE_CUTOFF,
        "nan_free": int(df.isna().sum().sum()) == 0,
        "amount_ok": med20 >= MED_AMT20_MIN,
        "med_amount20_cny": round(med20, 0),
    }


def load_panel():
    """Truncate-to-cutoff load + name-face universe re-derive + gates.

    Fail-closed (prereg s6): re-derive MUST equal the frozen 8-member
    roster; lockbox face last==2026-09-22 zero-NaN; sse cover>=0.95.
    """
    cut = pd.Timestamp(EVIDENCE_CUTOFF)
    cands = name_face()
    legs = {}
    passed = []
    outs = {"no_board": [], "clause": []}
    for sym in cands:
        f = os.path.join(DAILY_DIR, sym + ".csv")
        if not os.path.exists(f):
            outs["no_board"].append(sym)
            continue
        d = pd.read_csv(f)
        d.columns = [str(c).lower() for c in d.columns]
        d["date"] = pd.to_datetime(d["date"])
        d = d[d["date"] <= cut].reset_index(drop=True)   # D2 lockbox
        if not len(d):
            outs["clause"].append({"sym": sym, "reason": "empty_after_cut"})
            continue
        face = _leg_filter_face(d)
        bad = [k for k in ("rows_ok", "first_ok", "last_ok", "nan_free",
                           "amount_ok") if not face[k]]
        if bad:
            outs["clause"].append({"sym": sym, "reason": bad,
                                   "med_amount20_cny": face["med_amount20_cny"]})
            continue
        legs[sym] = d
        passed.append(sym)
    passed.sort()
    gates = {
        "universe_n_ok": len(passed) == len(FROZEN_EIGHT),
        "roster_cross_ok": passed == sorted(FROZEN_EIGHT),
        "name_face_n": len(cands),
    }
    if not all(gates[k] for k in ("universe_n_ok", "roster_cross_ok")):
        print(f"FAIL-CLOSED: universe gates red {gates} "
              f"derive={passed} -- no artifact")
        return None, gates

    cand = passed
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

    # -- returns + per-leg faces (union-calendar, NaN-aware)
    rets = np.full_like(close_m, np.nan)
    with np.errstate(invalid="ignore"):
        rets[1:] = close_m[1:] / close_m[:-1] - 1.0
    ma200 = pd.DataFrame(close_m).rolling(MA_WIN,
                                          min_periods=MA_WIN).mean().to_numpy(float)
    with np.errstate(invalid="ignore"):
        leg_gate = (close_m > ma200) & np.isfinite(close_m) \
            & np.isfinite(ma200)
    std60 = pd.DataFrame(rets).rolling(STD_WIN,
                                       min_periods=STD_WIN).std().to_numpy(float)
    adv_arg = pd.DataFrame(vol_m * close_m).rolling(20,
                                                    min_periods=20).mean() \
        .shift(1).to_numpy(float)              # ADV20 through close t-1

    # -- staggered availability (WARMUP own bars) + sleeve EW face
    fin_close = np.isfinite(close_m)
    avail = np.zeros((T, N), bool)
    for j in range(N):
        cs = np.cumsum(fin_close[:, j])
        avail[:, j] = cs >= WARMUP
    avail_start = np.array([int(np.argmax(avail[:, j])) if avail[:, j].any()
                            else T for j in range(N)])
    n_avail = avail.sum(axis=1)
    t_sleeve0 = int(np.argmax(n_avail > 0)) if (n_avail > 0).any() else T
    with np.errstate(invalid="ignore"):
        a_fin = avail & np.isfinite(rets)
        n_a = a_fin.sum(axis=1)
        ew_full = np.where(n_a > 0,
                           np.where(a_fin, rets, 0.0).sum(axis=1)
                           / np.maximum(n_a, 1), 0.0)
    idx_close = np.full(T, np.nan)
    if t_sleeve0 < T:
        idx_close[t_sleeve0] = 1.0            # base at warmup-end close
        for t in range(t_sleeve0 + 1, T):
            idx_close[t] = idx_close[t - 1] * (1.0 + ew_full[t])
    idx_s = pd.Series(idx_close)
    idx_ma200 = idx_s.rolling(MA_WIN, min_periods=MA_WIN).mean().to_numpy(float)
    idx_age = np.arange(T) - t_sleeve0
    agg_start = int(np.argmax((idx_age >= AGG_AGE_MIN)
                             & (n_avail >= AGG_LEGS_MIN)))
    if not ((idx_age >= AGG_AGE_MIN) & (n_avail >= AGG_LEGS_MIN)).any():
        agg_start = T
    hi252 = idx_s.rolling(REPAIR_DD_WIN,
                          min_periods=REPAIR_DD_WIN).max().to_numpy(float)
    with np.errstate(invalid="ignore"):
        dd252 = idx_close / hi252 - 1.0
    prev63 = idx_s.rolling(REPAIR_HI_WIN,
                           min_periods=REPAIR_HI_WIN).max() \
        .shift(1).to_numpy(float)

    # -- LEGMA200 per-leg duty cycles (null Bernoulli p, prereg s2)
    p_leg = np.zeros(N)
    for j in range(N):
        col = avail[:, j] & np.isfinite(close_m[:, j]) & np.isfinite(ma200[:, j])
        p_leg[j] = float(leg_gate[:, j][col].mean()) if col.any() else 0.0

    gates["sse_cover_ok"] = cover >= SSE_COVER_MIN
    gates["T_sanity_ok"] = T >= ROWS_MIN
    gates["sleeve_start_ok"] = t_sleeve0 < T and agg_start < T
    if not all(gates[k] for k in ("sse_cover_ok", "T_sanity_ok",
                                  "sleeve_start_ok")):
        print(f"FAIL-CLOSED: panel gates red {gates}")
        return None, gates

    return {
        "idx": idx, "days": idx, "syms": cand, "T": T, "N": N,
        "open": open_m, "close": close_m, "close_ff": close_ff,
        "adv_arg": adv_arg, "rets": rets,
        "ma200": ma200, "leg_gate": leg_gate, "std60": std60,
        "avail": avail, "avail_start": avail_start, "n_avail": n_avail,
        "ew_full": ew_full, "sleeve_idx": idx_close, "idx_ma200": idx_ma200,
        "idx_age": idx_age, "agg_start": agg_start,
        "dd252": dd252, "prev63": prev63,
        "sse": sse_v, "sse_ma200": sse_ma200,
        "p_leg": p_leg, "sse_cover": cover, "cover_gaps": cover_gaps,
        "universe_outs": outs,
        "gates": gates,
    }, gates


# ---------------------------------------------------------------- events


def cell_events(P, cell):
    """(enter_ev, exit_ev) boolean (T,N) matrices per frozen cell spec."""
    T, N = P["T"], P["N"]
    avail = P["avail"]
    name = cell["name"]
    enter = np.zeros((T, N), bool)
    exit_ = np.zeros((T, N), bool)

    if name == "SOE_HOLD":
        for j in range(N):
            t0 = int(P["avail_start"][j])
            if t0 < T:
                enter[t0, j] = True
        return enter, exit_

    if name == "SOE_LEGMA200":
        gate = P["leg_gate"]
        for j in range(N):
            t0 = int(P["avail_start"][j])
            if t0 >= T:
                continue
            if gate[t0, j]:                       # state entry at warmup end
                enter[t0, j] = True
            g_prev = gate[t0, j]
            for t in range(t0 + 1, T):
                g = gate[t, j]
                if g and not g_prev:
                    enter[t, j] = True
                elif (not g) and g_prev:
                    exit_[t, j] = True
                g_prev = g
        return enter, exit_

    if name == "SOE_HOLD_MA200":
        gate = (P["sleeve_idx"] > P["idx_ma200"]) \
            & np.isfinite(P["sleeve_idx"]) & np.isfinite(P["idx_ma200"])
        a0 = int(P["agg_start"])
        if a0 >= T:
            return enter, exit_
        if gate[a0]:                              # state entry at eval start
            enter[a0, :] = avail[a0, :]
        g_prev = gate[a0]
        for t in range(a0 + 1, T):
            g = gate[t]
            if g and not g_prev:
                enter[t, :] = avail[t, :]
            elif (not g) and g_prev:
                exit_[t, :] = avail[t, :]
            g_prev = g
        return enter, exit_

    if name == "SOE_REPAIR":
        dd = P["dd252"]
        hi63 = P["prev63"]
        close_i = P["sleeve_idx"]
        a0 = int(P["agg_start"])
        in_rep = False
        for t in range(a0, T):
            d_t = dd[t]
            d_prev = dd[t - 1] if t > 0 else np.nan   # no negative-index wrap
            crossing = (np.isfinite(d_t) and np.isfinite(d_prev)
                        and d_t <= -REPAIR_DD and d_prev > -REPAIR_DD)
            new_high = (np.isfinite(close_i[t]) and np.isfinite(hi63[t])
                        and close_i[t] > hi63[t])
            if not in_rep and crossing:
                enter[t, :] = avail[t, :]
                in_rep = True
            elif in_rep and new_high:
                exit_[t, :] = avail[t, :]
                in_rep = False
        return enter, exit_

    if name == "SOE_LOWVOL3":
        std60 = P["std60"]
        prev_sel = set()
        for t in range(0, T, SELECT_STEP):
            cand_j = [j for j in range(N)
                      if avail[t, j] and np.isfinite(std60[t, j])]
            cand_j.sort(key=lambda j: (float(std60[t, j]), j))
            sel = set(cand_j[:LOWVOL_N])
            for j in sel - prev_sel:
                enter[t, j] = True
            for j in prev_sel - sel:
                exit_[t, j] = True
            prev_sel = sel
        return enter, exit_

    raise ValueError(f"unknown cell {name}")


# ---------------------------------------------------------------- engine


def run_portfolio(ctx, enter_ev, exit_ev, cost_fn=None, collect=False,
                  rebal_step=None):
    """Event-driven multi-leg sleeve engine (prereg s2 frozen semantics).

    Decisions at close t -> fills at open t+1 (T+1 asserted per order).
    Sells first then buys, leg order asc (deterministic). Buys
    lot-rounded with the r251 afford loop; renorm targets lot-aligned
    down; cash zero-yield; fill-day open/ADV NaN -> roll forward.
    """
    if cost_fn is None:
        cost_fn = side_cost_x2
    if rebal_step is None:
        rebal_step = REBAL_STEP
    T, N = ctx["T"], ctx["N"]
    O, C = ctx["open"], ctx["close"]
    Cff, adv = ctx["close_ff"], ctx["adv_arg"]
    days = ctx.get("days")
    held = np.zeros(N, bool)
    shares = np.zeros(N, float)
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

    def _fill_px(t, j):
        px = O[t, j]
        a = adv[t, j]
        if not (np.isfinite(px) and np.isfinite(a) and a > 0):
            return None, None
        return float(px), float(a)

    def _buy(t, j, px, a, target_val):
        """Lot-rounded afford loop (r251: cost reserved before cash leaves)."""
        nonlocal cash, shares, n_trades, cost_total
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
        nonlocal cash, shares, n_trades, cost_total
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
                if not _sell(t, j, px, a, nsh):
                    pending.setdefault(t + 1, []).append((kind, j, w, sig))
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
        for j in np.flatnonzero(exits):
            pending.setdefault(t + 1, []).append(("sell_all", j, 0.0, t))
            held[j] = False
        entries = enter_ev[t] & ~held
        e_idx = np.flatnonzero(entries)
        if t % rebal_step == 0:
            active = held.copy()
            active[e_idx] = True
            n_act = int(active.sum())
            if n_act:
                w = {j: min(1.0 / n_act, W_CAP)
                     for j in np.flatnonzero(active)}
                for j in np.flatnonzero(active):
                    pending.setdefault(t + 1, []).append(
                        ("set", j, w[j], t))
        elif e_idx.size:
            n_after = int(held.sum()) + int(e_idx.size)
            w = {j: min(1.0 / n_after, W_CAP) for j in e_idx}
            for j in e_idx:
                pending.setdefault(t + 1, []).append(("buy", j, w[j], t))
            held[e_idx] = True
        if t % rebal_step == 0 and e_idx.size:
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
    """One same-mask random-activation null draw (prereg s2, seed band)."""
    ctx = _NULL_CTX
    T, N = ctx["T"], ctx["N"]
    rng = np.random.default_rng(ctx["seed_base"] + k)
    n_grid = int(math.ceil(T / 5))            # weekly grid (family face)
    draws = rng.random((n_grid, N)) < ctx["p_leg"][None, :]
    states = np.repeat(draws, 5, axis=0)[:T]
    prev = np.vstack([np.zeros((1, N), bool), states[:-1]])
    enter = states & ~prev
    exit_ = ~states & prev
    rec = run_portfolio(ctx, enter, exit_, cost_fn=side_cost_x2,
                        collect=False, rebal_step=REBAL_STEP)
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
    out = run_cells_parallel(jobs, workers=4, desc="cn_soe nulls",
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
                "cn_soe_etf_p1: K=2000 per-leg weekly-grid Bernoulli("
                "p=SOE_LEGMA200 per-leg duty cycle, the batch's per-leg "
                "activation cell; SOE_HOLD duty is degenerate 1.0) random "
                "long/flat sleeves, same universe same execution (21d "
                "renorm) same x2 cost face, seed 20272301+k k<2000 "
                "(declared band)"],
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
    rule family face). Passive proxy = sleeve staggered EW (prereg s2)."""
    T = P["T"]
    starts = list(range(STARTS_FROM, T - WIN_DAYS))
    segs = np.array([seg_class(P, t0) for t0 in starts])
    sa = np.array(starts)
    ew = np.asarray(P["ew_full"], float)
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
    """Block bootstrap (block=10d) + sign-flip, 2000 draws each (s2)."""
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
    pairwise."""
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
    return d6


def _calendar(kind, leg_syms, cut):
    """Dated-calendar reconstruction from the raw board (loader-verbatim
    per family runner: intersection for DIV, union for CN-TREND)."""
    sets = []
    for s in leg_syms:
        f = os.path.join(DAILY_DIR, s + ".csv")
        if not os.path.exists(f):
            return None
        dts = pd.to_datetime(pd.read_csv(f, usecols=["date"])["date"])
        sets.append(set(dts))
    if kind == "intersection":
        days = set.intersection(*sets)
    else:
        days = set.union(*sets)
    days = pd.DatetimeIndex(sorted(d for d in days if d <= cut))
    return days if len(days) >= 2 else None


def _family_cross(P, series_by_cell, fam, art_path, cal_kind, leg_syms):
    """Advisory-only cross leg vs a prior-negative family's judged cells,
    via DATED reconstruction (positional value lists without dates would
    be dishonest -- calendar is rebuilt from the raw board and
    length-verified against the artifact's own T before any corr)."""
    out = {"family": fam, "face": "advisory_disclosure_only"}
    if not os.path.exists(art_path):
        out["status"] = "artifact_absent"
        return out
    try:
        art = json.load(open(art_path, encoding="utf-8"))
        audit = art.get("judged_x2_returns_6dp_audit")
        if not audit:
            out["status"] = "audit_absent"
            return out
        cut = pd.Timestamp(art.get("evidence_cutoff", EVIDENCE_CUTOFF))
        days = _calendar(cal_kind, leg_syms, cut)
        if days is None:
            out["status"] = "calendar_reconstruction_unavailable"
            return out
        T_ref = art.get("panel_gates", {}).get("T") \
            or art.get("panel_face", {}).get("T")
        if T_ref is not None and int(T_ref) != len(days):
            out["status"] = "calendar_mismatch_honest_skip"
            out["reconstructed_T"] = len(days)
            out["artifact_T"] = int(T_ref)
            return out
        out["status"] = "dated_reconstruction_verified"
        out["overlap_calendar"] = {"T": len(days),
                                   "first": str(days[0].date()),
                                   "last": str(days[-1].date())}
        days_ret = days[1:]
        ours = {n: pd.Series(np.asarray(s, float)[1:], index=P["idx"][1:])
                for n, s in series_by_cell.items()}
        cells = {}
        for cname, vals in audit.items():
            if not isinstance(vals, list) or len(vals) != len(days_ret):
                cells[cname] = {
                    "status": "value_count_mismatch_honest_skip",
                    "n_values": len(vals) if isinstance(vals, list) else None,
                    "n_expected": len(days_ret)}
                continue
            fr = pd.Series([float(v) for v in vals], index=days_ret)
            per = {}
            for n, s in ours.items():
                v, ov = _corr(s, fr)
                per[n] = {"corr": v, "overlap_days": ov}
            fin = [abs(d["corr"]) for d in per.values()
                   if d["corr"] is not None]
            cells[cname] = {"corr_vs_our_cells": per,
                            "max_abs_corr": round(max(fin), 4) if fin
                            else None}
        out["cells"] = cells
    except Exception as exc:
        out["status"] = "error"
        out["error"] = repr(exc)[:160]
    return out


def div_cross_face(P, series_by_cell):
    """Prereg s1 REQUIRED disclosure leg (queue-note verbatim): vs
    CN-DIV-LOWVOL-ROT judged cells. Their panel calendar = INTERSECTION
    of sh510880/sh512890 truncated at cutoff (cn_div_lowvol_rot_p1.py
    loader-verbatim)."""
    return _family_cross(P, series_by_cell, "CN-DIV-LOWVOL-ROT-P1",
                         DIV_ARTIFACT, "intersection", DIV_LEGS)


def trend_cross_face(P, series_by_cell):
    """Prereg s1 post-landing leg: vs CN_TREND_ETF_P1 judged cells (their
    panel calendar = UNION of their frozen 23-ETF universe, artifact
    panel_face.universe)."""
    out = {"family": "CN_TREND_ETF_P1",
           "face": "advisory_disclosure_only"}
    if not os.path.exists(TREND_ARTIFACT):
        out["status"] = ("artifact_absent (in-flight bm-b lane; prereg s1 "
                         "post-landing backfill leg applies)")
        return out
    try:
        art = json.load(open(TREND_ARTIFACT, encoding="utf-8"))
        uni = art.get("panel_face", {}).get("universe")
        if not uni:
            out["status"] = "universe_absent_in_artifact"
            return out
        merged = _family_cross(P, series_by_cell, "CN_TREND_ETF_P1",
                               TREND_ARTIFACT, "union", list(uni))
        merged["face"] = "advisory_disclosure_only"
        return merged
    except Exception as exc:
        out["status"] = "error"
        out["error"] = repr(exc)[:160]
        return out


# ---------------------------------------------------------------- finalize


def _jsonable(x):
    if isinstance(x, dict):
        return {k: _jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_jsonable(v) for v in x]
    if isinstance(x, np.bool_):
        return bool(x)
    if isinstance(x, (np.floating, np.integer)):
        return x.item()
    if isinstance(x, np.ndarray):
        return [_jsonable(v) for v in x.tolist()]
    return x


def _attr_row(batch, delta, total, gates):
    d = json.load(open(ATT_JSON, encoding="utf-8"))
    d["entries"].append({"batch": batch,
                         "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
                         "kind": "measurement", "cells_ledger_delta": delta,
                         "ledger_total_after": total, "gates": gates})
    with open(ATT_JSON + ".tmp", "w", encoding="utf-8") as fh:
        json.dump(_jsonable(d), fh, ensure_ascii=False, indent=1)
    os.replace(ATT_JSON + ".tmp", ATT_JSON)


def finalize(P, panel_face, cells_out, nulls, d6, divx, trendx, vstarts,
             robust, t0):
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
        BATCH_NAME, BATCH_CELLS, file_name="cn_soe_etf_p1",
        evidence_cutoff=EVIDENCE_CUTOFF,
        note="5 judged cells (SOE_HOLD/SOE_HOLD_MA200/SOE_LEGMA200/"
             "SOE_REPAIR/SOE_LOWVOL3) staggered 8-member zhongtegu SOE "
             "sleeve + 2000 same-mask weekly-Bernoulli nulls (x2 judged "
             "face, seed band 20272301+k); V2 ADV20-tiered cost, judged x2 "
             "always on; prereg research/CN_SOE_ETF_PREREG.md frozen "
             "ba54b43f; " + TICKET)
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
            "prereg": "research/CN_SOE_ETF_PREREG.md",
            "prereg_sha256_lf_normalized": prereg_sha,
            "roster": ("frozen 8-member probe cross-check = prereg s2 "
                       "table (universe re-derive fail-closed face)"),
            "judge_face": f"{JUDGED_FACE} (whole-V2 doubled, CN-* family "
                          "precedent, always on); x1 disclosure track",
            "seed": {"base": SEED, "k": K_NULLS,
                     "band": "20272301..20274300 (registry-declared)"},
            "accounting": "decision close t -> fills open t+1 (T+1 "
                          "asserted per order); SOE_HOLD per-leg staggered "
                          "entry at 200-own-bar warmup end (F6 entries==8 "
                          "structural = prereg s5 prediction 2); "
                          "HOLD_MA200/LEGMA200 STATE semantics (entry at "
                          "eval start if gate already open; break -> "
                          "cash); REPAIR crossing latch (dd[t-1] finite "
                          "> -20% AND dd[t] <= -20% enter; 63d closing "
                          "high exit; undefined dd = fail-closed); "
                          "LOWVOL3 63-bar re-selection grid, lowest "
                          "60d-std min(3, available) legs, 20% cap leaves "
                          "cash with 3 selected (no redistribution); "
                          "renorm every 21 bars offset=0, equal weight "
                          "min(1/n,0.20), capped excess to cash; off-grid "
                          "entries buy the new leg only; buys lot-rounded "
                          "with r251 afford loop, renorm targets "
                          "lot-aligned down, sells lot-multiples exact; "
                          "sells before buys (leg order asc); fill-day "
                          "open/ADV NaN rolls forward; PBP=243 (ETF-board "
                          "family constant); passive census baseline = "
                          "sleeve staggered EW (in-batch derive)",
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
        "cross_family_advisory": {
            "cn_div_lowvol_rot": divx,
            "cn_trend_etf": trendx,
        },
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
        json.dump(_jsonable(result), fh, ensure_ascii=False, indent=1)
    os.replace(OUT_JSON + ".tmp", OUT_JSON)
    rows = []
    for n in cells_out:
        for f in ("x1", "x2"):
            rows.append({"cell": n, "face": f,
                         **cells_out[n][f]["stats"]})
    pd.DataFrame(rows).to_csv(OUT_CSV, index=False)
    return result


# ---------------------------------------------------------------- driver


def _compute_cells(P):
    """Cells x faces assembly glue (checkpoint-aware). r286 law: the
    blob->cells_out[name][face] assignment lives in BOTH branches and is
    selftest-exercised (leg [16]) -- component greens are not driver
    greens."""
    os.makedirs(CELL_DIR, exist_ok=True)        # glue self-contained
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
                cells_out[name][face] = blob
            else:
                rec = run_portfolio(P, enter_ev, exit_ev,
                                    cost_fn=fn,
                                    collect=(face == JUDGED_FACE))
                if not rec["t1_ok"]:
                    print(f"FAIL-CLOSED: T+1 violation in {name}/{face}")
                    return None
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
                cells_out[name][face] = blob
                np.save(ck.replace(".json", ".npy"), rec["returns"])
                dump = {k: v for k, v in blob.items() if k != "series"}
                with open(ck + ".tmp", "w", encoding="utf-8") as fh:
                    json.dump(_jsonable(dump), fh, ensure_ascii=False,
                              indent=1)
                os.replace(ck + ".tmp", ck)
                print(f"cell {name}/{face}: sharpe="
                      f"{blob['stats']['sharpe_full']} trades="
                      f"{rec['n_trades']} entries={rec['n_entries']}",
                      flush=True)
        if cells_out[name][JUDGED_FACE]["n_trades"] == 0:
            print(f"VOID: {name} zero trades -- signal machinery broken")
            return None
        cells_out[name] = {f: cells_out[name][f] for f in ("x1", "x2")}
    return cells_out


def cmd_run():
    global SEED
    SEED = SG.SEED_REGISTRY["cn_soe_etf_p1"]
    t0 = time.time()
    P, gates = load_panel()
    if P is None:
        return 2
    cells_out = _compute_cells(P)
    if cells_out is None:
        return 2
    nulls = run_nulls(P)
    series_by_cell = {n: cells_out[n][JUDGED_FACE]["series"]
                      for n in cells_out}
    d6 = d6_face(P, series_by_cell)
    divx = div_cross_face(P, series_by_cell)
    trendx = trend_cross_face(P, series_by_cell)
    vstarts = virtual_starts(P, series_by_cell)
    robust = {n: robust_stats(s) for n, s in series_by_cell.items()}
    panel_face = {
        "T": P["T"], "N": P["N"], "universe": P["syms"],
        "universe_n": len(P["syms"]),
        "name_face_n": P["gates"]["name_face_n"],
        "universe_outs": P["universe_outs"],
        "sse_cover": round(P["sse_cover"], 4),
        "cover_gaps_postlisting": P["cover_gaps"],
        "sleeve_start": str(P["idx"][int(np.argmax(P["n_avail"] > 0))]
                            .date()) if (P["n_avail"] > 0).any() else None,
        "agg_eval_start": str(P["idx"][P["agg_start"]].date())
                          if P["agg_start"] < P["T"] else None,
        "avail_start_days": [str(P["idx"][t].date())
                             for t in P["avail_start"]],
        "duty_cycles_p_leg": [round(float(v), 4) for v in P["p_leg"]],
        "gates": P["gates"],
        "sleeve_ew_bars": int(len(P["ew_full"])),
    }
    res = finalize(P, panel_face, cells_out, nulls, d6, divx, trendx,
                   vstarts, robust, t0)
    g1_all = [res["gates"][n]["g1_prime_v2"]["pass_v2"]
              for n in res["gates"]]
    print(f"finalize ok: cells={len(res['cells'])} "
          f"ledger={res['trials_ledger']['total']} "
          f"g1_pass={g1_all} "
          f"elapsed={res['audit']['elapsed_sec']}s")
    return 0


# ---------------------------------------------------------------- selftest


def _mk_board(tmp, T=520, n_pass=5):
    """Hermetic synthetic board + synthetic etf_list: staggered pass legs
    (to exercise the warmup face) + crafted rejects per clause
    (rows/first/NaN/amount/name-exclusion)."""
    board = os.path.join(tmp, "daily")
    os.makedirs(board)
    list_path = os.path.join(tmp, "etf_list.csv")
    end = pd.Timestamp(EVIDENCE_CUTOFF)
    cal = pd.bdate_range(end=end, periods=T)
    rng = np.random.default_rng(11)
    # common market factor with a crash segment: the sleeve-EW index
    # must cross a >=20% drawdown from its rolling-high window so the
    # REPAIR cell has real events on the synthetic board too
    mkt = np.cumprod(1.0 + rng.normal(0.0004, 0.006, T))
    mkt[250:320] *= np.linspace(1.0, 0.72, 70)     # -28% descent
    mkt[320:] *= 0.72
    rows = []
    syms_pass = []
    for i in range(n_pass):
        px = 2.0 + 0.5 * i
        start = i * 40                             # staggered listings
        n = T - start
        drift = np.cumprod(1.0 + rng.normal(0.0004, 0.012, n))
        close = px * drift * mkt[start:]
        open_ = close * (1 + rng.normal(0, 0.003, n))
        high = np.maximum(open_, close) * 1.004
        low = np.minimum(open_, close) * 0.996
        vol = np.full(n, 6e6) + rng.random(n) * 2e6
        sym = f"sh5101{i:02d}"
        pd.DataFrame({"date": cal[start:], "open": open_, "high": high,
                      "low": low, "close": close, "volume": vol,
                      "amount": vol * close}).to_csv(
            os.path.join(board, sym + ".csv"), index=False)
        syms_pass.append(sym)
        rows.append((sym, f"央企创新ETF测试{i}"))
    # reject: rows too short (listed late -> also first clause)
    sym = "sh500001"
    k = 120
    pd.DataFrame({"date": cal[-k:], "open": np.full(k, 3.0),
                  "high": np.full(k, 3.0), "low": np.full(k, 3.0),
                  "close": np.full(k, 3.0), "volume": np.full(k, 6e6),
                  "amount": np.full(k, 1.8e7)}).to_csv(
        os.path.join(board, sym + ".csv"), index=False)
    rows.append((sym, "央企ETF短史"))
    # reject: NaN row
    sym = "sh500002"
    df = pd.DataFrame({"date": cal, "open": np.full(T, 3.0),
                       "high": np.full(T, 3.0), "low": np.full(T, 3.0),
                       "close": np.full(T, 3.0), "volume": np.full(T, 6e6),
                       "amount": np.full(T, 1.8e7)})
    df.loc[T // 2, "close"] = np.nan
    df.to_csv(os.path.join(board, sym + ".csv"), index=False)
    rows.append((sym, "国企ETF带缺"))
    # reject: amount too thin
    sym = "sh500003"
    pd.DataFrame({"date": cal, "open": np.full(T, 3.0), "high": np.full(T, 3.0),
                  "low": np.full(T, 3.0), "close": np.full(T, 3.0),
                  "volume": np.full(T, 1e2), "amount": np.full(T, 3e2)}
                 ).to_csv(os.path.join(board, sym + ".csv"), index=False)
    rows.append((sym, "国企ETF太薄"))
    # name-face rejects (never reach board clauses)
    rows.append(("sh500004", "恒生央企ETF测试"))
    rows.append(("sh500005", "央企港股ETF测试"))
    pd.DataFrame(rows, columns=["代码", "名称"]).to_csv(list_path,
                                                        index=False,
                                                        encoding="utf-8-sig")
    return board, list_path, sorted(syms_pass), cal


def cmd_selftest():
    global DAILY_DIR, ETF_LIST, OUT_DIR, CELL_DIR, OUT_JSON, OUT_CSV, ATT_JSON
    global FROZEN_EIGHT, ROWS_MIN, FIRST_MAX, MED_AMT20_MIN, SSE_COVER_MIN
    global SEED, K_NULLS, WARMUP, AGG_AGE_MIN, AGG_LEGS_MIN, MA_WIN
    global REBAL_STEP, SELECT_STEP, STD_WIN, REPAIR_DD_WIN, REPAIR_HI_WIN
    global WIN_DAYS, STARTS_FROM, DIV_ARTIFACT, DIV_LEGS, cscv_pbo
    tmp = tempfile.mkdtemp(prefix="cn_soe_selftest_")
    board, list_path, syms_expect, cal = _mk_board(tmp)
    DAILY_DIR, ETF_LIST = board, list_path
    OUT_DIR = os.path.join(tmp, "out")
    CELL_DIR = os.path.join(OUT_DIR, "cells")
    OUT_JSON = os.path.join(OUT_DIR, "p1_results.json")
    OUT_CSV = os.path.join(OUT_DIR, "cells_summary.csv")
    ATT_JSON = os.path.join(tmp, "attr.json")
    json.dump({"entries": []}, open(ATT_JSON, "w"))
    FROZEN_EIGHT = tuple(sorted(syms_expect))
    ROWS_MIN, FIRST_MAX = 300, "2025-12-31"
    MED_AMT20_MIN, SSE_COVER_MIN = 1e6, 0.0
    SEED = 20272301
    K_NULLS = 32       # skill_line_v2 null-pool floor is 30 values
    WARMUP, AGG_AGE_MIN, AGG_LEGS_MIN = 40, 30, 3
    MA_WIN = 30
    REBAL_STEP, SELECT_STEP, STD_WIN = 5, 13, 10
    REPAIR_DD_WIN, REPAIR_HI_WIN = 60, 20
    WIN_DAYS, STARTS_FROM = 100, 60
    # div cross face: point at a synthetic mini-artifact + synthetic legs
    div_legs = ("sh600001", "sh600002")
    for s, driftseed in ((div_legs[0], 21), (div_legs[1], 22)):
        n = 200
        rng = np.random.default_rng(driftseed)
        drift = np.cumprod(1.0 + rng.normal(0.0004, 0.01, n))
        close = 2.0 * drift
        vol = np.full(n, 5e6)
        pd.DataFrame({"date": cal[-n:], "open": close,
                      "high": close * 1.01, "low": close * 0.99,
                      "close": close, "volume": vol,
                      "amount": vol * close}).to_csv(
            os.path.join(board, s + ".csv"), index=False)
    div_days = pd.to_datetime(pd.read_csv(
        os.path.join(board, div_legs[0] + ".csv"))["date"])
    div_days = div_days[div_days <= pd.Timestamp(EVIDENCE_CUTOFF)]
    rng_v = np.random.default_rng(33)
    div_vals = [round(float(v), 6) for v in
                rng_v.normal(0.0002, 0.008, len(div_days) - 1)]
    div_art = os.path.join(tmp, "div_p1_results.json")
    json.dump({"evidence_cutoff": EVIDENCE_CUTOFF,
               "panel_gates": {"T": int(len(div_days))},
               "judged_x2_returns_6dp_audit": {"W63_bare": div_vals}},
              open(div_art, "w"))
    DIV_ARTIFACT, DIV_LEGS = div_art, div_legs
    ok = []

    def check(name, cond, detail=""):
        ok.append((name, bool(cond), detail))
        print(f"  [{'PASS' if cond else 'FAIL'}] {name} {detail}")

    # hermetic stubs for repo-state-coupled faces (family precedent)
    _ne, _pb, _al = SG.n_eff, SG.passive_baseline, SG.append_ledger
    SG.n_eff = lambda bc, rd=None: int(bc)
    SG.passive_baseline = lambda pool, rd=None: 0.4606
    SG.append_ledger = lambda *a, **k: {"prev_total": 0, "total": 100,
                                        "batch": BATCH_NAME}
    _cp = cscv_pbo
    cscv_pbo = lambda mat: {"pbo": 0.1}       # 1-cell fixture: PBO not
    _lr = None                                # under test here (family [15])
    try:
        # [1] panel gates: name-face re-derive == crafted pass set
        P, gates = load_panel()
        check("[1] panel loads, universe == name-face pass set",
              P is not None and P["syms"] == syms_expect,
              f"n={0 if P is None else P['N']}")
        T, N = P["T"], P["N"]

        # [2] staggered warmup: per-leg availability at 200-own-bar mark
        ent_h, _ = cell_events(P, CELLS[0])
        ev_days = np.flatnonzero(ent_h.any(axis=1))
        check("[2] SOE_HOLD staggered entries == per-leg warmup ends",
              len(ev_days) == N
              and all(ent_h[t, j] for t, j in
                      ((int(P["avail_start"][j]), j) for j in range(N))))
        check("[2b] availability = WARMUP own bars (listing-lag honest)",
              all(int(P["avail_start"][j])
                  >= int(np.argmax(np.isfinite(P["close"][:, j])))
                  + WARMUP - 1 for j in range(N)))

        # [3] sleeve face: index starts at first avail member, EW accrual
        t0 = int(np.argmax(P["n_avail"] > 0))
        check("[3] sleeve index base at first-avail warmup end",
              abs(float(P["sleeve_idx"][t0]) - 1.0) < 1e-12
              and np.all(np.isnan(P["sleeve_idx"][:t0])))
        n_a = P["avail"] & np.isfinite(P["rets"])
        with np.errstate(invalid="ignore"):
            exp_ew = np.where(n_a[t0 + 1].sum() > 0,
                              np.where(n_a[t0 + 1], P["rets"][t0 + 1],
                                       0.0).sum()
                              / max(int(n_a[t0 + 1].sum()), 1), 0.0)
        check("[3b] sleeve EW accrual = available-leg mean return",
              abs(float(P["ew_full"][t0 + 1]) - float(exp_ew)) < 1e-12)

        # [4] HOLD_MA200 state semantics: entry at agg start if gate open
        ent_m, ext_m = cell_events(P, CELLS[1])
        a0 = int(P["agg_start"])
        gate0 = (P["sleeve_idx"][a0] > P["idx_ma200"][a0]) \
            and np.isfinite(P["idx_ma200"][a0])
        check("[4] agg eval start = age>=AGG_AGE_MIN and legs>=AGG_LEGS_MIN",
              a0 < T and P["idx_age"][a0] >= AGG_AGE_MIN
              and P["n_avail"][a0] >= AGG_LEGS_MIN)
        check("[4b] state entry at eval start iff gate open",
              bool(ent_m[a0].any()) == bool(gate0),
              f"gate_open={gate0} entered={bool(ent_m[a0].any())}")
        ups = np.flatnonzero(ent_m.any(axis=1))
        downs = np.flatnonzero(ext_m.any(axis=1))
        check("[4c] gate transitions produce enter/exit events",
              len(ups) + len(downs) >= 1)

        # [5] LEGMA200 per-leg state semantics from warmup end
        ent_l, ext_l = cell_events(P, CELLS[2])
        j = 0
        t0j = int(P["avail_start"][j])
        lg = P["leg_gate"]
        check("[5] per-leg state entry at warmup end iff leg above MA",
              bool(ent_l[t0j, j]) == bool(lg[t0j, j]))
        ent_after = np.flatnonzero(ent_l[t0j + 1:, j])
        ok_edges = all(lg[t0j + 1 + t, j] and not lg[t0j + t, j]
                       for t in ent_after)
        check("[5b] re-entries only on rising edges",
              ok_edges, f"n={len(ent_after)}")

        # [6] REPAIR crossing latch semantics (crafted single-leg context)
        Tk = 300
        close_i = np.full(Tk, 100.0)
        close_i[70:100] = np.linspace(100.0, 75.0, 30)   # -25% INSIDE the
        #   rolling-high window (60 bars): dd crosses -20% at ~t94
        close_i[100:150] = 75.0                          # floor: held, no re-fire
        close_i[150:210] = np.linspace(75.0, 101.0, 60)  # recovery: 20-bar
        #   closing new high fires the single exit early in the ramp
        close_i[210:] = 102.0
        ctx6 = {"T": Tk, "N": 1, "open": close_i, "close": close_i,
                "close_ff": close_i, "adv_arg": np.full((Tk, 1), 1e9),
                "avail": np.ones((Tk, 1), bool), "days": None}
        s = pd.Series(close_i)
        hi = s.rolling(REPAIR_DD_WIN, min_periods=REPAIR_DD_WIN).max() \
            .to_numpy(float)
        with np.errstate(invalid="ignore"):
            dd = close_i / hi - 1.0
        prev63 = s.rolling(REPAIR_HI_WIN,
                           min_periods=REPAIR_HI_WIN).max().shift(1) \
            .to_numpy(float)
        ctx6.update({"sleeve_idx": close_i, "idx_ma200": np.full(Tk, np.nan),
                     "dd252": dd, "prev63": prev63, "agg_start": 0,
                     "idx_age": np.arange(Tk), "n_avail": np.ones(Tk, int)})
        ent_r, ext_r = cell_events(ctx6, CELLS[3])
        ent_ts = np.flatnonzero(ent_r.any(axis=1))
        ext_ts = np.flatnonzero(ext_r.any(axis=1))
        check("[6] REPAIR single entry on first dd<=-20% crossing",
              len(ent_ts) == 1 and dd[ent_ts[0]] <= -REPAIR_DD,
              f"ent={ent_ts.tolist()}")
        check("[6b] REPAIR exit at 63d closing new high, no re-entry",
              len(ext_ts) == 1 and close_i[ext_ts[0]] > prev63[ext_ts[0]],
              f"ext={ext_ts.tolist()}")

        # [7] LOWVOL3 selection: 3 lowest std60 at SELECT_STEP grid
        ent_v, ext_v = cell_events(P, CELLS[4])
        grid_ts = [t for t in range(0, T, SELECT_STEP)
                   if P["avail"][t].any()
                   and np.isfinite(P["std60"][t][P["avail"][t]]).any()]
        check("[7] LOWVOL3 events only at grid points",
              all(t % SELECT_STEP == 0
                  for t in np.flatnonzero(ent_v.any(axis=1))))
        t_g = grid_ts[0]
        cand = [j for j in range(N) if P["avail"][t_g, j]
               and np.isfinite(P["std60"][t_g, j])]
        cand.sort(key=lambda j: (float(P["std60"][t_g, j]), j))
        want = set(cand[:LOWVOL_N])
        check("[7b] first selection = lowest-60d-std min(3, available)",
              set(j for j in range(N) if ent_v[t_g, j]) == want,
              f"want={sorted(want)}")

        # [8] T+1 + afford + lot integrity on tiny capital
        global CAPITAL
        saved_cap = CAPITAL
        CAPITAL = 3_000.0
        rec = run_portfolio(P, ent_h, np.zeros((T, N), bool),
                            cost_fn=side_cost_x2, collect=True)
        CAPITAL = saved_cap
        check("[8a] T+1 asserted", rec["t1_ok"])
        check("[8b] trades executed under tiny capital",
              rec["n_trades"] >= 1)
        bad = [tr for tr in rec["transitions_head"]
               if tr["shares"] % LOT != 0]
        check("[8c] all fills lot-multiples", not bad)

        # [9] 20% cap: portfolio vol < single-leg vol with capped weights
        act = np.zeros((T, N), bool)
        act[:, 0] = True
        act[:, 1] = True
        prev = np.vstack([np.zeros((1, N), bool), act[:-1]])
        rec2 = run_portfolio(P, act & ~prev, ~act & prev,
                             cost_fn=side_cost_x2, collect=False)
        leg_vol = np.nanstd(np.diff(np.log(P["close_ff"][:, 0])))
        port_vol = np.nanstd(rec2["returns"][1:])
        check("[9] cap 20%: 2-leg portfolio vol < single-leg vol",
              port_vol < leg_vol, f"p={port_vol:.5f} l={leg_vol:.5f}")

        # [10] determinism: double-run identity (equal_nan r255 law)
        r1 = run_portfolio(P, ent_h, np.zeros((T, N), bool),
                           cost_fn=side_cost_x2)
        r2 = run_portfolio(P, ent_h, np.zeros((T, N), bool),
                           cost_fn=side_cost_x2)
        check("[10] deterministic double-run identity",
              bool(np.array_equal(r1["returns"], r2["returns"],
                                  equal_nan=True))
              and r1["n_trades"] == r2["n_trades"])

        # [11] null machinery: deterministic, finite, p in [0,1]
        n1 = run_nulls(P)
        n2 = run_nulls(P)
        check("[11a] nulls deterministic (double-run identity)",
              n1["values"] == n2["values"])
        check("[11b] null coverage finite + count",
              n1["coverage"]["n_values"] == K_NULLS
              and all(np.isfinite(v) for v in n1["values"]))
        check("[11c] duty cycles in [0,1]",
              all(0.0 <= v <= 1.0 for v in P["p_leg"]))

        # [12] census + splits structure (REV_OSC s2.1/s2.3 family face)
        vs = virtual_starts(P, {"SOE_HOLD": r1["returns"]})
        check("[12] census n_starts == T-WIN_DAYS-STARTS_FROM",
              vs["n_starts"] == T - WIN_DAYS - STARTS_FROM,
              f"{vs['n_starts']}")
        check("[12b] splits + walk-forward present",
              "split_sign_agreement_pct" in vs["cells"]["SOE_HOLD"]
              and len(vs["cells"]["SOE_HOLD"]["walk_forward_sharpe"]) == 5)

        # [13] robust dual p values in [0,1]
        rb = robust_stats(r1["returns"])
        check("[13] robust p faces in [0,1]",
              0.0 <= rb["sign_flip_p"] <= 1.0
              and 0.0 <= rb["block_bootstrap_p_le_0"] <= 1.0)

        # [14] D6 real path: twin reject / value-reversed ortho no-reject
        s = pd.Series(np.asarray(r1["returns"], float)[1:],
                      index=P["idx"][1:])
        twin = d6_block(s, {"TRADER-X": s.copy()})
        rev_vals = pd.Series(s.to_numpy()[::-1], index=s.index)
        ortho = d6_block(s, {"TRADER-Y": rev_vals})
        check("[14] D6 twin reject / ortho no-reject",
              bool(twin["member_face"]["reject"]) is True
              and bool(ortho["member_face"]["reject"]) is False)

        # [15] gates wiring smoke (stubbed line faces, hermetic)
        g1 = SG.g1_prime_v2(1.2, s, batch_cells=10, pool="core48",
                            null_pool={"values": n1["values"],
                                       "coverage": n1["coverage"]},
                            n_trades=100, n_entries=100)
        check("[15] g1 dict face with skill_line",
              "skill_line" in g1 and "pass_v2" in g1)

        # [16] r286 assembly-glue leg: _compute_cells fills cells_out for
        #      all names x faces (component green != driver green)
        cells_out = _compute_cells(P)
        check("[16] _compute_cells glue: 5 cells x 2 faces populated",
              cells_out is not None
              and sorted(cells_out) == sorted(c["name"] for c in CELLS)
              and all(sorted(cells_out[n]) == ["x1", "x2"]
                      and "series" in cells_out[n]["x2"]
                      and "stats" in cells_out[n]["x2"]
                      for n in cells_out))
        check("[16b] checkpoints idempotent (second pass loads, identical)",
              _compute_cells(P) is not None
              and all(np.array_equal(
                  cells_out[n]["x2"]["series"],
                  _compute_cells(P)[n]["x2"]["series"],
                  equal_nan=True) for n in cells_out))

        # [17] div cross dated reconstruction (synthetic mini-artifact):
        #      calendar length-verified + corr computed on aligned dates
        dcx = div_cross_face(P, {"SOE_HOLD": r1["returns"]})
        check("[17] div cross dated reconstruction verified",
              dcx["status"] == "dated_reconstruction_verified"
              and "W63_bare" in dcx.get("cells", {})
              and dcx["cells"]["W63_bare"]["corr_vs_our_cells"]
              ["SOE_HOLD"]["corr"] is not None,
              f"status={dcx.get('status')}")

        # [18] finalize product on synthetic (trials_ledger r252 +
        #      entries r248 + cutoff meta + cross legs carried)
        d6 = d6_block(s, {"TRADER-X": s.copy()})
        d6w = {"cells": {c: d6 for c in cells_out}, "member_cutoffs": {},
               "same_batch_cross": {}, "reject_line": D6_REJECT,
               "members": []}
        res = finalize(P, {"T": T, "N": N}, cells_out, n1, d6w,
                       div_cross_face(P, {"SOE_HOLD": r1["returns"]}),
                       trend_cross_face(P, {"SOE_HOLD": r1["returns"]}),
                       {"n_starts": 1, "segments": {}, "cells": {}},
                       {"SOE_HOLD": rb}, time.time())
        check("[18] finalize product + trials_ledger key law",
              os.path.exists(OUT_JSON)
              and "trials_ledger" in res
              and res["evidence_cutoff"] == EVIDENCE_CUTOFF
              and "cutoff_meta" in res
              and "cross_family_advisory" in res)
        att = json.load(open(ATT_JSON, encoding="utf-8"))
        check("[18b] attrition row in entries (r248)",
              len(att["entries"]) == 1
              and att["entries"][0]["batch"] == BATCH_NAME)

        # [19] r286: dump payloads must be numpy-native-coerced (real-
        #      data x2 crash face: transitions_head 'leg' np.int64)
        tr = {"day": "2026-09-22", "leg": np.int64(7), "side": "buy",
              "shares": int(300), "notional": np.float64(123.4),
              "cost": np.float64(1.2)}
        probe_dump = _jsonable(
            {"stats": {"sharpe": np.float32(0.5)},
             "transitions_head": [tr],
             "flags": np.bool_(True),
             "vec": np.array([1, 2])})
        check("[19] _jsonable native coercion on dump payloads (r286)",
              isinstance(probe_dump["transitions_head"][0]["leg"], int)
              and isinstance(probe_dump["stats"]["sharpe"], float)
              and probe_dump["flags"] is True
              and probe_dump["vec"] == [1, 2]
              and json.dumps(probe_dump) is not None)

        # [20] checkpoint payload itself parses as json after dump (the
        #      real-data crash site: per-cell json dump with np types)
        ck = os.path.join(CELL_DIR, "SOE_HOLD_x2.json")
        blob = json.load(open(ck, encoding="utf-8"))
        check("[20] per-cell checkpoint parses (r286 dump site)",
              "stats" in blob and "transitions_head" in blob)
    finally:
        SG.n_eff, SG.passive_baseline, SG.append_ledger = _ne, _pb, _al
        cscv_pbo = _cp
        shutil.rmtree(tmp, ignore_errors=True)

    n_ok = sum(1 for _, v, _ in ok if v)
    print(f"cn_soe_etf_p1 selftest: {n_ok}/{len(ok)} PASS")
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
            os.environ.get("CN_SOE_ETF_P1_REFINALIZE") != "1":
        print("idempotent no-op: p1_results.json exists "
              "(CN_SOE_ETF_P1_REFINALIZE=1 = only redo)")
        return 0
    return cmd_run()


if __name__ == "__main__":
    sys.exit(main())
