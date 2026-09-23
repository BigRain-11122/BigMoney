"""Default parameters for the top-level holding-period iron rules.

All values are numeric and machine-executable. Tuning engine can sweep
these fields directly.
"""
from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class HoldPeriodConfig:
    # Global hard ceiling (do not exceed under any strategy / any PnL)
    global_hard_limit_days: int = 15

    # Dynamic max hold days split by PnL state
    max_hold_days_loss: int = 8      # floating loss  -> forced exit at day 8
    max_hold_days_profit: int = 15   # floating profit -> allow up to global ceiling

    # Individual stop loss (priority above time rules)
    stop_loss_rate: float = -0.08    # -8%

    # Market-wide circuit breaker (top priority)
    market_circuit_break: bool = False  # set externally by market monitor

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "HoldPeriodConfig":
        base = cls()
        merged = {**asdict(base), **(d or {})}
        return cls(**merged)
