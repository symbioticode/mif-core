"""Minimal offline example of metric output certification."""

from types import SimpleNamespace

from core import MetricAdapter, MetricCertifier, MetricMetadata


class MeanReturn(MetricAdapter):
    metadata = MetricMetadata("mean-return", "performance", "scalar")

    def calculate(self, handoff):
        values = handoff.stream
        return sum(values) / len(values)


handoff = SimpleNamespace(
    stream=[1.0, 1.1, 1.2],
    asset_id="DEMO",
    calendar="SYNTHETIC",
    assembly_hash="a" * 64,
    handoff_timestamp=object(),
    dal_version="demo",
    source_manifest=({"source": "synthetic"},),
    coverage="FULL",
    dqf_status="PASS",
    dqf_mpi=100.0,
    dqf_version="demo",
    dqf_report=object(),
    aqi=100.0,
)

print(MetricCertifier().certify(MeanReturn(), handoff))
