from dataclasses import dataclass


@dataclass(frozen=True)
class MetricMetadata:
    """Explicit description of a metric's output and intended domain."""

    name: str
    domain: str
    output_kind: str
    version: str = "0.1.0"

    def __post_init__(self) -> None:
        if not all(
            isinstance(value, str) and value
            for value in (self.name, self.domain, self.version)
        ):
            raise ValueError("metric name, domain, and version are required")
        if self.output_kind not in {"series", "scalar", "signal"}:
            raise ValueError("output_kind must be series, scalar, or signal")
