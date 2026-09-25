# -*- coding: utf-8 -*-
"""MF_ROT_S1 mid-frequency rotation first batch runner (T-2026-09-25-60 s3,
bm-b claim). Prereg research/midfreq/MF_ROT_S1_PREREG.md frozen pre-run r178
(R99 law: verdicts final, run-only §7 backfill, no threshold tuning).

Judgment face = G1'v2 + G2 registration gates via shared library
science_gates.py (zero hand-copied lines, T-02 law). Cells (prereg §3):

  MF-SR2   score = ln(close) 25-day OLS slope x252 (annualized) x R^2;
           Top3 of the 48-member bare pool, DAILY checks, min-hold 8
           consecutive trading days; turnover budget <=12 one-sided/yr
  MF-SR2W  same signal, weekly first-trading-day checks (sanctioned
           frequency A/B pair with MF-SR2; also min-hold 8td)
  MF-DM    monthly: pct_change(20) cross-rank Top3 among pct_change(60)>0
           passers; passers<3 -> passers equal-weight + rest cash (repo
           accrual); 0 passers -> 100% 511260 defense
  MF-GEM   monthly: 252-day cumulative return winner of 510300 vs 513100;
           winner cum < cash 252d cum (repo) -> 100% 511260

Execution lag: signal at close of T (prev trading day) -> trade at open of
T+1. Membership-only trading (frozen semantics): rebalance to target equal
weights ONLY when the held set changes or at inception; weights drift
between changes -- prereg's own turnover budget and §5.1 predictions
(8-22 one-sided/yr) freeze this reading.

min-hold semantics (frozen at implementation, disclosed in results):
target set = Top3 UNION held members whose consecutive-hold clock < 8
trading days (clock = exec-day-index - entry-day-index, reset on entry,
continuous segments only); equal weight across the union.

Eligibility: 60 trading days of panel history (late-listed members join
ranking from that day, prereg §2 roster); any NaN in the signal window
excludes the member from that day's ranking (never zero-filled, §5.6(3)).
Warmup = cash accrual until a cell's first valid signal (SR2 ~60td, DM
~60td, GEM ~252td) -- deterministic, disclosed per cell.

Costs: V2 face reused VERBATIM from alloc_backtest.py imports (commission
2.5bp w/ 5-yuan floor + handling 0.341bp + supervision 0.2bp + ADV20-tiered
slippage 2/5/10bp, missing-ADV -> 10bp) + 1% ADV fill cap + lot 100. ADV
index for open executions = t-1 (fully known at the open; inception without
t-1 falls to the 10bp tier). x2/x3 = whole-V2 multiplied (descriptive
survival faces only).

Null family (prereg §3): 100 pooled draws, seeds 59000+i (registered
mf_rot_s1=59000 in science_gates.SEED_REGISTRY): i<50 daily-cadence, i>=50
monthly-cadence random Top3 of the same eligible set, same lag + costs, no
min-hold. Batch-own null_pool feeds skill_line_v2 + DSR (cta_p1 precedent).

Passives in-batch (recomputed, never hand-copied): EW48 buy-hold / 510300
buy-hold / EW48 monthly rebalance. Skill line pool = "core48" (shared
library live passive face). D6: batch-internal corr -> |corr|>=0.7 merge
clause = connected components -> N_eff actual (skill line AND ledger both
consume post-merge count); t35 sleeve pre-gate reused from alloc_backtest
(honest pending under the 20-trading-day overlap gate).

Virtual starts (O-1532): 13 monthly-offset inceptions (first trading day
2020-08 .. 2021-08), full remaining window, frozen rules; per-start Sharpe
distribution + pass rate = descriptive robustness face, zero new gates.

Hard gates: panel completeness >=95% non-null per member (VOID exit 2);
selftest green before pool burn. Ledger + gate_attrition appended at
finalize only (single-shot guard; MF_ROT_S1_REFINALIZE=1 = only redo path).
Zero wall-clock fields in MF_ROT_S1.json; determinism via selftest F11
double-run byte-identity. Usage: run | selftest

Products: results/midfreq/MF_ROT_S1.json + MF_ROT_S1_cells.csv + per-cell
checkpoints results/midfreq/mf_rot_s1_cells/<cell>.json + null-family
checkpoint mf_rot_s1_nulls.json (config-sha keyed resume, T-33 law).
"""
import argparse
import json
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "screening"))

import numpy as np
import pandas as pd

import science_gates as sg
from alloc_backtest import (CUTOFF, START, side_cost_v2, est_leg_cost,
                            t35_sleeve_corr, load_repo, four_metrics,
                            _r6, config_sha)  # noqa: F401 (four_metrics house face)
import alloc_backtest as AB
from knowledge import rules as krules

FEE = krules.FeeSchedule()

TICKET = "T-2026-09-25-60"
PREREG = "research/midfreq/MF_ROT_S1_PREREG.md"
CAPITAL = 1_000_000.0
DATA = os.path.join("data", "daily")
OUT_JSON = os.path.join("results", "midfreq", "MF_ROT_S1.json")
OUT_CSV = os.path.join("results", "midfreq", "MF_ROT_S1_cells.csv")
CELLS_DIR = os.path.join("results", "midfreq", "mf_rot_s1_cells")
NULL_FILE = os.path.join("results", "midfreq", "mf_rot_s1_nulls.json")
ATT_JSON = os.path.join("results", "gate_attrition.json")
LOG_PATH = os.path.join("results", "midfreq", "mf_rot_backtest.log")

TOP_K = 3
SR2_WIN = 25                 # prereg §3 frozen
MIN_HOLD_TD = 8              # prereg §3 frozen (consecutive trading days)
DM_REL_WIN = 20
DM_ABS_WIN = 60
GEM_WIN = 252
MIN_HIST = 60                # eligibility: trading days of panel history
DEFENSE = "511260"           # 10-year treasury ETF (prereg §2 frozen leg)
GEM_LEGS = ("510300", "513100")
BENCH_LEG = "510300"
SEED_BASE = 59_000           # science_gates.SEED_REGISTRY["mf_rot_s1"]
NULL_DRAWS_PER_FACE = 50     # x2 cadence faces = 100 pooled (prereg §0)
TURNOVER_BUDGET = 12.0       # one-sided/yr, declared for SR2/SR2W (§3)
OOS_START = "2025-01-01"     # house constant
BATCH_CELLS_NOMINAL = 4
NAMED_EVENT_WINDOWS = {      # prereg §5.4 crisis-awareness disclosure faces
    "2020-03_pandemic": ("2020-02-03", "2020-03-31"),
    "2022-03": ("2022-03-01", "2022-03-31"),
    "2022-10": ("2022-10-01", "2022-10-31"),
    "2024-09-24": ("2024-09-24", "2024-09-24"),
    "2024-09-26": ("2024-09-26", "2024-09-26"),
}
# prereg §5 frozen prediction ranges (machine reconciliation face only)
PRED = {
    "MF-SR2": {"sharpe": (0.2, 0.8), "max_dd": (-0.25, -0.15),
               "turnover_per_yr": (8.0, 22.0)},
    "MF-SR2W": {"sharpe_delta_vs_sr2": (-0.15, 0.15),
                "turnover_delta_frac_vs_sr2": (-0.60, -0.30)},
    "MF-DM": {"sharpe": (0.4, 1.0), "max_dd": (-0.18, -0.10),
              "defense_month_frac": (0.15, 0.35)},
    "MF-GEM": {"sharpe": (0.5, 1.1), "max_dd": (-0.20, -0.12),
               "defense_month_frac": (0.05, 0.15)},
    "corr": {"sr2_sr2w_min": 0.9, "sr2_dm": (0.5, 0.8), "gem_others": (0.3, 0.6)},
    "null_sharpe": (-0.3, 0.2),
    "passive_ew48_bh": (0.25, 0.35),
    "virtual_start_pass_rate": (0.6, 0.9),
}
EXTREME_PRIOR_PCT = (-6.0, 2.0)   # §5.4: combo single-day -6..+2 expected band


def _log(msg):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as fh:
        fh.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}\n")


# ---------------------------------------------------------------- data faces

def load_core_panel():
    """core48 bare pool (live.paper.load_core listing mirror): digit-named
    CSVs in data/daily, open/close/amount, cutoff-truncated to 2026-09-22."""
    out = {}
    for f in sorted(os.listdir(DATA)):
        if not (f.endswith(".csv") and f[:-4].isdigit()):
            continue
        df = pd.read_csv(os.path.join(DATA, f))
        df["date"] = df["date"].astype(str)
        df = df.set_index("date").sort_index()
        if len(df) < MIN_HIST:
            continue
        out[f[:-4]] = df[[c for c in ("open", "close", "amount") if c in df.columns]]
    return out


