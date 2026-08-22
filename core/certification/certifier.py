from typing import Any

from ..strategy import StrategyAdapter
from ..testing import TestCatalog
from ..testing import TestResult
from ..integrations.dal import validate_dal_handoff
from .report import CertificationReport
from .tiers import calculate_tier


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
            try:
                result = definition.execute(strategy=strategy, handoff=handoff)
            except Exception as exc:
                result = {"passed": False, "value": None, "details": {"error": str(exc)}}
            normalized = TestResult(
                test_id=test_id,
                test_name=definition.name,
                category=definition.category,
                passed=result.get("passed", False) is True,
                value=result.get("value"),
                details=result.get("details", {}),
                threshold=result.get("threshold"),
            )
            results[test_id] = normalized.to_dict()
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
            tier=calculate_tier(results),
        )
