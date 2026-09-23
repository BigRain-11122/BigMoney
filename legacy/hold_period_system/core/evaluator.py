from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

from .enums import ExitReason
from .position_state import PositionState
from .risk_rules import Decision, evaluate_position
from config import HoldPeriodConfig


@dataclass
class CloseCommand:
    symbol: str
    strategy_id: str
    reason: ExitReason
    pnl_rate: float
    hold_days: int
    current_price: float
    quantity: float
    message: str


class DailyEvaluator:
    """Daily close evaluator shared by backtest and live trading.

    Usage:
        ev = DailyEvaluator(cfg)
        ev.on_bar_close(portfolio_positions, market_circuit_break=False,
                        close_executor=your_close_func)

    The caller (backtest engine / live broker adapter) owns:
      - incrementing hold_days once per daily bar (via advance_bar)
      - updating current_price on each PositionState
      - executing the actual close (provided as close_executor)
    """

    def __init__(self, cfg: Optional[HoldPeriodConfig] = None):
        self.cfg = cfg or HoldPeriodConfig()

    def advance_bar(self, positions: Dict[str, PositionState]) -> None:
        """Call once per daily bar, AFTER close evaluation for the bar.

        Increments hold_days for every open position.
        """
        for p in positions.values():
            p.hold_days += 1

    def evaluate(
        self,
        positions: Dict[str, PositionState],
        market_circuit_break: bool = False,
    ) -> List[CloseCommand]:
        """Evaluate all open positions. Returns the list of close commands.

        Note: this does NOT mutate positions; the caller should remove closed
        positions after the executor runs. hold_days increment is done by
        advance_bar() on the next bar, keeping the rule exactly as specified:
            at bar N close, if hold_days (already = N-1) hits threshold -> close.
        """
        commands: List[CloseCommand] = []
        for sym, pos in positions.items():
            d: Decision = evaluate_position(pos, self.cfg, market_circuit_break)
            if d.should_close:
                commands.append(CloseCommand(
                    symbol=pos.symbol,
                    strategy_id=pos.strategy_id,
                    reason=d.reason,
                    pnl_rate=d.pnl_rate,
                    hold_days=d.hold_days,
                    current_price=pos.current_price,
                    quantity=pos.quantity,
                    message=d.message,
                ))
        return commands

    def run(
        self,
        positions: Dict[str, PositionState],
        close_executor: Callable[[CloseCommand], None],
        market_circuit_break: bool = False,
    ) -> List[CloseCommand]:
        """One-call helper: evaluate + execute + return executed commands."""
        commands = self.evaluate(positions, market_circuit_break)
        for cmd in commands:
            try:
                close_executor(cmd)
            except Exception as e:  # pragma: no cover - defensive
                cmd.message = f"executor_error: {e}"
        return commands