def build_frames(raw):
    """Raw close frame (signal face, NaN preserved) + ffill valuation frames."""
    close = pd.DataFrame({s: d["close"] for s, d in raw.items()}).sort_index()
    close = close[(close.index >= START) & (close.index <= CUTOFF)]
    openp = pd.DataFrame({s: d["open"] for s, d in raw.items()}).reindex(close.index)
    amt = pd.DataFrame({s: d["amount"] for s, d in raw.items()}).reindex(close.index)
    return close, openp, amt


def completeness_gate(close):
    """Per prereg §2 probe semantics: zero-null WITHIN each member's listed
    range (late-listed heads are the natural listing face, eligibility rules
    own them). Gate = no internal gaps: non-null ratio inside
    [first_valid, last_valid] >= 0.95 AND no mid-series nulls."""
    rows, ok = {}, True
    for s in close.columns:
        col = close[s]
        seg = col.dropna()
        if len(seg) == 0:
            rows[s] = {"listed_rows": 0, "internal_nulls": None, "ratio": 0.0}
            ok = False
            continue
        span = col.loc[seg.index[0]:seg.index[-1]]
        internal_nulls = int(span.isna().sum())
        ratio = float(span.notna().sum()) / len(span)
        rows[s] = {"listed_rows": int(len(span)),
                   "first_valid": str(seg.index[0]), "last_valid": str(seg.index[-1]),
                   "internal_nulls": internal_nulls, "ratio": _r6(ratio)}
        if ratio < 0.95:
            ok = False
    return ok, rows


# ---------------------------------------------------------------- signal faces

def _rolling_ols_score(y, win):
    """Vectorized per-day OLS slope(annualized)*R^2 of ln(close) over win
    trailing points. NaN window -> NaN. Zero-variance window -> 0 score."""
    n = float(win)
    x = np.arange(win, dtype=float)
    sx = x.sum()
    sxx = float((x * x).sum())
    denom = n * sxx - sx * sx
    if len(y) < win:
        return np.full(len(y), np.nan)
    y = np.asarray(y, dtype=float)
    ln = np.log(np.where(np.isfinite(y) & (y > 0), y, np.nan))
    from numpy.lib.stride_tricks import sliding_window_view
    w = sliding_window_view(ln, win)                     # (T-win+1, win)
    valid = ~np.isnan(w).any(axis=1)
    sy = w.sum(axis=1)
    sxy = w @ x
    syy = (w * w).sum(axis=1)
    slope = (n * sxy - sx * sy) / denom
    var_x = sxx - sx * sx / n
    var_y = syy - sy * sy / n
    with np.errstate(divide="ignore", invalid="ignore"):
        r2 = (sxy - sx * sy / n) ** 2 / (var_x * var_y)
        r2 = np.where(var_y <= 0, 0.0, r2)
    score = slope * 252.0 * r2
    score[~valid] = np.nan
    out = np.full(len(y), np.nan)
    out[win - 1:] = score
    return out


def sr2_score_matrix(close, win=SR2_WIN):
    return pd.DataFrame(
        {s: _rolling_ols_score(close[s].to_numpy(dtype=float), win)
         for s in close.columns},
        index=close.index)


def eligibility_matrix(close, min_hist=MIN_HIST):
    """True where the member has >= min_hist trading days of history."""
    out = {}
    for s in close.columns:
        v = close[s].notna().to_numpy()
        out[s] = v.cumsum() >= min_hist
    return pd.DataFrame(out, index=close.index)


def pct_change_matrix(close, win):
    return close.pct_change(win)


def cash_cum252(cash_ret, win=GEM_WIN):
    """Rolling cumulative cash-leg return over `win` trading days."""
    g = (1.0 + cash_ret.to_numpy(dtype=float))
    from numpy.lib.stride_tricks import sliding_window_view
    if len(g) < win:
        return np.full(len(g), np.nan)
    w = sliding_window_view(g, win)
    out = np.full(len(g), np.nan)
    out[win - 1:] = np.prod(w, axis=1) - 1.0
    return out


def _check_day_indices(dates, cadence):
    """Execution-day indices (trade at OPEN of these days; signal = prev
    trading day close). daily: all; weekly: first trading day of ISO week;
    monthly: first trading day of month."""
    if cadence == "daily":
        return list(range(1, len(dates)))
    idx = []
    prev_key = None
    for t, d in enumerate(dates):
        dt = pd.Timestamp(d)
        key = (dt.isocalendar()[1], dt.isocalendar()[0]) if cadence == "weekly" else d[:7]
        if t > 0 and key != prev_key:
            idx.append(t)
        prev_key = key
    return idx


# ---------------------------------------------------------------- plan faces

def build_plan(cell, close, cash_ret, sr2_scores=None, elig=None,
               rel20=None, abs60=None, gem_leg_cum=None, cash_c=None):
    """{exec_idx: {"members": [...], "weights": {sym: w}, "cash_weight": w,
    "top3": [...], "state": str}}. Signal always from close of exec_idx-1."""
    dates = list(close.index)
    n = len(dates)
    if cell in ("MF-SR2", "MF-SR2W"):
        cadence = "daily" if cell == "MF-SR2" else "weekly"
        sc = sr2_scores
        plan = {}
        for t in _check_day_indices(dates, cadence):
            row = sc.iloc[t - 1]
            er = elig.iloc[t - 1]
            cand = [(row[s], s) for s in close.columns
                    if er[s] and np.isfinite(row[s])]
            cand.sort(key=lambda kv: (-kv[0], kv[1]))
            members = [s for _, s in cand[:TOP_K]]
            if members:
                w = 1.0 / len(members)
                plan[t] = {"members": members,
                           "weights": {s: w for s in members},
                           "cash_weight": 0.0, "top3": list(members),
                           "state": f"top{len(members)}"}
        return plan
    if cell == "MF-DM":
        plan = {}
        for t in _check_day_indices(dates, "monthly"):
            rel = rel20.iloc[t - 1]
            ab = abs60.iloc[t - 1]
            er = elig.iloc[t - 1]
            cand = [(rel[s], s) for s in close.columns
                    if er[s] and np.isfinite(rel[s]) and np.isfinite(ab[s])
                    and ab[s] > 0.0]
            cand.sort(key=lambda kv: (-kv[0], kv[1]))
            passers = [s for _, s in cand[:TOP_K]]
            if not passers:
                plan[t] = {"members": [DEFENSE], "weights": {DEFENSE: 1.0},
                           "cash_weight": 0.0, "top3": [],
                           "state": "zero_passers_defense"}
            else:
                w = 1.0 / TOP_K
                plan[t] = {"members": passers,
                           "weights": {s: w for s in passers},
                           "cash_weight": 1.0 - w * len(passers),
                           "top3": list(passers),
                           "state": (f"{len(passers)}passers"
                                     + ("_cash" if len(passers) < TOP_K else ""))}
        return plan
    if cell == "MF-GEM":
        plan = {}
        for t in _check_day_indices(dates, "monthly"):
            i = t - 1
            a = gem_leg_cum["510300"][i]
            b = gem_leg_cum["513100"][i]
            c = cash_c[i]
            if not all(np.isfinite(v) for v in (a, b, c)):
                continue                      # warmup: cash until valid
            winner = ("510300", a) if a >= b else ("513100", b)
            if winner[1] < c:
                plan[t] = {"members": [DEFENSE], "weights": {DEFENSE: 1.0},
                           "cash_weight": 0.0, "top3": [],
                           "state": "winner_below_cash_defense"}
            else:
                plan[t] = {"members": [winner[0]],
                           "weights": {winner[0]: 1.0},
                           "cash_weight": 0.0, "top3": [],
                           "state": f"winner_{winner[0]}"}
        return plan
    raise ValueError(f"unknown cell {cell}")


def build_null_plan(close, elig, cadence, seed, dates_len):
    """Random Top3 of the eligible set at each check; no min-hold; same lag."""
    dates = list(close.index)
    rng = np.random.default_rng(seed)
    syms = list(close.columns)
    plan = {}
    elig_np = elig.to_numpy()
    for t in _check_day_indices(dates, cadence):
        pool = [syms[j] for j in range(len(syms)) if elig_np[t - 1][j]]
        if len(pool) >= TOP_K:
            pick = list(rng.choice(len(pool), size=TOP_K, replace=False))
            members = [pool[j] for j in pick]
        elif pool:
            members = list(pool)
        else:
            continue
        w = 1.0 / len(members)
        plan[t] = {"members": members, "weights": {s: w for s in members},
                   "cash_weight": 0.0, "top3": list(members),
                   "state": f"null_pick{len(members)}"}
    return plan


