"""INNOVATION_QUOTA_W1 runner -- REPO-CALENDAR-P1 repo calendar term-swing
family judged batch (T-2026-09-28-107 sec.4(d), fill_ladder tranche-1(d)).

Laws frozen in research/INNOVATION_QUOTA_W1_PREREG.md @commit dd62920e
(r180 bm-c, SEED_REGISTRY['innovation_quota_w1_repo']=20295000 registered
same-commit):

  panel   data/repo_daily/*.csv raw pd.read_csv direct read (date,open,high,
          low,close,volume), 11 terms, every file D2-truncated to evidence
          cutoff 2026-09-22 (new bars locked out). G-PANEL: 11 files;
          judged terms GC001/007/014/028 last row == cutoff; GC001 rows ==
          3735. G-CALENDAR (re-derive == frozen probe counts, fail-closed):
          month-end last-2 == 370, quarter-end last-5 == 310, pre-longholiday
          pre-gap last-2 == 194 (gap >= 4 natural days on the panel's own
          trading calendar = the sole calendar authority, zero look-ahead:
          a window day is known at its own close). G-RATE: judged-domain
          closes in (0, 200).
  engine  deterministic daily-accrual swing state machine (prereg s3
          frozen): decisions happen at trading-day closes; a GC001
          overnight decided at d accrues close(d)/365 on the single natural
          day d+1 ("次日单日计息", daily roll -- the 每日滚隔夜 passive face);
          a term GC-k decided at d locks close_k(d) and accrues
          close_k(d)/365 on each natural day d+1 .. d+k (no early
          redemption -- real repo constraint); after a term matures, the
          first trading day strictly after the maturity re-decides (funds
          return at maturity). Daily return series = per-natural-day
          accruals (frozen engine law "日收益=计息利率/365 逐自然日累乘");
          natural days with no active position accrue 0 (single-day
          overnight clause, disclosed honestly). Sharpe annualized at the
          shared-library PERIODS_PER_YEAR for gate-chain single-source
          consistency; natural-day annualized return disclosed alongside.
  cells   4 judged cells (prereg s3 frozen, zero in-batch selection):
          CAL-SWITCH-GC007 (month-end last-2 + pre-longholiday last-2 ->
          overnight GC001, else GC007 term roll),
          CAL-SWITCH-GC014 (same windows, GC014),
          QW5-SWITCH-GC014 (quarter-end last-5 + pre-longholiday last-2 ->
          overnight, else GC014),
          CAL-SWITCH-GC028 (same windows as cell 1, GC028).
          Passive = PASSIVE-GC001-ROLL (daily overnight roll). Cost face =
          zero transaction cost (exchange repo fee negligible for the cash
          leg, pre-fee basis disclosed; if a cell ever registers, the
          five-step law carries the fee-after re-check at the paper face).
  nulls   K=2000 random calendar-swing nulls (RANDOM_LARGE_SAMPLE_LAW s3):
          rng = np.random.default_rng([20295000, k]); each draw preserves
          the CAL-union window-day count per Gregorian year (swing strength
          preserved) but shuffles WHICH trading days are window days
          (calendar structure destroyed); null machinery = CAL-SWITCH-GC007
          structure on the pseudo-calendar. Family pool -> skill_line_v2
          null_term.
  starts  K=1000 virtual starts (k in [2000, 3000), law s1 K>=1000):
          windows 6m/12m/24m = 183/365/730 natural days, beat = cell window
          cum return > passive window cum return, per-window beat_rate
          disclosed (law s1 binding). 100 random split windows (k in
          [3000, 3100), law s3 >= 100): random split point in [0.2n, 0.8n]
          of the natural-day series, half-window Sharpe same-sign rate
          >= 80% = segment-stable.
  gates   G1'v2 per cell via science_gates.g1_prime_v2 (batch_cells=2004,
          pool='repo_cash' -- additive passive branch reads THIS batch's
          own PASSIVE-GC001-ROLL Sharpe from the phase-1 product; the
          cash-leg domain never borrows equity passives), batch-own null
          pool; DSR via deflated_sharpe_ratio on the raw cell series;
          family PBO via screening/pbo cscv_pbo CSCV-8 over the 4-cell
          matrix; G2 via g2_registration_v2. No hand-copied lines (O-2250).
  d6      4-cell pairwise |corr| + vs the registered 6 CE members (core48
          equity face via cn_rev_tilt_p1.load_member_rets reuse); reject
          line 0.7; cross-asset expectation < 0.1 disclosed as prior only.
  ledger  append_ledger("REPO_CALENDAR_P1", 2004, "results/innovation_quota/
          REPO-CALENDAR-P1.json", evidence_cutoff="2026-09-22")
          single-count; gate_attrition measurement row (r248 entries face).

Products (prereg s6): results/innovation_quota/REPO-CALENDAR-P1.json (top
evidence_cutoff + cutoff_meta + panel + passive + 4 cells + nulls +
virtual starts + splits + d6 + extreme-day tail + funnel dual columns +
gates + ledger) + nulls shard npy checkpoints (idempotent resume).

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
from screening.pbo import cscv_pbo              # family PBO CSCV-8

PANEL_DIR = os.path.join(ROOT, "data", "repo_daily")
OUT_DIR = os.path.join(ROOT, "results", "innovation_quota")
NULL_DIR = os.path.join(OUT_DIR, "nulls")
OUT_JSON = os.path.join(OUT_DIR, "REPO-CALENDAR-P1.json")
# results ROOT for shared-library faces (repo_cash branch joins
# innovation_quota/REPO-CALENDAR-P1.json under it; live ledger chain head)
OUT_DIR_RESULTS = os.path.dirname(OUT_DIR)
ATT_JSON = os.path.join(ROOT, "results", "gate_attrition.json")

BATCH_NAME = "REPO_CALENDAR_P1"
BATCH_CELLS = 2004                # 4 judged cells + 2000 null draws (s0)
EVIDENCE_CUTOFF = "2026-09-22"
PBP = SG.PERIODS_PER_YEAR         # gate-chain single-source convention
K_NULLS = 2000
NULL_SHARDS = 8
K_STARTS = 1000
K_SPLITS = 100
SEED = None                       # filled from SG.SEED_REGISTRY at run
TERMS_ALL = ["GC001", "GC003", "GC004", "GC007", "GC014", "GC028",
             "GC091", "GC182", "R-001", "R-003", "R-007"]
JUDGED_TERMS = ["GC001", "GC007", "GC014", "GC028"]
GC001_ROWS = 3735                 # frozen probe (G-PANEL)
CAL_MONTH_END, CAL_QUARTER_END, CAL_PREHOL = 370, 310, 194  # G-CALENDAR
GAP_MIN_DAYS = 4                  # pre-longholiday gap definition (frozen)
D6_REJECT = 0.7
WIN_DAYS = {"6m": 183, "12m": 365, "24m": 730}   # natural-day windows (law s1)

# extreme-day family (prereg s4/s5 disclosure carries)
EXTREME_PRIORS = ["2013-06 money-famine window", "2015-02-10 GC001 53.44",
                  "2015-07 crash-week window days"]


def gate_refuse(msg):
    print(f"GATE-REFUSE(exit2): {msg}")
    return 2


def _d(x):
    """datetime64[D] -> int day number helper."""
    return int(x.astype("datetime64[D]").astype("int64"))


# ------------------------------------------------------------------ panel
def load_repo_panel():
    """G-PANEL / G-RATE / G-CALENDAR fail-closed battery + panel assembly."""
    files = sorted(f for f in os.listdir(PANEL_DIR) if f.endswith(".csv"))
    stems = [f[:-4] for f in files]
    if sorted(stems) != sorted(TERMS_ALL):
        return None, f"panel census drift: {sorted(stems)} != {TERMS_ALL}"
    cut = pd.Timestamp(EVIDENCE_CUTOFF)
    frames = {}
    for s in stems:
        df = pd.read_csv(os.path.join(PANEL_DIR, s + ".csv"))
        df["date"] = pd.to_datetime(df["date"])
        df = df[df["date"] <= cut].reset_index(drop=True)
        if not len(df):
            return None, f"{s}: empty after cutoff truncation"
        frames[s] = df
    for s in JUDGED_TERMS:
        if str(frames[s]["date"].iloc[-1].date()) != EVIDENCE_CUTOFF:
            return None, (f"G-PANEL {s} last row "
                          f"{frames[s]['date'].iloc[-1].date()} != "
                          f"{EVIDENCE_CUTOFF}")
    if len(frames["GC001"]) != GC001_ROWS:
        return None, f"G-PANEL GC001 rows {len(frames['GC001'])} != {GC001_ROWS}"
    for s in JUDGED_TERMS:
        c = frames[s]["close"].to_numpy(dtype=float)
        if not (np.isfinite(c).all() and (c > 0).all() and (c < 200).all()):
            return None, f"G-RATE {s} close outside (0, 200)"
    cal = frames["GC001"]["date"].to_numpy().astype("datetime64[D]")
    w_me = month_end_window(cal, 2)
    w_qe = month_end_window(cal, 5, quarter=True)
    w_ph = pre_longholiday_window(cal, 2)
    if int(w_me.sum()) != CAL_MONTH_END:
        return None, (f"G-CALENDAR month-end {int(w_me.sum())} != "
                      f"{CAL_MONTH_END}")
    if int(w_qe.sum()) != CAL_QUARTER_END:
        return None, (f"G-CALENDAR quarter-end {int(w_qe.sum())} != "
                      f"{CAL_QUARTER_END}")
    if int(w_ph.sum()) != CAL_PREHOL:
        return None, (f"G-CALENDAR pre-longholiday {int(w_ph.sum())} != "
                      f"{CAL_PREHOL}")
    rates = {s: frames[s]["close"].to_numpy(dtype=float) for s in JUDGED_TERMS}
    face = {s: {"rows": len(frames[s]),
                "first": str(frames[s]["date"].iloc[0].date()),
                "last": str(frames[s]["date"].iloc[-1].date()),
                "close_min": round(float(frames[s]["close"].min()), 4),
                "close_max": round(float(frames[s]["close"].max()), 4),
                "close_median": round(float(frames[s]["close"].median()), 4)}
            for s in TERMS_ALL}
    return {"cal": cal, "rates": rates, "w_me": w_me, "w_qe": w_qe,
            "w_ph": w_ph, "face": face}, None


def month_end_window(cal, last_n, quarter=False):
    """Last n trading days of each Gregorian month (quarter=True: of each
    Gregorian quarter). Exogenous calendar: known at the day's own close."""
    months = cal.astype("datetime64[M]").astype("int32")
    if quarter:
        months = months // 3
    out = np.zeros(len(cal), dtype=bool)
    last_pos = {}
    for i in range(len(cal)):
        last_pos[int(months[i])] = i
    for i in range(len(cal)):
        if last_pos[int(months[i])] - i < last_n:
            out[i] = True
    return out


