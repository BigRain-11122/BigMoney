from config import HoldPeriodConfig
from core import (
    PositionState,
    classify_pnl,
    dynamic_max_hold_days,
    evaluate_position,
    ExitReason,
)


def pos(price, cost=100.0, hold=0, qty=100.0, sym="A", sid="s1"):
    return PositionState(
        symbol=sym, strategy_id=sid,
        cost_price=cost, current_price=price,
        hold_days=hold, quantity=qty,
    )


def test_pnl_classification():
    from core.enums import PnlState
    assert classify_pnl(pos(99.0)) == PnlState.LOSS
    assert classify_pnl(pos(101.0)) == PnlState.PROFIT
    assert classify_pnl(pos(100.0)) == PnlState.FLAT


def test_dynamic_max_hold_loss_uses_loss_bucket():
    cfg = HoldPeriodConfig()
    p = pos(99.0)  # pnl < 0
    assert dynamic_max_hold_days(p, cfg) == cfg.max_hold_days_loss


def test_dynamic_max_hold_profit_uses_profit_bucket():
    cfg = HoldPeriodConfig()
    p = pos(101.0)
    assert dynamic_max_hold_days(p, cfg) == cfg.max_hold_days_profit


def test_dynamic_max_hold_is_capped_by_global_limit():
    cfg = HoldPeriodConfig(global_hard_limit_days=10,
                           max_hold_days_profit=15)
    p = pos(101.0)
    assert dynamic_max_hold_days(p, cfg) == 10
