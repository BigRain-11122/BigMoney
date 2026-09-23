from config import HoldPeriodConfig
from core import PositionState, DailyEvaluator, CloseCommand, ExitReason


def make_pos(price, hold, sym, cost=100.0):
    return PositionState(symbol=sym, strategy_id="s",
                         cost_price=cost, current_price=price,
                         hold_days=hold, quantity=100.0)


def test_evaluator_returns_close_commands():
    cfg = HoldPeriodConfig()
    ev = DailyEvaluator(cfg)
    positions = {
        "LOSS8": make_pos(99.0, 8, "LOSS8"),
        "PROFIT14": make_pos(110.0, 14, "PROFIT14"),
        "STOP": make_pos(90.0, 1, "STOP"),
    }
    cmds = ev.evaluate(positions)
    reasons = {c.symbol: c.reason for c in cmds}
    assert reasons["LOSS8"] == ExitReason.DYNAMIC_TIME_EXIT
    assert reasons["STOP"] == ExitReason.INDIVIDUAL_STOP_LOSS
    assert "PROFIT14" not in reasons


def test_evaluator_run_executes_and_removes():
    cfg = HoldPeriodConfig()
    ev = DailyEvaluator(cfg)
    positions = {"A": make_pos(90.0, 1, "A")}
    executed = []

    def exec_(cmd: CloseCommand):
        executed.append(cmd.symbol)

    ev.run(positions, exec_)
    assert executed == ["A"]


def test_advance_bar_increments_hold_days():
    cfg = HoldPeriodConfig()
    ev = DailyEvaluator(cfg)
    positions = {"A": make_pos(100.0, 0, "A")}
    ev.advance_bar(positions)
    assert positions["A"].hold_days == 1
