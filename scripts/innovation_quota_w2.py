"""INNOVATION_QUOTA_W2 runner -- REPO-CALENDAR-P2 repo calendar long-term
term-swing family extension judged batch (T-2026-09-28-107 sec.4(d),
fill_ladder catalog tranche-2, INNOVATION-QUOTA-SLOT-2).

Laws frozen in research/INNOVATION_QUOTA_W2_PREREG.md @commit e265828a
(r183 bm-c, SEED_REGISTRY['innovation_quota_w2_repo']=20298500 registered
same-commit):

  panel   data/repo_daily/*.csv raw pd.read_csv direct read, 11 terms
          (W1 census), every file D2-truncated to evidence cutoff
          2026-09-22. G-ANCHOR-FACE four-tuples per O-20260928-1712
          (runner probe paths must equal the prereg-declared paths
          bit-for-bit -- one mismatch = face-mismatch VOID, fail-closed
          exit 2, "face mismatch" not "data rot"). Count anchors
          fail-closed: GC001 rows == 3735 (first 2011-05-13), GC091
          rows == 3689, GC182 rows == 3376; judged-domain closes in
          (0, 200) all-finite; outside-cal == 0 (every GC091/GC182 date
          must sit inside the GC001 trading calendar).
  cells   2 judged cells on their OWN windows of the GC001 trading
          calendar (cell window = GC001 calendar truncated to the
          term's own first in-window trading day): CAL-SWITCH-GC091
          (window start 2011-06-16; cal_rows 3712, month-end last-2
          368, pre-longholiday last-2 192, union 454, term-missing 145)
          and CAL-SWITCH-GC182 (window start 2011-09-08; cal_rows 3652,
          month-end last-2 362, pre-longholiday last-2 192, union 448,
          term-missing 281) -- every count anchor fail-closed.
  engine  W1 frozen state machine verbatim (daily decisions at trading-
          day closes; overnight = single natural day d+1 accrual; term
          GC-k decided at d locks close_k(d)/365 on each natural day
          d+1..d+k; re-decide at the first trading day strictly after
          maturity; no early redemption) EXTENDED by the term-missing
          fallback law (this batch's frozen extension): a non-window
          decision day whose term has no settle row that day falls
          back to overnight GC001 (real constraint = the term is not
          obtainable that day; zero fabrication zero ffill; fallback
          day count anchor-disclosed 145/281). Natural days with no
          active position accrue 0. Sharpe annualized at the shared-
          library PERIODS_PER_YEAR (single-source convention).
  passive per cell: PASSIVE-GC001-ROLL re-derived on EACH cell's own
          window calendar (all-win mask forces the overnight branch at
          every decision) -- the two cell windows differ, so the two
          passives differ; g1_prime_v2 receives passive_override
          (per-cell batch-own passive, additive shared-library branch).
  nulls   K=2000 random calendar-swing masks, rng = np.random.default_
          rng([20298500, k]), k < 2000; each mask preserves the union
          window-day count per Gregorian year ON THAT CELL'S OWN window
          calendar (swing strength preserved, calendar structure
          destroyed) and is evaluated on BOTH cell structures -- each
          cell keeps its own 2000-draw null pool (skill_line per-cell
          own mu/sigma) = 4000 null draws total.
  starts  K=1000 virtual starts (k in [2000, 3000), law s1): windows
          6m/12m/24m = 183/365/730 natural days, per-cell start
          positions drawn on that cell's own series length, beat =
          cell window cum return > that cell's passive window cum
          return. 100 random split windows (k in [3000, 3100), law
          s3 >= 100): random split point, half-window Sharpe same-sign
          rate >= 80% = segment-stable.
  gates   G1'v2 per cell via science_gates.g1_prime_v2 (batch_cells=
          4002, pool='repo_cash' domain tag, passive_override = this
          cell's own passive Sharpe, batch-own per-cell null pool);
          DSR via deflated_sharpe_ratio on the raw cell series; family
          PBO via screening/pbo cscv_pbo CSCV-8 over the 2-cell matrix;
          G2 via g2_registration_v2. No hand-copied lines (O-2250).
  d6      vs the registered 6 CE members (core48 equity face via
          cn_rev_tilt_p1.load_member_rets reuse, reject line 0.7,
          cross-asset prior <0.1 disclosed); batch-internal 2-cell
          pairwise |corr| measured and disclosed; vs the P1 registered
          3 eligible cells (CAL-SWITCH-GC014 / QW5-GC014 / CAL-SWITCH-
          GC028, cash-leg sleeve candidate pool, same-family):
          within-family high corr is the expected fact -- disclosed
          pairwise, NOT rejected (sleeve-collapsing semantics: an
          eligible P2 cell joins the SAME cash-leg sleeve candidate
          pool, no independent member claim).
  ledger  append_ledger("REPO_CALENDAR_P2", 4002, "results/
          innovation_quota/REPO-CALENDAR-P2.json", evidence_cutoff=
          "2026-09-22") single-count; gate_attrition measurement row.

Products (prereg s6): results/innovation_quota/REPO-CALENDAR-P2.json
(top evidence_cutoff + cutoff_meta + anchor gates + per-cell passive +
2 cells + per-cell nulls + virtual starts + splits + d6 + extreme-day
tail + funnel dual columns + gates + ledger) + nulls shard npy
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
from screening.pbo import cscv_pbo              # family PBO CSCV-8

PANEL_DIR = os.path.join(ROOT, "data", "repo_daily")
OUT_DIR = os.path.join(ROOT, "results", "innovation_quota")
NULL_DIR = os.path.join(OUT_DIR, "nulls_p2")
OUT_JSON = os.path.join(OUT_DIR, "REPO-CALENDAR-P2.json")
OUT_DIR_RESULTS = os.path.dirname(OUT_DIR)     # results root for shared faces
ATT_JSON = os.path.join(ROOT, "results", "gate_attrition.json")

BATCH_NAME = "REPO_CALENDAR_P2"
BATCH_CELLS = 4002                # 2 judged cells + 4000 null draws (s0)
EVIDENCE_CUTOFF = "2026-09-22"
PBP = SG.PERIODS_PER_YEAR         # gate-chain single-source convention
K_NULLS = 2000                    # per cell (x2 structures = 4000 draws)
NULL_SHARDS = 8
K_STARTS = 1000
K_SPLITS = 100
SEED = None                       # filled from SG.SEED_REGISTRY at run
TERMS_ALL = ["GC001", "GC003", "GC004", "GC007", "GC014", "GC028",
             "GC091", "GC182", "R-001", "R-003", "R-007"]
JUDGED_TERMS = ["GC001", "GC091", "GC182"]
GAP_MIN_DAYS = 4                  # pre-longholiday gap definition (W1 law)
D6_REJECT = 0.7
WIN_DAYS = {"6m": 183, "12m": 365, "24m": 730}   # natural-day windows (law s1)
EXTREME_PRIORS = ["2013-06 money-famine window", "2015-02-10 GC001 53.44",
                  "2015-07 crash-week window days"]

# ---- G-ANCHOR-FACE frozen probe anchors (r183 bm-c, prereg s2) ----------
GC001_ROWS = 3735
GC001_FIRST = "2011-05-13"
GC091_ROWS = 3689
GC182_ROWS = 3376
CELL_ANCHORS = {
    "GC091": {"start": "2011-06-16", "cal_rows": 3712,
              "month_end": 368, "pre_hol": 192, "union": 454,
              "missing": 145, "days": 91},
    "GC182": {"start": "2011-09-08", "cal_rows": 3652,
              "month_end": 362, "pre_hol": 192, "union": 448,
              "missing": 281, "days": 182},
}


def gate_refuse(msg):
    print(f"GATE-REFUSE(exit2): {msg}")
    return 2


def _d(x):
    """datetime64[D] -> int day number helper."""
    return int(x.astype("datetime64[D]").astype("int64"))


# ------------------------------------------------------------------ panel
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
    natural days. Zero look-ahead (W1 law verbatim)."""
    out = np.zeros(len(cal), dtype=bool)
    for i in range(len(cal) - 1):
        gap = _d(cal[i + 1]) - _d(cal[i])
        if gap >= GAP_MIN_DAYS:
            for j in range(max(0, i - last_n + 1), i + 1):
                out[j] = True
    return out


