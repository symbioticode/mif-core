from __future__ import annotations

import math
from typing import Any

from ..integrations.dal import validate_dal_handoff
from .adapter import MetricAdapter


class MetricCertifier:
    """Validate a metric's declared output contract against one DAL handoff."""

    def certify(self, metric: MetricAdapter, handoff: Any) -> dict[str, Any]:
        validate_dal_handoff(handoff)
        try:
            output = metric.calculate(handoff)
        except Exception as exc:
            return {"metric_name": metric.metadata.name, "status": "FAIL", "details": {"error": str(exc)}}

        kind = metric.metadata.output_kind
        if kind in {"series", "signal"}:
            try:
                actual_length = len(output)
            except TypeError:
                actual_length = -1
            expected_length = len(handoff.stream)
            passed = actual_length == expected_length
            details = {
                "expected_length": expected_length,
                "actual_length": actual_length,
                "output_kind": kind,
            }
        else:
            passed = isinstance(output, (int, float)) and not isinstance(output, bool) and math.isfinite(output)
            details = {"output_kind": kind, "finite_numeric": passed}
        return {
            "metric_name": metric.metadata.name,
            "metric_version": metric.metadata.version,
            "status": "PASS" if passed else "FAIL",
            "validity_domain": {
                "asset_scope": handoff.asset_id,
                "calendar": handoff.calendar,
                "assembly_hash": handoff.assembly_hash,
                "dqf_status": handoff.dqf_status,
            },
            "details": details,
        }
