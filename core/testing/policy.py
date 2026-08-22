from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CriteriaPolicy:
    """Explicit, validated thresholds used by adaptive built-in tests."""

    low_frequency_positive_rate: float = 0.60
    default_positive_rate: float = 0.50
    out_of_sample_positive_rate: float = 0.50

    def __post_init__(self) -> None:
        for name in (
            "low_frequency_positive_rate",
            "default_positive_rate",
            "out_of_sample_positive_rate",
        ):
            value = getattr(self, name)
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be in [0, 1]")

    def positive_rate_for(self, frequency: str) -> float:
        return (
            self.low_frequency_positive_rate
            if frequency == "low"
            else self.default_positive_rate
        )

