from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class CertificationReport:
    strategy_name: str
    tests_run: Dict[str, Dict[str, Any]]
    status: str
    validity_domain: Dict[str, Any]
    tier: str = "C"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "strategy_name": self.strategy_name,
            "status": self.status,
            "tests_run": self.tests_run,
            "validity_domain": self.validity_domain,
            "tier": self.tier,
        }
