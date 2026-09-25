"""Futures CTA portfolio runner — CTA_P1 batch carrier (research/CTA_P1.md SS3).

Port of Money0923/quant/futures_backtest.py semantics, adapted to BigMoney
panel conventions. The ETF engine (engine/backtester.py) is UNTOUCHED
(O-2250 additive-iron rule) — this is a separate execution path for
margin/two-way/per-lot-fee/T+0 futures mechanics.

Accounting model (cash pool + signed notional, M0923 delta convention):
- lots are signed integers: long > 0, short < 0; target lots = |margin share|
  x equity / (mult x open x margin-rate) — futures position defined by
  margin, not notional (small accounts may round to zero lots, honestly).
- unified cash flow per fill: cash += -d_lots*mult*price - |d_lots|*per_lot_cost,
  per_lot_cost = (fee_lot + tick*mult) * cost_mult (1-tick/side slippage).
- margin budget: sum |target lots|*mult*open*margin <= equity; oversize ->
  shrink the largest occupant lot-by-lot (M0923 loop).
- per-variety margin share <= per_variety_cap (0.20) * equity
  (max_etf_position_pct red-line analogue for futures).
- T+0 two-way; T signal -> T+1 open execution (weights shifted one day inside).
- limit approximation (V1): open beyond prev close +/- variety limit -> that
  variety's target goes FLAT for the day (M0923 want=0 semantics on blocked
  days; closing is thereby allowed, new exposure is not).
- idle cash accrues 0% (V0 conservative; GC001 repo leg = G2 deepening item).

Adaptations vs M0923 (documented deviations, causality discipline):
- sizing equity uses YESTERDAY's close mark (M0923 used same-day close — a
  same-day look-ahead for sizing; fixed per project no-lookahead rule).
- weights matrix supports NaN = "carry" (no rebalance that day, lots frozen)
  for the r20 frozen-evaluation regime ("持有期内仓位不变"); non-NaN value =
  rebalance to that signed target margin share (0 = close position).
- marking uses last finite close (ffill semantics) so a mid-panel hole cannot
  zero out equity (defensive; CTA_P1 G3 gate requires zero holes anyway).
"""
from __future__ import annotations

import math
import os
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from engine.metrics import annual_return, max_drawdown, sharpe

# ---------------------------------------------------------------- constants
# Provenance: Money0923/quant/futures.py FUT_UNIVERSE + FUT_LIMITS, frozen
# 2026-09 (exchange-published approximations, M0923 verified batch). tick =
# exchange minimum price increment (for the 1-tick/side slippage term).
FUT_META: dict[str, dict] = {
    "IF": {"name": "沪深300股指", "margin": 0.12, "mult": 300.0, "fee_lot": 27.6, "tick": 0.2, "limit": 0.10, "group": "equity_index"},
    "IC": {"name": "中证500股指", "margin": 0.14, "mult": 200.0, "fee_lot": 34.6, "tick": 0.2, "limit": 0.12, "group": "equity_index"},
    "IM": {"name": "中证1000股指", "margin": 0.15, "mult": 200.0, "fee_lot": 36.8, "tick": 0.2, "limit": 0.12, "group": "equity_index"},
    "IH": {"name": "上证50股指", "margin": 0.12, "mult": 300.0, "fee_lot": 26.0, "tick": 0.2, "limit": 0.10, "group": "equity_index"},
    "T":  {"name": "十年国债", "margin": 0.02, "mult": 10000.0, "fee_lot": 4.2, "tick": 0.005, "limit": 0.02, "group": "bond"},
    "TF": {"name": "五年国债", "margin": 0.012, "mult": 10000.0, "fee_lot": 3.7, "tick": 0.005, "limit": 0.012, "group": "bond"},
    "RB": {"name": "螺纹钢", "margin": 0.09, "mult": 10.0, "fee_lot": 4.3, "tick": 1.0, "limit": 0.07, "group": "commodity"},
    "AU": {"name": "黄金", "margin": 0.08, "mult": 1000.0, "fee_lot": 10.1, "tick": 0.02, "limit": 0.08, "group": "commodity"},
    "SC": {"name": "原油", "margin": 0.10, "mult": 1000.0, "fee_lot": 20.0, "tick": 0.1, "limit": 0.13, "group": "commodity"},
    # CTA_WAVE1 TS leg (additive, R187): all values exchange-verified 2026-09-25
    # vs CFFEX official faces (R169/R173 discipline, evidence
    # results/cta_wave1_g2_ts_check.json): /cn/2ts.html contract table
    # (mult 20000 = 2,000,000 face / 100-yuan quote, margin 0.5%, limit +/-0.5%)
    # + /sj/jscs/202609/21/20260921_1.csv (fee 3 yuan/lot). tick frozen at the
    # VERIFIED 0.002 (prereg provisional was 0.005; 150% deviation > 30% ->
    # freeze-verified protocol, prereg SS3 G2, disclosed in batch JSON).
    "TS": {"name": "两年国债", "margin": 0.005, "mult": 20000.0, "fee_lot": 3.0, "tick": 0.002, "limit": 0.005, "group": "bond"},
}

FUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "data", "futures_daily")
FIELDS = ("open", "high", "low", "close", "volume")


def load_panel(start: str = "2017-01-17", end: str = "2026-09-23",
               varieties: list[str] | None = None) -> dict:
    """Read data/futures_daily/*.csv into an aligned dates x variety panel.

    Panel = union of variety dates within [start, end]; a variety absent on a
    date (pre-listing, untraded) is NaN there. Only OHLCV fields are loaded —
    oi/settle are disclosure metadata only (CTA_P1 SS2 signal-input freeze).
    """
    varieties = list(FUT_META) if varieties is None else list(varieties)
    frames: dict[str, pd.DataFrame] = {}
    for v in varieties:
        path = os.path.join(FUT_DIR, f"{v}.csv")
        if not os.path.exists(path):
            raise FileNotFoundError(f"futures csv missing: {path}")
        df = pd.read_csv(path, index_col=0, parse_dates=True).sort_index()
        df = df.loc[(df.index >= pd.Timestamp(start)) & (df.index <= pd.Timestamp(end))]
        frames[v] = df
    all_dates = sorted(set().union(*[set(f.index) for f in frames.values()]))
    idx = pd.DatetimeIndex(all_dates)
    panel = {"dates": idx}
    for fld in FIELDS:
        panel[fld] = pd.DataFrame(
            {v: frames[v][fld].reindex(idx) for v in varieties},
            index=idx, columns=varieties)
    return panel


@dataclass
class FutResult:
    equity: pd.Series
    invested: pd.Series
    trades: list
    metrics: dict
    per_variety: dict = field(default_factory=dict)
    daily_pnl: pd.DataFrame | None = None


