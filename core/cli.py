from __future__ import annotations

import argparse
import json
from types import SimpleNamespace

from . import (
    Certifier,
    MetricAdapter,
    MetricCertifier,
    MetricMetadata,
    StrategyAdapter,
    StrategyMetadata,
    default_catalog,
)


class _DemoStrategy(StrategyAdapter):
    metadata = StrategyMetadata("demo", "medium", "1D", 20, 5, ("synthetic",))

    def calculate_signals(self, handoff):
        return [0] * len(handoff.stream)

    def backtest(self, handoff):
        return {"returns": [0.1, -0.02, 0.03, 0.01]}


class _DemoMetric(MetricAdapter):
    metadata = MetricMetadata("demo-mean", "performance", "scalar")

    def calculate(self, handoff):
        return sum(handoff.stream) / len(handoff.stream)


def _demo_handoff():
    return SimpleNamespace(
        stream=[1, 2, 3, 4], asset_id="DEMO", calendar="SYNTHETIC",
        assembly_hash="a" * 64, handoff_timestamp=object(), dal_version="demo",
        source_manifest=({"source": "synthetic"},), coverage="FULL",
        dqf_status="PASS", dqf_mpi=100.0, dqf_version="demo",
        dqf_report=object(), aqi=100.0,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="mif-core")
    parser.add_argument("command", choices=("catalog", "demo", "metric-demo"))
    parser.add_argument("--format", choices=("json", "text"), default="json")
    args = parser.parse_args(argv)
    catalog = default_catalog()
    if args.command == "catalog":
        for definition in catalog.as_dict().values():
            print(f"{definition.id}\t{definition.category}\t{definition.name}")
        return 0
    if args.command == "metric-demo":
        result = MetricCertifier().certify(_DemoMetric(), _demo_handoff())
        if args.format == "text":
            print(f"Metric: {result['metric_name']} v{result['metric_version']}")
            print(f"Status: {result['status']}")
            print("Validity: " + ", ".join(
                f"{key}={value}" for key, value in result["validity_domain"].items()
            ))
        else:
            print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    report = Certifier(catalog).certify(
        _DemoStrategy(), _demo_handoff(), list(catalog.as_dict())
    )
    if args.format == "text":
        print(report.to_text())
    else:
        print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
    return 0 if report.status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