def load_repo_panel():
    """G-ANCHOR-FACE fail-closed battery + full-history panel assembly.

    Returns (panel dict, None) or (None, refusal message). The panel dict
    carries: GC001 full calendar + rates, per-term full-history close
    arrays keyed by date (for term-rate alignment), the census face.
    """
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
    # -- completeness gates (prereg s2 ①②③④): last-row, rows, rate band
    for s in JUDGED_TERMS:
        if str(frames[s]["date"].iloc[-1].date()) != EVIDENCE_CUTOFF:
            return None, (f"G-PANEL {s} last row "
                          f"{frames[s]['date'].iloc[-1].date()} != "
                          f"{EVIDENCE_CUTOFF}")
    if len(frames["GC001"]) != GC001_ROWS:
        return None, f"G-PANEL GC001 rows {len(frames['GC001'])} != {GC001_ROWS}"
    if str(frames["GC001"]["date"].iloc[0].date()) != GC001_FIRST:
        return None, (f"G-PANEL GC001 first row "
                      f"{frames['GC001']['date'].iloc[0].date()} != "
                      f"{GC001_FIRST}")
    if len(frames["GC091"]) != GC091_ROWS:
        return None, f"G-PANEL GC091 rows {len(frames['GC091'])} != {GC091_ROWS}"
    if len(frames["GC182"]) != GC182_ROWS:
        return None, f"G-PANEL GC182 rows {len(frames['GC182'])} != {GC182_ROWS}"
    for s in JUDGED_TERMS:
        c = frames[s]["close"].to_numpy(dtype=float)
        if not (np.isfinite(c).all() and (c > 0).all() and (c < 200).all()):
            return None, f"G-RATE {s} close outside (0, 200)"
    # -- outside-cal gate (prereg s2 ④): every GC091/GC182 date must sit
    #    inside the GC001 trading calendar
    gc001_days = set(_d(x) for x in
                     frames["GC001"]["date"].to_numpy().astype("datetime64[D]"))
    for s in ("GC091", "GC182"):
        bad = [d for d in
               frames[s]["date"].to_numpy().astype("datetime64[D]")
               if _d(d) not in gc001_days]
        if bad:
            return None, (f"outside-cal {s}: {len(bad)} term dates not on "
                          f"the GC001 trading calendar "
                          f"(first {str(bad[0])})")
    rates = {s: frames[s]["close"].to_numpy(dtype=float) for s in TERMS_ALL}
    term_rate_map = {s: {_d(x): float(v) for x, v in
                         zip(frames[s]["date"].to_numpy()
                             .astype("datetime64[D]"),
                             frames[s]["close"].to_numpy(dtype=float))}
                     for s in TERMS_ALL}
    face = {s: {"rows": len(frames[s]),
                "first": str(frames[s]["date"].iloc[0].date()),
                "last": str(frames[s]["date"].iloc[-1].date()),
                "close_min": round(float(frames[s]["close"].min()), 4),
                "close_max": round(float(frames[s]["close"].max()), 4),
                "close_median": round(float(frames[s]["close"].median()), 4)}
            for s in TERMS_ALL}
    return {"cal": frames["GC001"]["date"].to_numpy()
            .astype("datetime64[D]"),
            "rates": rates,
            "term_rate_map": term_rate_map,
            "face": face}, None