def run(panel: dict, weights: pd.DataFrame, start_cash: float = 1_000_000.0,
        cost_mult: float = 1.0, per_variety_cap: float = 0.20,
        margin_cap: float = 1.0) -> FutResult:
    """CTA portfolio run. weights: dates x variety signed margin-share of
    equity; NaN = carry (no rebalance); rebalance executes next-day open.
    margin_cap: total margin usage ceiling as a fraction of yesterday's
    equity (CTA_WAVE1 Leg B 50/30 variants); default 1.0 = the original
    M0923 full-budget semantics, bit-identical for all prior batches."""
    varieties = list(weights.columns)
    dates = panel["dates"]
    if not weights.index.equals(dates):
        raise ValueError("weights index must equal panel dates")
    op = panel["open"].reindex(columns=varieties).to_numpy(dtype=float)
    cl = panel["close"].reindex(columns=varieties).to_numpy(dtype=float)
    m = len(varieties)
    mult = np.array([FUT_META[v]["mult"] for v in varieties], dtype=float)
    margin = np.array([FUT_META[v]["margin"] for v in varieties], dtype=float)
    fee_lot = np.array([FUT_META[v]["fee_lot"] for v in varieties], dtype=float)
    tickv = np.array([FUT_META[v]["tick"] * FUT_META[v]["mult"] for v in varieties],
                     dtype=float)
    lim = np.array([FUT_META[v]["limit"] for v in varieties], dtype=float)
    per_lot_cost = (fee_lot + tickv) * float(cost_mult)

    wmat = weights.to_numpy(dtype=float)
    wshift = np.full_like(wmat, np.nan)
    wshift[1:] = wmat[:-1]          # T signal -> T+1 open; day 0 never executes

    lots = np.zeros(m, dtype=np.int64)
    avg_entry = np.zeros(m, dtype=float)
    prev_close = np.full(m, np.nan)  # last finite close per variety (ffill mark)
    cash = float(start_cash)
    n = len(dates)
    eq_arr = np.zeros(n)
    inv_arr = np.zeros(n)
    pnl_arr = np.full((n, m), np.nan)
    trades: list[dict] = []
    n_entries = 0
    turnover = 0.0
    wins = closes = 0
    margin_ratio_max = 0.0

    for i in range(n):
        o, c = op[i], cl[i]
        lots_before = lots.copy()
        # yesterday's mark (ffill) -> causal sizing base
        mark = np.where(np.isfinite(c), c, np.where(np.isfinite(o), o, prev_close))
        eq_prev = cash + float(np.nansum(lots * mult * np.where(np.isfinite(mark), mark, 0.0)))
        known = np.isfinite(prev_close)
        up = prev_close * (1.0 + lim)
        dn = prev_close * (1.0 - lim)
        tradable = np.isfinite(o) & known & (eq_prev > 0)

        ws = wshift[i]
        has_t = np.isfinite(ws)
        want = lots.copy()
        for j in range(m):
            if not has_t[j]:
                continue               # NaN = carry (position frozen)
            if not tradable[j]:
                continue               # cannot trade: keep current lots (carry)
            tw = ws[j]
            if tw == 0.0:
                want[j] = 0            # explicit flat target
                continue
            if tw > 0 and o[j] >= up[j] - 1e-9:
                want[j] = 0            # limit-up: no new long (M0923 flat rule)
                continue
            if tw < 0 and o[j] <= dn[j] + 1e-9:
                want[j] = 0            # limit-down: no new short
                continue
            margin_share = min(abs(tw) * eq_prev, per_variety_cap * eq_prev)
            lots_raw = margin_share / (mult[j] * o[j] * margin[j])
            want[j] = int(math.copysign(math.floor(lots_raw), tw))

        # margin budget over TARGET state: shrink largest occupant (M0923);
        # margin_cap < 1.0 = CTA_WAVE1 Leg B global-usage ceiling (shrink
        # rule identical, only the budget line moves).
        usage = np.abs(want) * mult * np.nan_to_num(o) * margin
        guard = 0
        while usage.sum() > margin_cap * eq_prev and (np.abs(want) > 0).any():
            j = int(np.argmax(usage))
            want[j] += -1 if want[j] > 0 else 1
            usage = np.abs(want) * mult * np.nan_to_num(o) * margin
            guard += 1
            if guard > 100000:
                break
        if eq_prev > 0:
            margin_ratio_max = max(margin_ratio_max, float(usage.sum() / eq_prev))

        # rebalance: close segment first (flip = full close), then open segment
        for j in range(m):
            if not tradable[j]:
                continue
            cur, tgt = int(lots[j]), int(want[j])
            if cur == tgt:
                continue
            close_qty = 0
            if cur != 0:
                if cur * tgt < 0:
                    close_qty = cur
                elif abs(tgt) < abs(cur):
                    close_qty = cur - tgt
            if close_qty != 0:
                direction = 1 if cur > 0 else -1
                qty = abs(close_qty)
                pnl = (o[j] - avg_entry[j]) * direction * mult[j] * qty \
                    - qty * per_lot_cost[j]
                cash += close_qty * mult[j] * o[j] - qty * per_lot_cost[j]
                trades.append({"date": str(dates[i].date()), "variety": varieties[j],
                               "side": "sell" if direction > 0 else "buy",
                               "lots": int(qty), "price": round(float(o[j]), 4),
                               "pnl": round(pnl, 2), "reason": "fut_close"})
                wins += 1 if pnl > 0 else 0
                closes += 1
                turnover += qty * mult[j] * o[j]
                lots[j] -= close_qty
                if lots[j] == 0:
                    avg_entry[j] = 0.0
                cur = int(lots[j])
            delta = tgt - cur
            if delta != 0:
                cash += -delta * mult[j] * o[j] - abs(delta) * per_lot_cost[j]
                old_abs, add_abs = abs(cur), abs(delta)
                if cur * delta >= 0:
                    avg_entry[j] = ((avg_entry[j] * old_abs + o[j] * add_abs)
                                    / (old_abs + add_abs)) if (old_abs + add_abs) else o[j]
                else:
                    avg_entry[j] = o[j]
                trades.append({"date": str(dates[i].date()), "variety": varieties[j],
                               "side": "buy" if delta > 0 else "sell",
                               "lots": int(abs(delta)), "price": round(float(o[j]), 4),
                               "pnl": 0.0, "reason": "fut_open"})
                n_entries += 1
                turnover += abs(delta) * mult[j] * o[j]
                lots[j] = tgt

        # close-of-day marking + per-variety daily PnL attribution
        mark_now = np.where(np.isfinite(c), c, np.where(np.isfinite(o), o, np.nan))
        for j in range(m):
            if not np.isfinite(mark_now[j]):
                mark_now[j] = prev_close[j] if np.isfinite(prev_close[j]) else np.nan
        for j in range(m):
            if np.isfinite(prev_close[j]) and np.isfinite(mark_now[j]):
                d = lots[j] - lots_before[j]
                fees = abs(d) * per_lot_cost[j]
                exec_px = o[j] if np.isfinite(o[j]) else mark_now[j]
                pnl_arr[i, j] = (-d * mult[j] * exec_px - fees
                                 + lots[j] * mult[j] * mark_now[j]
                                 - lots_before[j] * mult[j] * prev_close[j])
        eq = cash + float(np.nansum(
            lots * mult * np.where(np.isfinite(mark_now), mark_now, 0.0)))
        eq_arr[i] = eq
        inv_arr[i] = float(np.nansum(np.abs(lots) * mult
                                     * np.where(np.isfinite(mark_now), mark_now, 0.0)))
        prev_close = np.where(np.isfinite(c), c, prev_close)

    equity = pd.Series(eq_arr, index=dates, name="equity")
    invested = pd.Series(inv_arr, index=dates, name="invested")
    daily_pnl = pd.DataFrame(pnl_arr, index=dates, columns=varieties)
    per_variety: dict = {}
    groups: dict[str, float] = {}
    for v in varieties:
        s = daily_pnl[v].dropna()
        pv_sharpe = 0.0
        if len(s) > 20 and s.std(ddof=1) > 0:
            pv_sharpe = float(s.mean() / s.std(ddof=1) * np.sqrt(252))
        per_variety[v] = {"pnl_total": round(float(s.sum()), 2) if len(s) else 0.0,
                          "sharpe": round(pv_sharpe, 4),
                          "group": FUT_META[v]["group"]}
        groups[FUT_META[v]["group"]] = round(
            groups.get(FUT_META[v]["group"], 0.0) + per_variety[v]["pnl_total"], 2)
    metrics = {
        "sharpe": round(float(sharpe(equity)), 4),
        "annual_return": round(float(annual_return(equity)), 4),
        "max_drawdown": round(float(max_drawdown(equity)), 4),
        "n_trades": len(trades),
        "n_entries": int(n_entries),
        "n_closes": int(closes),
        "win_rate": round(wins / closes, 4) if closes else 0.0,
        "turnover": round(float(turnover), 2),
        "final_equity": round(float(eq_arr[-1]), 2),
        "groups_pnl": groups,
        "margin_usage_max_ratio": round(margin_ratio_max, 6),
    }
    return FutResult(equity=equity, invested=invested, trades=trades,
                     metrics=metrics, per_variety=per_variety, daily_pnl=daily_pnl)