def pre_longholiday_window(cal, last_n):
    """Last n trading days before each calendar gap >= GAP_MIN_DAYS
    natural days. Zero look-ahead: the window day itself has traded; the
    gap is the absence of a next bar (known by the next session, never
    needed before the window day's own close decision)."""
    out = np.zeros(len(cal), dtype=bool)
    for i in range(len(cal) - 1):
        gap = _d(cal[i + 1]) - _d(cal[i])
        if gap >= GAP_MIN_DAYS:
            for j in range(max(0, i - last_n + 1), i + 1):
                out[j] = True
    return out


# ------------------------------------------------------------------ engine
def swing_engine(cal, r_gc001, term_rate, win_mask, term_days):
    """Deterministic daily-accrual swing state machine (prereg s3 frozen).

    Decisions at trading-day closes. Overnight decided at d accrues
    r_gc001[d]/365 on the single natural day d+1 (daily roll). A term
    decided at d locks term_rate[d]/365 on each natural day d+1..d+k;
    while the term runs no decision happens (no early redemption); after
    it matures the first trading day strictly after the maturity
    re-decides. Overnight maturity = d+1: the next trading decision at the
    first trading day >= d+1 (daily roll law, 每日滚隔夜).

    Returns (per-natural-day accrual array over [cal[0]+1, cal[-1]],
    episode list [(start_idx, end_idx, per_day_rate), ...]).
    """
    day0 = _d(cal[0]) + 1
    dayn = _d(cal[-1])
    n_out = dayn - day0 + 1
    out = np.zeros(n_out)
    episodes = []
    # active term position: (per_day_rate, maturity_day); None = free
    pos = None
    for i in range(len(cal)):
        di = _d(cal[i])
        if pos is not None and di <= pos[1]:
            continue                       # term still running
        if di + 1 > dayn:
            break                          # accrual would start past cutoff
        if win_mask[i]:
            rate = r_gc001[i] / 365.0
            lo, hi = di + 1, di + 1
            pos = None                     # overnight: free next session
        else:
            rate = term_rate[i] / 365.0
            lo, hi = di + 1, di + term_days
            pos = (rate, hi)
        hi_c = min(hi, dayn)
        out[lo - day0:hi_c - day0 + 1] = rate
        episodes.append((lo - day0, hi_c - day0, rate))
    return out, episodes


