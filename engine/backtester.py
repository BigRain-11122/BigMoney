"""Backtest engine.

Fixes vs old version:
  - entry signal at day T -> execute at day T+1 OPEN (no look-ahead)
  - T+1: positions opened today cannot be sold today
  - fees from knowledge/rules.py (commission + handling + slippage)
  - ffill + min listing age filter
"""
import numpy as np
import pandas as pd

from .exit_rules import ExitConfig, ExitState, evaluate
from .metrics import summarize
from knowledge.rules import FeeSchedule, is_t0


def _entry_signal(close: pd.Series, fast: int = 5, slow: int = 20) -> pd.Series:
    f = close.rolling(fast).mean()
    s = close.rolling(slow).mean()
    cross = (f > s) & (f.shift(1) <= s.shift(1))
    return cross.fillna(False)


def _exit_signal(close: pd.Series, fast: int = 5, slow: int = 20) -> pd.Series:
    f = close.rolling(fast).mean()
    s = close.rolling(slow).mean()
    cross = (f < s) & (f.shift(1) >= s.shift(1))
    return cross.fillna(False)


def run_backtest(prices: dict, params: dict,
                 initial_cash: float = 1_000_000.0,
                 entry_signal: pd.DataFrame = None,
                 exit_signal: pd.DataFrame = None) -> dict:
    """prices: dict[symbol] -> DataFrame with date index, cols open/close/high/low.

    J7 signal-injection adapter (BACKTEST_PLAN S2 contract):
      entry_signal / exit_signal: DataFrame (date x symbol), truthy -> on.
      Default None -> built-in MA(5,20) cross (432-grid behavior unchanged).
      Signals computed on day T close execute at T+1 open (no look-ahead).
    """
    cfg = ExitConfig(
        take_profit_levels=tuple(params.get("take_profit_levels", (0.05, 0.10, 0.20))),
        trailing_activate=params.get("trailing_stop_activate", 0.05),
        time_decay_period=params.get("time_decay_period", 12),
        time_decay_threshold=params.get("time_decay_threshold", 0.02),
        position_size_pct=params.get("position_size_pct", 0.10),
        max_positions=params.get("max_positions", 5),
    )
    fee = FeeSchedule()
    cost_rate = fee.commission_rate + fee.handling_fee + fee.supervision_fee + fee.slippage_a

    # align all symbols on common trading calendar
    closes = pd.DataFrame({sym: df["close"] for sym, df in prices.items()}).sort_index()
    opens = pd.DataFrame({sym: df["open"] for sym, df in prices.items()}).sort_index()
    closes = closes.ffill()
    opens = opens.ffill()

    cash = initial_cash
    positions: dict[str, ExitState] = {}
    trades: list[dict] = []
    equity_curve: list[float] = []
    dates = closes.index

    # precompute signals on close
    def _injected(sig: pd.DataFrame, sym: str) -> pd.Series:
        if sig is None or sym not in sig.columns:
            return pd.Series(False, index=dates)
        return sig[sym].reindex(dates).fillna(0).astype(bool)

    if entry_signal is None:
        entry_sig = {sym: _entry_signal(closes[sym]) for sym in closes.columns}
    else:
        entry_sig = {sym: _injected(entry_signal, sym) for sym in closes.columns}
    if exit_signal is None:
        exit_sig = {sym: _exit_signal(closes[sym]) for sym in closes.columns}
    else:
        exit_sig = {sym: _injected(exit_signal, sym) for sym in closes.columns}

    # pending entries: signal fired at day T, execute at day T+1 open
    pending_entries: dict[str, dict] = {}

    for i, date in enumerate(dates):
        row_close = closes.loc[date]
        row_open = opens.loc[date]

        # 0) execute pending entries at today's OPEN
        for sym, info in list(pending_entries.items()):
            if sym in positions:
                continue
            if len(positions) >= cfg.max_positions:
                break
            px = row_open[sym]
            if pd.isna(px):
                continue
            target_value = initial_cash * cfg.position_size_pct
            qty = target_value / px
            total_cost = px * qty * (1 + cost_rate)
            if total_cost > cash:
                continue
            cash -= total_cost
            positions[sym] = ExitState(
                cost_price=px, quantity=qty, high_watermark=px,
            )
            del pending_entries[sym]

        # 1) manage open positions at today's CLOSE
        for sym in list(positions.keys()):
            st = positions[sym]
            # T+1: cannot sell on entry day
            if st.hold_days == 0 and not is_t0(sym):
                st.hold_days += 1
                continue
            px = row_close[sym]
            if pd.isna(px):
                st.hold_days += 1
                continue
            sig_rev = bool(exit_sig[sym].loc[date])
            action = evaluate(st, px, cfg, signal_reversed=sig_rev)

            if action.should_close:
                qty = st.quantity * action.close_fraction
                gross = qty * px
                proceeds = gross * (1 - cost_rate)
                cash += proceeds
                pnl_rate = (px - st.cost_price) / st.cost_price
                trades.append({
                    "date": str(date.date()), "symbol": sym,
                    "reason": action.reason,
                    "price": round(px, 4), "qty": round(qty, 2),
                    "fee": round(gross * cost_rate, 2),
                    "pnl": round((px - st.cost_price) * qty - gross * cost_rate, 2),
                    "pnl_rate": round(pnl_rate, 4),
                    "hold_days": st.hold_days,
                })
                if action.close_fraction >= 1.0:
                    del positions[sym]
                else:
                    st.quantity -= qty
                    st.tier_reached += 1
            st.hold_days += 1

        # 2) queue new entries based on today's close signals
        for sym in closes.columns:
            if sym in positions or sym in pending_entries:
                continue
            if len(positions) + len(pending_entries) >= cfg.max_positions:
                break
            if entry_sig[sym].loc[date]:
                pending_entries[sym] = {"queued": str(date.date())}

        # 3) mark-to-market
        pos_val = sum(st.quantity * row_close[sym]
                      for sym, st in positions.items() if sym in row_close)
        equity_curve.append(cash + pos_val)

    equity = pd.Series(equity_curve, index=dates[:len(equity_curve)])
    metrics = summarize(equity, trades)
    return {
        "metrics": metrics,
        "trades": trades,
        "equity_curve": [round(v, 2) for v in equity_curve],
    }
