from enum import Enum


class ExitReason(str, Enum):
    """Closed-enum exit reasons. String values are stable for logging / analysis."""

    MARKET_CIRCUIT_BREAK = "market_circuit_break"
    INDIVIDUAL_STOP_LOSS = "individual_stop_loss"
    DYNAMIC_TIME_EXIT = "dynamic_time_exit"
    GLOBAL_HARD_LIMIT = "global_hard_limit"
    HOLD = "hold"


class PnlState(str, Enum):
    LOSS = "loss"
    FLAT = "flat"
    PROFIT = "profit"
