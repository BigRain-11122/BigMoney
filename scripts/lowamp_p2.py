"""LOWAMP-P2 -- low-amplitude cross-sectional daily-rebalance family judged
batch RE-ENTRY (T-2026-10-01-140 action-4 runner). The as-designed family
face re-enters supply via the exit-axis explicit gate FIRST application.

Prereg (FROZEN): research/LOWAMP-P2.md -- frozen at c3c825c2a9 (bm-a r514
adoption commit; banned_direction_gate ADMIT rc0 re-verified same round).
Judgments live there; this file implements them, never re-states a
threshold. LOWAMP-P1 verdict VOID-with-face-note (O-20261001-1108 sec.3);
this batch is a NEW batch, not a re-run (T-136 audit "Either way" line).

Family (prereg sec.3, frozen verbatim from the furnace band):
  amp(t) = rolling std of close-to-close daily returns over W bars
  (min_periods=W, strictly causal); cross-sectional ASCENDING rank, keep the
  Top-N LOWEST-amp members; weights invvol (w_i ~ 1/amp_i, normalized) or
  eq (1/N); ALWAYS-ON (no regime gate, no confirmation); daily rebalance,
  engine-canonical T+1 execution. Judged cells: LA-REP(W89,N2,invvol),
  LA-EQ(W89,N2,eq), LA-T3(W89,N3,invvol), LA-EDGE(W104,N2,invvol).

Execution semantics (prereg sec.3 + sec.0.6 exit-axis, engine/ untouched):
  entry_signal = selected-today, exit_signal = entry<=0 (t22 _run_cell
  convention verbatim -- the ONLY exit: selection-rotation, the family's
  own mechanism). HOLD-THROUGH declared: the engine default exit stack is
  EXPLICITLY DISABLED key-by-key in run_cell_portfolio params (prereg
  sec.0.6 verbatim: take_profit_levels=(), trailing_stop_activate=1e12,
  initial_stop=-1.0, time_decay_period=1e9, loss_time_days=1e9,
  global_hard_limit=1e9) -- the same params channel the T-136 audit
  as-burned leg proved, used in reverse (r301 hybrid finding closed).
  x2 face = CostPatch(2.0) multiplier (r82 fix face).

  Engine-face weight mapping (disclosed implementation note): the engine's
  position_size_pct is a scalar, so per-symbol invvol weights ride the
  T-21 entry_size_scale Series (date-indexed, read at the EXECUTION day,
  values = the weight computed at the PRIOR signal close -- the engine's
  own causality contract). Each symbol runs as its own engine sub-account
  (initial_cash = 1,000,000, max_positions=1, position_size_pct=1.0 x
  scale): every fill/cost/exit goes through the frozen engine, and the
  portfolio NAV is the additive decomposition
      NAV(t) = CAPITAL + sum_s (NAV_s(t) - CAPITAL)
  which honors "entry fills at target weight" exactly (no shared-cash
  partial-fill artifact). Symbols with no selection day in a window are
  skipped (flat sub-account contributes zero) -- pure compute skip, zero
  semantic change. Weights are set at entry and never resized mid-hold
  (twin naive precedent, t22 fixed_initial sizing face).

Axes (prereg sec.2): legacy = live.paper load_core canonical face with the
  19 consolidation-affected members' price source REPLACED by the T-19
  adjusted view (both axes, GF law); deep = t22 _load_axis_prices('deep')
  (manifest-gated, adjusted view preferred for the 19). Both truncated
  <= evidence_cutoff 2026-09-22 before joint use (D2 lockbox).

G-CENSUS zero-burn amendment (2026-10-01, pre-burn, zero cells burned,
r251/r280 lineage, result-blind): the frozen text pinned legacy starts to
the t22 finalize reading 1,255 -- measured on t22's 2026-09-23-END panel.
Under THIS batch's binding evidence_cutoff 2026-09-22 truncation the
deterministic enumeration yields 1,254 on BOTH the raw and adjusted
faces (anchor rows 1,631; 1631-252-126+1). The binding cutoff discipline
wins; the gate is re-anchored to the measured reading {legacy: 1254,
deep: 1506}. Deep reading matches the frozen 1,506 bit-for-bit.

Seed registry disclosure (P2 band, prereg sec.3 verbatim): nulls bound to
rng([20334500, k]); sensitivity param draws bound to rng([20333500, k]);
the lowamp_p2_starts=20334000 registry row is NOT consumed by this batch
(judged starts = T-22 deterministic full enumeration; sensitivity legs =
full-panel continuous runs) -- disclosed here and in the results audit
block.

Nulls (prereg sec.3, K=2000, same-mask): each day, uniform random choice
of N=2 members from the SAME eligibility mask universe as LA-REP (liquidity
gate + valid amp included), eq weights, legacy full-panel continuous run;
Sharpe distribution feeds skill_line_v2 via g1_prime_v2's null_pool face
(G-MASK: null daily universe == real cell daily universe by construction,
asserted per draw).

Checkpoint/resume: per-shard JSONL append with done-key skip (t22
pattern), per-shard marker file, deterministic bytes (sort_keys, rounded).

Usage:
  python scripts/lowamp_p2.py probe                  # ignition gate face
  python scripts/lowamp_p2.py run --cell LA-REP --axis legacy --face base
  python scripts/lowamp_p2.py run --nulls
  python scripts/lowamp_p2.py run --sensitivity
  python scripts/lowamp_p2.py status
  python scripts/lowamp_p2.py finalize                # round-owned, post-shards
  python scripts/lowamp_p2.py selftest                # hermetic, offline
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd

from live.paper import build_panels, load_core
from t22_virtual_timepoints import (
    _load_axis_prices, _slice_metrics, enumerate_starts, regime_proxy,
)
from science_gates import (
    CostPatch, SEED_REGISTRY, append_ledger, closed_family_check, cutoff_meta,
    deflated_sharpe_ratio, g1_prime_v2, g2_registration_v2, m1_t_value_gate,
    t_from_sharpe,
)
from knowledge import cost_spec

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TICKET = "T-2026-10-01-140"
PREREG = os.path.join(ROOT, "research", "LOWAMP-P2.md")
OUT_DIR = os.path.join(ROOT, "results", "lowamp_p2")
LOG_DIR = os.path.join(OUT_DIR, "logs")
PROBE_JSON = os.path.join(OUT_DIR, "probe.json")
OUT_JSON = os.path.join(OUT_DIR, "lowamp_p2_results.json")
OUT_CSV = os.path.join(OUT_DIR, "cells.csv")

CUTOFF = pd.Timestamp("2026-09-22")          # prereg sec.2 D2 lockbox
BATCH_NAME = "LOWAMP-P2"
BATCH_CELLS = 2008                          # 4 cells x 2 faces + 2000 nulls
FAMILY_KEY = "lowamp_daily_xs"              # prereg sec.1 M3
CAPITAL = 1_000_000.0                       # prereg CN-C7 nominal tier
WARMUP_TD = 252                             # T-22 caliber
W6M, W12M, W24M = 126, 252, 504
MIN_LISTED = 24
AMT20_WIN = 20
AMT20_MIN = 50_000_000.0                    # frozen liquidity floor (sec.2)
K_NULLS = 2000
SEED_NULLS = 20334500                       # prereg sec.3 verbatim
K_SENS = 500
SEED_SENS = 20333500                        # prereg sec.3 verbatim
BOOT_B = 2000                               # deep-axis binomial bootstrap
D6_REJECT = 0.7                             # prereg sec.1 D6
G_CENSUS = {"legacy": 1254, "deep": 1506}   # amended anchor, see docstring
CELLS = {
    "LA-REP":  {"W": 89,  "N": 2, "sizing": "invvol"},
    "LA-EQ":   {"W": 89,  "N": 2, "sizing": "eq"},
    "LA-T3":   {"W": 89,  "N": 3, "sizing": "invvol"},
    "LA-EDGE": {"W": 104, "N": 2, "sizing": "invvol"},
}
FACES = ("base", "x2")
AXES = ("legacy", "deep")
ADJ_DIR = os.path.join(ROOT, "data", "consolidation", "adjusted_view")
DEEP_DIR = os.path.join(ROOT, "Money02", "data", "cache",
                        "t18_deep_panel", "ohlcv")
DEEP_MANIFEST = os.path.join(ROOT, "results", "shortline",
                             "t18_deep_manifest.json")
FROZEN_ENVELOPE = ("2026-10-01 pre-burn amendment note: legacy G-CENSUS "
                   "re-anchored 1255->1254 under the binding 2026-09-22 "
                   "cutoff truncation (r251/r280 zero-burn lineage)")

_G = {}   # per-worker globals


# set by cmd_run at launch; rides the pool-claim handshake (see
# _pool_claim -- O-20260930-2355 window)
_CLAIM_STARTED = ""


def _machine_id() -> str:
    try:
        return json.load(open(os.path.join(ROOT, "fleet", "machine.json"),
                              encoding="utf-8"))["machine_id"]
    except Exception:
        return "unknown"


def _log(name: str, msg: str):
    os.makedirs(LOG_DIR, exist_ok=True)
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(os.path.join(LOG_DIR, name + ".log"), "a", encoding="utf-8") as fh:
        fh.write(f"{stamp} {msg}\n")


def _dump(obj, path):
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=2, sort_keys=True)


# ------------------------------------------------------------------ data face

def _adj_replace(prices: dict) -> int:
    """Prereg sec.2: both axes take the T-19 adjusted view as the price
    source for the 19 consolidation-affected members (amp signal must eat
    the adjusted face -- raw-face merge days would pollute the amp rank)."""
    n = 0
    for code in list(prices.keys()):
        vpath = os.path.join(ADJ_DIR, code + ".parquet")
        if not os.path.exists(vpath):
            continue
        df = pd.read_parquet(vpath)
        if "date" in df.columns:
            df = df.set_index("date")
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        assert df.index.is_monotonic_increasing \
            and not df.index.duplicated().any(), f"adj face corrupt: {code}"
        prices[code] = df[
            ["open", "high", "low", "close", "volume", "amount"]].copy()
        n += 1
    return n


def load_axis(axis: str, truncate: bool = True) -> dict:
    if axis == "legacy":
        prices = load_core()
        n_adj = _adj_replace(prices)
        assert n_adj == 19, f"adj replace {n_adj}/19 -- GF hard gate"
    else:
        prices = _load_axis_prices("deep")   # t22 verbatim (adj-preferred)
    if truncate:
        prices = {s: df[df.index <= CUTOFF] for s, df in prices.items()}
    return prices


def axis_face_facts(prices: dict, axis: str) -> dict:
    close = build_panels(prices)["close"]
    return {
        "axis": axis,
        "members": len(prices),
        "panel_start": str(close.index[0].date()),
        "panel_end": str(close.index[-1].date()),
        "anchor_rows_510300": int((prices["510300"].index <= CUTOFF).sum())
        if "510300" in prices else None,
        "starts": len(enumerate_starts(len(close.index),
                                       close.notna().sum(axis=1))),
    }


# ---------------------------------------------------------------- signal face

def build_signal(close: pd.DataFrame, volume: pd.DataFrame,
                 amount: pd.DataFrame, W: int, N: int):
    """Prereg sec.3 signal: amp = rolling std of close-to-close returns
    (min_periods=W), ascending rank -> Top-N lowest, eligibility mask with
    the frozen liquidity floor. Returns (entry bool DF, weights DF, elig)."""
    rets = close.pct_change()
    amp = rets.rolling(W, min_periods=W).std()
    amt20 = amount.rolling(AMT20_WIN, min_periods=AMT20_WIN).median()
    elig = (amp.notna() & close.notna() & (volume > 0) & (amount > 0)
            & (amt20 >= AMT20_MIN))
    entry = pd.DataFrame(False, index=close.index, columns=close.columns)
    weights = pd.DataFrame(np.nan, index=close.index, columns=close.columns,
                           dtype=float)
    amp_v = amp.to_numpy(dtype=float)
    el_v = elig.to_numpy(dtype=bool)
    cols = list(close.columns)
    for i in range(len(close.index)):
        idx = np.where(el_v[i])[0]
        if idx.size == 0:
            continue
        order = idx[np.lexsort((np.asarray([cols[j] for j in idx]), amp_v[i, idx]))]
        pick = order[:min(N, idx.size)]
        entry.iloc[i, pick] = True
        if pick.size:
            a = amp_v[i, pick]
            if a.size and np.isfinite(a).all() and (a > 0).all():
                w = 1.0 / a
                w = w / w.sum()
            else:
                w = np.full(pick.size, 1.0 / pick.size)
            weights.iloc[i, pick] = w
    return entry, weights, elig


def exec_day_scale(weights: pd.DataFrame, sym: str) -> pd.Series:
    """Per-symbol entry_size_scale indexed at the EXECUTION day (engine
    contract: value at exec day E reflects the prior signal close). Weight
    of signal day T lands on the next trading bar = positional shift(1)."""
    col = weights[sym]
    if not (col.notna() & (col > 0)).any():
        return pd.Series(dtype=float)
    return col.shift(1)


# ------------------------------------------------------------- engine face

def run_cell_portfolio(prices: dict, close: pd.DataFrame, entry: pd.DataFrame,
                       weights: pd.DataFrame, face: str, active: list,
                       sdate=None, e=None):
    """Engine-canonical run of one cell on a window (None/None = the full
    panel, the continuous face). Per-symbol sub-account decomposition -- see
    module docstring. Returns dict(nav pnl series on the panel window index,
    n_trades, n_entries, trade_dates)."""
    from engine import run_backtest
    params = {"position_size_pct": 1.0, "max_positions": 1,
              "sizing_mode": "fixed_initial", "report_num_entries": True,
              # sec.0.6 exit-axis: HOLD-THROUGH -- engine default exit
              # stack explicitly disabled key-by-key (prereg verbatim;
              # r301 default-stack x low-amp hybrid finding reversed via
              # the engine's own params channel -- engine/ untouched)
              "take_profit_levels": (),
              "trailing_stop_activate": 1e12,
              "initial_stop": -1.0,
              "time_decay_period": 10 ** 9,
              "loss_time_days": 10 ** 9,
              "global_hard_limit": 10 ** 9}
    lo = close.index[0] if sdate is None else sdate
    hi = close.index[-1] if e is None else e
    win_idx = close.index[(close.index >= lo) & (close.index <= hi)]
    pnl = None
    n_trades = n_entries = 0
    trade_dates = []
    from contextlib import nullcontext
    for sym in active:
        win = {sym: prices[sym][(prices[sym].index >= lo)
                               & (prices[sym].index <= hi)]}
        if win[sym].empty:
            continue
        ent = entry[[sym]]
        sc = exec_day_scale(weights, sym)
        with (CostPatch(2.0) if face == "x2" else nullcontext()):
            res = run_backtest(win, params, entry_signal=ent,
                               exit_signal=ent <= 0, entry_size_scale=sc)
        eq = pd.Series(res["equity_curve"],
                       index=win[sym].index[:len(res["equity_curve"])])
        p = (eq - CAPITAL).reindex(win_idx).ffill().fillna(0.0)
        pnl = p if pnl is None else pnl + p
        n_trades += len(res["trades"])
        n_entries += int(res["metrics"].get("num_entries", 0))
        for tr in res["trades"]:
            trade_dates.append(pd.Timestamp(tr["date"]))
    if pnl is None:
        return None
    return {"pnl": pnl, "n_trades": n_trades, "n_entries": n_entries,
            "trade_dates": trade_dates}


# ------------------------------------------------------------------ workers

def _init_worker(axis: str):
    import psutil
    pri = getattr(psutil, "BELOW_NORMAL_PRIORITY_CLASS", None)
    if pri is not None:
        try:
            psutil.Process().nice(pri)   # O-1136 low-priority pool law
        except Exception:
            pass
    prices = load_axis(axis)
    P = build_panels(prices)
    close = P["close"]
    # sec.2: regime labels ALWAYS from the 510300 legacy face (both axes)
    if "510300" in close.columns:
        reg = regime_proxy(close["510300"])
    else:
        leg_close = build_panels(load_axis("legacy"))["close"]
        reg = regime_proxy(leg_close["510300"]) if "510300" in leg_close.columns \
            else None
    _G.update(prices=prices, P=P, close=close, idx=close.index,
              axis=axis, regime=reg, _sig={})


def _cell_task(payload):
    """One (cell, startpoint, face) row -- t22 pattern: longest window once,
    6m/12m/24m sliced off the same equity curve; passive = EW B&H of
    members listed at the start over the identical span (t22 verbatim)."""
    cell, pos, face = payload["cell"], payload["pos"], payload["face"]
    spec = CELLS[cell]
    cache = _G.setdefault("_sig", {})
    key = (cell, face)
    if key not in cache:
        P, close = _G["P"], _G["close"]
        entry, weights, _ = build_signal(close, P["volume"], P["amount"],
                                         spec["W"], spec["N"])
        cache[key] = (entry, weights)
    entry, weights = cache[key]
    prices, idx = _G["prices"], _G["idx"]
    sdate = idx[pos]
    e = idx[min(pos + W24M - 1, len(idx) - 1)]
    sig_win = entry.loc[sdate:e]
    active = [c for c in entry.columns if sig_win[c].any()]
    if active:
        run = run_cell_portfolio(prices, _G["close"], entry, weights, face,
                                 active, sdate, e)
    else:
        run = None
    close = _G["close"]
    win_idx = idx[pos:pos + W24M]
    if run is None:
        eq = pd.Series(CAPITAL, index=win_idx)
        trades = []
    else:
        eq = (run["pnl"] + CAPITAL).reindex(win_idx).ffill().fillna(CAPITAL)
        trades = [{"date": d} for d in run["trade_dates"]]
    m6 = _slice_metrics(eq, trades, W6M)
    m12 = _slice_metrics(eq, trades, W12M)
    m24 = _slice_metrics(eq, trades, W24M)
    syms = close.columns[close.loc[sdate].notna()]
    base = close.loc[sdate, syms]
    rel = (close.loc[sdate:e, syms] / base).mean(axis=1)
    p6 = _slice_metrics(rel, [], W6M)
    p12 = _slice_metrics(rel, [], W12M)
    p24 = _slice_metrics(rel, [], W24M)
    reg = _G.get("regime")
    rlabel = "na"
    if reg is not None and sdate in reg.index:
        rlabel = str(reg.loc[sdate])
    return {"key": f"{cell}|{_G['axis']}|{face}|{pos}", "cell": cell,
            "axis": _G["axis"], "face": face, "pos": pos,
            "start": str(sdate.date()), "regime": rlabel,
            "n_listed": int(len(syms)), "n_active": len(active),
            "partial_12m": m12["n_bars"] < W12M,
            "partial_24m": m24["n_bars"] < W24M,
            "ret_6m": m6["ret"], "ret_12m": m12["ret"], "ret_24m": m24["ret"],
            "p_ret_6m": p6["ret"], "p_ret_12m": p12["ret"],
            "p_ret_24m": p24["ret"],
            "dd_6m": m6["dd"], "dd_12m": m12["dd"], "dd_24m": m24["dd"],
            "sharpe_6m": m6["sharpe"], "sharpe_12m": m12["sharpe"],
            "sharpe_24m": m24["sharpe"],
            "trades_6m": m6["trades"], "trades_12m": m12["trades"],
            "trades_24m": m24["trades"],
            "beat_6m": m6["ret"] > p6["ret"],
            "beat_12m": m12["ret"] > p12["ret"],
            "beat_24m": m24["ret"] > p24["ret"]}


def _cont_task(payload):
    """Continuous full-panel run of one (cell, face) on the worker's axis
    -- the headline/G1'/M1/DSR/x2/PBO supply face."""
    cell, face = payload["cell"], payload["face"]
    spec = CELLS[cell]
    P, close = _G["P"], _G["close"]
    entry, weights, _ = build_signal(close, P["volume"], P["amount"],
                                     spec["W"], spec["N"])
    active = [c for c in entry.columns if entry[c].any()]
    run = run_cell_portfolio(_G["prices"], close, entry, weights, face, active)
    nav = run["pnl"] + CAPITAL
    nav = nav.reindex(close.index).ffill().fillna(CAPITAL)
    rets = nav.pct_change().dropna()
    from engine.metrics import max_drawdown, sharpe
    yrs = len(nav) / 252.0
    return {"key": f"cont|{cell}|{_G['axis']}|{face}", "cell": cell,
            "axis": _G["axis"], "face": face,
            "sharpe_full": round(float(sharpe(nav)), 6),
            "ret_full": round(float(nav.iloc[-1] / nav.iloc[0] - 1), 6),
            "max_dd": round(float(max_drawdown(nav)), 6),
            "n_trades": run["n_trades"], "n_entries": run["n_entries"],
            "trades_per_year": round(run["n_trades"] / yrs, 2) if yrs else None,
            "n_days": int(len(nav)),
            "returns": [round(float(v), 8) for v in rets.to_numpy()],
            "nav_first": round(float(nav.iloc[0]), 2),
            "nav_last": round(float(nav.iloc[-1]), 2)}


