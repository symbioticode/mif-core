from dataclasses import dataclass
import json
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

    def to_json(self) -> str:
        """Serialize the report using the stable dictionary representation."""
        return json.dumps(self.to_dict(), sort_keys=True)

    def to_text(self) -> str:
        """Render a compact human-readable report without losing test detail."""
        lines = [
            f"Strategy: {self.strategy_name}",
            f"Status: {self.status}  Tier: {self.tier}",
            "Validity: " + ", ".join(
                f"{key}={value}" for key, value in self.validity_domain.items()
            ),
            "Tests:",
        ]
        for result in self.tests_run.values():
            line = (
                f"- {result['test_id']} [{result['status']}] {result['test_name']}"
                f" value={result['value']}"
            )
            if result.get("threshold") is not None:
                line += f" threshold={result['threshold']}"
            if result.get("details"):
                line += " details=" + json.dumps(result["details"], sort_keys=True)
            lines.append(line)
        return "\n".join(lines)
