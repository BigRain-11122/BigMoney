# -*- coding: utf-8 -*-
"""ALLOC_LINE_S2 s3 backtest runner (T-2026-09-25-59 s3, lane bm-b r175 claim).

Pre-registered in research/allocation/ALLOC_LINE_S2_PREREG.md BEFORE any run
(frozen r176 pre-run, R99 law). Iron rules: no threshold tuning, verdicts
final (ALLOC_S2_REFINALIZE=1 = only redo path), cutoff lockbox 2026-09-22
(post-cutoff bars never flow back), costs always on, determinism double-run
byte-identical (zero wall-clock fields in results JSON).

Judgment face = CEO order O-20260925-1145 sec.1 four allocation metrics
(post-cost annualized return / max drawdown / Calmar / monthly positive
rate) -- NOT G1'/G2 (three-lines-three-judgments law, prereg sec.4).

Cells (prereg sec.3 frozen weights; 7-cell batch, N_eff=7):
  P1 all-weather CN 30/40/15/15cash | P2 simplified risk parity (rolling
  126d inverse-vol, cap 50% iterative<=5, warmup=equal-weight frozen per
  sec.5.6) | P3 60-40 monthly | P3B 60-40 daily 5pp threshold twin |
  P4 fixed-income-plus 80-20 | P5 dividend-retirement 50/40/10 (PENDING
  off-hours 510880 pull -> data/ext_slots/etf_daily/510880.csv, same CSV
  schema as data/daily; absent or window-inadequate = honest 6-cell
  interim, NO ledger append, finalize only at 7/7) | P6 three-pockets
  10cash/60bond-mix/30QDII.

Costs (prereg sec.3, knowledge/rules.py 承制面): per side per leg =
  max(gross*2.5bp, 5 yuan commission floor) + gross*handling(0.0341bp)
  + gross*supervision(0.2bp) + gross*ADV20-tiered slippage(2/5/10bp;
  missing ADV falls back 10bp tier); lot=100 shares; 1% ADV(20d) fill cap
  (refused legs disclosed); cross-border ETFs annotated T+1-conservative
  (design has no same-day round-trip anyway); V1 13.041bp flat dual-track
  + cost x2 stress = descriptive disclosure faces only (NOT new cells).
Cash leg: repo_daily.csv rate/100/252 daily accrual (CASH_LEG carrier
read-only reuse; no major_bear parking -- allocation line = zero timing).
Reserve convention (frozen pre-run): trade targets computed on
(equity - cost_reserve) with per-leg envelope estimate
max(0.0013541*g, 5+0.0010541*g) so cash never goes negative; lot/cost
residual stays in cash (disclosed).

Benchmarks: STOCK100 / BOND100 / BENCH-6040-NOREBAL + structural null
NULL-EW5 (equal-weight buy-hold of the 5-asset common pool; zero-signal
line has no random null by construction, prereg sec.3). One V2 entry cost.

Sensitivity (sec.3 iron law, 另列非新格): inception offset +1/+2 months
feasible; -1/-2 structurally unavailable (panel head = window head,
data/daily starts 2020-01-02) -- honest disclosure.

Hard gates (any FAIL = batch VOID, exit 2): panel completeness >=95%
non-null per asset at cutoff; selftest must pass before pool burn.
Pending legs disclosed honestly: D6 vs-trader-sleeve corr (t35 series
insufficient + zero overlap with frozen window); P5 window backfill.

Usage: python scripts/alloc_backtest.py run | selftest
Products: results/allocation/ALLOC_S2_BACKTEST.json (+ .csv) + per-cell
checkpoints results/alloc_s2_cells/<cell>.json (config-sha keyed resume,
finalize reads checkpoints never in-memory state, T-33 law) + trials-ledger
append + gate_attrition row at 7/7 finalize (single-shot guard).
"""
import argparse
import json
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd

import science_gates as sg
from knowledge import rules as krules

TICKET = "T-2026-09-25-59"
CUTOFF = "2026-09-22"              # prereg sec.2 forward lockbox (pinned)
START = "2020-01-02"               # prereg sec.2 window head
CAPITAL = 1_000_000.0              # product face: CNY 1,000,000 per account
DATA = os.path.join("data", "daily")
REPO = os.path.join("Money0923", "data", "repo_daily.csv")
P5_SLOT = os.path.join("data", "ext_slots", "etf_daily", "510880.csv")
OUT_JSON = os.path.join("results", "allocation", "ALLOC_S2_BACKTEST.json")
OUT_CSV = os.path.join("results", "allocation", "ALLOC_S2_BACKTEST.csv")
CELLS_DIR = os.path.join("results", "alloc_s2_cells")
ATT_JSON = os.path.join("results", "gate_attrition.json")
LOG_PATH = os.path.join("results", "allocation", "alloc_backtest.log")
BATCH_CELLS = 7                     # prereg sec.0 N_eff (P5 included when data lands)

RISK = ["510300", "511010", "518880", "513100", "513500"]
P2_POOL = ["510300", "511010", "518880"]
P5_SYMS = ["510880", "511010", "518880"]

