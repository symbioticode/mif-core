from __future__ import annotations

from .adapter import MetricAdapter


class MetricRegistry:
    """Explicit registry for caller-owned metrics."""

    def __init__(self) -> None:
        self._metrics: dict[str, MetricAdapter] = {}

    def register(self, metric: MetricAdapter) -> None:
        name = metric.metadata.name
        if name in self._metrics:
            raise ValueError(f"duplicate metric name: {name}")
        self._metrics[name] = metric

    def get(self, name: str) -> MetricAdapter:
        return self._metrics[name]

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._metrics))

