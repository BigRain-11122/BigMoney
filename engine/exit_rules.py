"""Enhanced exit rules.

Priority:
  P1 signal_reversal -> close all
  P2 stop_loss       -> initial -8%, trailing after +5%, follows high
  P3 take_profit     -> tiered scale-out
  P4 time_decay      -> hold N periods, return < threshold
  P5 loss_time_stop  -> if losing and hold_days >= 8, force close
  P6 hard_limit      -> global ceiling
"""
from dataclasses import dataclass


@dataclass
class ExitConfig:
    take_profit_levels: tuple = (0.05, 0.10, 0.20)
    take_profit_fractions: tuple = (1/3, 1/3, 1.0)
    trailing_activate: float = 0.05
    trailing_lock: float = 0.01
    initial_stop: float = -0.08
    loss_time_days: int = 8            # NEW: losing position force-exit
    time_decay_period: int = 12        # was 20, now < hard_limit
    time_decay_threshold: float = 0.02
    global_hard_limit: int = 25        # was 15, was conflicting with decay
    position_size_pct: float = 0.10
    max_positions: int = 5


@dataclass
class ExitState:
    cost_price: float
    hold_days: int = 0
    tier_reached: int = 0
    trailing_stop_price: float = 0.0
    high_watermark: float = 0.0         # NEW: track max price since entry
    quantity: float = 0.0


@dataclass
class ExitAction:
    should_close: bool
    close_fraction: float
    reason: str
    stop_price: float
    pnl_rate: float


def evaluate(state: ExitState, current_price: float,
             cfg: ExitConfig, signal_reversed: bool = False) -> ExitAction:
    if state.cost_price <= 0:
        return ExitAction(False, 0.0, "invalid", 0.0, 0.0)

    pnl = (current_price - state.cost_price) / state.cost_price

    # track high watermark
    if current_price > state.high_watermark:
        state.high_watermark = current_price

    # P1: signal reversal
    if signal_reversed:
        return ExitAction(True, 1.0, "signal_reversal",
                          state.trailing_stop_price, pnl)

    # P2: stop loss
    # trailing activates once profit >= activate, then follows high - lock%
    if pnl >= cfg.trailing_activate:
        new_stop = state.high_watermark * (1 - cfg.trailing_lock)
        if new_stop > state.trailing_stop_price:
            state.trailing_stop_price = new_stop
    stop = state.trailing_stop_price if state.trailing_stop_price > 0 \
        else state.cost_price * (1 + cfg.initial_stop)

    if current_price <= stop:
        return ExitAction(True, 1.0, "stop_loss", stop, pnl)

    # P3: layered take-profit
    if state.tier_reached < len(cfg.take_profit_levels):
        th = cfg.take_profit_levels[state.tier_reached]
        if pnl >= th:
            frac = cfg.take_profit_fractions[state.tier_reached]
            return ExitAction(True, frac,
                              f"take_profit_tier_{state.tier_reached+1}",
                              stop, pnl)

    # P4: time decay (only when barely profitable)
    if state.hold_days >= cfg.time_decay_period and pnl < cfg.time_decay_threshold:
        return ExitAction(True, 1.0, "time_decay", stop, pnl)

    # P5: losing position time stop (your original iron rule)
    if pnl < 0 and state.hold_days >= cfg.loss_time_days:
        return ExitAction(True, 1.0, "loss_time_stop", stop, pnl)

    # P6: global hard limit
    if state.hold_days >= cfg.global_hard_limit:
        return ExitAction(True, 1.0, "global_hard_limit", stop, pnl)

    return ExitAction(False, 0.0, "hold", stop, pnl)
