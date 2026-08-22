from dataclasses import dataclass
from typing import Any, Callable, Dict


@dataclass(frozen=True)
class TestDefinition:
    id: str
    name: str
    category: str
    execute: Callable[..., Dict[str, Any]]


class TestCatalog:
    def __init__(self) -> None:
        self._tests: dict[str, TestDefinition] = {}

    def register(self, definition: TestDefinition) -> None:
        if definition.id in self._tests:
            raise ValueError(f"duplicate test id: {definition.id}")
        self._tests[definition.id] = definition

    def get(self, test_id: str) -> TestDefinition:
        return self._tests[test_id]

    def as_dict(self) -> Dict[str, TestDefinition]:
        return dict(self._tests)