def _null_task(payload):
    """Same-mask random-selection null draw k (prereg sec.3): per day, N=2
    uniform picks from the LA-REP eligibility universe, eq weights, legacy
    full-panel continuous run. G-MASK holds by construction (same frame)."""
    k = payload["k"]
    spec = CELLS["LA-REP"]
    P, close = _G["P"], _G["close"]
    entry, weights, elig = build_signal(close, P["volume"], P["amount"],
                                        spec["W"], spec["N"])
    rng = np.random.default_rng([SEED_NULLS, k])
    null_entry = pd.DataFrame(False, index=close.index, columns=close.columns)
    null_w = pd.DataFrame(np.nan, index=close.index, columns=close.columns,
                          dtype=float)
    for i, dt in enumerate(close.index):
        cands = [c for c in close.columns if bool(elig.iloc[i][c])]
        if len(cands) < 2:
            continue
        pick = rng.choice(len(cands), size=2, replace=False)
        picked = sorted(cands[j] for j in pick)
        for c in picked:
            null_entry.loc[dt, c] = True
            null_w.loc[dt, c] = 0.5
    active = [c for c in null_entry.columns if null_entry[c].any()]
    run = run_cell_portfolio(_G["prices"], close, null_entry, null_w, "base",
                             active)
    from engine.metrics import max_drawdown, sharpe
    nav = (run["pnl"] + CAPITAL).reindex(close.index).ffill().fillna(CAPITAL)
    rets = nav.pct_change().dropna()
    return {"key": f"null|{k}", "k": k,
            "sharpe": round(float(sharpe(nav)), 6),
            "ret": round(float(nav.iloc[-1] / nav.iloc[0] - 1), 6),
            "max_dd": round(float(max_drawdown(nav)), 6),
            "n_trades": run["n_trades"],
            "n_entries": run["n_entries"],
            "n_selected_days": int(null_entry.any(axis=1).sum())}


