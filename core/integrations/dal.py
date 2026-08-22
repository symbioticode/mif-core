from __future__ import annotations

import math
from typing import Any


class HandoffContractError(ValueError):
    """Raised when CORE receives an object outside the DALHandoff contract."""


def validate_dal_handoff(handoff: Any) -> None:
    """Validate the public DALHandoff boundary without importing DAL at runtime."""
    required = (
        "stream", "asset_id", "calendar", "assembly_hash", "handoff_timestamp",
        "dal_version", "source_manifest", "coverage", "dqf_status", "dqf_mpi",
        "dqf_version", "dqf_report", "aqi",
    )
    missing = [name for name in required if not hasattr(handoff, name)]
    if missing:
        raise HandoffContractError(f"handoff missing DAL fields: {missing}")
    for name in ("asset_id", "calendar", "assembly_hash", "dal_version", "coverage"):
        if not isinstance(getattr(handoff, name), str) or not getattr(handoff, name):
            raise HandoffContractError(f"handoff {name} must be a non-empty string")
    if not hasattr(handoff.stream, "__len__"):
        raise HandoffContractError("handoff stream must be sized")
    if handoff.dqf_status not in {"PASS", "WARNING"}:
        raise HandoffContractError(f"unsupported dqf_status: {handoff.dqf_status!r}")
    if not isinstance(handoff.source_manifest, tuple) or not handoff.source_manifest:
        raise HandoffContractError("handoff source_manifest must be a non-empty tuple")
    for name in ("aqi", "dqf_mpi"):
        value = getattr(handoff, name)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise HandoffContractError(f"handoff {name} must be numeric")
        if not math.isfinite(value) or not 0.0 <= value <= 100.0:
            raise HandoffContractError(f"handoff {name} must be finite and in [0, 100]")
