from typing import Any

from ..strategy import StrategyAdapter
from ..testing import TestCatalog
from ..integrations.dal import validate_dal_handoff
from .report import CertificationReport


class Certifier:
    """Runs explicitly selected tests; it does not silently choose a protocol."""

    def __init__(self, catalog: TestCatalog) -> None:
        self.catalog = catalog

    def certify(self, strategy: StrategyAdapter, handoff: Any, test_ids: list[str]) -> CertificationReport:
        validate_dal_handoff(handoff)
        if not test_ids:
            raise ValueError("at least one test must be selected")
        results: dict[str, dict[str, Any]] = {}
        for test_id in test_ids:
            definition = self.catalog.get(test_id)
            results[test_id] = definition.execute(strategy=strategy, handoff=handoff)
        status = "PASS" if all(item.get("passed", False) for item in results.values()) else "FAIL"
        return CertificationReport(
            strategy_name=strategy.metadata.name,
            tests_run=results,
            status=status,
            validity_domain={
                "asset_scope": handoff.asset_id,
                "calendar": handoff.calendar,
                "coverage": handoff.coverage,
                "dqf_status": handoff.dqf_status,
                "assembly_hash": handoff.assembly_hash,
            },
        )