def yearly_returns(equity: pd.Series) -> dict:
    """Calendar-year total returns from an equity curve (report convention)."""
    out: dict = {}
    if len(equity) < 2:
        return out
    last_by_year = equity.groupby(equity.index.year).last()
    years = sorted(last_by_year.index)
    for k, yr in enumerate(years):
        base = equity.iloc[0] if k == 0 else last_by_year[years[k - 1]]
        out[str(yr)] = round(float(last_by_year[yr] / base - 1.0), 4)
    return out


def basis_carry_signal(fut_close: pd.Series, spot_close: pd.Series,
                       window: int = 60, band: float = 0.002) -> pd.Series:
    """Leg C dual-input signal interface (CTA_WAVE1 SS3, additive; ETF engine
    untouched). r = F_close/S_close (scale-free premium ratio, ETF proxy of
    the index -- proxy law disclosed in prereg SS2); m = window-day rolling
    mean of r; dev = r/m - 1. dev < -band -> +1 (deep discount: long futures,
    collect basis convergence / hedge-insurance premium); dev > +band -> -1;
    dead zone -> 0 (explicit flat). Days without basis data (pre spot-window,
    futures not listed, spot gap beyond ffill) -> NaN (no signal, carry).

    Causality: spot is reindexed to the futures calendar with ffill (last
    PRIOR spot close only); every statistic at T uses data up to and
    including T; execution lag is the runner's own T+1 open shift.
    """
    if not isinstance(fut_close.index, pd.DatetimeIndex):
        raise TypeError("fut_close must carry a DatetimeIndex")
    spot = spot_close.reindex(fut_close.index).ffill()
    r = fut_close / spot
    m = r.rolling(window, min_periods=window).mean()
    dev = r / m - 1.0
    sig = pd.Series(0.0, index=fut_close.index)
    sig[dev < -band] = 1.0
    sig[dev > band] = -1.0
    sig = sig.where(r.notna() & m.notna())     # no-basis days -> NaN (carry)
    return sig
