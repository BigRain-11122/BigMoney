"""Live trading demo: wire the guard to your broker callbacks."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adapters import LiveHoldingGuard
from config import HoldPeriodConfig
from core import PositionState, CloseCommand


# --- Inject these from your real strategy / broker ---------------------------
def my_positions_provider():
    return {
        "000001.SZ": PositionState(
            symbol="000001.SZ", strategy_id="ma_cross",
            cost_price=12.50, current_price=12.10,
            hold_days=3, quantity=1000,
        ),
        "600519.SH": PositionState(
            symbol="600519.SH", strategy_id="breakout",
            cost_price=1700.0, current_price=1780.0,
            hold_days=14, quantity=10,
        ),
    }


def my_close_executor(cmd: CloseCommand):
    # Replace with: broker.place_order(side=SELL, symbol=cmd.symbol, qty=cmd.quantity)
    print(f"[LIVE] SELL {cmd.symbol} qty={cmd.quantity} "
          f"px={cmd.current_price} reason={cmd.reason.value}")
# -----------------------------------------------------------------------------


def main():
    guard = LiveHoldingGuard(cfg=HoldPeriodConfig())
    guard.set_providers(my_positions_provider, my_close_executor)

    # Call once at every trading day close
    executed = guard.on_daily_close(market_circuit_break=False)
    for c in executed:
        print(f"closed {c.symbol} reason={c.reason.value} pnl={c.pnl_rate:.2%}")


if __name__ == "__main__":
    main()
