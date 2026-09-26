# -*- coding: utf-8 -*-
"""DIV_LOWVOL_P1 dividend-lowvol carry sleeve batch runner (T-2026-09-25-53
slice-7, bm-a lane). Prereg research/DIV_LOWVOL_P1.md frozen pre-run R178
(verdicts final, run-only s7 backfill, no threshold tuning).

Cells (prereg s0, N_eff=36 = C1-C4 + K32 nulls, all on the D1 bill):
  C1 judged      pair {512890,510880} 50/50 nominal, ORANGE-regime gate +
                 hard-bound triad; the ONLY registration-facing cell
  C2/C3 attrib   single-leg sleeves (100% nominal), same gate + bounds
  C4 ablation    pair buy-and-hold, NO gate NO bounds (full-window carry
                 context cell; 1 entry event)
  K32 nulls      random segment-mask sleeves, duration multiset preserved
                 (recorded-window ORANGE episode lengths), same mechanism +
                 same bounds + same judged (x2) cost face; seeds 60_000+k,
                 registered div_lowvol_p1 in science_gates.SEED_REGISTRY

Mechanism (prereg s3, frozen):
  signal day t (state(t close)==ORANGE, ETF-face v1 matrix via the IMPORTED
  frozen regime layer -- regime_calibration.build_bench/bench_dim_series/
  breadth_series/raw_series/state_replay, zero re-implementation) -> hold
  from open(t+1); state leaves ORANGE at s -> exit at open(s+1). Equal
  weight reset at each segment entry, no intra-segment rebalance.
  Hard-bound triad evaluated at close of marked days while holding:
   (a) sleeve 20-marked-day rolling cumret <= -0.1267 (probe q0.001 line)
   (b) episode-local HWM drawdown <= -12%  (episode-local per s5.4 「段内」
       language -- an all-time HWM would lock the sleeve out forever after
       any single -12% episode; frozen implementation reading, disclosed)
   (c) |r1| >= 5% single-day -> crisis log (cut is the protective action,
       no exemption path protects the position)
  Trigger -> cut at next tradable open + LOCK until the next segment entry
  (zero re-entry within the segment; no re-entry parameter).

Execution/valuation (frozen): entry at t+1 open, close valuation daily,
exit at t+1 open (exit-day P&L = open/prev_close - 1); lot 100; suspension
bars (enumerated: 512890 2021-10-22) = no trade + no mark for that leg
(equity series skips the day, returns span it); entry/exit landing on a
suspension day slide to the next tradable open (logged).

Split adjustment (s2.3, batch-local in-memory ONLY, corpus untouched):
512890 pre-2021-10-25 bars x0.5 -- event list imported VERBATIM from
scripts/div_lowvol_probe.SPLIT_EVENTS (single source). ADV20 = raw
amount (yuan) rolling-20 mean, unadjusted per prereg ("volume not
adjusted"); slippage tier + 1% ADV fill cap per knowledge/rules.py;
exec at t uses adv[t-1] (through-date; inception without t-1 -> 10bp
tier, no cap -- mf_rot precedent).

Cost faces: judge face = x2 (whole-V2 doubled, side_cost_x2 semantics =
CostPatch single source), always on; x1 = side_cost_v2 verbatim; x3 =
same components tripled (disclosure). Each face is a complete
self-consistent sleeve (bounds monitored on that face's own equity path).
Out-of-market marked days contribute 0 to the full-timeline judged return
series (prereg s4: 含场外日 0 收益; no repo accrual in this sleeve).

D6 (s1): reject face = max|corr| of C1 (judged series) vs the 6 REGISTERED
members (COMPOSITE-CE-01/02, DROUGHT-CE-01, ENGULF-CE-01, NEEDLE-DE-01,
VOLATILITY-CE-01) >= 0.7 -> REJECT (s5.5 pins argmax expectation to
VOLATILITY-CE-01 at 0.2-0.5 -- same-batch C2/C3/C4 and the null family
are DISCLOSURE faces by construction, s0 declares them non-judgment
cells; full corr table still reported, sleeve-tag precedent). Member
series via the ew6 canon (ew6_portfolio.member_run -- IDENTICAL code path
to the live.paper anchor gate; factor_blend._member_task precedent).
H4 alpha face: corr(C1-510300, VOLATILITY-CE-01-510300) on overlap.

Gates: G1'v2 + G2 via scripts/science_gates.py shared library (zero
hand-copied lines); skill line = pool "core48" + batch-own null_pool
(P4_EXT_TILT additive precedent); DSR on C1 judged raw returns; family
PBO = screening/pbo.py CSCV over {C1,C2,C3,C4} (4-cell family, noise
disclosed). ORANGE segment gate (STYLE_CORPS s5): primary = pooled
held-day cumret sleeve vs 510300 same day-set; secondary = per-segment
beats (>=12/22 prediction) + per-segment CI.

Products: results/div_lowvol_p1.json (+ sg.cutoff_meta top level),
gate_attrition row + trials-ledger append at finalize only (single-shot;
DIV_LOWVOL_P1_REFINALIZE=1 = only redo path). Zero wall-clock fields in
the batch JSON; determinism via selftest double-run byte-identity.

Usage: run | selftest
"""
import argparse
import json
import math
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "screening"))

import numpy as np
import pandas as pd

import science_gates as sg
from alloc_backtest import side_cost_v2, side_cost_x2
import div_lowvol_probe as DLP
from scripts.regime_calibration import (
    build_bench, bench_dim_series, breadth_series, raw_series, state_replay,
)
from scripts.market_regime import GREEN, ORANGE, RED, YELLOW

TICKET = "T-2026-09-25-53"
PREREG = os.path.join(ROOT, "research", "DIV_LOWVOL_P1.md")
OUT_JSON = os.path.join(ROOT, "results", "div_lowvol_p1.json")
ATT_JSON = os.path.join(ROOT, "results", "gate_attrition.json")
LOG_PATH = os.path.join(ROOT, "results", "div_lowvol_backtest.log")

WINDOW_START = "2020-01-02"      # prereg s2 (recorded replay window head)
WINDOW_END = "2026-09-22"        # prereg s2 forward lockbox (dividend-leg last bar)
RECENT_START = "2021-01-01"      # H1-law dual-report window
LEGS = ("512890", "510880")
BENCH = "510300"
CAPITAL = 1_000_000.0
CUT20_LINE = -0.1267             # s3(a) probe-frozen q0.001 of pair 20d cumret
MAX_DD_CAP = -0.12               # s3(b) max hard cap
CRISIS_ABS_R = 0.05              # s3(c) crisis-log threshold
BOUNDS_WINDOW = 20               # s3(a) marked-day rolling window
SEED_BASE = 60_000               # science_gates.SEED_REGISTRY["div_lowvol_p1"]
K_NULLS = 32                     # prereg s0/s3
BATCH_CELLS_NOMINAL = 36         # C1-C4 + K32 (prereg s0, D1 bill)
D6_REJECT = 0.7                  # prereg s1 hard line
REG6 = ("COMPOSITE-CE-01", "COMPOSITE-CE-02", "DROUGHT-CE-01",
        "ENGULF-CE-01", "NEEDLE-DE-01", "VOLATILITY-CE-01")
LOT = 100
ADV_FILL_CAP = 0.01              # knowledge/rules.py ADV_FILL_CAP_RATE

