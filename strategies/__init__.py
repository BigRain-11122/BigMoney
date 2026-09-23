"""Strategy schools registry.

Each school is a module. Functions return either:
  - pd.Series: position signal (0/1) for a single symbol
  - pd.DataFrame: weights (0/1) across the panel
"""
from . import trend
from . import mean_reversion
from . import momentum
from . import volatility
from . import sentiment
from . import seasonal
from . import macro
from . import event

__all__ = [
    "trend", "mean_reversion", "momentum", "volatility",
    "sentiment", "seasonal", "macro", "event",
]
