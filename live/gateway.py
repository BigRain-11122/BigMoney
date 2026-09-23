"""Live trading gateway.

Daily close:
  1. load top strategies from results/ranking.csv
  2. compute target weights from latest price + strategy params
  3. run risk checks
  4. emit order sheet (CSV) -> paper trading first
"""
import csv
import os
import sys
from dataclasses import dataclass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import PATHS, RISK


@dataclass
class Order:
    date: str
    symbol: str
    side: str            # BUY / SELL
    target_weight: float
    reason: str
    price: float = 0.0


class RiskGate:
    def __init__(self):
        self.orders_today = 0

    @staticmethod
    def _network_allows_new_open() -> bool:
        """Block new buys on HOTSPOT to avoid surprise data/order traffic."""
        try:
            from network_detector import read_status
            st = read_status()
            return not st.get("hotspot", False)
        except Exception:
            return True

    def check(self, orders: list[Order],
              current_positions: dict,
              portfolio_value: float) -> list[Order]:
        approved = []
        used_pct = sum(p.get("weight", 0) for p in current_positions.values())
        network_ok = self._network_allows_new_open()
        for o in orders:
            if self.orders_today >= RISK.max_daily_trades:
                continue
            if o.side == "BUY":
                if not network_ok:
                    continue
                if used_pct + o.target_weight > RISK.max_total_pct:
                    continue
                if o.target_weight > RISK.max_position_pct:
                    continue
            approved.append(o)
            self.orders_today += 1
        return approved

    def daily_loss_breaker(self, daily_pnl_pct: float) -> bool:
        """Return True if trading should be halted today."""
        return daily_pnl_pct <= RISK.daily_loss_limit


def emit_order_sheet(orders: list[Order], date: str) -> str:
    path = os.path.join(PATHS.logs_dir, f"orders_{date}.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["date", "symbol", "side", "target_weight", "reason", "price"])
        for o in orders:
            w.writerow([o.date, o.symbol, o.side, o.target_weight,
                         o.reason, o.price])
    return path
