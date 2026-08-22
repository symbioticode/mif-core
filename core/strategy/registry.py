from __future__ import annotations

from .adapter import StrategyAdapter


class StrategyRegistry:
    """Explicit in-process registry; it performs no discovery or imports."""

    def __init__(self) -> None:
        self._strategies: dict[str, StrategyAdapter] = {}

    def register(self, strategy: StrategyAdapter) -> None:
        if not isinstance(strategy, StrategyAdapter):
            raise TypeError("strategy must implement StrategyAdapter")
        name = strategy.metadata.name
        if name in self._strategies:
            raise ValueError(f"duplicate strategy name: {name}")
        self._strategies[name] = strategy

    def get(self, name: str) -> StrategyAdapter:
        return self._strategies[name]

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._strategies))
