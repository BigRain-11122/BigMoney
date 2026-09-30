"""ETF_OPS_BP2 runner -- 周期定投纪律链全网格回测批 (T-103 s2 chain #2).

Laws frozen in research/etf_ops/ETF_OPS_BP2_PREREG.md (R458 freeze commit
b809b59d1, SEED_REGISTRY['etf_ops_bp2']=20294100 registered same commit,
R250 law; band 20294100..20294114 rg-scan clean). Freeze precedes runner
build precedes ANY burn. Run-products may only backfill prereg s7; criteria
are never re-derived by hand (O-2250 single-source: gate lines come from
science_gates).

  members five-member two-tier frozen universe (O-1555): 510050 / 510300 /
          510500 / 512100 / 588000 (20cm tier). G-ANCHOR-FACE four-tuple per
          member + row census + last-bar == evidence_cutoff 2026-09-29 --
          any face mismatch = fail-closed refuse (exit 2), reported as
          face-mismatch not data-rot (INCIDENT-20260928 law). D2 lockbox:
          rows after cutoff never enter (loader truncates, discloses).
  entry  monthly calendar DCA (prereg s3, zero-skill claim): signal = first
          trading day of each Gregorian month on the member's own panel
          calendar; execution = T+1 next-open buy ONE unit; skip-while-
          holding (single position, no pyramiding; skipped_signals
          disclosed: valid signals lost to an open position, the reentry
          window, or a window boundary); after round close the next monthly
          signal must be strictly > exit-fill day (same-day no-reentry,
          BP1 frozen mirror); guard-isolated monthly signal day -> that
          month skipped (member-level guard_isolated_signals counter).
          NO data-derived entry condition (MA200/depth faces REMOVED --
          the transplanted face is the exit stack ONLY).
  exits  BP1 exit stack verbatim transplant: TP1 close >= entry*(1+P1) ->
          T+1 open sell 50%; TP2 close >= entry*(1+P2) -> T+1 open clear;
          hard SL close <= entry*0.92; trend SL close < MA200 -> T+1 open
          clear (NaN-warmup inert, honest). Same-close-day priority
          trend_sl > hard_sl > tp2 > tp1 (engine/exit_rules canon mirror).
          TP1 remainder keeps entry_cost basis.
  limit  honest accounting (BP1 verbatim): entry-day one-word limit-up ->
          blocked_entry (round voided, that month consumed; NOT in win
          denominator); exit-day one-word limit-down -> blocked_exit
          (committed exit rolls to next tradable open, no re-evaluation).
  guard  fund event guard r239 frozen law (BP1 verbatim): day |r1| > 10.5%
          (588000: 20.5%) AND same-day five-member universe median |r1|
          < 3% -> member-day isolated.
  costs  V1 legacy 13.041bp/side single source = alloc_backtest.V1_FLAT_SIDE;
          dual track base x1 + x2 (CostPatch multiplier law). Multiplicative
          both legs: leg net = px_exit*(1-c_out)/(px_entry*(1+c_in)) - 1.
          JUDGED FACE = x2; x1 = disclosure face.
  window primary face (prereg s3 window-paired engine): virtual windows
          L in {126, 252, 504} td, every feasible start s (s+L <= n, T-22
          lineage), each window simulated independently (flat start):
            chain leg  = monthly signals -> T+1 open entries -> exit stack;
                        window end (L-1 bar) forces close of any open
                        position (incl. TP1 remainder; pending blocked_exit
                        rolls to window end) at LAST-BAR CLOSE mark, costs
                        counted (window-boundary measurement fill, frozen).
            dca leg    = same ACTUAL chain entry fills (same day, same
                        price, same costs), each unit held to window end,
                        sold at last-bar close (entry sets identical ->
                        isolates the exit-discipline increment).
          window metric = per-unit net means of both legs; paired_diff =
          mean(chain unit nets) - mean(dca unit nets); windows with < 2
          chain filled units excluded from the paired set (counted).
          Implementation law = vectorized-across-starts numpy state
          machine; selftest asserts byte-identity vs the brute-force
          reference on the FULL start set (>= 50 windows/member by far).
  primary gate (prereg s4, judged face x2): per member-cell pool ALL
          qualified windows (3 lengths x all starts): median(paired_diff)
          > 0 AND bootstrap CI95 (10,000 resamples, percentile method,
          rng default_rng([20294100, 1000+cell_idx])) excludes 0.
          Batch primary count = passing cells / 15.
  gates  G1'v2 (science_gates.g1_prime_v2, batch_cells=15, pool='core48')
          on the chain full-panel daily mark-to-market x2 series (BP1
          chain_daily booked-evenly face, eval_start = first MA200-valid);
          DSR (deflated_sharpe_ratio, n_eff = head_base+15, r253 redo-echo
          guard); family PBO CSCV-8 over the 15-cell x2 matrix (common-tail
          alignment, 588000 warmup face); g2_registration_v2. Combined
          registration = primary gate AND G2 (primary fail = no
          registration regardless of Sharpe).
  nulls  K=200 uniform-random-trading-day-entry null per member-cell
          (equal round count, same exit stack, same costs; rng
          default_rng([20294100, cell_idx]), cell_idx < 15; pool = all
          panel days except the last, guard days kept = naive uniform
          face, disclosed) -- continuity face ONLY, never a gate (prereg
          s3: monthly-rhythm vs any-day zero-skill claim readout).
  faces  beat-passive (full-panel chain cum vs buy-hold + virtual
          timepoints {6m,12m,24m} x {x1,x2} beat rates, BP1 verbatim);
          beat-pure-DCA (naive all-months-no-skip DCA held to panel end,
          per-unit mean vs chain full-panel per-unit mean; naive face =
          no guard, blocked entries void only, disclosed).
  regime disclosure-only (never a switch gate): paired_diff medians
          stratified by T-74 L2 route state (GREEN/CHOP/ORANGE/RED,
          YELLOW->CHOP, imported frozen regime_deep_replay v3) and T-89
          segment (bear/chop/bull at window start); no all-weather claims.
  d6     reject face = max|corr| vs the six registered trader sleeves
          (REG6, ew6 canon member_run, live.paper anchor path); >= 0.7 ->
          cell rejected.

Products (prereg s6): results/etf_ops/bp2_grid.json (top evidence_cutoff +
science_gates.cutoff_meta mandatory) + bp2_nulls.json + bp2_windows.json +
bp2_rounds_<code>.csv + bp2_windows_npy/<code>_<cellidx>_<face>.npy
(qualified-window rows [start_idx, L, paired_diff]) + bp2_series/
<code>_<cellidx>_<face>.npy chain daily streams + shard files
bp2_shard_<code>.json. Deterministic: no wall-clock in any product;
re-run byte-identical.

Usage:
  python scripts/etf_ops_bp2.py run --shard 510300     (one member burn)
  python scripts/etf_ops_bp2.py run --shard all         (five sequential)
  python scripts/etf_ops_bp2.py finalize
  python scripts/etf_ops_bp2.py status
  python scripts/etf_ops_bp2.py selftest                 (hermetic, offline)

Exit contract: 0 ok/no-op; 2 fail-closed gate refusal; 3 RAM floor.
"""
import argparse
import json
import os
import sys
import tempfile

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import science_gates as SG                      # shared gate library (O-2250)
from alloc_backtest import V1_FLAT_SIDE          # V1 13.041bp single source
import etf_ops_bp1 as BP1                        # inherited machinery

OUT_DIR = os.path.join(ROOT, "results", "etf_ops")
WN_DIR = os.path.join(OUT_DIR, "bp2_windows_npy")
SER_DIR = os.path.join(OUT_DIR, "bp2_series")
OUT_JSON = os.path.join(OUT_DIR, "bp2_grid.json")
OUT_NULLS = os.path.join(OUT_DIR, "bp2_nulls.json")
OUT_WINDOWS = os.path.join(OUT_DIR, "bp2_windows.json")

EVIDENCE_CUTOFF = "2026-09-29"
BATCH_NAME = "ETF_OPS_BP2"
SEED_KEY = "etf_ops_bp2"
BATCH_CELLS = 15
N_BOOT = 10000
BOOT_CHUNK = 100
PBP = 252
D6_REJECT = 0.7
HARD_SL_MULT = 0.92
RAM_FLOOR_GB = 2.0                # light batch: five small CSVs (r354 family)
WINDOWS = {"6m": 126, "12m": 252, "24m": 504}
OOS_FROM = "2025-01-01"