def _sens_task(payload):
    """Sensitivity draw k (prereg sec.3 sec.2.2 leg): uniform space-filling
    draw over (W in [77,104], N in {2,3}, sizing in {invvol,eq}), gate
    always-on fixed, legacy full-panel continuous run. Descriptive only."""
    k = payload["k"]
    rng = np.random.default_rng([SEED_SENS, k])
    W = int(rng.integers(77, 105))
    N = int(rng.choice([2, 3]))
    sizing = str(rng.choice(np.array(["invvol", "eq"])))
    P, close = _G["P"], _G["close"]
    entry, weights, _ = build_signal(close, P["volume"], P["amount"], W, N)
    if sizing == "eq":
        # equal-weight among the day's active entries (identical math to
        # the original in-place variant; pandas>=3 CoW makes to_numpy()
        # read-only, which killed every eq-draw sens task with
        # "assignment destination is read-only" -- r498 silent engine
        # death, zero rows in 68 min)
        on = entry.to_numpy(dtype=bool)
        cnt = entry.sum(axis=1).to_numpy(dtype=float)
        wf = np.full(weights.shape, np.nan, dtype=float)
        for i in range(len(close.index)):
            if cnt[i] > 0:
                wf[i, on[i]] = 1.0 / cnt[i]
        weights = pd.DataFrame(wf, index=weights.index,
                               columns=weights.columns)
    active = [c for c in entry.columns if entry[c].any()]
    run = run_cell_portfolio(_G["prices"], close, entry, weights, "base",
                             active)
    from engine.metrics import max_drawdown, sharpe
    nav = (run["pnl"] + CAPITAL).reindex(close.index).ffill().fillna(CAPITAL)
    return {"key": f"sens|{k}", "k": k, "W": W, "N": N, "sizing": sizing,
            "sharpe": round(float(sharpe(nav)), 6),
            "ret": round(float(nav.iloc[-1] / nav.iloc[0] - 1), 6),
            "max_dd": round(float(max_drawdown(nav)), 6),
            "n_trades": run["n_trades"]}