# ------------------------------------------------- cell windows + anchors
def build_cell(P, term):
    """Derive one cell's window calendar + fail-closed anchor battery.

    Cell window = the GC001 trading calendar truncated to the term's own
    first in-window trading day (the first GC001-calendar day on which
    the term has a settle row). Window masks are re-derived ON the cell
    window's own calendar (prereg s3). Term rate/validity arrays align
    to the cell window day by day; missing term days carry valid=False
    (fallback law input)."""
    a = CELL_ANCHORS[term]
    cal_full = P["cal"]
    term_map = P["term_rate_map"][term]
    starts = [i for i in range(len(cal_full))
              if _d(cal_full[i]) in term_map]
    if not starts:
        return None, f"{term}: no in-window term settle day on GC001 cal"
    first_idx = starts[0]
    if str(cal_full[first_idx]) != a["start"]:
        return None, (f"G-ANCHOR {term} window start "
                      f"{str(cal_full[first_idx])} != {a['start']}")
    cal = cal_full[first_idx:]
    if len(cal) != a["cal_rows"]:
        return None, (f"G-ANCHOR {term} cal_rows {len(cal)} != "
                      f"{a['cal_rows']}")
    w_me = month_end_window(cal, 2)
    w_ph = pre_longholiday_window(cal, 2)
    win = w_me | w_ph
    n_me, n_ph = int(w_me.sum()), int(w_ph.sum())
    if n_me != a["month_end"]:
        return None, (f"G-ANCHOR {term} month-end {n_me} != "
                      f"{a['month_end']}")
    if n_ph != a["pre_hol"]:
        return None, (f"G-ANCHOR {term} pre-longholiday {n_ph} != "
                      f"{a['pre_hol']}")
    if int(win.sum()) != a["union"]:
        return None, (f"G-ANCHOR {term} union {int(win.sum())} != "
                      f"{a['union']}")
    # term-rate alignment + missing-day census (fallback-law input)
    term_rate = np.full(len(cal), np.nan)
    missing = 0
    for i, dt in enumerate(cal):
        di = _d(dt)
        if di in term_map:
            term_rate[i] = term_map[di]
        else:
            missing += 1
    if missing != a["missing"]:
        return None, (f"G-ANCHOR {term} term-missing {missing} != "
                      f"{a['missing']}")
    r_gc001 = np.array([P["rates"]["GC001"][j] for j in range(first_idx,
                                                              len(cal_full))],
                       dtype=float)
    return {"term": term, "days": a["days"], "cal": cal, "win": win,
            "w_me": w_me, "w_ph": w_ph, "term_rate": term_rate,
            "r_gc001": r_gc001, "missing": missing,
            "start": str(cal[0]), "cal_rows": len(cal)}, None


# ------------------------------------------------------------------ engine
def swing_engine_p2(cal, r_gc001, term_rate, win_mask, term_days):
    """W1 frozen state machine verbatim + term-missing fallback law.

    Decisions at trading-day closes. Overnight (window day, or a
    non-window day whose term has no settle row = fallback) accrues
    r_gc001[d]/365 on the single natural day d+1 and frees the next
    session; a term decided at d locks term_rate[d]/365 on each natural
    day d+1..d+term_days; while the term runs no decision happens (no
    early redemption); after it matures the first trading day strictly
    after the maturity re-decides. Natural days with no active position
    accrue 0.

    Returns (per-natural-day accrual array over [cal[0]+1, cal[-1]],
    episode list, fallback-day count).
    """
    day0 = _d(cal[0]) + 1
    dayn = _d(cal[-1])
    n_out = dayn - day0 + 1
    out = np.zeros(n_out)
    episodes = []
    fallback_days = 0
    pos = None
    for i in range(len(cal)):
        di = _d(cal[i])
        if pos is not None and di <= pos[1]:
            continue                       # term still running
        if di + 1 > dayn:
            break                          # accrual would start past cutoff
        if win_mask[i] or not np.isfinite(term_rate[i]):
            if not win_mask[i]:
                fallback_days += 1         # missing-term fallback (honest)
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
    return out, episodes, fallback_days


def passive_roll_p2(cell):
    """PASSIVE-GC001-ROLL on the cell's own window calendar (all-win
    mask forces the overnight branch at every decision)."""
    allwin = np.ones(len(cell["cal"]), dtype=bool)
    ser, eps, _fb = swing_engine_p2(cell["cal"], cell["r_gc001"],
                                    cell["term_rate"], allwin,
                                    cell["days"])
    return ser, eps


def sharpe_of(series):
    r = np.asarray(series, dtype=float)
    sd = r.std(ddof=1)
    return float(r.mean() / sd * math.sqrt(PBP)) if sd > 0 else 0.0


def cum_ret(series, lo, hi):
    """Window cumulative return over natural-day indices [lo, hi)."""
    seg = np.asarray(series[lo:hi], dtype=float)
    return float(np.prod(1.0 + seg) - 1.0)


def episode_kpi(passive_ser, ser, eps):
    """Win rate + mean episode edge vs passive over the same days
    (O-1524 KPI dual-disclosure law)."""
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
def _null_mask(cal, win_mask_true, rng):
    """One random-calendar-swing mask on this cell's own window calendar:
    preserve the union window-day count per Gregorian year, shuffle
    which trading days are window days (W1 law, per-cell calendar)."""
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
    return pmask


def run_nulls(cell):
    """K=2000-draw per-cell null pool (npy checkpoint resume, shard 8)."""
    os.makedirs(NULL_DIR, exist_ok=True)
    per = K_NULLS // NULL_SHARDS
    vals = np.empty(K_NULLS)
    tag = cell["term"]
    for s in range(NULL_SHARDS):
        path = os.path.join(NULL_DIR, f"calnull_{tag}_shard{s}.npy")
        if os.path.exists(path):
            vals[s * per:(s + 1) * per] = np.load(path)
            continue
        chunk = np.empty(per)
        for i in range(per):
            k = s * per + i
            pmask = _null_mask(cell["cal"], cell["win"],
                               np.random.default_rng([SEED, k]))
            ser, _, _fb = swing_engine_p2(cell["cal"], cell["r_gc001"],
                                          cell["term_rate"], pmask,
                                          cell["days"])
            chunk[i] = sharpe_of(ser)
        np.save(path, chunk)
        vals[s * per:(s + 1) * per] = chunk
    cov = {"mu": round(float(vals.mean()), 4),
           "sigma": round(float(vals.std(ddof=1)), 4),
           "n_values": int(len(vals))}
    return {"values": [round(float(v), 4) for v in vals],
            "coverage": cov,
            "face": f"random calendar permutation of the {tag} cell "
                    f"union window (per-year count preserved, structure "
                    f"destroyed); {tag} cell machinery with term-missing "
                    f"fallback law"}


