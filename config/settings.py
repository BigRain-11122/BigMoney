"""Central configuration. All nodes read this file."""
import os
from dataclasses import dataclass


@dataclass
class RedisConfig:
    # Master Tailscale IP, e.g. 100.x.x.x. Override via env QUANT_MASTER_TS_IP.
    host: str = os.environ.get("QUANT_MASTER_TS_IP", "127.0.0.1")
    port: int = int(os.environ.get("QUANT_REDIS_PORT", "6379"))
    db: int = 0
    backtest_queue: str = "backtest_queue"
    heartbeat_queue: str = "heartbeat_queue"


@dataclass
class PathConfig:
    root: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir: str = os.path.join(root, "data")
    daily_dir: str = os.path.join(data_dir, "daily")
    basic_dir: str = os.path.join(data_dir, "basic")
    results_dir: str = os.path.join(root, "results")
    logs_dir: str = os.path.join(root, "logs")


@dataclass
class RiskConfig:
    max_position_pct: float = 0.10       # single symbol
    max_total_pct: float = 0.80           # total exposure
    max_daily_trades: int = 10
    daily_loss_limit: float = -0.03      # stop opening new positions


@dataclass
class ScreenConfig:
    min_trades: int = 30
    max_drawdown_limit: float = 0.25
    min_sharpe: float = 1.2
    weights: dict = None

    def __post_init__(self):
        if self.weights is None:
            self.weights = {
                "annual_return": 0.40,
                "sharpe": 0.30,
                "max_drawdown": 0.20,
                "win_rate": 0.10,
            }


REDIS = RedisConfig()
PATHS = PathConfig()
RISK = RiskConfig()
SCREEN = ScreenConfig()