# frozen member order + G-ANCHOR-FACE (prereg s2 table verbatim, cutoff 09-29)
MEMBERS = ["510050", "510300", "510500", "512100", "588000"]
ANCHORS = {
    "510050": {"path": "data/daily/sh510050.csv", "first": "2005-02-23", "rows": 5252},
    "510300": {"path": "data/daily/sh510300.csv", "first": "2012-05-28", "rows": 3487},
    "510500": {"path": "data/daily/sh510500.csv", "first": "2013-03-15", "rows": 3290},
    "512100": {"path": "data/daily/sh512100.csv", "first": "2016-11-04", "rows": 2406},
    "588000": {"path": "data/daily/sh588000.csv", "first": "2020-11-16", "rows": 1426},
}
TIER_20CM = {"588000"}
# frozen grid (prereg s0: (P1,P2) in {(5,10),(6,12),(8,15)} pct)
GRID = [
    {"P1": 0.05, "P2": 0.10},
    {"P1": 0.06, "P2": 0.12},
    {"P1": 0.08, "P2": 0.15},
]
COST_X1 = float(V1_FLAT_SIDE)          # 13.041bp/side (V1 single source)
COST_X2 = COST_X1 * 2.0                # CostPatch multiplier law (x2 face)

GRAMMAR = BATCH_NAME + "|v1|cutoff=" + EVIDENCE_CUTOFF + \
    "|monthly-first-td-T+1open|skip-while-holding|reentry>exit_fill_day" \
    "|prio trend>hard>tp2>tp1|SL0.92|MA200,minp200" \
    "|TP{(5,10),(6,12),(8,15)}|windows 126/252/504 all-starts" \
    "|forced-close last-close|dca same-entry|paired median>0+CI95excl0" \
    "|boot 10k pct rng[20294100,1000+ci]" \
    "|nulls uniform-days K" + str(BP1.K_NULLS) + \
    "|judged=x2|V1FLAT=" + format(COST_X1, ".7f")

GRAMMAR_SHA16 = BP1._sha16(GRAMMAR)


def gate_refuse(msg):
    print(f"GATE-REFUSE(exit2): {msg}")
    return 2


def load_member(code, data_dir=None, anchors=None, cutoff=None):
    """G-ANCHOR-FACE fail-closed loader (BP1 machinery, BP2 anchor table)."""
    return BP1.load_member(code, data_dir=data_dir,
                           anchors=anchors or ANCHORS,
                           cutoff=cutoff or EVIDENCE_CUTOFF)


def monthly_signal_mask(m):
    """First trading day of each Gregorian month on the member's own panel
    calendar (prereg s3 entry face; zero data-derived condition)."""
    mask = np.zeros(m["n"], dtype=bool)
    prev_ym = None
    for i, d in enumerate(m["dates"]):
        ym = d[:7]
        if ym != prev_ym:
            mask[i] = True
            prev_ym = ym
    return mask


def member_aux(m, med_abs):
    """BP1 member_arrays + the monthly mask (BP2 auxiliary face)."""
    thr = BP1.GUARD_THR_20CM if m["code"] in TIER_20CM else BP1.GUARD_THR
    aux = BP1.member_arrays(m, med_abs, thr)
    aux["monthly"] = monthly_signal_mask(m)
    return aux


def chain_rounds(m, aux, grid, cost_x1, cost_x2):
    """Full-panel sequential chain face: monthly signal candidates (guard
    excluded), BP1 state machine semantics + skip/guard counters (prereg
    s3). Returns (rounds, stats) -- rounds identical schema to BP1."""
    o, c, ma = m["o"], m["c"], m["ma200"]
    n = m["n"]
    P1, P2 = grid["P1"], grid["P2"]
    dates = m["dates"]
    monthly = aux["monthly"]
    iso = aux["isolated"]
    cand = [int(i) for i in np.flatnonzero(monthly & ~iso)]
    rounds = []
    blocked_entries = 0
    open_at_end = 0
    skipped_signals = 0
    guard_isolated_signals = int((monthly & iso).sum())
    last_exit = -1
    for s in cand:
        if s <= last_exit:
            skipped_signals += 1
            continue
        e = s + 1
        if e >= n:
            skipped_signals += 1        # signal on last panel day: no T+1
            continue
        if aux["limit_up"][e]:
            blocked_entries += 1
            last_exit = e              # signal consumed; BP1 mirror
            continue
        entry = float(o[e])
        legs = []
        tp1_done = False
        d = e
        tag = None
        while d < n:
            pri = None
            if np.isfinite(ma[d]) and c[d] < ma[d]:
                pri = "trend_sl"
            elif c[d] <= entry * HARD_SL_MULT:
                pri = "hard_sl"
            elif c[d] >= entry * (1.0 + P2):
                pri = "tp2"
            elif (not tp1_done) and c[d] >= entry * (1.0 + P1):
                pri = "tp1"
            if pri is None:
                d += 1
                continue
            xd = d + 1
            rolls = 0
            while xd < n and aux["limit_dn"][xd]:
                rolls += 1
                xd += 1
            if xd >= n:
                open_at_end += 1
                break
            px = float(o[xd])
            if pri == "tp1":
                legs.append((0.5, int(xd), px, "tp1", rolls))
                tp1_done = True
                d = xd
                continue
            legs.append((0.5 if tp1_done else 1.0, int(xd), px, pri, rolls))
            tag = pri
            last_exit = xd
            break
        if tag is None:
            continue                    # open at panel end, disclosed
        pnl_x1 = pnl_x2 = 0.0
        for frac, xd, px, _t, _r in legs:
            leg_x1 = px * (1.0 - cost_x1) / (entry * (1.0 + cost_x1)) - 1.0
            leg_x2 = px * (1.0 - cost_x2) / (entry * (1.0 + cost_x2)) - 1.0
            pnl_x1 += frac * leg_x1
            pnl_x2 += frac * leg_x2
        rounds.append({
            "entry_date": dates[e], "entry_px": round(entry, 6),
            "entry_idx": int(e), "exit_idx": int(last_exit),
            "exit_date": dates[last_exit],
            "legs": [[f, dates[x], round(p, 6), t, r]
                     for f, x, p, t, r in legs],
            "pnl_x1": round(pnl_x1, 8), "pnl_x2": round(pnl_x2, 8),
            "hold_days": int(last_exit - e),
            "seg_entry": str(aux["seg"][s]),
            "blocked_exit_rolls": int(sum(r for *_a, _t, r in legs)),
            "n_legs": len(legs),
        })
    stats = {"n_rounds": len(rounds), "blocked_entries": blocked_entries,
             "open_at_end": open_at_end, "skipped_signals": skipped_signals,
             "guard_isolated_signals": guard_isolated_signals}
    return rounds, stats


def pure_dca_face(m, aux, cost):
    """Naive all-months-no-skip DCA (prereg s3/s4 beat-pure-DCA face):
    every monthly signal day buys ONE unit at T+1 open (one-word limit-up
    voids that month = physical impossibility only; NO guard, naive face
    disclosed), held to panel end, sold at last close.
    Returns (mean unit net, n units)."""
    o, c = m["o"], m["c"]
    n = m["n"]
    nets = []
    for s in np.flatnonzero(aux["monthly"]):
        e = int(s) + 1
        if e >= n:
            continue
        if aux["limit_up"][e]:
            continue                      # blocked_entry, naive face
        nets.append(c[-1] * (1.0 - cost) / (o[e] * (1.0 + cost)) - 1.0)
    if not nets:
        return None, 0
    return float(np.mean(nets)), len(nets)