# ------------------------------------------------ starts / splits / tails
def virtual_starts_cell(cell_ser, passive_ser):
    """K=1000 virtual starts x 3 windows on this cell's own series length
    (law s1), beat = cell window cum ret > this cell's passive window cum
    ret (per-window identical start position, windows nested: honest
    overlap disclosed -- W1 draw-stream law, per-cell lengths)."""
    s = np.asarray(cell_ser, dtype=float)
    p = np.asarray(passive_ser, dtype=float)
    n = len(s)
    wmax = max(WIN_DAYS.values())
    los = [int(np.random.default_rng([SEED, 2000 + k]).integers(0,
                                                                n - wmax))
           for k in range(K_STARTS)]
    wins = {}
    for wname, w in WIN_DAYS.items():
        hits = 0
        for k in range(K_STARTS):
            lo = los[k]
            hits += int(cum_ret(s, lo, lo + w) > cum_ret(p, lo, lo + w))
        wins[wname] = {"beats": hits, "beat_rate": round(hits / K_STARTS, 4)}
    return wins


def split_windows_face(ser, k_splits=None):
    """Random split windows (law s3): split point in [0.2n, 0.8n]; half-
    window Sharpe same-sign rate >= 80% = segment-stable."""
    ks = k_splits if k_splits is not None else K_SPLITS
    r = np.asarray(ser, dtype=float)
    n = len(r)
    agree = 0
    for k in range(ks):
        rng = np.random.default_rng([SEED, 3000 + k])
        cut = int(rng.integers(int(0.2 * n), int(0.8 * n)))
        a, b = sharpe_of(r[:cut]), sharpe_of(r[cut:])
        agree += int((a > 0) == (b > 0))
    rate = agree / ks
    return {"same_sign_rate": round(rate, 4),
            "segment_stable": bool(rate >= 0.80),
            "n_splits": ks}


def extreme_tail(ser, cal, top_n=10):
    """Positive-tail single-day accrual disclosure (annualized %)."""
    r = np.asarray(ser, dtype=float) * 365.0
    order = np.argsort(r)[::-1][:top_n]
    day0 = _d(cal[0]) + 1
    rows = []
    for i in order:
        rows.append({"day": str(np.datetime64("1970-01-01", "D")
                                + np.timedelta64(int(day0 + i), "D")),
                     "annualized_accrual_pct": round(float(r[i]) * 100, 3)})
    return rows


def ser_to_dated(ser, cal):
    """Per-natural-day accrual array -> DatetimeIndex pd.Series (for
    date-aligned cross-face correlation)."""
    day0 = _d(cal[0]) + 1
    idx = pd.DatetimeIndex([
        np.datetime64("1970-01-01", "D") + np.timedelta64(int(day0 + i), "D")
        for i in range(len(ser))])
    return pd.Series(np.asarray(ser, dtype=float), index=idx)


# ------------------------------------------------------------------ d6
MR_LOADER = None            # registered-CE-member returns loader
P1_FAMILY_LOADER = None     # P1 eligible-cell series loader (family corr)


def _default_mr_loader():
    from cn_rev_tilt_p1 import load_member_rets, _corr, REG6
    rets, _cuts = load_member_rets()
    return rets, _corr, list(REG6)


def _default_p1_family_loader():
    """Deterministic re-derivation of the P1 registered 3 eligible cell
    series (cash-leg sleeve candidate pool, same-family corr face) by
    reusing the W1 runner module -- zero reimplementation."""
    import innovation_quota_w1 as W1
    P1, err = W1.load_repo_panel()
    if err:
        raise RuntimeError(f"W1 panel reload refused: {err}")
    out = {}
    for cell in W1.CELLS:
        if cell["name"] not in ("CAL-SWITCH-GC014", "QW5-GC014",
                                "CAL-SWITCH-GC028"):
            continue
        ser, _eps, _win = W1.run_cell(P1, cell)
        out[cell["name"]] = ser_to_dated(ser, P1["cal"])
    if len(out) != 3:
        raise RuntimeError(f"P1 family re-derivation got {len(out)} != 3")
    return out


def _aligned_corr(a, b, min_overlap=20):
    """Date-aligned (join inner) Pearson corr of two dated series."""
    j = pd.concat([a, b], axis=1, join="inner").dropna()
    if len(j) < min_overlap:
        return None, int(len(j))
    v = float(np.corrcoef(j.iloc[:, 0], j.iloc[:, 1])[0, 1])
    return round(v, 4), int(len(j))


def d6_block(cells, passives):
    """D6 disclosure: vs registered CE members (reject line 0.7);
    batch-internal pairwise; vs P1 same-family eligible cells (expected
    high corr -- disclosed, NOT rejected; sleeve-collapsing semantics)."""
    loader = MR_LOADER or _default_mr_loader
    member_rets, corr_fn, reg6 = loader()
    p1_family = (P1_FAMILY_LOADER or _default_p1_family_loader)()
    out = {"reject_line": D6_REJECT, "members": reg6,
           "family_semantics": "within-family high corr is the expected "
                               "fact (same cash-leg sleeve family): "
                               "disclosed pairwise, not rejected; an "
                               "eligible P2 cell joins the SAME cash-leg "
                               "sleeve candidate pool (no independent "
                               "member claim)",
           "cells": {}}
    for name, cell in cells.items():
        s = ser_to_dated(cell["ser"], cell["cal"])
        per = {}
        for tid, mr in member_rets.items():
            v, ov = corr_fn(s, mr)
            per[tid] = {"corr": v, "overlap_days": ov}
        fin = {t: v["corr"] for t, v in per.items() if v["corr"] is not None}
        amax = max(fin, key=lambda t: abs(fin[t])) if fin else None
        fam = {}
        for p1n, p1s in p1_family.items():
            v, ov = _aligned_corr(s, p1s)
            fam[p1n] = {"corr": v, "overlap_days": ov}
        out["cells"][name] = {
            "per_member": per,
            "max_abs_corr_member": round(abs(fin[amax]), 4)
            if amax else None,
            "reject": bool(amax and abs(fin[amax]) >= D6_REJECT),
            "p1_family_pairwise": fam}
    names = list(cells)
    cross = {}
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a = ser_to_dated(cells[names[i]]["ser"], cells[names[i]]["cal"])
            b = ser_to_dated(cells[names[j]]["ser"],
                             cells[names[j]]["cal"])
            v, ov = _aligned_corr(a, b)
            cross[f"{names[i]}|{names[j]}"] = {"corr": v,
                                              "overlap_days": ov}
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