WEIGHTS = {
    "ALLOC-P1": {"510300": 0.30, "511010": 0.40, "518880": 0.15, "CASH": 0.15},
    "ALLOC-P3": {"510300": 0.60, "511010": 0.40},
    "ALLOC-P3B": {"510300": 0.60, "511010": 0.40},
    "ALLOC-P4": {"511010": 0.80, "510300": 0.20},
    "ALLOC-P5": {"510880": 0.50, "511010": 0.40, "518880": 0.10},
    "ALLOC-P6": {"CASH": 0.10, "511010": 0.40, "510300": 0.20,
                 "513100": 0.15, "513500": 0.15},
}
BENCH = {
    "BENCH-STOCK100": {"510300": 1.0},
    "BENCH-BOND100": {"511010": 1.0},
    "BENCH-6040-NOREBAL": {"510300": 0.60, "511010": 0.40},
}
NULL_NAME = "NULL-EW5"              # equal-weight buy-hold of RISK pool
P3B_THRESHOLD = 0.05                 # prereg sec.3 daily 5pp deviation reset
P2_VOL_WIN = 126                    # prereg sec.3: 126 daily returns strictly before update day
P2_CAP = 0.50
P2_CAP_ROUNDS = 5
P2_RULE_LABEL = "rolling-126d inverse-vol, cap 50% iter<=5, warmup=EW (frozen sec.5.6)"
V1_FLAT_SIDE = 0.0013041             # 13.041bp flat (rules.py COST_BASIS_V1 face)
NAMED_EVENT_DAYS = ("2020-07-06", "2024-09-24", "2024-09-26")  # prereg sec.5
T1_CONSERVATIVE = ("513100", "513500")  # cross-border ETFs, conservative annotation

FEE = krules.FeeSchedule()
EST_RATE_MAX = 0.0013541            # envelope: 2.5bp comm + handling + superv + 10bp slip cap
EST_MIN_ADD = 0.0010541             # envelope tail for sub-floor legs


def _log(msg):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as fh:
        fh.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}\n")


def _r6(x):
    return None if x is None or not np.isfinite(x) else round(float(x), 6)


# ---------------------------------------------------------------- cost faces

def side_cost_v2(gross, adv20):
    """Per-side cost on one trade leg, V2 basis (prereg sec.3)."""
    if gross <= 0:
        return 0.0
    slip = krules.cost_v2_slippage(adv20)
    comm = max(gross * FEE.commission_rate, FEE.commission_min)
    return comm + gross * (FEE.handling_fee + FEE.supervision_fee) + gross * slip


def side_cost_v1(gross, adv20):
    """V1 flat 13.041bp dual-track disclosure face (no commission floor)."""
    return gross * V1_FLAT_SIDE if gross > 0 else 0.0


def side_cost_x2(gross, adv20):
    """x2 stress face: every V2 component doubled (comm rate AND floor)."""
    if gross <= 0:
        return 0.0
    slip = krules.cost_v2_slippage(adv20)
    comm = max(gross * FEE.commission_rate * 2.0, FEE.commission_min * 2.0)
    return comm + gross * 2.0 * (FEE.handling_fee + FEE.supervision_fee) + gross * 2.0 * slip


COST_FACES = {"v2": side_cost_v2, "v1": side_cost_v1, "x2": side_cost_x2}


def est_leg_cost(gross):
    """Frozen reserve envelope (docstring): guarantees cash >= 0 post-trade."""
    if gross <= 0:
        return 0.0
    return max(EST_RATE_MAX * gross, FEE.commission_min + EST_MIN_ADD * gross)


def p2_invvol_weights(rets_window):
    """sec.3: w ~ 1/sigma (annualized), cap 50% iterative <=5 rounds."""
    vol = rets_window.std() * math.sqrt(252.0)
    if bool(vol.isna().any() or (vol <= 0).any()):
        vol = pd.Series(1.0, index=rets_window.columns)
    inv = 1.0 / vol
    w = inv / inv.sum()
    for _ in range(P2_CAP_ROUNDS):
        over = w[w > P2_CAP + 1e-12]
        if over.empty:
            break
        w[over.index] = P2_CAP
        rest_idx = [s for s in inv.index if w[s] < P2_CAP]
        if not rest_idx:
            break
        rest = inv[rest_idx]
        w[rest_idx] = rest / rest.sum() * (1.0 - P2_CAP * len(over))
    return (w / w.sum()).to_dict()


# ---------------------------------------------------------------- engine

