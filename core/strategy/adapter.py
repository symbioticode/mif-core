from abc import ABC, abstractmethod
from typing import Any

from .metadata import StrategyMetadata


class StrategyAdapter(ABC):
    """Minimal strategy boundary consumed by the certification engine."""

    metadata: StrategyMetadata

    @abstractmethod
    def calculate_signals(self, handoff: Any) -> Any:
        """Calculate signals from one certified DAL handoff."""

    @abstractmethod
    def backtest(self, handoff: Any) -> Any:
        """Run a deterministic backtest against one certified handoff."""

