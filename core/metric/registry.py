from __future__ import annotations

from .adapter import MetricAdapter


class MetricRegistry:
    """Explicit registry for caller-owned metrics."""

    def __init__(self) -> None:
        self._metrics: dict[str, MetricAdapter] = {}

    def register(self, metric: MetricAdapter) -> None:
        if not isinstance(metric, MetricAdapter):
            raise TypeError("metric must implement MetricAdapter")
        name = metric.metadata.name
        if name in self._metrics:
            raise ValueError(f"duplicate metric name: {name}")
        self._metrics[name] = metric

    def get(self, name: str) -> MetricAdapter:
        try:
            return self._metrics[name]
        except KeyError:
            raise KeyError(f"unknown metric name: {name}") from None

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._metrics))
