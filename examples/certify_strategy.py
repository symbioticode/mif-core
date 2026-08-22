"""Minimal offline example of a caller-owned strategy."""

from types import SimpleNamespace

from core import Certifier, StrategyAdapter, StrategyMetadata, default_catalog


class ExampleStrategy(StrategyAdapter):
    metadata = StrategyMetadata(
        name="example-strategy",
        frequency="medium",
        optimal_timeframe="1D",
        min_trades_per_year=20,
        typical_holding_days=5,
        asset_classes=("synthetic",),
    )

    def calculate_signals(self, handoff):
        return [0] * len(handoff.stream)

    def backtest(self, handoff):
        return {"returns": [0.10, -0.02, 0.03, 0.01]}


handoff = SimpleNamespace(
    stream=[1, 2, 3, 4],
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

report = Certifier(default_catalog()).certify(
    ExampleStrategy(), handoff, ["T_HANDOFF_001", "T_SIGNAL_SHAPE_001", "T_STABILITY_001"]
)
print(report.to_dict())