def simulate(dates, prices, adv20_map, cash_ret, weights, capital,
             mode="monthly", cost_fn=side_cost_v2, p2=False, start_idx=0):
    """Daily share-based sim. mode: monthly | daily-threshold | buyhold.

    weights: {sym: w} with 'CASH' as explicit residual leg (never traded).
    p2=True overrides weights monthly from rolling vol (warmup equal-weight).
    adv20_map: {sym: [adv20 per day]} (NaN = 10bp-tier fallback).
    start_idx: inception offset (sensitivity face; 0 = window head).
    """
    syms = list(P2_POOL) if p2 else [s for s in weights if s != "CASH"]
    n_days = len(dates)
    holdings = {s: 0.0 for s in syms}
    cash = float(capital)
    trades = 0
    turnover = 0.0
    total_cost = 0.0
    comm_floor_hits = 0
    fill_refusals = 0
    equity_path = []
    prev_month = None

    for t in range(start_idx, n_days):
        d = dates[t]
        cash *= (1.0 + float(cash_ret[t]))          # accrual on held balance
        px_t = {s: prices[s][t] for s in syms}
        asset_val = {s: holdings[s] * px_t[s] for s in syms}
        equity = cash + sum(asset_val.values())
        m = d[:7]
        is_month_first = (prev_month is not None and m != prev_month)
        prev_month = m

        if t == start_idx:
            w = ({s: 1.0 / len(P2_POOL) for s in P2_POOL} if p2 else dict(weights))
        elif p2 and is_month_first:
            lo = max(1, t - P2_VOL_WIN)
            rets = {s: [prices[s][i] / prices[s][i - 1] - 1.0
                        for i in range(lo, t)] for s in P2_POOL}
            win = pd.DataFrame(rets)
            w = (p2_invvol_weights(win) if len(win) >= P2_VOL_WIN
                 else {s: 1.0 / len(P2_POOL) for s in P2_POOL})
        elif mode == "monthly" and is_month_first:
            w = dict(weights)
        elif mode == "daily-threshold" and t > start_idx:
            cur_w = {s: (asset_val[s] / equity if equity > 0 else 0.0) for s in syms}
            w = (dict(weights) if any(
                abs(cur_w.get(s, 0.0) - weights.get(s, 0.0)) >= P3B_THRESHOLD
                for s in syms) else None)
        else:
            w = None

        if w is not None:
            nominal = {s: w.get(s, 0.0) * equity - asset_val[s] for s in syms}
            reserve = sum(est_leg_cost(abs(nominal[s])) for s in syms)
            equity_adj = equity - reserve
            for s in syms:
                target_val = w.get(s, 0.0) * equity_adj
                delta = target_val - asset_val[s]
                if abs(delta) < px_t[s]:
                    continue                            # below one share
                shares = int(abs(delta) / px_t[s] // 100) * 100
                if shares <= 0:
                    continue
                gross = shares * px_t[s]
                adv20 = adv20_map.get(s)
                a = adv20[t] if adv20 is not None else float("nan")
                if np.isfinite(a) and gross > krules.ADV_FILL_CAP_RATE * a:
                    fill_refusals += 1                  # 1% ADV cap: refused
                    continue
                if gross * FEE.commission_rate < FEE.commission_min:
                    comm_floor_hits += 1
                cost = cost_fn(gross, a)
                if delta > 0:
                    cash -= gross + cost
                    holdings[s] += shares
                else:
                    cash += gross - cost
                    holdings[s] -= shares
                trades += 1
                turnover += gross
                total_cost += cost
            equity = cash + sum(holdings[s] * px_t[s] for s in syms)

        equity_path.append(equity)

    eq = pd.Series(equity_path, index=dates[start_idx:])
    return {"eq": eq, "trades": trades, "turnover": turnover,
            "total_cost": total_cost, "comm_floor_hits": comm_floor_hits,
            "fill_refusals": fill_refusals}


def four_metrics(eq):
    """O-1145 sec.1 face: ann / maxDD / Calmar / monthly positive rate."""
    yrs = len(eq) / 252.0
    ann = float(eq.iloc[-1] / eq.iloc[0]) ** (1.0 / yrs) - 1.0 if yrs > 0 else 0.0
    dd = float((eq / eq.cummax() - 1.0).min())
    calmar = (ann / abs(dd)) if dd < 0 else None
    month_last = eq.groupby(eq.index.str[:7]).last()
    mret = month_last.pct_change().dropna()
    pos_rate = float((mret > 0).mean()) if len(mret) else None
    return {"ann_ret": _r6(ann), "max_dd": _r6(dd), "calmar": _r6(calmar),
            "monthly_pos_rate": _r6(pos_rate), "n_months": int(len(mret)),
            "years": _r6(yrs)}


def daily_returns(eq):
    return eq.pct_change().fillna(0.0)


def extreme_days(r):
    out = {"worst_3": [], "named_events": {}}
    if len(r) == 0:
        return out
    for d, v in r.sort_values().head(3).items():
        out["worst_3"].append({"date": d, "ret": _r6(v)})
    for d in NAMED_EVENT_DAYS:
        if d in r.index:
            out["named_events"][d] = _r6(r.loc[d])
    return out


# ---------------------------------------------------------------- data faces

def load_symbol_csv(path):
    df = pd.read_csv(path)
    df["date"] = df["date"].astype(str)
    s = df.set_index("date")
    return s[s.index <= CUTOFF]


def load_panel(symbols):
    px, amt = {}, {}
    for sym in symbols:
        df = load_symbol_csv(os.path.join(DATA, f"{sym}.csv"))
        px[sym] = df["close"]
        amt[sym] = df["amount"]
    panel = pd.DataFrame(px).sort_index()
    panel = panel[panel.index >= START]
    amounts = pd.DataFrame(amt).reindex(panel.index)
    adv = {sym: amounts[sym].rolling(20).mean() for sym in symbols}
    return panel, adv


def load_repo(panel_index):
    repo = pd.read_csv(REPO)
    repo["date"] = repo["date"].astype(str)
    rs = repo.set_index("date")["rate"].astype(float)
    rs = rs[rs.index <= CUTOFF]
    daily = rs / 100.0 / 252.0
    return daily.reindex(panel_index).ffill().fillna(0.0)


def completeness_gate(panel, symbols):
    rows, ok = {}, True
    for sym in symbols:
        col = panel[sym]
        ratio = float(col.notna().sum()) / len(col) if len(col) else 0.0
        rows[sym] = {"rows": int(len(col)), "non_null": int(col.notna().sum()),
                     "ratio": _r6(ratio)}
        if ratio < 0.95:
            ok = False
    return ok, rows


def config_sha(weights, mode, p2, capital, start, cutoff):
    import hashlib
    cfg = json.dumps({"w": weights, "mode": mode, "p2": p2,
                      "capital": capital, "start": start, "cutoff": cutoff},
                     sort_keys=True)
    return hashlib.sha256(cfg.encode()).hexdigest()[:16]


def cell_file(name):
    return os.path.join(CELLS_DIR, f"{name}.json")


def load_valid_cell(name, sha):
    p = cell_file(name)
    if not os.path.exists(p):
        return None
    try:
        j = json.load(open(p, encoding="utf-8"))
    except Exception:
        return None
    return j if j.get("config_sha") == sha else None


def _month_shift(ym, k):
    """year-month string shifted by k months (calendar arithmetic)."""
    t = int(ym[:4]) * 12 + (int(ym[5:7]) - 1) + k
    return f"{t // 12:04d}-{t % 12 + 1:02d}"


def run_cell_faces(name, weights, dates, prices, adv20_map, cash_ret,
                   mode, p2):
    """All faces for one cell: v2 main (+extreme/month-end) + v1 + x2 +
    inception offsets +1/+2. Checkpoint-resumable via config sha."""
    sha = config_sha(weights if not p2 else P2_RULE_LABEL, mode, p2,
                     CAPITAL, START, CUTOFF)
    cached = load_valid_cell(name, sha)
    if cached is not None:
        _log(f"cell {name}: checkpoint valid (sha {sha}), resume-load")
        return cached

    base = simulate(dates, prices, adv20_map, cash_ret, weights, CAPITAL,
                    mode=mode, cost_fn=side_cost_v2, p2=p2, start_idx=0)
    m_v2 = four_metrics(base["eq"])
    faces = {"v2_main": m_v2}
    for face, fn in (("v1_flat", side_cost_v1), ("cost_x2", side_cost_x2)):
        r = simulate(dates, prices, adv20_map, cash_ret, weights, CAPITAL,
                     mode=mode, cost_fn=fn, p2=p2, start_idx=0)
        faces[face] = four_metrics(r["eq"])
    offs = {}
    base_ym = dates[0][:7]
    for k in (1, 2):
        target_m = _month_shift(base_ym, k)
        try:
            idx = next(i for i, d in enumerate(dates) if d[:7] == target_m)
        except StopIteration:
            offs[f"plus_{k}"] = {"unavailable": f"no trading day in {target_m}"}
            continue
        r = simulate(dates, prices, adv20_map, cash_ret, weights, CAPITAL,
                     mode=mode, cost_fn=side_cost_v2, p2=p2, start_idx=idx)
        offs[f"plus_{k}"] = four_metrics(r["eq"])
    month_end_eq = [[d, _r6(float(v))] for d, v in
                    base["eq"].groupby(base["eq"].index.str[:7]).last().items()]
    out = {
        "config_sha": sha,
        "weights": (P2_RULE_LABEL if p2 else weights),
        "mode": mode,
        "faces": faces,
        "start_offset_sensitivity": offs,
        "month_end_equity_cny": month_end_eq,
        "trades_summary": {
            "n_trades": int(base["trades"]),
            "total_cost_cny": _r6(base["total_cost"]),
            "turnover_cny": _r6(base["turnover"]),
            "commission_floor_hits": int(base["comm_floor_hits"]),
            "fill_cap_refusals": int(base["fill_refusals"]),
        },
        "extreme_days": extreme_days(daily_returns(base["eq"])),
    }
    os.makedirs(CELLS_DIR, exist_ok=True)
    with open(cell_file(name), "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    _log(f"cell {name}: simulated + checkpoint written (sha {sha})")
    return out


def run_bench(dates, prices, adv20_map, cash_ret, weights):
    res = simulate(dates, prices, adv20_map, cash_ret, weights, CAPITAL,
                   mode="buyhold", cost_fn=side_cost_v2, p2=False, start_idx=0)
    m = four_metrics(res["eq"])
    m["n_trades"] = int(res["trades"])
    m["total_cost_cny"] = _r6(res["total_cost"])
    return m


# ---------------------------------------------------------------- t35 corr leg

def t35_sleeve_corr(alloc_rets):
    """D6 pre-run leg: corr vs 6 registered trader sleeves (prereg sec.1).
    Honest skip on insufficient sample / zero overlap with frozen window."""
    d = os.path.join("results", "paper_export")
    if not os.path.isdir(d):
        return {"status": "pending_no_series",
                "note": "results/paper_export/ absent"}
    series = {}
    for fn in sorted(os.listdir(d)):
        if not (fn.startswith("export-") and fn.endswith(".json")):
            continue
        try:
            j = json.load(open(os.path.join(d, fn), encoding="utf-8"))
        except Exception:
            continue
        dt = j.get("export_date")
        for tr in j.get("traders", []):
            eqv = tr.get("capital_cny", {}).get("equity")
            if tr.get("trader") and eqv is not None:
                series.setdefault(tr["trader"], {})[dt] = float(eqv)
    out = {"n_traders": len(series)}
    if not series:
        out["status"] = "pending_no_series"
        out["note"] = "no export files with trader equity"
        return out
    overlap = 0
    for pts in series.values():
        r = pd.Series(pts).sort_index().pct_change().dropna()
        overlap = max(overlap, len(r.index.intersection(alloc_rets.index)))
    if overlap < 20:
        first_day = min(min(p) for p in series.values())
        out["status"] = "pending_insufficient_sample"
        out["note"] = (f"t35 series from {first_day}; max overlap with "
                       f"frozen window = {overlap} < 20 trading days "
                       "(prereg sec.1 honest-pending clause; structural note: "
                       "paper starts after window end -> zero overlap until "
                       "a future prereg'd probe face)")
        return out
    per = {}
    for tid, pts in series.items():
        r = pd.Series(pts).sort_index().pct_change().dropna()
        j = pd.concat([r, alloc_rets], axis=1, join="inner").dropna()
        per[tid] = (_r6(float(np.corrcoef(j.iloc[:, 0], j.iloc[:, 1])[0, 1]))
                    if len(j) >= 20 else None)
    out["status"] = "computed"
    out["per_trader"] = per
    return out


# ---------------------------------------------------------------- main run

def cmd_run(_):
    sys.stdout.reconfigure(encoding="utf-8")
    p5_present = os.path.exists(P5_SLOT)
    symbols = list(RISK) + (["510880"] if p5_present else [])
    panel, adv = load_panel(symbols)
    gate_ok, comp = completeness_gate(panel, symbols)
    if not gate_ok:
        print("VOID: panel completeness gate FAILED (<95% non-null):",
              json.dumps(comp))
        return 2
    dates = list(panel.index)
    prices = {s: panel[s].ffill().tolist() for s in symbols}
    p5_usable = p5_present
    if p5_present:
        p5_series = prices["510880"]
        p5_usable = (all(np.isfinite(v) for v in p5_series)
                     and panel["510880"].notna().sum() == len(dates))
        if not p5_usable:
            print("P5 510880 ext-slot data window-inadequate vs batch "
                  "window (first-valid head mismatch or gaps) -> honest "
                  "6-cell interim (prereg sec.2 window clause)")
    adv20_map = {s: adv[s].tolist() for s in symbols}
    cash_ret = load_repo(panel.index).tolist()

    cells_spec = [
        ("ALLOC-P1", WEIGHTS["ALLOC-P1"], "monthly", False),
        ("ALLOC-P2", None, "monthly", True),
        ("ALLOC-P3", WEIGHTS["ALLOC-P3"], "monthly", False),
        ("ALLOC-P3B", WEIGHTS["ALLOC-P3B"], "daily-threshold", False),
        ("ALLOC-P4", WEIGHTS["ALLOC-P4"], "monthly", False),
    ]
    if p5_usable:
        cells_spec.append(("ALLOC-P5", WEIGHTS["ALLOC-P5"], "monthly", False))
    cells_spec.append(("ALLOC-P6", WEIGHTS["ALLOC-P6"], "monthly", False))

    cells = {}
    for name, w, mode, p2 in cells_spec:
        cells[name] = run_cell_faces(name, w, dates, prices, adv20_map,
                                     cash_ret, mode, p2)

    bench = {name: run_bench(dates, prices, adv20_map, cash_ret, w)
             for name, w in BENCH.items()}
    null_w = {s: 1.0 / len(RISK) for s in RISK}
    null_m = run_bench(dates, prices, adv20_map, cash_ret, null_w)

    # D6 batch-internal daily-return corr (main face, deterministic re-sim)
    rets_df = {}
    for name, w, mode, p2 in cells_spec:
        r = simulate(dates, prices, adv20_map, cash_ret,
                     (w if w is not None else {s: None for s in P2_POOL}),
                     CAPITAL, mode=mode, cost_fn=side_cost_v2, p2=p2,
                     start_idx=0)
        rets_df[name] = daily_returns(r["eq"])
    cr = pd.DataFrame(rets_df)
    names = list(cr.columns)
    corr_pairs = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            corr_pairs.append({"pair": f"{names[i]}|{names[j]}",
                               "corr": _r6(float(cr[names[i]].corr(cr[names[j]])))})
    batch_abs = [abs(p["corr"]) for p in corr_pairs if p["corr"] is not None]
    d6_batch_max = max(batch_abs) if batch_abs else None
    d6_pair = next((p["pair"] for p in corr_pairs if p["corr"] is not None
                    and d6_batch_max is not None
                    and abs(abs(p["corr"]) - d6_batch_max) < 1e-9), None)

    sleeve = t35_sleeve_corr(rets_df["ALLOC-P1"])

    n_cells = len(cells)
    finalized = (n_cells == BATCH_CELLS)
    if finalized and os.path.exists(OUT_JSON):
        try:
            prev = json.load(open(OUT_JSON, encoding="utf-8"))
            if prev.get("finalized") and os.environ.get("ALLOC_S2_REFINALIZE") != "1":
                print("finalize refused: OUT_JSON already finalized "
                      "(single-shot guard; ALLOC_S2_REFINALIZE=1 to redo)")
                return 2
        except Exception:
            pass

    led = None
    if finalized:
        led = sg.append_ledger("ALLOC_LINE_S2", BATCH_CELLS,
                               file_name="results/allocation/ALLOC_S2_BACKTEST.json",
                               evidence_cutoff=CUTOFF,
                               note="7 allocation cells, O-1145 four-metric CEO face "
                                    "(no G1/G2 by three-lines law); prereg "
                                    "research/allocation/ALLOC_LINE_S2_PREREG.md frozen r176")
        att = json.load(open(ATT_JSON, encoding="utf-8"))
        att["entries"].append({
            "batch": "ALLOC_LINE_S2", "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
            "kind": "measurement", "cells_ledger_delta": BATCH_CELLS,
            "ledger_total_after": led["total"],
            "gates": {"completeness_pass": True, "p5_included": True,
                      "judgment_face": "O-1145 four-metrics (no G1/G2 by law)"},
            "eliminated": 0,
            "refs": {"results": "results/allocation/ALLOC_S2_BACKTEST.json",
                     "prereg": "research/allocation/ALLOC_LINE_S2_PREREG.md",
                     "ticket": TICKET},
        })
        with open(ATT_JSON, "w", encoding="utf-8") as fh:
            json.dump(att, fh, ensure_ascii=False, indent=1)

    if p5_present and not p5_usable:
        p5_status = "pending_data_window_inadequate"
    elif p5_usable:
        p5_status = "included"
    else:
        p5_status = "pending_data_pull"

    out = {
        "schema": "alloc_s2_backtest_v1",
        "batch": "ALLOC_LINE_S2",
        "ticket": f"{TICKET} s3",
        "prereg": "research/allocation/ALLOC_LINE_S2_PREREG.md (frozen pre-run r176, R99)",
        "evidence_cutoff": CUTOFF,
        "window": {"start": dates[0], "end": dates[-1], "rows": len(dates)},
        "initial_capital_cny": CAPITAL,
        "judgment_face": "O-20260925-1145 sec.1 four allocation metrics post-cost (NOT G1'/G2, three-lines law)",
        "p5_status": p5_status,
        "p5_slot_path": "data/ext_slots/etf_daily/510880.csv (pinned; off-hours fund_etf_hist_em leg, 2.5s pacing + checkpoint per MF spec)",
        "finalized": finalized,
        "n_cells": n_cells,
        "cells": cells,
        "benchmarks": bench,
        "structural_null": null_m,
        "d6": {
            "batch_max_abs_corr": _r6(d6_batch_max),
            "argmax_pair": d6_pair,
            "declared": "ALLOC-P3B = declared rebalance-method A/B twin of ALLOC-P3 (prereg sec.1; static probe face ~1.000 by construction)",
            "vs_trader_sleeves": sleeve,
        },
        "sensitivity_disclosure": {
            "start_offset_plus_months": {
                k: {n: cells[n]["start_offset_sensitivity"][k] for n in cells}
                for k in ("plus_1", "plus_2")},
            "start_offset_minus_months": ("structurally unavailable: panel head "
                                          "= window head (data/daily starts "
                                          "2020-01-02), honest disclosure per "
                                          "prereg sec.3 virtual-start law"),
            "v1_flat_dual_track": {n: cells[n]["faces"]["v1_flat"] for n in cells},
            "cost_x2_stress": {n: cells[n]["faces"]["cost_x2"] for n in cells},
        },
        "descriptive_clauses": {n: {
            "ann_positive": bool(cells[n]["faces"]["v2_main"]["ann_ret"] > 0),
            "monthly_pos_ge_50": bool(
                (cells[n]["faces"]["v2_main"]["monthly_pos_rate"] or 0.0) >= 0.50),
            "x2_direction_flip": bool(
                (cells[n]["faces"]["v2_main"]["ann_ret"] > 0) !=
                (cells[n]["faces"]["cost_x2"]["ann_ret"] > 0)),
        } for n in cells},
        "audit": {
            "data_completeness": comp,
            "missing_asset_days": {s: int(panel[s].isna().sum()) for s in symbols},
            "cost_model": {
                "basis": krules.COST_BASIS_V2,
                "per_side": "max(gross*2.5bp, 5) + gross*handling(0.341bp) + gross*superv(0.2bp) + gross*adv20_tiered_slip(2/5/10bp, nan->10bp)",
                "lot": 100,
                "adv_fill_cap": krules.ADV_FILL_CAP_RATE,
                "v1_flat_side": V1_FLAT_SIDE,
                "t1_conservative_note": ("cross-border ETFs 513100/513500 "
                                         "modeled T+1-conservative (company iron "
                                         "rule); design has no same-day round-trip"),
            },
            "cash_model": "repo_daily.csv rate/100/252 daily accrual, ffill, zero-timing (no major_bear parking)",
            "commission_floor_hits": {n: cells[n]["trades_summary"]["commission_floor_hits"]
                                      for n in cells},
            "fill_cap_refusals": {n: cells[n]["trades_summary"]["fill_cap_refusals"]
                                  for n in cells},
            "determinism": "no wall-clock fields in this JSON; engine deterministic (selftest F8 double-run byte-identity)",
            "reserve_convention": "targets on (equity - cost_reserve), envelope max(0.0013541*g, 5+0.0010541*g); lot/cost residual stays in cash",
        },
        "extreme_days": {n: cells[n]["extreme_days"] for n in cells},
    }
    if led is not None:
        out["trials_ledger"] = led

    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)

    rows = [{"name": n, "face": "v2_main", **cells[n]["faces"]["v2_main"]}
            for n in cells]
    rows += [{"name": n, "face": "bench", **m} for n, m in bench.items()]
    rows.append({"name": NULL_NAME, "face": "structural_null", **null_m})
    pd.DataFrame(rows).to_csv(OUT_CSV, index=False, encoding="utf-8")

    print(f"ALLOC_LINE_S2 s3: cells={n_cells}/{BATCH_CELLS} p5={p5_status} "
          f"finalized={finalized} window={dates[0]}..{dates[-1]} rows={len(dates)}")
    for n in cells:
        m = cells[n]["faces"]["v2_main"]
        print(f"  {n}: ann={m['ann_ret']} maxDD={m['max_dd']} "
              f"calmar={m['calmar']} mpos={m['monthly_pos_rate']}")
    if not finalized:
        print("interim pass: ledger NOT appended; finalize at 7/7 after "
              "510880 pull leg (off-hours)")
    return 0


# ---------------------------------------------------------------- selftest (G3)

def cmd_selftest(_):
    sys.stdout.reconfigure(encoding="utf-8")
    fails = []

    def check(fid, cond, detail=""):
        print(f"  [{fid}] {'PASS' if cond else 'FAIL'} {detail}")
        if not cond:
            fails.append(fid)

    # F1 cost components (pure-function, hand numbers)
    g = 600_000.0
    exp = max(g * 0.00025, 5) + g * (0.0000341 + 0.00002) + g * 0.0002
    check("F1-v2-2bp", abs(side_cost_v2(g, 1e9) - exp) < 1e-9)
    g5 = 10_000.0
    exp5 = max(g5 * 0.00025, 5) + g5 * (0.0000341 + 0.00002 + 0.0005)
    check("F1-v2-5bp", abs(side_cost_v2(g5, 2e8) - exp5) < 1e-9)
    exp10 = 5.0 + g5 * (0.0000341 + 0.00002 + 0.001)
    check("F1-v2-nanfb", abs(side_cost_v2(g5, float("nan")) - exp10) < 1e-9)
    check("F1-v1", abs(side_cost_v1(500_000, None) - 500_000 * 0.0013041) < 1e-9)
    check("F1-x2", abs(side_cost_x2(g5, float("nan")) - 2 * exp10) < 1e-9)
    check("F1-envelope",
          est_leg_cost(g5) >= side_cost_v2(g5, float("nan"))
          and est_leg_cost(g) >= side_cost_v2(g, float("nan")),
          f"{est_leg_cost(g5):.4f} vs {side_cost_v2(g5, float('nan')):.4f}")

    # F2 synthetic inception (hand-computed chain; frozen semantic: accrual
    # at day START on held cash, incl. inception day -- deposit parks in
    # repo until the close-invest; prereg sec.3 CASH_LEG daily accrual)
    dates = ["2021-01-04", "2021-01-05", "2021-01-06", "2021-01-07",
             "2021-02-01", "2021-02-02"]
    prices = {"AAA": [10.0, 10.5, 9.0, 10.0, 11.0, 11.0],
              "BBB": [100.0, 99.0, 101.0, 100.0, 102.0, 102.0]}
    adv20_map = {"AAA": [float("nan")] * 6, "BBB": [float("nan")] * 6}
    cash_ret = [0.0001] * 6
    w = {"AAA": 0.60, "BBB": 0.40}
    res = simulate(dates, prices, adv20_map, cash_ret, w, 1_000_000.0,
                   mode="monthly", cost_fn=side_cost_v2, p2=False, start_idx=0)
    eq0_eff = 1_000_000.0 * 1.0001          # day-1 accrual before trade
    resv = est_leg_cost(0.6 * eq0_eff) + est_leg_cost(0.4 * eq0_eff)
    adj = eq0_eff - resv
    shA = int((0.6 * adj / 10.0) // 100) * 100
    shB = int((0.4 * adj / 100.0) // 100) * 100
    gA, gB = shA * 10.0, shB * 100.0
    costA = side_cost_v2(gA, float("nan"))
    costB = side_cost_v2(gB, float("nan"))
    cash1 = eq0_eff - gA - gB - costA - costB
    eq1 = cash1 * 1.0001 + shA * 10.5 + shB * 99.0
    check("F2-shares", shA == 59_900 and shB == 3_900, f"shA={shA} shB={shB}")
    check("F2-equity-day2", abs(float(res["eq"].iloc[1]) - eq1) < 1e-6,
          f"{float(res['eq'].iloc[1]):.4f} vs {eq1:.4f}")
    check("F2-cash-nonneg", cash1 > 0, f"cash1={cash1:.2f}")

    # F3 monthly rebalance on 2021-02-01 (hand chain, day-5 close prices)
    cash5_pre = cash1 * (1.0001 ** 4)       # accruals on days 2,3,4,5
    vA5, vB5 = shA * 11.0, shB * 102.0
    eq5_pre = cash5_pre + vA5 + vB5
    nomA, nomB = 0.6 * eq5_pre - vA5, 0.4 * eq5_pre - vB5
    resv2 = est_leg_cost(abs(nomA)) + est_leg_cost(abs(nomB))
    adj2 = eq5_pre - resv2
    dA = 0.6 * adj2 - vA5
    shA2 = int(abs(dA) / 11.0 // 100) * 100 * (1 if dA > 0 else -1)
    dB = 0.4 * adj2 - vB5
    shB2 = int(abs(dB) / 102.0 // 100) * 100 * (1 if dB > 0 else -1)
    exp_trades = 2 + (1 if shA2 else 0) + (1 if shB2 else 0)
    cash_after = cash5_pre
    if shA2 > 0:
        cash_after -= abs(shA2) * 11.0 + side_cost_v2(abs(shA2) * 11.0, float("nan"))
    elif shA2 < 0:
        cash_after += abs(shA2) * 11.0 - side_cost_v2(abs(shA2) * 11.0, float("nan"))
    if shB2 > 0:
        cash_after -= abs(shB2) * 102.0 + side_cost_v2(abs(shB2) * 102.0, float("nan"))
    elif shB2 < 0:
        cash_after += abs(shB2) * 102.0 - side_cost_v2(abs(shB2) * 102.0, float("nan"))
    eq5 = cash_after + (shA + shA2) * 11.0 + (shB + shB2) * 102.0
    check("F3-rebalance-equity", abs(float(res["eq"].iloc[4]) - eq5) < 1e-6,
          f"{float(res['eq'].iloc[4]):.4f} vs {eq5:.4f}")
    check("F3-trades-total", res["trades"] == exp_trades,
          f"got={res['trades']} exp={exp_trades}")

    # F4 P3B threshold fires mid-month; monthly does not
    dates4 = ["2021-01-04", "2021-01-05", "2021-01-06"]
    prices4 = {"AAA": [10.0, 10.5, 13.0], "BBB": [100.0, 100.0, 100.0]}
    am4 = {"AAA": [float("nan")] * 3, "BBB": [float("nan")] * 3}
    r_mon = simulate(dates4, prices4, am4, [0.0] * 3, w, 1e6,
                     mode="monthly", cost_fn=side_cost_v2, start_idx=0)
    r_thr = simulate(dates4, prices4, am4, [0.0] * 3, w, 1e6,
                     mode="daily-threshold", cost_fn=side_cost_v2, start_idx=0)
    check("F4-threshold-fires-midmonth", r_thr["trades"] > r_mon["trades"],
          f"thr={r_thr['trades']} mon={r_mon['trades']}")

    # F5 P2 weights: cap + warmup (varied deterministic returns; constant
    # columns would degenerate std=0 -> fallback face, not the cap face)
    rets = pd.DataFrame({
        "510300": [0.01, -0.008] * 63,
        "511010": [0.0005, -0.0004] * 63,
        "518880": [0.004, -0.003] * 63,
    })
    wv = p2_invvol_weights(rets)
    check("F5-cap-50", max(wv.values()) <= 0.5 + 1e-9, f"max={max(wv.values()):.4f}")
    check("F5-sum-1", abs(sum(wv.values()) - 1.0) < 1e-9)
    check("F5-lowvol-heaviest", wv["511010"] > wv["510300"])
    res5 = simulate(dates,
                    {"510300": [10.0] * 6, "511010": [100.0] * 6,
                     "518880": [300.0] * 6},
                    {"510300": [float("nan")] * 6, "511010": [float("nan")] * 6,
                     "518880": [float("nan")] * 6},
                    [0.0] * 6, {}, 1e6, mode="monthly", p2=True, start_idx=0)
    check("F5-warmup-equal-third", res5["trades"] == 3,
          f"trades={res5['trades']}")

    # F6 metrics hand-check (one month-end per month; formula identities)
    eq = pd.Series([100.0, 120.0, 90.0, 99.0],
                   index=["2021-01-29", "2021-02-26", "2021-03-31",
                          "2021-04-30"])
    m = four_metrics(eq)
    check("F6-maxdd", abs(m["max_dd"] - (90.0 / 120.0 - 1.0)) < 1e-9)
    check("F6-calmar-identity",
          m["calmar"] is not None
          and abs(m["calmar"] - m["ann_ret"] / abs(m["max_dd"])) < 1e-5,
          f"calmar={m['calmar']} ann={m['ann_ret']}")
    check("F6-months", m["n_months"] == 3, f"n_months={m['n_months']}")

    # F7 month-first = first TRADING day (2021-05-01 Sat -> 05-06)
    d7 = ["2021-04-30", "2021-05-06", "2021-05-07"]
    p7 = {"AAA": [10.0, 10.0, 10.0], "BBB": [100.0, 100.0, 100.0]}
    am7 = {"AAA": [float("nan")] * 3, "BBB": [float("nan")] * 3}
    r7 = simulate(d7, p7, am7, [0.0] * 3, w, 1e6, mode="monthly",
                  cost_fn=side_cost_v2, start_idx=0)
    check("F7-month-boundary", r7["trades"] >= 2, f"trades={r7['trades']}")

    # F8 determinism double-run byte-identity (synthetic, temp dir)
    import tempfile
    global CELLS_DIR
    with tempfile.TemporaryDirectory() as td:
        keep = CELLS_DIR
        CELLS_DIR = os.path.join(td, "cells")
        try:
            w8 = {"AAA": 0.5, "BBB": 0.5}
            dates8 = ([f"2021-01-{d:02d}" for d in range(4, 30)] +
                      [f"2021-02-{d:02d}" for d in range(1, 25)])
            pr8 = {"AAA": [10.0 + 0.01 * i for i in range(len(dates8))],
                   "BBB": [100.0 - 0.005 * i for i in range(len(dates8))]}
            am8 = {"AAA": [float("nan")] * len(dates8),
                   "BBB": [float("nan")] * len(dates8)}
            cr8 = [0.0001] * len(dates8)
            out1 = run_cell_faces("DET-CELL", w8, dates8, pr8, am8, cr8,
                                  "monthly", False)
            s1 = json.dumps(out1, sort_keys=True)
            os.remove(cell_file("DET-CELL"))
            out2 = run_cell_faces("DET-CELL", w8, dates8, pr8, am8, cr8,
                                  "monthly", False)
            s2 = json.dumps(out2, sort_keys=True)
            check("F8-det-byte-identity", s1 == s2)
        finally:
            CELLS_DIR = keep

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