# prereg s5 frozen predictions (reconciliation face only, never gates)
PRED = {
    "c1_entries": 44, "c23_entries": 22, "c4_entries": 1,
    "seg_beat_range": (12, 15), "seg_total": 22,
    "c1_sharpe": (0.5, 0.9), "d6_argmax": "VOLATILITY-CE-01",
    "d6_range": (0.2, 0.5), "bound_triggers_min": 1,
    "recent_ann_range": (0.03, 0.06),
}


def _log(msg):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as fh:
        fh.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}\n")
    print(f"[div_lowvol] {msg}", flush=True)


def side_cost_x3(gross, adv20):
    """x3 disclosure face: every V2 component tripled (side_cost_x2
    semantics at 3.0 -- CostPatch single-source lineage)."""
    if gross <= 0:
        return 0.0
    from knowledge import rules as krules
    slip = krules.cost_v2_slippage(adv20)
    fee = krules.FeeSchedule
    comm = max(gross * fee.commission_rate * 3.0,
               fee.commission_min * 3.0)
    return comm + gross * 3.0 * (fee.handling_fee + fee.supervision_fee) \
        + gross * 3.0 * slip


FACES = {"x1": side_cost_v2, "x2": side_cost_x2, "x3": side_cost_x3}


# ---------------------------------------------------------------- data faces

def _leg_frame(fname):
    df = pd.read_csv(os.path.join(ROOT, "data", "daily", fname),
                     parse_dates=["date"])
    return df.set_index("date").sort_index()


def load_faces():
    """Window-aligned arrays: split-adjusted legs (in-memory, event list
    single-sourced from the probe), bench calendar, through-date ADV20."""
    raw = {c: _leg_frame(f"sh{c}.csv") for c in LEGS}
    adj = {c: DLP._adjust_split(raw[c], DLP.SPLIT_EVENTS[c]) for c in LEGS}
    bench = _leg_frame(f"{BENCH}.csv")
    head, tail = pd.Timestamp(WINDOW_START), pd.Timestamp(WINDOW_END)
    days = bench.index[(bench.index >= head) & (bench.index <= tail)]
    n = len(days)
    legs = {}
    susp = {d for ev in DLP.SPLIT_EVENTS.values() if ev
             for d in ev["suspended_bars"]}
    for c in LEGS:
        f = adj[c].reindex(days)
        o = f["open"].to_numpy(dtype=float)
        cl = f["close"].to_numpy(dtype=float)
        # tradable = valid open AND close that day (suspension bars are not)
        tradable = np.isfinite(o) & np.isfinite(cl)
        # through-date ADV20: raw amount rolling-20, unadjusted (prereg s2.3)
        amt = raw[c]["amount"].rolling(20).mean()
        adv = amt.reindex(days).to_numpy(dtype=float)
        legs[c] = {"open": o, "close": cl, "tradable": tradable,
                   "adv": adv}
    b_close = bench["close"].reindex(days).to_numpy(dtype=float)
    b_open = bench["open"].reindex(days).to_numpy(dtype=float)
    return {"days": days, "n": n, "legs": legs,
            "bench": {"close": b_close, "open": b_open},
            "suspension_days": susp}


def regime_faces():
    """IMPORTED frozen layer: per-day states + drift gate vs the recorded
    file (prereg s2.2: counts must match bit-for-bit or the batch VOIDs)."""
    rec_path = os.path.join(ROOT, "results", "regime_calibration.json")
    rec = json.load(open(rec_path, encoding="utf-8"))
    bb = build_bench()
    ds = bench_dim_series(bb)
    br = breadth_series(bb)
    raw = raw_series(bb, ds, br)
    states, _st, _init = state_replay(bb, raw)
    ser = pd.Series({d: states[d] for d in states}).sort_index()
    rw = rec["window"]
    rec_slice = ser[(ser.index >= pd.Timestamp(rw["start"]))
                    & (ser.index <= pd.Timestamp(rw["end"]))]
    counts = {s: int((rec_slice == s).sum()) for s in (GREEN, YELLOW, ORANGE, RED)}

    def _eps(series):
        segs, in_seg, start, prev = [], False, None, None
        for d, st in series.items():
            if st == ORANGE and not in_seg:
                start, in_seg = d, True
            elif st != ORANGE and in_seg:
                segs.append((start, prev))
                in_seg = False
            prev = d
        if in_seg:
            segs.append((start, prev))
        return segs

    rec_eps = _eps(rec_slice)
    drift = {
        "recorded_window": {"start": rw["start"], "end": rw["end"]},
        "recomputed_state_counts": counts,
        "recorded_state_counts": {k: int(v) for k, v in rec["state_counts"].items()},
        "recomputed_orange_episodes": len(rec_eps),
        "recorded_orange_episodes": int(rec["false_alarm"]["orange"]["episodes"]),
        "counts_match": bool(
            counts == {k: int(v) for k, v in rec["state_counts"].items()}
            and len(rec_eps) == int(rec["false_alarm"]["orange"]["episodes"])),
        # null-family duration multiset source: RECORDED-window episodes
        # (prereg s3: 与在册记录窗逐段相同)
        "recorded_window_orange_durations": [int((e - s).days) + 1
                                             for s, e in rec_eps],
    }
    return ser, drift


def sleeve_mask(states, days):
    """gate_mask[i] = state(days[i]) == ORANGE (signal at close of i ->
    hold from open of i+1)."""
    return np.array([states.get(d) == ORANGE for d in days], dtype=bool)


# ---------------------------------------------------------------- simulator

