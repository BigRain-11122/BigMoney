"""INNOVATION_QUOTA_W3 runner -- HIGHERMOM-TIMING-P1 index higher-moment
timing family judged batch (T-2026-09-28-107 sec.4(d), fill_ladder
tranche-3(d); ASTYLE_ZOO #95 index_higher_mom_timing, param-frozen r263).

Laws frozen in research/INNOVATION_QUOTA_W3_PREREG.md @commit 97ca15fee
(r239 bm-c freeze + r240 seed re-take 20317500->20319000 zero-run
correction, bm-b r441 W11 collision; SEED_REGISTRY['innovation_quota_w3_mom']
registered same-window):

  panel   data/daily/sh510300.csv raw pd.read_csv direct read
          (date,open,high,low,close,volume,amount), D2-truncated to
          evidence cutoff 2026-09-28 (new bars locked out). G-PANEL:
          rows == 3486, first == 2012-05-28, last == 2026-09-28. G-SIG
          warmup chain: ret first-valid idx 1 -> moment(20) first-valid
          idx 20 -> EMA(90, adjust=False) first defined idx 20 -> signal
          first decidable idx 21; decidable days 3,465. G-LEG (re-derive
          == frozen probe counts, fail-closed): mom3 86 entries / 4
          stops / 1810 raw long days / 1713 held days; mom4 41/2/908/860;
          mom5 46/5/1854/1733 (results/_r239bmc_highermom_w3_probe_facts.json).
  engine  deterministic daily state machine (prereg s3 frozen): mom(n) =
          ret.pow(n).rolling(20, min_periods=20).mean(); ema =
          mom.ewm(span=90, adjust=False).mean(); rising = ema.diff() > 0
          (T close info, zero lookahead); sig = rising.shift(1) warmup-
          guarded below idx 21 (T+1 position onset, causal). Episodes =
          sig False->True edges (entry at close); exit on sig True->False
          OR -10% since-entry cumulative stop (single stop line,
          conservative reading frozen; after a stop, re-entry only at the
          NEXT episode onset). Position-day return = position(t) x ret(t)
          close-to-close: position(t) = in_pos at end of day t-1 (the
          held-days face 1713/860/1733 IS the accrual-day count; the stop
          day's crash return accrues on its exit day, then the position
          is flat -- episode cumulative == the stop-check r exactly).
          Costs: x1 = ce_transfer.COST_X1_RATE (13.041bp/side) charged
          on |dpos| booked to the following day (round trip = 2 sides);
          judged face = x1; x2 = double-rate disclosure column only.
  cells   3 judged cells (prereg s3 frozen, zero in-batch selection):
          MOM3-TIMING / MOM4-TIMING / MOM5-TIMING (moment order {3,4,5}
          full-spectrum three-leg comparison, zoo r263 freeze candidate).
          Passive = PASSIVE-510300-BH buy-and-hold over the same
          decidable window, batch-window live-computed Sharpe fed to
          g1_prime_v2 passive_override (REPO_CALENDAR_P2 law, no
          hand-copied lines).
  nulls   K=2000 random-episode-placement nulls per leg
          (RANDOM_LARGE_SAMPLE_LAW s3): rng = np.random.default_rng(
          [SEED, k]), k < 2000 (one k-stream shared across legs, seed
          law frozen in prereg s3); each draw preserves the leg's episode
          count, per-episode lengths (= held-days face) and window length
          by permuting the E+1 inter-episode gaps (episode onsets
          randomized, trading intensity preserved, moment structure
          destroyed); same x1 cost machinery (flip count preserved by
          construction). Per-leg family feeds that cell's skill_line
          null_term.
  starts  K=1000 virtual starts (k in [2000, 3000), law s1 K>=1000):
          windows 6m/12m/24m = 126/252/504 trading days (252 ppy
          convention, disclosed); beat = cell window cum ret (x1 net)
          > passive window cum ret, per-window beat_rate disclosed.
          100 random split windows (k in [3000, 3100), law s3 >= 100):
          random split point in [0.2n, 0.8n], half-window Sharpe
          same-sign rate >= 80% = segment-stable.
  gates   G1'v2 per cell via science_gates.g1_prime_v2 (batch_cells=2003
          = 3 judged cells + 2000 null draws, prereg s0 counting law,
          CN_KLINE/W1 same-caliber -- prereg s4 wrote "batch_cells=3" as
          the judged-cell shorthand, s0's N_eff=2003 governs per the W1
          precedent prereg-vs-runner reconciliation; all skill_line
          inputs disclosed), pool='core48' default named-pool reader
          overridden by passive_override = this batch's 510300-BH
          window Sharpe; batch-own null_pool per cell; DSR via
          deflated_sharpe_ratio on the raw x1 cell series; family PBO
          via screening.pbo cscv_pbo CSCV-8 over the 3-cell matrix;
          G2 via g2_registration_v2. No hand-copied lines (O-2250).
  d6      3-cell pairwise |corr| + vs the registered 6 CE members (core48
          equity face via cn_rev_tilt_p1.load_member_rets + REG6 reuse,
          W1 mirror); reject line 0.7; VOLATILITY-CE-01 (2nd-moment
          cross-section) and REGIME_GUARD state faces = near-neighbor
          warning list, different moment-order / different reading.
  ledger  append_ledger("HIGHERMOM_TIMING_P1", 2003,
          "results/innovation_quota/HIGHERMOM-TIMING-P1.json",
          evidence_cutoff="2026-09-28"); out["trials_ledger"] carries the
          return value (r434 pit law); gate_attrition measurement row.

Products (prereg s6): results/innovation_quota/HIGHERMOM-TIMING-P1.json
(top evidence_cutoff + cutoff_meta + panel + legs face + passive +
3 cells + per-leg nulls + virtual starts + splits + d6 + extreme-day
single-column + funnel dual columns + gates + ledger) + nulls shard npy
checkpoints (idempotent resume).

Usage: run | selftest   (exit 0 ok; 2 = fail-closed gate refusal)
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
from ce_transfer import COST_X1_RATE            # x1 = 13.041bp/side (G2-recorded)
from screening.pbo import cscv_pbo              # family PBO CSCV-8
from cn_rev_tilt_p1 import load_member_rets, _corr, REG6   # D6 member face

PANEL_CSV = os.path.join(ROOT, "data", "daily", "sh510300.csv")
OUT_DIR = os.path.join(ROOT, "results", "innovation_quota")
NULL_DIR = os.path.join(OUT_DIR, "nulls_w3")
OUT_JSON = os.path.join(OUT_DIR, "HIGHERMOM-TIMING-P1.json")
OUT_DIR_RESULTS = os.path.dirname(OUT_DIR)      # results root for lib faces
ATT_JSON = os.path.join(ROOT, "results", "gate_attrition.json")

BATCH_NAME = "HIGHERMOM_TIMING_P1"
BATCH_CELLS = 2003                # 3 judged cells + 2000 null draws (s0 law)
EVIDENCE_CUTOFF = "2026-09-28"
PBP = SG.PERIODS_PER_YEAR         # gate-chain single-source convention (252)
K_NULLS = 2000
NULL_SHARDS = 8
K_STARTS = 1000
K_SPLITS = 100
SEED = None                       # filled from SG.SEED_REGISTRY at run
MOM_WINDOW = 20
EMA_SPAN = 90
STOP_LINE = -0.10
FIRST_DECIDABLE = 21
D6_REJECT = 0.7
WIN_DAYS = {"6m": 126, "12m": 252, "24m": 504}   # trading-day windows (252 ppy)

# frozen probe faces (G-PANEL / G-SIG / G-LEG; r239 probe facts file)
PANEL_ROWS = 3486
PANEL_FIRST = "2012-05-28"
PANEL_LAST = "2026-09-28"
DECIDABLE_DAYS = 3465
LEG_FACES = {
    "mom3": {"entries": 86, "stop_exits": 4, "raw_long_days": 1810,
             "held_days": 1713},
    "mom4": {"entries": 41, "stop_exits": 2, "raw_long_days": 908,
             "held_days": 860},
    "mom5": {"entries": 46, "stop_exits": 5, "raw_long_days": 1854,
             "held_days": 1733},
}
CELLS = ["MOM3-TIMING", "MOM4-TIMING", "MOM5-TIMING"]
LEG_OF = {"MOM3-TIMING": "mom3", "MOM4-TIMING": "mom4",
          "MOM5-TIMING": "mom5"}


def gate_refuse(msg):
    print(f"GATE-REFUSE(exit2): {msg}")
    return 2


def sharpe_of(series):
    r = np.asarray(series, dtype=float)
    sd = r.std(ddof=1)
    return float(r.mean() / sd * math.sqrt(PBP)) if sd > 0 else 0.0


def cum_ret(series, lo, hi):
    """Window cumulative return over indices [lo, hi)."""
    seg = np.asarray(series[lo:hi], dtype=float)
    return float(np.prod(1.0 + seg) - 1.0)


# ------------------------------------------------------------------ panel
def load_panel():
    """G-PANEL / G-SIG / G-LEG fail-closed battery + panel assembly.
    Engine re-derivation must match the r239 frozen probe faces exactly
    (one-face-off = config mismatch VOID, INCIDENT-20260928 R3 law)."""
    df = pd.read_csv(PANEL_CSV)
    df = df[df["date"] <= EVIDENCE_CUTOFF].reset_index(drop=True)
    if len(df) != PANEL_ROWS:
        return None, f"G-PANEL rows {len(df)} != {PANEL_ROWS}"
    if str(df["date"].iloc[0]) != PANEL_FIRST or \
            str(df["date"].iloc[-1]) != PANEL_LAST:
        return None, (f"G-PANEL span {df['date'].iloc[0]}.."
                      f"{df['date'].iloc[-1]} != "
                      f"{PANEL_FIRST}..{PANEL_LAST}")
    ret = df["close"].pct_change()
    if int(ret.first_valid_index()) != 1:
        return None, f"G-SIG ret first-valid {ret.first_valid_index()} != 1"
    legs = {}
    for n in (3, 4, 5):
        mom = ret.pow(n).rolling(MOM_WINDOW, min_periods=MOM_WINDOW).mean()
        ema = mom.ewm(span=EMA_SPAN, adjust=False).mean()
        rising = ema.diff() > 0
        sig = rising.shift(1).fillna(False).astype(bool)
        sig.iloc[:FIRST_DECIDABLE] = False
        if int(mom.first_valid_index()) != 20 or \
                int(ema.first_valid_index()) != 20:
            return None, "G-SIG warmup chain broken (moment/EMA idx != 20)"
        pos_end, eps, stops, entries, held, stop_days = \
            run_state_machine(sig, df["close"].to_numpy(dtype=float))
        key = f"mom{n}"
        face = LEG_FACES[key]
        got = {"entries": entries, "stop_exits": stops,
               "raw_long_days": int(rising.sum()),
               "held_days": held}
        for f, v in face.items():
            if got[f] != v:
                return None, (f"G-LEG {key} {f} {got[f]} != frozen {v} "
                              f"(face mismatch -> config VOID, not data "
                              f"corruption)")
        legs[key] = {"sig": sig, "pos_end": pos_end, "episodes": eps,
                     "stop_days": stop_days, "entries": entries,
                     "stops": stops, "held": held,
                     "raw_long_days": int(rising.sum())}
    if len(df) - FIRST_DECIDABLE != DECIDABLE_DAYS:
        return None, (f"G-SIG decidable {len(df) - FIRST_DECIDABLE} != "
                      f"{DECIDABLE_DAYS}")
    face = {"rows": len(df), "first": str(df["date"].iloc[0]),
            "last": str(df["date"].iloc[-1]),
            "close_min": float(df["close"].min()),
            "close_max": float(df["close"].max())}
    return {"df": df, "ret": ret.to_numpy(dtype=float),
            "dates": df["date"].to_numpy(), "legs": legs,
            "panel_face": face}, None


def run_state_machine(sig, close):
    """Frozen s3 segment state machine (probe loop verbatim, extended to
    emit the end-of-day position array + episode list + stop days).

    pos_end[i] = in_pos at end of day i; position-day accrual face:
    position(t) = pos_end[t-1] (held-days count == accrual-day count,
    stop-day crash return accrues on the exit day, then flat).
    """
    n = len(close)
    pos_end = np.zeros(n, dtype=bool)
    eps = []          # (entry_idx, last_accrual_idx) half-open day spans
    cur_entry = None
    in_pos = False
    entry_px = None
    sig_prev = False
    stops = entries = held = 0
    stop_days = []
    for i in range(n):
        s = bool(sig.iloc[i]) if hasattr(sig, "iloc") else bool(sig[i])
        if in_pos:
            r = close[i] / entry_px - 1.0
            if r < STOP_LINE:
                in_pos = False
                stops += 1
                stop_days.append(i)
                eps.append((cur_entry, i))    # last accrual day = stop day
            elif not s:
                in_pos = False
                eps.append((cur_entry, i))    # last accrual day = exit day
        if (not in_pos) and s and not sig_prev:
            in_pos = True
            entry_px = close[i]
            entries += 1
            cur_entry = i
        if in_pos:
            held += 1
        pos_end[i] = in_pos
        sig_prev = s
    return pos_end, eps, stops, entries, held, stop_days


def position_series(pos_end, ret, lo):
    """Decidable-window close-to-close position face: pos[t] = pos_end[t-1]
    over window indices [lo, n); cost = x1 rate on |dpos| booked to the
    following day (entry side on the first accrual day, exit side on the
    first flat day; round trip = 2 sides)."""
    n = len(ret)
    w = n - lo
    pos = np.zeros(w)
    pos[0] = 0.0 if lo == 0 else float(pos_end[lo - 1])
    for t in range(1, w):
        pos[t] = float(pos_end[lo - 1 + t])
    gross = pos * ret[lo:]
    flips = np.zeros(w)
    flips[0] = abs(pos[0] - (0.0 if lo == 0 else float(pos_end[lo - 2])))
    for t in range(1, w):
        flips[t] = abs(pos[t] - pos[t - 1])
    net = gross - COST_X1_RATE * flips
    return pos, gross, net


def passive_series(ret, lo):
    """PASSIVE-510300-BH: buy-and-hold over the same decidable window
    (zero flips, zero cost); batch-window live-computed face."""
    return ret[lo:].copy()


# ------------------------------------------------------------------ nulls
def gap_shuffle_null(pos_end, episodes, rng):
    """One random-episode-placement draw: keep per-episode lengths (=
    held-days face) and episode count, permute the E+1 gaps (leading /
    inter / trailing) -> onsets randomized, window length preserved,
    trading intensity preserved, moment structure destroyed. Same x1 cost
    machinery applies downstream (flip count preserved by construction:
    2 flips per episode)."""
    n = len(pos_end)
    lengths = []
    gaps = []
    prev_end = -1
    for (a, b) in episodes:
        lengths.append(b - a)          # pos_end-True days: a .. b-1
        gaps.append(a - prev_end - 1)  # flat days since last True day
        prev_end = b - 1               # last pos_end-True day of episode
    gaps.append(n - 1 - prev_end)
    perm = rng.permutation(len(gaps))
    new_pos = np.zeros(n, dtype=bool)
    cur = int(gaps[perm[0]])
    for j, L in enumerate(lengths):
        new_pos[cur:cur + L] = True
        cur += L + int(gaps[perm[j + 1]])
    return new_pos


def run_nulls(leg_key, pos_end, episodes, ret, lo):
    """K=2000 null draws for one leg (shared k-stream seed law, rng([SEED,
    k]) k<2000); shard npy checkpoints for idempotent resume."""
    os.makedirs(NULL_DIR, exist_ok=True)
    per = K_NULLS // NULL_SHARDS
    vals = np.empty(K_NULLS)
    for s in range(NULL_SHARDS):
        path = os.path.join(NULL_DIR, f"{leg_key}_shard{s}.npy")
        if os.path.exists(path):
            vals[s * per:(s + 1) * per] = np.load(path)
            continue
        chunk = np.empty(per)
        for i in range(per):
            k = s * per + i
            rng = np.random.default_rng([SEED, k])
            npos = gap_shuffle_null(pos_end, episodes, rng)
            _, _, net = position_series(npos, ret, lo)
            chunk[i] = sharpe_of(net)
        np.save(path, chunk)
        vals[s * per:(s + 1) * per] = chunk
    cov = {"mu": round(float(vals.mean()), 4),
           "sigma": round(float(vals.std(ddof=1)), 4),
           "n_values": int(len(vals))}
    return {"values": [round(float(v), 4) for v in vals],
            "coverage": cov,
            "face": "random episode placement (per-episode lengths + "
                    "episode count + window preserved, E+1 gaps permuted; "
                    "x1 cost machinery applied; moment structure destroyed)"}


# ------------------------------------------------- starts / splits
def virtual_starts(series_by_face, passive):
    """K=1000 random virtual starts x 3 windows (law s1); one rng per k
    shared across windows (per-window identical start position, nested
    windows honest overlap disclosed); beat = cell window cum (x1 net) >
    passive window cum."""
    out = {"n_starts": K_STARTS, "windows_days": WIN_DAYS, "cells": {}}
    n = len(passive)
    wmax = max(WIN_DAYS.values())
    los = []
    for k in range(K_STARTS):
        rng = np.random.default_rng([SEED, 2000 + k])
        los.append(int(rng.integers(0, n - wmax)))
    for name, ser in series_by_face.items():
        s = np.asarray(ser, dtype=float)
        wins = {}
        for wname, w in WIN_DAYS.items():
            hits = 0
            for k in range(K_STARTS):
                lo = los[k]
                hits += int(cum_ret(s, lo, lo + w) >
                            cum_ret(passive, lo, lo + w))
            wins[wname] = {"beats": hits,
                           "beat_rate": round(hits / K_STARTS, 4)}
        out["cells"][name] = wins
    return out


def split_windows(series_by_face):
    """100 random split windows (law s3): split point in [0.2n, 0.8n],
    half-window Sharpe same-sign rate >= 80% = segment-stable."""
    out = {}
    for name, ser in series_by_face.items():
        r = np.asarray(ser, dtype=float)
        n = len(r)
        agree = 0
        for k in range(K_SPLITS):
            rng = np.random.default_rng([SEED, 3000 + k])
            cut = int(rng.integers(int(0.2 * n), int(0.8 * n)))
            a, b = sharpe_of(r[:cut]), sharpe_of(r[cut:])
            agree += int((a > 0) == (b > 0))
        rate = agree / K_SPLITS
        out[name] = {"same_sign_rate": round(rate, 4),
                     "segment_stable": bool(rate >= 0.80),
                     "n_splits": K_SPLITS}
    return out


# ------------------------------------------------------------------ d6
MR_LOADER = None        # member-returns loader (selftest stub hook)


def _default_mr_loader():
    rets, _cuts = load_member_rets()
    return rets, _corr, list(REG6)


def d6_block(P, series_by_cell):
    loader = MR_LOADER or _default_mr_loader
    member_rets, corr_fn, reg6 = loader()
    idx = pd.DatetimeIndex(P["dates"][FIRST_DECIDABLE:])
    out = {"reject_line": D6_REJECT, "members": reg6,
           "near_neighbor_warning": ["VOLATILITY-CE-01 (2nd-moment "
                                     "cross-section face, different order "
                                     "and usage)",
                                     "REGIME_GUARD state face (state "
                                     "machine reading, not moment reading)"],
           "cells": {}}
    for name, ser in series_by_cell.items():
        s = pd.Series(np.asarray(ser, dtype=float), index=idx)
        per = {}
        for tid, mr in member_rets.items():
            v, ov = corr_fn(s, mr)
            per[tid] = {"corr": v, "overlap_days": ov}
        fin = {t: v["corr"] for t, v in per.items()
               if v["corr"] is not None}
        amax = max(fin, key=lambda t: abs(fin[t])) if fin else None
        out["cells"][name] = {
            "per_member": per,
            "max_abs_corr_member": round(abs(fin[amax]), 4) if amax else None,
            "reject": bool(amax and abs(fin[amax]) >= D6_REJECT)}
    cross = {}
    names = list(series_by_cell)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a = np.asarray(series_by_cell[names[i]], dtype=float)
            b = np.asarray(series_by_cell[names[j]], dtype=float)
            if a.std() > 0 and b.std() > 0:
                cross[f"{names[i]}|{names[j]}"] = round(float(
                    np.corrcoef(a, b)[0, 1]), 4)
    out["same_batch_cross"] = cross
    return out


# ------------------------------------------------------------------ product
def _cell_stats(ser):
    r = np.asarray(ser, dtype=float)
    n = len(r)
    eq = np.cumprod(1.0 + r)
    dd = float((eq / np.maximum.accumulate(eq) - 1.0).min())
    ann = float(eq[-1] ** (PBP / max(n, 1)) - 1.0)
    return {"sharpe_full": round(sharpe_of(r), 4),
            "ann_ret": round(ann, 6),
            "max_dd": round(dd, 6), "n_days": int(n),
            "median_abs_r": round(float(np.median(np.abs(r))), 8)}


def episode_kpi(passive_ser, net_ser, P, episodes):
    """O-1524 KPI dual disclosure. Trade-level faces (the law's primary
    reading: 交易级胜率+期望+盈亏比) + the W1-lineage passive-same-days
    faces. Degeneracy disclosure: for a pure long-flat timing face the
    cell is fully invested on every intra-episode day, so the
    vs-passive-same-days edge is -entry-cost by construction (win rate 0,
    honest face kept for W1 lineage comparability) -- the alpha question
    lives at the full-window/segment-mix level (G1/vstarts/splits)."""
    pas = np.asarray(passive_ser, dtype=float)
    cel = np.asarray(net_ser, dtype=float)
    wins_p, edges, ep_rets = 0, [], []
    for (a, b) in episodes:
        lo = a + 1 - FIRST_DECIDABLE
        hi = b + 1 - FIRST_DECIDABLE
        if lo < 0 or hi > len(pas):
            continue
        e_cum = float(np.prod(1.0 + cel[lo:hi]) - 1.0)
        p_cum = float(np.prod(1.0 + pas[lo:hi]) - 1.0)
        if np.isfinite(e_cum) and np.isfinite(p_cum):
            wins_p += int(e_cum > p_cum)
            edges.append(e_cum - p_cum)
            ep_rets.append(e_cum)
    n_ep = len(ep_rets)
    win_rets = [r for r in ep_rets if r > 0]
    loss_rets = [r for r in ep_rets if r <= 0]
    payoff = None
    if win_rets and loss_rets:
        mw = float(np.mean(win_rets))
        ml = abs(float(np.mean(loss_rets)))
        payoff = round(mw / ml, 4) if ml > 0 else None
    return {
        "n_closed_episodes": n_ep,
        "win_rate_trade_level": round(
            len(win_rets) / n_ep, 4) if n_ep else None,
        "mean_episode_return": round(
            float(np.mean(ep_rets)), 8) if ep_rets else None,
        "payoff_ratio_win_over_loss": payoff,
        "win_rate_vs_passive_same_days": round(wins_p / n_ep, 4)
        if n_ep else None,
        "mean_episode_edge_vs_passive": round(float(np.mean(edges)), 8)
        if edges else None,
        "kpi_face_note": "trade-level faces are the O-1524 primary "
                         "reading; vs-passive-same-days faces are "
                         "structurally -entry-cost for long-flat timing "
                         "(degenerate, kept for W1 lineage)",
    }


def extreme_face(P, legs):
    """Extreme-day single-column disclosure (prereg s4/s5): panel worst/
    best day + per-leg stop-exit dates (moment-dominated events)."""
    ret = P["ret"]
    dates = P["dates"]
    worst = int(np.nanargmin(ret))
    best = int(np.nanargmax(ret))
    out = {
        "worst_day": {"date": str(dates[worst]),
                      "ret": round(float(ret[worst]), 6)},
        "best_day": {"date": str(dates[best]),
                     "ret": round(float(ret[best]), 6)},
        "stop_exit_days": {},
    }
    for key, leg in legs.items():
        out["stop_exit_days"][key] = [str(dates[i]) for i in leg["stop_days"]]
    return out


def _attr_row(batch, delta, total, gates, entries):
    d = json.load(open(ATT_JSON, encoding="utf-8"))
    row = {"batch": batch,
           "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
           "kind": "measurement", "cells_ledger_delta": delta,
           "ledger_total_after": total, "gates": gates,
           "entries": entries}
    own = [i for i, e in enumerate(d["entries"])
           if e.get("batch") == batch and e.get("kind") == "measurement"]
    if own:
        d["entries"][own[-1]] = row
    else:
        d["entries"].append(row)
    with open(ATT_JSON + ".tmp", "w", encoding="utf-8") as fh:
        json.dump(d, fh, ensure_ascii=False, indent=1)
    os.replace(ATT_JSON + ".tmp", ATT_JSON)


def phase1_write(P, cells, passive_stats, nulls, vstarts, splits, d6,
                 xfaces):
    """Phase-1 product (no gates): passive_override consumer face."""
    os.makedirs(OUT_DIR, exist_ok=True)
    product = {
        "batch": BATCH_NAME,
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "cutoff_meta": SG.cutoff_meta(EVIDENCE_CUTOFF),
        "prereg": "research/INNOVATION_QUOTA_W3_PREREG.md (@97ca15fee "
                  "freeze + r240 seed re-take 20319000)",
        "seed": {"base": SEED, "k_nulls": K_NULLS,
                 "retake_note": "20317500 -> 20319000 zero-run correction "
                                "(bm-b r441 W11 collision, later-yields)"},
        "panel": P["panel_face"],
        "warmup_law": "ret idx 1 -> moment(20) idx 20 -> EMA(90) idx 20 "
                      "-> signal decidable idx 21; decidable days 3,465",
        "legs_face": {k: {"entries": v["entries"],
                          "stop_exits": v["stops"],
                          "raw_signal_long_days": v["raw_long_days"],
                          "held_days_after_stop_overlay": v["held"]}
                      for k, v in P["legs"].items()},
        "cost_face": {"x1_rate_per_side": COST_X1_RATE,
                      "booking": "|dpos| booked to the following day; "
                                 "round trip = 2 sides",
                      "judged_face": "x1",
                      "x2_disclosure": 2 * COST_X1_RATE},
        "engine_law": "mom(n)=ret^n.rolling(20).mean; ema=ewm(90, "
                      "adjust=False); rising=ema.diff()>0; sig=rising."
                      "shift(1) (T+1 onset); episodes on sig False->True; "
                      "exit on True->False or -10% since-entry stop; "
                      "after stop re-entry only at next episode onset; "
                      "position(t)=pos_end(t-1), close-to-close",
        "passive": {"passive_510300_bh": {"full": passive_stats}},
        "cells": {n: cells[n]["stats"] for n in CELLS},
        "nulls": nulls, "virtual_starts": vstarts, "splits": splits,
        "d6": d6,
        "extreme_day_face": xfaces["extreme"],
        "funnel": {"harvest_column": 1,
                   "harvest_note": "in-repo untried face scan (zoo #95 "
                                   "untried family, r239 probe facts)",
                   "gate_column": "0/3 pending judgment (this batch)"},
    }
    with open(OUT_JSON + ".tmp", "w", encoding="utf-8") as fh:
        json.dump(product, fh, ensure_ascii=False, indent=1)
    os.replace(OUT_JSON + ".tmp", OUT_JSON)
    return product


def finalize(product, P, cells, passive_ser):
    prev_total = None
    if os.path.exists(OUT_JSON):
        try:
            with open(OUT_JSON, encoding="utf-8") as fh:
                old = json.load(fh)
            prev_total = (old.get("trials_ledger") or {}).get("prev_total")
        except Exception:
            prev_total = None
    passive_override = product["passive"]["passive_510300_bh"]["full"][
        "sharpe_full"]
    gates = {}
    for name in CELLS:
        net = cells[name]["net"]
        st = cells[name]["stats"]
        g1 = SG.g1_prime_v2(st["sharpe_full"], net,
                            batch_cells=BATCH_CELLS, pool="core48",
                            results_dir=OUT_DIR_RESULTS,
                            null_pool={"values": product["nulls"][
                                           LEG_OF[name]]["values"],
                                       "coverage": product["nulls"][
                                           LEG_OF[name]]["coverage"]},
                            n_trades=P["legs"][LEG_OF[name]]["entries"],
                            n_entries=P["legs"][LEG_OF[name]]["entries"],
                            passive_override=passive_override)
        dsr = SG.deflated_sharpe_ratio(
            net, n_trials=g1["skill_line"]["n_eff"])
        gates[name] = {"g1_prime_v2": g1, "dsr": dsr}
    mat = pd.DataFrame({n: np.asarray(cells[n]["net"], dtype=float)
                        for n in CELLS})
    pbo = cscv_pbo(mat)
    for name in gates:
        gates[name]["g2"] = SG.g2_registration_v2(
            gates[name]["g1_prime_v2"]["pass_v2"], gates[name]["dsr"],
            float(pbo["pbo"]))
        gates[name]["d6_reject"] = bool(
            product["d6"]["cells"][name]["reject"])
    ledger = SG.append_ledger(BATCH_NAME, BATCH_CELLS,
                              file_name="results/innovation_quota/"
                                        "HIGHERMOM-TIMING-P1.json",
                              evidence_cutoff=EVIDENCE_CUTOFF,
                              prev_total=prev_total)
    product["gates"] = gates
    product["family_pbo"] = pbo
    product["passive_override_fed"] = passive_override
    product["episode_kpi"] = {
        n: episode_kpi(passive_ser, cells[n]["net"], P,
                       P["legs"][LEG_OF[n]]["episodes"])
        for n in CELLS}
    product["trials_ledger"] = ledger          # r434 pit law: value carried
    product["judgment_note"] = ("judged per prereg s4 via shared library; "
                                "judged-negative family = slot closed + "
                                "new-evidence reopen note (law s5); "
                                "G2-eligible cell = T-34 fastline candidate "
                                "pool registration face, intake walks the "
                                "CE admission harness separately; T0 brake "
                                "authority stays with REGIME_GUARD")
    with open(OUT_JSON + ".tmp", "w", encoding="utf-8") as fh:
        json.dump(product, fh, ensure_ascii=False, indent=1)
    os.replace(OUT_JSON + ".tmp", OUT_JSON)
    _attr_row(BATCH_NAME, BATCH_CELLS, int(ledger["total"]),
              {"g1_pass": {n: gates[n]["g1_prime_v2"]["pass_v2"]
                           for n in gates},
               "g2_eligible": {n: gates[n]["g2"]["eligible_v2"]
                               for n in gates},
               "family_pbo": pbo},
              {"episodes": {n: P["legs"][LEG_OF[n]]["entries"]
                            for n in CELLS},
               "stops": {n: P["legs"][LEG_OF[n]]["stops"] for n in CELLS}})
    return product


# ------------------------------------------------------------------ driver
def cmd_run():
    global SEED
    SEED = SG.SEED_REGISTRY["innovation_quota_w3_mom"]
    t0 = time.time()
    P, err = load_panel()
    if err:
        return gate_refuse(err)
    print(f"panel ok: {P['panel_face']['rows']} rows, legs "
          f"{ {k: (v['entries'], v['stops']) for k, v in P['legs'].items()} }"
          f" ({time.time() - t0:.0f}s)", flush=True)
    lo = FIRST_DECIDABLE
    passive_ser = passive_series(P["ret"], lo)
    passive_stats = _cell_stats(passive_ser)
    passive_stats["sharpe"] = passive_stats["sharpe_full"]  # alias face
    cells = {}
    for name in CELLS:
        leg = P["legs"][LEG_OF[name]]
        pos, gross, net = position_series(leg["pos_end"], P["ret"], lo)
        cells[name] = {"pos": pos, "gross": gross, "net": net,
                       "stats": _cell_stats(net)}
        print(f"  cell {name}: sharpe_x1={cells[name]['stats']['sharpe_full']}"
              f" entries={leg['entries']} stops={leg['stops']}"
              f" ({time.time() - t0:.0f}s)", flush=True)
    nulls = {}
    for name in CELLS:
        leg = P["legs"][LEG_OF[name]]
        nulls[LEG_OF[name]] = run_nulls(LEG_OF[name], leg["pos_end"],
                                        leg["episodes"], P["ret"], lo)
        print(f"  nulls {LEG_OF[name]}: mu={nulls[LEG_OF[name]]['coverage']['mu']}"
              f" sigma={nulls[LEG_OF[name]]['coverage']['sigma']}"
              f" ({time.time() - t0:.0f}s)", flush=True)
    series_by_face = {n: cells[n]["net"] for n in CELLS}
    vstarts = virtual_starts(series_by_face, passive_ser)
    splits = split_windows({**series_by_face,
                            "PASSIVE-510300-BH": passive_ser})
    d6 = d6_block(P, series_by_face)
    xfaces = {"extreme": extreme_face(P, P["legs"])}
    product = phase1_write(P, cells, passive_stats, nulls, vstarts, splits,
                           d6, xfaces)
    print(f"phase-1 product written ({time.time() - t0:.0f}s)", flush=True)
    product = finalize(product, P, cells, passive_ser)
    print(f"finalize ok: cells={len(cells)} "
          f"ledger={product['trials_ledger']['total']} "
          f"elapsed={time.time() - t0:.0f}s")
    return 0


# ------------------------------------------------------------------ selftest
def _mk_equity_fixture(tmp):
    """Synthetic 510300-like panel: geometric walk with a planted crash
    cluster + planted trend regimes so moment signals have structure."""
    global PANEL_CSV
    dates = pd.bdate_range("2012-05-28", end="2026-09-28")
    n = len(dates)
    rng = np.random.default_rng(7)
    ret = rng.normal(0.0002, 0.012, n)
    # planted crash: two consecutive -10% days mid-panel (stop face)
    crash = n // 2
    ret[crash] = -0.1005
    ret[crash + 1] = 0.0999
    # planted long bull regime early (moment legs should enter)
    ret[100:400] += 0.0015
    close = 3.0 * np.cumprod(1.0 + ret)
    df = pd.DataFrame({
        "date": dates.strftime("%Y-%m-%d"),
        "open": close * 0.999, "high": close * 1.01, "low": close * 0.99,
        "close": close, "volume": 1e6, "amount": 1e8,
    })
    PANEL_CSV = os.path.join(tmp, "sh510300.csv")
    df.to_csv(PANEL_CSV, index=False)
    return df


def cmd_selftest():
    global OUT_DIR, NULL_DIR, OUT_JSON, OUT_DIR_RESULTS, ATT_JSON, SEED, \
        K_NULLS, NULL_SHARDS, K_STARTS, K_SPLITS, PANEL_ROWS, PANEL_FIRST, \
        PANEL_LAST, DECIDABLE_DAYS, LEG_FACES, MR_LOADER, PANEL_CSV
    tmp = tempfile.mkdtemp(prefix="innovation_quota_w3_selftest_")
    K_NULLS, NULL_SHARDS = 40, 2     # >= 30: skill_line_v2 thin-pool floor
    K_STARTS, K_SPLITS = 12, 6
    SEED = 20319000

    def _stub_corr(a, b, min_overlap=20):
        j = pd.concat([a, b], axis=1, join="inner").dropna()
        if len(j) < min_overlap:
            return None, int(len(j))
        v = float(np.corrcoef(j.iloc[:, 0], j.iloc[:, 1])[0, 1])
        return round(v, 4), int(len(j))

    MR_LOADER = (lambda: (
        {"M1": pd.Series(np.sin(np.arange(800) / 30.0) * 0.01,
                         index=pd.bdate_range("2020-01-01", periods=800))},
        _stub_corr, ["M1"]))
    # tmp-path reassignment FIRST: every face (nulls included) must stay
    # hermetic -- a late reassignment poisons the real nulls_w3 dir with
    # selftest-sized shards (resume broadcast crash, this round's fix)
    OUT_DIR = os.path.join(tmp, "results", "innovation_quota")
    NULL_DIR = os.path.join(OUT_DIR, "nulls_w3")
    OUT_JSON = os.path.join(OUT_DIR, "HIGHERMOM-TIMING-P1.json")
    OUT_DIR_RESULTS = os.path.dirname(OUT_DIR)
    os.makedirs(NULL_DIR, exist_ok=True)
    ATT_JSON = os.path.join(tmp, "attr.json")
    json.dump({"entries": []}, open(ATT_JSON, "w"))
    ok = []
    try:
        df = _mk_equity_fixture(tmp)
        # derive-then-freeze the panel/leg gate constants on the fixture
        cut_df = df  # fixture last row == 2026-09-28 by construction
        PANEL_ROWS = len(cut_df)
        PANEL_FIRST = str(cut_df["date"].iloc[0])
        PANEL_LAST = str(cut_df["date"].iloc[-1])
        DECIDABLE_DAYS = PANEL_ROWS - FIRST_DECIDABLE
        ret = cut_df["close"].pct_change()
        LEG_FACES = {}
        for n_ in (3, 4, 5):
            mom = ret.pow(n_).rolling(MOM_WINDOW,
                                      min_periods=MOM_WINDOW).mean()
            ema = mom.ewm(span=EMA_SPAN, adjust=False).mean()
            rising = ema.diff() > 0
            sig = rising.shift(1).fillna(False).astype(bool)
            sig.iloc[:FIRST_DECIDABLE] = False
            pos_end, eps, stops, entries, held, sd = run_state_machine(
                sig, cut_df["close"].to_numpy(dtype=float))
            LEG_FACES[f"mom{n_}"] = {
                "entries": entries, "stop_exits": stops,
                "raw_long_days": int(rising.sum()), "held_days": held}
            if n_ == 3:
                ok.append(("fixture mom3 episodes derived", entries > 0))
        ok.append(("fixture legs have structure (entries>0, held>0)",
                   all(LEG_FACES[f"mom{n_}"]["entries"] > 0
                       and LEG_FACES[f"mom{n_}"]["held_days"] > 0
                       for n_ in (3, 4, 5))))

        # state-machine hand-check on a tiny planted calendar
        idx = pd.RangeIndex(12)
        close = np.array([10, 10.5, 11, 10.8, 9.5, 9.4, 9.3, 9.0, 9.2,
                          9.6, 10.2, 10.4])
        sig = pd.Series([False] * 2 + [True] * 6 + [False] * 4, index=idx)
        pos_end, eps, stops, entries, held, sd = run_state_machine(
            sig, close)
        # entry at day 2 (close 11.0); day 3 r=-1.8% no stop; day 4
        # r=9.5/11-1=-13.64% < -10% -> stop at day 4; no re-entry (sig
        # stays True -> no False->True edge); held = days 2..3 = 2
        ok.append(("tiny stop machine: 1 entry, 1 stop, held=2 (d2..d3)",
                   entries == 1 and stops == 1 and held == 2
                   and eps == [(2, 4)] and sd == [4]))
        ok.append(("tiny machine pos_end face",
                   list(pos_end.astype(int)) ==
                   [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]))

        # position_series shift semantics: accrual day t = pos_end[t-1]
        ret_arr = np.array([0.0, 0.05, 0.0, -0.02, -0.10, -0.01, 0.03,
                            0.0, 0.0, 0.0, 0.0, 0.0])
        pos, gross, net = position_series(pos_end, ret_arr, 0)
        ok.append(("pos = shifted pos_end (day t holds pos_end[t-1])",
                   list(pos.astype(float)) ==
                   [0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0]))
        # cost: flips = entry (booked d3) + exit (booked d5) = 2 sides
        ok.append(("cost booking: 2 flip sides, x1 rate each",
                   abs(float(np.sum(np.abs(np.diff(np.concatenate(
                       [[0.0], pos]))))) - 2.0) < 1e-12
                   and abs(net[5] - (0.0 - COST_X1_RATE * 1.0)) < 1e-12
                   and abs(net[3] - (ret_arr[3] - COST_X1_RATE)) < 1e-12))
        # stop-day crash return accrues (gross[4] = -0.10 * 1)
        ok.append(("stop-day crash return accrues on exit day",
                   abs(gross[4] - (-0.10)) < 1e-12))

        # gap-shuffle null: episode count + held days preserved
        npos = gap_shuffle_null(pos_end, eps,
                                np.random.default_rng([SEED, 0]))
        npos_int = npos.astype(int)
        flips_null = int(np.abs(np.diff(
            np.concatenate([[0], npos_int]))).sum())
        ok.append(("null preserves episode count + held days",
                   int(npos.sum()) == held and flips_null == 2 * entries))

        # full pipeline on fixture
        P, err = load_panel()
        ok.append(("panel/leg gates pass on fixture", err is None))
        if err:
            raise RuntimeError(err)
        lo = FIRST_DECIDABLE
        passive_ser = passive_series(P["ret"], lo)
        cells = {}
        for name in CELLS:
            leg = P["legs"][LEG_OF[name]]
            pos, gross, net = position_series(leg["pos_end"], P["ret"], lo)
            cells[name] = {"pos": pos, "gross": gross, "net": net,
                           "stats": _cell_stats(net)}
        ok.append(("3 cells + passive derive finite",
                   all(np.isfinite(cells[c]["stats"]["sharpe_full"])
                       for c in cells)
                   and np.isfinite(_cell_stats(passive_ser)["sharpe_full"])))
        n1 = run_nulls("mom3", P["legs"]["mom3"]["pos_end"],
                       P["legs"]["mom3"]["episodes"], P["ret"], lo)
        n2 = run_nulls("mom3", P["legs"]["mom3"]["pos_end"],
                       P["legs"]["mom3"]["episodes"], P["ret"], lo)
        ok.append(("nulls deterministic (npy resume) + size",
                   n1["values"] == n2["values"]
                   and len(n1["values"]) == K_NULLS))
        series_by_face = {n: cells[n]["net"] for n in CELLS}
        vstarts = virtual_starts(series_by_face, passive_ser)
        splits = split_windows({**series_by_face,
                                "PASSIVE-510300-BH": passive_ser})
        d6 = d6_block(P, series_by_face)
        xfaces = {"extreme": extreme_face(P, P["legs"])}
        ok.append(("vstarts/splits/d6 shapes",
                   set(vstarts["cells"]) == set(CELLS)
                   and all(set(vstarts["cells"][c]) == set(WIN_DAYS)
                           for c in vstarts["cells"])
                   and all("segment_stable" in splits[s] for s in splits)
                   and not d6["cells"]["MOM3-TIMING"]["reject"]))
        ok.append(("extreme face carries stop dates + worst/best",
                   set(xfaces["extreme"]["stop_exit_days"]) ==
                   set(P["legs"])
                   and "worst_day" in xfaces["extreme"]))
        nulls_all = {LEG_OF[n]: run_nulls(LEG_OF[n],
                                          P["legs"][LEG_OF[n]]["pos_end"],
                                          P["legs"][LEG_OF[n]]["episodes"],
                                          P["ret"], lo) for n in CELLS}
        product = phase1_write(P, cells, _cell_stats(passive_ser),
                               nulls_all, vstarts, splits, d6, xfaces)

        # shared-library stateful faces stubbed (hermetic isolation)
        _ne, _al, _lh = SG.n_eff, SG.append_ledger, SG.ledger_head
        SG.n_eff = lambda bc, rd=None: int(bc)
        SG.append_ledger = lambda *a, **k: {"prev_total": 0, "total": 100,
                                            "batch": BATCH_NAME}
        SG.ledger_head = lambda rd=None: {"total": 500, "file": None,
                                          "note": None}
        _real_cscv = globals()["cscv_pbo"]
        globals()["cscv_pbo"] = lambda mat: {"pbo": 0.1}
        try:
            product = finalize(product, P, cells, passive_ser)
            ok.append(("finalize product fields",
                       os.path.exists(OUT_JSON)
                       and product["evidence_cutoff"] == EVIDENCE_CUTOFF
                       and "cutoff_meta" in product
                       and len(product["gates"]) == 3
                       and all("g2" in g for g in product["gates"].values())
                       and product["trials_ledger"]["total"] == 100
                       and product["passive_override_fed"] ==
                       product["passive"]["passive_510300_bh"]["full"]
                       ["sharpe_full"]))
            ok.append(("episode kpi face (O-1524 trade-level + lineage)",
                       all("win_rate_vs_passive_same_days"
                           in product["episode_kpi"][n]
                           and "win_rate_trade_level"
                           in product["episode_kpi"][n]
                           for n in CELLS)))
            att = json.load(open(ATT_JSON, encoding="utf-8"))
            ok.append(("attrition row + funnel dual columns",
                       att["entries"][-1]["batch"] == BATCH_NAME
                       and product["funnel"]["harvest_column"] == 1))
        finally:
            SG.n_eff, SG.append_ledger, SG.ledger_head = _ne, _al, _lh
            globals()["cscv_pbo"] = _real_cscv

        # gate-refusal paths (drift -> refuse)
        real_rows = PANEL_ROWS
        PANEL_ROWS = real_rows + 1
        _, err2 = load_panel()
        ok.append(("G-PANEL drift refusal", err2 is not None
                   and "rows" in str(err2)))
        PANEL_ROWS = real_rows
        real_leg = LEG_FACES["mom3"]["entries"]
        LEG_FACES["mom3"] = dict(LEG_FACES["mom3"], entries=real_leg + 1)
        _, err3 = load_panel()
        ok.append(("G-LEG drift refusal", err3 is not None
                   and "G-LEG" in str(err3)))
        LEG_FACES["mom3"] = dict(LEG_FACES["mom3"], entries=real_leg)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    n_ok = sum(1 for _, v in ok if v)
    print(f"innovation_quota_w3 selftest: {n_ok}/{len(ok)} PASS")
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
            os.environ.get("INNOVATION_QUOTA_W3_REFINALIZE") != "1":
        print("idempotent no-op: HIGHERMOM-TIMING-P1.json exists "
              "(INNOVATION_QUOTA_W3_REFINALIZE=1 = only redo)")
        return 0
    return cmd_run()


if __name__ == "__main__":
    sys.exit(main())
