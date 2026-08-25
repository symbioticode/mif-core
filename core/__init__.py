from importlib.metadata import PackageNotFoundError, version

from .certification import CertificationReport, Certifier, calculate_tier
from .integrations import validate_dal_handoff
from .metric import MetricAdapter, MetricCertifier, MetricMetadata, MetricRegistry
from .strategy import StrategyAdapter, StrategyMetadata, StrategyRegistry
from .testing import (
    CriteriaPolicy,
    TestCatalog,
    TestDefinition,
    TestResult,
    default_catalog,
)

try:
    __version__ = version("mif-foundation")
except PackageNotFoundError:
    __version__ = "0.1.0"

__all__ = [
    "CertificationReport",
    "Certifier",
    "CriteriaPolicy",
    "MetricAdapter",
    "MetricCertifier",
    "MetricMetadata",
    "MetricRegistry",
    "StrategyAdapter",
    "StrategyMetadata",
    "StrategyRegistry",
    "TestCatalog",
    "TestDefinition",
    "TestResult",
    "__version__",
    "calculate_tier",
    "default_catalog",
    "validate_dal_handoff",
]