def simulate_sleeve(faces, mask, weights, *, bounds_on, cost_fn, capital):
    """One sleeve run (one face). Arrays indexed 0..n-1 over bench days.

    mask: bool array (state(i close)==ORANGE -> hold from open(i+1));
          None = buy-and-hold from day-0 open (C4 ablation form).
    weights: {leg: nominal weight at entry}.
    Returns the full sim record (marks/returns/metrics/logs)."""
    days, n = faces["days"], faces["n"]
    legs = faces["legs"]
    wl = list(weights)
    cash = float(capital)
    hold = {c: 0.0 for c in wl}
    holding = False
    locked = False
    pending_entry = pending_exit = pending_cut = False
    cut_reason = None
    ep_high = None
    prev_desired = False
    prev_mark_eq = None
    ret_hist = []
    marks = []            # (day_idx, equity)
    rets = pd.Series(dtype=float)   # full-timeline judged series (marked days)
    held_days = []
    n_entries = n_trades = entry_events = 0
    per_leg = {c: {"opens": 0, "closes": 0} for c in wl}
    cuts, crisis, deferrals = [], [], []
    cost_total = 0.0
    fill_refusals = 0
    truncated = False
    seg_costs = []        # per-segment cost rows
    cur_seg_cost = None

    for t in range(n):
        desired = True if mask is None else (bool(mask[t - 1]) if t >= 1
                                             else False)
        if desired and not prev_desired:
            # new segment entry clears any in-segment bound lock (s3:
            # lock runs to the NEXT segment, not forever)
            locked = False
            ep_high = None
            pending_entry = True
            cur_seg_cost = {"entry_cost": 0.0, "exit_cost": 0.0,
                            "entry_day": int(t)}
        if not desired:
            pending_entry = False
            if holding and not pending_cut:
                pending_exit = True
        exited_today = False

        if holding:
            if pending_cut or pending_exit:
                if all(legs[c]["tradable"][t] for c in wl if hold[c] > 0):
                    seg_exit = 0.0
                    fully_out = True
                    for c in wl:
                        if hold[c] <= 0:
                            continue
                        sh = hold[c]
                        px = legs[c]["open"][t]
                        a = legs[c]["adv"][t - 1] if t >= 1 else float("nan")
                        if np.isfinite(a) and sh * px > ADV_FILL_CAP * a:
                            fill_refusals += 1
                            deferrals.append({"day": int(t),
                                              "kind": "exit_cap_refusal"})
                            fully_out = False
                            continue
                        cost = cost_fn(sh * px, a)
                        cash += sh * px - cost
                        cost_total += cost
                        seg_exit += cost
                        hold[c] = 0.0
                        per_leg[c]["closes"] += 1
                        n_trades += 1
                    if fully_out:
                        if pending_cut:
                            cuts.append({"day": int(t),
                                         "reason": cut_reason})
                            locked = True
                        holding = False
                        exited_today = True
                        pending_cut = pending_exit = False
                        cut_reason = None
                        if cur_seg_cost is not None:
                            cur_seg_cost["exit_cost"] = round(seg_exit, 2)
                            cur_seg_cost["exit_day"] = int(t)
                            seg_costs.append(cur_seg_cost)
                            cur_seg_cost = None
        elif pending_entry and desired:
            if all(legs[c]["tradable"][t] for c in wl):
                eq0 = cash
                seg_entry = 0.0
                for c in wl:
                    target = weights[c] * eq0
                    px = legs[c]["open"][t]
                    shares = int(target / px // LOT) * LOT
                    if shares <= 0:
                        continue
                    a = legs[c]["adv"][t - 1] if t >= 1 else float("nan")
                    if np.isfinite(a) and shares * px > ADV_FILL_CAP * a:
                        fill_refusals += 1
                        deferrals.append({"day": int(t),
                                          "kind": "entry_cap_refusal",
                                          "leg": c})
                        continue
                    cost = cost_fn(shares * px, a)
                    cash -= shares * px + cost
                    cost_total += cost
                    seg_entry += cost
                    hold[c] = float(shares)
                    per_leg[c]["opens"] += 1
                    n_entries += 1
                if any(v > 0 for v in hold.values()):
                    holding = True
                    entry_events += 1
                    pending_entry = False
                    if cur_seg_cost is not None:
                        cur_seg_cost["entry_cost"] = round(seg_entry, 2)
                # else: keep pending_entry, retry next day
            else:
                deferrals.append({"day": int(t),
                                  "kind": "entry_suspension_slide"})

        if holding or exited_today:
            # held day = position open at any point (entry day through
            # exit day; the exit day still carries open/prev_close P&L)
            held_days.append(int(t))
        if holding:
            # close mark: all held legs need a valid close
            if all(np.isfinite(legs[c]["close"][t]) for c in wl if hold[c] > 0):
                eq = cash + sum(hold[c] * legs[c]["close"][t]
                                for c in wl if hold[c] > 0)
                marks.append((t, float(eq)))
                if prev_mark_eq is not None:
                    r = eq / prev_mark_eq - 1.0
                    rets.loc[days[t]] = r
                    ret_hist.append(float(r))
                    if len(ret_hist) > BOUNDS_WINDOW:
                        ret_hist.pop(0)
                    if bounds_on:
                        ep_high = eq if ep_high is None else max(ep_high, eq)
                        dd = eq / ep_high - 1.0
                        cum20 = (math.prod(1.0 + x for x in ret_hist) - 1.0
                                if len(ret_hist) == BOUNDS_WINDOW else None)
                        if not pending_cut:
                            if dd <= MAX_DD_CAP:
                                pending_cut = True
                                cut_reason = {"type": "b_hwm_dd",
                                              "dd": round(float(dd), 6)}
                            elif cum20 is not None and cum20 <= CUT20_LINE:
                                pending_cut = True
                                cut_reason = {"type": "a_cum20",
                                              "cum20": round(float(cum20), 6)}
                        if abs(r) >= CRISIS_ABS_R:
                            crisis.append({"day": str(days[t].date()),
                                           "r1": round(float(r), 6)})
                prev_mark_eq = eq
            # suspension day: no mark, returns span (probe construction)
        else:
            eq = cash
            marks.append((t, float(eq)))
            if prev_mark_eq is not None:
                r = eq / prev_mark_eq - 1.0
                rets.loc[days[t]] = r
                # out-of-market 0s ARE part of the account's trailing
                # 20-marked-day window (sleeve-account reading, frozen)
                ret_hist.append(float(r))
                if len(ret_hist) > BOUNDS_WINDOW:
                    ret_hist.pop(0)
            prev_mark_eq = eq
        prev_desired = desired

    if holding:
        truncated = True   # window-end open position (cutoff truncation face)

    eqs = pd.Series({days[t]: e for t, e in marks}).sort_index()
    out = {
        "n_marks": int(len(eqs)),
        "sharpe": _sharpe(rets),
        "ann_ret": _ann(rets),
        "max_dd": _max_dd(eqs),
        "n_entries": int(n_entries), "n_trades": int(n_trades),
        "entry_events": int(entry_events),
        "per_leg": per_leg,
        "held_days": held_days,
        "cuts": cuts, "crisis_log": crisis, "deferrals": deferrals,
        "cost_total": round(float(cost_total), 2),
        "seg_costs": seg_costs,
        "fill_refusals": int(fill_refusals),
        "truncated": bool(truncated),
        "yearly": _yearly(eqs),
        "recent_ann": _recent_ann(rets),
    }
    out["returns"] = rets
    out["eq"] = eqs
    return out


def _sharpe(rets):
    if len(rets) < 20 or float(rets.std()) == 0:
        return None
    return round(float(rets.mean() / rets.std() * math.sqrt(252.0)), 4)


def _ann(rets):
    if len(rets) < 20:
        return None
    total = float((1.0 + rets).prod())
    return round(total ** (252.0 / len(rets)) - 1.0, 6)


def _max_dd(eqs):
    if len(eqs) < 2:
        return None
    return round(float((eqs / eqs.cummax() - 1.0).min()), 6)


def _yearly(eqs):
    if not len(eqs):
        return {}
    return {int(y): round(float(g.iloc[-1] / g.iloc[0] - 1.0), 4)
            for y, g in eqs.groupby(eqs.index.year)}


def _recent_ann(rets):
    r = rets[rets.index >= pd.Timestamp(RECENT_START)]
    return _ann(r) if len(r) else None


# ---------------------------------------------------------------- nulls

def build_null_mask(durations, n_days, seed):
    """Random segment placement, duration multiset preserved, non-overlap
    by rejection, deterministic per seed (prereg s3). Segments are placed
    in DECREASING-duration order (bin-packing heuristic): the longest
    episodes draw their random starts first so scattered small segments
    can never fragment the free space into infeasibility; start positions
    remain uniform random draws from the seeded rng."""
    rng = np.random.default_rng(seed)
    placed = []
    order = sorted(range(len(durations)), key=lambda i: -int(durations[i]))
    for ji in order:
        dur = int(durations[ji])
        ok = False
        for _attempt in range(500):
            s = 1 if dur >= n_days - 1 else int(rng.integers(1, n_days - dur + 1))
            e = s + dur - 1
            if all(e < p0 or s > p1 for p0, p1 in placed):
                placed.append((s, e))
                ok = True
                break
        if not ok:   # first-fit fallback (deterministic)
            for s in range(1, n_days - dur + 1):
                e = s + dur - 1
                if all(e < p0 or s > p1 for p0, p1 in placed):
                    placed.append((s, e))
                    ok = True
                    break
        if not ok:
            raise RuntimeError(f"null placement infeasible dur={dur}")
    mask = np.zeros(n_days, dtype=bool)
    for s, e in placed:
        mask[s:e + 1] = True
    return mask, sorted(placed)


def run_nulls(faces, durations):
    """K=32 random segment-mask sleeves on the judged x2 face (same
    mechanism + bounds + costs as C1)."""
    vals, per_draw = [], {}
    weights = {c: 0.5 for c in LEGS}
    for k in range(K_NULLS):
        mask, placed = build_null_mask(durations, faces["n"], SEED_BASE + k)
        r = simulate_sleeve(faces, mask, weights, bounds_on=True,
                            cost_fn=FACES["x2"], capital=CAPITAL)
        vals.append(r["sharpe"] if r["sharpe"] is not None else 0.0)
        per_draw[f"draw{k}"] = {
            "seed": SEED_BASE + k, "sharpe": r["sharpe"],
            "n_entries": r["n_entries"], "n_trades": r["n_trades"],
            "cuts": len(r["cuts"]), "placed_segments": len(placed),
        }
    mu, sigma = float(np.mean(vals)), float(np.std(vals, ddof=1))
    return {
        "config": {"base": SEED_BASE, "registered": "div_lowvol_p1",
                   "draws": K_NULLS, "face": "x2_judged",
                   "durations_multiset": list(durations)},
        "n_values": len(vals),
        "values_rounded": [round(v, 6) for v in vals],
        "coverage": {"n_values": len(vals), "mu": mu, "sigma": sigma,
                     "schemas_parsed": [f"div_lowvol_p1: {K_NULLS} random "
                                        f"segment-mask pair sleeves"],
                     "known_unparsed": []},
        "per_draw": per_draw,
    }


# ---------------------------------------------------------------- D6 + gates

def _corr(a: pd.Series, b: pd.Series, min_overlap=20):
    j = pd.concat([a, b], axis=1, join="inner").dropna()
    if len(j) < min_overlap:
        return None, int(len(j))
    v = float(np.corrcoef(j.iloc[:, 0], j.iloc[:, 1])[0, 1])
    return round(v, 4), int(len(j))


def d6_block(c1_rets, batch_rets, null_rets_list, bench_close):
    """D6: member reject face + full disclosure table (s1)."""
    out = {"reject_line": D6_REJECT, "members": list(REG6)}
    member_rets = None
    try:
        import ew6_portfolio as E
        from live.paper import load_core
        if E.PRICES_FULL is None:
            E.PRICES_FULL = load_core()
        member_rets = {}
        member_cutoffs = {}
        for tid in REG6:
            r = E.member_run(tid)
            eq = pd.Series(r["eq"], index=pd.to_datetime(r["dates"]))
            member_rets[tid] = eq.pct_change().dropna()
            member_cutoffs[tid] = r.get("cutoff")
        per_member = {}
        for tid in REG6:
            v, ov = _corr(c1_rets, member_rets[tid])
            per_member[tid] = {"corr": v, "overlap_days": ov}
        finite = {t: v["corr"] for t, v in per_member.items()
                  if v["corr"] is not None}
        argmax = max(finite, key=lambda k: abs(finite[k])) if finite else None
        out["member_face"] = {
            "per_member": per_member, "member_cutoffs": member_cutoffs,
            "max_abs_corr": round(abs(finite[argmax]), 4) if argmax else None,
            "argmax_member": argmax,
            "reject": bool(argmax is not None
                           and abs(finite[argmax]) >= D6_REJECT),
        }
        # H4 alpha face: excess vs bench (C1-510300 vs member-510300)
        bench_r = bench_close.pct_change().dropna()
        vol_x = (member_rets.get("VOLATILITY-CE-01", pd.Series(dtype=float))
                 .sub(bench_r, fill_value=np.nan).dropna())
        v_x, ov_x = _corr(c1_rets.sub(bench_r, fill_value=np.nan).dropna(),
                          vol_x)
        out["h4_alpha_face"] = {
            "c1_excess_vs_volatility_member_excess_corr": v_x,
            "overlap_days": ov_x,
            "note": "alpha-corr significantly below the raw corr = "
                    "orthogonal-increment evidence (prereg s1)",
        }
    except Exception as exc:                      # honest pending face
        out["member_face"] = {"status": "pending_error",
                              "error": repr(exc)[:200]}
        out["h4_alpha_face"] = {"status": "pending_error"}
    same_batch, nulls_face = {}, {}
    for name, r in batch_rets.items():
        v, ov = _corr(c1_rets, r)
        same_batch[name] = {"corr": v, "overlap_days": ov}
    for i, r in enumerate(null_rets_list):
        v, _ov = _corr(c1_rets, r)
        nulls_face[f"draw{i}"] = v
    out["same_batch_face"] = same_batch
    out["null_family_face"] = {"values": nulls_face,
                               "note": "disclosure-only (non-judgment cells)"}
    out["reject_semantics"] = (
        "reject face = max|corr| vs REGISTERED members only (prereg s5.5 "
        "argmax prediction pins the reject face); same-batch C2/C3/C4 and "
        "the K32 nulls are disclosure faces (prereg s0 non-judgment cells)")
    return out


def orange_gate(c1, states, days, bench_close):
    """STYLE_CORPS s5 conditional gate: pooled held-day cumret vs bench on
    the same day-set (primary) + per-segment beats/CI (secondary)."""
    rets = c1["returns"]
    held = set(c1["held_days"])
    bench_r = bench_close.pct_change()
    day_pos = {d: i for i, d in enumerate(days)}
    segs = []
    in_seg, start, prev = False, None, None
    for d in days:
        st = states.get(d)
        if st == ORANGE and not in_seg:
            start, in_seg = d, True
        elif st != ORANGE and in_seg:
            segs.append((start, prev))
            in_seg = False
        prev = d
    if in_seg:
        segs.append((start, prev))
    rows = []
    for s0, s1 in segs:
        hd = [d for d in days if s0 <= d <= s1 and day_pos[d] in held
              and d in rets.index]
        if not hd:
            rows.append({"start": str(s0.date()), "end": str(s1.date()),
                         "held": 0})
            continue
        sr = rets.loc[hd]
        br = bench_r.reindex(hd)
        both = pd.concat([sr, br], axis=1).dropna()
        if not len(both):
            rows.append({"start": str(s0.date()), "end": str(s1.date()),
                         "held": 0})
            continue
        s_cum = float((1.0 + both.iloc[:, 0]).prod() - 1.0)
        b_cum = float((1.0 + both.iloc[:, 1]).prod() - 1.0)
        diff = (both.iloc[:, 0] - both.iloc[:, 1]).to_numpy()
        ci_half = (1.96 * float(np.std(diff, ddof=1)) / math.sqrt(len(diff))
                   if len(diff) > 1 else None)
        rows.append({
            "start": str(s0.date()), "end": str(s1.date()),
            "held_days": int(len(both)),
            "sleeve_cumret": round(s_cum, 6),
            "bench_cumret": round(b_cum, 6),
            "beat": bool(s_cum > b_cum),
            "diff_mean_daily": round(float(np.mean(diff)), 6),
            "diff_ci95": ([round(float(np.mean(diff)) - ci_half, 6),
                           round(float(np.mean(diff)) + ci_half, 6)]
                          if ci_half is not None else None),
        })
    beats = sum(1 for r in rows if r.get("beat"))
    hd_all = [d for d in rets.index if day_pos.get(d) in held]
    pooled_s = (round(float((1.0 + rets.loc[hd_all]).prod() - 1.0), 6)
                if hd_all else None)
    pooled_b = (round(float((1.0 + bench_r.reindex(hd_all)).prod() - 1.0), 6)
                if hd_all else None)
    n_total = len(rows)
    return {
        "primary_pooled_held_day_cumret": {
            "sleeve": pooled_s, "bench_same_dayset": pooled_b,
            "pass": bool(pooled_s is not None and pooled_s > pooled_b),
        },
        "secondary_per_segment": {
            "beat_count": int(beats), "segments": int(n_total),
            "majority_beat_pass": bool(beats * 2 > n_total),
            "prediction": f"{PRED['seg_beat_range'][0]}-"
                          f"{PRED['seg_beat_range'][1]}/{PRED['seg_total']}",
        },
        "per_segment": rows,
    }


def prediction_reconciliation(c1, d6, og, n_seg):
    """prereg s5 written-down predictions vs actuals (honesty face)."""
    mf = d6.get("member_face", {})
    argmax = mf.get("argmax_member")
    mac = mf.get("max_abs_corr")
    return {
        "entries": {
            "predicted": {"c1": PRED["c1_entries"],
                          "c2_c3": PRED["c23_entries"],
                          "c4": PRED["c4_entries"]},
            "actual_c1_leg_opens": c1["n_entries"],
            "actual_c1_events": c1["entry_events"],
            "in_range": bool(c1["n_entries"] >= 30),
        },
        "segment_beat": {
            "predicted_range": list(PRED["seg_beat_range"]),
            "actual": og["secondary_per_segment"]["beat_count"],
            "total_segments": n_seg,
        },
        "sharpe": {
            "predicted_range": list(PRED["c1_sharpe"]),
            "actual": c1["sharpe"],
            "note": "line pass/fail IS the batch ruling face, not prejudged",
        },
        "bound_triggers": {
            "predicted_min": PRED["bound_triggers_min"],
            "actual_cuts": len(c1["cuts"]),
            "actual_crisis_days": len(c1["crisis_log"]),
        },
        "d6": {
            "predicted_argmax": PRED["d6_argmax"],
            "predicted_range": list(PRED["d6_range"]),
            "actual_argmax": argmax, "actual_max_abs_corr": mac,
        },
        "recent_window": {
            "predicted_ann_range": list(PRED["recent_ann_range"]),
            "actual": c1["recent_ann"],
        },
        "null_family": {
            "note": "K32 values reported in full (three-iron-law baseline)",
            "n": K_NULLS,
        },
    }


# ---------------------------------------------------------------- run / cli

def cmd_run(_):
    t0 = time.time()
    if os.environ.get("DIV_LOWVOL_P1_REFINALIZE") != "1" \
            and os.path.exists(OUT_JSON):
        try:
            j = json.load(open(OUT_JSON, encoding="utf-8"))
            if j.get("trials_ledger"):
                print("REFINALIZE guard: results/div_lowvol_p1.json already "
                      "finalized (ledger block present). Set "
                      "DIV_LOWVOL_P1_REFINALIZE=1 for the only redo path.")
                return 2
        except Exception:
            pass
    if sg.SEED_REGISTRY.get("div_lowvol_p1") != SEED_BASE:
        print("VOID: seed base div_lowvol_p1 not registered in "
              "science_gates.SEED_REGISTRY (prereg s3: register BEFORE run)")
        return 2

    faces = load_faces()
    states, drift = regime_faces()
    # completeness gate (prereg s2.1/s2.2): zero NaN excl enumerated
    # suspension bars + leg/bench window-end coverage + drift bit-match
    susp = faces["suspension_days"]
    nan_excl = {}
    for c in LEGS:
        cl = faces["legs"][c]["close"]
        idx = [i for i, d in enumerate(faces["days"])
               if str(d.date()) not in susp]
        nan_excl[c] = int(np.sum(~np.isfinite(cl[idx])))
    bench_nan = int(np.sum(~np.isfinite(faces["bench"]["close"])))
    cover_end = all(np.isfinite(faces["legs"][c]["close"][-1]) for c in LEGS)
    comp = {"nan_close_days_excl_suspension": nan_excl,
            "bench_nan": bench_nan, "legs_cover_window_end": cover_end,
            "suspension_bars_whitelisted": sorted(susp),
            "n_bench_trading_days": int(faces["n"])}
    comp_ok = (all(v == 0 for v in nan_excl.values()) and bench_nan == 0
               and cover_end and drift["counts_match"])
    if not comp_ok:
        print("VOID: completeness/drift gate FAILED:", json.dumps(
            {"completeness": comp, "drift": drift}, ensure_ascii=False)[:800])
        return 2
    _log(f"gates: completeness+drift OK ({faces['n']} bench days, "
         f"{len(drift['recorded_window_orange_durations'])} ORANGE episodes)")

    mask = sleeve_mask(states, faces["days"])
    weights_pair = {"512890": 0.5, "510880": 0.5}
    cells = {}
    cells_rets = {}
    specs = [
        ("C1", mask, weights_pair, True),
        ("C2", mask, {"512890": 1.0}, True),
        ("C3", mask, {"510880": 1.0}, True),
        ("C4", None, weights_pair, False),
    ]
    for name, m, w, bounds in specs:
        per_face = {}
        for fkey, fn in FACES.items():
            per_face[fkey] = simulate_sleeve(faces, m, w, bounds_on=bounds,
                                            cost_fn=fn, capital=CAPITAL)
        cells[name] = per_face
        cells_rets[name] = per_face["x2"]["returns"]   # judged face series
    _log("cells: C1-C4 x3 faces done")

    nulls = run_nulls(faces, drift["recorded_window_orange_durations"])
    null_rets_list = []
    for k in range(K_NULLS):
        m, _pl = build_null_mask(
            drift["recorded_window_orange_durations"], faces["n"],
            SEED_BASE + k)
        r = simulate_sleeve(faces, m, weights_pair, bounds_on=True,
                            cost_fn=FACES["x2"], capital=CAPITAL)
        null_rets_list.append(r["returns"])
    _log(f"nulls: K={K_NULLS} drawn (mu={nulls['coverage']['mu']:.4f} "
         f"sigma={nulls['coverage']['sigma']:.4f})")

    # passive: 510300 buy-and-hold, in-batch disclosure (mf_rot precedent)
    bench_eq = faces["bench"]["close"]
    passive = {"510300_bh_ann": round(float(
        (bench_eq[-1] / bench_eq[0]) ** (252.0 / faces["n"]) - 1.0), 6),
        "note": "skill line passive anchor = pool core48 via shared library"}

    bench_close = pd.Series(faces["bench"]["close"], index=faces["days"])
    d6 = d6_block(cells_rets["C1"],
                  {k: v for k, v in cells_rets.items() if k != "C1"},
                  null_rets_list, bench_close)
    og = orange_gate(cells["C1"]["x2"], states, faces["days"], bench_close)

    # G1'v2 (C1 judged face) + G2 (DSR + family CSCV PBO over C1-C4)
    null_pool = {"values": nulls["values_rounded"],
                 "coverage": nulls["coverage"]}
    line = sg.skill_line_v2(batch_cells=BATCH_CELLS_NOMINAL, pool="core48",
                            null_pool=null_pool)
    c1x = cells["C1"]["x2"]
    g1 = sg.g1_prime_v2(sharpe_full=c1x["sharpe"], returns=c1x["returns"],
                        batch_cells=BATCH_CELLS_NOMINAL, pool="core48",
                        null_pool=null_pool, n_trades=c1x["n_trades"],
                        n_entries=c1x["n_entries"])
    from pbo import cscv_pbo, align_returns
    fam = {k: cells_rets[k] for k in ("C1", "C2", "C3", "C4")}
    mat = align_returns(fam)
    fam_pbo = cscv_pbo(mat)
    dsr = sg.deflated_sharpe_ratio(c1x["returns"], n_trials=line["n_eff"],
                                   var_null_sr=nulls["coverage"]["sigma"] ** 2)
    g2 = sg.g2_registration_v2(g1_pass=bool(g1["pass_v2"]), dsr=dsr,
                                pbo=fam_pbo["pbo"])

    descriptive = {
        "full_ann_positive": bool((c1x["ann_ret"] or 0) > 0),
        "recent_2021plus_ann": c1x["recent_ann"],
        "recent_dual_positive": bool((c1x["recent_ann"] or 0) > 0),
        "max_dd_red_line_pass": bool((c1x["max_dd"] or 0) >= -0.35),
        "cost_face_totals": {f: cells["C1"][f]["cost_total"]
                             for f in FACES},
        "note": "per-face totals + per-segment costs in cells block",
    }

    def _cell_face(rec):
        r = {k: v for k, v in rec.items() if k not in ("returns", "eq")}
        return r

    cells_out = {name: {f: _cell_face(rec) for f, rec in per_face.items()}
                 for name, per_face in cells.items()}

    recon = prediction_reconciliation(
        c1x, d6, og, len(drift["recorded_window_orange_durations"]))

    led = sg.append_ledger("DIV_LOWVOL_P1", BATCH_CELLS_NOMINAL,
                           file_name="results/div_lowvol_p1.json",
                           evidence_cutoff=WINDOW_END,
                           note=(f"C1-C4 (2-leg ORANGE carry sleeve + "
                                 f"attribution/ablation) + K{K_NULLS} random "
                                 f"segment-mask nulls (seeds 60000+k, "
                                 f"registered div_lowvol_p1); prereg "
                                 f"research/DIV_LOWVOL_P1.md frozen R178"))
    att = json.load(open(ATT_JSON, encoding="utf-8"))
    att_row = {
        "batch": "DIV_LOWVOL_P1", "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
        "kind": "measurement", "cells_ledger_delta": BATCH_CELLS_NOMINAL,
        "ledger_total_after": led["total"],
        "gates": {"completeness_pass": True, "drift_match": True,
                  "g1_prime_pass": bool(g1["pass_v2"]),
                  "g2_eligible": bool(g2["eligible_v2"]),
                  "orange_gate_primary":
                      og["primary_pooled_held_day_cumret"]["pass"],
                  "d6_reject": d6.get("member_face", {}).get("reject")},
        "eliminated": BATCH_CELLS_NOMINAL - (1 if g2["eligible_v2"] else 0),
        "refs": {"prereg": "research/DIV_LOWVOL_P1.md", "ticket": TICKET},
    }
    att["entries"].append(att_row)

    prereg_sha = None
    try:
        import hashlib
        prereg_sha = hashlib.sha256(
            open(PREREG, "rb").read().replace(b"\r\n", b"\n")).hexdigest()
    except Exception:
        pass

    payload = {
        **sg.cutoff_meta(WINDOW_END),
        "meta": {"batch": "DIV_LOWVOL_P1", "dept": "research+strategy",
                 "ticket": TICKET, "prereg": "research/DIV_LOWVOL_P1.md",
                 "prereg_sha256_lf_normalized": prereg_sha,
                 "judge_face": "x2 (whole-V2 doubled, CostPatch single-source)",
                 "seed_base_registered": "div_lowvol_p1=60000",
                 "window": {"start": WINDOW_START, "end": WINDOW_END,
                            "recent": RECENT_START},
                 "orange_days_in_window": int(mask.sum()),
                 "machine": _machine_id()},
        "gates": {"completeness": comp, "regime_drift": drift},
        "cells": cells_out,
        "nulls": nulls,
        "passive": passive,
        "d6_correlation": d6,
        "orange_segment_gate": og,
        "skill_line": line,
        "g1_prime_v2": g1,
        "g2_registration_v2": g2,
        "family_pbo": {k: fam_pbo[k] for k in ("pbo", "n_blocks")
                       if k in fam_pbo},
        "dsr": dsr,
        "descriptive": descriptive,
        "prediction_reconciliation": recon,
        "audit": {"elapsed_sec": round(time.time() - t0, 1),
                  "cells": len(cells), "nulls": K_NULLS,
                  "member_gate_runs": len(REG6), "workers": 1},
        "trials_ledger": led,
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
    _log(f"finalize: ledger total={led['total']} | g1={g1['pass_v2']} "
         f"g2={g2['eligible_v2']} | orange_gate="
         f"{og['primary_pooled_held_day_cumret']['pass']} | d6_reject="
         f"{d6.get('member_face', {}).get('reject')} | C1 sharpe="
         f"{c1x['sharpe']} entries={c1x['n_entries']}")
    print(f"[div_lowvol] written {OUT_JSON}; g1_prime_v2={g1['pass_v2']} "
          f"g2={g2['eligible_v2']} sharpe={c1x['sharpe']}")
    return 0


def _machine_id():
    try:
        return json.load(open(os.path.join(ROOT, "fleet", "machine.json"),
                              encoding="utf-8-sig"))["machine_id"]
    except Exception:
        return os.environ.get("COMPUTERNAME", "unknown")


# ---------------------------------------------------------------- selftest

def _mk_faces(days, legs_spec, bench=None):
    """Synthetic face dict mirroring load_faces() shapes (hermetic)."""
    n = len(days)
    legs = {}
    for c, spec in legs_spec.items():
        legs[c] = {"open": np.array(spec["open"], dtype=float),
                   "close": np.array(spec["close"], dtype=float),
                   "tradable": np.array(spec.get(
                       "tradable", [True] * n), dtype=bool),
                   "adv": np.array(spec.get("adv", [1e12] * n), dtype=float)}
    b = bench or {"close": [100.0] * n, "open": [100.0] * n}
    return {"days": pd.DatetimeIndex(days), "n": n, "legs": legs,
            "bench": {"close": np.array(b["close"], dtype=float),
                      "open": np.array(b["open"], dtype=float)},
            "suspension_days": set()}


def cmd_selftest(_):
    fails = []

    def ok(fid, cond, detail=""):
        print(f"  [{'PASS' if cond else 'FAIL'}] {fid} {detail}")
        if not cond:
            fails.append(fid)

    # F1 split adjustment: in-memory x0.5, phantom return removed (probe
    # event-list single source; production form = suspension bar two days
    # before the first post-split bar; fixture SPANS the split date)
    df = pd.DataFrame({
        "open": [1.6, 1.63, np.nan, 1.62, 1.61, 1.60, 0.80],
        "high": [1.7] * 7, "low": [1.5] * 7,
        "close": [1.639, 1.64, np.nan, 1.63, 1.62, 1.61, 0.801],
        "volume": [1e8] * 7, "amount": [1e8] * 7,
    }, index=pd.date_range("2021-10-19", periods=7))
    adj = DLP._adjust_split(df, DLP.SPLIT_EVENTS["512890"])
    r_adj = float(adj["close"].iloc[6] / adj["close"].iloc[1] - 1.0)
    r_raw = float(df["close"].iloc[6] / df["close"].iloc[1] - 1.0)
    ok("F1 split-adjust removes phantom return", abs(r_adj + 0.023) < 0.03
       and r_raw < -0.5, f"adj={r_adj:.4f} raw={r_raw:.4f}")

    # F2 gate timing: state ORANGE at close t -> enter open t+1; exit-day
    # P&L = open/prev_close-1 (hand-computed, x1-cost drag ~5e-4/leg-turn)
    days = pd.date_range("2024-01-01", periods=6)
    px = [1.0, 1.0, 1.0, 1.1, 1.0, 1.0]
    faces = _mk_faces(days, {"L": {"open": px, "close": px}})
    mask = np.array([False, True, True, True, False, False])
    r = simulate_sleeve(faces, mask, {"L": 1.0}, bounds_on=True,
                        cost_fn=FACES["x1"], capital=1_000_000.0)
    rets = r["returns"]
    exp = [0.0, -0.000504, 0.09995, -0.09086, -0.000504]
    ok("F2 gate timing + exit-day open/prev_close P&L",
       len(rets) == 5 and all(abs(float(v) - e) < 1e-3
                              for v, e in zip(rets.values, exp))
       and r["n_entries"] == 1 and r["n_trades"] == 1
       and r["held_days"] == [2, 3, 4, 5],
       f"rets={[round(float(v),6) for v in rets.values]} "
       f"held={r['held_days']}")

    # F3 bound (b): single-day crash through -12% HWM -> cut next open +
    # lock (no re-entry despite continued ORANGE mask)
    days = pd.date_range("2024-01-01", periods=12)
    px = [1.0, 1.0, 1.0, 0.85, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5]
    faces = _mk_faces(days, {"L": {"open": px, "close": px}})
    mask = np.array([True] * 11 + [False])
    r = simulate_sleeve(faces, mask, {"L": 1.0}, bounds_on=True,
                        cost_fn=FACES["x1"], capital=1_000_000.0)
    ok("F3 bound(b) HWM cut + segment lock",
       len(r["cuts"]) == 1 and r["cuts"][0]["reason"]["type"] == "b_hwm_dd"
       and r["n_trades"] == 1 and r["n_entries"] == 1,
       f"cuts={r['cuts']}")

    # F4 bound (a): CROSS-EPISODE sustained bleed -- trailing 20d cumret
    # (account face, includes out-day zeros) pierces -12.67% while each
    # episode's own HWM dd stays above -12%, so (a) fires and (b) never
    # does; then lock holds (no re-entry mid-segment) and the NEXT
    # segment re-enters (lock cleared at episode start)
    days = pd.date_range("2024-01-01", periods=30)
    cl = [1.0]
    for k in range(1, 11):                 # ep1: 10 days at -1.2%/day
        cl.append(0.988 ** k)
    for _ in range(11, 16):                # flat exit + 4 flat days
        cl.append(0.988 ** 10)
    for k in range(1, 6):                  # ep2: 5 days at -1.4%/day
        cl.append(0.988 ** 10 * 0.986 ** k)
    for _ in range(21, 26):                # cut + flat
        cl.append(0.988 ** 10 * 0.986 ** 5)
    cl.append(cl[-1] * 1.01)               # ep3: mild rise
    cl.append(cl[-1] * 1.01)
    cl.append(cl[-1])
    cl.append(cl[-1])
    op = [cl[0]] + cl[:-1]                 # open[i] = prev close
    faces = _mk_faces(days, {"L": {"open": op, "close": cl}})
    mask = np.array([True] * 10 + [False] * 5 + [True] * 7
                    + [False] * 3 + [True] * 3 + [False] * 2)
    r = simulate_sleeve(faces, mask, {"L": 1.0}, bounds_on=True,
                        cost_fn=FACES["x1"], capital=1_000_000.0)
    a_cut = [c for c in r["cuts"] if c["reason"]["type"] == "a_cum20"]
    locked_gap = [d for d in r["held_days"] if 22 <= d <= 25]
    ok("F4 bound(a) cross-episode bleed cut + lock + next-seg re-entry",
       len(r["cuts"]) == 1 and len(a_cut) == 1 and not locked_gap
       and r["entry_events"] == 3 and r["n_entries"] == 3,
       f"cuts={[c['day'] for c in r['cuts']]} "
       f"type={r['cuts'][0]['reason']['type'] if r['cuts'] else None} "
       f"entries={r['n_entries']} locked_gap={locked_gap}")

    # F5 crisis log: |r1|>=5% in-position day logged
    days = pd.date_range("2024-01-01", periods=8)
    px = [1.0, 1.0, 0.94, 0.94, 0.94, 0.94, 0.94, 0.94]
    faces = _mk_faces(days, {"L": {"open": px, "close": px}})
    mask = np.array([True] * 7 + [False])
    r = simulate_sleeve(faces, mask, {"L": 1.0}, bounds_on=True,
                        cost_fn=FACES["x1"], capital=1_000_000.0)
    ok("F5 crisis log |r1|>=5%", len(r["crisis_log"]) >= 1,
       f"crisis={r['crisis_log']}")

    # F6 cost faces monotone + commission floor + lot + ADV cap refusal
    from knowledge import rules as krules
    g = 500_000.0
    c1, c2, c3 = side_cost_v2(g, 1e9), side_cost_x2(g, 1e9), \
        side_cost_x3(g, 1e9)
    ok("F6 cost faces monotone x1<x2<x3", c1 < c2 < c3,
       f"{c1:.2f}/{c2:.2f}/{c3:.2f}")
    ok("F6 commission floor active at tiny gross",
       side_cost_v2(100.0, 1e9) >= krules.FeeSchedule.commission_min)
    days = pd.date_range("2024-01-01", periods=3)
    faces = _mk_faces(days, {"L": {"open": [1.0] * 3, "close": [1.0] * 3,
                                   "adv": [100.0] * 3}})
    mask = np.array([True, True, False])
    r = simulate_sleeve(faces, mask, {"L": 1.0}, bounds_on=False,
                        cost_fn=FACES["x1"], capital=1_000_000.0)
    ok("F6 1% ADV fill cap refuses oversized entry",
       r["n_entries"] == 0 and r["fill_refusals"] >= 1,
       f"entries={r['n_entries']} refusals={r['fill_refusals']}")

    # F7 null masks: determinism, multiset preserved, non-overlap, distinct
    durs = [3, 5, 2]
    m1, p1 = build_null_mask(durs, 40, SEED_BASE)
    m2, _ = build_null_mask(durs, 40, SEED_BASE)
    m3, _ = build_null_mask(durs, 40, SEED_BASE + 1)
    got_durs = sorted(e - s + 1 for s, e in p1)
    no_overlap = all(e1 < s2 or s1 > e2
                     for i, (s1, e1) in enumerate(p1)
                     for s2, e2 in p1[i + 1:])
    ok("F7 null mask: deterministic + multiset + non-overlap + distinct",
       (m1 == m2).all() and got_durs == sorted(durs) and no_overlap
       and not (m1 == m3).all(), f"placed={p1}")

    # F8 suspension: held leg missing close -> no mark that day (returns
    # span), no trade that day
    days = pd.date_range("2021-10-20", periods=5)
    cl = [1.0, 1.0, np.nan, 1.04, 1.04]
    faces = _mk_faces(days, {"L": {"open": cl, "close": cl,
                                   "tradable": [True, True, False,
                                                True, True]}})
    mask = np.array([True, True, True, True, False])
    r = simulate_sleeve(faces, mask, {"L": 1.0}, bounds_on=True,
                        cost_fn=FACES["x1"], capital=1_000_000.0)
    marked = [str(d.date()) for d in r["returns"].index]
    ok("F8 suspension no-mark + spanning returns",
       "2021-10-22" not in marked and r["n_marks"] == 4,
       f"marked={marked}")

    # F9 C4 ablation: bounds off -> holds through crash, no cuts
    days = pd.date_range("2024-01-01", periods=10)
    px = [1.0, 1.0, 1.0, 0.7, 0.6, 0.55, 0.5, 0.5, 0.5, 0.5]
    faces = _mk_faces(days, {"L": {"open": px, "close": px}})
    r = simulate_sleeve(faces, None, {"L": 1.0}, bounds_on=False,
                        cost_fn=FACES["x1"], capital=1_000_000.0)
    ok("F9 C4 ablation holds through crash (no gate no bounds)",
       r["n_entries"] == 1 and r["n_trades"] == 0 and len(r["cuts"]) == 0
       and r["truncated"] is True,
       f"entries={r['n_entries']} cuts={len(r['cuts'])}")

    # F10 out-of-market marked days contribute 0 to the judged series
    days = pd.date_range("2024-01-01", periods=8)
    px = [1.0, 1.0, 1.1, 1.1, 1.1, 1.1, 1.1, 1.1]
    faces = _mk_faces(days, {"L": {"open": px, "close": px}})
    mask = np.array([False, True, True, False, False, False, False, False])
    r = simulate_sleeve(faces, mask, {"L": 1.0}, bounds_on=False,
                        cost_fn=FACES["x1"], capital=1_000_000.0)
    vals = list(r["returns"].values)
    ok("F10 flat marked days = 0 returns (full-timeline face)",
       len(vals) == 7 and vals[0] == 0.0
       and abs(vals[1] + 0.000504) < 1e-5
       and vals[2] == 0.0 and abs(vals[3] + 0.000504) < 1e-5
       and all(v == 0.0 for v in vals[4:])
       and r["held_days"] == [2, 3, 4],
       f"rets={[round(float(v), 6) for v in vals]}")

    # F11 determinism: mini-pipeline double-run byte identity (zero
    # wall-clock inside sim outputs)
    def _mini():
        d = pd.date_range("2024-01-01", periods=24)
        up = [1.0 * (1.01 ** (i % 7)) for i in range(24)]
        f = _mk_faces(d, {"A": {"open": up, "close": up},
                          "B": {"open": [v * 0.9 for v in up],
                                "close": [v * 0.9 for v in up]}})
        m = np.array([True] * 20 + [False] * 4)
        out = {}
        for name, mk, w, b in (("C1", m, {"A": 0.5, "B": 0.5}, True),
                               ("C4", None, {"A": 0.5, "B": 0.5}, False)):
            rec = simulate_sleeve(f, mk, w, bounds_on=b,
                                  cost_fn=FACES["x2"], capital=1_000_000.0)
            rec = {k: v for k, v in rec.items() if k not in ("returns", "eq")}
            out[name] = rec
        nm, _ = build_null_mask([4, 3], 24, SEED_BASE + 7)
        rec = simulate_sleeve(f, nm, {"A": 0.5, "B": 0.5}, bounds_on=True,
                              cost_fn=FACES["x2"], capital=1_000_000.0)
        out["null"] = {k: v for k, v in rec.items()
                       if k not in ("returns", "eq")}
        return json.dumps(out, sort_keys=True, default=str)

    a, b = _mini(), _mini()
    ok("F11 double-run byte identity", a == b and len(a) > 500)

    # F12 orange gate helpers on tiny synthetic
    days = pd.date_range("2024-01-01", periods=10)
    px = [1.0, 1.0, 1.05, 1.02, 1.06, 1.0, 1.0, 1.0, 1.0, 1.0]
    faces = _mk_faces(days, {"L": {"open": px, "close": px}},
                      bench={"close": [1.0] * 10, "open": [1.0] * 10})
    mask = np.array([True] * 5 + [False] * 5)
    c1 = simulate_sleeve(faces, mask, {"L": 1.0}, bounds_on=False,
                         cost_fn=FACES["x1"], capital=1_000_000.0)
    states = {d: (ORANGE if i < 5 else GREEN) for i, d in enumerate(days)}
    bench_close = pd.Series([1.0] * 10, index=days)
    og = orange_gate(c1, states, days, bench_close)
    ok("F12 orange gate pooled + per-segment beats",
       og["primary_pooled_held_day_cumret"]["sleeve"] is not None
       and og["secondary_per_segment"]["segments"] == 1
       and og["per_segment"][0]["beat"] is True,
       json.dumps(og["primary_pooled_held_day_cumret"]))

    # F13 corr helper: perfect + anti + insufficient overlap
    s = pd.Series([0.01, 0.02, -0.01, 0.03, 0.01] * 6,
                  index=pd.date_range("2024-01-01", periods=30))
    t = pd.Series([0.01, 0.02, -0.01, 0.03, 0.01] * 6,
                  index=pd.date_range("2024-01-01", periods=30))
    v_p, _ = _corr(s, t)
    v_n, _ = _corr(s, -t)
    v_i, ov_i = _corr(s.iloc[:5], t.iloc[:5], min_overlap=20)
    ok("F13 corr helper: perfect/anti/insufficient",
       abs(v_p - 1.0) < 1e-9 and abs(v_n + 1.0) < 1e-9 and v_i is None
       and ov_i == 5)

    # F14 window-end truncation: mask ORANGE at end -> open position,
    # truncated flag, entries > trades
    days = pd.date_range("2024-01-01", periods=4)
    px = [1.0, 1.0, 1.1, 1.2]
    faces = _mk_faces(days, {"L": {"open": px, "close": px}})
    mask = np.array([True, True, True, True])
    r = simulate_sleeve(faces, mask, {"L": 1.0}, bounds_on=False,
                        cost_fn=FACES["x1"], capital=1_000_000.0)
    ok("F14 window-end truncation face",
       r["truncated"] is True and r["n_entries"] == 1 and r["n_trades"] == 0)

    print(f"div_lowvol selftest: {14 - len(fails)}/14 PASS, "
          f"{len(fails)} FAIL")
    return 0 if not fails else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "selftest"])
    args = ap.parse_args()
    if args.cmd == "selftest":
        return cmd_selftest(args)
    return cmd_run(args)


if __name__ == "__main__":
    raise SystemExit(main())