# ------------------------------------------------- windowed paired engine
def windowed_paired_vectorized(m, aux, grid, L, cin, cout):
    """Vectorized-across-starts window-paired engine (prereg s3 primary
    face). Every start s in [0, n-L] simulated independently, flat start.
    Step order per window position d (mirrors the brute-force reference
    EXACTLY -- byte-identity asserted in selftest):
      open  fills: committed full exits (pend_exit) and tp1 partials
             (pend_part) from the previous close; one-word limit-down rolls
             forward (blocked_exit, committed); pending entries from the
             previous day's signal fill at open; one-word limit-up = void
             (blocked_entry, month consumed, last_exit = fill pos);
      close triggers: in-position starts (no committed exit pending)
             evaluate the exit stack by frozen priority
             (trend_sl > hard_sl > tp2 > tp1);
      close signals: valid (guard-excluded) monthly signals fire a pending
             entry when flat and strictly after the last exit fill; every
             other valid monthly signal counts as skipped (open position /
             reentry window / window boundary);
      window end (d == L-1): after the open fills, everything still open
             force-closes at the LAST-BAR CLOSE (pending blocked exits same
             price; costs counted; frozen window-boundary measurement).
    Returns per-start arrays: n_units, sum_chain, sum_dca, skipped,
    blocked_e, blocked_x.
    """
    n = m["n"]
    S = n - L + 1
    if S <= 0:
        return None
    o, c, ma = m["o"], m["c"], m["ma200"]
    lim_up, lim_dn, iso = aux["limit_up"], aux["limit_dn"], aux["isolated"]
    monthly = aux["monthly"]
    P1, P2 = grid["P1"], grid["P2"]
    in_pos = np.zeros(S, dtype=bool)
    tp1_done = np.zeros(S, dtype=bool)
    pend_exit = np.zeros(S, dtype=bool)   # committed full exit awaiting fill
    pend_part = np.zeros(S, dtype=bool)   # committed tp1 partial awaiting fill
    pend_entry = np.zeros(S, dtype=bool)
    entry_px = np.zeros(S)
    last_exit = np.full(S, -1, dtype=np.int64)
    n_units = np.zeros(S, dtype=np.int64)
    sum_chain = np.zeros(S)
    sum_dca = np.zeros(S)
    partial_sum = np.zeros(S)
    skipped = np.zeros(S, dtype=np.int64)
    blocked_e = np.zeros(S, dtype=np.int64)
    blocked_x = np.zeros(S, dtype=np.int64)
    last_close = c[L - 1: L - 1 + S]      # window-end close per start
    with np.errstate(invalid="ignore"):
        for d in range(L):
            oo = o[d:d + S]
            cc = c[d:d + S]
            maa = ma[d:d + S]
            lu = lim_up[d:d + S]
            ld_ = lim_dn[d:d + S]
            sig = monthly[d:d + S]
            iso_s = iso[d:d + S]
            # --- open fills: committed exits ----------------------------
            can_fill = ~ld_
            fill = pend_exit & can_fill
            blocked_x += (pend_exit & ld_)
            if fill.any():
                px = oo[fill]
                frac = np.where(tp1_done[fill], 0.5, 1.0)
                leg = px * (1.0 - cout) / (entry_px[fill] * (1.0 + cin)) - 1.0
                unit = partial_sum[fill] + frac * leg
                sum_chain[fill] += unit
                n_units[fill] += 1
                in_pos[fill] = False
                pend_exit[fill] = False
                partial_sum[fill] = 0.0
                if d < L - 1:
                    last_exit[fill] = d
            fpart = pend_part & can_fill
            blocked_x += (pend_part & ld_)
            if fpart.any():
                ppx = oo[fpart]
                legp = ppx * (1.0 - cout) / (entry_px[fpart] * (1.0 + cin)) - 1.0
                partial_sum[fpart] += 0.5 * legp
                tp1_done[fpart] = True
                pend_part[fpart] = False
            # --- open fills: pending entries ----------------------------
            fent = pend_entry & ~lu
            void = pend_entry & lu
            blocked_e += void
            if void.any() and d < L - 1:
                last_exit[void] = d       # BP1 mirror: month consumed
            if fent.any():
                entry_px[fent] = oo[fent]
                in_pos[fent] = True
                tp1_done[fent] = False
                partial_sum[fent] = 0.0
                dleg = last_close[fent] * (1.0 - cout) / \
                    (oo[fent] * (1.0 + cin)) - 1.0
                sum_dca[fent] += dleg
            pend_entry[pend_entry] = False
            if d < L - 1:
                # --- close triggers ------------------------------------
                hold = in_pos & ~pend_exit & ~pend_part
                if hold.any():
                    sub = np.flatnonzero(hold)
                    tr = np.isfinite(maa[sub]) & (cc[sub] < maa[sub])
                    hs = cc[sub] <= entry_px[sub] * HARD_SL_MULT
                    t2 = cc[sub] >= entry_px[sub] * (1.0 + P2)
                    t1 = (~tp1_done[sub]) & \
                        (cc[sub] >= entry_px[sub] * (1.0 + P1))
                    full = tr | hs | t2
                    pend_exit[sub[full]] = True
                    pend_part[sub[~full & t1]] = True
                # --- close signals --------------------------------------
                valid = sig & ~iso_s
                fire = valid & ~in_pos & (d > last_exit)
                skipped += (valid & ~fire).astype(np.int64)
                pend_entry[fire] = True
            else:
                # --- window end: force close at LAST-BAR CLOSE ---------
                open_now = in_pos
                if open_now.any():
                    pxl = cc[open_now]
                    frac = np.where(tp1_done[open_now], 0.5, 1.0)
                    leg = pxl * (1.0 - cout) / \
                        (entry_px[open_now] * (1.0 + cin)) - 1.0
                    unit = partial_sum[open_now] + frac * leg
                    sum_chain[open_now] += unit
                    n_units[open_now] += 1
                    in_pos[open_now] = False
                    partial_sum[open_now] = 0.0
                # valid signals on the last bar can never fill in-window
                skipped += (sig & ~iso_s).astype(np.int64)
    return {"n_units": n_units, "sum_chain": sum_chain, "sum_dca": sum_dca,
            "skipped": skipped, "blocked_e": blocked_e, "blocked_x": blocked_x}


def windowed_paired_bruteforce(m, aux, grid, L, cin, cout, starts):
    """Brute-force reference implementation (selftest oracle): plain scalar
    loops per start, semantics EXACTLY mirroring the vectorized engine.
    Returns dict start -> (n_units, sum_chain, sum_dca, skipped, blocked_e,
    blocked_x) with identical float arithmetic order."""
    o, c, ma = m["o"], m["c"], m["ma200"]
    n = m["n"]
    P1, P2 = grid["P1"], grid["P2"]
    lim_up, lim_dn, iso = aux["limit_up"], aux["limit_dn"], aux["isolated"]
    monthly = aux["monthly"]
    out = {}
    for s0 in starts:
        s0 = int(s0)
        if s0 + L > n:
            continue
        in_pos = False
        tp1_done = False
        pend_exit = False
        pend_part = False
        pend_entry = False
        entry = 0.0
        last_exit = -1
        n_units = 0
        sum_chain = 0.0
        sum_dca = 0.0
        partial = 0.0
        skipped = 0
        blocked_e = 0
        blocked_x = 0
        last_close = float(c[s0 + L - 1])
        for d in range(L):
            g = s0 + d
            oo = float(o[g]); cc = float(c[g]); maa = float(ma[g])
            lu = bool(lim_up[g]); ld_ = bool(lim_dn[g])
            sig = bool(monthly[g]); iso_d = bool(iso[g])
            # open fills: committed exits
            if pend_exit:
                if ld_:
                    blocked_x += 1
                else:
                    px = oo
                    frac = 0.5 if tp1_done else 1.0
                    leg = px * (1.0 - cout) / (entry * (1.0 + cin)) - 1.0
                    unit = partial + frac * leg
                    sum_chain += unit
                    n_units += 1
                    in_pos = False
                    pend_exit = False
                    partial = 0.0
                    if d < L - 1:
                        last_exit = d
            if pend_part:
                if ld_:
                    blocked_x += 1
                else:
                    ppx = oo
                    legp = ppx * (1.0 - cout) / (entry * (1.0 + cin)) - 1.0
                    partial += 0.5 * legp
                    tp1_done = True
                    pend_part = False
            # open fills: pending entries
            if pend_entry:
                if lu:
                    blocked_e += 1
                    if d < L - 1:
                        last_exit = d
                else:
                    entry = oo
                    in_pos = True
                    tp1_done = False
                    partial = 0.0
                    dleg = last_close * (1.0 - cout) / (oo * (1.0 + cin)) - 1.0
                    sum_dca += dleg
                pend_entry = False
            if d < L - 1:
                # close triggers
                if in_pos and not pend_exit and not pend_part:
                    pri = None
                    if np.isfinite(maa) and cc < maa:
                        pri = "trend_sl"
                    elif cc <= entry * HARD_SL_MULT:
                        pri = "hard_sl"
                    elif cc >= entry * (1.0 + P2):
                        pri = "tp2"
                    elif (not tp1_done) and cc >= entry * (1.0 + P1):
                        pri = "tp1"
                    if pri == "tp1":
                        pend_part = True
                    elif pri is not None:
                        pend_exit = True
                # close signals
                if sig and not iso_d:
                    if in_pos or d <= last_exit:
                        skipped += 1
                    else:
                        pend_entry = True
            else:
                # window end: force close at last-bar close
                if in_pos:
                    pxl = cc
                    frac = 0.5 if tp1_done else 1.0
                    leg = pxl * (1.0 - cout) / (entry * (1.0 + cin)) - 1.0
                    unit = partial + frac * leg
                    sum_chain += unit
                    n_units += 1
                    in_pos = False
                    partial = 0.0
                if sig and not iso_d:
                    skipped += 1
        out[s0] = (n_units, sum_chain, sum_dca, skipped, blocked_e, blocked_x)
    return out


