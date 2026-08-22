from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class CertificationReport:
    strategy_name: str
    tests_run: Dict[str, Dict[str, Any]]
    status: str
    validity_domain: Dict[str, Any]

