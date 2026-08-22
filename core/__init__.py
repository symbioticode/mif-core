from importlib.metadata import PackageNotFoundError, version

from .certification import Certifier, CertificationReport, calculate_tier
from .strategy import StrategyAdapter, StrategyMetadata, StrategyRegistry
from .testing import (
    CriteriaPolicy,
    TestCatalog,
    TestDefinition,
    TestResult,
    default_catalog,
)
from .integrations import validate_dal_handoff
from .metric import MetricAdapter, MetricCertifier, MetricMetadata, MetricRegistry

try:
    __version__ = version("metric-integrity-core")
except PackageNotFoundError:
    __version__ = "0.1.0.dev1"

__all__ = [
    "Certifier",
    "CertificationReport",
    "calculate_tier",
    "StrategyAdapter",
    "StrategyMetadata",
    "CriteriaPolicy",
    "MetricAdapter",
    "MetricCertifier",
    "MetricMetadata",
    "MetricRegistry",
    "StrategyRegistry",
    "TestCatalog",
    "TestDefinition",
    "TestResult",
    "default_catalog",
    "validate_dal_handoff",
    "__version__",
]
