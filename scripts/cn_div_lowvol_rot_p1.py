# -*- coding: utf-8 -*-
"""CN-DIV-LOWVOL-ROT-P1 -- CN-DIV-LOWVOL-ROT combo model, s3 slice-2 batch
runner (T-2026-09-26-73, CEO order O-20260926-0926 "CN-native combo models").

Prereg FROZEN research/CN_DIV_LOWVOL_ROT_PREREG.md (R250 freeze; R251
zero-run amendment: T_joint 1861->1862 probe-authoritative count, mismatch
day narrative = 512890 share-fold suspension bar, event-guard leg via
DLP._adjust_split per r239 pit law). Zero threshold edits post-run; s7/s8
backfill is the only sanctioned prereg edit (control plane, not here).

Cells (prereg s0: judged grid = 4, K=50 nulls NOT in the skill grid):
  W63_bare  / W252_bare    naked 21d-rhythm rotation: argmax RS_W of the
                           two legs, 100% single leg (tie -> 50/50)
  W63_gate  / W252_gate    MA200 defensive gate (constitutive axis): the
                           SELECTED leg must close above its MA200 at the
                           rebalance close, else 100% cash that period;
                           tie -> per-leg gate on each half (frozen rule)
  Machinery: RS_W(t) = C_t/C_{t-W} - 1 on the DLP._adjust_split post-event
  price face (512890 factor 0.5 -- raw face carries a -51% fold artifact
  at 2021-10-25, forbidden in signal faces per r239 law); signal at close
  r, execution from open r+1 (T+1).

Accounting (prereg s3.2/s3.5 -- family MF_ROT/DOG semantics + queue fill):
  capital = 1,000,000 CNY; 21-trading-day rebalance rhythm (schedule =
  range(20, T-1, 21), frozen); single-leg 100% (no leverage, no buffer);
  daily close valuation; exit-day leg P&L rides open fills at that day's
  open; cash leg zero-yield. Cost = V2 ADV20-tiered (knowledge/rules.py
  CostPatch single source); judge face = x2 (whole-V2 doubled,
  side_cost_x2 -- family precedent, always on); x1 = side_cost_v2 verbatim,
  x3 = every component tripled (div_lowvol_backtest.side_cost_x3 single
  source) = disclosure tracks. Each face is a complete self-consistent
  sleeve (family law).
  QUEUE FILL (prereg s3.5, the family fill_refusal -> queuing correction):
  any transition notional above 1% x ADV20 fills over multiple days at
  min(remaining, 1% x ADV20(t-1)) per day; sells execute before buys
  (proceeds fund same-day buys); buys round DOWN to 100-share lots
  (knowledge.rules.min_lot single source), sells are exact-share; a new
  rebalance re-anchors the remainders and SUPERSEDES an incomplete
  transition (fill_days=None recorded honestly); fill_days counters land
  in the artifact per transition (judged face).

Nulls (s3.4): K=50 random-leg rotation sleeves -- one draw per rebalance
point from numpy.random.default_rng(20260980+k), uniform leg, k<50; same
window/rhythm/cost(x2)/warmup (W63-bare activation rule); gate cells share
the bare-null distribution (prereg explicit conservative note).
Baselines (s3.4): static EW pair 50/50 re-set at each active rebalance +
per-leg buy-and-hold (both W63-bare-anchored, x2 face, disclosure only).
Trial count N = 4 cells + 50 nulls = 54 on the D1 bill.

Panel (prereg s2 + R251 amendment): corpus twins data/daily/sh{510880,
512890}.csv, intersection timeline T=1862 (2019-01-18..2026-09-22),
A-only-within-window == ['2021-10-22'] (512890 fold-suspension bar, DLP
single source), B-only == [], zero NaN on the timeline. ADV20 = rolling-20
mean of raw volume x close (CNY; continuous across the share fold; volume
unadjusted = conservative bias, family note). Data gates fail-closed
exit 2 on any drift (date-drift refusal law). evidence_cutoff = 2026-09-22
(D2 forward lockbox; 09-23/24 bars excluded).

Gates (prereg s4, shared library only -- zero hand-copied lines):
  G1'v2 = science_gates.g1_prime_v2(batch_cells=4, pool='core48',
  null_pool=batch-own {values, coverage}) on the JUDGED x2 series;
  G2 = g2_registration_v2 + DSR (deflated_sharpe_ratio raw daily returns,
  n_trials=line.n_eff, var_null_sr=null sigma^2) + family PBO
  (screening/pbo.cscv_pbo CSCV-8 over the 4-cell x2 grid).
  D6 (s1): reject face = max|corr| vs the 6 registered traders (ew6 canon,
  identical loader to the live.paper anchor gate); same-batch cross-corr
  = disclosure; H4-style disclosures (never admission): vs family
  DIV_LOWVOL_P1 C1 x2 (artifact carries no return series -> honest
  "unavailable", prereg 0.6-0.9 band stands) + vs 510880 leg daily
  returns (= the ALLOC P5 slot leg face).
  Descriptive clauses (s4, disclosure never gates): ann>0, OOS(>=2025-01-01)
  dual positive, |maxDD|<=35%, no <=-30% crash year, x1/x3 yearly sign
  stability vs x2. Hard-bound triad: median/p99.9 carry the extreme-day
  reading; max|d1| with crisis-window awareness (frozen windows 2020-03 /
  2021-02 / 2024-09..10) -> single-point exemption column.
  REGIME_GUARD v3 descriptive column via the IMPORTED frozen deep-replay
  layer (cn_rev_tilt_p1.regime_v3_column reuse; never a switch).

Products (prereg s6): results/cn_div_lowvol_rot/p1_results.json (top-level
evidence_cutoff + science_gates.cutoff_meta + 4 cells x {x1,x2,x3} + nulls
+ baselines + D6 + fill_days faces + cost faces) + cells_summary.csv;
ledger append single-shot at finalize (CN_DIV_LOWVOL_ROT_P1_REFINALIZE=1
is the only redo path); attrition row lands in the ENTRIES list (r248
consumer-chain law); per-unit .npz checkpoints (gitignored, exact resume).

Usage: run | selftest   (exit 0 ok; 2 = fail-closed gate/mechanism refusal)
"""
import argparse
import json
import math
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "screening"))

import numpy as np
import pandas as pd

import science_gates as sg
from alloc_backtest import side_cost_v2, side_cost_x2
from div_lowvol_backtest import side_cost_x3
import div_lowvol_probe as DLP
from pbo import cscv_pbo, align_returns
from composite_ic import IS_END
from knowledge import rules as krules
# family single sources (identical semantics; descriptive/reject faces):
from cn_rev_tilt_p1 import (_corr, d6_block, load_member_rets,
                            regime_v3_column)

TICKET = "T-2026-09-26-73"
PREREG = os.path.join(ROOT, "research", "CN_DIV_LOWVOL_ROT_PREREG.md")
OUT_DIR = os.path.join(ROOT, "results", "cn_div_lowvol_rot")
CKPT_DIR = os.path.join(OUT_DIR, "ckpt")
OUT_JSON = os.path.join(OUT_DIR, "p1_results.json")
OUT_CSV = os.path.join(OUT_DIR, "cells_summary.csv")
ATT_JSON = os.path.join(ROOT, "results", "gate_attrition.json")
LOG_PATH = os.path.join(OUT_DIR, "runner.log")

EVIDENCE_CUTOFF = "2026-09-22"     # prereg s2 (R250 freeze; legs' last bar)
EVIDENCE_CUTOFF_TS = pd.Timestamp(EVIDENCE_CUTOFF)
OOS_START = "2025-01-01"           # composite_ic shared split (IS_END+1)
SEED_BASE = 20_260_980             # SEED_REGISTRY['cn_div_lowvol_rot_p1']
K_NULLS = 50
BATCH_CELLS = 4                    # judged grid (prereg s0; nulls excluded)
LEDGER_TRIALS = 54                 # 4 cells + 50 nulls on the D1 bill
LEGS = ("510880", "512890")
LEG_BY_I = {0: LEGS[0], 1: LEGS[1]}
T_JOINT_FROZEN = 1862              # R251 amendment (probe joint_bars)
JOINT_FIRST_FROZEN = "2019-01-18"
MISMATCH_FROZEN = ["2021-10-22"]   # 512890 fold-suspension bar (A-only)
W_SET = (63, 252)                  # prereg s3.1 frozen windows
MA_WIN = 200                       # prereg s3.3 defensive gate window
REBAL_STEP = 21                    # monthly rhythm (prereg s3.2, frozen)
REBAL_FIRST = 20                    # schedule anchor: range(20, T-1, 21)
CAPITAL = 1_000_000.0              # CN-* paper spec (prereg s3.2)
LOT = int(krules.min_lot(LEGS[0]))           # 100 shares (single source)
ADV_CAP = float(krules.ADV_FILL_CAP_RATE)     # 1% ADV20 (single source)
JUDGED_FACE = "x2"                 # prereg s3.5 family precedent
FACES = {"x1": side_cost_v2, "x2": side_cost_x2, "x3": side_cost_x3}
MAXDD_LINE = -0.35                  # descriptive red line (s4)
CRASH_YEAR_LINE = -0.30             # "no crash year" definition (s4)
D6_REJECT = 0.7                     # s1 hard line
CRISIS_WINDOWS = [("2020-03-01", "2020-03-31"),
                  ("2021-02-01", "2021-02-28"),
                  ("2024-09-01", "2024-10-31")]   # s4 hard-bound triad