def phase1_write(P, cells, passives, nulls, vstarts, splits, d6):
    """Phase-1 product (no gates): per-cell passives live HERE (the two
    cell windows differ, so two distinct PASSIVE-GC001-ROLL re-derivations
    are disclosed side by side)."""
    os.makedirs(OUT_DIR, exist_ok=True)
    anchor_face = {}
    for name, cell in cells.items():
        a = CELL_ANCHORS[cell["term"]]
        anchor_face[name] = {"term": cell["term"],
                             "window_start": a["start"],
                             "cal_rows": a["cal_rows"],
                             "month_end_last2": a["month_end"],
                             "pre_longholiday_last2": a["pre_hol"],
                             "union_days": a["union"],
                             "term_missing_days": a["missing"],
                             "derived_missing_days": cell["missing"],
                             "fallback_days_triggered":
                                 cell["fallback_days"],
                             "k_natural_days": a["days"]}
    product = {
        "batch": BATCH_NAME,
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "cutoff_meta": SG.cutoff_meta(EVIDENCE_CUTOFF),
        "prereg": "research/INNOVATION_QUOTA_W2_PREREG.md (@e265828a freeze)",
        "seed": {"base": SEED, "k_nulls_per_cell": K_NULLS,
                 "null_draws_total": K_NULLS * len(cells)},
        "panel": P["face"],
        "anchor_gates": anchor_face,
        "cost_face": "zero transaction cost (pre-fee basis, prereg s3 "
                     "disclosed; fee-after recheck = frozen intake "
                     "precondition, T-112 precedent, b*>=1bp line)",
        "engine_law": "W1 frozen state machine verbatim (daily decisions "
                      "at trading-day closes; overnight = single natural "
                      "day d+1 accrual; term = k natural days locked; "
                      "re-decide at first trading day strictly after "
                      "maturity; no early redemption) + term-missing "
                      "fallback law: non-window decision day with no "
                      "term settle row falls back to overnight GC001 "
                      "(zero fabrication zero ffill, count anchor-"
                      "disclosed)",
        "passive": {f"PASSIVE-GC001-ROLL@{name}":
                    {"full": _cell_stats(passives[name])}
                    for name in cells},
        "cells": {n: _cell_stats(cells[n]["ser"]) for n in cells},
        "nulls": nulls,
        "virtual_starts": vstarts,
        "splits": splits,
        "d6": d6,
        "extreme_day_tail": {n: extreme_tail(cells[n]["ser"],
                                             cells[n]["cal"])
                             for n in cells},
        "extreme_day_priors": EXTREME_PRIORS,
        "funnel": {"harvest_column": 1,
                   "harvest_note": "in-repo untried face scan (P1 "
                                   "batch-internal new fact: term-"
                                   "premium needs enough lock days)",
                   "gate_column": f"0/{len(cells)} pending judgment "
                                  "(this batch)"},
    }
    with open(OUT_JSON + ".tmp", "w", encoding="utf-8") as fh:
        json.dump(product, fh, ensure_ascii=False, indent=1)
    os.replace(OUT_JSON + ".tmp", OUT_JSON)
    return product


def finalize(product, cells, passives, nulls):
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
        pas_sharpe = _cell_stats(passives[name])["sharpe_full"]
        g1 = SG.g1_prime_v2(st["sharpe_full"], ser,
                            batch_cells=BATCH_CELLS, pool="repo_cash",
                            results_dir=OUT_DIR_RESULTS,
                            null_pool={"values":
                                       nulls[name]["values"],
                                       "coverage":
                                           nulls[name]["coverage"]},
                            n_trades=cells[name]["n_episodes"],
                            n_entries=cells[name]["n_episodes"],
                            passive_override=pas_sharpe)
        dsr = SG.deflated_sharpe_ratio(ser,
                                       n_trials=g1["skill_line"]["n_eff"])
        gates[name] = {"g1_prime_v2": g1, "dsr": dsr,
                       "passive_override": pas_sharpe}
    # family PBO over the 2-cell matrix -- the two cell windows differ,
    # so the CSCV matrix is date-aligned (join inner) on the natural-day
    # calendars; the aligned span is disclosed inside pbo["pbo"] product
    dated = {n: ser_to_dated(cells[n]["ser"], cells[n]["cal"])
             for n in cells}
    mat = pd.concat(dated, axis=1, join="inner").dropna()
    pbo = cscv_pbo(mat)
    for name in gates:
        gates[name]["g2"] = SG.g2_registration_v2(
            gates[name]["g1_prime_v2"]["pass_v2"], gates[name]["dsr"],
            float(pbo["pbo"]))
        gates[name]["d6_reject"] = bool(
            product["d6"]["cells"][name]["reject"])
    ledger = SG.append_ledger(BATCH_NAME, BATCH_CELLS,
                              file_name="results/innovation_quota/"
                                        "REPO-CALENDAR-P2.json",
                              evidence_cutoff=EVIDENCE_CUTOFF,
                              prev_total=prev_total)
    product["gates"] = gates
    product["family_pbo"] = pbo
    product["episode_kpi"] = {
        n: episode_kpi(passives[n], cells[n]["ser"], cells[n]["eps"])
        for n in cells}
    product["trials_ledger"] = ledger
    product["judgment_note"] = ("judged per prereg s4 via shared library; "
                                "judged-negative family = slot closed + "
                                "new-evidence reopen note (law s5); "
                                "G2-eligible cell = joins the SAME "
                                "cash-leg sleeve candidate pool "
                                "(within-family sleeve collapsing, no "
                                "independent member claim) and the "
                                "fee-after recheck is the frozen intake "
                                "precondition (T-112 precedent)")
    with open(OUT_JSON + ".tmp", "w", encoding="utf-8") as fh:
        json.dump(product, fh, ensure_ascii=False, indent=1)
    os.replace(OUT_JSON + ".tmp", OUT_JSON)
    _attr_row(BATCH_NAME, BATCH_CELLS, int(ledger["total"]),
              {"g1_pass": {n: gates[n]["g1_prime_v2"]["pass_v2"]
                           for n in gates},
               "g2_eligible": {n: gates[n]["g2"]["eligible_v2"]
                               for n in gates},
               "family_pbo": pbo},
              {"episodes": {n: cells[n]["n_episodes"] for n in cells},
               "fallback_days": {n: cells[n]["fallback_days"]
                                 for n in cells}})
    return product


