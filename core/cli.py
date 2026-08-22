from __future__ import annotations

import argparse
import json
from types import SimpleNamespace

from . import Certifier, StrategyAdapter, StrategyMetadata, default_catalog


class _DemoStrategy(StrategyAdapter):
    metadata = StrategyMetadata("demo", "medium", "1D", 20, 5, ("synthetic",))

    def calculate_signals(self, handoff):
        return [0] * len(handoff.stream)

    def backtest(self, handoff):
        return {"returns": [0.1, -0.02, 0.03, 0.01]}


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
    parser.add_argument("command", choices=("catalog", "demo"))
    args = parser.parse_args(argv)
    catalog = default_catalog()
    if args.command == "catalog":
        for definition in catalog.as_dict().values():
            print(f"{definition.id}\t{definition.category}\t{definition.name}")
        return 0
    report = Certifier(catalog).certify(
        _DemoStrategy(), _demo_handoff(), list(catalog.as_dict())
    )
    print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
    return 0 if report.status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