# ---------------------------------------------------------------- engine

def simulate_rotation(dates, open_px, close_px, adv, cash_ret, plan, capital,
                       cost_mult=1.0, start_idx=0, min_hold=0):
    """Daily share-based sim; trades at OPEN of plan days (signal = prev day
    close). Membership-only trading: rebalance when held set != target set
    (target = plan members UNION min-hold-protected held members). Weights
    drift between trades. adv: {sym: [adv20]} indexed t-1 at execution."""
    syms = list(open_px.keys())
    holdings = {s: 0.0 for s in syms}
    clock = {}                                    # sym -> entry day index
    cash = float(capital)
    n_trades = 0
    n_entries = 0
    total_cost = 0.0
    comm_floor_hits = 0
    fill_refusals = 0
    equity_path = []
    holdings_track = {}

    for t in range(start_idx, len(dates)):
        cash *= (1.0 + float(cash_ret[t]))
        po = {s: open_px[s][t] for s in syms}
        pc = {s: close_px[s][t] for s in syms}
        # r182: finite-only valuation -- pre-listing heads survive ffill and
        # 0*NaN=NaN poisons equity through every downstream number; an
        # unpriced symbol can be neither valued nor traded this day (never
        # zero-filled, prereg s5.6(3) family). Listed-range internal gaps
        # are gate-zero (r179), so held symbols always price.
        equity = cash + sum(holdings[s] * po[s] for s in syms
                            if np.isfinite(po[s]))

        st = plan.get(t)
        if st is not None:
            members = list(st["members"])
            weights = dict(st["weights"])
            if min_hold:
                for s in sorted(clock):
                    if s not in members and (t - clock[s]) < min_hold:
                        members.append(s)          # min-hold protection
                if members != list(st["members"]):
                    w = 1.0 / len(members)
                    weights = {s: w for s in members}
            held = sorted(s for s in syms if holdings[s] > 0)
            if sorted(members) != held:
                reserve = 0.0
                nom = {}
                for s in syms:
                    if not np.isfinite(po[s]):
                        continue          # unpriced at the open: no leg cost
                    tv = weights.get(s, 0.0) * equity - holdings[s] * po[s]
                    nom[s] = tv
                    reserve += est_leg_cost(abs(tv))
                equity_adj = equity - reserve
                for s in syms:
                    if not np.isfinite(po[s]):
                        continue          # untradeable this exec day (r182)
                    target = weights.get(s, 0.0) * equity_adj
                    cur = holdings[s] * po[s]
                    delta = target - cur
                    if abs(delta) < po[s]:
                        continue
                    shares = int(abs(delta) / po[s] // 100) * 100
                    if shares <= 0:
                        continue
                    gross = shares * po[s]
                    a = adv.get(s)[t - 1] if (t > 0 and adv.get(s) is not None) \
                        else float("nan")
                    if np.isfinite(a) and gross > krules.ADV_FILL_CAP_RATE * a:
                        fill_refusals += 1
                        continue
                    if gross * AB.FEE.commission_rate < AB.FEE.commission_min:
                        comm_floor_hits += 1
                    cost = cost_mult * side_cost_v2(gross, a)
                    if delta > 0:
                        cash -= gross + cost
                        holdings[s] += shares
                        n_entries += 1
                    else:
                        cash += gross - cost
                        holdings[s] -= shares
                    n_trades += 1
                    total_cost += cost
                # refresh clocks: entries reset, exits clear
                new_held = {s for s in syms if holdings[s] > 0}
                for s in sorted(clock):
                    if holdings[s] <= 0:
                        del clock[s]
                for s in sorted(new_held):
                    if s not in clock:
                        clock[s] = t
                equity = cash + sum(holdings[s] * po[s] for s in syms
                                    if np.isfinite(po[s]))
            holdings_track[t] = (sorted(s for s in syms if holdings[s] > 0),
                                 {s: holdings[s] for s in syms if holdings[s] > 0})

        equity_path.append(cash + sum(holdings[s] * pc[s] for s in syms
                                      if np.isfinite(pc[s])))

    eq = pd.Series(equity_path, index=pd.Index(dates[start_idx:]))
    return {"eq": eq, "n_trades": n_trades, "n_entries": n_entries,
            "total_cost": total_cost, "comm_floor_hits": comm_floor_hits,
            "fill_refusals": fill_refusals, "holdings_track": holdings_track}


def sharpe_ann(eq):
    r = eq.pct_change().dropna()
    if len(r) < 2:
        return 0.0
    sd = float(r.std())
    if sd <= 0:
        return 0.0
    return float(r.mean()) / sd * math.sqrt(252.0)


def cell_metrics(eq, n_trades, n_entries, total_cost):
    yrs = len(eq) / 252.0
    ann = float(eq.iloc[-1] / eq.iloc[0]) ** (1.0 / yrs) - 1.0 if yrs > 0 else 0.0
    dd = float((eq / eq.cummax() - 1.0).min())
    month_last = eq.groupby(eq.index.str[:7]).last()
    mret = month_last.pct_change().dropna()
    return {
        "sharpe": _r6(sharpe_ann(eq)), "ann_ret": _r6(ann), "max_dd": _r6(dd),
        "monthly_pos_rate": _r6(float((mret > 0).mean()) if len(mret) else None),
        "n_trades": int(n_trades), "n_entries": int(n_entries),
        "turnover_per_yr": _r6(n_trades / yrs if yrs > 0 else None),
        "total_cost_cny": _r6(total_cost), "years": _r6(yrs),
        "n_months": int(len(mret)),
    }


def extreme_days(eq):
    r = eq.pct_change().dropna()
    out = {"worst_3": [], "named_events": {}, "prior_band_pct": list(EXTREME_PRIOR_PCT)}
    if len(r) == 0:
        return out
    for d, v in r.sort_values().head(3).items():
        out["worst_3"].append({"date": d, "ret_pct": _r6(float(v) * 100.0)})
    for name, (lo, hi) in NAMED_EVENT_WINDOWS.items():
        seg = r[(r.index >= lo) & (r.index <= hi)]
        if len(seg):
            d, v = seg.sort_values().index[0], float(seg.min())
            out["named_events"][name] = {"worst_day": d, "ret_pct": _r6(v * 100.0)}
    return out


def defense_month_frac(plan, dates):
    """Monthly cells: fraction of exec months carrying a defense/cash state."""
    months = {}
    for t, st in plan.items():
        months[dates[t][:7]] = st["state"]
    if not months:
        return None
    defn = sum(1 for s in months.values()
               if "defense" in s or "cash" in s or "below" in s)
    return _r6(defn / len(months))


# ---------------------------------------------------------------- cells run

def cell_config_sha(cell):
    cfg = {"cell": cell, "capital": CAPITAL, "start": START, "cutoff": CUTOFF,
           "sr2_win": SR2_WIN, "min_hold": MIN_HOLD_TD, "dm": (DM_REL_WIN, DM_ABS_WIN),
           "gem_win": GEM_WIN, "min_hist": MIN_HIST, "top_k": TOP_K,
           "defense": DEFENSE, "engine": "membership-only-equalweight-v1"}
    return config_sha(cfg, "rotation", False, CAPITAL, START, CUTOFF)


def run_cell(cell, dates, open_px, close_px, adv, cash_ret, plans):
    """All faces for one cell: v2 main + x2/x3 + 13 virtual starts.
    Checkpoint-resumable via config sha."""
    os.makedirs(CELLS_DIR, exist_ok=True)
    sha = cell_config_sha(cell)
    path = os.path.join(CELLS_DIR, f"{cell}.json")
    if os.path.exists(path):
        try:
            j = json.load(open(path, encoding="utf-8"))
            if j.get("config_sha") == sha:
                _log(f"cell {cell}: checkpoint valid (sha {sha}), resume-load")
                return j
        except Exception:
            pass

    plan = plans[cell]
    base = simulate_rotation(dates, open_px, close_px, adv, cash_ret, plan,
                             CAPITAL, cost_mult=1.0, start_idx=0,
                             min_hold=(MIN_HOLD_TD if cell in ("MF-SR2", "MF-SR2W") else 0))
    m = cell_metrics(base["eq"], base["n_trades"], base["n_entries"],
                     base["total_cost"])
    m["total_cost_cny"] = _r6(base["total_cost"])
    m["commission_floor_hits"] = int(base["comm_floor_hits"])
    m["fill_cap_refusals"] = int(base["fill_refusals"])
    first_exec = min(plan.keys()) if plan else None
    m["first_exec_day"] = dates[first_exec] if first_exec is not None else None
    m["warmup_note"] = (f"cash accrual until first valid signal; first exec "
                        f"{m['first_exec_day']} (lookback-dependent, prereg §3)")
    faces = {"v2_main": m}
    for face, mult in (("cost_x2", 2.0), ("cost_x3", 3.0)):
        r = simulate_rotation(dates, open_px, close_px, adv, cash_ret, plan,
                              CAPITAL, cost_mult=mult, start_idx=0,
                              min_hold=(MIN_HOLD_TD if cell in ("MF-SR2", "MF-SR2W") else 0))
        faces[face] = {"sharpe": _r6(sharpe_ann(r["eq"])),
                       "ann_ret": cell_metrics(r["eq"], r["n_trades"],
                                               r["n_entries"],
                                               r["total_cost"])["ann_ret"]}
    # 13 monthly-offset virtual starts (O-1532): first trading day 2020-08..2021-08
    starts = {}
    start_days = []
    seen = set()
    for t, d in enumerate(dates):
        ym = d[:7]
        if "2020-08" <= ym <= "2021-08" and ym not in seen:
            seen.add(ym)
            start_days.append((t, d))
    sharpes = []
    for t, d in start_days:
        r = simulate_rotation(dates, open_px, close_px, adv, cash_ret, plan,
                              CAPITAL, cost_mult=1.0, start_idx=t,
                              min_hold=(MIN_HOLD_TD if cell in ("MF-SR2", "MF-SR2W") else 0))
        sv = sharpe_ann(r["eq"])
        starts[d] = _r6(sv)
        sharpes.append(sv)
    pass_rate = _r6(float(sum(1 for v in sharpes if v > 0.0)) / len(sharpes)
                    if sharpes else None)
    oos_eq = base["eq"][base["eq"].index >= OOS_START]
    oos_m = cell_metrics(oos_eq, 0, 0, 0.0) if len(oos_eq) >= 20 else None
    out = {
        "config_sha": sha,
        "faces": faces,
        "virtual_starts": {"per_start_sharpe": starts,
                           "n_starts": len(starts),
                           "pass_rate_sharpe_positive": pass_rate,
                           "sharpe_min": _r6(min(sharpes)) if sharpes else None,
                           "sharpe_median": _r6(float(np.median(sharpes))) if sharpes else None,
                           "sharpe_max": _r6(max(sharpes)) if sharpes else None},
        "oos_from_2025_01_01": ({"sharpe": oos_m["sharpe"], "ann_ret": oos_m["ann_ret"],
                                 "max_dd": oos_m["max_dd"],
                                 "dual_positive": bool(oos_m["sharpe"] > 0
                                                       and oos_m["ann_ret"] > 0)}
                                if oos_m else None),
        "extreme_days": extreme_days(base["eq"]),
        "defense_month_frac": defense_month_frac(plan, dates),
        "month_end_equity_cny": [[d, _r6(float(v))] for d, v in
                                 base["eq"].groupby(base["eq"].index.str[:7]).last().items()],
    }
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    _log(f"cell {cell}: simulated + checkpoint written (sha {sha})")
    return out


def run_nulls(dates, open_px, close_px, adv, cash_ret, elig):
    """100 pooled random-Top3 nulls, seeds 59000+i (daily i<50, monthly
    i>=50). Checkpoint whole family in one sha-keyed file."""
    os.makedirs(os.path.dirname(NULL_FILE), exist_ok=True)
    cfg = {"base": SEED_BASE, "faces": ["daily", "monthly"],
           "draws": NULL_DRAWS_PER_FACE, "top_k": TOP_K, "cutoff": CUTOFF}
    sha = config_sha(cfg, "nulls", False, CAPITAL, START, CUTOFF)
    if os.path.exists(NULL_FILE):
        try:
            j = json.load(open(NULL_FILE, encoding="utf-8"))
            if j.get("config_sha") == sha and j.get("n_values") == 2 * NULL_DRAWS_PER_FACE:
                _log("nulls: checkpoint valid, resume-load")
                return j
        except Exception:
            pass
    vals = []
    per_draw = {}
    for i in range(2 * NULL_DRAWS_PER_FACE):
        cadence = "daily" if i < NULL_DRAWS_PER_FACE else "monthly"
        plan = build_null_plan(close_px, elig, cadence, SEED_BASE + i, len(dates))
        r = simulate_rotation(dates, open_px, close_px, adv, cash_ret, plan,
                              CAPITAL, cost_mult=1.0, start_idx=0, min_hold=0)
        sv = sharpe_ann(r["eq"])
        vals.append(sv)
        per_draw[f"{cadence}_draw{i}"] = {"seed": SEED_BASE + i, "sharpe": _r6(sv),
                                          "n_trades": int(r["n_trades"])}
    mu = float(np.mean(vals))
    sigma = float(np.std(vals, ddof=1))
    out = {
        "config_sha": sha,
        "seed_base_registered": "mf_rot_s1=59000 (science_gates.SEED_REGISTRY)",
        "n_values": len(vals),
        "values_rounded": [_r6(v) for v in vals],
        "coverage": {"n_values": len(vals), "mu": mu, "sigma": sigma,
                     "schemas_parsed": ["mf_rot_s1: daily(50)+monthly(50) random Top3"],
                     "known_unparsed": []},
        "per_draw": per_draw,
    }
    json.loads(json.dumps(out))                     # validate before write
    with open(NULL_FILE, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    _log(f"nulls: {len(vals)} draws done (mu={mu:.4f} sigma={sigma:.4f})")
    return out


def run_passive(dates, open_px, close_px, adv, cash_ret, close_df):
    """In-batch passives (prereg §3): EW48 buy-hold / 510300 buy-hold /
    EW48 monthly rebalance. Costs on, one V2 face."""
    syms = list(close_df.columns)
    out = {}
    # buy-hold helper: single inception trade set, no later trades
    def _bh(members):
        plan = {0: {"members": members,
                    "weights": {s: 1.0 / len(members) for s in members},
                    "cash_weight": 0.0, "top3": [], "state": "bh_inception"}}
        r = simulate_rotation(dates, open_px, close_px, adv, cash_ret, plan,
                              CAPITAL, cost_mult=1.0, start_idx=0, min_hold=0)
        return {"sharpe": _r6(sharpe_ann(r["eq"])),
                **{k: v for k, v in cell_metrics(r["eq"], r["n_trades"],
                                                 r["n_entries"],
                                                 r["total_cost"]).items()
                   if k in ("ann_ret", "max_dd", "n_trades", "years")}}
    out["PASSIVE-EW48-BH"] = _bh(syms)
    out["PASSIVE-510300-BH"] = _bh([BENCH_LEG])
    mon_idx = _check_day_indices(dates, "monthly")
    mon_idx = [t for t in mon_idx if t > 0]
    first = mon_idx[0] if mon_idx else 0
    plan = {}
    w = 1.0 / len(syms)
    plan[first] = {"members": list(syms), "weights": {s: w for s in syms},
                   "cash_weight": 0.0, "top3": [], "state": "ew_inception"}
    for t in mon_idx[1:]:
        plan[t] = {"members": list(syms), "weights": {s: w for s in syms},
                   "cash_weight": 0.0, "top3": [], "state": "ew_monthly"}
    r = simulate_rotation(dates, open_px, close_px, adv, cash_ret, plan,
                          CAPITAL, cost_mult=1.0, start_idx=0, min_hold=0)
    out["PASSIVE-EW48-MONTHLY"] = {
        "sharpe": _r6(sharpe_ann(r["eq"])),
        **{k: v for k, v in cell_metrics(r["eq"], r["n_trades"], r["n_entries"],
                                          r["total_cost"]).items()
           if k in ("ann_ret", "max_dd", "n_trades", "years")}}
    return out


# ---------------------------------------------------------------- D6 / merge

def batch_corr_and_merge(cells_rets):
    names = list(cells_rets)
    cr = pd.DataFrame(cells_rets)
    corr_pairs = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            v = cr[names[i]].corr(cr[names[j]])
            corr_pairs.append({"pair": f"{names[i]}|{names[j]}",
                               "corr": _r6(float(v))})
    # connected components over |corr| >= 0.7 (D6 merge clause)
    parent = {n: n for n in names}

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for p in corr_pairs:
        if p["corr"] is not None and abs(p["corr"]) >= 0.7:
            a, b = p["pair"].split("|")
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[ra] = rb
    comps = {}
    for n in names:
        comps.setdefault(find(n), []).append(n)
    return corr_pairs, [sorted(v) for v in comps.values()]


def prediction_reconciliation(cells, nulls, passives, corr_pairs, n_eff):
    """Machine face: prereg §5 frozen ranges vs actuals (evidence only)."""
    rec = {}

    def rng_ok(v, lo, hi):
        return None if v is None else bool(lo <= v <= hi)

    m = cells["MF-SR2"]["faces"]["v2_main"]
    rec["MF-SR2_sharpe"] = {"actual": m["sharpe"],
                            "range": list(PRED["MF-SR2"]["sharpe"]),
                            "in_range": rng_ok(m["sharpe"], *PRED["MF-SR2"]["sharpe"])}
    rec["MF-SR2_maxdd"] = {"actual": m["max_dd"],
                           "range": list(PRED["MF-SR2"]["max_dd"]),
                           "in_range": rng_ok(m["max_dd"], *PRED["MF-SR2"]["max_dd"])}
    rec["MF-SR2_turnover"] = {"actual": m["turnover_per_yr"],
                              "range": list(PRED["MF-SR2"]["turnover_per_yr"]),
                              "in_range": rng_ok(m["turnover_per_yr"],
                                                 *PRED["MF-SR2"]["turnover_per_yr"]),
                              "budget_12": bool((m["turnover_per_yr"] or 0) <= TURNOVER_BUDGET)}
    mw = cells["MF-SR2W"]["faces"]["v2_main"]
    td = ((mw["turnover_per_yr"] or 0) - (m["turnover_per_yr"] or 0)) / \
         (m["turnover_per_yr"] or 1.0)
    rec["MF-SR2W_sharpe_delta"] = {"actual": _r6(mw["sharpe"] - m["sharpe"]),
                                    "range": list(PRED["MF-SR2W"]["sharpe_delta_vs_sr2"]),
                                    "in_range": rng_ok(mw["sharpe"] - m["sharpe"],
                                                       *PRED["MF-SR2W"]["sharpe_delta_vs_sr2"])}
    rec["MF-SR2W_turnover_delta_frac"] = {"actual": _r6(td),
                                          "range": list(PRED["MF-SR2W"]["turnover_delta_frac_vs_sr2"]),
                                          "in_range": rng_ok(td, *PRED["MF-SR2W"]["turnover_delta_frac_vs_sr2"])}
    for c in ("MF-DM", "MF-GEM"):
        mc = cells[c]["faces"]["v2_main"]
        rec[f"{c}_sharpe"] = {"actual": mc["sharpe"], "range": list(PRED[c]["sharpe"]),
                              "in_range": rng_ok(mc["sharpe"], *PRED[c]["sharpe"])}
        rec[f"{c}_maxdd"] = {"actual": mc["max_dd"], "range": list(PRED[c]["max_dd"]),
                             "in_range": rng_ok(mc["max_dd"], *PRED[c]["max_dd"])}
        dm = cells[c].get("defense_month_frac")
        rec[f"{c}_defense_frac"] = {"actual": dm, "range": list(PRED[c]["defense_month_frac"]),
                                    "in_range": rng_ok(dm, *PRED[c]["defense_month_frac"])}
    cp = {p["pair"]: p["corr"] for p in corr_pairs}
    rec["corr_sr2_sr2w"] = {"actual": cp.get("MF-SR2|MF-SR2W"),
                            "min": PRED["corr"]["sr2_sr2w_min"],
                            "in_range": (None if cp.get("MF-SR2|MF-SR2W") is None else
                                         bool(cp["MF-SR2|MF-SR2W"] >= PRED["corr"]["sr2_sr2w_min"])),
                            "declared": "sanctioned A/B pair (prereg §1)"}
    rec["corr_sr2_dm"] = {"actual": cp.get("MF-SR2|MF-DM"),
                          "range": list(PRED["corr"]["sr2_dm"]),
                          "in_range": rng_ok(cp.get("MF-SR2|MF-DM"), *PRED["corr"]["sr2_dm"])}
    gem_o = [abs(v) for k, v in cp.items() if "MF-GEM" in k and v is not None]
    rec["corr_gem_vs_rest_abs"] = {"actual": _r6(max(gem_o)) if gem_o else None,
                                   "range": list(PRED["corr"]["gem_others"]),
                                   "in_range": rng_ok(max(gem_o) if gem_o else None,
                                                      *PRED["corr"]["gem_others"])}
    mu = nulls["coverage"]["mu"]
    rec["null_sharpe_mean"] = {"actual": _r6(mu), "range": list(PRED["null_sharpe"]),
                               "in_range": rng_ok(mu, *PRED["null_sharpe"])}
    pw = passives["PASSIVE-EW48-BH"]["sharpe"]
    rec["passive_ew48_bh_sharpe"] = {"actual": pw, "range": list(PRED["passive_ew48_bh"]),
                                     "in_range": rng_ok(pw, *PRED["passive_ew48_bh"]),
                                     "note": "J8 live recompute (in-batch, never hand-copied)"}
    prs = [cells[c]["virtual_starts"]["pass_rate_sharpe_positive"]
           for c in cells]
    rec["virtual_start_pass_rate"] = {"actual_per_cell": {c: cells[c]["virtual_starts"]["pass_rate_sharpe_positive"] for c in cells},
                                      "range": list(PRED["virtual_start_pass_rate"]),
                                      "in_range_min_ok": all(
                                          (v is None) or (v >= PRED["virtual_start_pass_rate"][0])
                                          for v in prs)}
    rec["n_eff_after_merge"] = {"actual": n_eff, "nominal": BATCH_CELLS_NOMINAL}
    return rec


# ---------------------------------------------------------------- main run

def cmd_run(_):
    sys.stdout.reconfigure(encoding="utf-8")
    if os.path.exists(OUT_JSON):
        try:
            prev = json.load(open(OUT_JSON, encoding="utf-8"))
            if prev.get("finalized") and os.environ.get("MF_ROT_S1_REFINALIZE") != "1":
                print("finalize refused: OUT_JSON already finalized (single-shot "
                      "guard; MF_ROT_S1_REFINALIZE=1 to redo)")
                return 2
        except Exception:
            pass

    raw = load_core_panel()
    close_df, open_df, amt_df = build_frames(raw)
    ok, comp = completeness_gate(close_df)
    if not ok:
        print("VOID: panel completeness gate FAILED (<95% non-null):",
              json.dumps(comp))
        return 2
    dates = list(close_df.index)
    open_px = {s: open_df[s].ffill().tolist() for s in close_df.columns}
    close_px = {s: close_df[s].ffill().tolist() for s in close_df.columns}
    adv = {s: amt_df[s].rolling(20).mean().tolist() for s in close_df.columns}
    cash_ret = load_repo(close_df.index).tolist()
    elig = eligibility_matrix(close_df)
    sr2_sc = sr2_score_matrix(close_df)
    rel20 = pct_change_matrix(close_df, DM_REL_WIN)
    abs60 = pct_change_matrix(close_df, DM_ABS_WIN)
    gem_leg_cum = {leg: (close_df[leg] / close_df[leg].shift(GEM_WIN) - 1.0).tolist()
                   for leg in GEM_LEGS}
    cash_c = cash_cum252(load_repo(close_df.index))

    plans = {}
    for cell in ("MF-SR2", "MF-SR2W", "MF-DM", "MF-GEM"):
        plans[cell] = build_plan(cell, close_df, cash_ret, sr2_scores=sr2_sc,
                                 elig=elig, rel20=rel20, abs60=abs60,
                                 gem_leg_cum=gem_leg_cum, cash_c=cash_c)
        print(f"[plan] {cell}: {len(plans[cell])} exec days, "
              f"first={dates[min(plans[cell])] if plans[cell] else 'none'}")

    cells = {}
    cells_rets = {}
    for cell in plans:
        cj = run_cell(cell, dates, open_px, close_px, adv, cash_ret, plans)
        cells[cell] = cj
        # re-derive main-face returns for corr/gates (deterministic re-sim)
        r = simulate_rotation(dates, open_px, close_px, adv, cash_ret,
                              plans[cell], CAPITAL, cost_mult=1.0, start_idx=0,
                              min_hold=(MIN_HOLD_TD if cell in ("MF-SR2", "MF-SR2W") else 0))
        cells_rets[cell] = r["eq"].pct_change().dropna()
    nulls = run_nulls(dates, open_px, close_px, adv, cash_ret, elig)
    passives = run_passive(dates, open_px, close_px, adv, cash_ret, close_df)

    corr_pairs, components = batch_corr_and_merge(cells_rets)
    n_eff = len(components)

    # G1'v2 per cell (skill line consumes post-merge N_eff + batch-own null)
    null_pool = {"values": nulls["values_rounded"],
                 "coverage": nulls["coverage"]}
    line = sg.skill_line_v2(batch_cells=n_eff, pool="core48", null_pool=null_pool)
    verdicts = {}
    passers = []
    for cell in plans:
        m = cells[cell]["faces"]["v2_main"]
        v = sg.g1_prime_v2(sharpe_full=m["sharpe"], returns=cells_rets[cell],
                           batch_cells=n_eff, pool="core48", null_pool=null_pool,
                           n_trades=m["n_trades"], n_entries=m["n_entries"])
        v["descriptive"] = {
            "annual_positive": bool(m["ann_ret"] > 0),
            "oos_dual_positive": bool(
                (cells[cell]["oos_from_2025_01_01"] or {}).get("dual_positive")),
            "dd_ok_ge_-35pct": bool(m["max_dd"] >= -0.35),
            "x2_direction_flip": bool((m["ann_ret"] > 0) !=
                                      (cells[cell]["faces"]["cost_x2"]["ann_ret"] > 0)),
            "x3_direction_flip": bool((m["ann_ret"] > 0) !=
                                      (cells[cell]["faces"]["cost_x3"]["ann_ret"] > 0)),
            "turnover_budget": (bool((m["turnover_per_yr"] or 0) <= TURNOVER_BUDGET)
                                if cell in ("MF-SR2", "MF-SR2W") else
                                f"no declared budget (monthly cadence, disclosed {m['turnover_per_yr']}/yr)"),
        }
        verdicts[cell] = v
        if v["pass_v2"]:
            passers.append(cell)

    # G2 for passers: DSR + family CSCV PBO (8 blocks, g25_retro precedent)
    from pbo import cscv_pbo, align_returns
    mat = align_returns(cells_rets)
    fam_pbo = cscv_pbo(mat)
    g2 = {}
    for cell in passers:
        dsr = sg.deflated_sharpe_ratio(cells_rets[cell], n_trials=line["n_eff"],
                                       var_null_sr=nulls["coverage"]["sigma"] ** 2)
        g2[cell] = sg.g2_registration_v2(g1_pass=True, dsr=dsr,
                                         pbo=fam_pbo["pbo"])

    sleeve = t35_sleeve_corr(cells_rets["MF-SR2"])
    recon = prediction_reconciliation(cells, nulls, passives, corr_pairs, n_eff)

    finalized = len(cells) == BATCH_CELLS_NOMINAL
    led = None
    att_row = None
    if finalized:
        led = sg.append_ledger("MF_ROT_S1", n_eff,
                               file_name="results/midfreq/MF_ROT_S1.json",
                               evidence_cutoff=CUTOFF,
                               note=(f"4 rotation cells (SR2/SR2W/DM/GEM, zoo "
                                     f"#81/#82/#83 new-written basis codes) + "
                                     f"100 random-Top3 nulls (seeds 59000+i, "
                                     f"registered mf_rot_s1) + 3 in-batch "
                                     f"passives; D6 merge -> N_eff={n_eff}; "
                                     f"prereg {PREREG} frozen r178 R99"))
        att = json.load(open(ATT_JSON, encoding="utf-8"))
        att_row = {
            "batch": "MF_ROT_S1", "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
            "kind": "measurement", "cells_ledger_delta": n_eff,
            "ledger_total_after": led["total"],
            "gates": {"completeness_pass": True,
                      "n_eff_after_d6_merge": n_eff,
                      "g1_prime_pass": sorted(passers),
                      "g2_eligible": sorted(k for k, v in g2.items()
                                             if v.get("eligible_v2"))},
            "eliminated": BATCH_CELLS_NOMINAL - len([k for k, v in g2.items()
                                                     if v.get("eligible_v2")]),
            "refs": {"results": "results/midfreq/MF_ROT_S1.json",
                     "prereg": PREREG, "ticket": f"{TICKET} s3"},
        }
        att["entries"].append(att_row)
        with open(ATT_JSON, "w", encoding="utf-8") as fh:
            json.dump(att, fh, ensure_ascii=False, indent=1)

    out = {
        "schema": "mf_rot_s1_v1",
        "batch": "MF_ROT_S1",
        "ticket": f"{TICKET} s3",
        "prereg": f"{PREREG} (frozen pre-run r178, R99)",
        **sg.cutoff_meta(CUTOFF),
        "window": {"start": dates[0], "end": dates[-1], "rows": len(dates)},
        "initial_capital_cny": CAPITAL,
        "judgment_face": "G1'v2 + G2 registration (science_gates shared library, T-02 law)",
        "finalized": finalized,
        "n_cells": len(cells),
        "execution_semantics": {
            "lag": "signal close of T (prev trading day) -> trade open of T+1",
            "trading": "membership-only; equal weights on set change; drift between",
            "min_hold": f"{MIN_HOLD_TD} consecutive td (SR2/SR2W); clock=exec-entry idx",
            "protection": "target = Top3 UNION held clock<8td; equal weight over union",
            "eligibility": f"{MIN_HIST} td panel history; NaN window excludes (no zero-fill)",
            "warmup": "cash accrual until first valid signal per cell",
        },
        "cells": cells,
        "d6": {
            "batch_corr_pairs": corr_pairs,
            "merge_components": components,
            "n_eff_after_merge": n_eff,
            "declared": "MF-SR2~MF-SR2W sanctioned A/B pair (frequency face, §1); "
                        "merge clause = |corr|>=0.7 connected components (zoo #82)",
            "vs_trader_sleeves": sleeve,
        },
        "nulls": {"summary": {"n": nulls["n_values"],
                               "mu": _r6(nulls["coverage"]["mu"]),
                               "sigma": _r6(nulls["coverage"]["sigma"]),
                               "p95": _r6(float(np.percentile(
                                   nulls["values_rounded"], 95))),
                               "max": _r6(max(nulls["values_rounded"])),
                               "min": _r6(min(nulls["values_rounded"]))},
                  "seed_base": SEED_BASE,
                  "per_face": {"daily": f"draws 0-{NULL_DRAWS_PER_FACE-1}",
                               "monthly": f"draws {NULL_DRAWS_PER_FACE}-{2*NULL_DRAWS_PER_FACE-1}"}},
        "passives": passives,
        "skill_line": line,
        "g1_prime_verdicts": verdicts,
        "family_pbo_cscv8": fam_pbo,
        "g2_registration": g2,
        "prediction_reconciliation": recon,
        "audit": {
            "data_completeness": comp,
            "missing_member_days": {s: int(close_df[s].isna().sum())
                                    for s in close_df.columns},
            "cost_model": {
                "basis": krules.COST_BASIS_V2,
                "per_side": "reused verbatim from alloc_backtest.side_cost_v2 "
                            "(comm 2.5bp floor 5 + handling 0.341bp + superv 0.2bp "
                            "+ adv20-tiered slip 2/5/10bp nan->10bp)",
                "lot": 100, "adv_fill_cap": krules.ADV_FILL_CAP_RATE,
                "adv_index_at_open": "t-1 (known at open; inception falls to 10bp tier)",
                "x2_x3": "whole-V2 multiplied, descriptive survival only",
            },
            "cash_model": "repo_daily rate/100/252 daily accrual (CASH_LEG carrier, alloc reuse)",
            "determinism": "no wall-clock fields in this JSON; selftest F11 double-run byte-identity",
            "turnover_budget_declared": f"<= {TURNOVER_BUDGET} one-sided/yr (SR2/SR2W, §3)",
        },
    }
    if led is not None:
        out["trials_ledger"] = led
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)

    rows = []
    for c in cells:
        rows.append({"name": c, "face": "v2_main", **cells[c]["faces"]["v2_main"]})
        for f in ("cost_x2", "cost_x3"):
            rows.append({"name": c, "face": f, **cells[c]["faces"][f]})
    for n, p in passives.items():
        rows.append({"name": n, "face": "passive", **p})
    pd.DataFrame(rows).to_csv(OUT_CSV, index=False, encoding="utf-8")

    print(f"MF_ROT_S1: cells={len(cells)}/{BATCH_CELLS_NOMINAL} "
          f"n_eff={n_eff} finalized={finalized} window={dates[0]}..{dates[-1]}")
    print(f"  skill_line_v2 = {line['line']} (passive_term={line['passive_term']} "
          f"null_term={line['null_term']})")
    for c in cells:
        m = cells[c]["faces"]["v2_main"]
        g1 = verdicts[c]["pass_v2"]
        print(f"  {c}: sharpe={m['sharpe']} ann={m['ann_ret']} maxDD={m['max_dd']} "
              f"turnover={m['turnover_per_yr']}/yr g1'={g1}")
    for c in passers:
        print(f"  G2 {c}: {g2[c].get('eligible_v2')} (dsr={g2[c].get('dsr')} "
              f"pbo={g2[c].get('pbo')})")
    return 0


# ---------------------------------------------------------------- selftest (G3)

def cmd_selftest(_):
    sys.stdout.reconfigure(encoding="utf-8")
    fails = []

    def check(fid, cond, detail=""):
        print(f"  [{fid}] {'PASS' if cond else 'FAIL'} {detail}")
        if not cond:
            fails.append(fid)

    # F1 exact linear series: score = slope*252*R^2 with R^2=1
    y = 100.0 * np.exp(0.001 * np.arange(SR2_WIN + 5))
    sc = _rolling_ols_score(y, SR2_WIN)
    check("F1-linear-score", abs(sc[-1] - 0.252) < 1e-9, f"{sc[-1]:.6f}")

    # F2 vectorized OLS == per-day polyfit reference (algorithmic identity)
    rng = np.random.default_rng(7)
    y2 = 100.0 * np.exp(np.cumsum(rng.normal(0.0005, 0.01, 60)))
    sc2 = _rolling_ols_score(y2, SR2_WIN)
    ref_ok = True
    for t in range(SR2_WIN - 1, len(y2)):
        w = np.log(y2[t - SR2_WIN + 1:t + 1])
        p = np.polyfit(np.arange(SR2_WIN), w, 1)
        slope = p[0]
        pred = np.polyval(p, np.arange(SR2_WIN))
        r2 = 1.0 - ((w - pred) ** 2).sum() / ((w - w.mean()) ** 2).sum()
        if abs(sc2[t] - slope * 252.0 * r2) > 1e-9:
            ref_ok = False
    check("F2-polyfit-identity", ref_ok)

    # synthetic universe for engine tests (35 days, 6 members, param windows)
    dts = [str(d.date()) for d in pd.bdate_range("2021-01-04", periods=35)]
    px = {}
    base = {"S1": 10.0, "S2": 20.0, "S3": 30.0, "S4": 40.0, "S5": 50.0, "S6": 60.0}
    for s, b in base.items():
        col = []
        for i in range(35):
            drift = {"S1": 1.002, "S2": 1.000, "S3": 0.999,
                     "S4": 1.0015, "S5": 0.998, "S6": 1.0005}[s]
            col.append(round(b * drift ** i, 4))
        px[s] = col
    close_df = pd.DataFrame(px, index=dts)
    open_px = {s: [v * 0.999 for v in px[s]] for s in px}
    close_px = {s: list(px[s]) for s in px}
    advz = {s: [float("nan")] * 35 for s in px}
    cret = [0.0001] * 35

    # F3 eligibility + NaN exclusion (min_hist param, NaN not zero-filled)
    elig = eligibility_matrix(close_df, min_hist=5)
    sc_df = pd.DataFrame({s: _rolling_ols_score(px[s], 3) for s in px}, index=dts)
    t_ok = True
    for t in range(5, 35):
        row_ok = all(elig.iloc[t][s] == (t + 1 >= 5) for s in px)
        if not row_ok:
            t_ok = False
    check("F3-eligibility-count", t_ok)
    px_nan = {s: list(px[s]) for s in px}
    px_nan["S2"][10] = float("nan")
    sc_nan = _rolling_ols_score(px_nan["S2"], 3)
    check("F3-nan-window-excluded", not np.isfinite(sc_nan[11]) and
          not np.isfinite(sc_nan[10]) and np.isfinite(sc_nan[13]),
          f"t10={sc_nan[10]} t11={sc_nan[11]} t13={sc_nan[13]}")

    # F4 min-hold protection: S1 enters, drops out of top at day e+2 -> held
    # until clock >= 8, then exits at a later check (engine trace verified)
    scores = {s: list(sc_df[s]) for s in px}
    plan4 = {}
    for t in range(6, 35):
        top = ["S1", "S4", "S6"] if t < 12 else ["S4", "S6", "S3"]
        w = 1.0 / 3
        plan4[t] = {"members": list(top), "weights": {s: w for s in top},
                   "cash_weight": 0.0, "top3": list(top), "state": "t"}
    r4 = simulate_rotation(dts, open_px, close_px, advz, cret, plan4, 1e6,
                           cost_mult=1.0, start_idx=0, min_hold=8)
    tr = r4["holdings_track"]
    h_11 = tr[11][0] if 11 in tr else None
    h_20 = tr[20][0] if 20 in tr else None
    check("F4-minhold-protects", h_11 is not None and "S1" in h_11,
          f"day11 holdings={h_11}")
    # S1 entered day 6 (clock=6), first check with clock>=8 and out-of-top
    # is day 14 (S1 out of top from day 12): at day 14 clock=8 -> exits
    h_14 = tr[14][0] if 14 in tr else None
    check("F4-minhold-exits-at-8", h_14 is not None and "S1" not in h_14,
          f"day14 holdings={h_14}")

    # F5 weekly cadence: first trading day of ISO week (holiday gap -> Tue)
    dts5 = [str(d.date()) for d in pd.bdate_range("2021-01-25", periods=25)]
    # inject a missing Monday: drop 2021-02-15 (Mon) so week starts Tue 16th
    dts5b = [d for d in dts5 if d != "2021-02-15"]
    idx5 = _check_day_indices(dts5b, "weekly")
    firsts = [dts5b[i] for i in idx5]
    check("F5-weekly-first-day", firsts == ["2021-02-01", "2021-02-08",
                                           "2021-02-16", "2021-02-22"],
          f"firsts={firsts}")
    idx5m = _check_day_indices(dts5b, "monthly")
    check("F5-monthly-first-day", dts5b[idx5m[0]] == "2021-02-01",
          f"first={dts5b[idx5m[0]]}")

    # F6 T+1 open lag: ranking flip at close of day t -> exec day t+1
    plan6 = {}
    for t in range(6, 35):
        top = ["S1", "S4", "S6"] if t < 20 else ["S4", "S6", "S3"]
        w = 1.0 / 3
        plan6[t] = {"members": list(top), "weights": {s: w for s in top},
                    "cash_weight": 0.0, "top3": list(top), "state": "t"}
    r6 = simulate_rotation(dts, open_px, close_px, advz, cret, plan6, 1e6,
                           cost_mult=1.0, start_idx=0, min_hold=0)
    tr6 = r6["holdings_track"]
    check("F6-lag-trade-next-open", ("S3" not in tr6[19][0]) and
          ("S3" in tr6[20][0]), f"t19={tr6[19][0]} t20={tr6[20][0]}")

    # F7 DM plan: 2 passers -> cash share; 0 passers -> 511260
    rel = pd.DataFrame({s: [0.05 if s == "S1" else (-0.02 if s == "S2" else 0.01)
                           for _ in range(35)] for s in px}, index=dts)
    ab = pd.DataFrame({s: [0.06 if s in ("S1", "S4") else -0.05 for _ in range(35)]
                       for s in px}, index=dts)
    rel.loc["2021-01-25", "S1"] = 0.05
    plan_dm = build_plan("MF-DM", close_df, cret, elig=elig, rel20=rel, abs60=ab)
    st_first = plan_dm[min(plan_dm)]
    check("F7-dm-2passers-cash", st_first["members"] == ["S1", "S4"] and
          abs(st_first["cash_weight"] - 1.0 / 3) < 1e-9,
          f"{st_first['members']} cw={st_first['cash_weight']}")
    ab0 = pd.DataFrame({s: [-0.05 for _ in range(35)] for s in px}, index=dts)
    plan_dm0 = build_plan("MF-DM", close_df, cret, elig=elig, rel20=rel, abs60=ab0)
    check("F7-dm-0passers-defense",
          plan_dm0[min(plan_dm0)]["members"] == [DEFENSE])

    # F8 GEM: winner + cash-fallback (param win, 3 monthly execs)
    dts8 = [str(d.date()) for d in pd.bdate_range("2021-01-04", periods=65)]
    cl8 = pd.DataFrame({s: [base[s] * (1.002 if s == "S1" else 0.999) ** i
                            for i in range(65)] for s in base}, index=dts8)
    cash8 = pd.Series([0.0001] * 65, index=dts8)
    gem_cum8 = {leg: (cl8[leg] / cl8[leg].shift(10) - 1.0).tolist()
                for leg in ("S1", "S4")}
    cc8 = cash_cum252(cash8, win=10)
    plan_g = {}
    for t in _check_day_indices(dts8, "monthly"):
        i = t - 1
        a, b, c = gem_cum8["S1"][i], gem_cum8["S4"][i], cc8[i]
        if not all(np.isfinite(v) for v in (a, b, c)):
            continue
        win_leg = "S1" if a >= b else "S4"
        members = [win_leg] if max(a, b) >= c else [DEFENSE]
        plan_g[t] = {"members": members, "weights": {m: 1.0 for m in members},
                     "cash_weight": 0.0, "top3": [], "state": "gem"}
    check("F8-gem-winner-or-defense", len(plan_g) >= 3 and
          all(v["members"][0] in ("S1", "S4", DEFENSE) for v in plan_g.values())
          and plan_g[min(plan_g)]["members"] == ["S1"],
          f"n={len(plan_g)} first={plan_g[min(plan_g)]['members']}")

    # F9 cost identity vs alloc_backtest + envelope
    from alloc_backtest import side_cost_v2 as sv2
    g9 = 200_000.0
    check("F9-cost-identity", abs(1.0 * sv2(g9, 1e9) - side_cost_v2(g9, 1e9)) < 1e-12
          and abs(2.0 * sv2(g9, 1e9) - 2 * sv2(g9, 1e9)) < 1e-12)
    check("F9-envelope", est_leg_cost(g9) >= sv2(g9, float("nan")))

    # F10 repo accrual identity: no-plan window grows cash at (1+r)^n
    r10 = simulate_rotation(dts, open_px, close_px, advz, [0.001] * 35, {},
                            1_000_000.0, cost_mult=1.0, start_idx=0, min_hold=0)
    exp10 = 1_000_000.0 * (1.001 ** 10)
    check("F10-cash-accrual", abs(float(r10["eq"].iloc[9]) - exp10) < 1e-6,
          f"{float(r10['eq'].iloc[9]):.2f} vs {exp10:.2f}")

    # F11 determinism: null plan + cell double-run byte-identity
    p1 = build_null_plan(close_df, elig, "daily", 59000, 35)
    p2 = build_null_plan(close_df, elig, "daily", 59000, 35)
    p3 = build_null_plan(close_df, elig, "daily", 59001, 35)
    j1 = json.dumps({str(k): v for k, v in p1.items()}, sort_keys=True)
    j2 = json.dumps({str(k): v for k, v in p2.items()}, sort_keys=True)
    j3 = json.dumps({str(k): v for k, v in p3.items()}, sort_keys=True)
    check("F11-null-seed-determinism", j1 == j2 and j1 != j3)
    r11a = simulate_rotation(dts, open_px, close_px, advz, cret, plan4, 1e6,
                             cost_mult=1.0, start_idx=0, min_hold=8)
    r11b = simulate_rotation(dts, open_px, close_px, advz, cret, plan4, 1e6,
                             cost_mult=1.0, start_idx=0, min_hold=8)
    check("F11-engine-byte-identity",
          json.dumps(list(r11a["eq"]), sort_keys=True) ==
          json.dumps(list(r11b["eq"]), sort_keys=True)
          and r11a["n_trades"] == r11b["n_trades"])

    # F12 metrics hand-check: Sharpe + maxDD + turnover
    eq12 = pd.Series([100.0, 110.0, 104.5, 115.0, 109.25],
                     index=["2021-01-04", "2021-01-05", "2021-01-06",
                            "2021-01-07", "2021-01-08"])
    m12 = cell_metrics(eq12, 5, 3, 10.0)
    r12 = eq12.pct_change().dropna()
    sd12 = float(r12.std())
    exp_sh = float(r12.mean()) / sd12 * math.sqrt(252.0)
    check("F12-sharpe-hand", abs(m12["sharpe"] - round(exp_sh, 6)) < 1e-9,
          f"{m12['sharpe']}")
    check("F12-maxdd-hand", abs(m12["max_dd"] - (104.5 / 110.0 - 1.0)) < 1e-9)
    check("F12-turnover-hand", abs(m12["turnover_per_yr"] - 5.0 / (5 / 252.0)) < 1e-6)

    # F13 merge clause: connected components over |corr|>=0.7
    rets = {"A": pd.Series([0.01, 0.02, -0.005, 0.011, 0.004]),
            "B": pd.Series([0.010, 0.019, -0.006, 0.012, 0.005]),   # ~A
            "C": pd.Series([0.004, -0.003, 0.002, -0.001, 0.0005])}  # ~uncorr
    dfc = pd.DataFrame(rets)
    fixture_ok = (abs(dfc["A"].corr(dfc["B"])) >= 0.7
                  and abs(dfc["A"].corr(dfc["C"])) < 0.7
                  and abs(dfc["B"].corr(dfc["C"])) < 0.7)
    pairs, comps = batch_corr_and_merge(rets)
    check("F13-merge-components", fixture_ok and len(comps) == 2 and
          sorted(comps[0] + comps[1]) == ["A", "B", "C"] and
          sorted(comps[0]) in (["A", "B"], ["C"]),
          f"fixture_ok={fixture_ok} comps={comps}")

    # F14 cash_cum252 rolling product identity
    cs = pd.Series([0.01, 0.02, 0.03, 0.04], index=dts[:4])
    cc14 = cash_cum252(cs, win=2)
    check("F14-cash-cum", abs(cc14[1] - (1.01 * 1.02 - 1)) < 1e-12 and
          abs(cc14[3] - (1.03 * 1.04 - 1)) < 1e-12 and not np.isfinite(cc14[0]))

    # F15 NaN-head production pairing (r182 live-fire: leading NaN heads
    # survive ffill in production panels; 0*NaN=NaN poisoned equity and
    # crashed the first rebalance at int(NaN) -- complete-data hermetic
    # panels lied green, R117 hermetic-production pairing law). Fixture
    # mirrors the live-fire shape: a late lister in the universe with a
    # NaN price head, rebalance days both before and after its listing.
    px_l = {s: list(px[s]) for s in px}
    open_l = {s: list(open_px[s]) for s in px}
    close_l = {s: list(close_px[s]) for s in px}
    LATE, head15 = "S7", 12
    px_l[LATE] = [float("nan")] * head15 + \
        [round(70.0 * 1.001 ** i, 4) for i in range(35 - head15)]
    open_l[LATE] = [float("nan")] * head15 + \
        [round(v * 0.999, 4) for v in px_l[LATE][head15:]]
    close_l[LATE] = list(px_l[LATE])
    advz[LATE] = [float("nan")] * 35
    plan15 = {}
    for t in range(6, 35):
        members = ["S1", "S4", "S6"] if t < 12 else ["S4", "S6", LATE]
        plan15[t] = {"members": members,
                     "weights": {s: 1.0 / 3 for s in members},
                     "cash_weight": 0.0, "top3": members, "state": "t"}
    try:
        r15 = simulate_rotation(dts, open_l, close_l, advz, cret, plan15,
                                1e6, cost_mult=1.0, start_idx=0, min_hold=0)
        eq15_ok = bool(np.isfinite(r15["eq"]).all())
        no_early_hold = all(
            r15["holdings_track"][t][1].get(LATE, 0.0) == 0.0
            for t in r15["holdings_track"] if t < head15)
        late_entered = any(
            r15["holdings_track"][t][1].get(LATE, 0.0) > 0.0
            for t in r15["holdings_track"] if t >= head15)
    except Exception as exc:            # live-fire face: unhandled NaN crash
        eq15_ok = no_early_hold = late_entered = False
        print(f"      F15 exception: {exc!r}")
    check("F15-nanhead-pairing",
          eq15_ok and no_early_hold and late_entered,
          f"eq_finite={eq15_ok} unheld_pre_list={no_early_hold} "
          f"entered_post_list={late_entered}")

    print(f"selftest: {'ALL PASS' if not fails else 'FAIL ' + str(fails)}")
    return 0 if not fails else 1


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("run")
    sub.add_parser("selftest")
    args = ap.parse_args()
    if args.cmd == "run":
        return cmd_run(args)
    return cmd_selftest(args)


if __name__ == "__main__":
    sys.exit(main())
