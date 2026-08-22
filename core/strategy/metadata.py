from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True)
class StrategyMetadata:
    """Explicit strategy description used to select appropriate tests."""

    name: str
    frequency: str
    optimal_timeframe: str
    min_trades_per_year: int
    typical_holding_days: int
    asset_classes: Tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.frequency not in {"high", "medium", "low"}:
            raise ValueError("frequency must be high, medium, or low")
        if self.min_trades_per_year < 0 or self.typical_holding_days < 0:
            raise ValueError("trade and holding-day counts cannot be negative")