# ------------------------------------------------------------------ driver
CELL_TERMS = ["GC091", "GC182"]


def cmd_run():
    global SEED
    SEED = SG.SEED_REGISTRY["innovation_quota_w2_repo"]
    t0 = time.time()
    P, err = load_repo_panel()
    if err:
        return gate_refuse(err)
    print(f"panel ok: 11 terms, GC001 {P['face']['GC001']['rows']} rows "
          f"({time.time() - t0:.0f}s)", flush=True)
    cells, passives = {}, {}
    for term in CELL_TERMS:
        cell, cerr = build_cell(P, term)
        if cerr:
            return gate_refuse(cerr)
        ser, eps, fb = swing_engine_p2(cell["cal"], cell["r_gc001"],
                                       cell["term_rate"], cell["win"],
                                       cell["days"])
        cell["ser"], cell["eps"] = ser, eps
        cell["n_episodes"] = len(eps)
        cell["fallback_days"] = fb
        pser, _peps = passive_roll_p2(cell)
        cells[f"CAL-SWITCH-{term}"] = cell
        passives[f"CAL-SWITCH-{term}"] = pser
        print(f"  cell CAL-SWITCH-{term}: window {cell['start']} "
              f"cal_rows={cell['cal_rows']} missing={cell['missing']} "
              f"fallback={fb} sharpe={sharpe_of(ser):.4f} "
              f"episodes={len(eps)} ({time.time() - t0:.0f}s)", flush=True)
    nulls = {}
    for name, cell in cells.items():
        nulls[name] = run_nulls(cell)
        print(f"nulls[{name}]: mu={nulls[name]['coverage']['mu']} "
              f"sigma={nulls[name]['coverage']['sigma']} "
              f"({time.time() - t0:.0f}s)", flush=True)
    vstarts = {n: virtual_starts_cell(cells[n]["ser"], passives[n])
               for n in cells}
    splits = {}
    for n in cells:
        splits[n] = split_windows_face(cells[n]["ser"])
        splits[f"PASSIVE-GC001-ROLL@{n}"] = split_windows_face(passives[n])
    d6 = d6_block(cells, passives)
    product = phase1_write(P, cells, passives, nulls, vstarts, splits, d6)
    print(f"phase-1 product written ({time.time() - t0:.0f}s)", flush=True)
    product = finalize(product, cells, passives, nulls)
    print(f"finalize ok: cells={len(cells)} "
          f"ledger={product['trials_ledger']['total']} "
          f"elapsed={time.time() - t0:.0f}s")
    return 0


# ------------------------------------------------------------------ selftest
def _mk_repo_fixture(tmp):
    """Synthetic 11-term repo panel: W1 planted structure (month-end
    elevation, even-June long gaps) + P2 needs -- GC091/GC182 begin
    later than GC001, carry planted missing days (fallback-law input),
    and never leave the GC001 calendar."""
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
    mask_drop = ((df["date"].dt.month == 6) & (df["date"].dt.day >= 10)
                 & (df["date"].dt.day <= 21)
                 & (df["date"].dt.year % 2 == 0))
    df = df[~mask_drop].reset_index(drop=True)
    for i, term in enumerate(TERMS_ALL):
        out = pd.DataFrame({
            "date": df["date"],
            "open": df["close"] + 0.01 * i,
            "high": df["close"] + 0.02 + 0.01 * i,
            "low": df["close"] - 0.05 - 0.01 * i,
            "close": df["close"] + 0.10 * i,
            "volume": 1000.0 + i,
        })
        if term in ("GC091", "GC182"):
            # long terms begin later (planted window starts) and miss
            # settle days (planted fallback-law input): deterministic
            # January-morning holes (never window days: the only planted
            # gaps sit in June, so January days are term-branch days)
            # + scattered random holes; every kept row stays ON the
            # GC001 calendar by construction
            d0 = out["date"].to_numpy().astype("datetime64[D]")
            start = np.datetime64("2013-03-01" if term == "GC091"
                                   else "2013-04-01", "D")
            keep = d0 >= start
            drop_rng = np.random.default_rng(
                [7, 91 if term == "GC091" else 182])
            drop_pick = drop_rng.random(len(out)) < 0.05
            jan_hole = out["date"].dt.month.eq(1) & \
                out["date"].dt.day.le(15)
            out = out[keep & ~drop_pick & ~jan_hole].reset_index(drop=True)
        out.to_csv(os.path.join(PANEL_DIR, f"{term}.csv"), index=False)
    return df


