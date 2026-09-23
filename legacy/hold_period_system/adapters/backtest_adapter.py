"""Backtest adapter: glue the top-level holding rules to a bar-feed engine.

This adapter is deliberately broker-agnostic: it only consumes
    bar_feed: Iterable[(date, {symbol: close_price})]
and produces
    trade_log: List[dict]

Drop-in replacement for any backtest engine that can replay daily bars.
"""
from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List, Optional, Tuple

from core import (
    CloseCommand,
    DailyEvaluator,
    ExitReason,
    PositionState,
)
from config import HoldPeriodConfig


@dataclass
class TradeRecord:
    date: str
    symbol: str
    strategy_id: str
    reason: str
    exit_price: float
    quantity: float
    pnl_rate: float
    hold_days: int
    message: str = ""


@dataclass
class BacktestResult:
    trades: List[TradeRecord] = field(default_factory=list)
    open_positions: Dict[str, PositionState] = field(default_factory=dict)


def run_backtest(
    initial_signals: Iterable[Tuple[str, str, float, str]],
    bar_feed: Iterable[Tuple[str, Dict[str, float]]],
    cfg: Optional[HoldPeriodConfig] = None,
    position_sizer: Optional[Callable[[str, str, float], float]] = None,
    market_circuit_breaker: Optional[Callable[[str], bool]] = None,
) -> BacktestResult:
    """Replay a daily bar feed against the top-level holding rules.

    Parameters
    ----------
    initial_signals
        Iterable of (date, symbol, price, strategy_id) representing entries
        opened at the close of `date`. The adapter opens a PositionState with
        hold_days=0 on that date and begins evaluating from the next bar.
    bar_feed
        Iterable of (date, {symbol: close_price}) sorted ascending by date.
    cfg
        Holding-period config; defaults to HoldPeriodConfig().
    position_sizer
        Callable(symbol, strategy_id, price) -> quantity. If None, quantity=1.
    market_circuit_breaker
        Callable(date) -> bool. Return True on dates when the market-wide
        circuit breaker is active; all positions close that bar.
    """
    evaluator = DailyEvaluator(cfg or HoldPeriodConfig())
    open_positions: Dict[str, PositionState] = {}
    result = BacktestResult()

    pending_entries: Dict[str, List[Tuple[str, float, str]]] = {}
    for d, sym, price, sid in initial_signals:
        pending_entries.setdefault(d, []).append((sym, price, sid))

    def execute_close(cmd: CloseCommand):
        qty = cmd.quantity
        rec = TradeRecord(
            date=current_date,
            symbol=cmd.symbol,
            strategy_id=cmd.strategy_id,
            reason=cmd.reason.value,
            exit_price=cmd.current_price,
            quantity=qty,
            pnl_rate=cmd.pnl_rate,
            hold_days=cmd.hold_days,
            message=cmd.message,
        )
        result.trades.append(rec)
        open_positions.pop(cmd.symbol, None)

    current_date = ""
    for date, price_map in bar_feed:
        current_date = date

        # 1) open entries scheduled for this date (filled at close)
        for sym, entry_price, sid in pending_entries.get(date, []):
            if sym in open_positions:
                continue
            qty = position_sizer(sym, sid, entry_price) if position_sizer else 1.0
            open_positions[sym] = PositionState(
                symbol=sym,
                strategy_id=sid,
                cost_price=entry_price,
                current_price=entry_price,
                hold_days=0,
                entry_date=date,
                quantity=qty,
            )

        # 2) mark-to-market current prices
        for sym, pos in open_positions.items():
            if sym in price_map:
                pos.current_price = price_map[sym]

        # 3) evaluate rules (priority chain inside evaluator)
        cb = market_circuit_breaker(date) if market_circuit_breaker else False
        evaluator.run(open_positions, execute_close, market_circuit_break=cb)

        # 4) advance bar for survivors
        evaluator.advance_bar(open_positions)

    result.open_positions = open_positions
    return result
