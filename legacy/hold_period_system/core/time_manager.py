from .enums import ExitReason, PnlState
from .position_state import PositionState
from config import HoldPeriodConfig


def classify_pnl(state: PositionState) -> PnlState:
    r = state.pnl_rate
    if r < 0:
        return PnlState.LOSS
    if r > 0:
        return PnlState.PROFIT
    return PnlState.FLAT


def dynamic_max_hold_days(state: PositionState, cfg: HoldPeriodConfig) -> int:
    """Return the dynamic max hold days given current PnL state.

    Loss side is strictly capped at cfg.max_hold_days_loss.
    Profit side is allowed up to cfg.max_hold_days_profit.
    Both are bounded by cfg.global_hard_limit_days (defensive).
    """
    pnl = classify_pnl(state)
    if pnl == PnlState.LOSS:
        m = cfg.max_hold_days_loss
    else:
        m = cfg.max_hold_days_profit
    return min(m, cfg.global_hard_limit_days)