def sharpe_of(series):
    r = np.asarray(series, dtype=float)
    sd = r.std(ddof=1)
    return float(r.mean() / sd * math.sqrt(PBP)) if sd > 0 else 0.0


def cum_ret(series, lo, hi):
    """Window cumulative return over natural-day indices [lo, hi)."""
    seg = np.asarray(series[lo:hi], dtype=float)
    return float(np.prod(1.0 + seg) - 1.0)


# ------------------------------------------------------------------ cells
CELLS = [
    {"name": "CAL-SWITCH-GC007", "term": "GC007", "days": 7, "win": "me_ph"},
    {"name": "CAL-SWITCH-GC014", "term": "GC014", "days": 14, "win": "me_ph"},
    {"name": "QW5-SWITCH-GC014", "term": "GC014", "days": 14, "win": "qe_ph"},
    {"name": "CAL-SWITCH-GC028", "term": "GC028", "days": 28, "win": "me_ph"},
]


def cell_window(P, cell):
    if cell["win"] == "me_ph":
        return P["w_me"] | P["w_ph"]
    return P["w_qe"] | P["w_ph"]


def run_cell(P, cell):
    win = cell_window(P, cell)
    ser, eps = swing_engine(P["cal"], P["rates"]["GC001"],
                           P["rates"][cell["term"]], win, cell["days"])
    return ser, eps, win


def passive_roll(P):
    """PASSIVE-GC001-ROLL: overnight roll at every trading day (win mask
    all-True forces the overnight branch every decision)."""
    allwin = np.ones(len(P["cal"]), dtype=bool)
    ser, eps = swing_engine(P["cal"], P["rates"]["GC001"],
                            P["rates"]["GC001"], allwin, 1)
    return ser, eps


def episode_kpi(passive_ser, ser, eps):
    """Win rate + mean episode edge vs passive over the same days (O-1524
    KPI dual-disclosure law). Episode = one locked position span."""
    wins, edges = 0, []
    for lo, hi, _rate in eps:
        e_cum = float(np.prod(1.0 + np.asarray(ser[lo:hi + 1])) - 1.0)
        p_cum = float(np.prod(1.0 + np.asarray(
            passive_ser[lo:hi + 1])) - 1.0)
        if np.isfinite(e_cum) and np.isfinite(p_cum):
            wins += int(e_cum > p_cum)
            edges.append(e_cum - p_cum)
    n_ep = len(edges)
    return {"n_episodes": n_ep,
            "win_rate_vs_passive_same_days": round(wins / n_ep, 4)
            if n_ep else None,
            "mean_episode_edge": round(float(np.mean(edges)), 8)
            if edges else None}


