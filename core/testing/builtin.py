from __future__ import annotations

from typing import Any

from .catalog import TestCatalog, TestDefinition


def _handoff_ready(*, handoff: Any, **_: Any) -> dict[str, Any]:
    """CORE gate: the DAL boundary has already been structurally validated."""
    return {
        "passed": True,
        "value": handoff.dqf_status,
        "details": {
            "asset_id": handoff.asset_id,
            "assembly_hash": handoff.assembly_hash,
            "dqf_status": handoff.dqf_status,
        },
    }


def _signals_shape(*, strategy: Any, handoff: Any) -> dict[str, Any]:
    """Check that a strategy emits one signal per input observation."""
    try:
        signals = strategy.calculate_signals(handoff)
        observations = len(handoff.stream)
        signal_count = len(signals)
    except Exception as exc:  # the result must explain strategy failures
        return {"passed": False, "value": None, "details": {"error": str(exc)}}
    passed = signal_count == observations
    return {
        "passed": passed,
        "value": signal_count,
        "details": {
            "signal_count": signal_count,
            "observation_count": observations,
            "reason": "one signal per observation" if passed else "length mismatch",
        },
    }


def default_catalog() -> TestCatalog:
    """Return the small, offline catalogue shipped with the first release."""
    catalog = TestCatalog()
    catalog.register(TestDefinition(
        "T_HANDOFF_001", "DAL handoff readiness", "integration", _handoff_ready
    ))
    catalog.register(TestDefinition(
        "T_SIGNAL_SHAPE_001", "Signal shape", "strategy", _signals_shape
    ))
    return catalog

