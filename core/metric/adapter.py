from abc import ABC, abstractmethod
from typing import Any

from .metadata import MetricMetadata


class MetricAdapter(ABC):
    """Boundary for a metric evaluated against one certified DAL handoff."""

    metadata: MetricMetadata

    @abstractmethod
    def calculate(self, handoff: Any) -> Any:
        """Calculate the metric without fetching or repairing data."""
