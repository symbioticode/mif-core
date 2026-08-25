from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class TestDefinition:
    id: str
    name: str
    category: str
    execute: Callable[..., dict[str, Any]]

    def __post_init__(self) -> None:
        if not all(
            isinstance(value, str) and value
            for value in (self.id, self.name, self.category)
        ):
            raise ValueError("test identity fields must be non-empty strings")
        if not callable(self.execute):
            raise TypeError("test execute must be callable")


class TestCatalog:
    def __init__(self) -> None:
        self._tests: dict[str, TestDefinition] = {}

    def register(self, definition: TestDefinition) -> None:
        if not isinstance(definition, TestDefinition):
            raise TypeError("definition must be a TestDefinition")
        if definition.id in self._tests:
            raise ValueError(f"duplicate test id: {definition.id}")
        self._tests[definition.id] = definition

    def get(self, test_id: str) -> TestDefinition:
        try:
            return self._tests[test_id]
        except KeyError:
            raise KeyError(f"unknown test ID: {test_id}") from None

    def as_dict(self) -> dict[str, TestDefinition]:
        return dict(self._tests)
