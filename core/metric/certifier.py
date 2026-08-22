from __future__ import annotations

import math
from numbers import Real
from typing import Any

from ..integrations.dal import validate_dal_handoff
from .adapter import MetricAdapter


class MetricCertifier:
    """Validate a metric's declared output contract against one DAL handoff."""

    def certify(self, metric: MetricAdapter, handoff: Any) -> dict[str, Any]:
        if not isinstance(metric, MetricAdapter):
            raise TypeError("metric must implement MetricAdapter")
        validate_dal_handoff(handoff)
        validity_domain = {
            "asset_scope": handoff.asset_id,
            "calendar": handoff.calendar,
            "coverage": handoff.coverage,
            "assembly_hash": handoff.assembly_hash,
            "dqf_status": handoff.dqf_status,
        }
        try:
            output = metric.calculate(handoff)
        except Exception as exc:
            return {
                "schema_version": 1,
                "metric_name": metric.metadata.name,
                "metric_version": metric.metadata.version,
                "status": "FAIL",
                "validity_domain": validity_domain,
                "details": {"error": str(exc)},
            }

        kind = metric.metadata.output_kind
        if kind in {"series", "signal"}:
            try:
                actual_length = len(output)
            except TypeError:
                actual_length = -1
            expected_length = len(handoff.stream)
            invalid: list[dict[str, object]] = []
            if actual_length >= 0:
                for index, value in enumerate(output):
                    if isinstance(value, bool) or not isinstance(value, Real):
                        invalid.append(
                            {
                                "index": index,
                                "value": repr(value),
                                "reason": "not numeric",
                            }
                        )
                    elif not math.isfinite(value):
                        invalid.append(
                            {
                                "index": index,
                                "value": repr(value),
                                "reason": "not finite",
                            }
                        )
            passed = actual_length == expected_length and not invalid
            details = {
                "expected_length": expected_length,
                "actual_length": actual_length,
                "output_kind": kind,
                "invalid": invalid,
            }
        else:
            passed = (
                isinstance(output, Real)
                and not isinstance(output, bool)
                and math.isfinite(output)
            )
            details = {"output_kind": kind, "finite_numeric": passed}
        return {
            "schema_version": 1,
            "metric_name": metric.metadata.name,
            "metric_version": metric.metadata.version,
            "status": "PASS" if passed else "FAIL",
            "validity_domain": validity_domain,
            "details": details,
        }
