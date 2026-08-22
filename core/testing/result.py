from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class TestResult:
    """Versioned machine-readable result for one atomic test."""

    test_id: str
    test_name: str
    category: str
    passed: bool
    value: Any
    details: dict[str, Any]
    threshold: Any = None
    schema_version: int = 1

    def __post_init__(self) -> None:
        if not self.test_id or not self.test_name or not self.category:
            raise ValueError("test identity fields are required")
        if not isinstance(self.passed, bool):
            raise TypeError("passed must be a boolean")
        if not isinstance(self.details, dict):
            raise TypeError("details must be a dictionary")
        if isinstance(self.schema_version, bool) or not isinstance(
            self.schema_version, int
        ):
            raise TypeError("schema_version must be an integer")
        if self.schema_version != 1:
            raise ValueError("unsupported test result schema version")

    def to_dict(self) -> dict[str, Any]:
        result = {
            "schema_version": self.schema_version,
            "test_id": self.test_id,
            "test_name": self.test_name,
            "category": self.category,
            "status": "PASS" if self.passed else "FAIL",
            "severity": "INFO" if self.passed else "ERROR",
            "interpretation": "Test passed" if self.passed else "Test failed",
            "passed": self.passed,
            "value": self.value,
            "details": self.details,
        }
        if self.threshold is not None:
            result["threshold"] = self.threshold
        return result