# ------------------------------------------------------------------ nulls
def _null_one(P, win_mask_true, rng):
    """One random-calendar-swing null draw: preserve the window-day count
    per Gregorian year, shuffle positions (swing strength preserved,
    calendar structure destroyed); CAL-SWITCH-GC007 machinery."""
    cal = P["cal"]
    n = len(cal)
    years = (cal.astype("datetime64[Y]").astype("int32") + 1970)
    pmask = np.zeros(n, dtype=bool)
    for y in np.unique(years):
        pos_y = np.flatnonzero(years == y)
        cnt = int(win_mask_true[pos_y].sum())
        if cnt <= 0:
            continue
        pick = rng.choice(pos_y, size=cnt, replace=False)
        pmask[pick] = True
    ser, _ = swing_engine(cal, P["rates"]["GC001"], P["rates"]["GC007"],
                          pmask, 7)
    return ser


def run_nulls(P, win_mask_true):
    os.makedirs(NULL_DIR, exist_ok=True)
    per = K_NULLS // NULL_SHARDS
    vals = np.empty(K_NULLS)
    for s in range(NULL_SHARDS):
        path = os.path.join(NULL_DIR, f"calnull_shard{s}.npy")
        if os.path.exists(path):
            vals[s * per:(s + 1) * per] = np.load(path)
            continue
        chunk = np.empty(per)
        for i in range(per):
            k = s * per + i
            chunk[i] = sharpe_of(_null_one(P, win_mask_true,
                                           np.random.default_rng([SEED, k])))
        np.save(path, chunk)
        vals[s * per:(s + 1) * per] = chunk
    cov = {"mu": round(float(vals.mean()), 4),
           "sigma": round(float(vals.std(ddof=1)), 4),
           "n_values": int(len(vals))}
    return {"values": [round(float(v), 4) for v in vals],
            "coverage": cov,
            "face": "random calendar permutation of the CAL-union window "
                    "(per-year count preserved, structure destroyed); "
                    "CAL-SWITCH-GC007 machinery"}


# ------------------------------------------------- starts / splits / tails
def virtual_starts(series_by_face, k_start_seed=None):
    """K=1000 random virtual starts x 3 windows (law s1), beat = cell
    window cum ret > passive window cum ret. Draw stream: one rng per k
    (shared across windows -- each window re-derives lo from its own rng
    call with the SAME [SEED, 2000+k] seed = per-window identical start
    position, windows nested: honest overlap disclosed)."""
    ks = k_start_seed if k_start_seed is not None else K_STARTS
    out = {"n_starts": ks, "windows_days": WIN_DAYS, "cells": {}}
    passive = np.asarray(series_by_face["PASSIVE-GC001-ROLL"], dtype=float)
    n = len(passive)
    wmax = max(WIN_DAYS.values())
    los = []
    for k in range(ks):
        rng = np.random.default_rng([SEED, 2000 + k])
        los.append(int(rng.integers(0, n - wmax)))
    for name, ser in series_by_face.items():
        if name == "PASSIVE-GC001-ROLL":
            continue
        s = np.asarray(ser, dtype=float)
        wins = {}
        for wname, w in WIN_DAYS.items():
            hits = 0
            for k in range(ks):
                lo = los[k]
                hits += int(cum_ret(s, lo, lo + w) > cum_ret(passive,
                                                             lo, lo + w))
            wins[wname] = {"beats": hits, "beat_rate": round(hits / ks, 4)}
        out["cells"][name] = wins
    return out


def split_windows(series_by_face, k_splits=None):
    """100 random split windows (law s3): random split point in [0.2n,
    0.8n] of the natural-day series; half-window Sharpe same-sign rate
    >= 80% = segment-stable."""
    ks = k_splits if k_splits is not None else K_SPLITS
    out = {}
    for name, ser in series_by_face.items():
        r = np.asarray(ser, dtype=float)
        n = len(r)
        agree = 0
        for k in range(ks):
            rng = np.random.default_rng([SEED, 3000 + k])
            cut = int(rng.integers(int(0.2 * n), int(0.8 * n)))
            a, b = sharpe_of(r[:cut]), sharpe_of(r[cut:])
            agree += int((a > 0) == (b > 0))
        rate = agree / ks
        out[name] = {"same_sign_rate": round(rate, 4),
                     "segment_stable": bool(rate >= 0.80),
                     "n_splits": ks}
    return out


def extreme_tail(ser, cal, top_n=10):
    """Positive-tail single-day accrual disclosure (per-day accrual x 365
    = annualized %). Interest upside = favorable tail (distribution-bound
    reading, not naked max)."""
    r = np.asarray(ser, dtype=float) * 365.0
    order = np.argsort(r)[::-1][:top_n]
    day0 = _d(cal[0]) + 1
    rows = []
    for i in order:
        rows.append({"day": str(np.datetime64("1970-01-01", "D")
                                + np.timedelta64(int(day0 + i), "D")),
                     "annualized_accrual_pct": round(float(r[i]) * 100, 3)})
    return rows


# ------------------------------------------------------------------ d6
MR_LOADER = None        # member-returns loader (run: cn_rev_tilt reuse)


