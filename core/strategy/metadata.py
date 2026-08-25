from dataclasses import dataclass, field


@dataclass(frozen=True)
class StrategyMetadata:
    """Explicit strategy description used to select appropriate tests."""

    name: str
    frequency: str
    optimal_timeframe: str
    min_trades_per_year: int
    typical_holding_days: int
    asset_classes: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not all(
            isinstance(value, str)
            for value in (self.name, self.frequency, self.optimal_timeframe)
        ):
            raise TypeError("strategy identity fields must be strings")
        if not all((self.name, self.frequency, self.optimal_timeframe)):
            raise ValueError("strategy identity fields must be non-empty strings")
        if self.frequency not in {"high", "medium", "low"}:
            raise ValueError("frequency must be high, medium, or low")
        if (
            isinstance(self.min_trades_per_year, bool)
            or not isinstance(self.min_trades_per_year, int)
            or isinstance(self.typical_holding_days, bool)
            or not isinstance(self.typical_holding_days, int)
        ):
            raise TypeError("trade and holding-day counts must be integers")
        if self.min_trades_per_year < 0 or self.typical_holding_days < 0:
            raise ValueError("trade and holding-day counts cannot be negative")
        if not isinstance(self.asset_classes, tuple) or not all(
            isinstance(asset, str) for asset in self.asset_classes
        ):
            raise TypeError("asset_classes must be a tuple of strings")
        if not all(self.asset_classes):
            raise ValueError("asset_classes entries must be non-empty")
