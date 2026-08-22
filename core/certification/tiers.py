from __future__ import annotations

from collections.abc import Mapping


def calculate_tier(results: Mapping[str, Mapping[str, object]]) -> str:
    """Return a transparent summary tier from normalized test results.

    S requires every test to pass. A and B describe partial evidence only;
    they are not production approval. An empty result set is always C.
    """
    if not results:
        return "C"
    ratio = sum(item.get("passed", False) is True for item in results.values()) / len(
        results
    )
    if ratio == 1.0:
        return "S"
    if ratio >= 0.80:
        return "A"
    if ratio >= 0.50:
        return "B"
    return "C"