def _default_mr_loader():
    from cn_rev_tilt_p1 import load_member_rets, _corr, REG6
    rets, _cuts = load_member_rets()
    return rets, _corr, list(REG6)


def d6_block(P, series_by_cell):
    loader = MR_LOADER or _default_mr_loader
    member_rets, corr_fn, reg6 = loader()
    day0 = _d(P["cal"][0]) + 1
    n_out = len(next(iter(series_by_cell.values())))
    idx = pd.DatetimeIndex([
        np.datetime64("1970-01-01", "D") + np.timedelta64(int(day0 + i), "D")
        for i in range(n_out)])
    out = {"reject_line": D6_REJECT, "members": reg6, "cells": {}}
    for name, ser in series_by_cell.items():
        s = pd.Series(np.asarray(ser, dtype=float), index=idx)
        per = {}
        for tid, mr in member_rets.items():
            v, ov = corr_fn(s, mr)
            per[tid] = {"corr": v, "overlap_days": ov}
        fin = {t: v["corr"] for t, v in per.items() if v["corr"] is not None}
        amax = max(fin, key=lambda t: abs(fin[t])) if fin else None
        out["cells"][name] = {"per_member": per,
                              "max_abs_corr_member": round(abs(fin[amax]), 4)
                              if amax else None,
                              "reject": bool(amax and
                                             abs(fin[amax]) >= D6_REJECT)}
    names = list(series_by_cell)
    cross = {}
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
    ann_nat = float(eq[-1] ** (365.0 / max(n, 1)) - 1.0)
    return {"sharpe_full": round(sharpe_of(r), 4),
            "ann_ret_natural_day": round(ann_nat, 6),
            "max_dd": round(dd, 6), "n_days": int(n),
            "median_abs_r": round(float(np.median(np.abs(r))), 8)}


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


def phase1_write(P, cells, passive, nulls, vstarts, splits, d6, win_face):
    """Phase-1 product (no gates): the repo_cash passive branch reads THIS
    file -- CTA_P1 phase-1-write-first precedent."""
    os.makedirs(OUT_DIR, exist_ok=True)
    pas_stats = _cell_stats(passive)
    pas_stats["sharpe"] = pas_stats["sharpe_full"]   # branch-face alias
    product = {
        "batch": BATCH_NAME,
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "cutoff_meta": SG.cutoff_meta(EVIDENCE_CUTOFF),
        "prereg": "research/INNOVATION_QUOTA_W1_PREREG.md (@dd62920e freeze)",
        "seed": {"base": SEED, "k_nulls": K_NULLS},
        "panel": P["face"],
        "calendar_gates": {"month_end_last2": CAL_MONTH_END,
                           "quarter_end_last5": CAL_QUARTER_END,
                           "pre_longholiday_last2": CAL_PREHOL,
                           "gap_min_days": GAP_MIN_DAYS},
        "cost_face": "zero transaction cost (pre-fee basis, prereg s3 "
                     "disclosed; fee-after re-check carries at the paper "
                     "face if a cell ever registers)",
        "engine_law": "daily decisions at trading-day closes; overnight = "
                      "single natural day d+1 accrual (daily roll); term = "
                      "k natural days locked; re-decide at first trading "
                      "day strictly after term maturity; no early "
                      "redemption",
        "windows": win_face,
        "passive": {"passive_gc001_roll": {"full": pas_stats}},
        "cells": {n: _cell_stats(cells[n]["ser"]) for n in cells},
        "nulls": nulls, "virtual_starts": vstarts, "splits": splits,
        "d6": d6,
        "extreme_day_tail": {n: extreme_tail(cells[n]["ser"], P["cal"])
                             for n in cells},
        "extreme_day_priors": EXTREME_PRIORS,
        "funnel": {"harvest_column": 1,
                   "harvest_note": "in-repo untried face scan (repo panel "
                                   "zero prereg lineage, r180 probe facts)",
                   "gate_column": "0/4 pending judgment (this batch)"},
    }
    with open(OUT_JSON + ".tmp", "w", encoding="utf-8") as fh:
        json.dump(product, fh, ensure_ascii=False, indent=1)
    os.replace(OUT_JSON + ".tmp", OUT_JSON)
    return product