def cmd_selftest():
    global OUT_DIR, NULL_DIR, OUT_JSON, OUT_DIR_RESULTS, ATT_JSON, SEED, \
        K_NULLS, NULL_SHARDS, K_STARTS, K_SPLITS, MR_LOADER, \
        P1_FAMILY_LOADER, CELL_ANCHORS, GC001_ROWS, GC001_FIRST, \
        GC091_ROWS, GC182_ROWS
    tmp = tempfile.mkdtemp(prefix="innovation_quota_w2_selftest_")
    K_NULLS, NULL_SHARDS = 40, 2
    K_STARTS, K_SPLITS = 20, 10
    SEED = 20298500

    def _stub_corr(a, b, min_overlap=20):
        return _aligned_corr(a, b, min_overlap)

    MR_LOADER = (lambda: (
        {"M1": pd.Series(np.sin(np.arange(500) / 25.0) * 0.001,
                         index=pd.bdate_range("2020-01-01", periods=500))},
        _stub_corr, ["M1"]))
    P1_FAMILY_LOADER = (lambda: {
        "CAL-SWITCH-GC014": pd.Series(
            np.sin(np.arange(400) / 30.0) * 0.002,
            index=pd.bdate_range("2020-01-01", periods=400)),
        "QW5-GC014": pd.Series(
            np.cos(np.arange(400) / 30.0) * 0.002,
            index=pd.bdate_range("2020-01-01", periods=400)),
        "CAL-SWITCH-GC028": pd.Series(
            np.sin(np.arange(400) / 45.0) * 0.002,
            index=pd.bdate_range("2020-01-01", periods=400))})
    ok = []
    try:
        df = _mk_repo_fixture(tmp)
        OUT_DIR = os.path.join(tmp, "results", "innovation_quota")
        NULL_DIR = os.path.join(OUT_DIR, "nulls_p2")
        OUT_JSON = os.path.join(OUT_DIR, "REPO-CALENDAR-P2.json")
        OUT_DIR_RESULTS = os.path.dirname(OUT_DIR)
        os.makedirs(NULL_DIR, exist_ok=True)
        ATT_JSON = os.path.join(tmp, "attr.json")
        json.dump({"entries": []}, open(ATT_JSON, "w"))

        # ---- derive-then-freeze all anchors on the fixture
        cut = pd.Timestamp(EVIDENCE_CUTOFF)
        cal_full = (pd.to_datetime(df["date"][df["date"] <= cut])
                    .to_numpy().astype("datetime64[D]"))
        GC001_ROWS = len(cal_full)
        GC001_FIRST = str(cal_full[0])
        g91 = pd.read_csv(os.path.join(PANEL_DIR, "GC091.csv"))
        g182 = pd.read_csv(os.path.join(PANEL_DIR, "GC182.csv"))
        GC091_ROWS = len(g91)
        GC182_ROWS = len(g182)
        CELL_ANCHORS = {}
        for term, gdf in (("GC091", g91), ("GC182", g182)):
            td = {_d(x) for x in pd.to_datetime(gdf["date"])
                  .to_numpy().astype("datetime64[D]")}
            first_idx = next(i for i in range(len(cal_full))
                             if _d(cal_full[i]) in td)
            cal = cal_full[first_idx:]
            w_me = month_end_window(cal, 2)
            w_ph = pre_longholiday_window(cal, 2)
            missing = sum(1 for dt in cal if _d(dt) not in td)
            CELL_ANCHORS[term] = {
                "start": str(cal[0]), "cal_rows": len(cal),
                "month_end": int(w_me.sum()),
                "pre_hol": int(w_ph.sum()),
                "union": int((w_me | w_ph).sum()),
                "missing": missing, "days": 91 if term == "GC091" else 182}
        ok.append(("anchors derived positive + long terms miss days",
                   all(a["cal_rows"] > 1000 and a["missing"] > 0
                       for a in CELL_ANCHORS.values())
                   and GC091_ROWS > 0 and GC182_ROWS > 0))

        P, err = load_repo_panel()
        ok.append(("panel gates pass on fixture", err is None))
        if err:
            raise RuntimeError(err)

        # ---- engine hand-check: term-missing fallback law
        tiny = np.array(["2026-01-05", "2026-01-06", "2026-01-09"],
                        dtype="datetime64[D]")
        r1 = np.array([2.0, 3.0, 4.0])
        rt_ok = np.array([2.5, 3.5, 4.5])
        rt_miss = np.array([np.nan, 3.5, 4.5])
        ser, eps, fb = swing_engine_p2(tiny, r1, rt_ok,
                                       np.array([0, 0, 0], dtype=bool), 7)
        # d0 term locks 2.5% for Jan-06..Jan-12 (tail clipped at Jan-09)
        ok.append(("long-term lock math (91/182-day family, 7d demo)",
                   len(ser) == 4 and np.allclose(ser, 2.5 / 365.0)
                   and len(eps) == 1 and fb == 0))
        ser2, eps2, fb2 = swing_engine_p2(tiny, r1, rt_miss,
                                          np.array([0, 0, 0], dtype=bool), 7)
        # d0 term missing -> fallback overnight 2.0/365 on Jan-06; d1/d2
        # term available again: d1 locks 3.5 through Jan-19 (clipped)
        ok.append(("term-missing fallback -> overnight + count",
                   fb2 == 1
                   and abs(ser2[0] - 2.0 / 365.0) < 1e-12
                   and abs(ser2[1] - 3.5 / 365.0) < 1e-12
                   and abs(ser2[2] - 3.5 / 365.0) < 1e-12
                   and abs(ser2[3] - 3.5 / 365.0) < 1e-12
                   and len(eps2) == 2))
        ser3, _e3, fb3 = swing_engine_p2(tiny, r1, rt_miss,
                                          np.array([1, 1, 1], dtype=bool), 7)
        # window days never count as fallback even when term missing
        ok.append(("window day with missing term = overnight, not "
                   "fallback-counted", fb3 == 0
                   and abs(ser3[0] - 2.0 / 365.0) < 1e-12
                   and ser3[2] == 0.0))

        # ---- cells + per-cell passives on the fixture panel
        cells, passives = {}, {}
        for term in CELL_TERMS:
            cell, cerr = build_cell(P, term)
            if cerr:
                raise RuntimeError(cerr)
            ser, eps, fbk = swing_engine_p2(
                cell["cal"], cell["r_gc001"], cell["term_rate"],
                cell["win"], cell["days"])
            cell["ser"], cell["eps"] = ser, eps
            cell["n_episodes"] = len(eps)
            cell["fallback_days"] = fbk
            pser, _pe = passive_roll_p2(cell)
            cells[f"CAL-SWITCH-{term}"] = cell
            passives[f"CAL-SWITCH-{term}"] = pser
        ok.append(("2 cells + per-cell passives finite; fallbacks "
                    "tracked", all(np.isfinite(sharpe_of(cells[n]["ser"]))
                                   for n in cells)
                   and all(np.isfinite(sharpe_of(passives[n]))
                           for n in passives)
                   and all(cells[n]["fallback_days"] > 0
                           for n in cells)))
        ok.append(("two cell windows differ (own-calendar law)",
                   cells["CAL-SWITCH-GC091"]["cal_rows"]
                   > cells["CAL-SWITCH-GC182"]["cal_rows"]
                   and cells["CAL-SWITCH-GC091"]["missing"]
                   != cells["CAL-SWITCH-GC182"]["missing"]))
        # planted term premium -> the longer lock carries the higher
        # annualized accrual on the fixture (spread monotone in term)
        ok.append(("planted premium: GC182 cell ann-ret > GC091 cell",
                   _cell_stats(cells["CAL-SWITCH-GC182"]["ser"])
                   ["ann_ret_natural_day"]
                   > _cell_stats(cells["CAL-SWITCH-GC091"]["ser"])
                   ["ann_ret_natural_day"]))

        nulls = {}
        for name, cell in cells.items():
            n1 = run_nulls(cell)
            n2 = run_nulls(cell)
            nulls[name] = n1
            ok.append((f"nulls[{name}] deterministic (npy resume)",
                       n1["values"] == n2["values"]
                       and len(n1["values"]) == K_NULLS
                       and n1["coverage"]["n_values"] >= 30))

        vstarts = {n: virtual_starts_cell(cells[n]["ser"], passives[n])
                   for n in cells}
        splits = {}
        for n in cells:
            splits[n] = split_windows_face(cells[n]["ser"])
            splits[f"PASSIVE-GC001-ROLL@{n}"] = \
                split_windows_face(passives[n])
        d6 = d6_block(cells, passives)
        ok.append(("vstarts/splits/d6 shapes",
                   all(set(vstarts[n]) == set(WIN_DAYS) for n in cells)
                   and all("segment_stable" in splits[s] for s in splits)
                   and set(d6["cells"]) == set(cells)
                   and all("p1_family_pairwise"
                           in d6["cells"][n] for n in cells)
                   and len(d6["same_batch_cross"]) == 1
                   and not d6["cells"]["CAL-SWITCH-GC091"]["reject"]))

        product = phase1_write(P, cells, passives, nulls, vstarts, splits,
                               d6)
        ok.append(("phase-1: per-cell passive pair disclosed",
                   len(product["passive"]) == 2
                   and all(abs(product["passive"]
                              [f"PASSIVE-GC001-ROLL@{n}"]["full"]
                              ["sharpe_full"]
                              - _cell_stats(passives[n])["sharpe_full"])
                           < 1e-9 for n in cells)))

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
            product = finalize(product, cells, passives, nulls)
            pv_ok = all(
                product["gates"][n]["g1_prime_v2"]["skill_line"]
                ["passive_source"] == "batch_own_per_cell"
                for n in cells)
            lin_ok = all(
                abs(product["gates"][n]["g1_prime_v2"]["skill_line"]
                    ["passive_term"]
                    - (product["gates"][n]["passive_override"] + 0.10))
                < 1e-9 for n in cells)
            ok.append(("finalize product fields",
                       os.path.exists(OUT_JSON)
                       and product["evidence_cutoff"] == EVIDENCE_CUTOFF
                       and "cutoff_meta" in product
                       and len(product["gates"]) == 2
                       and all("g2" in g for g in
                               product["gates"].values())
                       and product["trials_ledger"]["total"] == 100))
            ok.append(("per-cell passive_override wired into line",
                       pv_ok and lin_ok))
            ok.append(("episode kpi + fallback disclosure",
                       all("win_rate_vs_passive_same_days"
                           in product["episode_kpi"][n]
                           for n in cells)
                       and all("fallback_days_triggered"
                               in product["anchor_gates"][n]
                               for n in product["anchor_gates"])))
            att = json.load(open(ATT_JSON, encoding="utf-8"))
            ok.append(("attrition row + funnel dual columns",
                       att["entries"][-1]["batch"] == BATCH_NAME
                       and product["funnel"]["harvest_column"] == 1))
        finally:
            SG.n_eff, SG.append_ledger, SG.ledger_head = _ne, _al, _lh
            globals()["cscv_pbo"] = _real_cscv

        # ---- passive_override vs named-pool reader branch (additive)
        line_ov = SG.skill_line_v2(batch_cells=BATCH_CELLS, pool="core48",
                                   null_pool={"values": nulls[
                                       "CAL-SWITCH-GC091"]["values"],
                                       "coverage": nulls[
                                           "CAL-SWITCH-GC091"][
                                           "coverage"]},
                                   passive_override=1.234)
        line_pl = SG.skill_line_v2(batch_cells=BATCH_CELLS, pool="core48",
                                   null_pool={"values": nulls[
                                       "CAL-SWITCH-GC091"]["values"],
                                       "coverage": nulls[
                                           "CAL-SWITCH-GC091"][
                                           "coverage"]})
        ok.append(("skill_line_v2 override branch + default intact",
                   abs(line_ov["passive_term"] - 1.334) < 1e-9
                   and line_ov["passive_source"] == "batch_own_per_cell"
                   and line_pl["passive_source"] == "pool:core48"))

        # ---- fail-closed refusal paths (anchor drift -> exit-2 face)
        real = {t: dict(a) for t, a in CELL_ANCHORS.items()}
        CELL_ANCHORS["GC091"]["missing"] += 1
        _c, cerr = build_cell(P, "GC091")
        ok.append(("term-missing anchor drift refusal", cerr is not None
                   and "term-missing" in str(cerr)))
        CELL_ANCHORS["GC091"]["start"] = "1999-01-01"
        _c, cerr = build_cell(P, "GC091")
        ok.append(("window-start anchor drift refusal", cerr is not None
                   and "window start" in str(cerr)))
        CELL_ANCHORS = real
        rr = GC001_ROWS
        GC001_ROWS = rr + 1
        _, err2 = load_repo_panel()
        ok.append(("G-PANEL rows drift refusal", err2 is not None
                   and "rows" in str(err2)))
        GC001_ROWS = rr
        # outside-cal: rewrite one GC182 settle row onto a SATURDAY (a
        # natural day on no trading calendar, inside the cutoff window)
        # -- the row count stays put so the refusal lands on the
        # outside-cal face specifically
        g182p = os.path.join(PANEL_DIR, "GC182.csv")
        gdf = pd.read_csv(g182p)
        gdf.loc[0, "date"] = "2013-04-06"     # Saturday
        gdf.to_csv(g182p, index=False)
        _, err3 = load_repo_panel()
        ok.append(("outside-cal refusal", err3 is not None
                   and "outside-cal" in str(err3)))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    n_ok = sum(1 for _, v in ok if v)
    print(f"innovation_quota_w2 selftest: {n_ok}/{len(ok)} PASS")
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
            os.environ.get("INNOVATION_QUOTA_W2_REFINALIZE") != "1":
        print("idempotent no-op: REPO-CALENDAR-P2.json exists "
              "(INNOVATION_QUOTA_W2_REFINALIZE=1 = only redo)")
        return 0
    return cmd_run()


if __name__ == "__main__":
    sys.exit(main())
