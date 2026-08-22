from __future__ import annotations

import copy
from dataclasses import is_dataclass, replace
import math
from typing import Any

from .catalog import TestCatalog, TestDefinition
from .policy import CriteriaPolicy


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


def _adaptive_stability(*, strategy: Any, handoff: Any, policy: CriteriaPolicy) -> dict[str, Any]:
    """Check positive-return rate with frequency-aware thresholds.

    Low-frequency strategies use a more conservative minimum sample-independent
    threshold because absolute degradation is not meaningful with few trades.
    The backtest contract is deliberately small: ``{"returns": iterable}``.
    """
    try:
        result = strategy.backtest(handoff)
        returns = list(result["returns"])
    except Exception as exc:
        return {"passed": False, "value": None, "details": {"error": str(exc)}}
    if not returns:
        return {"passed": False, "value": 0.0, "details": {"reason": "no returns"}}
    positive_rate = sum(value > 0 for value in returns) / len(returns)
    threshold = policy.positive_rate_for(strategy.metadata.frequency)
    return {
        "passed": positive_rate >= threshold,
        "value": positive_rate,
        "threshold": threshold,
        "details": {
            "positive_observations": sum(value > 0 for value in returns),
            "observations": len(returns),
            "frequency": strategy.metadata.frequency,
        },
    }


def _return_integrity(*, strategy: Any, handoff: Any) -> dict[str, Any]:
    """Reject missing, non-numeric, NaN, or infinite backtest returns."""
    try:
        returns = list(strategy.backtest(handoff)["returns"])
    except Exception as exc:
        return {"passed": False, "value": None, "details": {"error": str(exc)}}
    invalid: list[dict[str, object]] = []
    for index, value in enumerate(returns):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            invalid.append({"index": index, "value": repr(value), "reason": "not numeric"})
        elif not math.isfinite(value):
            invalid.append({"index": index, "value": repr(value), "reason": "not finite"})
    return {
        "passed": bool(returns) and not invalid,
        "value": len(returns),
        "details": {"observations": len(returns), "invalid": invalid},
    }


def _walk_forward_consistency(*, strategy: Any, handoff: Any, policy: CriteriaPolicy) -> dict[str, Any]:
    """Check that the out-of-sample half retains a non-negative hit rate."""
    try:
        returns = list(strategy.backtest(handoff)["returns"])
    except Exception as exc:
        return {"passed": False, "value": None, "details": {"error": str(exc)}}
    split = len(returns) // 2
    test_returns = returns[split:]
    if not test_returns:
        return {"passed": False, "value": 0.0, "details": {"reason": "no out-of-sample observations"}}
    positive_rate = sum(value > 0 for value in test_returns) / len(test_returns)
    return {
        "passed": positive_rate >= policy.out_of_sample_positive_rate,
        "value": positive_rate,
        "threshold": policy.out_of_sample_positive_rate,
        "details": {
            "train_observations": split,
            "test_observations": len(test_returns),
            "positive_test_observations": sum(value > 0 for value in test_returns),
        },
    }


def _no_lookahead(*, strategy: Any, handoff: Any) -> dict[str, Any]:
    """Check that a prefix produces the same signals as the full run prefix."""
    try:
        stream = handoff.stream
        midpoint = max(1, len(stream) // 2)
        if is_dataclass(handoff):
            prefix_handoff = replace(handoff, stream=stream[:midpoint])
        else:
            prefix_handoff = copy.copy(handoff)
            prefix_handoff.stream = stream[:midpoint]
        full_signals = list(strategy.calculate_signals(handoff))
        prefix_signals = list(strategy.calculate_signals(prefix_handoff))
        expected = full_signals[:midpoint]
        passed = prefix_signals == expected
    except Exception as exc:
        return {"passed": False, "value": None, "details": {"error": str(exc)}}
    return {
        "passed": passed,
        "value": midpoint,
        "details": {
            "prefix_length": midpoint,
            "full_length": len(full_signals),
            "reason": "prefix signals are stable" if passed else "future data influence detected",
        },
    }


def default_catalog(policy: CriteriaPolicy | None = None) -> TestCatalog:
    """Return the small, offline catalogue shipped with the first release."""
    policy = policy or CriteriaPolicy()
    catalog = TestCatalog()
    catalog.register(TestDefinition(
        "T_HANDOFF_001", "DAL handoff readiness", "integration", _handoff_ready
    ))
    catalog.register(TestDefinition(
        "T_SIGNAL_SHAPE_001", "Signal shape", "strategy", _signals_shape
    ))
    catalog.register(TestDefinition(
        "T_STABILITY_001", "Adaptive positive-return stability", "stability",
        lambda **kwargs: _adaptive_stability(policy=policy, **kwargs),
    ))
    catalog.register(TestDefinition(
        "T_RETURN_INTEGRITY_001", "Backtest return integrity", "data_quality", _return_integrity
    ))
    catalog.register(TestDefinition(
        "T_WALK_FORWARD_001", "Out-of-sample consistency", "stability",
        lambda **kwargs: _walk_forward_consistency(policy=policy, **kwargs),
    ))
    catalog.register(TestDefinition(
        "T_LOOKAHEAD_001", "Prefix causality", "indicator", _no_lookahead
    ))
    return catalog