def finalize(product, P, cells, passive):
    prev_total = None
    if os.path.exists(OUT_JSON):
        try:
            with open(OUT_JSON, encoding="utf-8") as fh:
                old = json.load(fh)
            prev_total = (old.get("trials_ledger") or {}).get("prev_total")
        except Exception:
            prev_total = None
    gates = {}
    for name in cells:
        ser = np.asarray(cells[name]["ser"], dtype=float)
        st = _cell_stats(ser)
        g1 = SG.g1_prime_v2(st["sharpe_full"], ser,
                            batch_cells=BATCH_CELLS, pool="repo_cash",
                            results_dir=OUT_DIR_RESULTS,
                            null_pool={"values": product["nulls"]["values"],
                                       "coverage":
                                           product["nulls"]["coverage"]},
                            n_trades=cells[name]["n_episodes"],
                            n_entries=cells[name]["n_episodes"])
        dsr = SG.deflated_sharpe_ratio(ser,
                                       n_trials=g1["skill_line"]["n_eff"])
        gates[name] = {"g1_prime_v2": g1, "dsr": dsr}
    mat = pd.DataFrame({n: np.asarray(cells[n]["ser"], dtype=float)
                        for n in cells})
    pbo = cscv_pbo(mat)
    for name in gates:
        gates[name]["g2"] = SG.g2_registration_v2(
            gates[name]["g1_prime_v2"]["pass_v2"], gates[name]["dsr"],
            float(pbo["pbo"]))
        gates[name]["d6_reject"] = bool(
            product["d6"]["cells"][name]["reject"])
    ledger = SG.append_ledger(BATCH_NAME, BATCH_CELLS,
                              file_name="results/innovation_quota/"
                                        "REPO-CALENDAR-P1.json",
                              evidence_cutoff=EVIDENCE_CUTOFF,
                              prev_total=prev_total)
    product["gates"] = gates
    product["family_pbo"] = pbo
    product["episode_kpi"] = {n: episode_kpi(passive, cells[n]["ser"],
                                            cells[n]["eps"])
                             for n in cells}
    product["trials_ledger"] = ledger
    product["judgment_note"] = ("judged per prereg s4 via shared library; "
                                "judged-negative family = slot closed + "
                                "new-evidence reopen note (law s5); "
                                "G2-eligible cell = STRATEGY_LIBRARY "
                                "cash-leg sleeve candidate, intake walks "
                                "the CE admission face separately")
    with open(OUT_JSON + ".tmp", "w", encoding="utf-8") as fh:
        json.dump(product, fh, ensure_ascii=False, indent=1)
    os.replace(OUT_JSON + ".tmp", OUT_JSON)
    _attr_row(BATCH_NAME, BATCH_CELLS, int(ledger["total"]),
              {"g1_pass": {n: gates[n]["g1_prime_v2"]["pass_v2"]
                           for n in gates},
               "g2_eligible": {n: gates[n]["g2"]["eligible_v2"]
                               for n in gates},
               "family_pbo": pbo},
              {"episodes": {n: cells[n]["n_episodes"] for n in cells}})
    return product


# ------------------------------------------------------------------ driver
def cmd_run():
    global SEED
    SEED = SG.SEED_REGISTRY["innovation_quota_w1_repo"]
    t0 = time.time()
    P, err = load_repo_panel()
    if err:
        return gate_refuse(err)
    print(f"panel ok: 11 terms, GC001 {P['face']['GC001']['rows']} rows, "
          f"calendar {CAL_MONTH_END}/{CAL_QUARTER_END}/{CAL_PREHOL} "
          f"({time.time() - t0:.0f}s)", flush=True)
    passive, _p_eps = passive_roll(P)
    cells = {}
    for cell in CELLS:
        ser, eps, win = run_cell(P, cell)
        cells[cell["name"]] = {"ser": ser, "eps": eps, "n_episodes": len(eps)}
        print(f"  cell {cell['name']}: sharpe={sharpe_of(ser):.4f} "
              f"episodes={len(eps)} ({time.time() - t0:.0f}s)", flush=True)
    win_true = cell_window(P, CELLS[0])
    nulls = run_nulls(P, win_true)
    print(f"nulls: mu={nulls['coverage']['mu']} "
          f"sigma={nulls['coverage']['sigma']} "
          f"({time.time() - t0:.0f}s)", flush=True)
    series_by_face = {**{n: cells[n]["ser"] for n in cells},
                      "PASSIVE-GC001-ROLL": passive}
    vstarts = virtual_starts(series_by_face)
    splits = split_windows(series_by_face)
    d6 = d6_block(P, {n: cells[n]["ser"] for n in cells})
    win_face = {"cal_union_days": int(win_true.sum()),
                "qe_ph_union_days": int(cell_window(P, CELLS[2]).sum())}
    product = phase1_write(P, cells, passive, nulls, vstarts, splits, d6,
                           win_face)
    print(f"phase-1 product written ({time.time() - t0:.0f}s)", flush=True)
    product = finalize(product, P, cells, passive)
    print(f"finalize ok: cells={len(cells)} "
          f"ledger={product['trials_ledger']['total']} "
          f"elapsed={time.time() - t0:.0f}s")
    return 0


# ------------------------------------------------------------------ selftest
def _mk_repo_fixture(tmp):
    """Synthetic 11-term repo panel with planted structure: month-end
    rate elevation, a planted long gap in even-numbered Junes."""
    global PANEL_DIR
    PANEL_DIR = os.path.join(tmp, "repo_daily")
    os.makedirs(PANEL_DIR, exist_ok=True)
    dates = pd.bdate_range("2013-01-02", end="2026-09-22")
    rows = []
    for d in dates:
        nxt = d + pd.offsets.BDay(1)
        month_tail = (nxt.month != d.month)
        base = 2.0 + (2.0 if month_tail else 0.0)
        rows.append((d, base))
    df = pd.DataFrame(rows, columns=["date", "close"])
    # planted longholiday gaps: drop the 2nd and 3rd week of June in even
    # years -> gap >= 4 natural days around them
    mask_drop = ((df["date"].dt.month == 6) & (df["date"].dt.day >= 10)
                 & (df["date"].dt.day <= 21)
                 & (df["date"].dt.year % 2 == 0))
    df = df[~mask_drop].reset_index(drop=True)
    # term premium: small monotone spread per term
    for i, term in enumerate(TERMS_ALL):
        out = pd.DataFrame({
            "date": df["date"],
            "open": df["close"] + 0.01 * i,
            "high": df["close"] + 0.02 + 0.01 * i,
            "low": df["close"] - 0.05 - 0.01 * i,
            "close": df["close"] + 0.10 * i,
            "volume": 1000.0 + i,
        })
        out.to_csv(os.path.join(PANEL_DIR, f"{term}.csv"), index=False)
    return df