CRISIS_LOG_ABS_R = 0.05             # crisis-day log threshold (s4)
PBP = 252.0
SELL_EPS = 1e-6                     # notional epsilon for sell remainders
JUDGED_CELLS = ("W63_bare", "W252_bare", "W63_gate", "W252_gate")
NULL_ACTIVATION_W = 63              # nulls/baselines share W63-bare warmup


def _log(msg):
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as fh:
        fh.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}\n")
    print(f"[cn_div_lowvol_rot] {msg}", flush=True)


# ---------------------------------------------------------------- panel


def _leg_frame(code):
    df = pd.read_csv(os.path.join(ROOT, "data", "daily", f"sh{code}.csv"),
                     parse_dates=["date"])
    return df.set_index("date").sort_index()


def panel_gates(days, a_only_win, b_only_win, nan_free):
    """s2 data gates (R251 amendment numbers), fail-closed."""
    cutoff = str(days[-1].date())
    cuts = [str(d.date()) for d in a_only_win]
    b_only = [str(d.date()) for d in b_only_win]
    ok = {
        "cutoff": cutoff,
        "cutoff_ok": bool(cutoff == EVIDENCE_CUTOFF),
        "first": str(days[0].date()),
        "first_ok": bool(str(days[0].date()) == JOINT_FIRST_FROZEN),
        "T": int(len(days)),
        "T_ok": bool(len(days) == T_JOINT_FROZEN),
        "legs": int(len(LEGS)),
        "legs_ok": bool(len(LEGS) == 2),
        "a_only_window": cuts,
        "a_only_ok": bool(cuts == MISMATCH_FROZEN),
        "b_only_window": b_only,
        "b_only_ok": bool(b_only == []),
        "nan_free": bool(nan_free),
    }
    ok["all_ok"] = bool(all(ok[k] for k in
                            ("cutoff_ok", "first_ok", "T_ok", "legs_ok",
                             "a_only_ok", "b_only_ok", "nan_free")))
    return ok


def load_panel():
    """Intersection timeline + event-adjusted price faces + raw-ADV face.
    Zero network; corpus twins are in-repo (prereg s2)."""
    raw = {c: _leg_frame(c) for c in LEGS}
    A = set(raw[LEGS[0]].index)
    B = set(raw[LEGS[1]].index)
    days = pd.DatetimeIndex(sorted((A & B)))
    days = days[days <= EVIDENCE_CUTOFF_TS]      # lockbox, belt+braces
    head = days[0]
    a_only_win = sorted(d for d in A - B if d >= head
                        and d <= EVIDENCE_CUTOFF_TS)
    b_only_win = sorted(d for d in B - A if d >= head
                        and d <= EVIDENCE_CUTOFF_TS)
    adj = {c: DLP._adjust_split(raw[c], DLP.SPLIT_EVENTS.get(c))
           for c in LEGS}                        # event-guard leg (r239 law)
    legs = {}
    nan_free = True
    for c in LEGS:
        f = adj[c].reindex(days)
        o = f["open"].to_numpy(dtype=np.float64)
        cl = f["close"].to_numpy(dtype=np.float64)
        nan_free &= bool(np.isfinite(o).all() and np.isfinite(cl).all())
        # ADV20 = raw volume x raw close (CNY; fold-continuous; frozen probe
        # caliber); rolling over the TIMELINE (both legs bar every day)
        vc = (raw[c]["volume"] * raw[c]["close"]).reindex(days)
        adv = vc.rolling(20).mean().to_numpy(dtype=np.float64)
        legs[c] = {"open": o, "close": cl, "adv": adv}
    gates = panel_gates(days, a_only_win, b_only_win, nan_free)
    return {"days": days, "n": int(len(days)), "legs": legs,
            "gates": gates, "raw_rows": {c: int(len(raw[c]))
                                         for c in LEGS}}


def rebal_schedule(T):
    """21-trading-day rhythm, frozen anchor range(20, T-1, 21)."""
    return list(range(REBAL_FIRST, T - 1, REBAL_STEP))


# ---------------------------------------------------------------- signals


def ma200_matrix(close_arr):
    """Rolling MA200 of the adjusted closes (first valid at index 199)."""
    return pd.DataFrame(close_arr).rolling(MA_WIN).mean().to_numpy(
        dtype=np.float64)


def make_rotation_target(close_arr, ma200_arr, w, gate_on):
    """s3.1/s3.3 target rule at rebalance close r.
    Warmup: r < w (signal) or (gate and r < MA_WIN-1) -> None (=cash-honest).
    Tie (strict float equality): 50/50; under gate each half is gated on
    its own leg (frozen deterministic rule)."""
    def tgt(r):
        if r < w:
            return None
        if gate_on and r < MA_WIN - 1:
            return None
        rs = close_arr[r] / close_arr[r - w] - 1.0
        if not np.all(np.isfinite(rs)):
            return None
        winners = np.flatnonzero(rs == rs.max())
        out = {}
        if winners.size == len(LEGS):            # full tie
            for i in winners:
                if not gate_on:
                    out[LEG_BY_I[int(i)]] = 1.0 / len(LEGS)
                else:
                    m = ma200_arr[r, int(i)]
                    if np.isfinite(m) and close_arr[r, int(i)] > m:
                        out[LEG_BY_I[int(i)]] = 1.0 / len(LEGS)
            return out                          # both fail gate -> cash
        i = int(winners[0])
        if gate_on:
            m = ma200_arr[r, i]
            if not np.isfinite(m) or close_arr[r, i] <= m:
                return {}
        return {LEG_BY_I[i]: 1.0}
    return tgt


def make_null_target(seed):
    """s3.4: one uniform leg draw per rebalance point (rng consumed in
    schedule order); warmup override r < NULL_ACTIVATION_W."""
    rng = np.random.default_rng(seed)
    state = {"rng": rng, "draws": []}

    def tgt(r):
        d = int(state["rng"].integers(0, len(LEGS)))
        state["draws"].append(d)
        if r < NULL_ACTIVATION_W:
            return None
        return {LEGS[d]: 1.0}
    tgt.draws = state["draws"]
    return tgt


# ---------------------------------------------------------------- simulator


