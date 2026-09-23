from config import HoldPeriodConfig
from core import PositionState, evaluate_position, ExitReason


def mk(price, hold, cost=100.0):
    return PositionState(symbol="X", strategy_id="s",
                         cost_price=cost, current_price=price,
                         hold_days=hold, quantity=100.0)


def test_priority1_market_circuit_break_wins_even_if_profitable():
    cfg = HoldPeriodConfig()
    d = evaluate_position(mk(150.0, hold=2), cfg, market_circuit_break=True)
    assert d.reason == ExitReason.MARKET_CIRCUIT_BREAK
    assert d.should_close


def test_priority2_stop_loss_beats_time():
    cfg = HoldPeriodConfig()
    # day 1, pnl = -9% -> stop loss fires even though hold_days < 8
    d = evaluate_position(mk(91.0, hold=1), cfg)
    assert d.reason == ExitReason.INDIVIDUAL_STOP_LOSS
    assert d.should_close


def test_priority2_stop_loss_boundary_is_inclusive():
    cfg = HoldPeriodConfig(stop_loss_rate=-0.08)
    d = evaluate_position(mk(92.0, hold=1), cfg)  # exactly -8%
    assert d.reason == ExitReason.INDIVIDUAL_STOP_LOSS


def test_priority3_loss_side_forced_exit_at_day8():
    cfg = HoldPeriodConfig()
    d = evaluate_position(mk(99.0, hold=8), cfg)  # small loss, day 8
    assert d.reason == ExitReason.DYNAMIC_TIME_EXIT
    d7 = evaluate_position(mk(99.0, hold=7), cfg)
    assert d7.reason == ExitReason.HOLD


def test_priority3_profit_side_allowed_to_day15():
    cfg = HoldPeriodConfig()
    d14 = evaluate_position(mk(110.0, hold=14), cfg)
    assert d14.reason == ExitReason.HOLD
    d15 = evaluate_position(mk(110.0, hold=15), cfg)
    assert d15.reason in (ExitReason.DYNAMIC_TIME_EXIT, ExitReason.GLOBAL_HARD_LIMIT)


def test_priority4_global_hard_limit_fallback():
    cfg = HoldPeriodConfig(global_hard_limit_days=15,
                           max_hold_days_loss=8,
                           max_hold_days_profit=15)
    # If profit-side max == global ceiling, day 15 may fire either reason;
    # both must close. Verify close happens regardless.
    d = evaluate_position(mk(105.0, hold=15), cfg)
    assert d.should_close


def test_profitable_position_holds_through_early_days():
    cfg = HoldPeriodConfig()
    for h in range(0, 15):
        d = evaluate_position(mk(105.0, hold=h), cfg)
        assert d.reason == ExitReason.HOLD, f"day {h} should hold"
