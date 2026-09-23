from dataclasses import dataclass
from typing import Optional

from .enums import ExitReason
from .position_state import PositionState
from .time_manager import dynamic_max_hold_days
from config import HoldPeriodConfig


@dataclass
class Decision:
    reason: ExitReason
    should_close: bool
    hold_days: int
    pnl_rate: float
    max_hold_days: int
    message: str = ""

    def to_dict(self) -> dict:
        return {
            "reason": self.reason.value,
            "should_close": self.should_close,
            "hold_days": self.hold_days,
            "pnl_rate": round(self.pnl_rate, 6),
            "max_hold_days": self.max_hold_days,
            "message": self.message,
        }


def evaluate_position(
    state: PositionState,
    cfg: HoldPeriodConfig,
    market_circuit_break: bool = False,
) -> Decision:
    """Priority chain (top to bottom, first hit wins):

      1. Market-wide circuit breaker -> close everything.
      2. Individual stop loss (pnl_rate <= stop_loss_rate) -> close immediately.
      3. Dynamic time exit (hold_days >= dynamic_max_hold_days) -> close.
      4. Global hard limit (hold_days >= global_hard_limit_days) -> close.
      5. Otherwise hold.
    """
    hold_days = state.hold_days
    pnl_rate = state.pnl_rate
    max_hold = dynamic_max_hold_days(state, cfg)

    # P1: market circuit breaker
    if market_circuit_break:
        return Decision(
            reason=ExitReason.MARKET_CIRCUIT_BREAK,
            should_close=True,
            hold_days=hold_days,
            pnl_rate=pnl_rate,
            max_hold_days=max_hold,
            message="market circuit breaker triggered",
        )

    # P2: individual stop loss
    if pnl_rate <= cfg.stop_loss_rate:
        return Decision(
            reason=ExitReason.INDIVIDUAL_STOP_LOSS,
            should_close=True,
            hold_days=hold_days,
            pnl_rate=pnl_rate,
            max_hold_days=max_hold,
            message=f"stop loss hit pnl={pnl_rate:.4f} <= {cfg.stop_loss_rate}",
        )

    # P3: dynamic time exit (loss=8d, profit=15d)
    if hold_days >= max_hold:
        return Decision(
            reason=ExitReason.DYNAMIC_TIME_EXIT,
            should_close=True,
            hold_days=hold_days,
            pnl_rate=pnl_rate,
            max_hold_days=max_hold,
            message=f"dynamic time exit at day {hold_days} (max={max_hold})",
        )

    # P4: global hard ceiling (double insurance)
    if hold_days >= cfg.global_hard_limit_days:
        return Decision(
            reason=ExitReason.GLOBAL_HARD_LIMIT,
            should_close=True,
            hold_days=hold_days,
            pnl_rate=pnl_rate,
            max_hold_days=max_hold,
            message=f"global hard limit at day {hold_days}",
        )

    return Decision(
        reason=ExitReason.HOLD,
        should_close=False,
        hold_days=hold_days,
        pnl_rate=pnl_rate,
        max_hold_days=max_hold,
        message="hold",
    )
