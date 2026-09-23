"""Enhanced exit rules: layered take-profit, trailing stop, time decay.

Priority chain (first hit wins):
  P1. signal reversal      -> close all immediately
  P2. stop loss            -> initial -8%, then trailing after +5%
  P3. layered take-profit  -> 5% / 10% / 20% tiers, scale out
  P4. time decay           -> hold N periods, return < threshold -> close
  P5. global hard limit    -> forced close at max days
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ExitConfig:
    # Layered take-profit: each level triggers a partial exit.
    # Profit levels, fractions to sell at each level.
    take_profit_levels: tuple = (0.05, 0.10, 0.20)
    take_profit_fractions: tuple = (1/3, 1/3, 1.0)  # 1/3, then 1/3 of remaining, then all

    # Trailing stop: once profit >= activate, stop moves to cost + lock_pct
    trailing_activate: float = 0.05
    trailing_lock: float = 0.01

    # Initial hard stop (before trailing activates)
    initial_stop: float = -0.08

    # Time decay
    time_decay_period: int = 20
    time_decay_threshold: float = 0.02

    # Global hard ceiling
    global_hard_limit: int = 15


@dataclass
class ExitState:
    """Per-position state. Carried across bars."""
    cost_price: float
    hold_days: int = 0
    tier_reached: int = 0           # how many take-profit tiers already hit
    trailing_stop_price: float = 0.0  # 0 = not yet activated


@dataclass
class ExitAction:
    should_close: bool
    close_fraction: float          # 1.0 = full close, 0.333 = partial
    reason: str
    stop_price: float              # updated stop level (for logging)
    pnl_rate: float
    hold_days: int


def evaluate(state: ExitState,
             current_price: float,
             cfg: ExitConfig,
             signal_reversed: bool = False) -> ExitAction:
    """Evaluate exit rules for one position.

    Returns ExitAction. Caller applies the partial fraction and updates
    ExitState.tier_reached / trailing_stop_price accordingly.
    """
    if state.cost_price <= 0:
        return ExitAction(False, 0.0, "invalid_cost", 0.0, 0.0, 0)

    pnl = (current_price - state.cost_price) / state.cost_price
    stop = 0.0

    # P1: signal reversal -> close all, no questions asked
    if signal_reversed:
        return ExitAction(True, 1.0, "signal_reversal",
                          state.trailing_stop_price, pnl, state.hold_days)

    # P2: stop loss
    # 2a. trailing stop active?
    if pnl >= cfg.trailing_activate and state.trailing_stop_price <= 0:
        state.trailing_stop_price = state.cost_price * (1 + cfg.trailing_lock)
    stop = state.trailing_stop_price if state.trailing_stop_price > 0 \
        else state.cost_price * (1 + cfg.initial_stop)

    if current_price <= stop:
        return ExitAction(True, 1.0, "stop_loss", stop, pnl, state.hold_days)

    # P3: layered take-profit
    if state.tier_reached < len(cfg.take_profit_levels):
        threshold = cfg.take_profit_levels[state.tier_reached]
        if pnl >= threshold:
            frac = cfg.take_profit_fractions[state.tier_reached]
            reason = f"take_profit_tier_{state.tier_reached + 1}"
            return ExitAction(True, frac, reason, stop, pnl, state.hold_days)

    # P4: time decay
    if state.hold_days >= cfg.time_decay_period and pnl < cfg.time_decay_threshold:
        return ExitAction(True, 1.0, "time_decay", stop, pnl, state.hold_days)

    # P5: global hard limit
    if state.hold_days >= cfg.global_hard_limit:
        return ExitAction(True, 1.0, "global_hard_limit", stop, pnl, state.hold_days)

    return ExitAction(False, 0.0, "hold", stop, pnl, state.hold_days)


def apply_action(state: ExitState, action: ExitAction,
                 current_quantity: float) -> tuple:
    """Apply action to a position. Returns (new_quantity, new_state).

    Full close -> caller removes position.
    Partial close -> caller reduces quantity; tier_reached increments.
    """
    if not action.should_close:
        return current_quantity, state

    if action.close_fraction >= 1.0:
        return 0.0, state

    # partial close: consume one tier
    qty = current_quantity * (1 - action.close_fraction)
    new_state = ExitState(
        cost_price=state.cost_price,
        hold_days=state.hold_days,
        tier_reached=state.tier_reached + 1,
        trailing_stop_price=state.trailing_stop_price,
    )
    return qty, new_state