def simulate(P, target_fn, cost_fn, capital=CAPITAL):
    """Queue-fill daily sim on the intersection timeline (prereg s3.2/3.5).

    target_fn(r) evaluated at the signal close r -> {leg: weight} ({} or
    None = cash/warmup). Transitions re-anchor at each rebalance boundary
    (supersession); remainders are NOTIONAL at the anchor-day open; each
    fill day: sells first (cap 1% x ADV20(t-1)), then buys with available
    cash (same cap, lot-rounded); buys complete when the remainder is
    within one lot (rounding residue, honest granularity face)."""
    days, n = P["days"], P["n"]
    legs = P["legs"]
    sched = P.get("rebal_days") or rebal_schedule(n)
    rebal_set = set(sched)
    holds = {c: 0.0 for c in LEGS}
    cash = float(capital)
    rem_sell = {c: 0.0 for c in LEGS}
    rem_buy = {c: 0.0 for c in LEGS}
    target = {}
    active = None
    transitions = []
    rets = np.full(n, np.nan)
    eq_prev = None
    n_entries = n_trades = n_active_rebal = n_superseded = 0
    n_warmup_rebal = 0
    first_entry_day = None
    traded_notional = 0.0
    cost_total = 0.0
    cost_by_year = {}
    sold_notional = bought_notional = 0.0

    def _cap(c, t):
        a = legs[c]["adv"][t - 1] if t >= 1 else float("nan")
        if not np.isfinite(a):
            return 0.0, a          # conservative: no fill on unknown ADV
        return ADV_CAP * float(a), a

    for t in range(n):
        # -- rebalance boundary: signal at close r = t-1
        if t >= 1 and (t - 1) in rebal_set:
            r = t - 1
            if active is not None and not active["completed"]:
                active.update(completed=False, fill_days=None,
                              superseded_by_r=r)
                transitions.append(active)
                n_superseded += 1
                active = None
            tgt = target_fn(r)
            if tgt is None:
                n_warmup_rebal += 1
            tgt = {c: float(w) for c, w in (tgt or {}).items() if w > 0.0}
            px = {c: legs[c]["open"][t] for c in LEGS}
            eq_open = cash + sum(holds[c] * px[c] for c in LEGS)
            rs = {c: 0.0 for c in LEGS}
            rb = {c: 0.0 for c in LEGS}
            for c in LEGS:
                held_n = holds[c] * px[c]
                tgt_n = tgt.get(c, 0.0) * eq_open
                if held_n - tgt_n > SELL_EPS:
                    rs[c] = held_n - tgt_n        # exit OR overweight trim
                # buy anchor needs >= one buyable lot: sub-lot residues
                # (cost/rounding pockets) sit in cash -- no phantom churn
                if tgt_n - held_n > LOT * px[c] + SELL_EPS:
                    rb[c] = tgt_n - held_n        # underweight top-up
            if any(rs.values()) or any(rb.values()):
                active = {"anchor_r": int(r), "first_exec": int(t),
                          "target": dict(tgt), "completed": False,
                          "fill_days": None, "n_fills": 0,
                          "entry_notional": 0.0, "exit_notional": 0.0,
                          "entry_cost": 0.0, "exit_cost": 0.0,
                          "superseded_by_r": None}
                n_active_rebal += 1
                rem_sell = rs
                rem_buy = rb
            else:
                rem_sell = {c: 0.0 for c in LEGS}
                rem_buy = {c: 0.0 for c in LEGS}
            target = tgt
        # -- queue fills at the open (sells first, then cash-limited buys)
        if active is not None and not active["completed"]:
            y = str(days[t].year)
            cost_by_year.setdefault(y, 0.0)
            for c in LEGS:
                if rem_sell[c] > SELL_EPS and holds[c] > 1e-9:
                    cap, a = _cap(c, t)
                    px = legs[c]["open"][t]
                    f = min(rem_sell[c], cap)
                    sh = min(holds[c], f / px)
                    notional = float(sh * px)
                    if notional > 0.0:
                        cost = float(cost_fn(notional, a))
                        cash += notional - cost
                        holds[c] -= sh
                        rem_sell[c] -= notional
                        n_trades += 1
                        active["n_fills"] += 1
                        active["exit_notional"] += notional
                        active["exit_cost"] += cost
                        traded_notional += notional
                        sold_notional += notional
                        cost_total += cost
                        cost_by_year[y] += cost
            for c in LEGS:
                if rem_buy[c] > SELL_EPS:
                    cap, a = _cap(c, t)
                    px = legs[c]["open"][t]
                    # affordability loop: notional + cost must fit in cash
                    # (cost floor can make a full-cap lot unbuyable -> step
                    # down one lot at a time; zero-cash -> no buy)
                    lots = 0
                    notional = cost = 0.0
                    trial = int(min(rem_buy[c], cap, max(cash, 0.0))
                               // px // LOT) * LOT
                    while trial > 0:
                        n_tr = float(trial * px)
                        c_tr = float(cost_fn(n_tr, a))
                        if n_tr + c_tr <= cash or trial <= LOT:
                            lots, notional, cost = trial, n_tr, c_tr
                            break
                        trial -= LOT
                    if lots > 0 and notional + cost <= cash:
                        cash -= notional + cost
                        holds[c] += lots
                        rem_buy[c] -= notional
                        n_trades += 1
                        n_entries += 1
                        active["n_fills"] += 1
                        active["entry_notional"] += notional
                        active["entry_cost"] += cost
                        traded_notional += notional
                        bought_notional += notional
                        cost_total += cost
                        cost_by_year[y] += cost
                        if first_entry_day is None:
                            first_entry_day = t
            sells_done = all(holds[c] <= 1e-9 or rem_sell[c] <= SELL_EPS
                             for c in LEGS)
            want = [c for c in LEGS
                    if rem_buy[c] > LOT * legs[c]["open"][t] + SELL_EPS]
            buys_done = not want
            # cash-exhausted terminal: sells done AND the remaining cash
            # cannot buy one lot of any still-wanting leg -> the queue is
            # as-done-as-possible (residue disclosed; never a stall)
            cash_done = (not want) or cash < LOT * min(
                legs[c]["open"][t] for c in want)
            if sells_done and (buys_done or cash_done):
                active["completed"] = True
                active["fill_days"] = int(t - active["first_exec"] + 1)
                transitions.append(active)
                active = None
                rem_sell = {c: 0.0 for c in LEGS}
                rem_buy = {c: 0.0 for c in LEGS}
        # -- close valuation
        eq = cash + sum(holds[c] * legs[c]["close"][t] for c in LEGS)
        if eq_prev is None:
            rets[t] = np.nan
        else:
            rets[t] = eq / eq_prev - 1.0 if eq_prev > 0 else 0.0
        eq_prev = eq
    truncated = bool(active is not None and not active["completed"])
    if active is not None and not active["completed"]:
        transitions.append(active)      # window-end open transition
    fill_days_list = [tr_["fill_days"] for tr_ in transitions
                      if tr_["completed"]]
    series = pd.Series(rets, index=days)
    transitions = [{
        **tr_,
        "entry_notional": float(tr_["entry_notional"]),
        "exit_notional": float(tr_["exit_notional"]),
        "entry_cost": float(tr_["entry_cost"]),
        "exit_cost": float(tr_["exit_cost"]),
    } for tr_ in transitions]
    return {
        "returns": series,
        "n_entries": n_entries, "n_trades": n_trades,
        "n_rebal": len(sched), "n_active_rebal": n_active_rebal,
        "n_warmup_rebal": n_warmup_rebal,
        "n_transitions": len(transitions),
        "n_completed": len(fill_days_list), "n_superseded": n_superseded,
        "fill_days_list": fill_days_list,
        "fill_days_max": max(fill_days_list) if fill_days_list else None,
        "fill_days_mean": (round(float(np.mean(fill_days_list)), 2)
                           if fill_days_list else None),
        "truncated": truncated,
        "first_entry_day": first_entry_day,
        "traded_notional_total": round(float(traded_notional), 2),
        "sold_notional_total": round(float(sold_notional), 2),
        "bought_notional_total": round(float(bought_notional), 2),
        "cost_total": round(float(cost_total), 2),
        "cost_by_year": {y: round(float(v), 2) for y, v in
                         sorted(cost_by_year.items())},
        "transitions": transitions,
        "inv_rebal_frac": (round(n_active_rebal / len(sched), 4)
                           if sched else 0.0),
    }


# ---------------------------------------------------------------- metrics


def _sharpe(rets):
    r = rets.dropna()
    if len(r) < 20 or float(r.std()) == 0:
        return None
    return round(float(r.mean() / r.std() * math.sqrt(PBP)), 4)


def _ann(rets):
    r = rets.dropna()
    if len(r) < 20:
        return None
    total = float((1.0 + r).prod())
    return round(total ** (PBP / len(r)) - 1.0, 6)


def _max_dd(eq):
    if len(eq) < 2:
        return None
    return round(float((eq / eq.cummax() - 1.0).min()), 6)


def _crisis_log(rets):
    rows = []
    for day, v in rets.iloc[1:].items():
        if np.isfinite(v) and abs(v) >= CRISIS_LOG_ABS_R and any(
                s <= str(day.date()) <= e for s, e in CRISIS_WINDOWS):
            rows.append({"day": str(day.date()), "r1": round(float(v), 6)})
    return rows


def _exempt(rets, bounds):
    """Hard-bound triad (s4): max|d1| day inside a frozen crisis window ->
    single-point exemption column (stats ex-that-day), disclosure only."""
    if not bounds["in_crisis_window"]:
        return {"applied": False}
    d1 = rets.iloc[1:]
    drop = pd.Timestamp(bounds["argmax_day"])
    kept = d1[d1.index != drop]
    return {"applied": True, "exempted_day": bounds["argmax_day"],
            "sharpe_ex": _sharpe(kept), "ann_ret_ex": _ann(kept)}


def metrics(rec):
    rets = rec["returns"]
    eq = (1.0 + rets.fillna(0.0)).cumprod()
    out = {
        "sharpe": _sharpe(rets), "ann_ret": _ann(rets),
        "max_dd": _max_dd(eq),
        "n_entries": rec["n_entries"], "n_trades": rec["n_trades"],
        "n_rebal": rec["n_rebal"], "n_active_rebal": rec["n_active_rebal"],
        "n_warmup_rebal": rec["n_warmup_rebal"],
        "n_transitions": rec["n_transitions"],
        "n_completed": rec["n_completed"],
        "n_superseded": rec["n_superseded"],
        "fill_days_max": rec["fill_days_max"],
        "fill_days_mean": rec["fill_days_mean"],
        "truncated": rec["truncated"],
        "first_entry_day": rec["first_entry_day"],
        "traded_notional_total": rec["traded_notional_total"],
        "sold_notional_total": rec["sold_notional_total"],
        "bought_notional_total": rec["bought_notional_total"],
        "cost_total": rec["cost_total"], "cost_by_year": rec["cost_by_year"],
        "inv_rebal_frac": rec["inv_rebal_frac"],
    }
    oos = rets[rets.index >= pd.Timestamp(OOS_START)]
    out["oos"] = {"sharpe": _sharpe(oos), "ann_ret": _ann(oos),
                  "n_days": int(len(oos))}
    out["yearly"] = {int(y): round(float(g.iloc[-1] / g.iloc[0] - 1.0), 4)
                     for y, g in eq.groupby(eq.index.year)}
    d1 = rets.iloc[1:]
    a = np.abs(d1.to_numpy())
    finite = np.isfinite(a)
    a_f = a[finite]
    argmax_day = str(d1.index[int(np.argmax(a))].date()) if len(a) else None
    out["d1_bounds"] = {
        "median": float(np.median(a_f)) if a_f.size else None,
        "p99_9": float(np.percentile(a_f, 99.9)) if a_f.size else None,
        "max": float(a_f.max()) if a_f.size else None,
        "argmax_day": argmax_day,
        "in_crisis_window": bool(any(
            s <= argmax_day <= e for s, e in CRISIS_WINDOWS))
        if argmax_day else False,
    }
    out["crisis_log"] = _crisis_log(rets)
    out["exempt_single_point"] = _exempt(rets, out["d1_bounds"])
    out["cost_stability"] = None      # filled at batch level (judged x2)
    return out


# ---------------------------------------------------------------- checkpoints


def _ck_path(unit):
    return os.path.join(CKPT_DIR, unit + ".npz")


def _ck_save(unit, rec, series):
    os.makedirs(CKPT_DIR, exist_ok=True)
    r = {k: v for k, v in rec.items() if k != "returns"}
    np.savez(_ck_path(unit), meta=json.dumps(r, default=str),
             returns=np.asarray(series, dtype=np.float64),
             index=np.asarray([str(d.date()) for d in series.index]))


def _ck_load(unit, idx):
    """Exact resume only on date-window match; any drift -> recompute."""
    p = _ck_path(unit)
    if not os.path.exists(p):
        return None
    try:
        z = np.load(p, allow_pickle=False)
        meta = json.loads(str(z["meta"]))
        dates = [str(x) for x in z["index"]]
        if len(dates) != len(idx) or dates[0] != str(idx[0].date()) \
                or dates[-1] != str(idx[-1].date()):
            return None
        out = dict(meta)
        out["returns"] = pd.Series(z["returns"], index=idx)
        return out
    except Exception:
        return None


def _write_ckpt_gitignore():
    os.makedirs(CKPT_DIR, exist_ok=True)
    p = os.path.join(CKPT_DIR, ".gitignore")
    if not os.path.exists(p):
        with open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("*\n!.gitignore\n")


def _compact_transitions(rec):
    rows = []
    for tr_ in rec["transitions"]:
        rows.append({
            "anchor_r": int(tr_["anchor_r"]),
            "first_exec": int(tr_["first_exec"]),
            "target": {k: float(v) for k, v in tr_["target"].items()},
            "completed": bool(tr_["completed"]),
            "fill_days": (int(tr_["fill_days"])
                          if tr_["fill_days"] is not None else None),
            "n_fills": int(tr_["n_fills"]),
            "entry_notional": round(float(tr_["entry_notional"]), 2),
            "exit_notional": round(float(tr_["exit_notional"]), 2),
            "entry_cost": round(float(tr_["entry_cost"]), 2),
            "exit_cost": round(float(tr_["exit_cost"]), 2),
            "superseded_by_r": (int(tr_["superseded_by_r"])
                                if tr_["superseded_by_r"] is not None
                                else None),
        })
    return rows


# ---------------------------------------------------------------- H4 faces


def h4_family_faces(judged_series):
    """s1 H4-style disclosures (never admission). 510880 leg daily returns
    (= ALLOC P5 slot leg face); family DIV_LOWVOL_P1 C1 x2 return series is
    not persisted in its artifact -> honest unavailable, prereg band stands."""
    legs = CURRENT_PANEL["legs"]
    days = CURRENT_PANEL["days"]
    out = {}
    leg510880 = pd.Series(
        np.append([np.nan], legs[LEGS[0]]["close"][1:]
                  / legs[LEGS[0]]["close"][:-1] - 1.0), index=days)
    for cell, rets in judged_series.items():
        v510, ov = _corr(rets, leg510880)
        out[cell] = {
            "corr_vs_510880_leg": {"corr": v510, "overlap_days": ov,
                                   "note": "ALLOC P5 slot leg face "
                                   "(disclosure only, line judgments never "
                                   "cross-wired)"},
            "corr_vs_div_lowvol_p1_c1_x2": {
                "status": "unavailable_in_artifact",
                "note": "family artifact carries per-face metrics only, no "
                        "return series; prereg s1 forecast band 0.6-0.9 "
                        "stands as the declared expectation (same-instrument "
                        "domain)"},
        }
    return out


# ---------------------------------------------------------------- run / cli


def run() -> int:
    global CURRENT_PANEL
    t0 = time.time()
    if os.environ.get("CN_DIV_LOWVOL_ROT_P1_REFINALIZE") != "1" \
            and os.path.exists(OUT_JSON):
        try:
            j = json.load(open(OUT_JSON, encoding="utf-8"))
            if j.get("ledger"):
                print("idempotent fast path: results/cn_div_lowvol_rot/"
                      "p1_results.json already finalized (ledger block "
                      "present); CN_DIV_LOWVOL_ROT_P1_REFINALIZE=1 = only "
                      "redo")
                return 0
        except Exception:
            pass
    if sg.SEED_REGISTRY.get("cn_div_lowvol_rot_p1") != SEED_BASE:
        print("VOID: seed base cn_div_lowvol_rot_p1 not registered in "
              "science_gates.SEED_REGISTRY (prereg s3.4: registered AT the "
              "R250 freeze commit)")
        return 2

    P = load_panel()
    CURRENT_PANEL = P
    if not P["gates"]["all_ok"]:
        print("VOID: panel gate FAILED:",
              json.dumps(P["gates"], ensure_ascii=False))
        return 2
    _write_ckpt_gitignore()
    _log(f"panel gates OK: T={P['gates']['T']} cutoff="
         f"{P['gates']['cutoff']} a_only={P['gates']['a_only_window']}"
         f" raw_rows={P['raw_rows']}")

    days, n = P["days"], P["n"]
    close_arr = np.vstack([P["legs"][c]["close"] for c in LEGS]).T
    ma200 = ma200_matrix(close_arr)
    sched = rebal_schedule(n)

    resumed = []

    def run_unit(unit, target_fn, cost_fn):
        ck = _ck_load(unit, days)
        if ck is not None and "returns" in ck:
            resumed.append(unit)
            return ck
        rec = simulate(P, target_fn, cost_fn)
        _ck_save(unit, rec, rec["returns"])
        return rec

    # -- judged cells x3 faces (s3.5: judge = x2, x1/x3 disclosure)
    cell_recs = {}
    for w in W_SET:
        for gate_on in (False, True):
            cell = f"W{w}_{'gate' if gate_on else 'bare'}"
            tf = make_rotation_target(close_arr, ma200, w, gate_on)
            for face, cost_fn in FACES.items():
                cell_recs[(cell, face)] = run_unit(
                    f"cell_{cell}_{face}", tf, cost_fn)
            m = metrics(cell_recs[(cell, JUDGED_FACE)])
            _log(f"cell {cell}: {JUDGED_FACE} sharpe={m['sharpe']} "
                 f"entries={m['n_entries']} fill_max={m['fill_days_max']} "
                 f"superseded={m['n_superseded']}")

    # -- R240 sanity law: target machinery never produced a non-warmup
    #    evaluation = signal face broken, refuse the verdict (a gate cell
    #    that legitimately never opens is NOT this -- warmup still counts)
    for cell in JUDGED_CELLS:
        rec = cell_recs[(cell, JUDGED_FACE)]
        if rec["n_active_rebal"] == 0 and rec["n_warmup_rebal"] == 0:
            print(f"VOID: {cell} zero rebalance evaluations -- signal "
                  "machinery broken, refusing verdict")
            return 2

    # -- K=50 nulls on the judged x2 face (s3.4)
    null_recs = []
    null_draws_head = None
    for k in range(K_NULLS):
        tf = make_null_target(SEED_BASE + k)
        rec = run_unit(f"null_{k:02d}", tf, FACES[JUDGED_FACE])
        null_recs.append(rec)
        if k == 0:
            null_draws_head = list(tf.draws[:12])
    null_vals = [(_sharpe(r["returns"]) or 0.0) for r in null_recs]
    mu, sigma = float(np.mean(null_vals)), float(np.std(null_vals, ddof=1))
    null_pool = {
        "values": [round(v, 6) for v in null_vals],
        "coverage": {"n_values": len(null_vals), "mu": mu, "sigma": sigma,
                     "schemas_parsed": [f"cn_div_lowvol_rot_p1: {K_NULLS} "
                                       f"random-leg 21d-rhythm rotation "
                                       f"sleeves (seeds 20260980+i, x2 "
                                       f"face, W63-bare warmup)"],
                     "known_unparsed": []},
    }
    _log(f"nulls: K={K_NULLS} mu={mu:.4f} sigma={sigma:.4f}")

    # -- passive baselines, W63-bare anchored, x2 face (s3.4)
    def ew_target(r):
        return None if r < NULL_ACTIVATION_W else \
            {LEGS[0]: 0.5, LEGS[1]: 0.5}

    def bh_target(leg):
        def f(r):
            return None if r < NULL_ACTIVATION_W else {leg: 1.0}
        return f

    ew_rec = run_unit("baseline_ew_pair", ew_target, FACES[JUDGED_FACE])
    bh_recs = {c: run_unit(f"baseline_buyhold_{c}", bh_target(c),
                           FACES[JUDGED_FACE]) for c in LEGS}

    # -- census gate (r188 law): every unit computed before finalize
    units_expected = (len(JUDGED_CELLS) * len(FACES) + K_NULLS + 3)
    units_have = (len(cell_recs) + len(null_recs) + 1 + len(bh_recs))
    if units_have < units_expected:
        print(f"finalize census gate: {units_have}/{units_expected} units "
              "-- premature finalize refused, no artifact written")
        return 2

    # -- gates (shared library, zero hand-copied lines; prereg s4)
    line = sg.skill_line_v2(batch_cells=BATCH_CELLS, pool="core48",
                            null_pool=null_pool)
    g1, dsr, g2 = {}, {}, {}
    judged_series = {}
    for cell in JUDGED_CELLS:
        rec = cell_recs[(cell, JUDGED_FACE)]
        rets = rec["returns"].iloc[1:]        # drop NaN head interval
        judged_series[cell] = rets
        g1[cell] = sg.g1_prime_v2(
            sharpe_full=_sharpe(rets), returns=rets,
            batch_cells=BATCH_CELLS, pool="core48", null_pool=null_pool,
            n_trades=rec["n_trades"], n_entries=rec["n_entries"])
        dsr[cell] = sg.deflated_sharpe_ratio(
            rets, n_trials=line["n_eff"], var_null_sr=sigma ** 2)
    fam_pbo = cscv_pbo(align_returns(judged_series))
    for cell in JUDGED_CELLS:
        g2[cell] = sg.g2_registration_v2(
            g1_pass=bool(g1[cell]["pass_v2"]), dsr=dsr[cell],
            pbo=fam_pbo["pbo"])

    g1_errs = {c: v.get("error") for c, v in g1.items()
               if isinstance(v, dict) and "error" in v}
    if g1_errs:
        first = next(iter(g1_errs.items()))
        print(f"finalize FAIL-CLOSED: g1 errored for {len(g1_errs)}/"
              f"{len(g1)} cells (first: {first[0]} -> "
              f"{str(first[1])[:120]}) -- no artifact written")
        return 2

    # -- D6 (registered members reject face + same-batch disclosure)
    try:
        member_rets, member_cutoffs = load_member_rets()
        d6 = {c: d6_block(judged_series[c], member_rets)
              for c in JUDGED_CELLS}
        d6["member_cutoffs"] = member_cutoffs
    except Exception as exc:
        d6 = {"status": "pending_error", "error": repr(exc)[:200]}
    same_batch = {}
    for a in JUDGED_CELLS:
        row = {}
        for b in JUDGED_CELLS:
            if a == b:
                continue
            v, ov = _corr(judged_series[a], judged_series[b])
            row[b] = {"corr": v, "overlap_days": ov}
        same_batch[a] = row
    h4 = h4_family_faces(judged_series)

    # -- descriptive clauses + x1/x3 stability vs judged x2 (s4)
    descriptive = {}
    for cell in JUDGED_CELLS:
        xm = metrics(cell_recs[(cell, JUDGED_FACE)])
        yr2 = xm["yearly"]
        stable = {}
        for face in ("x1", "x3"):
            yf = metrics(cell_recs[(cell, face)])["yearly"]
            common = [y for y in yr2 if y in yf]
            stable[face] = {
                "sign_match_years": int(sum(
                    1 for y in common if (yr2[y] > 0) == (yf[y] > 0))),
                "n_common_years": len(common),
            }
        xm["cost_stability"] = stable
        descriptive[cell] = {
            "full_ann_positive": bool((xm["ann_ret"] or 0) > 0),
            "oos_dual_positive": bool(
                (xm["oos"]["sharpe"] or 0) > 0
                and (xm["oos"]["ann_ret"] or 0) > 0),
            "max_dd_line_pass": bool((xm["max_dd"] or 0) >= MAXDD_LINE),
            "no_crash_year": bool(all(
                v > CRASH_YEAR_LINE for v in yr2.values())),
            "crash_year_line": CRASH_YEAR_LINE,
            "x1_x3_yearly_stability": stable,
        }

    # -- regime descriptive columns (imported layer, never a switch)
    reg_col = regime_v3_column(days)
    gate_axis = {}
    for cell in JUDGED_CELLS:
        w = int(cell.split("_")[0][1:])
        gate_on = cell.endswith("_gate")
        tf = make_rotation_target(close_arr, ma200, w, gate_on)
        per_year = {}
        leg_counts = {c: 0 for c in LEGS}
        for r in sched:
            y = int(days[r].year)
            per_year.setdefault(y, {"cash": 0, "warmup": 0})
            tgt = tf(r)
            if tgt is None:
                per_year[y]["warmup"] += 1
            elif not tgt:
                per_year[y]["cash"] += 1
            else:
                for c in tgt:
                    leg_counts[c] += 1
        gate_axis[cell] = {"rebal_target_counts_per_year": per_year,
                           "leg_pick_counts": leg_counts}

    # -- cells block (judged face carries the per-transition fill rows)
    cells_out = {}
    for cell in JUDGED_CELLS:
        per_face = {}
        for face in FACES:
            mrec = metrics(cell_recs[(cell, face)])
            if face == JUDGED_FACE:
                mrec["cost_stability"] = descriptive[cell][
                    "x1_x3_yearly_stability"]
                mrec["transitions"] = _compact_transitions(
                    cell_recs[(cell, face)])
            per_face[face] = mrec
        cells_out[cell] = per_face
    judged_returns_audit = {
        cell: [round(float(v), 6) for v in judged_series[cell].tolist()]
        for cell in JUDGED_CELLS}

    nulls_out = {
        "config": {"base": SEED_BASE, "registered": "cn_div_lowvol_rot_p1",
                   "draws": K_NULLS, "face": f"{JUDGED_FACE}_judged",
                   "rule": "one uniform leg draw per rebalance point "
                           "(rng per sleeve, consumed in schedule order); "
                           "warmup = W63-bare activation; gate cells share "
                           "the bare-null distribution (prereg s3.4 "
                           "conservative note)",
                   "null0_draws_head": null_draws_head},
        "n_values": len(null_vals),
        "values_rounded": null_pool["values"],
        "coverage": null_pool["coverage"],
    }
    baselines_out = {
        "ew_pair_5050": metrics(ew_rec),
        "buy_hold_510880": metrics(bh_recs[LEGS[0]]),
        "buy_hold_512890": metrics(bh_recs[LEGS[1]]),
        "note": "W63-bare-anchored passive faces (disclosure only); "
                "skill-line passive anchor = core48 pool via the shared "
                "library (s4); EW re-sets to 50/50 at each active "
                "rebalance through the same queue machinery",
    }

    led = sg.append_ledger(
        "CN-DIV-LOWVOL-ROT-P1", LEDGER_TRIALS,
        file_name="results/cn_div_lowvol_rot/p1_results.json",
        evidence_cutoff=EVIDENCE_CUTOFF,
        note="4 judged cells {W63,W252}x{bare,MA200-gate} 21d-rhythm "
             "rotation + K50 random-leg nulls (seeds 20260980+i, "
             "registered cn_div_lowvol_rot_p1 at the R250 freeze commit); "
             "V2 ADV20-tiered cost, judge face x2, 1%ADV queue-fill; "
             "prereg research/CN_DIV_LOWVOL_ROT_PREREG.md frozen R250 + "
             "R251 zero-run amendment; T-2026-09-26-73 s3 slice-2")

    att = json.load(open(ATT_JSON, encoding="utf-8"))
    d6_rejects = ({c: ((d6.get(c) or {}).get("member_face", {})
                       .get("reject")) for c in JUDGED_CELLS}
                  if d6.get("status") != "pending_error" else None)
    att["entries"].append({
        "batch": "CN-DIV-LOWVOL-ROT-P1",
        "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
        "kind": "measurement",
        "cells_ledger_delta": LEDGER_TRIALS,
        "ledger_total_after": led["total"],
        "gates": {
            "panel_pass": True,
            "g1_prime_pass": {c: bool(g1[c]["pass_v2"])
                              for c in JUDGED_CELLS},
            "g2_eligible": {c: bool(g2[c]["eligible_v2"])
                            for c in JUDGED_CELLS},
            "d6_reject": d6_rejects,
        },
        "eliminated": LEDGER_TRIALS - sum(
            1 for c in JUDGED_CELLS if g2[c]["eligible_v2"]),
        "refs": {"prereg": "research/CN_DIV_LOWVOL_ROT_PREREG.md",
                 "ticket": TICKET},
    })

    import hashlib
    prereg_sha = hashlib.sha256(
        open(PREREG, "rb").read().replace(b"\r\n", b"\n")).hexdigest()

    payload = {
        **sg.cutoff_meta(EVIDENCE_CUTOFF),
        "meta": {
            "batch": "CN-DIV-LOWVOL-ROT-P1", "ticket": TICKET,
            "prereg": "research/CN_DIV_LOWVOL_ROT_PREREG.md",
            "prereg_sha256_lf_normalized": prereg_sha,
            "judge_face": f"{JUDGED_FACE} (whole-V2 doubled, side_cost_x2 "
                          "family precedent, always on); x1/x3 disclosure "
                          "tracks",
            "seed_base_registered": "cn_div_lowvol_rot_p1=20260980",
            "cost_basis": "V2 ADV20-tiered (knowledge/rules.py CostPatch "
                          "single source) + 1% ADV participation cap with "
                          "DAY-QUEUED fills (fill_days counters per "
                          "transition; family fill_refusal -> queuing "
                          "correction per prereg s3.5)",
            "accounting": "signal close r -> fills from open r+1 (T+1); "
                          "21-trading-day rhythm range(20,T-1,21); daily "
                          "close valuation; cash zero-yield; warmup = "
                          "cash-honest; tie -> 50/50 (gate cells: per-leg "
                          "gate on each half); re-anchor supersedes "
                          "incomplete transitions (fill_days=None)",
            "panel": "intersection timeline T=1862 (R251 amendment); "
                     "prices = DLP._adjust_split post-event face (512890 "
                     "factor 0.5; r239 event-guard law); ADV20 = raw "
                     "volume x close rolling-20 (fold-continuous CNY); "
                     "corpus twins zero network",
            "machine": _machine_id(),
        },
        "panel_gates": P["gates"],
        "raw_corpus_rows": P["raw_rows"],
        "cells": cells_out,
        "nulls": nulls_out,
        "baselines": baselines_out,
        "skill_line": line,
        "g1_prime_v2": g1,
        "g2_registration_v2": g2,
        "family_pbo": {k: fam_pbo[k] for k in
                       ("pbo", "n_blocks", "n_trials", "n_rows",
                        "n_combinations") if k in fam_pbo},
        "dsr": dsr,
        "d6_correlation": d6,
        "same_batch_corr": same_batch,
        "h4_disclosure_faces": h4,
        "descriptive": descriptive,
        "regime_columns": {
            "market_v3_axis": reg_col,
            "rotation_gate_axis": gate_axis,
        },
        "judged_x2_returns_6dp_audit": judged_returns_audit,
        "n_trials": LEDGER_TRIALS,
        "audit": {
            "elapsed_sec": round(time.time() - t0, 1),
            "workers": 1,
            "units_expected": units_expected,
            "units_fresh_this_run": units_expected - len(resumed),
            "units_resumed_from_checkpoint": len(resumed),
            "resumed_units_head": resumed[:80],
            "blind_run_flags": {
                "deterministic_sim": "no wall-clock inside sim outputs; "
                                     "double-run byte identity via selftest",
                "queue_rule_frozen": "sells before buys; caps from "
                                     "ADV20(t-1); buys lot-rounded; "
                                     "completion = sells done AND buys "
                                     "within one lot",
            },
        },
        "ledger": led,
    }
    json.loads(json.dumps(payload, default=str))     # validate before write
    tmp = OUT_JSON + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1, default=str)
    os.replace(tmp, OUT_JSON)
    tmp = ATT_JSON + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(att, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, ATT_JSON)
    _write_csv(cells_out, g1, g2, d6)
    _log(f"finalize: ledger total={led['total']} | g1="
         f"{ {c: g1[c]['pass_v2'] for c in JUDGED_CELLS} } g2="
         f"{ {c: g2[c]['eligible_v2'] for c in JUDGED_CELLS} } | "
         f"elapsed={round(time.time() - t0, 1)}s")
    print(f"[cn_div_lowvol_rot] written {OUT_JSON}; g1="
          f"{ {c: g1[c]['pass_v2'] for c in JUDGED_CELLS} }")
    return 0