def paired_rows_from_engine(res, L):
    """Qualified-window rows [start_idx, L, paired_diff] (n_units >= 2)."""
    if res is None:
        return np.zeros((0, 3))
    nu = res["n_units"]
    ok = nu >= 2
    if not ok.any():
        return np.zeros((0, 3))
    starts = np.flatnonzero(ok)
    mean_ch = res["sum_chain"][ok] / nu[ok]
    mean_dc = res["sum_dca"][ok] / nu[ok]
    paired = mean_ch - mean_dc
    return np.column_stack([starts.astype(np.float64),
                            np.full(len(starts), float(L)), paired])


def bootstrap_median_ci(vals, seed, cell_idx, n_boot=N_BOOT, chunk=BOOT_CHUNK):
    """Percentile bootstrap CI95 of the median (prereg s4 primary gate).
    rng = default_rng([seed, 1000+cell_idx]); resample WITH replacement,
    chunked to bound memory. Returns (median, ci_lo, ci_hi)."""
    vals = np.asarray(vals, dtype=np.float64)
    med = float(np.median(vals))
    rng = np.random.default_rng([int(seed), 1000 + int(cell_idx)])
    meds = []
    done = 0
    while done < n_boot:
        b = int(min(chunk, n_boot - done))
        draw = rng.choice(vals, size=(b, len(vals)), replace=True)
        meds.extend(np.median(draw, axis=1).tolist())
        done += b
    return med, float(np.percentile(meds, 2.5)), float(np.percentile(meds, 97.5))


# ------------------------------------------------------------------ shard
def burn_member(code, data_dir=None, seed=None):
    """One member shard: 3 cells x (full-panel chain + windowed paired
    engine x 3 L x 2 cost faces + K nulls) + pure-DCA + faces."""
    members = []
    if data_dir is None:
        for mc in MEMBERS:
            mm, e2 = load_member(mc)
            if mm is None:
                return None, f"universe leg refuses: {mc}: {e2}"
            members.append(mm)
        m = next(x for x in members if x["code"] == code)
    else:
        mm, e2 = load_member(code, data_dir=data_dir)
        if mm is None:
            return None, e2
        members = [mm]
        m = mm
    med_abs = BP1.universe_median_abs_r1(members)
    aux = member_aux(m, med_abs)
    mi = MEMBERS.index(code) if code in MEMBERS else 0
    eval_start = int(np.argmax(np.isfinite(m["ma200"])))
    cells = {}
    os.makedirs(WN_DIR, exist_ok=True)
    os.makedirs(SER_DIR, exist_ok=True)
    for gi, grid in enumerate(GRID):
        cell_idx = mi * 3 + gi
        name = f"{code}-TP{int(grid['P1']*100)}-{int(grid['P2']*100)}"
        rounds, stats = chain_rounds(m, aux, grid, COST_X1, COST_X2)
        # nulls: uniform trading-day pool (all days except last; naive face)
        pool_days = np.arange(0, m["n"] - 1, dtype=np.int64)
        n_x1, n_x2, ne_x1, ne_x2, n_eff = BP1.nulls_for_cell(
            m, aux, pool_days, stats["n_rounds"], cell_idx, seed, grid,
            COST_X1, COST_X2)
        p95_x1 = round(float(np.percentile(n_x1, 95)), 6) if n_x1 else None
        p95_x2 = round(float(np.percentile(n_x2, 95)), 6) if n_x2 else None
        ep95_x1 = round(float(np.percentile(ne_x1, 95)), 8) if ne_x1 else None
        ep95_x2 = round(float(np.percentile(ne_x2, 95)), 8) if ne_x2 else None
        # windowed paired engine, both faces, pooled rows -> npy
        win_meta = {}
        for face_key, cost in (("x2", COST_X2), ("x1", COST_X1)):
            rows = np.zeros((0, 3))
            per_L = {}
            for wname, W in WINDOWS.items():
                res = windowed_paired_vectorized(m, aux, grid, W, cost, cost)
                rr = paired_rows_from_engine(res, W)
                per_L[wname] = {
                    "n_starts": int(0 if res is None else len(res["n_units"])),
                    "n_qualified": int(len(rr)),
                    "skipped": int(0 if res is None else res["skipped"].sum()),
                    "blocked_entries": int(
                        0 if res is None else res["blocked_e"].sum()),
                    "blocked_exit_rolls": int(
                        0 if res is None else res["blocked_x"].sum()),
                }
                if len(rr):
                    rows = np.concatenate([rows, rr])
            np.save(os.path.join(WN_DIR, f"{code}_{cell_idx}_{face_key}.npy"),
                    rows.astype(np.float64), allow_pickle=False)
            win_meta[face_key] = per_L
        # series faces for G1'/DSR/descriptive (BP1 chain_daily machinery)
        ser_x1 = BP1.chain_daily(m, rounds, COST_X1, eval_start)
        ser_x2 = BP1.chain_daily(m, rounds, COST_X2, eval_start)
        np.save(os.path.join(SER_DIR, f"{code}_{cell_idx}_x1.npy"),
                ser_x1.astype(np.float64), allow_pickle=False)
        np.save(os.path.join(SER_DIR, f"{code}_{cell_idx}_x2.npy"),
                ser_x2.astype(np.float64), allow_pickle=False)
        with np.errstate(invalid="ignore"):
            pr = m["c"][1:] / m["c"][:-1] - 1.0
        passive = float(np.nansum(pr[eval_start:]))
        w_x1 = sum(1 for r in rounds if r["pnl_x1"] > 0) / max(len(rounds), 1)
        w_x2 = sum(1 for r in rounds if r["pnl_x2"] > 0) / max(len(rounds), 1)
        e_x1 = float(np.mean([r["pnl_x1"] for r in rounds])) if rounds else None
        e_x2 = float(np.mean([r["pnl_x2"] for r in rounds])) if rounds else None
        cells[name] = {
            "cell_idx": cell_idx,
            "grid": {"P1": grid["P1"], "P2": grid["P2"]},
            **stats,
            "win_rate_x1": round(w_x1, 6), "win_rate_x2": round(w_x2, 6),
            "e_pnl_x1": (round(e_x1, 8) if e_x1 is not None else None),
            "e_pnl_x2": (round(e_x2, 8) if e_x2 is not None else None),
            "nulls": {"n_draws_effective": len(n_eff),
                      "win_p95_x1": p95_x1, "win_p95_x2": p95_x2,
                      "e_p95_x1": ep95_x1, "e_p95_x2": ep95_x2,
                      "mean_eff_rounds": (round(float(np.mean(n_eff)), 3)
                                          if n_eff else None)},
            "windows_meta": win_meta,
            "rounds": rounds,
            "passive_cum_full": round(passive, 8),
            "eval_start_idx": eval_start,
            "eval_start_date": m["dates"][eval_start],
        }
        print(f"  cell {name}: rounds={stats['n_rounds']} "
              f"skipped={stats['skipped_signals']} "
              f"wr_x2={w_x2:.4f} null_p95_x2={p95_x2}")
    pure_x1, pure_n1 = pure_dca_face(m, aux, COST_X1)
    pure_x2, pure_n2 = pure_dca_face(m, aux, COST_X2)
    with np.errstate(invalid="ignore"):
        crisis = int(np.sum(np.abs(m["r1"]) >
                            (BP1.GUARD_THR_20CM if code in TIER_20CM
                             else BP1.GUARD_THR)))
    shard = {
        "grammar_sha16": GRAMMAR_SHA16, "member": code,
        "evidence_cutoff": EVIDENCE_CUTOFF, "seed": int(seed),
        "face": m["face"], "tier": aux["tier"],
        "isolated_days": int(aux["isolated"].sum()),
        "crisis_days_gt_threshold": crisis,
        "monthly_signals": int(aux["monthly"].sum()),
        "seg_census": {s: int((aux["seg"] == s).sum())
                       for s in ("bear", "chop", "bull", "na")},
        "pure_dca": {"x1": (round(pure_x1, 8) if pure_x1 is not None else None),
                     "x2": (round(pure_x2, 8) if pure_x2 is not None else None),
                     "n_units": pure_n1},
        "cells": cells,
    }
    return shard, None


# ------------------------------------------------------------------ finalize
def _regime_states_by_date():
    """T-74 L2 route states via the imported frozen deep-replay layer
    (descriptive only, never a switch gate). Key-format repair over the
    BP1 inherited face: regime_deep_replay v3 state keys carry a
    ' 00:00:00' time component ('2005-04-08 00:00:00') while round/window
    dates are date-only -- the BP1 join silently returned all-'na'
    (found at BP2 real-data first fire r459; disclosure-only face, no gate
    consumed it; normalized to date-only keys here)."""
    raw = BP1._regime_states_by_date()
    if "__error__" in raw:
        return raw
    return {str(k)[:10]: v for k, v in raw.items()}


