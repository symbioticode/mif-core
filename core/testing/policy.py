from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CriteriaPolicy:
    """Explicit, validated thresholds used by adaptive built-in tests."""

    low_frequency_positive_rate: float = 0.60
    default_positive_rate: float = 0.50
    out_of_sample_positive_rate: float = 0.50
    walk_forward_test_fraction: float = 0.50
    walk_forward_min_test_observations: int = 2
    walk_forward_train_observations: int = 2
    walk_forward_step: int = 1

    def __post_init__(self) -> None:
        for name in (
            "low_frequency_positive_rate",
            "default_positive_rate",
            "out_of_sample_positive_rate",
        ):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeError(f"{name} must be numeric")
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be in [0, 1]")
        if isinstance(self.walk_forward_test_fraction, bool) or not isinstance(
            self.walk_forward_test_fraction, (int, float)
        ):
            raise TypeError("walk_forward_test_fraction must be numeric")
        if not 0.0 < self.walk_forward_test_fraction < 1.0:
            raise ValueError("walk_forward_test_fraction must be between 0 and 1")
        if isinstance(self.walk_forward_min_test_observations, bool) or not isinstance(
            self.walk_forward_min_test_observations, int
        ):
            raise TypeError("walk_forward_min_test_observations must be an integer")
        if self.walk_forward_min_test_observations < 1:
            raise ValueError("walk_forward_min_test_observations must be >= 1")
        if (
            isinstance(self.walk_forward_train_observations, bool)
            or not isinstance(self.walk_forward_train_observations, int)
            or isinstance(self.walk_forward_step, bool)
            or not isinstance(self.walk_forward_step, int)
        ):
            raise TypeError("walk-forward observations and step must be integers")
        if self.walk_forward_train_observations < 1 or self.walk_forward_step < 1:
            raise ValueError("walk-forward train observations and step must be >= 1")

    def positive_rate_for(self, frequency: str) -> float:
        return (
            self.low_frequency_positive_rate
            if frequency == "low"
            else self.default_positive_rate
        )
