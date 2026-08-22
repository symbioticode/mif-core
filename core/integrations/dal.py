from __future__ import annotations

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
    if handoff.dqf_status not in {"PASS", "WARNING"}:
        raise HandoffContractError(f"unsupported dqf_status: {handoff.dqf_status!r}")
    if not handoff.asset_id or not handoff.calendar:
        raise HandoffContractError("handoff asset_id and calendar are required")
    if not isinstance(handoff.source_manifest, tuple) or not handoff.source_manifest:
        raise HandoffContractError("handoff source_manifest must be a non-empty tuple")
    if not 0.0 <= handoff.aqi <= 100.0:
        raise HandoffContractError("handoff aqi must be in [0, 100]")
    if not 0.0 <= handoff.dqf_mpi <= 100.0:
        raise HandoffContractError("handoff dqf_mpi must be in [0, 100]")