def cmd_selftest():
    global OUT_DIR, NULL_DIR, OUT_JSON, OUT_DIR_RESULTS, ATT_JSON, SEED, \
        K_NULLS, NULL_SHARDS, K_STARTS, K_SPLITS, CAL_MONTH_END, \
        CAL_QUARTER_END, CAL_PREHOL, GC001_ROWS, MR_LOADER
    tmp = tempfile.mkdtemp(prefix="innovation_quota_selftest_")
    K_NULLS, NULL_SHARDS = 40, 2
    K_STARTS, K_SPLITS = 20, 10
    SEED = 20295000

    def _stub_corr(a, b, min_overlap=20):
        j = pd.concat([a, b], axis=1, join="inner").dropna()
        if len(j) < min_overlap:
            return None, int(len(j))
        v = float(np.corrcoef(j.iloc[:, 0], j.iloc[:, 1])[0, 1])
        return round(v, 4), int(len(j))

    MR_LOADER = (lambda: (
        {"M1": pd.Series(np.sin(np.arange(500) / 25.0) * 0.001,
                         index=pd.bdate_range("2020-01-01", periods=500))},
        _stub_corr, ["M1"]))
    ok = []
    try:
        df = _mk_repo_fixture(tmp)
        OUT_DIR = os.path.join(tmp, "results", "innovation_quota")
        NULL_DIR = os.path.join(OUT_DIR, "nulls")
        OUT_JSON = os.path.join(OUT_DIR, "REPO-CALENDAR-P1.json")
        OUT_DIR_RESULTS = os.path.dirname(OUT_DIR)   # results root face
        os.makedirs(NULL_DIR, exist_ok=True)
        ATT_JSON = os.path.join(tmp, "attr.json")
        json.dump({"entries": []}, open(ATT_JSON, "w"))

        # derive-then-freeze the calendar gate constants on the fixture
        cut = pd.Timestamp(EVIDENCE_CUTOFF)
        cal = (pd.to_datetime(df["date"][df["date"] <= cut])
               .to_numpy().astype("datetime64[D]"))
        CAL_MONTH_END = int(month_end_window(cal, 2).sum())
        CAL_QUARTER_END = int(month_end_window(cal, 5, quarter=True).sum())
        CAL_PREHOL = int(pre_longholiday_window(cal, 2).sum())
        GC001_ROWS = len(cal)
        w_me = month_end_window(cal, 2)
        w_qe = month_end_window(cal, 5, quarter=True)
        w_ph = pre_longholiday_window(cal, 2)
        # quarter-final month: its month-end last-2 must sit inside the
        # quarter-end last-5 (middle months of a quarter legitimately are
        # not quarter-end days)
        qe_of_me = True
        for i in np.flatnonzero(w_me):
            m = int(pd.Timestamp(cal[i].astype("datetime64[D]")).month)
            if m in (3, 6, 9, 12) and not w_qe[i]:
                qe_of_me = False
        ok.append(("calendar counts positive; q-final month-end in q-end",
                   CAL_MONTH_END > 0 and CAL_QUARTER_END > 0
                   and CAL_PREHOL > 0 and qe_of_me))
        # planted gap check: June even-year drop produces pre-holiday days
        june_ph = w_ph[pd.to_datetime(df["date"][df["date"] <= cut])
                       .dt.month.to_numpy() == 6]
        ok.append(("planted June gaps detected", bool(june_ph.any())))

        P, err = load_repo_panel()
        ok.append(("panel gates pass on fixture", err is None))
        if err:
            raise RuntimeError(err)

        # engine hand-check on a tiny planted calendar
        tiny = np.array(["2026-01-05", "2026-01-06", "2026-01-09"],
                        dtype="datetime64[D]")
        r1 = np.array([2.0, 3.0, 4.0])
        rt = np.array([2.5, 3.5, 4.5])
        ser, eps = swing_engine(tiny, r1, rt,
                                np.array([False, False, False]), 7)
        # d0 (Jan-05) term: locks 2.5% for Jan-06..Jan-12; d1/d2 skipped
        # (term running); series ends at dayn=Jan-09 -> the 4 in-window
        # accrual days each carry 2.5/365 (beyond-cutoff tail clipped,
        # honest)
        ok.append(("term lock math (7-day lock, tail clipped at cutoff)",
                   len(ser) == 4 and np.allclose(ser, 2.5 / 365.0)
                   and len(eps) == 1))
        ser2, _ = swing_engine(tiny, r1, rt,
                               np.array([True, True, True]), 7)
        # all overnight: Jan-05->06, Jan-06->07; d2 (Jan-09) accrual lands
        # Jan-10 > dayn -> dropped; gap days Jan-08 zero
        ok.append(("overnight daily roll single-day accruals",
                   len(ser2) == 4
                   and abs(ser2[0] - 2.0 / 365.0) < 1e-12
                   and abs(ser2[1] - 3.0 / 365.0) < 1e-12
                   and ser2[2] == 0.0 and ser2[3] == 0.0))
        ser3, eps3 = swing_engine(tiny, r1, rt,
                                  np.array([False, True, False]), 1)
        # d0 term 1d (rate 2.5 on Jan-06, index 0); d1 WINDOW day skipped
        # (term running through its maturity, no early redemption --
        # otherwise an overnight there would write 3.0/365 at index 1);
        # d2 accrual Jan-10 falls past the series end (dropped, honest)
        ok.append(("term blocks window day (no early redemption)",
                   len(ser3) == 4 and len(eps3) == 1
                   and abs(ser3[0] - 2.5 / 365.0) < 1e-12
                   and ser3[1] == 0.0 and ser3[2] == 0.0
                   and ser3[3] == 0.0))

        # cells + passive + nulls on the fixture panel
        passive, _ = passive_roll(P)
        cells = {}
        for cell in CELLS:
            ser, eps, win = run_cell(P, cell)
            cells[cell["name"]] = {"ser": ser, "eps": eps,
                                   "n_episodes": len(eps)}
        ok.append(("4 cells + passive derive finite",
                   all(np.isfinite(sharpe_of(cells[c]["ser"]))
                       for c in cells)
                   and np.isfinite(sharpe_of(passive))))
        ok.append(("planted term premium -> GC028 cell beats GC007 cell",
                   sharpe_of(cells["CAL-SWITCH-GC028"]["ser"])
                   > sharpe_of(cells["CAL-SWITCH-GC007"]["ser"])))
        win_true = cell_window(P, CELLS[0])
        n1 = run_nulls(P, win_true)
        n2 = run_nulls(P, win_true)
        ok.append(("nulls deterministic (npy resume) + size",
                   n1["values"] == n2["values"]
                   and len(n1["values"]) == K_NULLS))

        # virtual starts / splits / d6 / phase-1 product
        series_by_face = {**{n: cells[n]["ser"] for n in cells},
                          "PASSIVE-GC001-ROLL": passive}
        vstarts = virtual_starts(series_by_face)
        splits = split_windows(series_by_face)
        d6 = d6_block(P, {n: cells[n]["ser"] for n in cells})
        ok.append(("vstarts/splits/d6 shapes",
                   set(vstarts["cells"]) == set(cells)
                   and all(set(vstarts["cells"][c]) == set(WIN_DAYS)
                           for c in vstarts["cells"])
                   and all("segment_stable" in splits[s] for s in splits)
                   and not d6["cells"]["CAL-SWITCH-GC007"]["reject"]))
        product = phase1_write(P, cells, passive, n1, vstarts, splits, d6,
                               {"cal_union_days": int(win_true.sum()),
                                "qe_ph_union_days":
                                    int(cell_window(P, CELLS[2]).sum())})
        pv = SG.passive_baseline("repo_cash", results_dir=OUT_DIR_RESULTS)
        ok.append(("repo_cash passive branch reads phase-1 product",
                   abs(pv - _cell_stats(passive)["sharpe_full"]) < 1e-9))

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
            product = finalize(product, P, cells, passive)
            ok.append(("finalize product fields",
                       os.path.exists(OUT_JSON)
                       and product["evidence_cutoff"] == EVIDENCE_CUTOFF
                       and "cutoff_meta" in product
                       and len(product["gates"]) == 4
                       and all("g2" in g for g in product["gates"].values())
                       and product["trials_ledger"]["total"] == 100))
            ok.append(("episode kpi face",
                       all("win_rate_vs_passive_same_days"
                           in product["episode_kpi"][n]
                           for n in cells)))
            att = json.load(open(ATT_JSON, encoding="utf-8"))
            ok.append(("attrition row + funnel dual columns",
                       att["entries"][-1]["batch"] == BATCH_NAME
                       and product["funnel"]["harvest_column"] == 1))
        finally:
            SG.n_eff, SG.append_ledger, SG.ledger_head = _ne, _al, _lh
            globals()["cscv_pbo"] = _real_cscv

        # gate-refusal paths (drift -> refuse)
        real_rows = GC001_ROWS
        GC001_ROWS = real_rows + 1
        _, err2 = load_repo_panel()
        ok.append(("G-PANEL drift refusal", err2 is not None
                   and "rows" in str(err2)))
        GC001_ROWS = real_rows
        real_me = CAL_MONTH_END
        CAL_MONTH_END = real_me + 1
        _, err3 = load_repo_panel()
        ok.append(("G-CALENDAR drift refusal", err3 is not None
                   and "month-end" in str(err3)))
        CAL_MONTH_END = real_me
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    n_ok = sum(1 for _, v in ok if v)
    print(f"innovation_quota_w1 selftest: {n_ok}/{len(ok)} PASS")
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
            os.environ.get("INNOVATION_QUOTA_W1_REFINALIZE") != "1":
        print("idempotent no-op: REPO-CALENDAR-P1.json exists "
              "(INNOVATION_QUOTA_W1_REFINALIZE=1 = only redo)")
        return 0
    return cmd_run()


if __name__ == "__main__":
    sys.exit(main())
