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
from knowledge.rules import (
    FeeSchedule, is_t0,
    ADV20_TIER_2BP_YUAN, ADV20_TIER_5BP_YUAN, ADV_FILL_CAP_RATE,
    SLIPPAGE_TIER_2BP, SLIPPAGE_TIER_5BP, SLIPPAGE_TIER_10BP, COST_BASIS_V2,
)


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
                 exit_signal: pd.DataFrame = None,
                 fill_guard=None,
                 cost_v2=None) -> dict:
    """prices: dict[symbol] -> DataFrame with date index, cols open/close/high/low.

    J7 signal-injection adapter (BACKTEST_PLAN S2 contract):
      entry_signal / exit_signal: DataFrame (date x symbol), truthy -> on.
      Default None -> built-in MA(5,20) cross (432-grid behavior unchanged).
      Signals computed on day T close execute at T+1 open (no look-ahead).

    P4-B2 s3.1 fill_guard (additive; default None = legacy path
    byte-identical). Execution-time transactability overlay built from the
    execution day's OWN information (no look-ahead):
      dict {"buy": DF(date x symbol, bool), "sell": DF(...)} -> side-aware
        (stock limit-board semantics: buy blocked on sealed limit-UP open,
         sell deferred off sealed limit-DOWN close);
      single DataFrame(date x symbol, bool) -> applied to BOTH sides.
      buy False on execution day -> pending entry DROPPED (unfilled order,
        not retried; a fresh signal may re-queue later -- that is a new order).
      sell False on exit day -> exit DEFERRED: retried each later close,
        force-executed at the first fillable close with the ORIGINAL exit
        reason/size (stale decision, honest late fill).
      Missing symbol/date -> unrestricted (True).

    D5 cost-basis v2 (BACKTEST_SCIENCE.md s5; additive; default None =
    legacy path byte-identical). cost_v2 accepts:
      DataFrame(date x symbol) -- ADV(20d) panel: rolling 20-day mean daily
        turnover in yuan ENDING at each date (inclusive); the engine shifts
        one day so an execution on day D only sees information through the
        prior (signal) close -- no look-ahead;
      dict {"adv20": <that DataFrame>} -- same panel keyed.
    When ON: per-side slippage tiered 2/5/10bp by ADV(20d) (missing ->
    10bp conservative = legacy); entry demand capped at 1% of ADV(20d)
    (excess does not fill, partial fill kept; zero/negative ADV -> order
    dropped; missing ADV -> no cap, counted). Exits keep the tiered rate but
    are NOT quantity-capped (exit machine owns sizing via close_fraction).
    Basis + counters are disclosed in result["cost_v2"] (key absent when off).
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

    # D5 cost v2 panels (built only when the additive flag is ON; the
    # legacy path below never touches these variables when cost_v2=None).
    if cost_v2 is None:
        tier_v2 = cap_v2 = None
        stats_v2 = None
    else:
        adv = cost_v2["adv20"] if isinstance(cost_v2, dict) else cost_v2
        adv = adv.reindex(index=dates, columns=closes.columns)
        adv_arr = adv.shift(1).to_numpy(dtype=float)   # exec day -> signal-day info
        with np.errstate(invalid="ignore"):
            finite = np.isfinite(adv_arr)
            tier_arr = np.full(adv_arr.shape, SLIPPAGE_TIER_10BP, dtype=float)
            m5 = finite & (adv_arr >= ADV20_TIER_5BP_YUAN)
            m2 = finite & (adv_arr >= ADV20_TIER_2BP_YUAN)
            tier_arr[m5] = SLIPPAGE_TIER_5BP
            tier_arr[m2] = SLIPPAGE_TIER_2BP          # m2 subset of m5: 2bp wins
            cap_arr = np.where(finite, ADV_FILL_CAP_RATE * adv_arr, np.inf)
        tier_v2 = pd.DataFrame(tier_arr, index=dates, columns=closes.columns)
        cap_v2 = pd.DataFrame(cap_arr, index=dates, columns=closes.columns)
        stats_v2 = {
            "cost_basis": COST_BASIS_V2,
            "tier_entries_2bp": 0, "tier_entries_5bp": 0,
            "tier_entries_10bp": 0,
            "capped_entries": 0, "dropped_zero_adv": 0,
            "missing_adv_executions": 0,
        }

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

    # P4-B2 s3.1 fill guard: None -> fully unrestricted (legacy path).
    def _guard_arrays(guard) -> dict:
        out = {}
        for sym in closes.columns:
            if guard is not None and sym in guard.columns:
                out[sym] = guard[sym].reindex(dates).fillna(True).astype(bool).to_numpy()
            else:
                out[sym] = None
        return out

    if fill_guard is None:
        buy_g = sell_g = None
    elif isinstance(fill_guard, dict):
        buy_g = _guard_arrays(fill_guard.get("buy"))
        sell_g = _guard_arrays(fill_guard.get("sell"))
    else:
        buy_g = _guard_arrays(fill_guard)
        sell_g = buy_g

    def _fillable(arrs: dict, sym: str, i: int) -> bool:
        if arrs is None:
            return True
        a = arrs.get(sym)
        return True if a is None else bool(a[i])

    # pending entries: signal fired at day T, execute at day T+1 open
    pending_entries: dict[str, dict] = {}
    # sell-deferral book (P4-B2): sym -> stored ExitAction awaiting a fillable close
    deferred_exits: dict[str, object] = {}

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
            if not _fillable(buy_g, sym, i):
                # P4-B2 buy rejection: unfilled at this open (e.g. sealed
                # limit-up) -> order dropped, not retried on stale signal.
                del pending_entries[sym]
                continue
            if tier_v2 is None:
                # legacy path (verbatim, byte-identical when flag off)
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
                continue
            # --- D5 cost-v2 entry path ---
            target_value = initial_cash * cfg.position_size_pct
            cap_i = float(cap_v2.at[date, sym])
            tier_i = float(tier_v2.at[date, sym])
            if not np.isfinite(cap_i):
                # missing ADV: conservative 10bp slippage (= legacy), no cap
                stats_v2["missing_adv_executions"] += 1
            elif cap_i <= 0:
                # zero/negative ADV(20d): no measurable liquidity -> dropped
                del pending_entries[sym]
                stats_v2["dropped_zero_adv"] += 1
                continue
            elif cap_i < target_value:
                # D5 volume constraint: demand > 1% ADV -> excess unfilled
                target_value = cap_i
                stats_v2["capped_entries"] += 1
            rate_buy = (fee.commission_rate + fee.handling_fee
                        + fee.supervision_fee + tier_i)
            qty = target_value / px
            total_cost = px * qty * (1 + rate_buy)
            if total_cost > cash:
                continue
            cash -= total_cost
            if tier_i == SLIPPAGE_TIER_2BP:
                stats_v2["tier_entries_2bp"] += 1
            elif tier_i == SLIPPAGE_TIER_5BP:
                stats_v2["tier_entries_5bp"] += 1
            else:
                stats_v2["tier_entries_10bp"] += 1
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
            if sym in deferred_exits:
                # P4-B2 sell deferral: exit already decided, executing late.
                action = deferred_exits.pop(sym)
            else:
                action = evaluate(st, px, cfg, signal_reversed=bool(exit_sig[sym].loc[date]))

            if action.should_close:
                if not _fillable(sell_g, sym, i):
                    # P4-B2 sell deferral: no liquidity at this close (e.g.
                    # sealed limit-down) -> retry at next fillable close.
                    deferred_exits[sym] = action
                    st.hold_days += 1
                    continue
                qty = st.quantity * action.close_fraction
                gross = qty * px
                if tier_v2 is None:
                    rate_sell = cost_rate   # legacy path (identical arithmetic)
                else:
                    rate_sell = (fee.commission_rate + fee.handling_fee
                                 + fee.supervision_fee
                                 + float(tier_v2.at[date, sym]))
                proceeds = gross * (1 - rate_sell)
                cash += proceeds
                pnl_rate = (px - st.cost_price) / st.cost_price
                trades.append({
                    "date": str(date.date()), "symbol": sym,
                    "reason": action.reason,
                    "price": round(px, 4), "qty": round(qty, 2),
                    "fee": round(gross * rate_sell, 2),
                    "pnl": round((px - st.cost_price) * qty - gross * rate_sell, 2),
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
    result = {
        "metrics": metrics,
        "trades": trades,
        "equity_curve": [round(v, 2) for v in equity_curve],
    }
    if stats_v2 is not None:
        result["cost_v2"] = stats_v2
    return result