def _write_csv(cells_out, g1, g2, d6):
    import csv as _csv
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as fh:
        w = _csv.writer(fh)
        w.writerow(["cell", "face", "sharpe", "ann_ret", "max_dd",
                    "oos_sharpe", "oos_ann", "n_entries", "n_trades",
                    "n_active_rebal", "fill_days_max", "n_superseded",
                    "traded_notional", "cost_total", "g1_pass",
                    "g2_eligible", "d6_max_abs_corr"])
        for cell, per_face in cells_out.items():
            for face, m in per_face.items():
                mf = ((d6.get(cell) or {}).get("member_face", {})
                      if face == JUDGED_FACE else {})
                w.writerow([cell, face, m["sharpe"], m["ann_ret"],
                            m["max_dd"], m["oos"]["sharpe"],
                            m["oos"]["ann_ret"], m["n_entries"],
                            m["n_trades"], m["n_active_rebal"],
                            m["fill_days_max"], m["n_superseded"],
                            m["traded_notional_total"], m["cost_total"],
                            g1[cell]["pass_v2"] if face == JUDGED_FACE
                            else "",
                            g2[cell]["eligible_v2"]
                            if face == JUDGED_FACE else "",
                            mf.get("max_abs_corr", "")])


def _machine_id():
    try:
        return json.load(open(os.path.join(ROOT, "fleet", "machine.json"),
                              encoding="utf-8-sig"))["machine_id"]
    except Exception:
        return os.environ.get("COMPUTERNAME", "unknown")