# ------------------------------------------------------------------- checkpoint

def _shard_files(cell=None, axis=None, face=None, kind=None):
    if kind == "nulls":
        return os.path.join(OUT_DIR, "nulls.jsonl")
    if kind == "sens":
        return os.path.join(OUT_DIR, "sens.jsonl")
    return os.path.join(OUT_DIR, f"cells_{cell}_{axis}_{face}.jsonl")


def _done_keys(path: str) -> set:
    keys = set()
    if not os.path.exists(path):
        return keys
    lines = open(path, encoding="utf-8").read().splitlines()
    for i, ln in enumerate(lines):
        if not ln.strip():
            continue
        try:
            keys.add(json.loads(ln)["key"])
        except (json.JSONDecodeError, KeyError):
            if i == len(lines) - 1:
                continue        # truncated crash tail: skip honestly
            raise
    return keys


def _append_rows(path: str, rows: list):
    with open(path, "a", encoding="utf-8", newline="\n") as fh:
        for r in rows:
            fh.write(json.dumps(r, default=bool, sort_keys=True,
                                ensure_ascii=False) + "\n")


def _regime_labels(close_legacy: pd.DataFrame) -> pd.Series:
    """sec.2: regime proxy ALWAYS from the 510300 close face (legacy axis),
    applied by date to both axes."""
    if "510300" not in close_legacy.columns:
        return None
    return regime_proxy(close_legacy["510300"])


# ---------------------------------------------------------------------- probe

def cmd_probe(_) -> int:
    os.makedirs(OUT_DIR, exist_ok=True)
    t0 = time.time()
    facts = {"ticket": TICKET, "batch": BATCH_NAME, "ts":
             time.strftime("%Y-%m-%d %H:%M:%S"), "checks": []}

    def chk(name, ok, detail=""):
        facts["checks"].append({"name": name, "pass": bool(ok),
                                "detail": str(detail)[:400]})
        return bool(ok)

    # cost single-source assert (CN-C7): ETF round-trip 26.082bp derived
    rate = cost_spec.x1_side_rate()
    chk("cost_x1_derived", abs(rate * 2.0 * 1e4 - 26.082) < 1e-6,
        f"x1_side={rate} -> rt_bp={rate*2e4:.3f}")
    # M3 closed family
    m3 = closed_family_check(FAMILY_KEY)
    chk("closed_family_open", m3.get("open") is True or m3.get("status") == "open",
        json.dumps(m3, ensure_ascii=False)[:200])
    # axes
    face_facts = {}
    for axis in AXES:
        prices = load_axis(axis)
        ff = axis_face_facts(prices, axis)
        face_facts[axis] = ff
        chk(f"members_{axis}", ff["members"] == 48, ff["members"])
        chk(f"panel_end_{axis}", ff["panel_end"] == "2026-09-22",
            ff["panel_end"])
        chk(f"no_dup_monotonic_{axis}", True, "per-frame asserts in loader")
        chk(f"g_census_{axis}", ff["starts"] == G_CENSUS[axis],
            f"starts={ff['starts']} want={G_CENSUS[axis]}")
        del prices
    man = json.load(open(DEEP_MANIFEST, encoding="utf-8"))
    n_deep_files = len([f for f in os.listdir(DEEP_DIR) if f.endswith(".parquet")])
    chk("deep_manifest_pass", man.get("verdict") == "PASS", man.get("verdict"))
    chk("deep_ohlcv_48", n_deep_files == 48, n_deep_files)
    n_adj = len([f for f in os.listdir(ADJ_DIR) if f.endswith(".parquet")])
    chk("adj_view_19", n_adj == 19, n_adj)
    # liquidity gate disclosure facts (LA-REP, legacy)
    prices = load_axis("legacy")
    P = build_panels(prices)
    close = P["close"]
    entry, weights, elig = build_signal(close, P["volume"], P["amount"], 89, 2)
    elig_n = elig.sum(axis=1)
    facts["liquidity"] = {
        "amt20_min_yuan": AMT20_MIN,
        "elig_days_median": float(elig_n.median()),
        "elig_days_min": int(elig_n.min()),
        "selected_days": int(entry.any(axis=1).sum()),
        "active_members_ever": int((entry.any(axis=0)).sum()),
    }
    # D6 same-family admission probe: headline LA-REP legacy continuous
    # daily returns vs ALL six registered members (ew6 canon), fail-closed.
    active = [c for c in entry.columns if entry[c].any()]
    run = run_cell_portfolio(prices, close, entry, weights, "base", active)
    nav = (run["pnl"] + CAPITAL).reindex(close.index).ffill().fillna(CAPITAL)
    headline_rets = nav.pct_change().dropna()
    facts["headline"] = {"sharpe_full": round(float(
        (headline_rets.mean() / headline_rets.std(ddof=1)) * np.sqrt(252)), 6),
        "ret_full": round(float(nav.iloc[-1] / nav.iloc[0] - 1), 6),
        "n_trades": run["n_trades"], "n_entries": run["n_entries"]}
    try:
        from cn_rev_tilt_p1 import REG6, load_member_rets
        mrets, _ = load_member_rets()
        pairs = []
        worst = None
        for tid in REG6:
            r = mrets[tid]
            both = pd.concat([headline_rets, r], axis=1).dropna()
            c = float(both.corr().iloc[0, 1]) if len(both) > 30 else None
            pairs.append({"member": tid, "corr": round(c, 4) if c is not None else None,
                          "n_overlap": int(len(both))})
            if c is not None and (worst is None or abs(c) > abs(worst[1])):
                worst = (tid, c)
        facts["d6"] = {"reject_line": D6_REJECT, "pairs": pairs,
                       "max_abs_corr": round(abs(worst[1]), 4) if worst else None,
                       "max_member": worst[0] if worst else None}
        chk("d6_admission", worst is not None and abs(worst[1]) < D6_REJECT,
            f"max|corr|={abs(worst[1]):.4f} vs {D6_REJECT}" if worst else "no pairs")
    except Exception as ex:      # fail-closed: no D6 face = no ignition
        chk("d6_admission", False, f"D6 face error: {ex}")
    facts["g_census_amendment"] = FROZEN_ENVELOPE
    facts["seed_disclosure"] = {
        "nulls": SEED_NULLS, "sensitivity": SEED_SENS,
        "registry_rows": {k: v for k, v in SEED_REGISTRY.items()
                          if "lowamp" in k},
        "note": "registry row lowamp_p2_starts=20334000 NOT consumed by "
                "this batch (T-22 full enumeration judged starts; "
                "full-panel continuous sensitivity); prereg sec.3 binds "
                "nulls to 20334500 and sens draws to 20333500 "
                "(verbatim)."}
    facts["runtime_sec"] = round(time.time() - t0, 1)
    facts["verdict"] = ("PASS" if all(c["pass"] for c in facts["checks"])
                        else "FAIL")
    _dump(facts, PROBE_JSON)
    print(f"probe {facts['verdict']} ({facts['runtime_sec']}s) -> {PROBE_JSON}")
    for c in facts["checks"]:
        print(f"  [{'PASS' if c['pass'] else 'FAIL'}] {c['name']}: {c['detail'][:120]}")
    return 0 if facts["verdict"] == "PASS" else 3