def cmd_finalize(args):
    if not os.path.exists(OUT_DIR):
        return gate_refuse("no shard dir -- burn shards first")
    shards = []
    for code in MEMBERS:
        p = os.path.join(OUT_DIR, f"bp2_shard_{code}.json")
        if not os.path.exists(p):
            return gate_refuse(f"shard absent: {code}")
        sh = json.load(open(p, encoding="utf-8"))
        if sh.get("grammar_sha16") != GRAMMAR_SHA16:
            return gate_refuse(f"shard grammar mismatch: {code} "
                              f"({sh.get('grammar_sha16')})")
        if sh.get("evidence_cutoff") != EVIDENCE_CUTOFF:
            return gate_refuse(f"shard cutoff drift: {code}")
        shards.append(sh)
    n_cells_total = sum(len(s["cells"]) for s in shards)
    if n_cells_total != BATCH_CELLS:
        return gate_refuse(f"shard census drift: {n_cells_total} != "
                          f"{BATCH_CELLS}")
    if os.path.exists(OUT_JSON):
        j = json.load(open(OUT_JSON, encoding="utf-8"))
        _tl = j.get("trials_ledger") or (j.get("science_gates")
                                         or {}).get("ledger")
        if _tl:
            print("idempotent fast path: bp2_grid.json already finalized "
                  "(ledger block present); ETF_OPS_BP2_REFINALIZE=1 = only redo")
            if os.environ.get("ETF_OPS_BP2_REFINALIZE") != "1":
                return 0
    prev_total = None
    if os.path.exists(OUT_JSON):
        try:
            prev_total = int(json.load(open(OUT_JSON, encoding="utf-8"))
                             ["trials_ledger"]["prev_total"])
        except Exception:
            prev_total = None
    head_base = (prev_total if prev_total is not None
                 else int(SG.ledger_head(SG.RESULTS_DIR)["total"]))
    seed = int(SG.SEED_REGISTRY[SEED_KEY])
    # members cache + universe median (single load pass)
    mcache = {}
    for c in MEMBERS:
        mm, e = load_member(c)
        if mm is None:
            return gate_refuse(f"member reload refuses: {c}: {e}")
        mcache[c] = mm
    med_abs = BP1.universe_median_abs_r1([mcache[c] for c in MEMBERS])
    auxcache = {c: member_aux(mcache[c], med_abs) for c in MEMBERS}
    # D6 registered sleeve returns (ew6 canon, live.paper anchor path)
    member_rets = None
    try:
        import ew6_portfolio as E
        from live.paper import load_core
        if E.PRICES_FULL is None:
            E.PRICES_FULL = load_core()
        member_rets = {}
        for tid in BP1.SG_REG6:
            r = E.member_run(tid)
            eq = pd.Series(r["eq"], index=pd.to_datetime(r["dates"]))
            member_rets[tid] = eq.pct_change().dropna()
    except Exception as exc:
        print(f"D6-WARN: registered sleeve face unavailable: {repr(exc)[:160]}")
    regime_states = _regime_states_by_date()
    # ---- per-cell faces --------------------------------------------------
    gates, cells_out, d6_cells = {}, {}, {}
    regime_face = {"source": "regime_deep_replay v3 (L2 route map "
                   "YELLOW->CHOP) + T-89 segment at window start, "
                   "descriptive only", "per_cell": {}}
    descr = {"per_cell": {}}
    series_x2, series_x1 = {}, {}
    win_summaries = {}
    for sh in shards:
        code = sh["member"]
        m = mcache[code]
        aux = auxcache[code]
        for name, cell in sh["cells"].items():
            ci = cell["cell_idx"]
            ser = np.load(os.path.join(SER_DIR, f"{code}_{ci}_x2.npy"))
            ser1 = np.load(os.path.join(SER_DIR, f"{code}_{ci}_x1.npy"))
            series_x2[name] = ser
            series_x1[name] = ser1
            # primary gate: pooled qualified windows (both faces)
            pg = {}
            for face_key in ("x2", "x1"):
                rows = np.load(os.path.join(WN_DIR, f"{code}_{ci}_{face_key}.npy"))
                if len(rows) < 2:
                    pg[face_key] = {"n_windows": int(len(rows)),
                                    "median_paired": None, "ci95": None,
                                    "pass": False,
                                    "note": "vacuous paired set (<2 windows)"}
                    continue
                vals = rows[:, 2]
                med, lo, hi = bootstrap_median_ci(vals, seed, ci)
                pass_v = bool(med > 0.0 and (lo > 0.0 or hi < 0.0))
                pg[face_key] = {"n_windows": int(len(rows)),
                                "median_paired": round(med, 8),
                                "ci95": [round(lo, 8), round(hi, 8)],
                                "pass": pass_v}
            # G1' v2 on chain daily x2 series
            g1 = None
            if len(ser) >= 20 and float(np.std(ser)) > 0:
                g1 = SG.g1_prime_v2(BP1._sharpe(ser), list(map(float, ser)),
                                   batch_cells=BATCH_CELLS, pool="core48",
                                   n_trades=cell["n_rounds"],
                                   n_entries=cell["n_rounds"],
                                   n_eff_override=head_base + BATCH_CELLS)
            dsr = None
            if g1 is not None:
                dsr = SG.deflated_sharpe_ratio(list(map(float, ser)),
                                               n_trials=g1["skill_line"]["n_eff"])
            gates[name] = {"primary_gate_x2": pg["x2"],
                           "primary_gate_x1": pg["x1"],
                           "g1_prime_v2": g1, "dsr": dsr}
            win_summaries[name] = {
                "member": code, "cell_idx": ci, "grid": cell["grid"],
                "primary_x2": pg["x2"], "primary_x1": pg["x1"],
                "windows_meta": cell["windows_meta"],
                "skipped_signals": cell["skipped_signals"],
                "guard_isolated_signals": cell["guard_isolated_signals"],
                "n_rounds": cell["n_rounds"],
                "blocked_entries": cell["blocked_entries"],
                "blocked_exit_rolls": int(sum(
                    r["blocked_exit_rolls"] for r in cell["rounds"])),
                "open_at_end": cell["open_at_end"],
            }
            # regime/segment stratification of paired_diff (x2 face)
            rows = np.load(os.path.join(WN_DIR, f"{code}_{ci}_x2.npy"))
            per_state, per_seg = {}, {}
            for s_i, L_i, pd_i in rows:
                d0 = m["dates"][int(s_i)]
                st = (regime_states.get(d0)
                      if "__error__" not in regime_states else None) or "na"
                per_state.setdefault(st, []).append(pd_i)
                per_seg.setdefault(str(aux["seg"][int(s_i)]), []).append(pd_i)
            regime_face["per_cell"][name] = {
                "by_route_state": {k: {"n": len(v), "median_paired": round(
                    float(np.median(v)), 8)}
                    for k, v in sorted(per_state.items())},
                "by_t89_segment": {k: {"n": len(v), "median_paired": round(
                    float(np.median(v)), 8)}
                    for k, v in sorted(per_seg.items())}}
            # descriptive clauses (x2 judged + x1 parallel)
            dates = m["dates"][cell["eval_start_idx"]:]
            yearly = BP1._yearly(ser, dates)
            cum = np.cumsum(ser)
            run_max = np.maximum.accumulate(cum)
            dd = float(np.min(cum - run_max)) if len(cum) else 0.0
            oos_mask = np.array([d >= OOS_FROM for d in dates], dtype=bool)
            oos_ann = (float(np.mean(ser[oos_mask]) * PBP)
                       if oos_mask.any() and float(np.std(ser)) > 0 else 0.0)
            oos_sh = (float(np.mean(ser[oos_mask]) /
                            np.std(ser[oos_mask], ddof=1) * np.sqrt(PBP))
                      if oos_mask.any()
                      and float(np.std(ser[oos_mask])) > 0 else 0.0)
            chain_cum = float(np.sum(ser))
            chain_units = [r["pnl_x2"] for r in cell["rounds"]]
            pure_x2 = sh["pure_dca"]["x2"]
            beat_pure = None
            if pure_x2 is not None and chain_units:
                beat_pure = bool(float(np.mean(chain_units)) > pure_x2)
            descr["per_cell"][name] = {
                "ann_x2": round(float(np.mean(ser) * PBP /
                                       (np.std(ser, ddof=1) or 1.0))
                                * (1 if float(np.std(ser)) > 0 else 0), 6),
                "oos_2025_ann_x2": round(oos_ann, 6),
                "oos_2025_sharpe_x2": round(oos_sh, 6),
                "maxdd_x2": round(dd, 6),
                "yearly_x2": yearly,
                "crash_year": bool(any(v <= -0.35 for v in yearly.values())),
                "chain_cum_x2": round(chain_cum, 6),
                "beat_passive_full_x2": bool(chain_cum > cell["passive_cum_full"]),
                "beat_margin_x2": round(chain_cum - cell["passive_cum_full"], 6),
                "chain_unit_mean_x2": (round(float(np.mean(chain_units)), 8)
                                      if chain_units else None),
                "pure_dca_unit_mean_x2": pure_x2,
                "beat_pure_dca_x2": beat_pure,
            }
            cells_out[name] = {
                "member": code, "cell_idx": ci, "grid": cell["grid"],
                "n_rounds": cell["n_rounds"],
                "skipped_signals": cell["skipped_signals"],
                "guard_isolated_signals": cell["guard_isolated_signals"],
                "blocked_entries": cell["blocked_entries"],
                "open_at_end": cell["open_at_end"],
                "win_rate_x1": cell["win_rate_x1"],
                "win_rate_x2": cell["win_rate_x2"],
                "e_pnl_x1": cell["e_pnl_x1"], "e_pnl_x2": cell["e_pnl_x2"],
                "nulls": cell["nulls"], "sharpe_x2": round(BP1._sharpe(ser), 4),
                "passive_cum_full": cell["passive_cum_full"],
                "windows_meta": cell["windows_meta"],
            }
            # virtual timepoints {6m,12m,24m} x {x1,x2} vs same-window buy-hold
            with np.errstate(invalid="ignore"):
                prr = m["c"][1:] / m["c"][:-1] - 1.0
            es = cell["eval_start_idx"]
            pas_full = np.concatenate(
                [np.zeros(1), np.nan_to_num(prr[es:])])[:len(ser)]
            vt = {}
            for wname, W in WINDOWS.items():
                for face_key, serry in (("x2", ser), ("x1", ser1)):
                    nn = len(serry)
                    if nn <= W:
                        vt[f"{wname}_{face_key}"] = {
                            "n_starts": 0, "beat_rate": None,
                            "note": "window longer than series (588000 face "
                                    "narrows honestly)"}
                        continue
                    ch = np.cumsum(serry)
                    pa = np.cumsum(pas_full)
                    starts = np.arange(0, nn - W)
                    beats = int(np.sum(ch[starts + W] - ch[starts]
                                       > pa[starts + W] - pa[starts]))
                    vt[f"{wname}_{face_key}"] = {
                        "n_starts": int(len(starts)),
                        "beat_rate": round(beats / len(starts), 4)}
            cells_out[name]["virtual_timepoints"] = vt
    # ---- family PBO (15-cell x2 matrix, common-tail alignment) ------------
    L = min(len(v) for v in series_x2.values())
    mat = pd.DataFrame({k: v[-L:] for k, v in series_x2.items()})
    pbo = None
    try:
        from screening.pbo import cscv_pbo
        pbo = cscv_pbo(mat)
        pbo = {"pbo": round(float(pbo["pbo"]), 4),
               "source": "screening.pbo cscv_pbo CSCV-8, 15-cell x2 matrix, "
                         f"common-tail alignment n={L} (588000 warmup face)",
               "n_aligned": int(L)}
    except Exception as exc:
        pbo = {"pbo": None, "error": repr(exc)[:200]}
    # ---- D6 face -----------------------------------------------------------
    if member_rets is not None:
        for name, serry in series_x2.items():
            code = cells_out[name]["member"]
            es = None
            for s in shards:
                if name in s["cells"]:
                    es = s["cells"][name]["eval_start_idx"]
                    break
            m2 = mcache[code]
            dates_d6 = pd.to_datetime(m2["dates"][es:])
            s_ = pd.Series(serry, index=dates_d6)
            per = {}
            best = None
            for tid, mr in member_rets.items():
                j = pd.concat([s_, mr], axis=1, join="inner").dropna()
                if len(j) < 20:
                    per[tid] = {"corr": None, "overlap_days": int(len(j))}
                    continue
                v = float(np.corrcoef(j.iloc[:, 0], j.iloc[:, 1])[0, 1])
                per[tid] = {"corr": round(v, 4), "overlap_days": int(len(j))}
                if best is None or abs(v) > abs(per[best]["corr"]):
                    best = tid
            mx = abs(per[best]["corr"]) if best else None
            d6_cells[name] = {
                "per_member": per,
                "max_abs_corr": (round(mx, 4) if mx is not None else None),
                "argmax_member": best,
                "reject": bool(mx is not None and mx >= D6_REJECT)}
    # ---- G2 + combined registration ---------------------------------------
    for name, g in gates.items():
        g1 = g.get("g1_prime_v2")
        dsr = g.get("dsr")
        g2 = None
        if g1 is not None and dsr is not None and pbo["pbo"] is not None:
            g2 = SG.g2_registration_v2(g1["pass_v2"], dsr, float(pbo["pbo"]))
        g["g2"] = g2
        g["combined_registration"] = bool(
            g["primary_gate_x2"]["pass"] and g2 is not None
            and g2.get("eligible_v2"))
    ledger = SG.append_ledger(BATCH_NAME, batch_trials=BATCH_CELLS,
                              file_name=OUT_JSON,
                              evidence_cutoff=EVIDENCE_CUTOFF,
                              prev_total=head_base)
    n_primary = sum(1 for g in gates.values() if g["primary_gate_x2"]["pass"])
    n_comb = sum(1 for g in gates.values() if g["combined_registration"])
    product = {
        "batch": BATCH_NAME, "grammar_sha16": GRAMMAR_SHA16,
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "science_gates": {"cutoff_meta": {"evidence_cutoff": EVIDENCE_CUTOFF},
                          "ledger": ledger},
        "members": MEMBERS, "anchors": {c: ANCHORS[c] for c in MEMBERS},
        "cost_faces": {"x1_side_bp": round(COST_X1 * 1e4, 3),
                       "x2_side_bp": round(COST_X2 * 1e4, 3),
                       "judged_face": "x2"},
        "primary_count": {"pass": n_primary, "of": BATCH_CELLS},
        "combined_registration_count": n_comb,
        "cells": cells_out, "gates": gates, "pbo": pbo,
        "d6": {"reject_line": D6_REJECT, "members": list(BP1.SG_REG6),
               "cells": d6_cells} if member_rets is not None else
              {"status": "unavailable", "reject_line": D6_REJECT},
        "regime_face": regime_face, "descriptive": descr,
        "blocked_accounting": {
            sh["member"]: {
                "blocked_entries": sum(c["blocked_entries"]
                                       for c in sh["cells"].values()),
                "open_at_end": sum(c["open_at_end"]
                                   for c in sh["cells"].values()),
                "isolated_days": sh["isolated_days"],
                "crisis_days_gt_threshold": sh["crisis_days_gt_threshold"],
                "guard_isolated_signals": sum(
                    c["guard_isolated_signals"] for c in sh["cells"].values()),
                "monthly_signals": sh["monthly_signals"],
                "pure_dca": sh["pure_dca"],
            } for sh in shards},
        "nulls_ref": OUT_NULLS,
        "windows_ref": OUT_WINDOWS,
    }
    BP1._atomic_json(OUT_JSON, product)
    nulls_out = {"batch": BATCH_NAME, "evidence_cutoff": EVIDENCE_CUTOFF,
                 "grammar_sha16": GRAMMAR_SHA16,
                 "cells": {name: c["nulls"] for name, c in cells_out.items()}}
    BP1._atomic_json(OUT_NULLS, nulls_out)
    BP1._atomic_json(OUT_WINDOWS, {"batch": BATCH_NAME,
                                   "evidence_cutoff": EVIDENCE_CUTOFF,
                                   "grammar_sha16": GRAMMAR_SHA16,
                                   "cells": win_summaries})
    print(f"FINALIZE OK: 15 cells; primary pass={n_primary}/15; "
          f"combined registration={n_comb}; ledger total={ledger.get('total')}")
    return 0


