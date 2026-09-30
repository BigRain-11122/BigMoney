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


class RiskGateRejected(RuntimeError):
    """RW-7 (T-127): a gate rejection is an EXCEPTION, never a silent drop.

    Carries the offending order and the machine-checkable reason so a
    rejected batch cannot quietly shrink (audit D-20260930-05 face 7).
    """

    def __init__(self, order: "Order", reason: str):
        self.order = order
        self.reason = reason
        super().__init__(
            f"risk gate rejected {order.side} {order.symbol}: {reason}")


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
              portfolio_value: float,
              daily_pnl_pct: float | None = None,
              strict: bool = True) -> list[Order]:
        """Sole order-exit check (RW-7).

        strict=True (default): any violation raises RiskGateRejected --
        the caller must not let a partially-approved batch drift silently.
        strict=False: legacy filter behaviour, kept for read-only probes.
        """
        approved = []
        used_pct = sum(p.get("weight", 0) for p in current_positions.values())
        network_ok = self._network_allows_new_open()
        # circuit-breaker first: a halted day must not open anything new
        if daily_pnl_pct is not None and self.daily_loss_breaker(daily_pnl_pct):
            for o in orders:
                if o.side == "BUY":
                    if strict:
                        raise RiskGateRejected(
                            o, f"daily_loss_breaker halt "
                               f"(pnl {daily_pnl_pct:.2%} <= "
                               f"{RISK.daily_loss_limit:.2%})")
                    continue
                approved.append(o)
            return approved
        for o in orders:
            if o.side not in ("BUY", "SELL"):
                if strict:
                    raise RiskGateRejected(o, f"invalid side {o.side!r}")
                continue
            if self.orders_today >= RISK.max_daily_trades:
                if strict:
                    raise RiskGateRejected(
                        o, f"max_daily_trades {RISK.max_daily_trades} reached")
                continue
            if o.side == "BUY":
                if not network_ok:
                    if strict:
                        raise RiskGateRejected(
                            o, "network hotspot: new buys blocked")
                    continue
                if used_pct + o.target_weight > RISK.max_total_pct:
                    if strict:
                        raise RiskGateRejected(
                            o, f"total weight "
                               f"{used_pct + o.target_weight:.2f} > cap "
                               f"{RISK.max_total_pct}")
                    continue
                if o.target_weight > RISK.max_position_pct:
                    if strict:
                        raise RiskGateRejected(
                            o, f"position weight {o.target_weight:.2f} > cap "
                               f"{RISK.max_position_pct}")
                    continue
            approved.append(o)
            self.orders_today += 1
        return approved

    def daily_loss_breaker(self, daily_pnl_pct: float) -> bool:
        """Return True if trading should be halted today."""
        return daily_pnl_pct <= RISK.daily_loss_limit


def gate_orders(orders: list[Order], current_positions: dict,
                portfolio_value: float,
                daily_pnl_pct: float | None = None) -> list[Order]:
    """RW-7 sole order exit: every order leaving the system passes here."""
    return RiskGate().check(orders, current_positions, portfolio_value,
                            daily_pnl_pct=daily_pnl_pct)


def emit_order_sheet(orders: list[Order], date: str,
                     gate_receipt: list[Order] | None = None) -> str:
    """Sole order-sheet writer (RW-7): refuses ungated orders."""
    if gate_receipt is None or list(gate_receipt) != list(orders):
        raise RuntimeError(
            "emit_order_sheet: orders not gate-approved (RW-7 sole-exit); "
            "route through gate_orders() first")
    path = os.path.join(PATHS.logs_dir, f"orders_{date}.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["date", "symbol", "side", "target_weight", "reason", "price"])
        for o in orders:
            w.writerow([o.date, o.symbol, o.side, o.target_weight,
                        o.reason, o.price])
    return path