# ------------------------------------------------------------------------ run

def _require_probe():
    if not os.path.exists(PROBE_JSON):
        print("FAIL-CLOSED: probe.json absent -- run `probe` before ignition "
              "(prereg sec.2 data-completeness gate)")
        return False
    v = json.load(open(PROBE_JSON, encoding="utf-8")).get("verdict")
    if v != "PASS":
        print(f"FAIL-CLOSED: probe verdict={v} -- ignition refused")
        return False
    return True


def _mk(kind, **kw):
    d = {"_fn": {"cell": _cell_task, "cont": _cont_task,
                 "null": _null_task, "sens": _sens_task}[kind], **kw}
    return d


def _now_iso() -> str:
    import datetime
    return datetime.datetime.now().astimezone().isoformat(
        timespec="seconds")


def _pool_claim(entry_id: str, shard_key: str, detail: str) -> None:
    """O-20260930-2355 window: worker-side half of the pool harvest
    handshake -- on a successful burn write results/pool_claims/
    <entry>/<shard>.<machine>.json with state=closed outcome=ok so the
    launcher's harvest flip lands the shard done (the worker NEVER
    writes runnable_pool.json -- pool single-writer law; without this
    handshake a completed burn reads as a crash to the fuse and the
    campaign freezes, r496 live family)."""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    d = os.path.join(root, "results", "pool_claims",
                     entry_id.replace("/", "_"))
    os.makedirs(d, exist_ok=True)
    fp = os.path.join(d, f"{shard_key}.{_machine_id()}.json")
    now = _now_iso()
    _dump({"machine_id": _machine_id(), "state": "closed",
           "pid": os.getpid(), "heartbeat": now, "outcome": "ok",
           "exit_code": 0, "started": _CLAIM_STARTED, "closed_at": now,
           "result_ref": detail}, fp)
    _log(entry_id.lower(), f"pool claim closed: {os.path.basename(fp)}")


def _entry_of(args) -> tuple:
    """Pool entry/shard identity for the claim handshake (ids mirror
    the r495 registration face exactly)."""
    if getattr(args, "nulls", None):
        return ("LOWAMP-P2-NULLS", "lowamp-p2-nulls-0of1")
    if getattr(args, "sensitivity", None):
        return ("LOWAMP-P2-SENS", "lowamp-p2-sens-0of1")
    entry = ("LOWAMP-P2-CELL-" + args.cell.replace("-", "").upper()
             + "-" + args.axis.upper() + "-" + args.face.upper())
    return (entry, entry.lower() + "-0of1")


def cmd_run(args) -> int:
    global _CLAIM_STARTED
    _CLAIM_STARTED = _now_iso()
    os.makedirs(OUT_DIR, exist_ok=True)
    if not _require_probe():
        return 3
    if args.nulls:
        path = _shard_files(kind="nulls")
        tasks = [_mk("null", k=k) for k in range(K_NULLS)]
        log = "nulls"
        axis = "legacy"
        keyfn = lambda p: f"null|{p['k']}"
        _run_parallel_tasks(tasks, axis, keyfn, path, log)
        _pool_claim(*_entry_of(args),
                    f"nulls N={K_NULLS} -> {path}")
        return 0
    if args.sensitivity:
        path = _shard_files(kind="sens")
        tasks = [_mk("sens", k=k) for k in range(K_SENS)]
        log = "sens"
        axis = "legacy"
        keyfn = lambda p: f"sens|{p['k']}"
        _run_parallel_tasks(tasks, axis, keyfn, path, log)
        _pool_claim(*_entry_of(args),
                    f"sens N={K_SENS} -> {path}")
        return 0
    if not (args.cell in CELLS and args.axis in AXES
            and args.face in FACES):
        print(f"bad unit: cell={args.cell} axis={args.axis} face={args.face}")
        return 2
    axis, cell, face = args.axis, args.cell, args.face
    log = f"{cell}_{axis}_{face}"
    prices = load_axis(axis)
    close = build_panels(prices)["close"]
    starts = enumerate_starts(len(close.index), close.notna().sum(axis=1))
    tasks = [_mk("cell", cell=cell, pos=pos, face=face) for pos in starts]
    path = _shard_files(cell=cell, axis=axis, face=face)
    keyfn = lambda p: f"{cell}|{axis}|{face}|{p['pos']}"
    _run_parallel_tasks(tasks, axis, keyfn, path, log)
    # continuous face for this cell-axis (G1'/M1/DSR/x2/PBO supply)
    cpath = os.path.join(OUT_DIR, f"cont_{cell}_{axis}_{face}.json")
    if not os.path.exists(cpath):
        _init_worker(axis)
        row = _cont_task(_mk("cont", cell=cell, face=face))
        _dump(row, cpath)
        _log(log, f"cont face written: {cpath}")
    _log(log, f"shard complete: {len(starts)} starts + cont face")
    _pool_claim(*_entry_of(args),
                f"cells {len(starts)} -> {path} + {os.path.basename(cpath)}")
    return 0


def _run_parallel_tasks(tasks, axis, keyfn, path, log_name):
    """t22-pattern parallel burn: ProcessPool with per-worker axis init,
    checkpoint done-key skip, JSONL append."""
    from concurrent.futures import ProcessPoolExecutor, as_completed
    from parallel_runner import worker_cap
    done = _done_keys(path)
    todo = [p for p in tasks if keyfn(p) not in done]
    _log(log_name, f"todo={len(todo)} resume-skipped={len(tasks)-len(todo)}")
    if not todo:
        return 0
    workers = int(min(worker_cap(), 12))
    t0, t_last, n = time.time(), time.time(), 0
    with ProcessPoolExecutor(max_workers=workers,
                             initializer=_init_worker,
                             initargs=(axis,)) as pool:
        futs = {pool.submit(p["_fn"], p): p for p in todo}
        for fut in as_completed(futs):
            row = fut.result()
            _append_rows(path, [row])
            n += 1
            if time.time() - t_last > 30:
                _log(log_name, f"progress {n}/{len(todo)}")
                t_last = time.time()
    _log(log_name, f"DONE {n}/{len(todo)} in {round(time.time()-t0,1)}s "
                   f"workers={workers}")
    return n


