from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PositionState:
    """A single live/backtest position snapshot used by the top-level rules.

    Backtest and live adapters MUST fill these fields identically so the
    evaluator behaves the same on both sides.
    """

    symbol: str
    strategy_id: str
    cost_price: float
    current_price: float
    hold_days: int = 0          # number of daily bars already held (incremented at close)
    entry_date: str = ""        # YYYY-MM-DD, informational
    quantity: float = 0.0
    # Free-form tags for downstream attribution (strategy params, batch id, etc.)
    meta: dict = field(default_factory=dict)

    @property
    def pnl_rate(self) -> float:
        if self.cost_price <= 0:
            return 0.0
        return (self.current_price - self.cost_price) / self.cost_price

    @property
    def market_value(self) -> float:
        return self.current_price * self.quantity

    @property
    def floating_pnl(self) -> float:
        return (self.current_price - self.cost_price) * self.quantity