# ---------------------------------------------------------------- selftest

CURRENT_PANEL = None


def _mk_panel(o_a=1.0, o_b=1.0, adv_a=1e9, adv_b=1e9, n=60, nan_adv=None):
    """Hermetic 2-leg panel: flat prices (cost/queue arithmetic isolation),
    caller-set constant ADV faces, optional per-day ADV NaN override."""
    days = pd.bdate_range("2020-01-01", periods=n)
    legs = {}
    for c, px, adv in ((LEGS[0], o_a, adv_a), (LEGS[1], o_b, adv_b)):
        arr_adv = np.full(n, float(adv))
        if nan_adv:
            for i in nan_adv:
                arr_adv[i] = np.nan
        legs[c] = {"open": np.full(n, float(px)),
                   "close": np.full(n, float(px)),
                   "adv": arr_adv}
    return {"days": days, "n": n, "legs": legs}


def selftest() -> int:
    fails = []

    def ok(fid, cond, detail=""):
        print(f"  [{'PASS' if cond else 'FAIL'}] {fid} {detail}")
        if not cond:
            fails.append(fid)

    # frozen constants drift guards (prereg numbers incl. R251 amendment)
    ok("[C1] frozen constants", all([
        T_JOINT_FROZEN == 1862 and JOINT_FIRST_FROZEN == "2019-01-18",
        MISMATCH_FROZEN == ["2021-10-22"],
        sg.SEED_REGISTRY.get("cn_div_lowvol_rot_p1") == SEED_BASE
        and SEED_BASE == 20_260_980,
        K_NULLS == 50 and BATCH_CELLS == 4 and LEDGER_TRIALS == 54,
        W_SET == (63, 252) and MA_WIN == 200 and REBAL_STEP == 21
        and REBAL_FIRST == 20,
        CAPITAL == 1_000_000.0 and LOT == 100
        and abs(ADV_CAP - krules.ADV_FILL_CAP_RATE) < 1e-15
        and ADV_CAP == 0.01,
        JUDGED_FACE == "x2" and set(FACES) == {"x1", "x2", "x3"}
        and FACES["x1"].__name__ == "side_cost_v2"
        and FACES["x2"].__name__ == "side_cost_x2"
        and FACES["x3"].__name__ == "side_cost_x3",
        D6_REJECT == 0.7 and MAXDD_LINE == -0.35
        and CRASH_YEAR_LINE == -0.30,
        EVIDENCE_CUTOFF == "2026-09-22" and OOS_START == "2025-01-01"
        and IS_END == "2024-12-31",
        JUDGED_CELLS == ("W63_bare", "W252_bare", "W63_gate", "W252_gate"),
        CRISIS_WINDOWS == [("2020-03-01", "2020-03-31"),
                           ("2021-02-01", "2021-02-28"),
                           ("2024-09-01", "2024-10-31")],
    ]))

    # [C2] panel gate fail-closed (R251 amendment numbers)
    days_ok = pd.bdate_range(JOINT_FIRST_FROZEN, periods=1861)
    days_ok = days_ok.append(pd.DatetimeIndex([EVIDENCE_CUTOFF_TS]))
    ok("[C2] panel gate pass/fail faces",
       panel_gates(days_ok, [pd.Timestamp("2021-10-22")], [], True)
       ["all_ok"] is True
       and panel_gates(days_ok[:-1], [], [], True)["all_ok"] is False
       and panel_gates(days_ok, [], [], True)["all_ok"] is False
       and panel_gates(days_ok, [pd.Timestamp("2021-10-22")], [], False)
       ["all_ok"] is False
       and panel_gates(days_ok, [pd.Timestamp("2019-03-08")], [], True)
       ["all_ok"] is False
       and panel_gates(days_ok, [pd.Timestamp("2021-10-22")],
                       [pd.Timestamp("2020-06-08")], True)["all_ok"]
       is False)

    # [F1] split event guard through the REAL adjust path (r239 law)
    raw = pd.DataFrame(
        {"close": [1.639] * 5 + [0.801] * 5},
        index=pd.bdate_range("2021-10-14", periods=10))
    ev = {"first_post_split_bar": "2021-10-21", "factor": 0.5,
          "suspended_bars": ["2021-10-22"]}
    adjf = DLP._adjust_split(raw, ev)
    r_adj = float(adjf["close"].iloc[5] / adjf["close"].iloc[4]) - 1.0
    r_raw = float(raw["close"].iloc[5] / raw["close"].iloc[4]) - 1.0
    ok("[F1] fold event adjusted face ~ -2.3pct (raw -51pct killed)",
       abs(r_adj - (0.801 / (1.639 * 0.5) - 1.0)) < 1e-12
       and abs(r_adj - (-0.022575)) < 1e-4 and r_raw < -0.5
       and DLP.SPLIT_EVENTS["512890"]["factor"] == 0.5
       and DLP.SPLIT_EVENTS["512890"]["suspended_bars"]
       == ["2021-10-22"]
       and DLP.SPLIT_EVENTS.get("510880") is None)

    # [F2] queue-fill hand math: caps, lot rounding, sell->buy funding
    #      order, supersession, fill_days, per-transition notionals
    P = _mk_panel(o_a=1.0, o_b=1.0, adv_a=10_000, adv_b=100_000, n=45)
    P["rebal_days"] = [5, 10]

    def tf(r):
        return {LEGS[0]: 1.0} if r == 5 else (
            {LEGS[1]: 1.0} if r == 10 else None)

    rec = simulate(P, tf, lambda g, a: 0.0, capital=1000.0)
    # cap_A = 1% x 10000 = 100/day. A-buy queues from exec day 6:
    # days 6..10 five fills x 100 = 500 bought, rem 500 when r=10
    # SUPERSEDES (fill_days=None, entry_notional=500);
    # then sell A 500 @100/day (days 11..15) funding B buys:
    # day 11 sell 100 -> cash 600 -> B buy 600 (cash-limited, not the
    # 1000 cap); days 12-15 sell+buy 100/day; complete day 15 -> 5 days.
    tr_ = rec["transitions"]
    ok("[F2] superseded transition honest",
       len(tr_) == 2 and tr_[0]["completed"] is False
       and tr_[0]["fill_days"] is None
       and tr_[0]["superseded_by_r"] == 10
       and tr_[0]["n_fills"] == 5
       and round(tr_[0]["entry_notional"], 2) == 500.0
       and rec["n_superseded"] == 1)
    ok("[F2] completed transition queue arithmetic",
       tr_[1]["completed"] is True and tr_[1]["fill_days"] == 5
       and tr_[1]["n_fills"] == 10
       and round(tr_[1]["entry_notional"], 2) == 1000.0
       and round(tr_[1]["exit_notional"], 2) == 500.0
       and rec["n_entries"] == 10 and rec["n_trades"] == 15
       and rec["first_entry_day"] == 6
       and rec["fill_days_list"] == [5]
       and rec["n_active_rebal"] == 2)
    ok("[F2] equity flat under zero cost + no warmup rebalances",
       bool(np.nanmax(np.abs(rec["returns"].dropna().to_numpy()))
            < 1e-12)
       and rec["n_warmup_rebal"] == 0)
    # cost leg: fixed 10bp on every fill's notional; lot rounding bites
    # day 11 (cash 599.4 -> 5 lots = 500) -> B buys 900 not 1000
    rec_c = simulate(P, tf, lambda g, a: 0.001 * g, capital=1000.0)
    ok("[F2] cost booked per fill on traded notional",
       abs(rec_c["cost_total"] - 1.9) < 0.01
       and rec_c["traded_notional_total"] == 1900.0
       and rec_c["sold_notional_total"] == 500.0
       and rec_c["bought_notional_total"] == 1400.0,
       f"cost={rec_c['cost_total']}")

    # [F3] same-target re-anchor = no phantom transition/turnover; warmup
    #      rebalance counted; cost-affordable lot step-down (999k of 1M)
    P3 = _mk_panel(n=60)
    P3["rebal_days"] = [2, 23, 44]

    def tf3(r):
        return None if r < 5 else {LEGS[0]: 1.0}

    rec3 = simulate(P3, tf3, lambda g, a: 0.001 * g)
    ok("[F3] same-target rebalance no-op + warmup + affordability face",
       rec3["n_active_rebal"] == 1 and rec3["n_trades"] == 1
       and rec3["n_entries"] == 1 and rec3["n_warmup_rebal"] == 1
       and rec3["n_superseded"] == 0
       and len(rec3["transitions"]) == 1
       and rec3["transitions"][0]["completed"] is True
       and rec3["transitions"][0]["fill_days"] == 1
       and rec3["traded_notional_total"] == 999_000.0
       and rec3["cost_total"] == 999.0,
       f"to={rec3['traded_notional_total']} "
       f"cost={rec3['cost_total']}")

    # [F4] tie -> 50/50; gate tie -> per-leg gate on halves
    cl = np.full((300, 2), 1.0)
    ma = ma200_matrix(cl)
    tf_bare = make_rotation_target(cl, ma, 63, False)
    ok("[F4] strict-float tie -> 50/50 both legs",
       tf_bare(250) == {LEGS[0]: 0.5, LEGS[1]: 0.5})
    cl2 = np.full((300, 2), 1.0)
    cl2[250, 0] = 1.5                    # leg0 strictly stronger at r=250
    tf_arg = make_rotation_target(cl2, ma, 63, False)
    ok("[F4] argmax pick",
       tf_arg(250) == {LEGS[0]: 1.0})
    # gate tie with RS equal (+5% both) but leg0 above / leg1 below MA200:
    # leg0 flat 10.0 then 10.5 (RS 10.5/10-1=+5%, close > MA);
    # leg1 long 20.0 history, 10.0 at t=222, 10.5 after (RS +5%,
    # MA200 ~16.96 -> close below).
    cl4 = np.full((300, 2), 0.0)
    cl4[:, 0] = 10.0
    cl4[280:, 0] = 10.5
    cl4[:, 1] = 20.0
    cl4[222, 1] = 10.0
    cl4[223:, 1] = 10.5
    ma4 = ma200_matrix(cl4)
    tf_gtie = make_rotation_target(cl4, ma4, 63, True)
    tf_gtie_bare = make_rotation_target(cl4, ma4, 63, False)
    ok("[F4] gate tie one leg above MA200 -> half position",
       tf_gtie(285) == {LEGS[0]: 0.5}
       and tf_gtie_bare(285) == {LEGS[0]: 0.5, LEGS[1]: 0.5})
    cl3 = np.full((300, 2), 10.0)
    cl3[280:, :] = 5.0                    # both below MA200, RS tie
    ma3 = ma200_matrix(cl3)
    tf_gtie0 = make_rotation_target(cl3, ma3, 63, True)
    ok("[F4] gate tie both legs below MA200 -> cash",
       tf_gtie0(285) == {})

    # [F5] gate rule: above -> hold, below -> cash, warmup before MA window
    cl5 = np.full((300, 2), 10.0)
    for t in range(63, 300):
        cl5[t, 0] = cl5[t - 1, 0] * 1.01        # leg0 rising (argmax)
        cl5[t, 1] = cl5[t - 1, 1] * 0.99
    ma5 = ma200_matrix(cl5)
    tf_g = make_rotation_target(cl5, ma5, 63, True)
    ok("[F5] gate above MA200 -> hold / warmup -> None",
       tf_g(250) == {LEGS[0]: 1.0}
       and tf_g(100) is None            # r=100 < 199 = MA warmup
       and make_rotation_target(cl5, ma5, 63, False)(100)
       == {LEGS[0]: 1.0})               # bare activates at r>=63
    cl6 = np.full((300, 2), 10.0)
    for t in range(150, 300):                   # late crash: close < MA200
        cl6[t, 0] = cl6[t - 1, 0] * 0.99
        cl6[t, 1] = cl6[t - 1, 1] * 0.995
    ma6 = ma200_matrix(cl6)
    tf_g6 = make_rotation_target(cl6, ma6, 63, True)
    ok("[F5] gate below MA200 -> cash period",
       tf_g6(299) == {})

    # [F6] nulls: determinism + warmup override + divergence
    n1 = make_null_target(SEED_BASE)
    n2 = make_null_target(SEED_BASE)
    n3 = make_null_target(SEED_BASE + 1)
    rr = list(range(0, 400, 20))          # 20 draws, warmup + active mix
    seq1 = [n1(r) for r in rr]
    seq2 = [n2(r) for r in rr]
    seq3 = [n3(r) for r in rr]
    warm_idx = [i for i, r in enumerate(rr) if r < NULL_ACTIVATION_W]
    act_idx = [i for i, r in enumerate(rr) if r >= NULL_ACTIVATION_W]
    ok("[F6] null same-seed identical + warmup override",
       seq1 == seq2
       and all(seq1[i] is None for i in warm_idx)
       and all(seq1[i] is not None for i in act_idx)
       and len(n1.draws) == len(rr))
    ok("[F6] null diff-seed diverges (post-warmup draws)",
       any(seq1[i] != seq3[i] for i in act_idx))

    # [F7] EW 50/50 drift reset: overweight trim + underweight top-up
    P7 = _mk_panel(o_a=10.0, o_b=10.0, adv_a=1e9, adv_b=1e9, n=60)
    P7["rebal_days"] = [5, 26]
    for t in range(1, 30):
        P7["legs"][LEGS[0]]["open"][t] = \
            P7["legs"][LEGS[0]]["open"][t - 1] * 1.01
        P7["legs"][LEGS[0]]["close"][t] = \
            P7["legs"][LEGS[0]]["open"][t]

    def ew_t(r):
        return None if r < 5 else {LEGS[0]: 0.5, LEGS[1]: 0.5}

    rec7 = simulate(P7, ew_t, lambda g, a: 0.0, capital=1_000_000.0)
    ok("[F7] EW drift reset transition exists with both deltas",
       rec7["n_active_rebal"] == 2
       and rec7["sold_notional_total"] > 0
       and rec7["bought_notional_total"] > 1000.0,
       f"active={rec7['n_active_rebal']} "
       f"sold={rec7['sold_notional_total']} "
       f"bought={rec7['bought_notional_total']}")

    # [F8] gates wiring: coverage-carrying pool (r217 law) + real verdicts
    fake_nulls = [0.01 * ((k * 37) % 23 - 11) for k in range(50)]
    pool = {"values": fake_nulls,
            "coverage": {"n_values": 50, "mu": float(np.mean(fake_nulls)),
                         "sigma": float(np.std(fake_nulls, ddof=1)),
                         "schemas_parsed": ["selftest"],
                         "known_unparsed": []}}
    rets8 = pd.Series([0.001 * ((k * 53) % 17 - 8) for k in range(300)],
                      index=pd.bdate_range("2020-01-02", periods=300))
    v8 = sg.g1_prime_v2(sharpe_full=0.3, returns=rets8, batch_cells=4,
                        pool="core48", n_trades=99, n_entries=99,
                        null_pool=pool)
    ok("[F8] g1 verdict real fields (no error)",
       "pass_v2" in v8 and "skill_line" in v8 and "bootstrap_ci" in v8
       and "error" not in v8)
    try:
        sg.g1_prime_v2(sharpe_full=0.3, returns=rets8, batch_cells=4,
                       pool="core48", null_pool={"values": fake_nulls})
        ok("[F8] values-only pool raises KeyError (r217 proof)", False)
    except KeyError:
        ok("[F8] values-only pool raises KeyError (r217 proof)", True)
    g2v = sg.g2_registration_v2(g1_pass=True, dsr={"dsr": 0.97}, pbo=0.10)
    ok("[F8] g2 verdict columns",
       g2v["eligible_v2"] is True and g2v["dsr_ok"] and g2v["pbo_ok"])
    g2m = sg.g2_registration_v2(g1_pass=False, dsr={"dsr": 0.99}, pbo=0.0)
    ok("[F8] g2 fail-closed on g1 miss",
       g2m["eligible_v2"] is False and "g1_prime_v2" in g2m["missing_inputs"])

    # [F9] family PBO wiring over 4 synthetic cells
    fam = {f"c{i}": pd.Series(
        np.random.default_rng(i).normal(0.0005 * (i + 1), 0.01, 400),
        index=pd.bdate_range("2020-01-02", periods=400)) for i in range(4)}
    pbo = cscv_pbo(align_returns(fam))
    ok("[F9] cscv 8 blocks over 4-cell grid",
       pbo["n_blocks"] == 8 and pbo["n_trials"] == 4
       and 0.0 <= pbo["pbo"] <= 1.0)

    # [F10] crisis exemption logic + hard-bound columns (MY windows)
    rets_c = pd.Series(np.zeros(300),
                       index=pd.bdate_range("2019-12-02", periods=300))
    big_day = pd.Timestamp("2020-03-09")
    rets_c.iloc[rets_c.index.get_loc(big_day)] = -0.092
    bnd = {"argmax_day": str(big_day.date()), "in_crisis_window": True,
           "median": 0.0, "p99_9": 0.0, "max": 0.092}
    ex = _exempt(rets_c, bnd)
    ok("[F10] crisis-window single-point exemption",
       ex["applied"] is True and ex["exempted_day"] == "2020-03-09")
    ok("[F10] crisis log captures >=5pct crisis-day",
       len(_crisis_log(rets_c)) == 1)
    nb = {"argmax_day": "2019-03-08", "in_crisis_window": False,
          "median": 0.0, "p99_9": 0.0, "max": 0.092}
    ok("[F10] out-of-window max -> no exemption",
       _exempt(rets_c, nb)["applied"] is False)

    # [F11] full mini-pipeline determinism (double-run byte identity)
    def _mini():
        Pm = _mk_panel(o_a=2.0, o_b=3.0, adv_a=50_000, adv_b=900_000,
                       n=120)
        clm = np.vstack([Pm["legs"][c]["close"] for c in LEGS]).T
        mam = ma200_matrix(clm) if clm.shape[0] >= MA_WIN else \
            np.full_like(clm, np.nan)
        out = {}
        for w in (5,):                    # synthetic short window
            for gate_on in (False, True):
                tfm = make_rotation_target(clm, mam, w, gate_on)
                r = simulate(Pm, tfm, FACES[JUDGED_FACE])
                out[f"{w}_{gate_on}"] = {
                    "rets": [round(float(x), 8) for x in
                             r["returns"].tolist()],
                    "trades": r["n_trades"],
                    "to": r["traded_notional_total"],
                    "fd": r["fill_days_list"]}
        return json.dumps(out, sort_keys=True)

    a11, b11 = _mini(), _mini()
    ok("[F11] mini-pipeline double-run byte identity", a11 == b11)

    # [F12] buy-and-hold: one transition, no churn
    P12 = _mk_panel(n=60)
    P12["rebal_days"] = [5, 26]

    def bh(r):
        return None if r < 5 else {LEGS[1]: 1.0}

    rec12 = simulate(P12, bh, lambda g, a: 0.0)
    ok("[F12] buy-hold single transition no churn",
       rec12["n_active_rebal"] == 1 and rec12["n_entries"] >= 1
       and all(tr_["target"] == {LEGS[1]: 1.0}
               for tr_ in rec12["transitions"]))

    # [F13] checkpoint round-trip: save -> load -> exact returns
    import tempfile
    global CKPT_DIR
    saved = CKPT_DIR
    CKPT_DIR = os.path.join(tempfile.gettempdir(),
                            "cnrot_selftest_ckpt")
    try:
        Pp = _mk_panel(n=80, adv_a=200_000)
        recp = simulate(Pp, lambda r: None if r < 5
                        else {LEGS[0]: 1.0}, FACES[JUDGED_FACE])
        _ck_save("selftest_unit", recp, recp["returns"])
        lod = _ck_load("selftest_unit", Pp["days"])
        ok("[F13] ckpt round-trip exact + date-drift refusal",
           lod is not None and np.array_equal(
               np.asarray(recp["returns"]), np.asarray(lod["returns"]),
               equal_nan=True)
           and lod["n_trades"] == recp["n_trades"]
           and _ck_load("selftest_unit", Pp["days"][:-1]) is None)
    finally:
        CKPT_DIR = saved
        import shutil
        shutil.rmtree(os.path.join(tempfile.gettempdir(),
                                   "cnrot_selftest_ckpt"),
                      ignore_errors=True)

    # [F14] metrics block: OOS split + yearly + d1 bounds + queue cols
    mret = pd.Series(
        np.random.default_rng(11).normal(0.001, 0.01, 800),
        index=pd.bdate_range("2022-01-03", periods=800))
    mrec = {"returns": mret, "n_entries": 40, "n_trades": 80,
            "n_rebal": 79, "n_active_rebal": 79, "n_warmup_rebal": 3,
            "n_transitions": 79, "n_completed": 77, "n_superseded": 2,
            "fill_days_list": [1] * 77, "fill_days_max": 1,
            "fill_days_mean": 1.0, "truncated": False,
            "first_entry_day": 21, "traded_notional_total": 12.0,
            "sold_notional_total": 6.0, "bought_notional_total": 6.0,
            "cost_total": 0.015, "cost_by_year": {"2022": 0.015},
            "transitions": [], "inv_rebal_frac": 1.0}
    m = metrics(mrec)
    ok("[F14] metrics: oos window + yearly keys + queue columns",
       m["oos"]["n_days"] == int(
           (mret.index >= pd.Timestamp(OOS_START)).sum())
       and 2022 in m["yearly"] and m["d1_bounds"]["max"] is not None
       and m["sharpe"] is not None and m["fill_days_max"] == 1
       and m["n_superseded"] == 2)

    # [F15] ADV-NaN conservative: no fill on unknown-ADV day
    P15 = _mk_panel(o_a=1.0, adv_a=1e9, n=30, nan_adv=[5, 6])
    P15["rebal_days"] = [5]
    # exec day 6: ADV(t-1)=adv[5]=NaN -> cap 0, no fill; day 7 same
    # (adv[6]=NaN); day 8 adv[7] finite -> full 1000 buy -> complete.
    rec15 = simulate(P15, lambda r: None if r < 5
                     else {LEGS[0]: 1.0}, lambda g, a: 0.0,
                     capital=1000.0)
    ok("[F15] NaN-ADV day = zero cap, fill deferred (conservative)",
       rec15["first_entry_day"] == 8
       and rec15["transitions"][0]["fill_days"] == 3,
       f"first={rec15['first_entry_day']} "
       f"fd={rec15['transitions'][0]['fill_days']}")

    # [F16] 510880 leg face: buy-hold corpus leg return continuity
    # (spot-check the H4 disclosure input construction on synthetic panel)
    legs_syn = _mk_panel()["legs"]
    lr = np.append([np.nan], legs_syn[LEGS[0]]["close"][1:]
                   / legs_syn[LEGS[0]]["close"][:-1] - 1.0)
    ok("[F16] leg return series construction (flat prices -> zeros)",
       bool(np.all(np.isnan(lr[:1]))) and
       bool(np.nanmax(np.abs(lr[1:])) < 1e-15))

    print(f"cn_div_lowvol_rot_p1 selftest: {len(fails)} FAIL")
    return 0 if not fails else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "selftest"])
    a = ap.parse_args()
    if a.cmd == "selftest":
        return selftest()
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
