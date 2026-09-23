"""Live trading adapter: same rules, wired to a broker-style interface.

The broker interface is abstracted via two callbacks:
    - price_provider(symbol) -> float (current mark price)
    - close_executor(cmd) -> None    (send real close order)
    - positions_provider() -> Dict[str, PositionState]

The adapter NEVER decides position sizing or entries; it only enforces the
top-level holding-period iron rules on whatever positions the live strategies
currently hold.
"""
from typing import Callable, Dict, Optional

from core import CloseCommand, DailyEvaluator, PositionState
from config import HoldPeriodConfig


class LiveHoldingGuard:
    def __init__(
        self,
        cfg: Optional[HoldPeriodConfig] = None,
        positions_provider: Optional[Callable[[], Dict[str, PositionState]]] = None,
        close_executor: Optional[Callable[[CloseCommand], None]] = None,
    ):
        self.cfg = cfg or HoldPeriodConfig()
        self.evaluator = DailyEvaluator(self.cfg)
        self._positions_provider = positions_provider
        self._close_executor = close_executor

    def set_providers(
        self,
        positions_provider: Callable[[], Dict[str, PositionState]],
        close_executor: Callable[[CloseCommand], None],
    ) -> None:
        self._positions_provider = positions_provider
        self._close_executor = close_executor

    def on_daily_close(self, market_circuit_break: bool = False) -> list:
        """Call once per trading day at market close.

        Returns the list of CloseCommand that were executed.
        The positions_provider MUST return positions with current_price already
        updated to today's close and hold_days already incremented by the
        strategy's own lifecycle (or via evaluator.advance_bar).
        """
        assert self._positions_provider is not None, "positions_provider not set"
        assert self._close_executor is not None, "close_executor not set"
        positions = self._positions_provider()
        return self.evaluator.run(
            positions,
            self._close_executor,
            market_circuit_break=market_circuit_break,
        )

    def advance_bar(self, positions: Dict[str, PositionState]) -> None:
        """Convenience: called by the strategy lifecycle after close."""
        self.evaluator.advance_bar(positions)