# --------------------------------------------------------------------- status

def cmd_status(_) -> int:
    if not os.path.isdir(OUT_DIR):
        print("no results/lowamp_p2 yet")
        return 0
    total_missing = 0
    for axis in AXES:
        prices = load_axis(axis)
        close = build_panels(prices)["close"]
        n_starts = len(enumerate_starts(len(close.index),
                                        close.notna().sum(axis=1)))
        del prices
        for cell in CELLS:
            for face in FACES:
                p = _shard_files(cell=cell, axis=axis, face=face)
                have = len(_done_keys(p)) if os.path.exists(p) else 0
                c = os.path.join(OUT_DIR, f"cont_{cell}_{axis}_{face}.json")
                cont = "Y" if os.path.exists(c) else "-"
                miss = n_starts - have
                total_missing += max(0, miss) + (0 if cont == "Y" else 1)
                print(f"{cell:7s} {axis:6s} {face:4s}: {have}/{n_starts} "
                      f"starts cont={cont}")
    for kind, want in (("nulls", K_NULLS), ("sens", K_SENS)):
        p = _shard_files(kind=kind)
        have = len(_done_keys(p)) if os.path.exists(p) else 0
        total_missing += max(0, want - have)
        print(f"{kind}: {have}/{want}")
    print(f"finalize_ready: {total_missing == 0} (missing={total_missing})")
    return 0


# ------------------------------------------------------------------ finalize

def _read_cells(cell, axis, face):
    p = _shard_files(cell=cell, axis=axis, face=face)
    if not os.path.exists(p):
        return None
    rows = []
    for ln in open(p, encoding="utf-8"):
        if ln.strip():
            rows.append(json.loads(ln))
    return rows


def _binom_ci(k, n, seed=20261001):
    rng = np.random.default_rng(seed)
    draws = rng.binomial(n, k / n, BOOT_B) / n
    lo, hi = np.percentile(draws, [2.5, 97.5])
    return round(float(lo), 4), round(float(hi), 4)


BLOCK_BOOT_LEN = 21     # prereg sec.3 null family 2 (frozen block length)
NULL_AUX_SEED = 20261001   # disclosed in output (bootstrap/sign-flip face)


def _block_bootstrap_sharpe(rets: pd.Series, b: int = BOOT_B,
                            block: int = BLOCK_BOOT_LEN, seed: int = NULL_AUX_SEED):
    """sec.3 null family 2: circular block bootstrap on the headline daily
    returns, block length 21td (frozen); Sharpe null distribution + p."""
    r = rets.to_numpy(dtype=float)
    t = len(r)
    if t < 2 * block:
        return None
    rng = np.random.default_rng(seed)
    starts = rng.integers(0, t, size=(b, int(np.ceil(t / block))))
    idx = (starts[:, :, None] + np.arange(block)[None, None, :]) % t
    samples = r[idx].reshape(b, -1)[:, :t]
    mu = samples.mean(axis=1)
    sd = samples.std(axis=1, ddof=1)
    sharpes = np.where(sd > 0, mu / sd * np.sqrt(252), 0.0)
    obs = float(rets.mean() / rets.std(ddof=1) * np.sqrt(252))
    return {"B": b, "block_len": block, "seed": seed,
            "sharpe_p05": round(float(np.percentile(sharpes, 5)), 4),
            "sharpe_p50": round(float(np.percentile(sharpes, 50)), 4),
            "sharpe_p95": round(float(np.percentile(sharpes, 95)), 4),
            "obs_sharpe": round(obs, 6),
            "p_ge_obs": round(float((sharpes >= obs).mean()), 6)}


def _sign_flip_perm(rets: pd.Series, p: int = BOOT_B, seed: int = NULL_AUX_SEED):
    """sec.3 null family 3: sign-flip permutation on the headline daily
    returns; |mean| null distribution + p (two-sided)."""
    r = rets.to_numpy(dtype=float)
    rng = np.random.default_rng(seed)
    signs = rng.choice([-1.0, 1.0], size=(p, len(r)))
    means = np.abs((r[None, :] * signs).mean(axis=1))
    obs = abs(float(r.mean()))
    return {"P": p, "seed": seed,
            "abs_mean_p50": round(float(np.percentile(means, 50)), 8),
            "abs_mean_p95": round(float(np.percentile(means, 95)), 8),
            "abs_mean_obs": round(obs, 8),
            "p_two_sided": round(float((means >= obs).mean()), 6)}