# ------------------------------------------------------------------ cli cmds
def cmd_run(args):
    ram = sorted(BP1._free_ram_gb() for _ in range(3))
    if ram[0] < RAM_FLOOR_GB:
        print(f"RAM-FLOOR(exit3): three-sample min {ram[0]:.2f}GB "
              f"< {RAM_FLOOR_GB}GB (r354 family, light-batch calibration)")
        return 3
    seed = int(SG.SEED_REGISTRY[SEED_KEY])
    os.makedirs(WN_DIR, exist_ok=True)
    os.makedirs(SER_DIR, exist_ok=True)
    codes = MEMBERS if args.shard == "all" else [args.shard]
    for code in codes:
        if code not in MEMBERS:
            return gate_refuse(f"unknown shard member: {code}")
        p = os.path.join(OUT_DIR, f"bp2_shard_{code}.json")
        if os.path.exists(p) and not args.force:
            j = json.load(open(p, encoding="utf-8"))
            if j.get("grammar_sha16") == GRAMMAR_SHA16:
                print(f"shard {code}: idempotent skip (grammar match); "
                      f"--force to redo")
                continue
            return gate_refuse(f"shard {code} grammar mismatch -- manual "
                               f"adjudication required")
        shard, err = burn_member(code, seed=seed)
        if shard is None:
            return gate_refuse(f"burn {code}: {err}")
        BP1._atomic_json(p, shard)
        rows = ["member,cell,entry_date,entry_px,exit_date,pnl_x1,pnl_x2,"
                "win_x1,win_x2,hold_days,n_legs,seg_entry,blocked_exit_rolls"]
        for name, cell in shard["cells"].items():
            for r in cell["rounds"]:
                rows.append(",".join([
                    code, name, r["entry_date"], str(r["entry_px"]),
                    r["exit_date"], str(r["pnl_x1"]), str(r["pnl_x2"]),
                    str(int(r["pnl_x1"] > 0)), str(int(r["pnl_x2"] > 0)),
                    str(r["hold_days"]), str(r["n_legs"]), r["seg_entry"],
                    str(r["blocked_exit_rolls"])]))
        BP1._atomic_text(os.path.join(OUT_DIR, f"bp2_rounds_{code}.csv"),
                         "\n".join(rows) + "\n")
        print(f"shard {code}: burnt -> bp2_shard_{code}.json + rounds csv "
              f"({sum(c['n_rounds'] for c in shard['cells'].values())} rounds)")
    return 0