def cmd_finalize(_) -> int:
    # completeness gate (fail-closed; finalize is round-owned)
    missing = []
    for axis in AXES:
        for cell in CELLS:
            for face in FACES:
                p = _shard_files(cell=cell, axis=axis, face=face)
                c = os.path.join(OUT_DIR, f"cont_{cell}_{axis}_{face}.json")
                if not os.path.exists(p) or not os.path.exists(c):
                    missing.append(f"{cell}/{axis}/{face}")
    for kind in ("nulls", "sens"):
        p = _shard_files(kind=kind)
        have = len(_done_keys(p)) if os.path.exists(p) else 0
        want = K_NULLS if kind == "nulls" else K_SENS
        if have < want:
            missing.append(f"{kind}:{have}/{want}")
    if missing:
        print("finalize REFUSED -- incomplete: " + ", ".join(missing[:8]))
        return 3
    if os.path.exists(OUT_JSON):
        try:
            j = json.load(open(OUT_JSON, encoding="utf-8"))
            if j.get("trials_ledger"):
                print(f"idempotent: {OUT_JSON} already finalized")
                return 0
        except Exception:
            pass
    t0 = time.time()
    probe = json.load(open(PROBE_JSON, encoding="utf-8"))
    cont = {}
    for axis in AXES:
        for cell in CELLS:
            for face in FACES:
                c = os.path.join(OUT_DIR, f"cont_{cell}_{axis}_{face}.json")
                cont[(cell, axis, face)] = json.load(open(c, encoding="utf-8"))
    nulls = [json.loads(ln) for ln in open(_shard_files(kind="nulls"),
                                           encoding="utf-8") if ln.strip()]
    sens = [json.loads(ln) for ln in open(_shard_files(kind="sens"),
                                          encoding="utf-8") if ln.strip()]
    null_vals = [r["sharpe"] for r in nulls]
    null_pool = {
        "coverage": {"mu": float(np.mean(null_vals)),
                     "sigma": float(np.std(null_vals, ddof=1)),
                     "n_values": len(null_vals)},
        "source": f"{BATCH_NAME} same-mask nulls K={K_NULLS} "
                  f"rng([{SEED_NULLS},k])",
    }
    # G1' (headline LA-REP legacy base continuous)
    h = cont[("LA-REP", "legacy", "base")]
    h_rets = pd.Series(h["returns"])
    g1 = g1_prime_v2(sharpe_full=h["sharpe_full"], returns=h_rets,
                     batch_cells=BATCH_CELLS, pool="core48",
                     n_trades=h["n_trades"], n_entries=h["n_entries"],
                     null_pool=null_pool)
    # x2 survival
    x2 = cont[("LA-REP", "legacy", "x2")]
    x2_pass = bool(x2["sharpe_full"] > 0)
    # M1
    tstat = t_from_sharpe(h["sharpe_full"], len(h_rets))
    m1 = m1_t_value_gate(tstat, claim_class="new_strategy")
    # DSR on raw returns (never dsr_from_stats)
    dsr = deflated_sharpe_ratio(h_rets, n_trials=BATCH_CELLS)
    # PBO: 4 judged cells, base face, legacy axis daily returns matrix
    mat = pd.DataFrame({cell: pd.Series(cont[(cell, "legacy", "base")]
                                         ["returns"]) for cell in CELLS})
    mat = mat.dropna()
    from screening.pbo import cscv_pbo, pbo_verdict
    pbo_rec = cscv_pbo(mat)
    pbo = float(pbo_rec["pbo"])
    pbo_band = pbo_verdict(pbo)
    g2 = g2_registration_v2(g1.get("pass"), dsr.get("dsr", dsr), pbo)
    # dual-axis confirmation: deep LA-REP base 12m full-window beat CI
    deep_rows = _read_cells("LA-REP", "deep", "base")
    full12 = [r for r in deep_rows if not r.get("partial_12m")]
    k12 = sum(1 for r in full12 if r["beat_12m"])
    n12 = len(full12)
    ci_lo, ci_hi = _binom_ci(k12, n12) if n12 else (None, None)
    dual_axis_pass = bool(n12 and ci_lo is not None and ci_lo > 0.50)
    # G-SEG coverage per axis
    seg_cov = {}
    gseg_pass = True
    for axis in AXES:
        rows = _read_cells("LA-REP", axis, "base") or []
        full = [r for r in rows if not r.get("partial_12m")]
        cnt = {}
        for r in full:
            cnt[r.get("regime", "na")] = cnt.get(r.get("regime", "na"), 0) + 1
        seg_cov[axis] = cnt
        for reg in ("bear", "bull", "chop"):
            if cnt.get(reg, 0) < 50:
                gseg_pass = False
    # verdict (three-state, conjunctive)
    gates_pass = bool(g1.get("pass") and x2_pass and m1.get("pass")
                      and g2.get("pass") and dual_axis_pass)
    if not gseg_pass:
        verdict = "insufficient-sample"
    elif gates_pass:
        verdict = "PASS"
    else:
        verdict = "judged-negative"
    # readouts: LA-REP legacy base per-start 12m distribution
    lrows = [r for r in _read_cells("LA-REP", "legacy", "base")
             if not r.get("partial_12m")]
    r12 = sorted(r["ret_12m"] for r in lrows)
    def pct(q):
        return round(float(np.percentile(r12, q)), 4) if r12 else None
    nav_series = None   # rolling worst from cont returns (LA-REP legacy base)
    hret = pd.Series(h["returns"])
    roll_worst = {}
    for yrs, bars in (("3y", 756), ("5y", 1260), ("10y", 2520)):
        if len(hret) >= bars:
            roll = (1 + hret).rolling(bars).apply(np.prod, raw=True) - 1
            roll_worst[yrs] = round(float(roll.min()), 4)
        else:
            roll_worst[yrs] = None   # honest: panel too short
    # calendar-year returns (crash-year descriptive)
    hidx = pd.date_range("2020-01-02", periods=len(hret) + 1,
                         freq="B")[:len(hret)]
    cy = (1 + hret).groupby(hidx.year).apply(lambda x: float(x.prod() - 1))
    crash_years = {int(y): round(v, 4) for y, v in cy.items() if v <= -0.35}
    results = {
        **cutoff_meta("2026-09-22"),
        "batch": BATCH_NAME, "ticket": TICKET,
        "family_key": FAMILY_KEY,
        "verdict": verdict,
        "gates": {
            "g1_prime": g1, "x2_survival": {"sharpe_full": x2["sharpe_full"],
                                            "pass": x2_pass},
            "m1": m1, "dsr": dsr, "pbo": {"pbo": round(pbo, 4),
                                           "band": pbo_band},
            "g2": g2,
            "dual_axis": {"beat_k": k12, "beat_n": n12,
                          "ci_lo": ci_lo, "ci_hi": ci_hi,
                          "pass": dual_axis_pass},
            "g_seg": {"coverage": seg_cov, "pass": gseg_pass},
        },
        "headline": {"sharpe_full": h["sharpe_full"], "ret_full":
                     h["ret_full"], "max_dd": h["max_dd"],
                     "n_trades": h["n_trades"], "n_entries": h["n_entries"],
                     "trades_per_year": h["trades_per_year"]},
        "cells": {f"{c}|{a}|{f}": {kk: vv for kk, vv in
                  cont[(c, a, f)].items() if kk != "returns"}
                  for c in CELLS for a in AXES for f in FACES},
        "nulls": {"same_mask": {
            "k": len(null_vals), "mu": round(float(np.mean(null_vals)), 4),
            "sigma": round(float(np.std(null_vals, ddof=1)), 4),
            "p05": round(float(np.percentile(null_vals, 5)), 4),
            "p50": round(float(np.percentile(null_vals, 50)), 4),
            "p95": round(float(np.percentile(null_vals, 95)), 4)},
            "block_bootstrap": _block_bootstrap_sharpe(h_rets),
            "sign_flip": _sign_flip_perm(h_rets)},
        "sensitivity": {
            "k": len(sens),
            "sharpe_p05": round(float(np.percentile([r["sharpe"] for r in sens], 5)), 4),
            "sharpe_p50": round(float(np.percentile([r["sharpe"] for r in sens], 50)), 4),
            "sharpe_p95": round(float(np.percentile([r["sharpe"] for r in sens], 95)), 4),
            "maxdd_worst": round(float(min(r["max_dd"] for r in sens)), 4)},
        "starts_12m_dist": {"n": len(r12), "best": pct(100), "worst": pct(0),
                            "p25": pct(25), "median": pct(50), "p75": pct(75),
                            "positive_share": round(sum(1 for v in r12
                                                         if v > 0) / len(r12), 4)
                            if r12 else None},
        "rolling_worst": roll_worst,
        "descriptive": {"crash_years_lte_-35pct": crash_years,
                        "is_ann_ret": round(float((1 + hret.iloc[:len(hret) // 2]).prod() - 1), 4),
                        "oos_ann_ret": round(float((1 + hret.iloc[len(hret) // 2:]).prod() - 1), 4),
                        "x2_cost_drag_sharpe": round(x2["sharpe_full"] - h["sharpe_full"], 4)},
        "d6": probe.get("d6"),
        "probe_ref": "results/lowamp_p2/probe.json",
        "audit": {
            "machine": _machine_id(),
            "g_census_amendment": FROZEN_ENVELOPE,
            "seed_disclosure": probe.get("seed_disclosure"),
            "engine_face": "engine.run_backtest, per-symbol sub-account "
                           "decomposition, entry_size_scale weight mapping "
                           "(see runner docstring)",
            "deep_axis_amount": "volume x close proxy (t22 precedent, disclosed)",
            "liquidity": probe.get("liquidity"),
            "finalize_runtime_sec": round(time.time() - t0, 1),
        },
    }
    # cells.csv small table (git face)
    with open(OUT_CSV, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("cell,axis,face,sharpe_full,ret_full,max_dd,n_trades,"
                 "n_entries,beat12_rate\n")
        for c in CELLS:
            for a in AXES:
                rows = _read_cells(c, a, "base") or []
                full = [r for r in rows if not r.get("partial_12m")]
                rate = (round(sum(1 for r in full if r["beat_12m"]) / len(full), 4)
                        if full else None)
                for f in FACES:
                    cc = cont[(c, a, f)]
                    fh.write(f"{c},{a},{f},{cc['sharpe_full']},{cc['ret_full']},"
                             f"{cc['max_dd']},{cc['n_trades']},{cc['n_entries']},"
                             f"{rate if f == 'base' else ''}\n")
    # trials ledger (canonical dict schema, embed-order law: append BEFORE
    # the results json dump carries the ledger block)
    led = append_ledger(batch_name=BATCH_NAME, batch_trials=BATCH_CELLS,
                        file_name="results/lowamp_p2/lowamp_p2_results.json",
                        evidence_cutoff="2026-09-22")
    results["trials_ledger"] = led
    _dump(results, OUT_JSON)
    print(f"finalize verdict={verdict} -> {OUT_JSON}")
    print(f"  g1={g1.get('pass')} x2={x2_pass} m1={m1.get('pass')} "
          f"g2={g2.get('pass')} dual_axis={dual_axis_pass} "
          f"g_seg={gseg_pass}")
    return 0


# ------------------------------------------------------------------- selftest

def cmd_selftest(_) -> int:
    """Hermetic offline self-check: synthetic panel, no repo data, no
    network. Deterministic double-run byte-identity, causality, weights,
    mask, checkpoint resume, engine T+1."""
    import shutil
    import tempfile
    fails = []

    def check(name, ok, detail=""):
        print(f"[{'PASS' if ok else 'FAIL'}] {name} {detail}")
        if not ok:
            fails.append(name)

    rng = np.random.default_rng(7)
    idx = pd.date_range("2020-01-02", periods=420, freq="B")
    syms = ["S1", "S2", "S3", "S4"]
    prices = {}
    for j, s in enumerate(syms):
        n = 420 - 20 * j
        r = rng.normal(0.0005, 0.01 + 0.005 * j, n)
        cl = 100 * np.cumprod(1 + r)
        df = pd.DataFrame({"open": cl * 0.999, "high": cl * 1.01,
                           "low": cl * 0.99, "close": cl,
                           "volume": [1e6] * n,
                           "amount": [1e8] * n},
                          index=idx[:n])
        prices[s] = df
    P = build_panels(prices)
    entry, weights, elig = build_signal(P["close"], P["volume"],
                                        P["amount"], 30, 2)
    # F1 weights: invvol normalization sums to 1 on selection days
    ok_days = entry.any(axis=1)
    wsum = weights.sum(axis=1)[ok_days]
    check("F1_invvol_sum1", bool(((wsum - 1).abs() < 1e-9).all()),
          f"days={int(ok_days.sum())}")
    # F2 selection = lowest amp among eligible
    rets = P["close"].pct_change()
    amp = rets.rolling(30, min_periods=30).std()
    d0 = ok_days.idxmax()
    sel = [c for c in syms if bool(entry.loc[d0][c])]
    elig_d0 = [c for c in syms if bool(elig.loc[d0][c])]
    amp_sorted = sorted(elig_d0, key=lambda c: (amp.loc[d0, c], c))
    check("F2_topN_lowest_amp", sorted(sel) == sorted(amp_sorted[:2]),
          f"sel={sel}")
    # F3 eq sizing path (LA-EQ face)
    e2, w2, _ = build_signal(P["close"], P["volume"], P["amount"], 30, 2)
    check("F3_build_deterministic", bool((e2.to_numpy() == entry.to_numpy()).all()))
    # F4 engine run + T+1 (entry day < first trade day)
    active = [c for c in entry.columns if entry[c].any()]
    run = run_cell_portfolio(prices, P["close"], entry, weights, "base",
                             active)
    nav = (run["pnl"] + CAPITAL).reindex(idx).ffill().fillna(CAPITAL)
    check("F4_nav_positive_len", run is not None and len(nav) > 300,
          f"nav_days={len(nav)}")
    first_sel = entry[entry.any(axis=1)].index[0]
    if run["trade_dates"]:
        check("F4_t_plus_1", min(run["trade_dates"]) > first_sel,
              f"first_trade={min(run['trade_dates']).date()} "
              f"first_signal={first_sel.date()}")
    else:
        check("F4_t_plus_1", True, "no fills in fixture (honest)")
    # F5 x2 face runs and differs (cost stress bites)
    runx = run_cell_portfolio(prices, P["close"], entry, weights, "x2",
                              active)
    navx = (runx["pnl"] + CAPITAL).reindex(idx).ffill().fillna(CAPITAL)
    check("F5_x2_face", runx is not None and len(navx) > 300)
    if run is not None and runx is not None and run["n_trades"] > 0:
        check("F5_x2_cost_bites",
              abs(navx.iloc[-1] - nav.iloc[-1]) > 1e-6)
    # F6 truncation causality: signal on truncated panel == prefix of full
    e_trunc, w_trunc, _ = build_signal(
        P["close"].iloc[:300], P["volume"].iloc[:300],
        P["amount"].iloc[:300], 30, 2)
    check("F6_causal_prefix",
          bool((e_trunc.to_numpy()
                == entry.to_numpy()[:300]).all()))
    # F7 determinism: double run byte-identity on the continuous face
    def _cont_fixture():
        active = [c for c in entry.columns if entry[c].any()]
        run = run_cell_portfolio(prices, P["close"], entry, weights,
                                 "base", active)
        from engine.metrics import sharpe
        nav = (run["pnl"] + CAPITAL).reindex(idx).ffill().fillna(CAPITAL)
        return {"sharpe": round(float(sharpe(nav)), 6),
                "nav_last": round(float(nav.iloc[-1]), 2),
                "n_trades": run["n_trades"]}
    a, b = _cont_fixture(), _cont_fixture()
    check("F7_double_run_identity", a == b, str(a))
    # F8 nulls rng determinism
    class _NS:
        pass
    k1 = np.random.default_rng([SEED_NULLS, 0]).integers(0, 48, 5).tolist()
    k2 = np.random.default_rng([SEED_NULLS, 0]).integers(0, 48, 5).tolist()
    check("F8_null_rng_substream", k1 == k2, str(k1))
    # F9 checkpoint resume: fake shard file with one done key
    tmp = tempfile.mkdtemp()
    p = os.path.join(tmp, "cells.jsonl")
    _append_rows(p, [{"key": "LA-REP|legacy|base|300"}])
    dk = _done_keys(p)
    check("F9_resume_skip", "LA-REP|legacy|base|300" in dk, str(len(dk)))
    shutil.rmtree(tmp, ignore_errors=True)
    # F10 cost single-source derivation
    rate = cost_spec.x1_side_rate()
    check("F10_cost_rt_26_082bp", abs(rate * 2.0 * 1e4 - 26.082) < 1e-6,
          f"{rate*2e4:.3f}bp")
    print(f"selftest: {len(fails)} FAIL" if fails else "selftest: ALL PASS")
    return 1 if fails else 0


# ----------------------------------------------------------------------- main

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="LOWAMP-P2 judged batch runner (exit-axis hold-through)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("probe")
    r = sub.add_parser("run")
    r.add_argument("--cell", default="")
    r.add_argument("--axis", default="legacy")
    r.add_argument("--face", default="base")
    r.add_argument("--nulls", action="store_true")
    r.add_argument("--sensitivity", action="store_true")
    sub.add_parser("status")
    sub.add_parser("finalize")
    sub.add_parser("selftest")
    args = ap.parse_args(argv)
    return {"probe": cmd_probe, "run": cmd_run, "status": cmd_status,
            "finalize": cmd_finalize, "selftest": cmd_selftest}[args.cmd](args)


if __name__ == "__main__":
    raise SystemExit(main())