def cmd_status(args):
    print(f"grammar_sha16={GRAMMAR_SHA16}")
    for code in MEMBERS:
        p = os.path.join(OUT_DIR, f"bp2_shard_{code}.json")
        if os.path.exists(p):
            j = json.load(open(p, encoding="utf-8"))
            n = sum(c["n_rounds"] for c in j["cells"].values())
            print(f"  {code}: shard OK (grammar "
                  f"{'match' if j['grammar_sha16'] == GRAMMAR_SHA16 else 'MISMATCH'}) "
                  f"rounds={n} seed={j['seed']}")
        else:
            print(f"  {code}: shard ABSENT")
    print(f"  finalize: {'DONE' if os.path.exists(OUT_JSON) else 'pending'}")
    return 0


# ------------------------------------------------------------------ selftest
def cmd_selftest(args):
    """Hermetic offline selftest: synthetic fixtures only, zero network,
    zero repo data loads, deterministic double-run byte-identical."""
    import shutil
    import subprocess
    tmp = tempfile.mkdtemp(prefix="bp2_st_")
    fails = []
    t = lambda ok, msg: (None if ok else fails.append(msg))

    n = 420                                   # >= MA200 warmup + windows
    rng = np.random.default_rng(11)
    base = np.linspace(2.0, 3.2, n) + np.sin(np.arange(n) / 7.0) * 0.06
    c = base.copy()
    o = c * (1 + rng.normal(0, 0.004, n))
    h = np.maximum(o, c) * 1.005
    l = np.minimum(o, c) * 0.995
    for dd in (260, 300):                     # dips, trend intact
        c[dd] = c[dd - 1] * 0.95
        o[dd] = c[dd]; h[dd] = c[dd] * 1.002; l[dd] = c[dd] * 0.998
    dates = pd.bdate_range("2023-01-02", periods=n).strftime("%Y-%m-%d")
    anchors_st = {"510050": {"path": "daily/st.csv", "first": dates[0],
                            "rows": n}}
    def write_fixture(d, arr_c=None, dts=None, arr_o=None, arr_h=None,
                      arr_l=None):
        os.makedirs(os.path.join(d, "daily"), exist_ok=True)
        df = pd.DataFrame({"date": dts or dates,
                           "open": arr_o if arr_o is not None else o,
                           "high": arr_h if arr_h is not None else h,
                           "low": arr_l if arr_l is not None else l,
                           "close": arr_c if arr_c is not None else c,
                           "volume": 1e6, "amount": 1e8})
        df.to_csv(os.path.join(d, "daily", "st.csv"), index=False)

    # [S1] anchor gates (BP2 anchor path)
    write_fixture(tmp)
    bad = dict(anchors_st)
    bad["510050"] = dict(anchors_st["510050"], rows=n - 1)
    m, err = load_member("510050", data_dir=tmp, anchors=bad,
                         cutoff=dates[-1])
    t(m is None and "row census drift" in err, f"S1a row-census refuse: {err}")
    m, err = load_member("510050", data_dir=tmp, anchors=anchors_st,
                        cutoff=dates[-1])
    t(m is not None, f"S1b clean load: {err}")
    c_nan = c.copy(); c_nan[50] = np.nan
    write_fixture(tmp, arr_c=c_nan)
    m2, err = load_member("510050", data_dir=tmp, anchors=anchors_st,
                         cutoff=dates[-1])
    t(m2 is None and "NaN" in err, f"S1c NaN refuse: {err}")
    write_fixture(tmp)

    # [S2] monthly mask: first trading day of each Gregorian month
    mm = monthly_signal_mask(m)
    ym_first = {}
    for i, d in enumerate(dates):
        ym_first.setdefault(d[:7], i)
    t(all(mm[i] for i in ym_first.values()), "S2a first-td-of-month set")
    t(int(mm.sum()) == len(ym_first),
      f"S2b mask count == months ({int(mm.sum())} vs {len(ym_first)})")
    t(bool(mm[0]), "S2c panel first bar is a monthly signal")

    # [S3] full-panel chain rounds on fixture
    med_abs = BP1.universe_median_abs_r1([m])
    aux = member_aux(m, med_abs)
    grid = GRID[0]
    rounds, stats = chain_rounds(m, aux, grid, COST_X1, COST_X2)
    t(stats["n_rounds"] >= 3, f"S3a rounds on fixture: {stats}")
    if rounds:
        r0 = rounds[0]
        t(r0["pnl_x2"] < r0["pnl_x1"], "S3b x2 stress face strictly costlier")
        t(r0["hold_days"] >= 1 and r0["n_legs"] >= 1, "S3c round shape")
    t(stats["skipped_signals"] + stats["n_rounds"] +
      stats["blocked_entries"] <= int(mm.sum()) + 1,
      f"S3d signal conservation: {stats}")

    # [S4] TP1+TP2 two-leg path engineered (wider grid on fixture)
    rounds_t, _ = chain_rounds(m, aux, GRID[2], COST_X1, COST_X2)
    t(any(len(r["legs"]) >= 2 for r in rounds_t),
      f"S4a tp1+tp2 two-leg path: {[r['n_legs'] for r in rounds_t[:5]]}")

    # [S5] hard SL engineered: crash region after first entry
    c_sl = c.copy()
    e_first = rounds[0]["entry_idx"]
    for d in range(e_first, min(e_first + 30, n)):
        c_sl[d] = c_sl[e_first] * 0.90
    write_fixture(tmp, arr_c=c_sl)
    m_sl, _ = load_member("510050", data_dir=tmp, anchors=anchors_st,
                         cutoff=dates[-1])
    aux_sl = member_aux(m_sl, med_abs)
    rounds_sl, _ = chain_rounds(m_sl, aux_sl, grid, COST_X1, COST_X2)
    t(any(lg[3] == "hard_sl" for r in rounds_sl for lg in r["legs"]),
      "S5a hard_sl path fired")
    t(all(r["pnl_x2"] < 0 for r in rounds_sl
          if any(lg[3] == "hard_sl" for lg in r["legs"])),
      "S5b hard_sl losing round")
    write_fixture(tmp)

    # [S6] trend SL engineered: break below MA200 mid-panel (post-warmup)
    c_tr = c.copy()
    ma_run = pd.Series(c_tr).rolling(200, min_periods=200).mean().to_numpy()
    e_eng = 250
    for d in range(e_eng, min(e_eng + 60, n)):
        if np.isfinite(ma_run[d]):
            c_tr[d] = min(c_tr[d], float(ma_run[d]) * 0.97)
    write_fixture(tmp, arr_c=c_tr)
    m_tr, _ = load_member("510050", data_dir=tmp, anchors=anchors_st,
                         cutoff=dates[-1])
    aux_tr = member_aux(m_tr, med_abs)
    rounds_tr, _ = chain_rounds(m_tr, aux_tr, grid, COST_X1, COST_X2)
    t(any(lg[3] == "trend_sl" for r in rounds_tr for lg in r["legs"]),
      "S6a trend_sl path fired")
    write_fixture(tmp)

    # [S7] blocked_entry: one-word limit-up on an entry fill day
    m7, _ = load_member("510050", data_dir=tmp, anchors=anchors_st,
                        cutoff=dates[-1])
    aux7 = member_aux(m7, med_abs)
    sig_first = int(np.flatnonzero(aux7["monthly"])[0])
    e7 = sig_first + 1
    o7 = o.copy(); h7 = h.copy(); l7 = l.copy()
    o7[e7] = m7["pc"][e7] * 1.100; h7[e7] = o7[e7]; l7[e7] = o7[e7]
    c7 = c.copy(); c7[e7] = o7[e7]
    write_fixture(tmp, arr_c=c7, arr_o=o7, arr_h=h7, arr_l=l7)
    m8, _ = load_member("510050", data_dir=tmp, anchors=anchors_st,
                        cutoff=dates[-1])
    aux8 = member_aux(m8, med_abs)
    rounds8, st8 = chain_rounds(m8, aux8, grid, COST_X1, COST_X2)
    t(st8["blocked_entries"] >= 1, f"S7a blocked_entry counted: {st8}")
    t(all(r["entry_idx"] != e7 for r in rounds8),
      "S7b blocked entry day never fills a round")
    write_fixture(tmp)

    # [S8] blocked_exit roll: one-word limit-down on an exit fill day
    m9, _ = load_member("510050", data_dir=tmp, anchors=anchors_st,
                        cutoff=dates[-1])
    aux9 = member_aux(m9, med_abs)
    rounds9, _ = chain_rounds(m9, aux9, GRID[2], COST_X1, COST_X2)
    if rounds9:
        ex_d = rounds9[0]["exit_idx"]
        o9 = o.copy(); h9 = h.copy(); l9 = l.copy(); c9 = c.copy()
        pcx = m9["pc"][ex_d]
        o9[ex_d] = pcx * 0.900; h9[ex_d] = o9[ex_d]; l9[ex_d] = o9[ex_d]
        c9[ex_d] = o9[ex_d]
        write_fixture(tmp, arr_c=c9, arr_o=o9, arr_h=h9, arr_l=l9)
        m10, _ = load_member("510050", data_dir=tmp, anchors=anchors_st,
                            cutoff=dates[-1])
        aux10 = member_aux(m10, med_abs)
        rounds10, _ = chain_rounds(m10, aux10, GRID[2], COST_X1, COST_X2)
        t(any(r["blocked_exit_rolls"] >= 1 for r in rounds10),
          f"S8a blocked_exit roll: "
          f"{[r['blocked_exit_rolls'] for r in rounds10[:4]]}")
    write_fixture(tmp)

    # [S9] vectorized vs brute-force byte-identity (full start sets)
    m11, _ = load_member("510050", data_dir=tmp, anchors=anchors_st,
                         cutoff=dates[-1])
    aux11 = member_aux(m11, med_abs)
    for L in (126, 252):
        res = windowed_paired_vectorized(m11, aux11, GRID[0], L, COST_X2,
                                         COST_X2)
        S = m11["n"] - L + 1
        starts = np.arange(S)
        ref = windowed_paired_bruteforce(m11, aux11, GRID[0], L, COST_X2,
                                         COST_X2, starts)
        ok = True
        for s0 in starts:
            rn, rc, rd, rs, rbe, rbx = ref[int(s0)]
            if (int(res["n_units"][s0]) != rn
                    or float(res["sum_chain"][s0]) != rc
                    or float(res["sum_dca"][s0]) != rd
                    or int(res["skipped"][s0]) != rs
                    or int(res["blocked_e"][s0]) != rbe
                    or int(res["blocked_x"][s0]) != rbx):
                ok = False
                fails.append(f"S9 byte-identity break L={L} s={s0}: "
                             f"vec=({res['n_units'][s0]},{res['sum_chain'][s0]},"
                             f"{res['sum_dca'][s0]},{res['skipped'][s0]},"
                             f"{res['blocked_e'][s0]},{res['blocked_x'][s0]}) "
                             f"ref=({rn},{rc},{rd},{rs},{rbe},{rbx})")
                break
        t(ok, f"S9 identity L={L} over {len(starts)} windows "
              f"(>=50 requirement)")

    # [S10] short-window forced-close: units complete at window end
    res10 = windowed_paired_vectorized(m11, aux11, GRID[0], 60, COST_X1,
                                       COST_X1)
    t(res10 is not None and int(res10["n_units"].sum()) >= 1,
      f"S10a short-window units complete at window end "
      f"(sum units={int(res10['n_units'].sum())})")

    # [S11] primary gate bootstrap determinism + stream separation
    vals = np.concatenate([np.linspace(-0.02, 0.05, 60),
                           np.linspace(0.01, 0.03, 40)])
    a1 = bootstrap_median_ci(vals, 20294100, 0)
    a2 = bootstrap_median_ci(vals, 20294100, 0)
    a3 = bootstrap_median_ci(vals, 20294100, 1)
    t(a1 == a2, "S11a bootstrap determinism (same seed/cell)")
    t(a1[0] > 0 and a1[1] > 0,
      f"S11b positive pool -> median>0 + CI excludes 0: {a1}")
    r0 = np.random.default_rng([20294100, 1000])
    r1 = np.random.default_rng([20294100, 1001])
    t(not np.array_equal(r0.integers(0, 10 ** 6, size=8),
                         r1.integers(0, 10 ** 6, size=8)),
      "S11c cell_idx streams differ (raw stream face; CI face may "
      "coincide on small discrete pools -- rng separation is the law)")

    # [S12] pure-DCA face (naive all-months, T+1 opens)
    m12, _ = load_member("510050", data_dir=tmp, anchors=anchors_st,
                        cutoff=dates[-1])
    mean_u, cnt = pure_dca_face(m12, aux11, COST_X1)
    t(cnt >= 12, f"S12a pure-DCA unit count ~ months ({cnt})")
    t(mean_u is not None and bool(np.isfinite(mean_u)),
      "S12b pure-DCA finite mean")

    # [S13] null determinism (BP1 machinery, uniform-day pool)
    pool13 = np.arange(0, m12["n"] - 1, dtype=np.int64)
    w1a, w2a, e1a, e2a, ne1 = BP1.nulls_for_cell(
        m12, aux11, pool13, 3, 0, 20294100, GRID[0], COST_X1, COST_X2)
    w1b, w2b, e1b, e2b, ne2 = BP1.nulls_for_cell(
        m12, aux11, pool13, 3, 0, 20294100, GRID[0], COST_X1, COST_X2)
    t(w1a == w1b and e1a == e1b, "S13a null determinism (same seed/stream)")

    # [S14] seed registry + grammar sha
    t(SG.SEED_REGISTRY.get(SEED_KEY) == 20294100,
      f"S14a SEED_REGISTRY etf_ops_bp2: {SG.SEED_REGISTRY.get(SEED_KEY)}")
    t(BP1._sha16(GRAMMAR) == GRAMMAR_SHA16, "S14b grammar sha self-consistent")

    # [S15] double-run byte-identical stdout
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    outs = []
    rc = 0
    for _ in range(2):
        r = subprocess.run([sys.executable, os.path.abspath(__file__),
                            "selftest", "--inner"],
                           capture_output=True, text=True, env=env, cwd=ROOT)
        outs.append(r.stdout)
        rc = r.returncode
    t(len(outs) == 2 and outs[0] == outs[1] and rc == 0,
      "S15 double-run stdout byte-identical")

    if fails:
        print("SELFTEST FAIL:")
        for f_ in fails:
            print("  -", f_)
        shutil.rmtree(tmp, ignore_errors=True)
        return 1
    print("SELFTEST PASS: 15 legs hermetic; vectorized==brute-force "
          "byte-identity over full start sets; double-run byte-identical")
    shutil.rmtree(tmp, ignore_errors=True)
    return 0


def _selftest_inner(args):
    print("inner ok: grammar", GRAMMAR_SHA16, "seed",
          SG.SEED_REGISTRY.get(SEED_KEY))
    return 0


def main():
    ap = argparse.ArgumentParser(description="ETF-OPS-BP2 runner (T-103 s2 #2)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p_run = sub.add_parser("run")
    p_run.add_argument("--shard", required=True, help="member code or 'all'")
    p_run.add_argument("--force", action="store_true")
    p_fin = sub.add_parser("finalize")
    p_sta = sub.add_parser("status")
    p_ste = sub.add_parser("selftest")
    p_ste.add_argument("--inner", action="store_true")
    args = ap.parse_args()
    if args.cmd == "run":
        return cmd_run(args)
    if args.cmd == "finalize":
        return cmd_finalize(args)
    if args.cmd == "status":
        return cmd_status(args)
    if args.cmd == "selftest":
        if getattr(args, "inner", False):
            return _selftest_inner(args)
        return cmd_selftest(args)
    return 2


if __name__ == "__main__":
    sys.exit(main())
